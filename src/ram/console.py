#!/usr/bin/python

import sys
import select


def waitkey(message=None, timeout=0):

    def _press(waitfor):
        return select.select([sys.stdin], [], [], waitfor) == ([sys.stdin], [], [])

    def _drain():
        while _press(0):
            sys.stdin.read(1)

    def _write(s):
        sys.stdout.write(s)
        sys.stdout.flush()

    if message is None:
        message = "Press ENTER to continue"

    press = False

    try:
        _drain()
        _write(message)

        if timeout:
            _write(':')
        else:
            _write(' ... ')

        waitfor = 0
        while not timeout or waitfor < abs(timeout):
            press = _press(1)
            if press:
                break
            if timeout:
                _write('.')
                waitfor += 1
        else:
            raise OverflowError(timeout)
    finally:
        if not press:
            _write('\n')
        _drain()
