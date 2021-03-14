# -*- coding: utf-8 -*-
"""PROVIDER INTERFACE"""

class ProviderInterface:
    """This interface provides methods to be implemented for each ISP"""

    def get_stream_info(self, channel_id: int) -> dict:
        """
            Get stream information (MPD address, Widewine key) for the specified id.
            Required keys: path, mime_type, manifest_type, drm, license_type, license_key
        """

    def get_streams(self) -> list:
        """
            Retrieve all the available channels and the the associated information (name, logo, zapping number,
            etc.) following JSON-STREAMS format
            (https://github.com/add-ons/service.iptv.manager/wiki/JSON-STREAMS-format)
        """

    def get_epg(self) -> dict:
        """
            Returns EPG data for the specified period following JSON-EPG format
            (https://github.com/add-ons/service.iptv.manager/wiki/JSON-EPG-format)
        """
