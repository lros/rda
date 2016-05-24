#!/usr/bin/env python3

# Simplified version of Python readline module that does not require the
# GNU readline package (which is available only on Linux).

# This Python module implements two key features:
# 1.  Tab completion
# 2.  History
# The history is optionally persistent in a file.
# Tab completion optionally includes identifiers from an execution context.
# This uses module-as-singleton: it is not possible to maintain multiple
# separate readline states simultaneously.

import sys
import rlcompleter

# Configuration state
_writeFn = None   # Function to write text
_context = None   # Dictionary of local identifiers

def configure(writeFn=None, context=None):
    global _writeFn, _context
    _writeFn = _defaultWriteFn if writeFn is None else writeFn
    _context = context

# Runtime state
_history = list()   # list of strings, [0] is oldest
_lineno = None      # index of current line in _history
_lineBuf = None     # bytearray of current line
# At any given moment, we are either
# 1. looking at an unmodified line in the history list, or
# 2. editing a line, or
# 3. at the end of the history with a blank line.
# If 1, then _lineno is not None; if 2, then _lineBuf is not None.

# Some other code hands input text to this function as bytes arrive.
# byte is a single byte value (an int), not a bytes object.
# Returns None or a full line of text (as a string).
def addByte(byte):
    global _history, _lineno, _lineBuf, _writeFn
    if byte == 13:  # \r
        if _lineBuf is not None:
            result = _lineBuf.decode()
        elif _lineno is not None:
            result = _lineBuf[_lineno]
        else:
            result = ""
        _lineno = _lineBuf = None
        _writeFn(b'\r\n')
        return result
    else:
        # TODO handle history
        if _lineBuf is None:
            _lineBuf = bytearray()
        _lineBuf.append(byte)
        _writeFn(_lineBuf[-1:])
    return None

def _defaultWriteFn(bites):
    # This will fail if stdout is not a normal tty console
    sys.stdout.buffer.raw.write(bites)

_writeFn = _defaultWriteFn

if __name__ == "__main__":
    getch = None
    oldtermios = None
    fd = None
    try:
        import msvcrt
        getch = msvcrt.getch
    except ImportError:
        # assume Linux
        import termios, tty
        fd = sys.stdin.fileno()
        oldtermios = termios.tcgetattr(fd)
        tty.setraw(fd)
        def getch():
            # This will fail if stdin is not a normal tty console
            return sys.stdin.buffer.raw.read(1)

    foo = "bar"
    configure(context=locals())
    while True:
        c = getch()
        #print('You typed:', repr(c))
        c = c[0]
        if c == 3: break  # control-C
        line = addByte(c)
        if line is not None:
            print('line:', line, end='\r\n')

    if oldtermios is not None:
        termios.tcsetattr(fd, termios.TCSADRAIN, oldtermios)

