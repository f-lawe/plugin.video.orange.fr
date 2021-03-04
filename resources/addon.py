# -*- coding: utf-8 -*-
"""Addon entry point"""
import routing # pylint: disable=import-error
import xbmcplugin

from lib.channel import build_channel_listitem, format_inputstream_properties
from lib.iptvmanager import IPTVManager
from lib.orange import get_channel_stream, get_channels, get_programs
from lib.utils import dialog, log

plugin = routing.Plugin()

@plugin.route('/channel/<channel_id>')
def channel(channel_id):
    """Load stream for the required channel id"""
    log('Loading channel {}'.format(channel_id), 'info')

    stream = get_channel_stream(channel_id)
    if not stream:
        dialog('This channel is not part of your current registration.')
        return

    drm = 'widevine'
    path, manifest_type, license_key = format_inputstream_properties(stream, drm)
    listitem = build_channel_listitem(path, manifest_type, drm, license_key)
    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem=listitem)

@plugin.route('/iptv/channels')
def iptv_channels():
    """Return JSON-STREAMS formatted data for all live channels"""
    log('Loading channel data for IPTV Manager', 'info')
    port = int(plugin.args.get('port')[0])
    IPTVManager(port, channels_loader=get_channels).send_channels()

@plugin.route('/iptv/epg')
def iptv_epg():
    """Return JSON-EPG formatted data for all live channel EPG data"""
    log('Loading progam data for IPTV Manager', 'info')
    port = int(plugin.args.get('port')[0])
    IPTVManager(port, programs_loader=lambda: get_programs(days=6)).send_epg()

if __name__ == '__main__':
    plugin.run()
