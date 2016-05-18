#!/usr/bin/env python3

# Use a thread per console.  The normal use case is one console.  The only
# strong use case I can think of for multiple consoles is if you somehow
# wedge one and want another.  In that case, you don't want the thread that
# listens for connections to also service any of the consoles.  So we use
# two threads for what is typically one console.

# To stop and clean up, the threads themselves have to check to see if they
# should stop.  Sadly, there's no portable (Linux and Windows) mechanism to
# wait for either an in-process signal of some sort or activity on a file
# descriptor.  (I think kqueue is the ideal solution but I'm not positive.)

import code
import errno
import select
import socket
import threading

# How long to wait (sec) between checking for stopping.
stopCheckDuration = 0.2

_addrPort = None
_listenerThread = None
_lock = threading.Lock()
_consoles = list()
_stopped = False

def _listenerFn():
    global stopCheckDuration, _addrPort, _stopped
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(_addrPort)
    sock.listen(1)
    sock.setblocking(False)
    slist = (sock,)
    empty = tuple()
    while True:
        readable, junk, junk = \
                select.select(slist, empty, empty, stopCheckDuration)
        if _stopped: break
        #if len(readable) > 0 and readable[0] is sock:
        if readable:
            conn, addr = sock.accept()
            print('accepted from', addr)
            conn.setblocking(False)
            c = Console(conn, addr)
            with _lock:
                _consoles.append(c)
            c.start()
    sock.close()
    print('listenerFn() exit')

class Console(threading.Thread):
    def __init__(self, sock, addr):
        super().__init__(name="SocketConsole")
        self.sock = sock
        self.fromAddress = addr

    def run(self):
        global stopCheckDuration, _stopped
        slist = (self.sock,)
        empty = tuple()
        while True:
            readable, junk, junk = \
                    select.select(slist, empty, empty, stopCheckDuration)
            if _stopped: break
            if readable:
                data = self.sock.recv(4096)
                if len(data) > 0:
                    print(self.fromAddress, data)
                else:
                    print('closed from', self.fromAddress)
                    break
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        with _lock:
            _consoles.remove(self)
        print('Console.run() exit')

# Starts a thread listening for connections on the given port.
# Listen on the given address's interface only, or default to all interfaces.
def start(port, address=''):
    # null string means INADDR_ANY
    global _addrPort, _listenerThread
    if _addrPort is not None: return
    _addrPort = (address, port)
    _listenerThread = threading.Thread(target=_listenerFn, name='SocketConsoleListener')
    _listenerThread.start()

# Stop any open SocketConsoles and stop listening for connections
def stop():
    global _addrPort, _listenerThread, _stopped
    if _addrPort is None: return
    _stopped = True
    _listenerThread.join()
    with _lock:
        copy = _consoles[:]
    for c in copy:
        c.join()
    print('consoles list:', _consoles)
    _addrPort = None
    _listenerThread = None
    _stopped = False

if __name__ == "__main__":

    import time

    print('Listening on port 2323')
    start(2323)
    try:
        while True:
            time.sleep(1)
    except:
        pass
    print('Stopping consoles')
    stop()

