# -*- coding: utf-8 -*-
"""Make the use of some Kodi functions easier"""
from random import randint

import xbmc
import xbmcaddon
import xbmcgui

ADDON_NAME = xbmcaddon.Addon().getAddonInfo('name')

USER_AGENTS = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36', # pylint: disable=line-too-long
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36', # pylint: disable=line-too-long
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36'

    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36 Edg/88.0.705.81', # pylint: disable=line-too-long
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36 Edg/88.0.705.63' # pylint: disable=line-too-long

    # Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Mozilla/5.0 (X11; Linux i686; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Mozilla/5.0 (Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0'
]

LOG_LEVELS = {
    'debug': xbmc.LOGDEBUG,
    'error': xbmc.LOGERROR,
    'fatal': xbmc.LOGFATAL,
    'info': xbmc.LOGINFO,
    'none': xbmc.LOGNONE,
    'warning': xbmc.LOGWARNING
}

def log(msg, level):
    """Wrapper around the Kodi log function"""
    xbmc.log('{}: {}'.format(ADDON_NAME, msg), LOG_LEVELS.get(level))

def dialog(msg):
    """Wrapper around the Kodi dialop function, display a popup window with a button"""
    xbmcgui.Dialog().ok(ADDON_NAME, msg)

def random_ua():
    """Get a random user agent in the list"""
    return USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
