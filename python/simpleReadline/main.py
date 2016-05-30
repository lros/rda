# Simplified version of Python readline module that does not require the
# GNU readline package (which is available only on Linux).

# This Python module implements two key features:
# 1.  Tab completion
# 2.  History
# The history is optionally persistent in a file.
# Tab completion optionally includes identifiers from an execution context.

# Design remarks:
# - The design uses module-as-singleton: it is not possible to maintain
#   multiple separate readline states simultaneously.
# - As you can see, the module is broken up into several files.

import sys
#import rlcompleter
#import simpleReadline as sr

def configure(writeFn=None, context=None):
    # TODO move context to the socket-oriented module?
    global _writeFn, _context
    _writeFn = _defaultWriteFn if writeFn is None else writeFn
    _context = context

def _defaultWriteFn(bites):
    # This will fail if stdout is not a normal tty console
    sys.stdout.buffer.raw.write(bites)

_writeFn = _defaultWriteFn

