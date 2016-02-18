# !/usr/bin/python
# encoding: iso-8859-1

"""
A simple tool to convert between rates in many currencies.
"""
from __future__ import division

__author__ = 'Kennedy Oliveira'

import argparse
import locale
import os
import re
import urllib
import csv
import currencies_utilities
import sys
import decimal
from decimal import Decimal
from workflow import Workflow, web, ICON_ERROR, ICON_WARNING, ICON_INFO
from collections import deque

# Locale settings for OS X
if sys.platform == 'darwin':
    locale.setlocale(locale.LC_ALL, 'en_US')
else:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Settings info
SETTINGS_DEFAULT_CURRENCY = 'default_currency'
SETTINGS_DEFAULT_NUMBER_DIVISOR = 'default_divisor'
STORED_DATA_CURRENCY_INFO = 'currency_info'

log = None
wf = None

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

    return Decimal(rate_resp['Rate'])


def get_currencies():
    """
    Get the currency info from the csv withing the workflow

    :rtype : dict[str,dict]
    """
    currencies = {}

    currencies_utilities.fetch_currencies()
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
        log.debug('Loading currency data...')
        moedas = get_currencies()
        wf.store_data(STORED_DATA_CURRENCY_INFO, moedas)
    return moedas


def is_float(val):
    """
    Check if the given val can be converted to float

    :type val: str
    """
    try:
        float(val)
        return True
    except ValueError:
        return False


def validate_currencies(queries, query, src, dst, currencies, wf):
    """
    Utility method to check if the currencies are valid.
    """
    if src not in currencies or dst not in currencies:
        show_autocomplete(queries, query, currencies, wf)
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

    # Special FIX
    if Decimal('0.0001').compare(rate) == 0:
        # Special treatment because yahoo returns 0.0001 at minimum, so i will do the process inverted to calculed
        # the rates myself
        log.debug('Rates for {} -> {} is equal to 0.0001, calculating inverted...'.format(src, dst))
        inverted_rate = search_rate(dst, src, wf)
        rate = decimal.Decimal(1) / inverted_rate

    return rate


def get_currency_name(currency):
    """
    :param currency:
    """
    if 'Charset' not in currency or not currency['Charset']:
        return currency['Name']
    else:
        return currency['Name'].decode(currency['Charset'])


def process_conversion(queries, query, src, dst, val, currencies, wf):
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
    if not validate_currencies(queries, query, src, dst, currencies, wf):
        return 100

    rate = search_rate(src, dst, wf)

    if rate == -1:
        wf.add_item('No exchange rate found for the especified currencies...', icon=ICON_ERROR)
        return 1

    ####################################################################################################
    # Gets the currency info
    ####################################################################################################
    src_currency_info = currencies[src]
    dst_currency_info = currencies[dst]

    cur_src_name = get_currency_name(src_currency_info)
    cur_dst_name = get_currency_name(dst_currency_info)

    cur_dst_symbol = str.decode(dst_currency_info['Simbol'], encoding='utf-8')
    flag_file_icon = wf.workflowfile('flags/{}'.format(dst_currency_info['Flag']))

    if not val:
        val = 1

    converted_rate = Decimal(val) * rate

    decimal_places = get_decimal_places_to_use(rate)

    fmt_converted_rate = format_result(wf, converted_rate, decimal_places)

    # module 1 will result in just the decimal part, if the decimal part is 0, then i'll show only 2 decimal places
    if (rate % Decimal(1)).compare(Decimal('0')) == 0:
        fmt_rate = format_result(wf, rate, 2)
    else:
        fmt_rate = format_result(wf, rate, decimal_places)

    title = cur_dst_symbol + ' ' + fmt_converted_rate
    sub_title = u'({}) -> ({}) with rate {} for query: {}'.format(cur_src_name, cur_dst_name, fmt_rate,
                                                                  ' '.join(query).upper())

    wf.add_item(title, sub_title, valid=True, arg=str(converted_rate), icon=flag_file_icon)

    ############################################################################################
    # Checks if an update is available, and add it to the output
    ############################################################################################
    if wf.update_available:
        handle_check_update(wf)

    return 0


