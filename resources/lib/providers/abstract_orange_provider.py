# ruff: noqa: D102
"""Orange provider template."""

import json
import re
from abc import ABC
from datetime import date, datetime, timedelta
from time import strptime
from typing import List
from urllib.parse import urlencode

import xbmc
import xbmcvfs
import xbmcaddon

from requests import Session
from requests.exceptions import JSONDecodeError, RequestException

from lib.exceptions import AuthenticationRequired, StreamDataDecodeError, StreamNotIncluded
from lib.providers.abstract_provider import AbstractProvider
from lib.utils.kodi import build_addon_url, get_addon_setting, get_drm, get_global_setting, log
from lib.utils.request import request, request_json


WEBAPP_PUBLIC_URL = "https://tv.orange.fr"

## old EPG endpoint
PROGRAMS_ENDPOINT = "https://rp-ott-mediation-tv.woopic.com/api-gw/live/v3/applications/STB4PC/programs?period={period}&epgIds=all&mco={mco}"

## new EPG endpoint
# BFF_EPG_GRID_URL = "/bff-guidetv-epggrid/v1/auth/accountToken/guidetv/epggrid/epggrid-tv-grid"

class AbstractOrangeProvider(AbstractProvider, ABC):
    """Abstract Orange Provider."""

    chunks_per_day = 2
    mco = "OFR"
    groups = {}

    def __init__(self):
        """Fetch auth data from home page and build __pinia and __config variables."""
        headers = {}
        profile_path = xbmcaddon.Addon().getAddonInfo('profile')
        pinia_file = f'{profile_path}__pinia.json'
        config_file = f'{profile_path}__config.json'

        if xbmcvfs.exists(pinia_file):
            with xbmcvfs.File(pinia_file) as f:
                self.__pinia = json.loads(f.read())
            with xbmcvfs.File(config_file) as f:
                self.__config = json.loads(f.read())

            if self.__pinia["tv_token_expires"] > datetime.utcnow().timestamp():
                return

            wassup = self.__pinia["wassup"]
            if self._is_wassup_valid(wassup):
                headers = {"Cookie": f"wassup={wassup}"}

        response = request("GET", WEBAPP_PUBLIC_URL, headers=headers)
        self.__pinia = json.loads(re.search('window.__pinia = ({.*?});', response.text).group(1))
        self.__config = json.loads(re.search('window.__config = ({.*?});', response.text).group(1))

        if not self.__pinia['authStore']['isAuthenticated']:
            log("Not on Orange network, login required", xbmc.LOGINFO)
            if not get_addon_setting("provider.use_credentials", bool):
                raise AuthenticationRequired("Please provide and use your credentials")
            wassup = self._login()
            headers = {"Cookie": f"wassup={wassup}"}
            response = request("GET", WEBAPP_PUBLIC_URL, headers=headers)
            self.__pinia = json.loads(re.search('window.__pinia = ({.*?});', response.text).group(1))
            self.__pinia["wassup"] = wassup
        
        if "wassup" in response.cookies:
            self.__pinia["wassup"] = response.cookies.get("wassup")

        self.__pinia["tv_token_expires"] = datetime.utcnow().timestamp() + 30 * 60

        with xbmcvfs.File(pinia_file, 'w') as f:
            f.write(json.dumps(self.__pinia))

        self.__config["PARAMS"] = "&".join([
            f'appVersion={self.__pinia["appStore"]["appVersion"]}',
            f'deviceModel={self.__config["BFF_DEVICE_MODEL"]}',
            f'deviceCategory={self.__config["BFF_DEVICE_CATEGORY"]}',
            f'customerOrangePopulation={self.__pinia["userStore"]["rights"]["customerOrangePopulation"]}',
            f'customerCanalPopulation={self.__pinia["userStore"]["rights"]["customerCanalPopulation"]}',
            'consentPersoStatus=0',
        ])

        if not xbmcvfs.exists(config_file):
            with xbmcvfs.File(config_file, 'w') as f:
                f.write(json.dumps(self.__config))
    
    def _is_wassup_valid(self, wassup: str) -> bool:
        """Check if wassup cookie is valid."""
        decoded_wassup = bytes.fromhex(wassup).decode()
        xwvd = re.search("\|X_WASSUP_VALID_DATE=(.*?)\|", decoded_wassup).group(1)
        wassup_expires = datetime(*(strptime(xwvd, "%Y%m%d%H%M%S")[0:6]))
        return wassup_expires > datetime.utcnow()

    def _login(self):
        """Login to Orange to get wassup cookie."""
        url = self.__config["IDME_URL"].split('/?')[0]
        session = Session()
        session.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
        }

        try:
            request("POST", f"{url}/api/access", data='{}', session=session)
        except RequestException:
            log("Error while authenticating (access)", xbmc.LOGWARNING)
            return

        try:
            data = json.dumps({"login": get_addon_setting("provider.username"), "loginOrigin": "input"})
            request("POST", f"{url}/api/login", data=data, session=session)
        except RequestException:
            log("Error while authenticating (login)", xbmc.LOGWARNING)
            return

        try:
            data = json.dumps({"password": get_addon_setting("provider.password"), "remember": True})
            request("POST", f"{url}/api/password", data=data, session=session)
        except RequestException:
            log("Error while authenticating (password)", xbmc.LOGWARNING)
            return

        wassup = session.cookies.get('wassup')
        if not wassup:
            log("Error while authenticating (wassup not found)", xbmc.LOGWARNING)

        return wassup

    def _get_auth_headers(self) -> dict:
        return {
            "Cookie": f"wassup={self.__pinia['wassup']}",
            "tv_token": f"Bearer {self.__pinia['authStore']['authInitEw']['token']}"
        }

    def get_live_stream_info(self, stream_id: str) -> dict:
        """Get live stream info."""
        live_endpoint = get_addon_setting("provider.live")
        live_key = "LIVE_STREAM_URL" if live_endpoint == "live" else "LIVE_STREAM_STARTOVER_URL"
        url = f'{self.__config["TV_GW_BASE_URL"]}/{self.__config[live_key]}/{stream_id}?{self.__config["PARAMS"]}'
        return self._get_stream_info(url)

    def get_catchup_stream_info(self, stream_id: str) -> dict:
        """Get catchup stream info."""
        url = (
            f'{self.__config["TV_GW_BASE_URL"]}/{self.__config["REPLAY_AUTH_URL"]}/PC/videos/{stream_id}/stream'
            f'?terminalModel={self.__config["REPLAY_TERMINAL_MODEL"]}&terminalId='
        )
        return self._get_stream_info(url)

    def get_streams(self) -> list:
        """Load stream data from Orange and convert it to JSON-STREAMS format."""
        headers = self._get_auth_headers()
        url = f'{self.__config["TV_GW_BASE_URL"]}/{self.__config["LIVE_SERVICE_PLAN_URL"]}?{self.__config["PARAMS"]}'
        channels = request_json(url, headers=headers)["channels"]
        log(f"{len(channels)} channels found", xbmc.LOGINFO)

        return [
            {
                "id": str(channel["epgId"]),
                "name": channel["name"],
                "preset": channel["lcn"],
                "logo": channel["logos"][0]['logoImageUrl'] + '|verifypeer=false',
                "stream": build_addon_url(f'/stream/live/{channel["externalId"]}'),
                "group": [group_name for group_name in self.groups if channel["epgId"] in self.groups[group_name]],
            }
            for channel in channels if channel['subscribed'] and channel["externalId"] != 'livetv_acces_limite_ctv'
        ]

    def get_epg(self) -> dict:
        """Load EPG data from Orange and convert it to JSON-EPG format."""
        past_days_to_display = get_global_setting("epg.pastdaystodisplay", int)
        future_days_to_display = get_global_setting("epg.futuredaystodisplay", int)

        start_day = datetime.combine(date.today() - timedelta(days=past_days_to_display), datetime.min.time())
        days_to_display = past_days_to_display + future_days_to_display

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

            start = datetime.fromtimestamp(program["diffusionDate"]).astimezone().replace(microsecond=0).isoformat()
            stop = datetime.fromtimestamp(program["diffusionDate"] + program["duration"]).astimezone().isoformat()

            epg[program["channelId"]].append(
                {
                    "start": start,
                    "stop": stop,
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
        item_getters = [
            self._get_catchup_channels,
            self._get_catchup_categories,
            self._get_catchup_articles,
            self._get_catchup_videos,
            self._get_catchup_video,
        ]

        return item_getters[depth](*levels)

    def _get_catchup_channels(self) -> list:
        """Load available catchup channels."""
        headers = self._get_auth_headers()
        url = (
            f'{self.__config["TV_GW_BASE_URL"]}/{self.__config["BFF_REPLAY_LISTING_CHANNELS_URL"]}'
            f'?{self.__config["PARAMS"]}'
        )
        channels = request_json(url, headers=headers)['page']['sections'][1]['items']
        # log(f"channels : {channels}", xbmc.LOGINFO)

        return [
            {
                "is_folder": True,
                "label": channel["titleText"],
                "path": build_addon_url(
                    f"/catchup/{channel['events']['onClick']['track']['trackParams'][-2]['value']}"
                ),
                "art": {"thumb": channel["titleLogoImageUrl"] + '|verifypeer=false'},
            }
            for channel in channels if 'rightTag' not in channel
        ]

    def _get_catchup_categories(self, channel_id: str) -> list:
        """Return a list of catchup categories for the specified channel id."""
        headers = self._get_auth_headers()
        url = (
            f'{self.__config["TV_GW_BASE_URL"]}/{self.__config["BFF_REPLAY_LANDING_CHANNEL_URL"]}'
            f'?{self.__config["PARAMS"]}&channelId={channel_id}'
        )
        categories = request_json(url, headers=headers)['page']['sections'][1:]
        # log(f"categories : {categories}", xbmc.LOGINFO)
        
        return [
            {
                "is_folder": True,
                "label": category['title']['text'],
                "path": build_addon_url(
                    f"/catchup/{channel_id}/{category['extraLink']['events']['onClick']['navigate']['route'].split('/')[-1]}"
                ),
            }
            for category in categories
        ]

    def _get_catchup_articles(self, channel_id: str, category_id: str) -> list:
        """Return a list of catchup groups for the specified channel id and category id."""
        headers = self._get_auth_headers()
        url = (
            f'{self.__config["TV_GW_BASE_URL"]}/{self.__config["BFF_REPLAY_LISTING_CHANNEL_CATEGORY_URL"]}'
            f'?{self.__config["PARAMS"]}&channelId={channel_id}&categoryId={category_id}'
        )
        articles = request_json(url, headers=headers)['page']['sections'][1]['items']
        # log(f"articles : {articles}", xbmc.LOGINFO)

        table = []
        for article in articles:
            route = article['events']['onClick']['navigate']['route'].split('/')
            if route[-2] == 'videos':
                path = f"/catchup/{channel_id}/{category_id}/{route[-1]}/{route[-1]}"
            else:
                path = f"/catchup/{channel_id}/{category_id}/{route[-1]}"
            table.append(
                {
                    "is_folder": True,
                    "label": article["titleText"],
                    "path": build_addon_url(path),
                    "art": {"poster": article["backgroundImageUrl"] + '|verifypeer=false'},
                }
            )

        return table

    def _get_catchup_videos(self, channel_id: str, category_id: str, article_id: str) -> list:
        """Return a list of catchup videos for the specified channel id, category id and article id."""
        headers = self._get_auth_headers()
        url = (
            f'{self.__config["TV_GW_BASE_URL"]}/{self.__config["BFF_REPLAY_FIP_URL"]}/fip-replay-serial'
            f'?{self.__config["PARAMS"]}&groupId={article_id}'
        )
        videos = request_json(url, headers=headers)['page']['sections'][2]['items']
        # log(f"videos : {videos}", xbmc.LOGINFO)

        if len(videos) == 1:
            return self._get_catchup_video(
                channel_id, category_id, article_id, videos[0]['events']['onClick']['track']['trackParams'][0]['value']
            )

        return [
            {
                "is_folder": True,
                "label": video["titleText"],
                "path": build_addon_url(
                    f"/catchup/{channel_id}/{category_id}/{article_id}/{video['events']['onClick']['track']['trackParams'][0]['value']}"
                ),
                "art": {"poster": video["backgroundImageUrl"] + '|verifypeer=false'},
                "info": {
                    "plot": f'[B]{video["titleText"]}[/B]\n{video["mainText"]["text"]}',
                },
            }
            for video in videos
        ]

    def _get_catchup_video(self, channel_id: str, category_id: str, article_id: str, video_id: str) -> dict:
        """Return a catchup video for the article id."""
        headers = self._get_auth_headers()
        url = (
            f'{self.__config["TV_GW_BASE_URL"]}/{self.__config["BFF_REPLAY_FIP_URL"]}/fip-replay-unit'
            f'?{self.__config["PARAMS"]}&videoId={video_id}'
        )
        video = request_json(url, headers=headers)['page']['sections']
        # log(f"video : {video}", xbmc.LOGINFO)

        return [
            {
                "is_folder": False,
                "label": video[1]['title']['text'],
                "path": build_addon_url(f"/stream/catchup/{video_id}"),
                "art": {"poster": video[1]["backgroundImageUrl"] + '|verifypeer=false'},
                "info": {
                    # "duration": int(video["duration"]) * 60,
                    # "genres": video["genres"],
                    "plot": (
                        f'[B]{video[1]["information"]["text"]}[/B]\n'
                        f'[I]{video[1]["footNote"]}[/I]\n'
                        f'{video[2]["items"][0]["paragraphs"][0]["text"]}'
                    ),
                    # "premiered": datetime.fromtimestamp(int(video["broadcastDate"]) / 1000).strftime("%Y-%m-%d"),
                    # "year": int(video["productionDate"]),
                },
            }
        ]

    def _get_stream_info(self, stream_endpoint_url: str) -> dict:
        """Load stream info from Orange."""
        headers = self._get_auth_headers()
        try:
            res = request("GET", stream_endpoint_url, headers=headers)
            stream = res.json()
        except RequestException as e:
            if e.response.status_code == 403:
                raise StreamNotIncluded() from e
            else:
                raise AuthenticationRequired("Cannot load stream data") from e
        except JSONDecodeError as e:
            raise StreamDataDecodeError() from e

        return self._format_stream_info(stream)

    def _format_stream_info(self, stream: dict) -> dict:
        """Compute stream info."""
        headers = self._get_auth_headers()
        protectionData = stream.get("protectionData") or stream.get("protectionDatas")
        path = stream.get("streamURL") or stream.get("url")

        license_server_url = (
            f'{self.__config["TV_GW_BASE_URL"]}/{self.__config["STREAM_LICENSE_AUTH_URL"]}'
            if stream.get("url") is None else ""
        )

        for system in protectionData:
            if system.get("keySystem") == get_drm():
                license_server_url += system.get("laUrl")

        stream_info = {
            "path": path,
            "protocol": "mpd",
            "mime_type": "application/xml+dash",
            "drm_config": {
                "license_type": get_drm(),
                "license_key": "|".join(
                    {
                        "licence_server_url": license_server_url,
                        "headers": urlencode({"Content-Type": "", **headers}),
                        "post_data": "R{SSM}",
                        "response_data": "",
                    }.values()
                ),
            },
        }

        log(stream_info, xbmc.LOGDEBUG)
        return stream_info

    def _get_programs(self, start_day: datetime, days_to_display: int, chunks_per_day: int, mco: str = "OFR") -> list:
        """Return the programs for today (default) or the specified period."""
        programs = []
        start_day_timestamp = start_day.timestamp()
        chunk_duration = 24 * 60 * 60 / chunks_per_day

        for chunk in range(0, days_to_display * chunks_per_day):
            period_start = (start_day_timestamp + chunk_duration * chunk) * 1000
            period_end = (start_day_timestamp + chunk_duration * (chunk + 1)) * 1000

            try:
                period = f"{int(period_start)},{int(period_end)}"
            except ValueError:
                period = "today"

            url = PROGRAMS_ENDPOINT.format(period=period, mco=mco)
            programs.extend(request_json(url, default=[]))

        return programs
