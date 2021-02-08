# -*- coding: utf-8 -*-
import json, sys

if sys.version_info[0] < 3:
    import urllib2 as request, urlparse as parse
else:
    from urllib import request, parse

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'

def get_channels():
    endpoint = 'https://rp-live.orange.fr/live-webapp/v3/applications/PC/channels'

    req = request.Request(endpoint, headers={
        'User-Agent': USER_AGENT,
        'Host': parse.urlparse(endpoint).netloc
    })

    res = request.urlopen(req)
    return json.loads(res.read())

def get_channel_stream(channel_id):
    endpoint = 'https://chaines-tv.orange.fr/live-webapp/v3/applications/PC/users/me/channels/{}/stream?terminalModel=WEB_PC'

    req = request.Request(endpoint.format(channel_id), headers={
        'User-Agent': USER_AGENT,
        'Host': parse.urlparse(endpoint).netloc
    })

    try:
        res = request.urlopen(req)
    except request.HTTPError as error:
        if error.code == 403:
            return False

    return json.loads(res.read())

def get_programs(period):
    # endpoint = 'https://rp-live.orange.fr/live-webapp/v3/applications/PC/programs?period={},{}&mco=OFR'
    endpoint = 'https://rp-live.orange.fr/live-webapp/v3/applications/PC/programs?period={}&mco=OFR'

    req = request.Request(endpoint.format(period), headers={
        'User-Agent': USER_AGENT,
        'Host': parse.urlparse(endpoint).netloc
    })

    res = request.urlopen(req)
    return json.loads(res.read())