def get_decimal_places_to_use(rate):
    '''
    get the total numbers of decimals to use after the decimal period
    Ex: in the rate 4.25431543 there are 8 decimals after the decimal
    period, so the result of this method will be 8.
    If there are less than 4 decimals, the return will be 4 as default

    :param rate The exchange rate
    :type rate Decimal
    '''
    log.debug("Checking decimal places for number: [{}]".format(rate))

    # remove the integer part
    decimal_part = rate % Decimal(1)
    log.debug("Removed integer part: [{}]".format(decimal_part))

    # get the total of decimal numbers
    # the minus 2 ignores the 0. of the number
    total_decimal_numbers = len(str(decimal_part)) - 2

    # if there are more than 4 decimal numbers after the decimal period i'll consider all of em
    # if there are less than 4, i consider 4 as default
    return total_decimal_numbers if total_decimal_numbers > 4 else 4


def format_result(wf, converted_rate, decimal_places=4):
    """
    Format the result acording to user configuration.
    :param decimal_places Number of decimals after the decimal point, default is to 4
    :type wf: Workflow
    :type converted_rate: Decimal
    :type decimal_places: int
    """
    fmt_val = locale.format('%%.%if' % decimal_places, converted_rate, True, True)

    # User divisor
    divisor = wf.settings.get(SETTINGS_DEFAULT_NUMBER_DIVISOR, '.')

    try:
        locale_divisor = locale.localeconv().get('decimal_point')
    except:
        # Numero de casas decimais pra pegar o divisor
        locale_divisor = fmt_val[-decimal_places]

    # when there are no decimal places, i don't format the number
    return fmt_val if decimal_places == 0 else fmt_number(fmt_val, divisor, locale_divisor)


def fmt_number(fmt_val, divisor, src_divisor=None):
    """
    Formats the number with the divisor parameter as the division number
    :type fmt_val: str
    :type divisor: str
    :type src_divisor: str
    """
    # If its didn't receive the source divisor number, try to figure out which one is using
    if not src_divisor:
        for char in fmt_val[::-1]:
            if char == '.' or char == ',':
                src_divisor = char
                break

    if not src_divisor:
        log.debug("Doesn't formating value %s because no divisor was informed nor found.", fmt_val)
        return fmt_val

    fmt_nums = fmt_val.split(src_divisor)

    # Inverse the user divisor
    replace_user_divisor = ',' if divisor == '.' else '.'

    # Inverse the locale divisor
    replace_locale_divisor = ',' if src_divisor == '.' else '.'

    return '{}{}{}'.format(fmt_nums[0].replace(replace_locale_divisor, replace_user_divisor), divisor, fmt_nums[1])


def extract_filter_params(query, currencies):
    """
    Extracts the params from query to use to filter for currencies

    :param currencies: Dict with currencies
    :param query: A list with parameters from query
    :return: A lista with the words for use in the filter
    """
    query_parsed = []

    if not query:
        return query_parsed

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


