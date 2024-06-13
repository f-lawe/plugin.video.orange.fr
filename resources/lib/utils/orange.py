"""."""

import codecs
import json
import re
from datetime import date, datetime, timedelta
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import xbmc

from lib.utils.request import get_random_ua
from lib.utils.xbmc import get_drm, get_global_setting, log

_ENDPOINT_EPG = "https://rp-ott-mediation-tv.woopic.com/api-gw/live/v3/applications/STB4PC/programs?period={period}&epgIds=all&mco={mco}"
_ENDPOINT_HOMEPAGE = "https://chaines-tv.orange.fr/"
_ENDPOINT_STREAM_INFO = "https://mediation-tv.orange.fr/all/api-gw/live/v3/auth/accountToken/applications/PC/channels/{channel_id}/stream?terminalModel=WEB_PC"
_ENDPOINT_STREAM_LOGO = "https://proxymedia.woopic.com/api/v1/images/2090%2Flogos%2Fv2%2Flogos%2F{external_id}%2F{hash}%2F{type}%2Flogo_{width}x{height}.png"
_ENDPOINT_STREAMS = "https://rp-ott-mediation-tv.woopic.com/api-gw/live/v3/applications/STB4PC/programs?groupBy=channel&epgIds=all&mco={mco}"


def get_stream_info(channel_id: str, mco: str = "OFR") -> dict:
    """Load stream info from Orange."""
    tv_token = _extract_tv_token()
    log(tv_token, xbmc.LOGDEBUG)

    url = _ENDPOINT_STREAM_INFO.format(channel_id=channel_id)
    headers = {**_build_headers(url), **{"tv_token": f"Bearer {tv_token}"}}
    req = Request(url, headers=headers)

    try:
        with urlopen(req) as res:
            stream_info = json.loads(res.read())
    except HTTPError as error:
        if error.code == 403:
            return False

    drm = get_drm()
    license_server_url = None
    for system in stream_info.get("protectionData"):
        if system.get("keySystem") == drm.value:
            license_server_url = system.get("laUrl")

    headers = {**_build_headers(url), **{"tv_token": f"Bearer {tv_token}", "Content-Type": ""}}
    h = ""

    for k, v in headers.items():
        h += f"{k}={v}&"

    headers = h[:-1]
    post_data = "R{SSM}"
    response = ""

    log(headers, xbmc.LOGDEBUG)

    stream_info = {
        "path": stream_info["url"],
        "mime_type": "application/xml+dash",
        "manifest_type": "mpd",
        "drm": drm.name.lower(),
        "license_type": drm.value,
        "license_key": f"{license_server_url}|{headers}|{post_data}|{response}",
    }

    log(stream_info, xbmc.LOGDEBUG)
    return stream_info


def get_streams(groups: dict, external_id_map: dict, mco: str = "OFR") -> list:
    """Load stream data from Orange and convert it to JSON-STREAMS format."""
    stream_details = _extract_stream_details(external_id_map)
    log(f"Stream details: {stream_details}", xbmc.LOGDEBUG)

    url = _ENDPOINT_STREAMS.format(mco=mco)
    headers = _build_headers(url)
    req = Request(url, headers=headers)

    with urlopen(req) as res:
        programs = json.loads(res.read())

    streams = []

    for channel_id in programs:
        channel_programs = programs[channel_id]

        if len(channel_programs) == 0:
            continue

        channel_program = channel_programs[0]
        external_id = channel_program["externalId"].replace("_ctv", "")
        channel_name = stream_details[external_id]["name"] if external_id in stream_details else external_id
        channel_logo = stream_details[external_id]["logo"] if external_id in stream_details else None

        # if channel_name == external_id:
        # log(" => " + channel_name)

        streams.append(
            {
                "id": channel_id,
                "name": channel_name,
                "preset": channel_program["channelZappingNumber"],
                "logo": channel_logo,
                "stream": f"plugin://plugin.video.orange.fr/channels/{channel_id}",
                "group": [group_name for group_name in groups if int(channel_id) in groups[group_name]],
            }
        )

    return streams


