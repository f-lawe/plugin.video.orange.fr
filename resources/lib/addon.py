# -*- coding: utf-8 -*-
import json, urllib2 as request, urlparse, sys
import xbmc, xbmcgui, xbmcplugin

from __init__ import STREAM_INFO_ENDPOINT, HOST, USER_AGENT
from utils import dialog, log

def get_channel_info(channel_id):
    req = request.Request(STREAM_INFO_ENDPOINT.format(channel_id), headers={
        'User-Agent': USER_AGENT,
        'Host': HOST
    })

    try:
        res = request.urlopen(req)
    except request.HTTPError as error:
        if error.code == 403:
            dialog('This channel is not part of your current registration.')
            return False

    channel_info = json.loads(res.read())

    stream_info = {
        'path': channel_info.get('url'),
    }

    for system in channel_info.get('protectionData'):
        if system.get('keySystem') == 'com.widevine.alpha':
            stream_info['keySystem'] = system.get('keySystem')
            stream_info['drmToken'] = system.get('drmToken')
            stream_info['laUrl'] = system.get('laUrl')

    return stream_info

def get_channel_stream_item(channel_id):
    channel_info = get_channel_info(channel_id)

    if channel_info == False:
        return

    license_server_url = channel_info['laUrl']
    headers = 'Content-Type=&User-Agent={}&Host={}'.format(USER_AGENT, HOST)
    post_data = 'R{SSM}'
    response = ''

    license_key = '{}|{}|{}|{}'.format(license_server_url, headers, post_data, response)
    log(license_key, xbmc.LOGNOTICE)

    listitem = xbmcgui.ListItem(path=channel_info['path'])
    listitem.setMimeType('application/xml+dash')
    listitem.setContentLookup(False)
    listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
    listitem.setProperty('inputstream.adaptive.license_key', license_key)

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

def main():
    if(len(sys.argv) > 3):
        args = urlparse.parse_qs(sys.argv[2][1:])
        log('Loading channel {}'.format(args['channel_id'][0]), xbmc.LOGNOTICE)
        get_channel_stream_item(args['channel_id'][0])

if __name__ == '__main__':
    main()