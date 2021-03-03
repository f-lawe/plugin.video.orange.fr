# -*- coding: utf-8 -*-
"""Update channels and programs data on startup and every hour"""
from datetime import date, datetime
import os

import xbmc
import xbmcaddon

from lib import M3UGenerator, XMLTVGenerator
from lib.orange import get_channels, get_programs
from lib.utils import log

ADDON = xbmcaddon.Addon()

def generate_m3u():
    """Load channels into m3u list"""
    filepath = os.path.join(ADDON.getAddonInfo('path'), 'resources', 'data', 'orange-fr.m3u')
    log(filepath, xbmc.LOGDEBUG)

    generator = M3UGenerator()
    generator.append_channels(get_channels())
    generator.write(filepath=filepath)

def generate_xmltv():
    """Load channels and programs data for the 6 next days into XMLTV file"""
    filepath = os.path.join(ADDON.getAddonInfo('path'), 'resources', 'data', 'orange-fr.xml')
    log(filepath, xbmc.LOGDEBUG)

    generator = XMLTVGenerator()
    generator.append_channels(get_channels())

    today = datetime.timestamp(datetime.combine(date.today(), datetime.min.time()))
    day_duration = 24 * 60 * 60

    for day in range(0, 6):
        period_start = (today + day_duration * day) * 1000
        period_end = period_start + (day_duration * 1000)
        generator.append_programs(get_programs(period_start=period_start, period_end=period_end))

    generator.write(filepath=filepath)

def run():
    """Run data generators"""
    log('Updating data...', xbmc.LOGINFO)
    generate_m3u()
    generate_xmltv()
    log('Channels and programs data updated', xbmc.LOGINFO)

def main():
    """Service initialisation"""
    log('Initialise service', xbmc.LOGINFO)
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
