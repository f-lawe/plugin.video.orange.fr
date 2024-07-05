# -*- coding: utf-8 -*-
"""Update channels and programs data on startup and every hour"""
import os

import xbmc
import xbmcaddon
import xbmcvfs

from lib.generators import EPGGenerator, PlaylistGenerator
from lib.providers import Provider
from lib.utils import log

ADDON = xbmcaddon.Addon()

def generate_playlist():
    """Load channels into playlist"""
    filepath = os.path.join(xbmcvfs.translatePath(ADDON.getAddonInfo('profile')), 'playlist.m3u8')
    log(filepath, 'debug')

    generator = PlaylistGenerator()
    generator.append_streams(Provider().get_streams())
    generator.write(filepath=filepath)

def generate_epg():
    """Load channels and programs data for the 6 next days into EPG"""
    filepath = os.path.join(xbmcvfs.translatePath(ADDON.getAddonInfo('profile')), 'epg.xml')
    log(filepath, 'debug')

    provider = Provider()
    generator = EPGGenerator()
    generator.append_streams(provider.get_streams())
    generator.append_epg(provider.get_epg(days=6))
    generator.write(filepath=filepath)

def run():
    """Run data generators"""
    log('Updating data...', 'info')
    generate_playlist()
    generate_epg()
    log('Channels and programs data updated', 'info')

def main():
    """Service initialisation"""
    log('Initialise service', 'info')
    interval = 10
    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        if monitor.waitForAbort(interval):
            break

        interval = int(ADDON.getSetting('basic.interval')) * 60

        if ADDON.getSetting('basic.enabled') == 'true':
            run()

if __name__ == '__main__':
    main()
