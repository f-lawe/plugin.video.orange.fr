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

def channel_entry(channel):
    entry = '##\t' + channel['name'] + '\n' \
        + '##\t' + channel['name'].lower() + '\n' \
        + '#EXTINF:-1 tvg-id="C' + channel['id'] + '.api.telerama.fr" tvg-logo="' + channel['logos']['square'] + '",' + channel['name'] + '\n' \
        + 'plugin://script.orange.fr/?channel_id=' + channel['id'] + '\n' \
        + '\n'

    return entry

def write_m3u(channels):
    file = open(M3U_FILEPATH, "w")
    file.write('#EXTM3U tvg-shift=0' + '\n\n')

    for channel in channels:
        file.write(channel_entry(channel))

    file.close()

def generate_m3u():
    channels = get_channels()
    write_m3u(channels)

def main():
    generate_m3u()

if __name__ == '__main__':
    main()