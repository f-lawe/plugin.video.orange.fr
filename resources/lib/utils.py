# -*- coding: utf-8 -*-
import xbmc, xbmcaddon

ADDON_NAME = xbmcaddon.Addon().getAddonInfo('name')

def log(msg, level):
    xbmc.log('{}: {}'.format(ADDON_NAME, msg), level)