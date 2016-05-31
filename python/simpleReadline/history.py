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
# TODO Should blank lines and repeats not be added to history?

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

# Rewrite the tail of the line.  The cursor is currently at _charPos,
# and _lineBuf[start:] has (potentially) changed.  Leave cursor at newPos.
# Note _lineBuf may not be None when this is called.
def _rewrite(start, newPos):
    global _lineBuf, _charPos
    command = bytearray()
    # Move cursor to start
    if _charPos is None:
        # We must be at the beginning of a blank line.
        # Remember _lineBuf has been updated but _charPos has not.
        _charPos = 0
    _cmdMove(command, start - _charPos)
    # Erase to end of line (end of screen, actually)
    command.extend(b'\033[J')
    # Write new data
    command.extend(_lineBuf[start:])
    # Move cursor to newPos
    _cmdMove(command, newPos - len(_lineBuf))
    sr.main._writeFn(command)
    _charPos = newPos

# Append escape sequence to command, to move right n spaces.
# Append nothing if n is zero; negative n means move left.
def _cmdMove(command, n):
    if n < 0:
        command.extend(b'\033[')
        command.extend(str(-n).encode())
        command.extend(b'D')
    elif n > 0:
        command.extend(b'\033[')
        command.extend(str(n).encode())
        command.extend(b'C')

def enter():
    global _lineBuf, _lineNo
    if _lineBuf is not None:
        result = _lineBuf.decode()
    else:
        result = ""
    _lineNo = _lineBuf = None
    _history.append(result)
    sr.main._writeFn(kReturn)
    return result

def left():
    global _lineBuf, _lineNo, _charPos
    if _lineBuf and _charPos > 0:
        _charPos += -1
        sr.main._writeFn(kLeft)
    else:
        sr.main._writeFn(kBeep)

def right():
    global _lineBuf, _lineNo, _charPos
    if _lineBuf and _charPos < len(_lineBuf):
        _charPos += 1
        sr.main._writeFn(kRight)
    else:
        sr.main._writeFn(kBeep)

def up():
    global _lineBuf, _lineNo, _charPos
    if _lineNo is None:
        if _history:
            new = len(_history) - 1
        else:
            new = None
    elif _lineNo > 0:
        new = _lineNo - 1
    else:
        new = 0
    # If new is None then we have no history; do nothing.  And _lineNo
    # is necessarily also None.
    if new != _lineNo:
        _lineBuf = bytearray(_history[new].encode())
        _rewrite(0, len(_lineBuf))
        _lineNo = new
    else:
        sr.main._writeFn(kBeep)

def down():
    global _lineBuf, _lineNo, _charPos
    if _lineNo is None:
        new = None
    else:
        new = _lineNo + 1
        if new >= len(_history):
            new = None
    # If new is None then we are on a new blank line
    if new != _lineNo:
        if new is None:
            _lineBuf = bytearray()
        else:
            _lineBuf = bytearray(_history[new].encode())
        _rewrite(0, len(_lineBuf))
        _lineNo = new
    else:
        sr.main._writeFn(kBeep)

def delLeft():
    global _lineBuf, _charPos
    if _lineBuf and _charPos > 0:
        newPos = _charPos - 1
        del _lineBuf[newPos]
        _rewrite(newPos, newPos)
    else:
        sr.main._writeFn(kBeep)

def delRight():
    global _lineBuf, _charPos
    if _lineBuf and _charPos < len(_lineBuf):
        del _lineBuf[_charPos]
        _rewrite(_charPos, _charPos)
    else:
        sr.main._writeFn(kBeep)

def insert(bite):
    global _lineBuf, _charPos
    if _lineBuf is None:
        _lineBuf = bytearray()
        _charPos = 0
    _lineBuf.insert(_charPos, bite)
    _rewrite(_charPos, _charPos + 1)

def expand():
    print("expand", end='\r\n')

