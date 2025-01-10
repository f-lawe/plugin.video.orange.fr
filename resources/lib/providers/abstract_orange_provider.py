# ruff: noqa: D102
"""Orange provider template."""

import re
from abc import ABC
from datetime import date, datetime, timedelta
from time import strptime
from typing import List
from urllib.parse import urlencode

import xbmc
from requests import Session
from requests.exceptions import JSONDecodeError, RequestException

from lib.exceptions import AuthenticationRequired, StreamDataDecodeError, StreamNotIncluded
from lib.providers.abstract_provider import AbstractProvider
from lib.utils.kodi import build_addon_url, get_addon_setting, get_drm, get_global_setting, log, set_addon_setting
from lib.utils.request import request, request_json

_PROGRAMS_ENDPOINT = "https://rp-ott-mediation-tv.woopic.com/api-gw/live/v3/applications/STB4PC/programs?period={period}&epgIds=all&mco={mco}"
_CATCHUP_CHANNELS_ENDPOINT = "https://rp-ott-mediation-tv.woopic.com/api-gw/catchup/v4/applications/PC/channels"
_CATCHUP_ARTICLES_ENDPOINT = "https://rp-ott-mediation-tv.woopic.com/api-gw/catchup/v4/applications/PC/channels/{channel_id}/categories/{category_id}"
_CATCHUP_VIDEOS_ENDPOINT = "https://rp-ott-mediation-tv.woopic.com/api-gw/catchup/v4/applications/PC/groups/{group_id}"
_CHANNELS_ENDPOINT = "https://rp-ott-mediation-tv.woopic.com/api-gw/pds/v1/live/ew?everywherePopulation=OTT_Metro"

_LIVE_STREAM_ENDPOINT = "https://mediation-tv.orange.fr/all/api-gw/live/v3/auth/accountToken/applications/PC/channels/{stream_id}/stream?terminalModel=WEB_PC&terminalId={terminal_id}"
_CATCHUP_STREAM_ENDPOINT = "https://mediation-tv.orange.fr/all/api-gw/catchup/v4/auth/accountToken/applications/PC/videos/{stream_id}/stream?terminalModel=WEB_PC&terminalId={terminal_id}"

_STREAM_LOGO_URL = "https://proxymedia.woopic.com/api/v1/images/2090{path}"
_LIVE_HOMEPAGE_URL = "https://chaines-tv.orange.fr/"
_CATCHUP_VIDEO_URL = "https://replay.orange.fr/videos/{stream_id}"
_LOGIN_URL = "https://login.orange.fr"


