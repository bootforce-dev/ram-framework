try:
    import unittest
    unittest.TextTestResult
except AttributeError:
    import unittest2 as unittest
    unittest.TextTestResult


import os
import sys
import subprocess

import ram.console


class CaptureTestCase(unittest.TestCase):

    def setUp(self):
        self.bufferize = ram.console.Bufferize()
        self.arrowline = ram.console.FancyLine('<<<', '>>>')
        self.starsline = ram.console.FancyLine(' *** ')

    def test_capture_buffer(self):
        with ram.console.capture(0, handlers=[self.bufferize]):
            with ram.console.capture(0, handlers=[self.arrowline]):
                with ram.console.capture(1, handlers=[self.starsline]):
                    print 'Start'

                    print >> sys.stdout, 'Aimed'
                    os.system("sh -c 'echo Subsh'")

                    os.system('echo Shell')
                    os.system('echo Sherr >&2')
                    os.system('echo Shred >/dev/stderr')

                    subprocess.call('echo Subps', shell=True)
                    subprocess.call('echo Subed >&2', shell=True)
                    subprocess.call(['echo', 'Subss'])

                    print >> sys.stderr, 'Error'

        lines = list(self.bufferize)
        assert len(lines) == 10

        assert lines[0] == "<<< *** Start *** >>>"
        assert lines[1] == "<<< *** Aimed *** >>>"
        assert lines[2] == "<<< *** Subsh *** >>>"
        assert lines[3] == "<<< *** Shell *** >>>"
        assert lines[4] == "<<< *** Sherr *** >>>"
        assert lines[5] == "<<< *** Shred *** >>>"
        assert lines[6] == "<<< *** Subps *** >>>"
        assert lines[7] == "<<< *** Subed *** >>>"
        assert lines[8] == "<<< *** Subss *** >>>"
        assert lines[9] == "<<< *** Error *** >>>"


if __name__ == '__main__':
    unittest.main()
