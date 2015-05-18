# !/usr/bin/python
# encoding: iso-8859-1
__author__ = 'Kennedy'

import unittest

import rates
from workflow import Workflow


class RatesFmtTest(unittest.TestCase):
    def setUp(self):
        self.wf = Workflow()
        self.wf.clear_settings()
        self.wf.clear_data()
        self.wf.clear_cache()
        self.wf.settings[rates.SETTINGS_DEFAULT_CURRENCY] = 'BRL'
        rates.log = self.wf.logger

    def tearDown(self):
        pass

    def testFmtNumberComma(self):
        self.wf.settings[rates.SETTINGS_DEFAULT_NUMBER_DIVISOR] = ','
        result = rates.format_result(self.wf, 1001.0123)
        self.assertEquals(result, '1.001,0123')

    def testFmtNumberDot(self):
        self.wf.settings[rates.SETTINGS_DEFAULT_NUMBER_DIVISOR] = '.'
        result = rates.format_result(self.wf, 1001.0123)
        self.assertEquals(result, '1,001.0123')


if __name__ == '__main__':
    unittest.main()
