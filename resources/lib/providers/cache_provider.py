"""Cache provider."""

import json
import os

import xbmc
import xbmcvfs

from lib.utils.kodi import get_addon_info, log

from .provider_interface import ProviderInterface


class CacheProvider(ProviderInterface):
    """Provider wrapper bringing cache capabilities on top of supplied provider."""

    cache_folder = os.path.join(xbmcvfs.translatePath(get_addon_info("profile")), "cache")

    def __init__(self, provider: ProviderInterface) -> None:
        """Initialize CacheProvider with TV provider."""
        self.provider = provider

        log(f"Cache folder: {self.cache_folder}", xbmc.LOGDEBUG)

        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

    def get_streams(self) -> list:
        """Retrieve all the available channels and the the associated information (name, logo, preset, etc.) following JSON-STREAMS format."""  # noqa: E501
        streams = []

        try:
            streams = self.provider.get_streams()
            with open(os.path.join(self.cache_folder, "streams.json"), "wb") as file:
                file.write(json.dumps(streams).encode("utf-8"))
        except Exception:
            log("Can't load streams: using cache instead", xbmc.LOGWARNING)
            with open(os.path.join(self.cache_folder, "streams.json"), encoding="utf-8") as file:
                streams = json.loads("".join(file.readlines()))

        return streams

    def get_epg(self) -> dict:
        """Return EPG data for the specified period following JSON-EPG format."""
        return self.provider.get_epg()
