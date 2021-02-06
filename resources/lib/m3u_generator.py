# -*- coding: utf-8 -*-
import json
from urllib import request, parse
from html.parser import HTMLParser

from __init__ import CHANNELS_ENDPOINT, USER_AGENT

M3U_FILEPATH = '../orange-fr.m3u'

def get_channels():
    req = request.Request(CHANNELS_ENDPOINT, headers={
        'User-Agent': USER_AGENT,
        'Host': parse.urlparse(CHANNELS_ENDPOINT).netloc
    })

    res = request.urlopen(req).read().decode('utf-8')
    channels = json.loads(res)
    channels.sort(key=lambda x: x.get('zappingNumber'))

    return channels

def load_channels(channels):
    current_zapping_number = 1
    loaded_channels = []

    for channel in channels:
        next_zapping_number = channel['zappingNumber']

        for zapping_number in range(current_zapping_number, next_zapping_number)[:-1]:
            loaded_channels.append(None)

        loaded_channels.append(channel)
        current_zapping_number = next_zapping_number

    return loaded_channels

def channel_entry(channel):
    return """
##\t{name}
#EXTINF:-1 tvg-name="{zapping_number}" tvg-id="C{id}.api.telerama.fr" tvg-logo="{logo}" group-title="channels",{name}
plugin://script.orange.fr/?channel_id={id}
""".format(
        id=channel['id'],
        name=channel['name'],
        logo=channel['logos']['square'],
        zapping_number=channel['zappingNumber'])

def empty_entry(zapping_number):
    return """
##\tPLACEHOLDER
#EXTINF:-1 tvg-name="{zapping_number}" tvg-id="" tvg-logo="" group-title="-",
http://null
""".format(
        zapping_number=zapping_number)

def write_m3u(channels):
    file = open(M3U_FILEPATH, "wb")
    file.write('#EXTM3U tvg-shift=0\n'.encode('utf-8'))

    for zapping_number, channel in enumerate(channels):
        if channel == None:
            file.write(empty_entry(zapping_number).encode('utf-8'))
        else:
            file.write(channel_entry(channel).encode('utf-8'))

    file.close()

def generate_m3u():
    channels = get_channels()
    channels = load_channels(channels)
    write_m3u(channels)

def main():
    generate_m3u()

if __name__ == '__main__':
    main()