def get_epg(chunks_per_day: int = 2, mco: str = "OFR") -> dict:
    """Load EPG data from Orange and convert it to JSON-EPG format."""
    start_day = datetime.timestamp(
        datetime.combine(
            date.today() - timedelta(days=int(get_global_setting("epg.pastdaystodisplay"))), datetime.min.time()
        )
    )

    days_to_display = int(get_global_setting("epg.futuredaystodisplay")) + int(
        get_global_setting("epg.pastdaystodisplay")
    )

    chunk_duration = 24 * 60 * 60 / chunks_per_day
    programs = []

    for chunk in range(0, days_to_display * chunks_per_day):
        programs.extend(
            _get_programs(
                mco,
                period_start=(start_day + chunk_duration * chunk) * 1000,
                period_end=(start_day + chunk_duration * (chunk + 1)) * 1000,
            )
        )

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


def _get_programs(mco: str, period_start: int = None, period_end: int = None) -> list:
    """Return the programs for today (default) or the specified period."""
    try:
        period = f"{int(period_start)},{int(period_end)}"
    except ValueError:
        period = "today"

    url = _ENDPOINT_EPG.format(period=period, mco=mco)
    log(f"Fetching: {url}")
    req = Request(url, headers=_build_headers(url))

    with urlopen(req) as res:
        return json.loads(res.read())


def _build_headers(url: str) -> dict:
    """Build headers."""
    return {"User-Agent": get_random_ua(), "Host": urlparse(url).netloc}


def _extract_tv_token() -> str:
    """Extract TV token."""
    headers = _build_headers(_ENDPOINT_HOMEPAGE)
    req = Request(_ENDPOINT_HOMEPAGE, headers=headers)

    with urlopen(req) as res:
        html = res.read().decode("utf-8")

    return re.search('instanceInfo:{token:"([a-zA-Z0-9-_.]+)"', html).group(1)


def _extract_stream_details(external_id_map: dict) -> dict:
    """Extract stream name and logo."""
    headers = _build_headers(_ENDPOINT_HOMEPAGE)
    req = Request(_ENDPOINT_HOMEPAGE, headers=headers)

    with urlopen(req) as res:
        html = codecs.decode(res.read().decode("utf-8"), "unicode-escape")

    matches = re.findall('"([A-Z0-9+/\': ]*[A-Z][A-Z0-9+/\': ]*)","(livetv_[a-zA-Z0-9_]+)",', html)
    stream_details = {match[1]: {"name": match[0], "logo": None} for match in matches}

    log(stream_details, xbmc.LOGDEBUG)

    matches = re.findall(
        'path:"%2Flogos%2Fv2%2Flogos%2F(livetv_[a-z0-9_]+)%2F([0-9]+_[0-9]+)%2FmobileAppliDark%2Flogo_([0-9]+)x([0-9]+)\.png"',
        html,
    )

    for match in matches:
        if match[0] not in stream_details:
            stream_details[match[0]] = {"name": match[0]}

        stream_details[match[0]]["logo"] = _ENDPOINT_STREAM_LOGO.format(
            external_id=match[0],
            hash=match[1],
            type="mobileAppliDark",
            width=match[2],
            height=match[3],
        )

    stream_details = {
        _get_epg_external_id(external_id_map, external_id): stream_details[external_id]
        for external_id in stream_details
    }

    return stream_details


def _get_epg_external_id(external_id_map: dict, stream_external_id: str) -> str:
    """Format external id to new format."""
    epg_external_id = stream_external_id.lower().replace("_umts", "").replace("livetv_", "")
    epg_external_id = "livetv_" + external_id_map.get(epg_external_id, epg_external_id)
    log(f"{stream_external_id} => {epg_external_id}".format(stream_external_id, epg_external_id), xbmc.LOGDEBUG)
    return epg_external_id
