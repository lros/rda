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

# Some ASCII codes
kBEL = ord('\a')
kBS = ord('\b')
kHT = ord('\t')
kLF = ord('\n')
kCR = ord('\r')
kESC = 27
kCSI = ord('[')  # introduces multi character escape sequences
kSS2 = ord('N')  # alternate character set (more commonly received codes)
kSS3 = ord('O')  # alternate character set (more commonly received codes)
kDEL = 127
kUP = ord('A')
kLEFT = ord('D')
kRIGHT = ord('C')
kDOWN = ord('B')
kDELKEY = ord('~')

# Windows console, determined by experimentation.  I made up the names.
kWESC = 224  # Used like ESC on Windows
kWUP = 72
kWLEFT = 75
kWRIGHT = 77
kWDOWN = 80
kWDEL = 83

# Some output sequences as bytes
kBeep = b'\a'
kErase = b'\b \b'

# Incoming escape sequence state
# None - not in an escape sequence
# True - ESC received
# (int) - alternate state, e.g. ESC-O
# (bytearray) - reading a CSI code
_escState = None

# Some other code hands input text to this function as bytes arrive.
# byte is a single byte value (an int), not a bytes object.
# Returns None or a full line of text (as a string).
def addByte(bite):
    global _escState
    #print('addByte():', bite, end='\r\n')
    #print('_escState is', _escState, end='\r\n')
    if _escState is not None:
        return _handleEsc(bite)
    global _history, _lineno, _lineBuf, _writeFn
    if bite == kCR or bite == kLF:
        return _return()
    elif bite == kDEL or bite == kBS:
        return _delLeft()
    elif bite == kHT:
        return _expand()
    elif bite == kESC:
        _escState = True
    elif bite == kWESC:
        _escState = kWESC
    else:
        # TODO handle history
        if _lineBuf is None:
            _lineBuf = bytearray()
        _lineBuf.append(bite)
        _writeFn(_lineBuf[-1:])
    return None

def _return():
    global _lineBuf, _lineno
    if _lineBuf is not None:
        result = _lineBuf.decode()
    elif _lineno is not None:
        result = _lineBuf[_lineno]
    else:
        result = ""
    _lineno = _lineBuf = None
    _writeFn(b'\r\n')
    return result

def _left():
    print("left", end='\r\n')

def _right():
    print("right", end='\r\n')

def _up():
    print("up", end='\r\n')

def _down():
    print("down", end='\r\n')

def _delLeft():
    global _lineBuf
    if _lineBuf:
        del _lineBuf[-1]
        _writeFn(kErase)
    else:
        _writeFn(kBeep)

def _delRight():
    print("delRight", end='\r\n')

def _insert(bite):
    print("insert", bite, end='\r\n')

def _expand():
    print("expand", end='\r\n')

def _handleEsc(bite):
    global _escState
    #print("_handleEsc(", bite, ")", end='\r\n')
    if _escState is True:
        if bite == kCSI:
            _escState = bytearray()
            #print('parsed CSI', end='\r\n')
        elif kSS2 <= bite <= kSS3:
            _escState = bite;
        elif 64 <= bite <= 95:   # two-character sequence
            _escState = None
            # TODO deal with sequence
            print('ESC-', chr(bite), end='\r\n')
        else:
            print('bad escape sequence:', kESC, bite, end='\r\n')
            _escState = None
    elif _escState is kWESC:
        if bite == kWUP:
            _up()
        elif bite == kWDOWN:
            _down()
        elif bite == kWLEFT:
            _left()
        elif bite == kWRIGHT:
            _right()
        elif bite == kWDEL:
            _delRight()
        else:
            print('Bad or unused Windows ESC-', bite, end='\r\n')
        _escState = None
    elif isinstance(_escState, bytearray):
        #print('within a CSI', end='\r\n')
        if 48 <= bite <= 63:
            _escState.append(bite)
        elif 64 <= bite <= 126:  # end of CSI sequence
            if bite == kUP:
                _up()
            elif bite == kDOWN:
                _down()
            elif bite == kLEFT:
                _left()
            elif bite == kRIGHT:
                _right()
            elif bite == kDELKEY and _escState == b'3':
                _delRight()
            else:
                print('unused or unknown ESC-',
                        _escState, chr(bite), end='\r\n')
            _escState = None
        else:
            print('bad escape sequence:', _escState, bite, end='\r\n')
            _escState = None
    elif isinstance(_escState, int):
        if _escState == kSS3:
            # TODO deal with sequence
            print('ESC-O', chr(bite), end='\r\n')
        else:
            print('bad escape sequence:', kESC, _escState, bite, end='\r\n')
        _escState = None
    else:
        raise RuntimeError("_escState broken: {}".format(_escState))

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
        #print('You typed:', repr(c), end='\r\n')
        c = c[0]
        if c == 3: break  # control-C
        line = addByte(c)
        if line is not None:
            print('line:', line, end='\r\n')
            for c in line:
                print(ord(c), end=' ')
            print(end='\r\n')

    if oldtermios is not None:
        termios.tcsetattr(fd, termios.TCSADRAIN, oldtermios)

