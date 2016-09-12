# !/usr/bin/python
# encoding: iso-8859-1
import os
import tempfile

from lib.workflow import Workflow
from src import currencies_utilities

__author__ = 'Kennedy'

import unittest


class TestCurrenciesUtilities(unittest.TestCase):
    def setUp(self):
        self.wf = Workflow()
        self.wf.clear_settings()
        self.wf.clear_data()
        self.wf.clear_cache()

    def test_fetch_currencies(self):
        currencies_file = os.path.join(tempfile.gettempdir(), 'test_currencies.csv')

        # Remove any previous file that could be leaked
        if os.path.exists(currencies_file):
            os.remove(currencies_file)

        # Check if there is no local copy
        self.assertFalse(os.path.exists(currencies_file), 'The local cache file was deleted')

        # Fetche new currencies
        fetched = currencies_utilities.fetch_currencies(currencies_file)
        self.assertTrue(fetched, "Must download new currencies")
        self.assertTrue(os.path.exists(currencies_file), 'The local cache file was downloaded succefully')
        self.assertGreater(os.path.getsize(currencies_file), 0, 'File has some content')

    def test_doesnt_need_to_update(self):
        currencies_file = os.path.join(tempfile.gettempdir(), 'test_currencies_not_need_to_update.csv')

        # Clean any file that could be leaked
        if (os.path.exists(currencies_file)):
            os.remove(currencies_file)
        self.assertFalse(os.path.exists(currencies_file), 'The local cache file was deleted')

        # Fetch new files
        fetched = currencies_utilities.fetch_currencies(currencies_file)
        self.assertTrue(fetched, "Must fetch new currencies")

        # Check if is valid with simple validation
        self.assertTrue(os.path.exists(currencies_file), 'The local cache file was downloaded succefully')
        self.assertGreater(os.path.getsize(currencies_file), 0, 'File has some content')

        # Try to fetch again, must not fetch since should be equals
        fetched = currencies_utilities.fetch_currencies(currencies_file)
        self.assertFalse(fetched, "Must not fetch new currencies")
