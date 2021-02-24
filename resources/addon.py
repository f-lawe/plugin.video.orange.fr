# -*- coding: utf-8 -*-
'''Addon entry point'''
from urllib.parse import urlparse

import routing # pylint: disable=import-error
import xbmc
import xbmcgui
import xbmcplugin

from lib.orange import get_channel_stream, USER_AGENT
from lib.utils import dialog, log

plugin = routing.Plugin()

def extract_stream_info(license_type, channel_stream):
    '''Extract Widevine licence information from stream details'''
    path = channel_stream.get('url')

    license_server_url = None
    for system in channel_stream.get('protectionData'):
        if system.get('keySystem') == license_type:
            license_server_url = system.get('laUrl')

    return path, license_server_url

@plugin.route('/channel/<channel_id>')
def channel(channel_id):
    '''Load stream for the required channel id'''
    log('Loading channel {}'.format(channel_id), xbmc.LOGINFO)
    stream = get_channel_stream(channel_id)

    if not stream:
        dialog('This channel is not part of your current registration.')
        return

    license_type = 'com.widevine.alpha'
    path, license_server_url = extract_stream_info(license_type, stream)
    headers = 'Content-Type=&User-Agent={}&Host={}'.format(USER_AGENT, urlparse(license_server_url).netloc)
    post_data = 'R{SSM}'
    response = ''
    license_key = '{}|{}|{}|{}'.format(license_server_url, headers, post_data, response)

    log(license_key, xbmc.LOGDEBUG)

    listitem = xbmcgui.ListItem(path=path)
    listitem.setMimeType('application/xml+dash')
    listitem.setContentLookup(False)
    listitem.setProperty('inputstream', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    listitem.setProperty('inputstream.adaptive.license_type', license_type)
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
