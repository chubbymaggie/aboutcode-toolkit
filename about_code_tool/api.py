#!/usr/bin/env python
# -*- coding: utf8 -*-

# ============================================================================
#  Copyright (c) 2013-2016 nexB Inc. http://www.nexb.com/ - All rights reserved.
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#      http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ============================================================================

from __future__ import print_function

import urllib
import urllib2
import httplib
import json
from collections import namedtuple


from about_code_tool import Error
from about_code_tool import ERROR

"""
API call helpers
"""

def build_api_url(url, api_username, api_key, license_key):
    """
    Return a URl suitable for making an API call.
    """
    url = url.rstrip('/')

    payload = {'username': api_username,
               'api_key': api_key,
               'format': 'json'}
    encoded_payload = urllib.urlencode(payload)

    api_url = '%(url)s/%(license_key)s/?%(encoded_payload)s' % locals()

    # handle special characters in URL such as space etc.
    api_url = urllib.quote(api_url, safe="%/:=&?~#+!$,;'@()*[]")
    return api_url


def get_license_data(self, url, api_username, api_key, license_key):
    """
    Return a list of errors and a dictionary of license data, given a DejaCode
    API url and a DejaCode license_key, send an API request to get license
    data for the license_key, authenticating through an api_key and username.
    """
    full_url = build_api_url(url, api_username, api_key, license_key)

    errors = []
    license_data = {}

    msg = 'Failed to collect license data for %(license_key)s.'

    try:
        request = urllib2.Request(full_url)
        response = urllib2.urlopen(request)
        response_content = response.read()
        license_data = json.loads(response_content)

    except urllib2.HTTPError as e:
        if e.code == httplib.UNAUTHORIZED:
            msg = msg + ('Authorization denied: '
                         'Invalid api_username: %(api_username)s '
                         'or api_key: %(api_key)s.')
        # FIXME: what about 404 and other cases?
        errors.append(Error(ERROR, msg % locals()))

    except urllib2.URLError as e:
        msg = msg + 'Network problem. Check your internet connection.'
        errors.append(Error(ERROR, msg % locals()))

    except Exception as e:
        # only keep the first 100 char of the exception
        emsg = repr(e)[:100]
        msg = msg + ' Error: %(emsg)s'
        errors.append(Error(ERROR, msg % locals()))

    return errors, license_data


LicenseInfo = namedtuple('LicenseInfo', ['key', 'name', 'text'])


def get_license_info(self, url, api_username, api_key, license_key,
                     caller=get_license_data):
    """
    Return a list of errors and a tuple of key, name, text for a given
    license_key using a DejaCode API request at url. caller is the function
    used to call the API and is used mostly for mocking in tests.
    """
    errors, data = get_license_data(url, api_username, api_key, license_key)
    key = data.get('key')
    name = data.get('name')
    text = data.get('full_text')
    return errors, LicenseInfo(key, name, text)
