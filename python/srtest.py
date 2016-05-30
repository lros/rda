#!/usr/bin/env python3

# Test program for simpleReadline module.

import sys
import simplereadline as sr

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
sr.configure(context=locals())
while True:
    c = getch()
    #print('You typed:', repr(c), end='\r\n')
    c = c[0]
    if c == 3: break  # control-C
    line = sr.addByte(c)
    if line is not None:
        print('line:', line, end='\r\n')
        for c in line:
            print(ord(c), end=' ')
        print(end='\r\n')

if oldtermios is not None:
    termios.tcsetattr(fd, termios.TCSADRAIN, oldtermios)

