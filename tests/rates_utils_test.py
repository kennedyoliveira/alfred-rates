import sys

import rates

__author__ = 'Kennedy'

import unittest

from workflow import Workflow
from mock import patch


class RatesCurrencyTest(unittest.TestCase):
    def setUp(self):
        self.wf = Workflow()
        self.wf.clear_settings()
        self.wf.clear_data()
        self.wf.clear_cache()
        rates.log = self.wf.logger

    def tearDown(self):
        pass

    def testLoadCurrencyInfo(self):
        currency_info = rates.get_currencies()

        # Checks if all itens have all info that is used by the script
        for currency, info in currency_info.iteritems():
            self.assertIn('Id', info, 'No ID for currency {}'.format(info))
            self.assertTrue(info['Id'], 'None ID specified for currency {}'.format(info))
            self.assertIn('Name', info, 'No Name for currency {}'.format(info))
            self.assertTrue(info['Name'], 'No Name for currency {}'.format(info))
            self.assertIn('Code', info, 'No Code for currency {}'.format(info))
            self.assertTrue(info['Code'], 'No Code for currency {}'.format(info))
            self.assertIn('Simbol', info, 'No Simbol for currency {}'.format(info))
            self.assertTrue(info['Simbol'], 'No Simbol for currency {}'.format(info))
            self.assertIn('Country', info, 'No Country for currency {}'.format(info))
            self.assertTrue(info['Country'], 'No Country for currency {}'.format(info))
            self.assertIn('Flag', info, 'No Flag for currency {}'.format(info))

    def test_is_float(self):
        tests = [(1, True),
                 ('asd', False),
                 (1.5, True),
                 ('1', True),
                 ('1', True)]

        for test in tests:
            self.assertEqual(rates.is_float(test[0]), test[1])

    def test_validate_currencies(self):
        currencies = rates.get_currencies()
        self.assertTrue(rates.validate_currencies([], 'BRL', 'USD', currencies, self.wf))
        self.assertFalse(rates.validate_currencies([], 'BRL', 'USDD', currencies, self.wf))
        self.assertFalse(rates.validate_currencies([], 'BRLL', 'USD', currencies, self.wf))

    def test_clear_caches(self):
        self.wf.cache_data('test_cache', 'testing cache')
        self.wf.store_data('test_store', 'testing store')
        with patch.object(sys, 'argv', 'program --clear'.split()):
            rates.main(self.wf)
        self.assertEqual(len(self.wf._items), 1)
        self.assertEqual(self.wf._items[0].title, 'Caches cleared!')
        self.assertIsNone(self.wf.stored_data('test_store'))
        self.assertIsNone(self.wf.cached_data('test_cache'))

    def test_evaluate_math(self):

        tests = [
            (['100*3', '100'], ['300', '100']),
            (['135.3*2', '234.5-5'], ['270.6', '229.5']),
            (['123/2', '61.5*50'], ['61.5', '3075.0']),
            (['123.5*2.5'], ['308.75']),
            # (['123', '/2', '61.5*50'], ['61.5', '3075.0']),
            # (['123', '/', '2', '61.5*50'], ['61.5', '3075.0']),
            # (['123', '/2', '/', '2', '61.5*50'], ['30.75', '3075.0']),
            # (['123', '/2', '/', '2', '61.5*50', '/3', '*2'], ['30.75', '2050.0'])
            # (['123*', '2'], ['246'])
            # (['100*2', 'usd', 'brl'], ['200', 'usd', 'brl'])
        ]

        for t in tests:
            result = rates.evaluate_math(t[0])
            self.assertEqual(result, t[1])

    def test_fmt_number(self):
        tests = [
            ('100.00', '.', '100.00'),
            ('100.00', ',', '100,00'),
            ('1.000,00', '.', '1,000.00'),
            ('100', None, '100')
        ]

        for t in tests:
            result = rates.fmt_number(t[0], t[1])
            self.assertEqual(result, t[2])


if __name__ == '__main__':
    unittest.main()
