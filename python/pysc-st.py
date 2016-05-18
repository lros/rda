#!/usr/bin/env python3

# This approach uses a single thread to service all consoles and the listening
# thread.  Unfortunately the only strong use case I can think of for multiple
# consoles is if you accidently wedged one and need another.

import code
import errno
import socket
import selectors
import threading

_addrPort = None
_selector = None
_thread = None
_stopped = False

# One of many ways to use selectors.  Bundle up the per-socket data in an
# instance.  We use three methods:  readable() and writable() for socket
# events coming from the selectors module; and close() that we call to
# clean up.

class _Selectable:
    def readable(self, sock):
        raise RuntimeError('No readable() implementation')
    def writeable(self, sock):
        raise RuntimeError('No writeable() implementation')
    def close(self, sock):
        raise RuntimeError('No close() implementation')

class _SelectableListener(_Selectable):
    def __init__(self):
        pass

    def readable(self, sock):
        conn, addr = sock.accept()
        print('accepted from', addr)
        conn.setblocking(False)
        sc = _SelectableConsole(addr)
        _selector.register(conn, selectors.EVENT_READ, sc)

    def close(self, sock):
        _selector.unregister(sock)
        sock.close()

class _SelectableConsole(_Selectable):
    def __init__(self, addr):
        self.fromAddress = addr

    def readable(self, sock):
        data = sock.recv(4096)
        if len(data) > 0:
            print(self.fromAddress, data)
        else:
            _selector.unregister(sock)
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            print('closed from', self.fromAddress)

    def close(self, sock):
        _selector.unregister(sock)
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

def _threadFn():
    global _addrPort, _selector, _stopped
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(_addrPort)
    s.listen(1)
    s.setblocking(False)
    sl = _SelectableListener()
    _selector.register(s, selectors.EVENT_READ, sl)

    while True:
        events = _selector.select()
        if _stopped: break
        for key, mask in events:
            if selectors.EVENT_READ & mask:
                key.data.readable(key.fileobj)
            if selectors.EVENT_WRITE & mask:
                key.data.writeable(key.fileobj)

    # Close all sockets.
    selectorkeys = list(_selector.get_map().values())
    for key in selectorkeys:
        key.data.close(key.fileobj)

# Starts a thread listening for connections on the given port.
# Listen on the given address's interface only, or default to all interfaces.
def start(port, address=''):
    # null string means INADDR_ANY
    global _addrPort, _selector, _thread
    if _addrPort is not None: return
    _addrPort = (address, port)
    _selector = selectors.DefaultSelector()
    _thread = threading.Thread(target=_threadFn, name='SocketConsole')
    _thread.start()

# Stop any open SocketConsoles and stop listening for connections
def stop():
    global _addrPort, _thread, _stopped
    if _addrPort is None: return
    _stopped = True
    # To get select() to return now, attempt to make a connetion to
    # the listener.  It will never be accept()-ed because _stopped is True.
    s = socket.socket()
    s.setblocking(False)
    port = _addrPort[1]
    try:
        s.connect(('127.0.0.1', port))
    except socket.error as e:
        if e.errno != errno.EWOULDBLOCK \
                and e.errno != errno.EINPROGRESS:
            raise
    _thread.join()
    s.close()
    _addrPort = None
    _selector = None
    _thread = None
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

