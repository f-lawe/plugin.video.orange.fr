"""Orange Caraïbe."""

from lib.providers.provider_interface import ProviderInterface
from lib.utils.orange import get_epg, get_stream_info, get_streams

from .orange import EXTERNAL_ID_MAP


class OrangeCaraibeProvider(ProviderInterface):
    """Orange Caraïbe provider."""

    groups = {}

    def get_stream_info(self, channel_id: str) -> dict:
        """Get stream information (MPD address, Widewine key) for the specified id. Required keys: path, mime_type, manifest_type, drm, license_type, license_key."""  # noqa: E501
        return get_stream_info(channel_id, "OCA")

    def get_streams(self) -> list:
        """Retrieve all the available channels and the the associated information (name, logo, preset, etc.) following JSON-STREAMS format."""  # noqa: E501
        return get_streams(self.groups, EXTERNAL_ID_MAP, "OCA")

    def get_epg(self) -> dict:
        """Return EPG data for the specified period following JSON-EPG format."""
        return get_epg(2, "OCA")
