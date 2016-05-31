# Simplified version of Python readline module that does not require the
# GNU readline package (which is available only on Linux).

# This file implements interpretation of the bytes sent by various terminal
# emulators (Windows console, Linux terminal, etc.).

import simpleReadline as sr

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
    global _writeFn
    if bite == kCR or bite == kLF:
        return sr.history.enter()
    elif bite == kDEL or bite == kBS:
        return sr.history.delLeft()
    elif bite == kHT:
        return sr.history.expand()
    elif bite == kESC:
        _escState = True
    elif bite == kWESC:
        _escState = kWESC
    else:
        sr.history.insert(bite)
    return None

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
            sr.history.up()
        elif bite == kWDOWN:
            sr.history.down()
        elif bite == kWLEFT:
            sr.history.left()
        elif bite == kWRIGHT:
            sr.history.right()
        elif bite == kWDEL:
            sr.history.delRight()
        else:
            print('Bad or unused Windows ESC-', bite, end='\r\n')
        _escState = None
    elif isinstance(_escState, bytearray):
        #print('within a CSI', end='\r\n')
        if 48 <= bite <= 63:
            _escState.append(bite)
        elif 64 <= bite <= 126:  # end of CSI sequence
            if bite == kUP:
                sr.history.up()
            elif bite == kDOWN:
                sr.history.down()
            elif bite == kLEFT:
                sr.history.left()
            elif bite == kRIGHT:
                sr.history.right()
            elif bite == kDELKEY and _escState == b'3':
                sr.history.delRight()
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

