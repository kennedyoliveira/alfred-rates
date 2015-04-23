import rates

__author__ = 'Kennedy'

import unittest
import os

from workflow import Workflow


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
        self.assertEquals(len(currency_info), 3)

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
            self.assertTrue(info['Flag'], 'No flag for the currency {}'.format(info))
            self.assertTrue(os.path.exists(os.path.join('flags', info['Flag'])),
                            'No flag file for the currency {}'.format(info))

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
        self.assertTrue(rates.validate_currencies('BRL', 'USD', currencies, self.wf))
        self.assertFalse(rates.validate_currencies('BRL', 'USDD', currencies, self.wf))
        self.assertEqual(len(self.wf._items), 1)
        self.assertEqual(self.wf._items[0].title, 'USDD not found')
        self.assertFalse(rates.validate_currencies('BRLL', 'USD', currencies, self.wf))


if __name__ == '__main__':
    unittest.main()