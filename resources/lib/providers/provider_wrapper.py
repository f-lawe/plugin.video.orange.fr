# -*- coding: utf-8 -*-
"""PROVIDER INTERFACE"""
import os
import json
from urllib.error import URLError
import xbmcvfs

from lib.utils import get_addon_profile, log, LogLevel

from .provider_interface import ProviderInterface

class ProviderWrapper(ProviderInterface):
    """The provider wrapper brings capabilities (like caching) on top of every registered providers"""
    cache_folder = os.path.join(xbmcvfs.translatePath(get_addon_profile()), 'cache')

    def __init__(self, provider: ProviderInterface) -> None:
        self.provider = provider

        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

    def get_stream_info(self, channel_id: int) -> dict:
        # todo: catch error and display clean Kodi error to user
        return self.provider.get_stream_info(channel_id)

    def get_streams(self) -> list:
        streams = []

        try:
            streams = self.provider.get_streams()
            with open(os.path.join(self.cache_folder, 'streams.json'), 'wb') as file:
                file.write(json.dumps(streams, indent=2).encode('utf-8'))
        except URLError:
            log('Can\'t reach server: load streams from cache', LogLevel.WARNING)
            with open(os.path.join(self.cache_folder, 'streams.json'), 'r', encoding='utf-8') as file:
                streams = json.loads(''.join(file.readlines()))

        return streams

    def get_epg(self) -> dict:
        # todo: catch error and display clean Kodi error to user
        return self.provider.get_epg()
