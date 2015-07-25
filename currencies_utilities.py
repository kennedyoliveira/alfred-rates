# !/usr/bin/python
# encoding: iso-8859-1

"""
Utility class for fetching remote currencies info.
"""
__author__ = 'kennedy'

import hashlib
import requests
import os.path


def fetch_currencies():
    """
    Checks if needs to fetch new currencies from remote, if so, then download

    :rtype : bool True if fetched new currencies, False otherwise
    """
    try:
        resp = requests.get('https://dl.dropboxusercontent.com/u/17155314/rates/currencies.csv.md5')

        if resp.status_code == 200:
            remote_md5 = resp.content

            md5 = hashlib.md5()

            if os.path.exists('currencies.csv'):
                md5.update(open('currencies.csv').read())
            else:
                md5.update('zupa!')

            actual_md5 = md5.hexdigest()

            if remote_md5 != actual_md5:
                downresp = requests.get('https://dl.dropboxusercontent.com/u/17155314/rates/currencies.csv')

                if downresp.status_code == 200:
                    with open('currencies.csv', 'w') as f:
                        f.write(downresp.content)

                return True
    except:
        return False
