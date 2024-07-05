# -*- coding: utf-8 -*-
"""Make the use of some Kodi functions easier"""
import xbmc
import xbmcaddon
import xbmcgui

ADDON_NAME = xbmcaddon.Addon().getAddonInfo('name')

def log(msg, level):
    """Wrapper around the Kodi log function"""
    xbmc.log('{}: {}'.format(ADDON_NAME, msg), level)

def dialog(msg):
    """Wrapper around the Kodi dialop function, display a popup window with a button"""
    xbmcgui.Dialog().ok(ADDON_NAME, msg)
