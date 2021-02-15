# -*- coding: utf-8 -*-
'''Orange API client'''
import json
import sys

if sys.version_info[0] < 3:
    from urlparse import urlparse # pylint: disable=import-error
    from urllib2 import HTTPError, Request, urlopen # pylint: disable=import-error
else:
    from urllib.error import HTTPError
    from urllib.parse import urlparse
    from urllib.request import Request, urlopen

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'

def get_channels():
    '''Retrieve all the available channels and the the associated information (name, logo, zapping number, etc.)'''
    endpoint = 'https://rp-live.orange.fr/live-webapp/v3/applications/PC/channels'

    req = Request(endpoint, headers={
        'User-Agent': USER_AGENT,
        'Host': urlparse(endpoint).netloc
    })

    res = urlopen(req)
    return json.loads(res.read())

def get_channel_stream(channel_id):
    '''Get stream information (MPD address, Widewine key) for the specified channel'''
    endpoint = \
        'https://chaines-tv.orange.fr/live-webapp/v3/applications/PC/users/me/channels/{}/stream?terminalModel=WEB_PC'

    req = Request(endpoint.format(channel_id), headers={
        'User-Agent': USER_AGENT,
        'Host': urlparse(endpoint).netloc
    })

    try:
        res = urlopen(req)
    except HTTPError as error:
        if error.code == 403:
            return False

    return json.loads(res.read())

def get_programs(period='today'):
    '''Returns all the programs for the specified period'''
    # endpoint = 'https://rp-live.orange.fr/live-webapp/v3/applications/PC/programs?period={},{}&mco=OFR'
    endpoint = 'https://rp-live.orange.fr/live-webapp/v3/applications/PC/programs?period={}&mco=OFR'

    req = Request(endpoint.format(period), headers={
        'User-Agent': USER_AGENT,
        'Host': urlparse(endpoint).netloc
    })

    res = urlopen(req)
    return json.loads(res.read())
