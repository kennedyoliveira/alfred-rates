# !/usr/bin/python
# encoding: iso-8859-1
import argparse
import locale
import os
import re

__author__ = 'Kennedy'
__doc__ = """
A simple tool to convert between rates in many currencies.
"""

import sys
import urllib
import csv

from workflow import Workflow, web, ICON_ERROR, ICON_WARNING, ICON_INFO

# Locale settings for OS X
if sys.platform == 'darwin':
    locale.setlocale(locale.LC_ALL, 'en_US')
else:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Settings info
SETTINGS_DEFAULT_CURRENCY = 'default_currency'
STORED_DATA_CURRENCY_INFO = 'currency_info'

log = None

# Url for the YQL Rest API
api_url = 'https://query.yahooapis.com/v1/public/yql'

# Query for the exchange rates
rates_query = '?q=select * from yahoo.finance.xchange where pair in (:?)&format=json&env=store://datatables.org/alltableswithkeys'

# File with the currencies info
currencies_csv = 'currencies.csv'


def get_rates(src, dst):
    """
    Gets the current exchange rates from src to dst.

    :type src: str
    :type dst: str
    :rtype : float
    """
    if not dst:
        dst = ''

    request = '{}{}'.format(api_url, rates_query.replace(':?', '"{}{}"'.format(src, dst)))

    response = web.get(urllib.quote(request, ':/?&=*'))

    response.raise_for_status()

    rates = response.json()

    rate_resp = rates['query']['results']['rate']

    if rate_resp['Rate'] == 'N/A':
        return -1

    return float(rate_resp['Rate'])


def get_currencies():
    """
    Get the currency info from the csv withing the workflow
    TODO Load it from rest service
    :rtype : dict[str,dict]
    """
    currencies = {}

    with open(currencies_csv, mode='rU') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            currencies[row['Code']] = row

    return currencies


def load_currency_info(wf):
    """
    Loads the currency info

    :type wf: Workflow
    """
    moedas = wf.stored_data(STORED_DATA_CURRENCY_INFO)
    if not moedas:
        moedas = get_currencies()
        wf.store_data(STORED_DATA_CURRENCY_INFO, moedas)
    return moedas


def is_float(val):
    """
    Check if the given val can be converted to float

    :type val: object
    """
    try:
        float(val)
        return True
    except ValueError:
        return False


def validate_currencies(query, src, dst, currencies, wf):
    """
    Utility method to check if the currencies are valid.
    """
    if src not in currencies or dst not in currencies:
        show_autocomplete(query, currencies, wf)
        return False
    else:
        return True


def search_rate(src, dst, wf):
    """
    Search the rates from YQL rest service
    """
    conv = '{}{}'.format(src, dst)

    def get_rates_wrapper():
        return get_rates(src, dst)

    # Search and caches for 1 hour the current rates for the currency
    rate = wf.cached_data(conv, get_rates_wrapper, max_age=3600)
    return rate


def process_conversion(query, src, dst, val, currencies, wf):
    """
    Process the conversion from src to dst using the info withing currencies and return 0 with sucess and
    != 0 otherwise.

    :param wf: Alfred Workflow helper instance
    :type wf: Workflow
    :param currencies: Dictionary with info about currencies
    :type currencies: dict
    :type val: float
    :param val: Value to be converted
    :type dst: str
    :param dst: Destiny currency CODE, like BRL or CLP
    :type src: str
    :param src: Source currency CODE, like BRL or CLP
    """
    ####################################################################################################
    # Make the currency case insensitive
    ####################################################################################################
    if src:
        src = src.upper()
    if dst:
        dst = dst.upper()

    ####################################################################################################
    # Validate the currencies to check if its a currency or not
    ####################################################################################################
    if not validate_currencies(query, src, dst, currencies, wf):
        return 100

    rate = search_rate(src, dst, wf)

    if rate == -1:
        wf.add_item('No rating found for the especified currencies...', icon=ICON_ERROR)
        wf.send_feedback()
        return 1

    ####################################################################################################
    # Gets the currency info
    ####################################################################################################
    cur_src_name = currencies[src]['Name']
    cur_dst_name = currencies[dst]['Name']
    cur_dst_symbol = str.decode(currencies[dst]['Simbol'], encoding='utf-8')
    flag_file_icon = wf.workflowfile('flags/{}'.format(currencies[dst]['Flag']))

    if not val:
        val = 1

    converted_rate = locale.currency(val * rate, grouping=True, symbol=False)

    title = cur_dst_symbol + ' ' + converted_rate
    sub_title = u'{} ({}) -> {} ({}) with rate {}'.format(src, cur_src_name, dst, cur_dst_name, rate)

    wf.add_item(title, sub_title, valid=True, arg=converted_rate, icon=flag_file_icon)
    wf.send_feedback()
    return 0


def extract_filter_params(query, currencies):
    """
    Extracts the params from query to use to filter for currencies

    :param currencies: Dict with currencies
    :param query: A list with parameters from query
    :return: A lista with the words for use in the filter
    """
    query_parsed = []

    if not query:
        query_parsed

    matcher = re.compile(r'[^0-9]+')

    for word in query:
        # Probably the value
        if not matcher.match(word):
            continue
        # Probably a word
        else:
            # If its not a currency simbol, append to the query
            if word.upper() not in currencies:
                query_parsed.append(word)

    return query_parsed


