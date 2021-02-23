# -*- coding: utf-8 -*-
'''Addon entry point'''
import sys

import xbmc
import xbmcgui
import xbmcplugin
import routing # pylint: disable=import-error

from lib.orange import get_channel_stream, USER_AGENT
from lib.utils import dialog, log

if sys.version_info[0] < 3:
    from urlparse import urlparse # pylint: disable=import-error
else:
    from urllib.parse import urlparse

plugin = routing.Plugin()

def extract_widevine_info(channel_stream):
    '''Extract Widevine licence information from stream details'''
    path = channel_stream.get('url')

    la_url = None
    for system in channel_stream.get('protectionData'):
        if system.get('keySystem') == 'com.widevine.alpha':
            la_url = system.get('laUrl')

    return path, la_url

@plugin.route('/channel/<channel_id>')
def channel(channel_id):
    '''Load stream for the required channel id'''
    log('Loading channel {}'.format(channel_id), xbmc.LOGNOTICE) # pylint: disable=no-member
    stream = get_channel_stream(channel_id)

    if not stream:
        dialog('This channel is not part of your current registration.')
        return

    path, license_server_url = extract_widevine_info(stream)
    headers = 'Content-Type=&User-Agent={}&Host={}'.format(USER_AGENT, urlparse(license_server_url).netloc)
    post_data = 'R{SSM}'
    response = ''
    license_key = '{}|{}|{}|{}'.format(license_server_url, headers, post_data, response)

    log(license_key, xbmc.LOGDEBUG)

    listitem = xbmcgui.ListItem(path=path)
    listitem.setMimeType('application/xml+dash')
    listitem.setContentLookup(False)
    listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
    listitem.setProperty('inputstream.adaptive.license_key', license_key)

    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem=listitem)

@plugin.route('/iptv/channels')
def iptv_channels():
    '''Return JSON-STREAMS formatted data for all live channels'''

@plugin.route('/iptv/epg')
def iptv_epg():
    '''Return JSON-EPG formatted data for all live channel EPG data'''

if __name__ == '__main__':
    plugin.run()
