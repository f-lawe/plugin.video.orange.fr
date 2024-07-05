# -*- coding: utf-8 -*-
"""Addon entry point"""
import routing # pylint: disable=import-error
import inputstreamhelper # pylint: disable=import-error
import xbmcplugin
import xbmcgui

from lib.iptvmanager import IPTVManager
from lib.providers import Provider
from lib.utils import dialog, log

plugin = routing.Plugin()

@plugin.route('/channel/<channel_id>')
def channel(channel_id: str):
    """Load stream for the required channel id"""
    log('Loading channel {}'.format(channel_id), 'info')

    stream = Provider().get_stream_info(channel_id)
    if not stream:
        dialog('This channel is not part of your current registration.')
        return

    is_helper = inputstreamhelper.Helper(stream['manifest_type'], drm=stream['drm'])
    if not is_helper.check_inputstream():
        dialog('Cannot load InputStream.')
        return

    listitem = xbmcgui.ListItem(path=stream['path'])
    listitem.setMimeType(stream['mime_type'])
    listitem.setProperty('inputstream', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', stream['manifest_type'])
    listitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
    listitem.setProperty('inputstream.adaptive.license_type', stream['license_type'])
    listitem.setProperty('inputstream.adaptive.license_key', stream['license_key'])
    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem=listitem)

@plugin.route('/iptv/channels')
def iptv_channels():
    """Return JSON-STREAMS formatted data for all live channels"""
    log('Loading channels for IPTV Manager', 'info')
    port = int(plugin.args.get('port')[0])
    IPTVManager(port, Provider()).send_channels()

@plugin.route('/iptv/epg')
def iptv_epg():
    """Return JSON-EPG formatted data for all live channel EPG data"""
    log('Loading EPG for IPTV Manager', 'info')
    port = int(plugin.args.get('port')[0])
    IPTVManager(port, Provider()).send_epg()

if __name__ == '__main__':
    plugin.run()
