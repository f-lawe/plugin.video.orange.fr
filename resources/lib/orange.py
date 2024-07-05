# -*- coding: utf-8 -*-
"""Orange API client"""
import json
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .utils import random_ua

def get_channels():
    """Retrieve all the available channels and the the associated information (name, logo, zapping number, etc.)"""
    endpoint = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/channels'

    req = Request(endpoint, headers={
        'User-Agent': random_ua(),
        'Host': urlparse(endpoint).netloc
    })

    res = urlopen(req)
    return json.loads(res.read())

def get_channel_stream(channel_id):
    """Get stream information (MPD address, Widewine key) for the specified channel"""
    endpoint = \
        'https://mediation-tv.orange.fr/all/live/v3/applications/PC/users/me/channels/{}/stream?terminalModel=WEB_PC'

    req = Request(endpoint.format(channel_id), headers={
        'User-Agent': random_ua(),
        'Host': urlparse(endpoint).netloc
    })

    try:
        res = urlopen(req)
    except HTTPError as error:
        if error.code == 403:
            return False

    return json.loads(res.read())

def get_programs(period_start='today', period_end=None):
    """Returns all the programs for the specified period"""
    endpoint = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/programs?period={}&mco=OFR'
    period = period_start if not period_end else '{},{}'.format(int(period_start), int(period_end))

    req = Request(endpoint.format(period), headers={
        'User-Agent': random_ua(),
        'Host': urlparse(endpoint).netloc
    })

    res = urlopen(req)
    return json.loads(res.read())
