# -*- coding: utf-8 -*-
"""Addon entry point"""
import routing # pylint: disable=import-error
import inputstreamhelper # pylint: disable=import-error
import xbmcgui
import xbmcplugin

from lib.iptvmanager import IPTVManager
from lib.providers import get_provider
from lib.utils import localize, log, LogLevel, ok_dialog

plugin = routing.Plugin()

@plugin.route('/')
def index():
    """Addon index"""
    ok_dialog(localize(30902))

@plugin.route('/channel/<channel_id>')
def channel(channel_id: str):
    """Load stream for the required channel id"""
    log(f'Loading channel {channel_id}', LogLevel.INFO)

    stream = get_provider().get_stream_info(channel_id)
    if not stream:
        ok_dialog(localize(30900))
        return

    is_helper = inputstreamhelper.Helper(stream['manifest_type'], drm=stream['drm'])
    if not is_helper.check_inputstream():
        ok_dialog(localize(30901))
        return

    listitem = xbmcgui.ListItem(path=stream['path'])
    listitem.setMimeType(stream['mime_type'])
    listitem.setProperty('inputstream', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.license_type', stream['license_type'])
    listitem.setProperty('inputstream.adaptive.license_key', stream['license_key'])
    listitem.setProperty('inputstream.adaptive.manifest_type', stream['manifest_type'])
    listitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
    listitem.setProperty('inputstream.adaptive.play_timeshift_buffer', 'true')
    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem=listitem)

@plugin.route('/iptv/channels')
def iptv_channels():
    """Return JSON-STREAMS formatted data for all live channels"""
    log('Loading channels for IPTV Manager', LogLevel.INFO)
    port = int(plugin.args.get('port')[0])
    IPTVManager(port, get_provider()).send_channels()

@plugin.route('/iptv/epg')
def iptv_epg():
    """Return JSON-EPG formatted data for all live channel EPG data"""
    log('Loading EPG for IPTV Manager', LogLevel.INFO)
    port = int(plugin.args.get('port')[0])
    IPTVManager(port, get_provider()).send_epg()

if __name__ == '__main__':
    plugin.run()
