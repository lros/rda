#!/usr/bin/env python3

import code
import select
import socket
import inspect
import threading

# How long to wait (sec) between checking for stopping.
stopCheckDuration = 0.2

_threadsToJoin = list()
_stopRequest = False

def start(port, address='', multiple=False, symtab=None):
    if symtab is None:
        # Get a copy of the caller's locals() to use as context.
        symtab = dict(inspect.currentframe().f_back.f_locals)
    _listen((address, port), multiple, symtab)

def stop():
    # TODO make sure this works when called from a console
    global _threadsToJoin, _stopRequest
    _stopRequest = True
    thisThread = threading.current()
    for t in _threadsToJoin:
        if t is not thisThread:
            t.join()
    _threadsToJoin.clear()

def _listen(addrPort, multiple, symtab):
    # Within this function, sock is the socket we listen on for connections.
    global stopCheckDuration, _stopRequest, _threadsToJoin
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addrPort)
    sock.listen(1)
    sock.setblocking(False)
    slist = (sock,)
    empty = tuple()
    while True:
        readable, junk, junk = \
                select.select(slist, empty, empty, stopCheckDuration)
        if _stopRequest: break
        #if len(readable) > 0 and readable[0] is sock:
        if readable:
            conn, addr = sock.accept()
            print('accepted from', addr)
            conn.setblocking(False)
            if multiple:
                t = threading.Thread(target=_console, args=(conn, addr, symtab))
                _threadsToJoin.append(t)
                t.start()
            else:
                _console(conn, addr, symtab)
        if _stopRequest: break
    sock.close()
    _stopRequest = False
    print('_listen() exit')

def _console(sock, fromAddress, symtab):
    # Within this function, sock is the socket from one connection.
    c = SocketInteractiveConsole(sock, symtab)
    c.interact()
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    print('_console() exit')
    # TODO Should I bother to remove this thread from _threadsToJoin?

class SocketInteractiveConsole(code.InteractiveConsole):

    ident = 0  # Id of next instance; also counts instances

    def __init__(self, sock, symtab):
        self.sock = sock
        self.stopRequest = False
        # Make exit() in the console only exit the console, not the program.
        # (There's still sys.exit().)
        symtab['exit'] = self.stop
        self.linebuf = bytearray()
        self.ident = SocketInteractiveConsole.ident
        SocketInteractiveConsole.ident += 1
        print('start SocketInteractiveConsole #', self.ident)
        # TODO get the right context in here (locals)
        super().__init__(filename='<socket-' + str(self.ident) + '>',
                locals=symtab)

    def raw_input(self, prompt):
        global stopCheckDuration, _stopRequest
        self.write(prompt)
        slist = (self.sock,)
        empty = tuple()
        while True:
            readable, junk, junk = \
                    select.select(slist, empty, empty, stopCheckDuration)
            if _stopRequest or self.stopRequest: break
            if readable:
                data = self.sock.recv(4096)
                if len(data) > 0:
                    #print('received', data)
                    self.linebuf.extend(data)
                    if self.linebuf[-1] == 10:
                        # Remove trailing LF or CRLF
                        del self.linebuf[-1]
                        if self.linebuf[-1] == 13:
                            del self.linebuf[-1]
                        line = self.linebuf.decode()
                        self.linebuf.clear()
                        #print('returning line:', line)
                        return line
                else:
                    print('EOF on SocketInteractiveConsole #', self.ident)
                    break
        raise EOFError()

    def write(self, strdata):
        self.sock.sendall(strdata.encode())

    def stop(self):
        self.stopRequest = True

