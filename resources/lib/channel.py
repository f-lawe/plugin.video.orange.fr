# -*- coding: utf-8 -*-
"""Channel stream management"""
from urllib.parse import urlparse

import inputstreamhelper # pylint: disable=import-error
import xbmcgui

from .orange import USER_AGENT

LICENSE_TYPES = {
    'widevine': 'com.widevine.alpha'
}

def extract_stream_info(stream, drm):
    """Extract Widevine licence information from stream details"""
    license_type = LICENSE_TYPES.get(drm)
    path = stream.get('url')

    license_server_url = None
    for system in stream.get('protectionData'):
        if system.get('keySystem') == license_type:
            license_server_url = system.get('laUrl')

    return path, license_server_url

def format_inputstream_properties(stream, drm):
    """Format parameters to be sent to InputStream list item"""
    path, license_server_url = extract_stream_info(stream, drm)
    headers = 'Content-Type=&User-Agent={}&Host={}'.format(USER_AGENT, urlparse(license_server_url).netloc)
    post_data = 'R{SSM}'
    response = ''
    license_key = '{}|{}|{}|{}'.format(license_server_url, headers, post_data, response)

    return path, 'mpd', license_key

def build_channel_listitem(path, manifest_type, drm, license_key):
    """Retreive stream information and load InputStream"""
    is_helper = inputstreamhelper.Helper(manifest_type, drm=drm)
    if not is_helper.check_inputstream():
        return False

    listitem = xbmcgui.ListItem(path=path)
    listitem.setMimeType('application/xml+dash')
    listitem.setProperty('inputstream', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', manifest_type)
    listitem.setProperty('inputstream.adaptive.license_type', LICENSE_TYPES.get(drm))
    listitem.setProperty('inputstream.adaptive.license_key', license_key)

    return listitem
