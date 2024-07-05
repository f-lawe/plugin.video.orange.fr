# -*- coding: utf-8 -*-
"""Channel stream management"""
from urllib.parse import urlparse

import inputstreamhelper # pylint: disable=import-error
import xbmc
import xbmcgui

from .orange import get_channel_stream, USER_AGENT
from .utils import dialog, log

def extract_stream_info(license_type, channel_stream):
    """Extract Widevine licence information from stream details"""
    path = channel_stream.get('url')

    license_server_url = None
    for system in channel_stream.get('protectionData'):
        if system.get('keySystem') == license_type:
            license_server_url = system.get('laUrl')

    return path, license_server_url

def format_inputstream_properties(stream, drm):
    """Format parameters to be sent to InputStream list item"""
    license_types = {
        'widevine': 'com.widevine.alpha'
    }

    license_type = license_types.get(drm)
    path, license_server_url = extract_stream_info(license_type, stream)
    headers = 'Content-Type=&User-Agent={}&Host={}'.format(USER_AGENT, urlparse(license_server_url).netloc)
    post_data = 'R{SSM}'
    response = ''
    license_key = '{}|{}|{}|{}'.format(license_server_url, headers, post_data, response)

    return path, 'mpd', license_type, license_key

def build_channel_listitem(channel_id):
    """Retreive stream information and load InputStream"""
    stream = get_channel_stream(channel_id)
    drm = 'widevine'

    if not stream:
        dialog('This channel is not part of your current registration.')
        return

    path, manifest_type, license_type, license_key = format_inputstream_properties(stream, drm)
    log(license_key, xbmc.LOGDEBUG)

    is_helper = inputstreamhelper.Helper(manifest_type, drm=drm)
    if not is_helper.check_inputstream():
        return False

    listitem = xbmcgui.ListItem(path=path)
    listitem.setMimeType('application/xml+dash')
    listitem.setProperty('inputstream', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', manifest_type)
    listitem.setProperty('inputstream.adaptive.license_type', license_type)
    listitem.setProperty('inputstream.adaptive.license_key', license_key)

    return listitem
