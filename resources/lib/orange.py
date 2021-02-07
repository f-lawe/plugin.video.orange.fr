# -*- coding: utf-8 -*-
import json, sys

if sys.version_info[0] < 3:
    import urllib2 as request, urlparse as parse
else:
    from urllib import request, parse

CHANNELS_ENDPOINT       = 'https://rp-live.orange.fr/live-webapp/v3/applications/PC/channels'
STREAM_INFO_ENDPOINT    = 'https://chaines-tv.orange.fr/live-webapp/v3/applications/PC/users/me/channels/{}/stream?terminalModel=WEB_PC'

USER_AGENT              = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'

def get_channels():
    req = request.Request(CHANNELS_ENDPOINT, headers={
        'User-Agent': USER_AGENT,
        'Host': parse.urlparse(CHANNELS_ENDPOINT).netloc
    })

    res = request.urlopen(req)
    return json.loads(res.read())

def get_channel_stream(channel_id):
    req = request.Request(STREAM_INFO_ENDPOINT.format(channel_id), headers={
        'User-Agent': USER_AGENT,
        'Host': parse.urlparse(STREAM_INFO_ENDPOINT).netloc
    })

    try:
        res = request.urlopen(req)
    except request.HTTPError as error:
        if error.code == 403:
            return False

    return json.loads(res.read())