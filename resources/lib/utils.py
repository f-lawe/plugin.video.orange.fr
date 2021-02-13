# -*- coding: utf-8 -*-
"""utils"""
import xbmc
import xbmcaddon
import xbmcgui

ADDON_NAME = xbmcaddon.Addon().getAddonInfo('name')

def log(msg, level):
    """log"""
    xbmc.log('{}: {}'.format(ADDON_NAME, msg), level)

def dialog(msg):
    """dialog"""
    xbmcgui.Dialog().ok(ADDON_NAME, msg)
