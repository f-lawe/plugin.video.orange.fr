"""OQEE by Free. WIP."""

import json
from typing import List
from urllib.parse import urlencode

import xbmc
from requests.exceptions import RequestException

from lib.exceptions import AuthenticationRequired
from lib.providers.abstract_provider import AbstractProvider
from lib.utils.kodi import build_addon_url, get_drm, log
from lib.utils.request import get_random_ua, request, request_json

_SERVICE_PLAN_ENDPOINT = "https://api.oqee.net/api/v5/service_plan"
_LOGIN_ENDPOINT = "https://api.oqee.net/api/v5/user/login"

_STREAM_LOGO_URL = "https://img1.dc2.oqee.net/channel_pictures/{stream_id}/w200"


class FreeOqeeProvider(AbstractProvider):
    """OQEE by Free provider."""

    def get_live_stream_info(self, stream_id: str) -> dict:
        """Get live stream information (MPD address, Widewine key) for the specified id. Returned keys: path, mime_type, manifest_type, drm, license_type, license_key."""  # noqa: E501
        try:
            res = request(
                "POST", _LOGIN_ENDPOINT, headers={"Content-Type": "application/json"}, data=json.dumps({"type": "ip"})
            )
        except RequestException as e:
            log(e, xbmc.LOGWARNING)
            raise AuthenticationRequired() from e

        login = res.json()

        if login.get("result", False) is False:
            log("Failed to login to OQEE", xbmc.LOGWARNING)
            raise AuthenticationRequired()

        # token = login["result"]["token"]

        # log(token)

        stream_info = {
            "path": "https://api-proxad.dc2.oqee.net/playlist/v1/live/612/1/live.mpd",
            "protocol": "mpd",
            "mime_type": "application/xml+dash",
            "drm_config": {
                "license_type": get_drm(),
                "license_key": "|".join(
                    {
                        "license_server_url": "https://license.oqee.net/api/v1/live/license/widevine",
                        "headers": urlencode(
                            {
                                "Host": "license.oqee.net",
                                "User-Agent": get_random_ua(),
                                "Accept": "*/*",
                                "Accept-Language": "fr-FR,fr;q=0.8,en-GB;q=0.5,en;q=0.3",
                                "Accept-Encoding": "gzip, deflate, br, zstd",
                                "Referer": "https://oqee.tv/",
                                "content-type": "application/json",
                                "x-oqee-account-provider": "free",
                                "x-oqee-customization": "1",
                                "x-oqee-platform": "web",
                                "x-oqee-profile": "qYyeeAzNbuWNxByv",
                                "Content-Length": "25",
                                "Origin": "https://oqee.tv",
                                "DNT": "1",
                                "Connection": "keep-alive",
                                "Sec-Fetch-Dest": "empty",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Site": "cross-site",
                                "Priority": "u=4",
                                "Pragma": "no-cache",
                                "Cache-Control": "no-cache",
                                "TE": "trailers",
                            }
                        ),
                        "post_data": "R{SSM}",
                        "response_data": "J[result.license]",
                    }.values()
                ),
            },
        }

        return stream_info

    def get_catchup_stream_info(self, stream_id: str) -> dict:
        """Get catchup stream information (MPD address, Widewine key) for the specified id. Returned keys: path, mime_type, manifest_type, drm, license_type, license_key."""  # noqa: E501
        pass

    def get_streams(self) -> list:
        """Load stream data from OQEE and convert it to JSON-STREAMS format."""
        service_plan = {"channels": {}, "channel_list": []}
        service_plan = request_json(_SERVICE_PLAN_ENDPOINT, default={"result": service_plan})["result"]
        # channel_list = service_plan["channel_list"].sort(key=lambda channel: channel["number"])
        channel_list = service_plan["channel_list"]

        log(f"{len(channel_list)} channels found", xbmc.LOGINFO)

        return [
            {
                "preset": str(channel["number"]),
                **self._extract_channel_info(channel["channel_id"], service_plan["channels"]),
            }
            for channel in channel_list
        ]

    def get_epg(self) -> list:
        """Load EPG data from OQEE and convert it to JSON-EPG format."""
        return []

    def get_catchup_items(self, levels: List[str]) -> list:
        """Return a list of directory items for the specified levels."""
        pass

    def _extract_channel_info(self, channel_id: dict, channels: dict, icon_type: str = "icon_dark") -> dict:
        """."""
        for channel in channels.values():
            if channel["id"] == channel_id and channel.get("freebox_id") is not None:
                return {
                    "id": str(channel["freebox_id"]),
                    "name": channel["name"],
                    "logo": channel[icon_type].replace("%d", "200"),
                    "stream": build_addon_url(f"/stream/live/{channel['freebox_id']}"),
                }

        return {}
