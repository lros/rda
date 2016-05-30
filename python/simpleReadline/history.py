# Simplified version of Python readline module that does not require the
# GNU readline package (which is available only on Linux).

# Manage the history state and changes including editing the current line.
# Also echoes back to the screen.

import simpleReadline as sr

# Behavior:
# - Up and down discard move through the history list.  If a new line is
#   displayed, any existing changes are discarded.
# - Left and right move through the current line.
# - Del and Backspace delete to the left and right of the current position.
# - Tab does expansion (see elsewhere).  TODO
# - Backtab does nothing.  It's not always available.
# - Return causes the current line to be processed.
# - Any other escape sequence is ignored.
# - Any other key is inserted at the current position.

_history = list()   # list of strings, [0] is oldest
_lineNo = None      # index of current line in _history
_lineBuf = None     # bytearray of current line
_charPos = None     # position within current line

# Data invariants:
# - _history is the history list as (Unicode) strings.
# - If there's a partial or complete line showing on the screen, it is
#   in _lineBuf as bytes.
# - A line is added to the history list only when Return is pressed and
#   it's processed.
# - If _lineBuf is not None then _charPos is valid.  If _lineBuf is None,
#   then we're at the beginning of a blank line.
# - _lineNo is None if we're on a new line not yet in history.

# Some output sequences as bytes
kBeep = b'\a'
kErase = b'\b \b'
kReturn = b'\r\n'
kLeft = b'\033[D'
kRight = b'\033[C'
kEraseLine = b'\033[0E\033[J'

def _return():
    global _lineBuf, _lineNo
    if _lineBuf is not None:
        result = _lineBuf.decode()
    else:
        result = ""
    _lineNo = _lineBuf = None
    _history.append(result)
    sr.main._writeFn(kReturn)
    return result

def _left():
    global _lineBuf, _lineNo, _charPos
    if _lineBuf is None:
        _lineBuf = bytes()
    if _charPos is None:
        _charPos = len(_lineBuf)
    if _charPos > 0:
        _charPos += -1
        sr.main._writeFn(kLeft)

def _right():
    global _lineBuf, _lineNo, _charPos
    if _lineBuf is None:
        _lineBuf = bytes()
    if _charPos is None:
        _charPos = len(_lineBuf)
    if _charPos < len(_lineBuf):
        _charPos += 1
        sr.main._writeFn(kRight)

def _up():
    if _lineNo is None:
        if _history:
            new = len(_history) - 1
        else:
            new = None
    elif _lineNo > 0:
        new = _lineNo - 1
    else:
        new = 0
    # If new is None then we have no history; do nothing.
    if new != _lineno:
        sr.main._writeFn(kEraseLine)
        _lineBuf = _history[_lineNo].encode()
        sr.main._writeFn(_lineBuf)
        _lineno = new
        _charPos = len(_lineBuf)

def _down():
    if _lineNo is None:
        new = None
    else:
        new = _lineNo + 1
        if new >= len(_history):
            new = None
    # If new is None then we are on a new blank line
    if new != _lineno:
        sr.main._writeFn(kEraseLine)
        if new is None:
        else:
            _lineBuf = _history[_lineNo].encode()
            sr.main._writeFn(_lineBuf)
            _lineno = new
            _charPos = len(_lineBuf)
        _lineNo = new

def _delLeft():
    global _lineBuf
    if _lineBuf:
        del _lineBuf[-1]
        sr.main._writeFn(kErase)
    else:
        sr.main._writeFn(kBeep)

def _delRight():
    print("delRight", end='\r\n')

def _insert(bite):
    # TODO currently only appends to end of line
    global _lineBuf
    if _lineBuf is None:
        _lineBuf = bytearray()
    _lineBuf.append(bite)
    sr.main._writeFn(_lineBuf[-1:])

def _expand():
    print("expand", end='\r\n')

