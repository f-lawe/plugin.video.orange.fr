# -*- coding: utf-8 -*-
'''SERVICE'''
import os
import xbmc
import xbmcaddon

from lib import orange, utils
from lib import M3UGenerator, XMLTVGenerator

def generate_m3u():
    '''Load channels into m3u list'''
    filepath = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'data', 'orange-fr.m3u')
    utils.log(filepath, xbmc.LOGDEBUG)

    generator = M3UGenerator(filepath=filepath)
    generator.append_channels(orange.get_channels())
    generator.write()

if __name__ == '__main__':
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            break

        utils.log('Updating data...', xbmc.LOGNOTICE) # pylint: disable=no-member
        generate_m3u()
