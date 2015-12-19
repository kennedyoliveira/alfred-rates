# !/usr/bin/python
# encoding: iso-8859-1

import unittest
from rates import get_currency_name

__author__ = 'Kennedy'


class RatesFmtTest(unittest.TestCase):
    def testGetCurrencyNameWithoutCharset(self):
        currency_info = {'Name': 'United States dollar'}
        currency_name = get_currency_name(currency_info)

        self.assertEqual('United States dollar', currency_name)

    def testGetCurrencyNameWithCharset(self):
        currency_info = {'Name': 'Vietnamese ??ng', 'Charset': 'UTF-8'}
        currency_name = get_currency_name(currency_info)

        self.assertEqual('Vietnamese ??ng', currency_name)
