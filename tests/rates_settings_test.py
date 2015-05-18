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
        rates.log = self.wf.logger

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

    def test_set_invalid_currency(self):
        with patch.object(sys, 'argv', 'program --set-default-currency zupa'.split()):
            rates.main(self.wf)

        self.assertEqual(len(self.wf._items), 1)
        self.assertEqual(self.wf._items[0].title, 'You entered a invalid currency...')

    def test_get_default_currency(self):
        self.wf.settings[rates.SETTINGS_DEFAULT_CURRENCY] = 'BRL'
        with patch.object(sys, 'argv', 'program --get-default-currency'.split()):
            rates.main(self.wf)

        self.assertEqual(len(self.wf._items), 1)
        self.assertEqual(self.wf._items[0].title, 'Your default currency is: BRL')

    def test_set_default_divisor_comma(self):
        with patch.object(sys, 'argv', 'program --set-default-divisor ,'.split()):
            rates.main(self.wf)

        self.assertEqual(self.wf._items[0].title, "Default divisor updated to: ','")

    def test_set_default_divisor_dot(self):
        with patch.object(sys, 'argv', 'program --set-default-divisor .'.split()):
            rates.main(self.wf)

        self.assertEqual(self.wf._items[0].title, "Default divisor updated to: '.'")


if __name__ == '__main__':
    unittest.main()
