# -*- coding: utf-8 -*-
from urlparse import urlparse
from urllib import urlencode

import xbmc, xbmcgui, xbmcplugin
import routing

from orange import get_channel_stream, USER_AGENT
from utils import dialog, log

plugin = routing.Plugin()

def extract_widevine_info(channel_stream):
    """Extract Widevine licence information from stream details"""
    path = channel_stream.get('url')

    laUrl = None
    for system in channel_stream.get('protectionData'):
        if system.get('keySystem') == 'com.widevine.alpha':
            laUrl = system.get('laUrl')

    return path, laUrl

@plugin.route('/channel/<channel_id>')
def channel(channel_id):
    """Load stream for the required channel id"""
    stream = get_channel_stream(channel_id)

    if stream == False:
        dialog('This channel is not part of your current registration.')
        return

    path, license_server_url = extract_widevine_info(stream)
    headers = 'Content-Type=&User-Agent={}&Host={}'.format(USER_AGENT, urlparse(license_server_url).netloc)
    post_data = 'R{SSM}'
    response = ''
    license_key = '{}|{}|{}|{}'.format(license_server_url, headers, post_data, response)

    log(path, xbmc.LOGNOTICE)
    log(license_key, xbmc.LOGNOTICE)

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
    """Return JSON-STREAMS formatted data for all live channels"""
    pass

@plugin.route('/iptv/epg')
def iptv_epg():
    """Return JSON-EPG formatted data for all live channel EPG data"""
    pass

if __name__ == '__main__':
    plugin.run()