def show_autocomplete(queries, query, currencies, wf):
    """
    This fuction return a list of possible currencies
    based on the query

    :param queries: list with all the queries entered even the one being processed now
    :param query: a list with the query being processed now
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

            autocomplete = ''

            # if there is more than 1 query, i keep all them for the autocomplete
            if len(queries) > 1:
                for q in queries[:-1]:
                    autocomplete += ' '.join(q) + ';'

            autocomplete += ' '.join(query + [currency['Code'].decode('utf-8')])

            wf.add_item(title=currency['Name'].decode('utf-8'),
                        subtitle='{}'.format(currency['Code'].decode('utf-8')),
                        autocomplete=autocomplete,
                        icon=flag_file_icon)


def handle_set_default_currency(args, currencies, wf):
    currency = args.default_currency.upper()
    if currency not in currencies:
        wf.add_item('You entered a invalid currency...', icon=ICON_ERROR)
        return 1
    wf.settings[SETTINGS_DEFAULT_CURRENCY] = currency
    print currency
    return 0


def handle_get_default_currency(wf):
    if SETTINGS_DEFAULT_CURRENCY in wf.settings:
        wf.add_item('Your default currency is: {}'.format(wf.settings[SETTINGS_DEFAULT_CURRENCY]), icon=ICON_INFO)
    else:
        wf.add_item('No default currency.', 'Please, use the ratesetcurrency to set the default currency first',
                    icon=ICON_WARNING, valid=True)
    return 0


def handle_clear(wf):
    wf.reset()
    wf.add_item('Caches cleared!', icon=ICON_INFO)
    return 0


def handle_update(wf):
    if wf.start_update():
        msg = 'Downloading and installing update ...'
    else:
        msg = 'No update available'
    wf.add_item(msg, icon=ICON_INFO)
    return 20


def handle_check_update(wf):
    log.debug('Checking if there is a new update available...')
    wf.check_update(True)
    update_info = wf.cached_data('__workflow_update_status', None)
    update_version = ''
    if update_info and 'version' in update_info:
        update_version = update_info['version']
    wf.add_item('There is a new update available! {} {}'.format('Version: ', update_version),
                'We recommend updating the workflow by running rateupdate!')


def handle_set_default_divisor(args, wf):
    if args.default_divisor == '.' or args.default_divisor == ',':
        wf.settings[SETTINGS_DEFAULT_NUMBER_DIVISOR] = args.default_divisor
        wf.add_item("Default divisor updated to: '{}'".format(args.default_divisor))
    else:
        wf.add_item("Wrong divisor, please specify '.' or ','.", icon=ICON_ERROR)
    return 0


def handle_get_default_divisor(wf):
    if SETTINGS_DEFAULT_NUMBER_DIVISOR in wf.settings:
        wf.add_item("The number divisor is: '{}'".format(wf.settings[SETTINGS_DEFAULT_NUMBER_DIVISOR]), icon=ICON_INFO)
    else:
        wf.add_item("No number divisor set, using the default '.'",
                    'Please, use the ratesetdivisor to set the default number divisor',
                    icon=ICON_WARNING, valid=True)
    return 0


def evaluate_math(query):
    """
    Evaluate maths expressions if there are any in the query

    :type query: list[str]
    """
    # Final result
    evaluated_query = []

    math_expr = re.compile(r'(\d+([.]\d+)*|[+\-/*])+\d([.]\d+)*$')

    for q in query:
        if math_expr.match(q):
            evaluated_query += [str(eval(q))]
        else:
            evaluated_query += [q]

    return evaluated_query


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
    parser.add_argument('--set-default-divisor', dest='default_divisor', default=None)
    parser.add_argument('--get-default-divisor', dest='get_default_divisor', default=None, action='store_true')
    parser.add_argument('--clear', default=None, action='store_true')
    parser.add_argument('--update', default=None, action='store_true')
    parser.add_argument('query', nargs='*')

    args = parser.parse_args(wf.args)

    log.debug('Args parsed: %s', args)
    log.debug('Args received: %s', wf.args)

    # Sets the local context precision for decimals to be 10, doens't need more than that
    decimal.getcontext().prec = 6

    ############################################################################################
    # Update the default currency
    ############################################################################################
    if args.default_currency:
        return handle_set_default_currency(args, currencies, wf)

    ############################################################################################
    # Get the default currency
    ############################################################################################
    if args.get_default_currency:
        return handle_get_default_currency(wf)

    ############################################################################################
    # Update the default divisor
    ############################################################################################
    if args.default_divisor:
        return handle_set_default_divisor(args, wf)

    ############################################################################################
    # Get the default divisor
    ############################################################################################
    if args.get_default_divisor:
        return handle_get_default_divisor(wf)

    ############################################################################################
    # Clean the caches
    ############################################################################################
    if args.clear:
        return handle_clear(wf)

    ############################################################################################
    # Update the workflow
    ############################################################################################
    if args.update:
        return handle_update(wf)

    # list of list of queries [ [query 1 parameters], [query 2 parameters] [query n parameters ...]]
    queries = []

    if len(args.query) > 0:
        # Split the queries for multiqueries
        tmp_queries = args.query[0].split(';')

        for q in tmp_queries:
            # split each of the queries into the parameters for each querie
            query = list(q.split())

            # Especial handling for queries like 1 GBP USD CAD CLP EUR, query the first
            # currency will be check against each one of the others, so in the example will need to transform
            # this query into 4 queries
            # 1 -> 1 GBP USD
            # 2 -> 1 GBP CAD
            # 3 -> 1 GBP CLP
            # 4 -> 1 GBP EUR
            if len(query) > 3:
                # The first parameter is a number, and the second are not
                queue = deque(evaluate_math(query))

                base_query = [queue.popleft(), queue.popleft()]

                while len(queue) > 0:
                    query_tmp = list(base_query)
                    query_tmp.append(queue.popleft())
                    queries.append(query_tmp)
            else:
                # just add
                queries.append(evaluate_math(query))

    returns = []

    for query in queries:
        if query and len(query) == 1:
            inverted_currency = query[0].startswith('!') or query[0].endswith('!')

            ############################################################################################
            # Show the currency against the default currency or USD if none specified
            ############################################################################################
            currency = query[0] if not inverted_currency else query[0].replace('!', '')

            default_currency = 'USD'

            # If Has a default currency settings, use it, otherwise keeps the default USD
            if SETTINGS_DEFAULT_CURRENCY in wf.settings:
                default_currency = wf.settings[SETTINGS_DEFAULT_CURRENCY]

            if inverted_currency:
                currency_src = currency
                currency_dst = default_currency
            else:
                currency_src = default_currency
                currency_dst = currency

            ret = process_conversion(queries, query, currency_src, currency_dst, None, currencies, wf)
            returns.append(ret)
        elif query and len(query) == 3:
            ####################################################################################################
            # Convert the currencies
            ####################################################################################################
            if not is_float(query[0]):
                show_autocomplete(queries, query, currencies, wf)
                return 100

            val = float(query[0])
            src = query[1]
            dst = query[2]

            ret = process_conversion(queries, query, src, dst, val, currencies, wf)
            returns.append(ret)
        elif query and len(query) == 2:
            ####################################################################################################
            # Convert a value to the default currency or from the default currency to the other especified
            ####################################################################################################
            if not (is_float(query[0]) or is_float(query[1])):
                show_autocomplete(queries, query, currencies, wf)
                return 100

            currency_dst = wf.settings.get(SETTINGS_DEFAULT_CURRENCY, 'USD')

            # First parameter is the value, means should convert from local default currency to the one specified in the query
            if is_float(query[0]) and not is_float(query[1]):
                currency_src = currency_dst
                currency_dst = query[1]
                val = float(query[0])
            # Second parameter is the value, means should convert from the query currency to the default one
            else:
                currency_src = query[0]
                val = float(query[1])

            ret = process_conversion(queries, query, currency_src, currency_dst, val, currencies, wf)
            returns.append(ret)
        else:
            show_autocomplete(queries, query, currencies, wf)
            returns.append(100)

    for r in returns:
        if r != 0:
            return r


if __name__ == '__main__':
    update_settings = {'github_slug': 'kennedyoliveira/alfred-rates', 'frequency': 1}

    wf = Workflow(update_settings=update_settings)
    log = wf.logger
    retorno = wf.run(main)
    wf.send_feedback()
    sys.exit(retorno)
