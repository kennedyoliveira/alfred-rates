# !/usr/bin/python
# encoding: iso-8859-1
import sys

__author__ = 'Kennedy'

import unittest

import rates
from workflow import Workflow
from mock import patch


class TestRatesSettings(unittest.TestCase):
    wf = None

    def setUp(self):
        self.wf = Workflow()
        self.wf.clear_settings()

    def tearDown(self):
        pass

    def test_default_currency(self):
        with patch.object(sys, 'argv', ['program', '--get-default-currency']):
            rates.main(self.wf)

        self.assertEqual(len(self.wf._items), 1)
        self.assertEqual(self.wf._items[0].title, 'No default currency.')

    def test_set_default_currency(self):
        with patch.object(sys, 'argv', ['program', '--set-default-currency', 'BRL']):
            rates.main(self.wf)

        self.assertEqual(self.wf.settings[rates.SETTINGS_DEFAULT_CURRENCY], 'BRL')

if __name__ == '__main__':
    unittest.main()