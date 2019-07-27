#!/usr/bin/python

try:
    import unittest
    unittest.TextTestResult
except AttributeError:
    import unittest2 as unittest
    unittest.TextTestResult

import ram.symbols

class SymbolsTestCase(unittest.TestCase):
    """cycling"""

    def test_empty_cycle_run(self):
        """empty ram.symbols"""
        assert str(ram.symbols()) == ""

    def test_symbols_copy_of(self):
        """symbols copy of"""

        symbols = ram.symbols({'xxx.yyy': {'zzz.www': '_'}})
        assert symbols == {'xxx': {'yyy': {'zzz': {'www': '_'}}}}

        symbols.update({'xxx': {'yyy.zzz': '_'}})
        assert symbols == {'xxx': {'yyy': {'zzz': '_'}}}

        symbols.update({'xxx.www': '_'})
        assert symbols == {'xxx': {'yyy': {'zzz': '_'}, 'www': '_'}}


class StructsTestCase(unittest.TestCase):
    """structs"""

    def setUp(self):
        self.symbols = ram.symbols()
        self.symbols['root']['strings'] = '_'
        self.symbols['root']['present']['sub'] = '_'

    def test_present_sub_get(self):
        """get present subkeys"""

        assert self.symbols['root.present.sub'] == '_'
        assert self.symbols['root']['present']['sub'] == '_'
        assert self.symbols['root', 'present', 'sub'] == '_'
        assert self.symbols['root', 'present']['sub'] == '_'
        assert self.symbols['root']['present', 'sub'] == '_'

        present = self.symbols['root.present']
        assert present['sub'] == '_'

        present = self.symbols['root']['present']
        assert present['sub'] == '_'

        present = self.symbols['root', 'present']
        assert present['sub'] == '_'

        root = self.symbols['root']
        assert root['present.sub'] == '_'
        assert root['present']['sub'] == '_'
        assert root['present', 'sub'] == '_'

    def test_chained_sub_set(self):
        """set contain subkeys"""

        self.symbols['root.contain.sub'] = 'flat'
        assert self.symbols['root.contain.sub'] == 'flat'

        del self.symbols['root.contain.sub']
        assert self.symbols['root.contain.sub'] == ''
        assert self.symbols['root.contain'] == ''

        self.symbols['root']['contain']['sub'] = 'node'
        assert self.symbols['root']['contain']['sub'] == 'node'

        del self.symbols['root']['contain']['sub']
        assert self.symbols['root']['contain']['sub'] == ''
        assert self.symbols['root']['contain'] == ''

        self.symbols['root', 'contain', 'sub'] = 'list'
        assert self.symbols['root', 'contain', 'sub'] == 'list'

        del self.symbols['root', 'contain', 'sub']
        assert self.symbols['root', 'contain', 'sub'] == ''
        assert self.symbols['root', 'contain'] == ''

        self.symbols['root', 'contain']['sub'] = 'lide'
        assert self.symbols['root', 'contain']['sub'] == 'lide'

        del self.symbols['root', 'contain']['sub']
        assert self.symbols['root', 'contain']['sub'] == ''
        assert self.symbols['root', 'contain'] == ''

        self.symbols['root']['contain', 'sub'] = 'nost'
        assert self.symbols['root']['contain', 'sub'] == 'nost'

        del self.symbols['root']['contain', 'sub']
        assert self.symbols['root']['contain', 'sub'] == ''
        assert self.symbols['root']['contain'] == ''

    def test_missing_sub_get(self):
        """get missing subkeys"""

        assert self.symbols['root.missing.sub'] == ''
        assert self.symbols['root']['missing']['sub'] == ''
        assert self.symbols['root', 'missing', 'sub'] == ''
        assert self.symbols['root', 'missing']['sub'] == ''
        assert self.symbols['root']['missing', 'sub'] == ''

        missing = self.symbols['root.missing']
        assert missing['sub'] == ''

        missing = self.symbols['root']['missing']
        assert missing['sub'] == ''

        missing = self.symbols['root', 'missing']
        assert missing['sub'] == ''

        root = self.symbols['root']
        assert root['missing.sub'] == ''
        assert root['missing']['sub'] == ''
        assert root['missing', 'sub'] == ''

    def test_missing_top_get(self):
        """get missing topkeys"""

        assert self.symbols['none.missing.sub'] == ''
        assert self.symbols['none']['missing']['sub'] == ''
        assert self.symbols['none', 'missing', 'sub'] == ''
        assert self.symbols['none', 'missing']['sub'] == ''
        assert self.symbols['none']['missing', 'sub'] == ''

        missing = self.symbols['none.missing']
        assert missing['sub'] == ''

        missing = self.symbols['none']['missing']
        assert missing['sub'] == ''

        missing = self.symbols['none', 'missing']
        assert missing['sub'] == ''

        none = self.symbols['none']
        assert none['missing.sub'] == ''
        assert none['missing']['sub'] == ''
        assert none['missing', 'sub'] == ''

    def test_strings_sub_get(self):
        """get strings subkeys"""

        with self.assertRaises(TypeError):
            self.symbols['root.strings.sub']

        with self.assertRaises(TypeError):
            self.symbols['root']['strings']['sub']

        with self.assertRaises(TypeError):
            self.symbols['root', 'strings', 'sub']

        with self.assertRaises(TypeError):
            self.symbols['root', 'strings']['sub']

        with self.assertRaises(TypeError):
            self.symbols['root']['strings', 'sub']

        strings = self.symbols['root.strings']
        with self.assertRaises(TypeError):
            strings['sub']

        strings = self.symbols['root']['strings']
        with self.assertRaises(TypeError):
            strings['sub']

        strings = self.symbols['root', 'strings']
        with self.assertRaises(TypeError):
            strings['sub']

        root = self.symbols['root']
        with self.assertRaises(TypeError):
            root['strings', 'sub']
        with self.assertRaises(TypeError):
            root['strings']['sub']
        with self.assertRaises(TypeError):
            root['strings', 'sub']


    def test_strings_sub_set(self):
        """set string subkeys"""

        with self.assertRaises(TypeError):
            self.symbols['root.strings.sub'] = '_'

        with self.assertRaises(TypeError):
            self.symbols['root']['strings']['sub'] = '_'

        with self.assertRaises(TypeError):
            self.symbols['root', 'strings', 'sub'] = '_'

        with self.assertRaises(TypeError):
            self.symbols['root', 'strings']['sub'] = '_'

        with self.assertRaises(TypeError):
            self.symbols['root']['strings', 'sub'] = '_'

        strings = self.symbols['root.strings']
        with self.assertRaises(TypeError):
            strings['sub'] = '_'

        strings = self.symbols['root']['strings']
        with self.assertRaises(TypeError):
            strings['sub'] = '_'

        strings = self.symbols['root', 'strings']
        with self.assertRaises(TypeError):
            strings['sub'] = '_'

        root = self.symbols['root']
        with self.assertRaises(TypeError):
            root['strings', 'sub'] = '_'
        with self.assertRaises(TypeError):
            root['strings']['sub'] = '_'
        with self.assertRaises(TypeError):
            root['strings', 'sub'] = '_'


    def test_strings_sub_del(self):
        """del string subkeys"""

        with self.assertRaises(TypeError):
            del self.symbols['root.strings.sub']

        with self.assertRaises(TypeError):
            del self.symbols['root']['strings']['sub']

        with self.assertRaises(TypeError):
            del self.symbols['root', 'strings', 'sub']

        with self.assertRaises(TypeError):
            del self.symbols['root', 'strings']['sub']

        with self.assertRaises(TypeError):
            del self.symbols['root']['strings', 'sub']

        strings = self.symbols['root.strings']
        with self.assertRaises(TypeError):
            del strings['sub']

        strings = self.symbols['root']['strings']
        with self.assertRaises(TypeError):
            del strings['sub']

        strings = self.symbols['root', 'strings']
        with self.assertRaises(TypeError):
            del strings['sub']

        root = self.symbols['root']
        with self.assertRaises(TypeError):
            del root['strings', 'sub']
        with self.assertRaises(TypeError):
            del root['strings']['sub']
        with self.assertRaises(TypeError):
            del root['strings', 'sub']


    def test_symbols_of_data(self):
        """symbols of data"""

        self.assertIsInstance(self.symbols, dict)
        self.assertIsInstance(self.symbols['root'], dict)
        self.assertIsInstance(self.symbols['root']['present'], dict)
        self.assertIsInstance(self.symbols['root']['present']['sub'], str)
        self.assertIsInstance(self.symbols['root']['missing']['sub'], str)

        assert self.symbols == {'root': {'present': {'sub': '_'}, 'strings': '_'}}
        assert self.symbols['root'] == {'present': {'sub': '_'}, 'strings': '_'}
        assert self.symbols['root']['present'] == {'sub': '_'}
        assert self.symbols['root', 'present'] == {'sub': '_'}
        assert self.symbols['root.present'] == {'sub': '_'}


    def test_chained_sub_key(self):
        """chained sub get"""

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings'))
        assert len(self.symbols['root']) == 2

        assert sorted(self.symbols['root.present']) == sorted(('sub',))
        assert len(self.symbols['root.present']) == 1

        assert sorted(self.symbols['root.missing']) == sorted(())
        assert len(self.symbols['root.missing']) == 0

        self.symbols['root.chained'] = ''

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings'))
        assert len(self.symbols['root']) == 2

        assert sorted(self.symbols['root.chained']) == sorted(())
        assert len(self.symbols['root.chained']) == 0

        self.symbols['root.chained.sub'] = '_'
        del self.symbols['root.chained']

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings'))
        assert len(self.symbols['root']) == 2

        assert sorted(self.symbols['root.chained']) == sorted(())
        assert len(self.symbols['root.chained']) == 0

        self.symbols['root.chained.sub'] = '_'
        self.symbols['root.chained.top'] = '_'

        del self.symbols['root.chained.sub']

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings', 'chained'))
        assert len(self.symbols['root']) == 3

        assert sorted(self.symbols['root.chained']) == sorted(('top',))
        assert len(self.symbols['root.chained']) == 1

        del self.symbols['root.chained.top']

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings'))
        assert len(self.symbols['root']) == 2

        assert sorted(self.symbols['root.chained']) == sorted(())
        assert len(self.symbols['root.chained']) == 0

        self.symbols['root.chained.sub'] = '_'
        self.symbols['root.chained.top'] = '_'
        self.symbols['root.chained'] = None

        assert sorted(self.symbols) == sorted(('root',))
        assert len(self.symbols) == 1

        assert sorted(self.symbols['root']) == sorted(('present', 'strings'))
        assert len(self.symbols['root']) == 2

        assert sorted(self.symbols['root.chained']) == sorted(())
        assert len(self.symbols['root.chained']) == 0


    def test_contain_sub_key(self):
        """contain sub key"""

        self.assertIn('root', self.symbols)
        self.assertNotIn('none', self.symbols)

        self.assertIn('root.present', self.symbols)
        self.assertNotIn('root.missing', self.symbols)

        self.assertIn('root.present.sub', self.symbols)
        self.assertNotIn('root.missing.sub', self.symbols)
        self.assertNotIn('root.present.top', self.symbols)

        self.assertIn(('root', 'present', 'sub'), self.symbols)
        self.assertNotIn(('root', 'missing', 'sub'), self.symbols)
        self.assertNotIn(('root', 'present', 'top'), self.symbols)

        self.assertIn('present', self.symbols['root'])
        self.assertIn('present.sub', self.symbols['root'])
        self.assertIn(('present','sub'), self.symbols['root'])
        self.assertNotIn('missing', self.symbols['root'])
        self.assertNotIn('missing.sub', self.symbols['root'])
        self.assertNotIn(('missing', 'sub'), self.symbols['root'])
        self.assertNotIn('present.top', self.symbols['root'])
        self.assertNotIn(('present', 'top'), self.symbols['root'])

        self.assertIn('sub', self.symbols['root.present'])
        self.assertIn('sub', self.symbols['root']['present'])
        self.assertIn('sub', self.symbols['root', 'present'])
        self.assertNotIn('sub', self.symbols['root.missing'])
        self.assertNotIn('sub', self.symbols['root']['missing'])
        self.assertNotIn('sub', self.symbols['root', 'missing'])
        self.assertNotIn('top', self.symbols['root.present'])
        self.assertNotIn('top', self.symbols['root']['present'])
        self.assertNotIn('top', self.symbols['root', 'present'])

        self.assertNotIn('strings.sub', self.symbols['root'])
        self.assertNotIn(('strings', 'sub'), self.symbols['root'])

        self.assertNotIn('sub.top', self.symbols['root.present'])
        self.assertNotIn(('sub','top'), self.symbols['root.present'])
        self.assertNotIn('sub.top', self.symbols['root']['present'])
        self.assertNotIn(('sub','top'), self.symbols['root']['present'])
        self.assertNotIn('sub.top', self.symbols['root', 'present'])
        self.assertNotIn(('sub','top'), self.symbols['root', 'present'])


    def test_parents_sub_key(self):
        """parents sub key"""

        root = self.symbols['root']

        present = self.symbols['root']['present']

        assert len(present) == 1
        assert sorted(present) == sorted(('sub',))

        self.assertNotIn('top', present)
        self.assertNotIn('present.top', root)
        self.assertNotIn(('present', 'top'), root)

        missing = self.symbols['root']['missing']

        assert len(missing) == 0
        assert sorted(missing) == sorted(())

        self.assertNotIn('top', missing)
        self.assertNotIn('missing.top', root)
        self.assertNotIn(('missing', 'top'), root)

        assert present['sub'] == '_'
        assert root['present.sub'] == '_'
        assert root['present']['sub'] == '_'
        assert root['present', 'sub'] == '_'
        assert self.symbols['root', 'present']['sub'] == '_'

        assert len(present) == 1
        assert sorted(present) == sorted(('sub',))

        self.assertIn('sub', present)
        self.assertIn('present.sub', root)
        self.assertIn(('present', 'sub'), root)

        present['new'] = '_'
        assert present['new'] == '_'
        assert root['present.new'] == '_'
        assert root['present']['new'] == '_'
        assert root['present', 'new'] == '_'
        assert self.symbols['root', 'present']['new'] == '_'

        assert len(present) == 2
        assert sorted(present) == sorted(('sub', 'new'))

        self.assertIn('new', present)
        self.assertIn('present.new', root)
        self.assertIn(('present', 'new'), root)

        del present['new']
        assert present['new'] == ''
        assert root['present.new'] == ''
        assert root['present']['new'] == ''
        assert root['present', 'new'] == ''
        assert self.symbols['root', 'present']['new'] == ''

        assert len(present) == 1
        assert sorted(present) == sorted(('sub',))

        self.assertNotIn('new', present)
        self.assertNotIn('present.new', root)
        self.assertNotIn(('present', 'new'), root)

        missing['new'] = '_'
        assert missing['new'] == '_'
        assert root['missing.new'] == '_'
        assert root['missing']['new'] == '_'
        assert root['missing', 'new'] == '_'
        assert self.symbols['root', 'missing']['new'] == '_'

        # ???: missing is symbols proxy and behaves like str
        # for methods like __len__ / __iter__ / __contains__

        #assert len(missing) == 1
        #assert sorted(missing) == sorted(('new',))

        #self.assertIn('new', missing)
        self.assertIn('missing.new', root)
        self.assertIn(('missing', 'new'), root)

        del missing['new']
        assert missing['new'] == ''
        assert root['missing.new'] == ''
        assert root['missing']['new'] == ''
        assert root['missing', 'new'] == ''
        assert self.symbols['root', 'missing']['new'] == ''

        assert len(missing) == 0
        assert sorted(missing) == sorted(())

        self.assertNotIn('new', missing)
        self.assertNotIn('missing.new', root)
        self.assertNotIn(('missing', 'new'), root)


    def test_symbols_key_str(self):
        """symbols key str"""

        with self.assertRaises(TypeError):
            self.symbols[None]

        with self.assertRaises(TypeError):
            self.symbols['root', None]

        with self.assertRaises(TypeError):
            self.symbols['root'][None]

        with self.assertRaises(TypeError):
            self.symbols['']

        with self.assertRaises(TypeError):
            self.symbols['root.']

        with self.assertRaises(TypeError):
            self.symbols['root', 'missing.']

        with self.assertRaises(TypeError):
            self.symbols['root']['missing.']

        with self.assertRaises(TypeError):
            self.symbols['root', 'missing', '']

        with self.assertRaises(TypeError):
            self.symbols['root']['missing']['']

        assert self.symbols['root']['my-keys'] == ''
        assert self.symbols['root']['my_keys'] == ''

        assert self.symbols['root', 'my-keys'] == ''
        assert self.symbols['root', 'my_keys'] == ''


if __name__ == '__main__':
    unittest.main()
