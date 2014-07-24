#!/usr/bin/env python3
# rdainfo.py - report a piece of rda-related info, use --help for details
# Both a command line utility and a Python utility module.

import os
import sys
import argparse
import os.path as path

def top(unknown=False, **kwargs):
    d = os.getcwd()
    while True:
        if path.isdir(path.join(d, 'build')):
            return d
        parent = path.dirname(d)
        if parent == d:
            if unknown:
                return 'unknown'
            raise Exception('Not in an RDA sandbox.')
        d = parent

def host(unknown=False, **kwargs):
    if sys.platform.startswith('linux'):
        return 'linux'
    if sys.platform.startswith('win'):
        return 'windows'
    if sys.platform.startswith('darwin'):
        return 'osx'
    if unknown:
        return 'unknown'
    raise Exception('Unknown host: ' + sys.platform)

if __name__ == '__main__':

    # Parse arguments

    parser = argparse.ArgumentParser(
        description='Report RDA-related information.')
    parser.add_argument('--top', action='store_true',
        help='Report the root of the sandbox containing the current directory.')
    parser.add_argument('--host', action='store_true',
        help='Report the host type running this program:'
                ' linux, windows, or osx.')
    parser.add_argument('--all', action='store_true',
        help='Report all items, with labels.  Implies --unknown.')
    parser.add_argument('--unknown', action='store_true',
        help='Print \'unknown\' instead of raising exceptions.')
    parser.add_argument('--debug', action='store_true',
        help='Debug this script: print extra crap.')
    args = parser.parse_args()

    # Process the arguments
    if args.debug:
        print(args)
    if args.all:
        args.unknown = True
        print('top:', top(**args.__dict__))
        print('host:', host(**args.__dict__))
    else:
        if args.top:
            print(top(**args.__dict__))
        if args.host:
            print(host(**args.__dict__))

