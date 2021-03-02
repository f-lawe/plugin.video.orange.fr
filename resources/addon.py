# -*- coding: utf-8 -*-
"""Addon entry point"""
from datetime import date, datetime

import routing # pylint: disable=import-error
import xbmc
import xbmcplugin

from lib.channel import build_channel_listitem, format_inputstream_properties
from lib.iptvmanager import IPTVManager
from lib.orange import get_channel_stream, get_channels, get_programs
from lib.utils import dialog, log

plugin = routing.Plugin()

@plugin.route('/channel/<channel_id>')
def channel(channel_id):
    """Load stream for the required channel id"""
    log('Loading channel {}'.format(channel_id), xbmc.LOGINFO)

    drm = 'widevine'
    stream = get_channel_stream(channel_id)

    if not stream:
        dialog('This channel is not part of your current registration.')
        return

    path, manifest_type, license_key = format_inputstream_properties(stream, drm)
    log(license_key, xbmc.LOGDEBUG)

    listitem = build_channel_listitem(path, manifest_type, drm, license_key)
    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem=listitem)

@plugin.route('/iptv/channels')
def iptv_channels():
    """Return JSON-STREAMS formatted data for all live channels"""
    log('Loading channel data for IPTV Manager', xbmc.LOGINFO)
    port = int(plugin.args.get('port')[0])
    IPTVManager(port, channels=get_channels()).send_channels()

@plugin.route('/iptv/epg')
def iptv_epg():
    """Return JSON-EPG formatted data for all live channel EPG data"""
    log('Loading progam data for IPTV Manager', xbmc.LOGINFO)

    today = datetime.timestamp(datetime.combine(date.today(), datetime.min.time()))
    day_duration = 24 * 60 * 60
    programs = []

    for day in range(0, 6):
        period_start = (today + day_duration * day) * 1000
        period_end = period_start + (day_duration * 1000)
        programs.extend(get_programs(period_start=period_start, period_end=period_end))

    port = int(plugin.args.get('port')[0])
    IPTVManager(port, programs=programs).send_epg()

if __name__ == '__main__':
    plugin.run()
