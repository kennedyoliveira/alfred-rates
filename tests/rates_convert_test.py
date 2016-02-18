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
        rates.log = self.wf.logger

    def tearDown(self):
        pass

    def test_full_convert(self):
        with patch.object(sys, 'argv', ['program', '100 BRL CLP']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(Brazilian real) -> (Chilean peso) with rate'), -1)

    def test_full_convert_multi_query(self):
        with patch.object(sys, 'argv', ['program', '100 BRL CLP; 100 USD BRL; 100 GBP CAD']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 3)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(Brazilian real) -> (Chilean peso) with rate'), -1)
        self.assertNotEqual(self.wf._items[1].subtitle.find('(United States dollar) -> (Brazilian real) with rate'), -1)
        self.assertNotEqual(self.wf._items[2].subtitle.find('(British pound [B]) -> (Canadian dollar) with rate'), -1)

    def test_inverted_full_convert(self):
        with patch.object(sys, 'argv', ['program', '100 CLP BRL']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(Chilean peso) -> (Brazilian real) with rate'), -1)

    def test_convert_from_default_to_other(self):
        with patch.object(sys, 'argv', ['program', '100 CLP']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(Brazilian real) -> (Chilean peso) with rate'), -1)

    def test_convert_from_default_to_other_multi_query(self):
        with patch.object(sys, 'argv', ['program', '100 BRL CLP; 100 GBP; 100 GBP CAD']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 3)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(Brazilian real) -> (Chilean peso) with rate'), -1)
        self.assertNotEqual(self.wf._items[1].subtitle.find('(Brazilian real) -> (British pound [B]) with rate'), -1)
        self.assertNotEqual(self.wf._items[2].subtitle.find('(British pound [B]) -> (Canadian dollar) with rate'), -1)

    def test_convert_from_other_to_default(self):
        with patch.object(sys, 'argv', ['program', 'CLP 100']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(Chilean peso) -> (Brazilian real) with rate'), -1)

    def test_convert_from_other_to_default_multi_query(self):
        with patch.object(sys, 'argv', ['program', '100 BRL CLP; GBP 100; 100 GBP CAD']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 3)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(Brazilian real) -> (Chilean peso) with rate'), -1)
        self.assertNotEqual(self.wf._items[1].subtitle.find('(British pound [B]) -> (Brazilian real) with rate'), -1)
        self.assertNotEqual(self.wf._items[2].subtitle.find('(British pound [B]) -> (Canadian dollar) with rate'), -1)

    def test_convert_from_default_to_other_without_values(self):
        self.wf.settings[rates.SETTINGS_DEFAULT_CURRENCY] = 'USD'

        with patch.object(sys, 'argv', ['program', 'BRL']):
            rates.main(self.wf)

        self.assertTrue(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(United States dollar) -> (Brazilian real)'), -1)

    def test_convert_from_detault_to_other_without_values_multi_query(self):
        self.wf.settings[rates.SETTINGS_DEFAULT_CURRENCY] = 'USD'

        with patch.object(sys, 'argv', ['program', '100 BRL CLP; GBP; 100 GBP CAD']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 3)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(Brazilian real) -> (Chilean peso) with rate'), -1)
        self.assertNotEqual(self.wf._items[1].subtitle.find('(United States dollar) -> (British pound [B]) with rate'), -1)
        self.assertNotEqual(self.wf._items[2].subtitle.find('(British pound [B]) -> (Canadian dollar) with rate'), -1)

    def test_invalid_currency_number_to_convert(self):
        with patch.object(sys, 'argv', ['program', 'zupa BRL USD']):
            ret = rates.main(self.wf)
        self.assertTrue(ret, 100)

    def test_invalid_currency_number_to_convert_using_default(self):
        with patch.object(sys, 'argv', ['program', 'zupa BRL']):
            ret = rates.main(self.wf)
        self.assertTrue(ret, 100)

    def test_invalid_argument(self):
        with patch.object(sys, 'argv', ['program', 'zupa']):
            ret = rates.main(self.wf)
        # 100 means auto complete
        self.assertEqual(ret, 100)

    def test_convert_case_insensitive(self):
        with patch.object(sys, 'argv', ['program', '1 brl clp']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(Brazilian real) -> (Chilean peso) with rate'), -1)

    def test_convert_eur(self):
        # This test is because of a bug with displaying EUR symbol
        with patch.object(sys, 'argv', ['program', '1 USD EUR']):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertNotEqual(self.wf._items[0].subtitle.find('(United States dollar) -> (Euro) with rate'), -1)

    def test_extract_filter_params(self):
        currencies = rates.get_currencies()

        # List of tuple (Params, Expected Result)

        test_itens = [('100 Braz'.split(), ['Braz']),
                      (['Braz'], ['Braz']),
                      ('100 CLP United States'.split(), ['United', 'States']),
                      ([''], []),
                      ([], [])]

        for test in test_itens:
            resp = rates.extract_filter_params(test[0], currencies)
            self.assertEqual(resp, test[1])

    def test_convert_high_rates(self):
        # Test the problem reported in #14, converting from idr to usd
        # Yahoo will return as rate 0.0001, because it's the minimum
        # but the rate is something around 0.000007...
        with patch.object(sys, 'argv', ['program', '1 idr usd']):
                rates.main(self.wf)
        # must have only 1 item
        self.assertEqual(len(self.wf._items), 1)
        # must not be rate 0.0001 for query
        self.assertEqual(self.wf._items[0].subtitle.find('(Indonesian rupiah) -> (United States dollar) with rate 0.0001 for query'), -1)
        # must be a conversion message
        self.assertNotEqual(self.wf._items[0].subtitle.find('(Indonesian rupiah) -> (United States dollar) with rate'), -1)

if __name__ == '__main__':
    unittest.main()
