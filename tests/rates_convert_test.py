# !/usr/bin/python
# encoding: iso-8859-1
__author__ = 'Kennedy'

import unittest

import sys
import rates
from mock import patch
from workflow import Workflow


class TestRatesConvert(unittest.TestCase):
    def setUp(self):
        self.wf = Workflow()
        self.wf.clear_settings()
        self.wf.clear_data()
        self.wf.clear_cache()
        self.wf.settings[rates.SETTINGS_DEFAULT_CURRENCY] = 'BRL'

    def tearDown(self):
        pass

    def test_full_convert(self):
        with patch.object(sys, 'argv', ['program', '100', 'BRL', 'CLP']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('BRL (Brazilian real) -> CLP (Chilean peso) with rate'), -1)

    def test_inverted_full_convert(self):
        with patch.object(sys, 'argv', ['program', '100', 'CLP', 'BRL']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('CLP (Chilean peso) -> BRL (Brazilian real) with rate'), -1)

    def test_convert_from_default_to_other(self):
        with patch.object(sys, 'argv', ['program', '100', 'CLP']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('BRL (Brazilian real) -> CLP (Chilean peso) with rate'), -1)

    def test_convert_from_other_to_default(self):
        with patch.object(sys, 'argv', ['program', 'CLP', '100']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('CLP (Chilean peso) -> BRL (Brazilian real) with rate'), -1)


if __name__ == '__main__':
    unittest.main()