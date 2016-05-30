# Manage the history state and changes for simpleReadline.

import simpleReadline as sr

_history = list()   # list of strings, [0] is oldest
_lineno = None      # index of current line in _history
_lineBuf = None     # bytearray of current line
# At any given moment, we are either
# 1. looking at an unmodified line in the history list, or
# 2. editing a line, or
# 3. at the end of the history with a blank line.
# If 1, then _lineno is not None; if 2, then _lineBuf is not None.

# Some output sequences as bytes
kBeep = b'\a'
kErase = b'\b \b'

def _return():
    global _lineBuf, _lineno
    if _lineBuf is not None:
        result = _lineBuf.decode()
    elif _lineno is not None:
        result = _lineBuf[_lineno]
    else:
        result = ""
    _lineno = _lineBuf = None
    sr.interpretKeys._writeFn(b'\r\n')
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
        sr.interpretKeys._writeFn(kErase)
    else:
        sr.interpretKeys._writeFn(kBeep)

def _delRight():
    print("delRight", end='\r\n')

def _insert(bite):
    # TODO currently only appends to end of line
    global _lineBuf
    if _lineBuf is None:
        _lineBuf = bytearray()
    _lineBuf.append(bite)
    sr.interpretKeys._writeFn(_lineBuf[-1:])
    print("insert", bite, end='\r\n')

def _expand():
    print("expand", end='\r\n')

