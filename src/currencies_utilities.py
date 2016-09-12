# !/usr/bin/python
# encoding: iso-8859-1

"""
Utility class for fetching remote currencies info.
"""
__author__ = 'Kennedy'

import hashlib
import os.path

from lib.workflow import Workflow

from lib.workflow import web

log = Workflow().logger


def fetch_currencies(target_file='currencies.csv'):
    """
    Checks if needs to fetch new currencies from remote, if so, then download

    :type target_file: str
    :param target_file Target file that the currencies data will be writed to
    :rtype : bool True if fetched new currencies, False otherwise
    """
    try:
        log.debug('Fetching currencies md5')
        resp = web.get('https://dl.dropboxusercontent.com/u/17155314/rates/currencies.csv.md5')

        if resp.status_code == 200:
            log.debug("Currencies md5 fetched succefully")
            remote_md5 = resp.content

            md5 = hashlib.md5()

            log.debug("Calculating local currencies md5...")
            if os.path.exists(target_file):
                md5.update(open(target_file).read())
            else:
                log.debug("No local currencies to calc md5...")
                md5.update('zupa!')

            actual_md5 = md5.hexdigest()

            log.debug("Current md5 [%s], remote md5 [%s]", actual_md5, remote_md5)
            if remote_md5 != actual_md5:
                log.debug("Local currencies needs to be updated, downloading updated currencies info...")
                downresp = web.get('https://dl.dropboxusercontent.com/u/17155314/rates/currencies.csv')

                if downresp.status_code == 200:
                    log.debug("Currencies info downloaded succefully.")
                    log.debug("Writing currencies info to local cache...")
                    with open(target_file, 'w') as f:
                        f.write(downresp.content)

                    return True
                else:
                    log.error("Failed to fetch currencies info: [response code: %s, response: %s]",
                              downresp.status_code, downresp.content)
            else:
                log.debug("Local hash and remote hash are equals, no need to update currencies.")
                return False
        else:
            log.error("Fail to fetch currencies md5. %s %s", resp.status_code, resp.content)
            return False
    except Exception as ex:
        log.error("Fail to fetch currencies. %s", ex.message)
        return False
