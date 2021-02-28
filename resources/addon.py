# -*- coding: utf-8 -*-
"""Addon entry point"""
import routing # pylint: disable=import-error
import xbmc
import xbmcplugin

from lib.channel import build_channel_listitem
from lib.iptvmanager import IPTVManager
from lib.utils import log

plugin = routing.Plugin()

@plugin.route('/channel/<channel_id>')
def channel(channel_id):
    """Load stream for the required channel id"""
    log('Loading channel {}'.format(channel_id), xbmc.LOGINFO)
    listitem = build_channel_listitem(channel_id)
    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem=listitem)

@plugin.route('/iptv/channels')
def iptv_channels():
    """Return JSON-STREAMS formatted data for all live channels"""
    log('Loading channel data for IPTV Manager', xbmc.LOGINFO)
    port = int(plugin.args.get('port')[0])
    IPTVManager(port).send_channels()

@plugin.route('/iptv/epg')
def iptv_epg():
    """Return JSON-EPG formatted data for all live channel EPG data"""
    log('Loading progam data for IPTV Manager', xbmc.LOGINFO)
    port = int(plugin.args.get('port')[0])
    IPTVManager(port).send_epg()

if __name__ == '__main__':
    plugin.run()
