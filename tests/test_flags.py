# !/usr/bin/python
# encoding: iso-8859-1
import os
from unittest import TestCase

from lib.workflow import Workflow
from src import rates

__author__ = 'Kennedy'


class TestFlags(TestCase):
    def setUp(self):
        self.wf = Workflow()
        self.wf.clear_settings()
        self.wf.clear_data()
        self.wf.clear_cache()
        rates.log = self.wf.logger
        rates.wf = self.wf

    def test_get_flag_for_currency(self):
        flag = rates.get_flag_for_currency('usd')

        self.assertTrue(os.path.exists(flag), 'The flag should exists')
        self.assertTrue(flag.find('_no_flag') == -1)

    def test_get_flag_non_existent_currency(self):
        flag_path = rates.get_flag_for_currency('zupao')

        self.assertTrue(flag_path.find('_no_flag.png') != -1, 'Should return a no flag file.')
        self.assertTrue(os.path.exists(flag_path), 'The flag "no flag" should exists')

    def test_all_currency_should_have_flags(self):
        currencies = rates.load_currency_info()

        for currency in currencies:
            flag_file = rates.get_flag_for_currency(currency)

            has_flag = flag_file.find('_no_flag.png') == -1

            if not has_flag:
                self.fail('The currency %s has no flag file!'.format(currency))
