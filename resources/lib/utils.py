# -*- coding: utf-8 -*-
import xbmc, xbmcaddon, xbmcgui

ADDON_NAME = xbmcaddon.Addon().getAddonInfo('name')

def log(msg, level):
    xbmc.log('{}: {}'.format(ADDON_NAME, msg), level)

def dialog(msg):
    xbmcgui.Dialog().ok(ADDON_NAME, msg)