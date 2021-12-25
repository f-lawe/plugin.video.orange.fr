# -*- coding: utf-8 -*-
"""Update channels and programs data on startup and every hour"""
import os

import xbmc
import xbmcvfs

from lib.generators import EPGGenerator, PlaylistGenerator
from lib.providers import get_provider
from lib.utils import get_addon_profile, get_addon_setting, get_global_setting, log, LogLevel

def run():
    """Run data generators"""
    log('Updating data...', LogLevel.INFO)
    provider = get_provider()

    filepath = os.path.join(xbmcvfs.translatePath(get_addon_profile()), 'playlist.m3u8')
    log(filepath, LogLevel.DEBUG)
    PlaylistGenerator(provider=provider).write(filepath=filepath)

    filepath = os.path.join(xbmcvfs.translatePath(get_addon_profile()), 'epg.xml')
    log(filepath, LogLevel.DEBUG)
    EPGGenerator(provider=provider).write(filepath=filepath)

    log('Channels and programs data updated', LogLevel.INFO)

def main():
    """Service initialisation"""
    if get_addon_setting('basic.enabled') == 'true':
        log('Initialising service', LogLevel.INFO)
        interval = 10
        monitor = xbmc.Monitor()

        while not monitor.abortRequested():
            if monitor.waitForAbort(interval):
                break

            interval = int(get_global_setting('epg.epgupdate')) * 60
            run()

if __name__ == '__main__':
    main()