class AbstractOrangeProvider(AbstractProvider, ABC):
    """Abstract Orange Provider."""

    chunks_per_day = 2
    mco = "OFR"
    groups = {}

    def get_live_stream_info(self, stream_id: str) -> dict:
        """Get live stream info."""
        auth_url = _LIVE_HOMEPAGE_URL
        return self._get_stream_info(auth_url, _LIVE_STREAM_ENDPOINT, stream_id)

    def get_catchup_stream_info(self, stream_id: str) -> dict:
        """Get catchup stream info."""
        auth_url = _CATCHUP_VIDEO_URL.format(stream_id=stream_id)
        return self._get_stream_info(auth_url, _CATCHUP_STREAM_ENDPOINT, stream_id)

    def get_streams(self) -> list:
        """Load stream data from Orange and convert it to JSON-STREAMS format."""
        channels = request_json(_CHANNELS_ENDPOINT, default={"channels": {}})["channels"]
        channels.sort(key=lambda channel: channel["displayOrder"])

        log(f"{len(channels)} channels found", xbmc.LOGINFO)

        return [
            {
                "id": str(channel["idEPG"]),
                "name": channel["name"],
                "preset": str(channel["displayOrder"]),
                "logo": self._extract_logo(channel["logos"]),
                "stream": build_addon_url(f"/stream/live/{channel['idEPG']}"),
                "group": [group_name for group_name in self.groups if int(channel["idEPG"]) in self.groups[group_name]],
            }
            for channel in channels
        ]

    def get_epg(self) -> dict:
        """Load EPG data from Orange and convert it to JSON-EPG format."""
        start_day = datetime.timestamp(
            datetime.combine(
                date.today() - timedelta(days=get_global_setting("epg.pastdaystodisplay", int)), datetime.min.time()
            )
        )

        days_to_display = get_global_setting("epg.futuredaystodisplay", int) + get_global_setting(
            "epg.pastdaystodisplay", int
        )

        programs = self._get_programs(start_day, days_to_display, self.chunks_per_day, self.mco)

        log(f"{len(programs)} EPG entries found", xbmc.LOGINFO)

        epg = {}

        for program in programs:
            if program["channelId"] not in epg:
                epg[program["channelId"]] = []

            if program["programType"] != "EPISODE":
                title = program["title"]
                subtitle = None
                episode = None
            else:
                title = program["season"]["serie"]["title"]
                subtitle = program["title"]
                season_number = program["season"]["number"]
                episode_number = program.get("episodeNumber", None)
                episode = f"S{season_number}E{episode_number}"

            image = None
            if isinstance(program["covers"], list):
                for cover in program["covers"]:
                    if cover["format"] == "RATIO_16_9":
                        image = program["covers"][0]["url"]

            epg[program["channelId"]].append(
                {
                    "start": datetime.fromtimestamp(program["diffusionDate"])
                    .astimezone()
                    .replace(microsecond=0)
                    .isoformat(),
                    "stop": (
                        datetime.fromtimestamp(program["diffusionDate"] + program["duration"]).astimezone()
                    ).isoformat(),
                    "title": title,
                    "subtitle": subtitle,
                    "episode": episode,
                    "description": program["synopsis"],
                    "genre": program["genre"] if program["genreDetailed"] is None else program["genreDetailed"],
                    "image": image,
                }
            )

        return epg

    def get_catchup_items(self, levels: List[str]) -> list:
        """Return a list of directory items for the specified levels."""
        depth = len(levels)

        if depth == 0:
            return self._get_catchup_channels()
        elif depth == 1:
            return self._get_catchup_categories(levels[0])
        elif depth == 2:
            return self._get_catchup_articles(levels[0], levels[1])
        elif depth == 3:
            return self._get_catchup_videos(levels[0], levels[1], levels[2])

    def _get_catchup_channels(self) -> list:
        """Load available catchup channels."""
        channels = request_json(_CATCHUP_CHANNELS_ENDPOINT, default=[])

        return [
            {
                "is_folder": True,
                "label": str(channel["name"]).upper(),
                "path": build_addon_url(f"/catchup/{channel['id']}"),
                "art": {"thumb": channel["logos"]["ref_millenials_partner_white_logo"]},
            }
            for channel in channels
        ]

    def _get_catchup_categories(self, channel_id: str) -> list:
        """Return a list of catchup categories for the specified channel id."""
        url = _CATCHUP_CHANNELS_ENDPOINT + "/" + channel_id
        categories = request_json(url, default={"categories": {}})["categories"]

        return [
            {
                "is_folder": True,
                "label": category["name"][0].upper() + category["name"][1:],
                "path": build_addon_url(f"/catchup/{channel_id}/{category['id']}"),
            }
            for category in categories
        ]

    def _get_catchup_articles(self, channel_id: str, category_id: str) -> list:
        """Return a list of catchup groups for the specified channel id and category id."""
        url = _CATCHUP_ARTICLES_ENDPOINT.format(channel_id=channel_id, category_id=category_id)
        articles = request_json(url, default={"articles": {}})["articles"]

        return [
            {
                "is_folder": True,
                "label": article["title"],
                "path": build_addon_url(f"/catchup/{channel_id}/{category_id}/{article['id']}"),
                "art": {"poster": article["covers"]["ref_16_9"]},
            }
            for article in articles
        ]

    def _get_catchup_videos(self, channel_id: str, category_id: str, article_id: str) -> list:
        """Return a list of catchup videos for the specified channel id and article id."""
        url = _CATCHUP_VIDEOS_ENDPOINT.format(group_id=article_id)
        videos = request_json(url, default={"videos": {}})["videos"]

        return [
            {
                "is_folder": False,
                "label": video["title"],
                "path": build_addon_url(f"/stream/catchup/{video['id']}"),
                "art": {"poster": video["covers"]["ref_16_9"]},
                "info": {
                    "duration": int(video["duration"]) * 60,
                    "genres": video["genres"],
                    "plot": video["longSummary"],
                    "premiered": datetime.fromtimestamp(int(video["broadcastDate"]) / 1000).strftime("%Y-%m-%d"),
                    "year": int(video["productionDate"]),
                },
            }
            for video in videos
        ]

    def _get_stream_info(self, auth_url: str, stream_endpoint: str, stream_id: str) -> dict:
        """Load stream info from Orange."""
        tv_token, tv_token_expires, wassup = self._retrieve_auth_data(auth_url)

        try:
            stream_endpoint_url = stream_endpoint.format(stream_id=stream_id, terminal_id="")
            headers = {"tv_token": f"Bearer {tv_token}", "Cookie": f"wassup={wassup}"}
            res = request("GET", stream_endpoint_url, headers=headers)
            stream = res.json()
            log("Initiate new session", xbmc.LOGINFO)
        except RequestException as e:
            if e.response.status_code == 403:
                raise StreamNotIncluded() from e
            else:
                raise AuthenticationRequired("Cannot initiate new session") from e
        tv_token, tv_token_expires, wassup = self._retrieve_auth_data(auth_url)

        try:
            stream_endpoint_url = stream_endpoint.format(stream_id=stream_id, terminal_id="")
            headers = {"tv_token": f"Bearer {tv_token}", "Cookie": f"wassup={wassup}"}
            res = request("GET", stream_endpoint_url, headers=headers)
            stream = res.json()
            log("Initiate new session", xbmc.LOGINFO)
        except RequestException as e:
            if e.response.status_code == 403:
                raise StreamNotIncluded() from e
            else:
                raise AuthenticationRequired("Cannot initiate new session") from e
        except JSONDecodeError as e:
            raise StreamDataDecodeError() from e

        return self._compute_stream_info(stream, tv_token, wassup)

    def _compute_stream_info(self, stream: dict, tv_token: str, wassup: str) -> dict:
        """Compute stream info."""
        protectionData = (
            stream.get("protectionData") if stream.get("protectionData") is not None else stream.get("protectionDatas")
        )

        license_server_url = None

        for system in protectionData:
            if system.get("keySystem") == get_drm():
                license_server_url = system.get("laUrl")

        stream_info = {
            "path": stream.get("url"),
            "protocol": "mpd",
            "mime_type": "application/xml+dash",
            "drm_config": {
                "license_type": get_drm(),
                "license_key": "|".join(
                    {
                        "licence_server_url": license_server_url,
                        "headers": urlencode(
                            {
                                "tv_token": f"Bearer {tv_token}",
                                "Content-Type": "",
                                "Cookie": f"wassup={wassup}",
                            }
                        ),
                        "post_data": "R{SSM}",
                        "response_data": "",
                    }.values()
                ),
            },
        }

        log(stream_info, xbmc.LOGDEBUG)
        return stream_info

    def _retrieve_auth_data(self, auth_url: str, login: str = None, password: str = None) -> (str, str, str):
        """Retreive auth data from Orange (tv token and wassup cookie)."""
        provider_session_data = get_addon_setting("provider.session_data", dict)
        tv_token, tv_token_expires, wassup = (
            provider_session_data.get(k) for k in ("tv_token", "tv_token_expires", "wassup")
        )

        if not tv_token_expires or datetime.utcnow().timestamp() > tv_token_expires:
            URL_ROOT = "https://chaines-tv.orange.fr"
            USER_AGENT_FIREFOX = "Mozilla/5.0 (Windows NT 10.0; rv:114.0) Gecko/20100101 Firefox/114.0"
            session = Session()
            session.headers = {
                "User-Agent": USER_AGENT_FIREFOX,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
            }

            if not self._expired_wassup(wassup):
                log("Cookie reuse", xbmc.LOGINFO)
                response = session.get(URL_ROOT + "/token", cookies={"wassup": wassup})
            else:
                response = session.get(URL_ROOT + "/token")
                if response.status_code != 200:
                    log("Login required", xbmc.LOGINFO)
                    self._login(session)
                    response = session.get(URL_ROOT + "/token")

            tv_token = response.json()
            tv_token_expires = datetime.utcnow().timestamp() + 30 * 60
            if "wassup" in session.cookies:
                wassup = session.cookies.get("wassup")
            provider_session_data = {
                "tv_token": tv_token,
                "tv_token_expires": tv_token_expires,
                "wassup": wassup,
            }
            set_addon_setting("provider.session_data", provider_session_data)

        log(f"tv_token: {tv_token}, tv_token_expires: {tv_token_expires}, wassup: {wassup}", xbmc.LOGDEBUG)
        return tv_token, tv_token_expires, wassup

    def _expired_wassup(self, wassup):
        try:
            wassup = bytes.fromhex(wassup).decode()
            xwvd = re.search("\|X_WASSUP_VALID_DATE=(.*?)\|", wassup).group(1)
            # expiration = datetime.strptime(xwvd, '%Y%m%d%H%M%S').timestamp()
            wassup_expires = datetime(*(strptime(xwvd, "%Y%m%d%H%M%S")[0:6])).timestamp()
            return datetime.utcnow().timestamp() > wassup_expires
        except:
            return True

    def _login(self, session) -> dict:
        """Login to Orange and return session cookie."""
        URL_LOGIN = "https://login.orange.fr"
        login, password = get_addon_setting("provider.username"), get_addon_setting("provider.password")
        session.get(URL_LOGIN)
        session.post(URL_LOGIN + "/api/login", data={"login": login, "params": {}})
        session.post(URL_LOGIN + "/api/password", json={"password": password, "remember": True})

    def _extract_logo(self, logos: list, definition_type: str = "mobileAppliDark") -> str:
        for logo in logos:
            if logo["definitionType"] == definition_type:
                return _STREAM_LOGO_URL.format(path=logo["listLogos"][0]["path"])

        return None

    def _get_programs(self, start_day: int, days_to_display: int, chunks_per_day: int = 2, mco: str = "OFR") -> list:
        """Return the programs for today (default) or the specified period."""
        programs = []
        chunk_duration = 24 * 60 * 60 / chunks_per_day

        for chunk in range(0, days_to_display * chunks_per_day):
            period_start = (start_day + chunk_duration * chunk) * 1000
            period_end = (start_day + chunk_duration * (chunk + 1)) * 1000

            try:
                period = f"{int(period_start)},{int(period_end)}"
            except ValueError:
                period = "today"

            url = _PROGRAMS_ENDPOINT.format(period=period, mco=mco)
            programs.extend(request_json(url, default=[]))

        return programs