def show_autocomplete(query, currencies, wf):
    """
    This fuction return a list of possible currencies
    based on the query

    :param query:
    :param currencies: Dict with all the
    :param wf:
    :return:
    """
    currencies_list = currencies.values()

    if query:
        query_parsed = extract_filter_params(query, currencies)

        if query_parsed:
            def key_for_currency(cur):
                return cur['Name'].decode('utf-8') + ' ' + cur['Code']

            currencies_list = wf.filter(' '.join(query_parsed), currencies_list, key=key_for_currency, min_score=20)

            # Removes all the query parsed strings used to filter
            for word in query_parsed:
                query.remove(word)

    if not currencies_list:
        wf.add_item('No currency found.')
    else:
        for currency in currencies_list:
            try:
                flag_file_icon = wf.workflowfile('flags/{}'.format(currency['Flag']))
            except UnicodeDecodeError:
                pass

            if not os.path.exists(flag_file_icon):
                flag_file_icon = wf.workflowfile('flags/_no_flag.png')

            autocomplete = ' '.join(query + [currency['Code'].decode('utf-8')])

            wf.add_item(title=currency['Name'].decode('utf-8'),
                        subtitle='{}'.format(currency['Code'].decode('utf-8')),
                        autocomplete=autocomplete,
                        icon=flag_file_icon)
    wf.send_feedback()


def main(wf):
    """
    Execute the script

    :type wf: Workflow
    """
    # Load the curency list
    currencies = load_currency_info(wf)

    ############################################################################################
    # Build the parser for the arguments
    ############################################################################################
    parser = argparse.ArgumentParser()

    parser.add_argument('--set-default-currency', dest='default_currency', default=None)
    parser.add_argument('--get-default-currency', dest='get_default_currency', default=None, action='store_true')
    parser.add_argument('--clear', default=None, action='store_true')
    parser.add_argument('--update', default=None, action='store_true')
    parser.add_argument('query', nargs='*')

    args = parser.parse_args(wf.args)

    ############################################################################################
    # Update the default currency
    ############################################################################################
    if args.default_currency:
        currency = args.default_currency.upper()

        if currency not in currencies:
            wf.add_item('You entered a invalid currency...', icon=ICON_ERROR)
            wf.send_feedback()
            return 1

        wf.settings[SETTINGS_DEFAULT_CURRENCY] = currency
        print currency
        return 0

    ############################################################################################
    # Get the default currency
    ############################################################################################
    if args.get_default_currency:
        if SETTINGS_DEFAULT_CURRENCY in wf.settings:
            wf.add_item('Your default currency is: {}'.format(wf.settings[SETTINGS_DEFAULT_CURRENCY]), icon=ICON_INFO)
            wf.send_feedback()
        else:
            wf.add_item('No default currency.', 'Please, use the ratesetcurrency to set the default currency first',
                        icon=ICON_WARNING, valid=True)
            wf.send_feedback()
        return 0

    ############################################################################################
    # Clean the caches
    ############################################################################################
    if args.clear:
        wf.reset()
        wf.add_item('Caches cleared!', icon=ICON_INFO)
        wf.send_feedback()
        return 0

    ############################################################################################
    # Update the workflow
    ############################################################################################
    if args.update:
        if wf.start_update():
            msg = 'Downloading and installing update ...'
        else:
            msg = 'No update available'

        wf.add_item(msg, icon=ICON_INFO)
        wf.send_feedback()
        return 20   

    ############################################################################################
    # Checks if an update is available
    ############################################################################################
    if wf.update_available:
        log.debug('There is a new update available...')

        update_info = wf.cached_data('__workflow_update_status', None)

        update_version = ''

        if update_info and 'version' in update_info:
            update_version = update_info['version']

        wf.add_item('There is a new update available! {} {}'.format('Version: ', update_version),
                    'We recommend updating the workflow by running rateupdate!')
        wf.send_feedback()
        sys.exit(10)

    ############################################################################################
    # Chech for convert actions
    ############################################################################################
    query = args.query

    if query and len(query) == 1 and query[0].upper() in currencies:
        ############################################################################################
        # Show the currency against the default currency or USD if none specified
        ############################################################################################
        currency = query[0]

        default_currency = 'USD'

        # If Has a default currency settings, use it, otherwise keeps the default USD
        if SETTINGS_DEFAULT_CURRENCY in wf.settings:
            default_currency = wf.settings[SETTINGS_DEFAULT_CURRENCY]

        return process_conversion(query, default_currency, currency, None, currencies, wf)
    elif args.query and len(args.query) == 3:
        ####################################################################################################
        # Convert the currencies
        ####################################################################################################
        if not is_float(query[0]):
            show_autocomplete(query, currencies, wf)
            return 100

        val = float(query[0])
        src = query[1]
        dst = query[2]

        return process_conversion(query, src, dst, val, currencies, wf)
    elif args.query and len(args.query) == 2:
        ####################################################################################################
        # Convert a value to the default currency or from the default currency to the other especified
        ####################################################################################################
        if not (is_float(query[0]) or is_float(query[1])):
            show_autocomplete(query, currencies, wf)
            return 100

        currency_dst = wf.settings.get(SETTINGS_DEFAULT_CURRENCY, 'USD')

        # First parameter is the value, means should convert from local default currency to the one specified in the query
        if is_float(query[0]) and not is_float(query[1]):
            currency_src = currency_dst
            currency_dst = query[1]
            val = float(query[0])
        # Second parameter is the value, means should convert from the query currency to the default one
        elif not is_float(query[0]) and is_float(query[1]):
            currency_src = query[0]
            val = float(query[1])
        else:
            wf.add_item('Wrong arguments ...', icon=ICON_ERROR)
            wf.send_feedback()
            return 1

        return process_conversion(query, currency_src, currency_dst, val, currencies, wf)
    else:
        show_autocomplete(query, currencies, wf)
        return 100


if __name__ == '__main__':
    update_settings = {'github_slug': 'kennedyoliveira/alfred-rates', 'frequency': 1}

    wf = Workflow(update_settings=update_settings)
    log = wf.logger
    sys.exit(wf.run(main))