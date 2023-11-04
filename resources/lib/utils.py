# -*- coding: utf-8 -*-
"""Make the use of some Kodi functions easier"""
from enum import Enum
from json import dumps, loads
from random import randint
from string import Formatter

import xbmc
import xbmcaddon
import xbmcgui

_ADDON = xbmcaddon.Addon()

_USER_AGENTS = [
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

class DRM(Enum):
    """DRM"""
    WIDEVINE = 'com.widevine.alpha'
    PLAYREADY = 'com.microsoft.playready'

class LogLevel(Enum):
    """Available Kodi log levels"""
    DEBUG = xbmc.LOGDEBUG
    ERROR = xbmc.LOGERROR
    FATAL = xbmc.LOGFATAL
    INFO = xbmc.LOGINFO
    NONE = xbmc.LOGNONE
    WARNING = xbmc.LOGWARNING

def get_addon_name():
    """Return the addon info name property"""
    return _ADDON.getAddonInfo('name')

def get_addon_path():
    """Return the addon info path property"""
    return _ADDON.getAddonInfo('path')

def get_addon_profile():
    """Return the addon info profile property"""
    return _ADDON.getAddonInfo('profile')

def get_addon_setting(name: str) -> str:
    """Return the addon setting from name"""
    return _ADDON.getSetting(name)

def get_drm() -> DRM:
    """Return the DRM system available for the current platform"""
    return DRM.WIDEVINE

def get_global_setting(key):
    """Get a global Kodi setting"""
    cmd = {
        'id': 0,
        'jsonrpc': '2.0',
        'method': 'Settings.GetSettingValue',
        'params': { 'setting': key }
    }

    return loads(xbmc.executeJSONRPC(dumps(cmd))).get('result', {}).get('value')

def localize(string_id: int, **kwargs):
    """Return the translated string from the .po language files, optionally translating variables"""
    if not isinstance(string_id, int) and not string_id.isdecimal():
        return string_id
    if kwargs:
        return Formatter().vformat(_ADDON.getLocalizedString(string_id), (), **kwargs)
    return _ADDON.getLocalizedString(string_id)

def log(msg: str, level: LogLevel):
    """Wrapper around the Kodi log function"""
    xbmc.log(f'{get_addon_name()}: {msg}', level.value)

def ok_dialog(msg: str):
    """Wrapper around the Kodi dialop function, display a popup window with a button"""
    xbmcgui.Dialog().ok(get_addon_name(), msg)

def random_ua() -> str:
    """Get a random user agent in the list"""
    return _USER_AGENTS[randint(0, len(_USER_AGENTS) - 1)]
