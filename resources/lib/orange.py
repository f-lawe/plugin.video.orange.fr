# -*- coding: utf-8 -*-
"""Orange API client"""
from datetime import date, datetime
import json
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import xbmc

from .utils import log, random_ua

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

def get_programs(**kwargs):
    """Returns all the programs for the specified period"""
    endpoint = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/programs?period={}&mco=OFR'

    if 'days' in kwargs and kwargs['days'] > 0:
        today = datetime.timestamp(datetime.combine(date.today(), datetime.min.time()))
        day_duration = 24 * 60 * 60
        programs = []

        for day in range(0, kwargs['days']):
            period_start = (today + day_duration * day) * 1000
            period_end = period_start + (day_duration * 1000)
            programs.extend(get_programs(period_start=period_start, period_end=period_end))

        return programs

    if 'period_start' in kwargs and 'period_end' in kwargs:
        period = '{},{}'.format(int(kwargs['period_start']), int(kwargs['period_end']))
    else:
        period = 'today'

    url = endpoint.format(period)
    log(url, xbmc.LOGINFO)

    req = Request(url, headers={
        'User-Agent': random_ua(),
        'Host': urlparse(endpoint).netloc
    })

    res = urlopen(req)
    return json.loads(res.read())
