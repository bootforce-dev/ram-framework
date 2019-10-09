#!/usr/bin/python

try:
    import unittest
    unittest.TextTestResult
except AttributeError:
    import unittest2 as unittest
    unittest.TextTestResult


import ram.watches

import time


class WatchesTestCase(unittest.TestCase):
    """watches"""

    def setUp(self):
        pass

    def test_iterable_list(self):
        "enlist"

        with ram.watches.watch_iterable([1,2,3]) as w:
            assert bool(w) == True
            time.sleep(0.1)
            assert bool(w) == True
            assert w() == 1
            assert bool(w) == True
            assert w() == 2
            assert bool(w) == True
            assert w() == 3
            assert bool(w) == True
            assert w() == None
            assert bool(w) == False
            assert w() == None
            assert bool(w) == False

    def test_stdout_status(self):
        "stdout"

        with ram.watches.watch_stdout('cat /var/log/messages') as w:
            assert bool(w) == True
            time.sleep(0.1)
            assert bool(w) == True
            w()
            assert bool(w) == False
            w()

    def test_sleepy_stdout(self):
        "sleepy"

        with ram.watches.watch_stdout('for _ in `seq 1 3`; do echo $_; sleep 0.1; done') as w:
            assert bool(w) == True
            assert w().strip() == '1'
            assert bool(w) == True
            assert w().strip() == '2'
            assert bool(w) == True
            assert w().strip() == '3'
            assert bool(w) == True
            assert w().strip() == ''
            assert bool(w) == False
            assert w().strip() == ''

    def test_sleepy_finite(self):
        "finite"

        with ram.watches.watch_output('sleep 0.3; exit 1', timeout=0.1) as w:
            assert bool(w) == True
            time.sleep(0.1)
            assert bool(w) == True
            time.sleep(0.3)
            assert bool(w) == True
            try:
                w()
            except RuntimeError:
                assert True
            else:
                assert False
            assert bool(w) == True
            assert w() == None
            assert bool(w) == False
            assert w() == None


if __name__ == '__main__':
    unittest.main()
