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

def run():
    """Run data generators"""
    log('Updating data...', 'info')
    provider = Provider()

    filepath = os.path.join(xbmcvfs.translatePath(ADDON.getAddonInfo('profile')), 'playlist.m3u8')
    log(filepath, 'debug')
    PlaylistGenerator(provider=provider).write(filepath=filepath)

    filepath = os.path.join(xbmcvfs.translatePath(ADDON.getAddonInfo('profile')), 'epg.xml')
    log(filepath, 'debug')
    EPGGenerator(provider=provider).write(filepath=filepath)

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
