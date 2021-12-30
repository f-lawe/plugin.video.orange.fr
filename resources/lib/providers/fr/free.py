# -*- coding: utf-8 -*-
"""Free"""

from lib.providers import ProviderInterface
from lib.utils import get_global_setting, log, LogLevel, random_ua

class FreeProvider(ProviderInterface):
    """Free provider"""

    def get_stream_info(self, channel_id: int) -> dict:
        log('Free get stream info', LogLevel.INFO)
        return {}

    def get_streams(self) -> list:
        log('Free get streams', LogLevel.INFO)
        return []

    def get_epg(self) -> dict:
        log('Free get epg', LogLevel.INFO)
        return {}
