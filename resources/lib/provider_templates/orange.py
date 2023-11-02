# -*- coding: utf-8 -*-
"""Orange Template"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
import os
import re
import xbmcvfs
from urllib.error import HTTPError
from urllib.parse import urlparse, quote
from urllib.request import Request, urlopen

from lib.providers.provider_interface import ProviderInterface
from lib.utils import get_drm, get_global_setting, log, LogLevel, random_ua, get_addon_profile

@dataclass
class OrangeTemplate(ProviderInterface):
    """This template helps creating providers based on the Orange architecture"""
    chunks_per_day: int = 2

    def __init__(
        self,
        endpoint_stream_info: str,
        endpoint_streams: str,
        endpoint_programs: str,
        groups: dict = None
    ) -> None:
        self.endpoint_stream_info = endpoint_stream_info
        self.endpoint_streams = endpoint_streams
        self.endpoint_programs = endpoint_programs
        self.groups = groups

    def auth(self, reset=False):
        timestamp = datetime.timestamp(datetime.today())
        filepath = os.path.join(xbmcvfs.translatePath(get_addon_profile()), 'auth')

        try:
            with open(filepath) as file:
                auth = json.loads(file.read())
        except FileNotFoundError:
            auth = {'timestamp': timestamp}

        if 'cookie' not in auth or reset is True:
            req = Request("https://chaines-tv.orange.fr", headers={
                'User-Agent': random_ua(),
                'Host': 'chaines-tv.orange.fr',
            })
            res = urlopen(req)
            cookie = res.headers['Set-Cookie'].split(";")[0]
            tv_token = "Bearer %s" % re.sub('.*token:"', '', str(res.read()), 1)
            tv_token = re.sub('",claims:.*', '', tv_token, 1)
            auth = {'timestamp': timestamp, 'cookie': cookie, 'tv_token': tv_token}
            with open(filepath, 'w') as file:
                file.write(json.dumps(auth))

        return auth


    def get_stream_info(self, channel_id: int) -> dict:
        timestamp = datetime.timestamp(datetime.today())
        for trie in range(2):
            auth = self.auth()
            req = Request(self.endpoint_stream_info.format(channel_id=channel_id), headers={
                'User-Agent': random_ua(),
                'Host': urlparse(self.endpoint_stream_info).netloc,
                'Cookie': auth["cookie"],
                'tv_token': auth["tv_token"],
            })

            try:
                with urlopen(req) as res:
                    stream_info = json.loads(res.read())
                break
            except HTTPError as error:
                if error.code in (403, 401):
                    if trie == 0:
                        log("cookie/token invalide, âge = %d" % (timestamp - auth["timestamp"]), LogLevel.DEBUG)
                        self.auth(reset=True)
                    else:
                        raise error

        drm = get_drm()
        license_server_url = None
        for system in stream_info.get('protectionData'):
            if system.get('keySystem') == drm.value:
                license_server_url = system.get('laUrl')

        headers = f'Content-Type=&User-Agent={random_ua()}&Host={urlparse(license_server_url).netloc}'
        headers += '&Cookie=%s' % quote(auth["cookie"])
        headers += '&tv_token=%s' % quote(auth["tv_token"])
        post_data = 'R{SSM}'
        response = ''

        stream_info = {
            'path': stream_info['url'],
            'mime_type': 'application/xml+dash',
            'manifest_type': 'mpd',
            'drm': drm.name.lower(),
            'license_type': drm.value,
            'license_key': f'{license_server_url}|{headers}|{post_data}|{response}'
        }

        log(stream_info, LogLevel.DEBUG)
        return stream_info

    def get_streams(self) -> list:
        auth = self.auth()
        req = Request(self.endpoint_streams, headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_streams).netloc,
            'Cookie': auth["cookie"],
            'tv_token': auth["tv_token"],
        })

        with urlopen(req, timeout=60) as res:
            channels = json.loads(res.read())

        streams = []

        for channel in channels:
            channel_infos = channels[channel][0]
            channel_id: str = channel
            channel_name = channel_infos['externalId']
            if channel_name.startswith("livetv_"):
                channel_name = channel_name[7:]
            if channel_name.endswith("_ctv"):
                channel_name = channel_name[:-4]
            streams.append({
                'id': channel_id,
                'name': channel_name,
                'preset': channel_infos['channelZappingNumber'],
                'logo': None,
                'stream': f'plugin://plugin.video.orange.fr/channel/{channel_id}',
                'group': [group_name for group_name in self.groups if int(channel_id) in self.groups[group_name]]
            })

        return streams

    def get_epg(self) -> dict:
        start_day = datetime.timestamp(
            datetime.combine(
                date.today() - timedelta(days=int(get_global_setting('epg.pastdaystodisplay'))),
                datetime.min.time()
            )
        )

        days_to_display = int(get_global_setting('epg.futuredaystodisplay')) \
            + int(get_global_setting('epg.pastdaystodisplay'))

        chunk_duration = 24 * 60 * 60 / self.chunks_per_day
        programs = []

        for chunk in range(0, days_to_display * self.chunks_per_day):
            programs.extend(self._get_programs(
                period_start=(start_day + chunk_duration * chunk) * 1000,
                period_end=(start_day + chunk_duration * (chunk + 1)) * 1000
            ))

        epg = {}

        for program in programs:
            if not program['channelId'] in epg:
                epg[program['channelId']] = []

            if program['programType'] != 'EPISODE':
                title = program['title']
                subtitle = None
                episode = None
            else:
                title = program['season']['serie']['title']
                subtitle = program['title']
                season_number = program['season']['number']
                episode_number = program['episodeNumber'] if 'episodeNumber' in program else None
                episode = f'S{season_number}E{episode_number}'

            image = None
            if isinstance(program['covers'], list):
                for cover in program['covers']:
                    if cover['format'] == 'RATIO_16_9':
                        image = program['covers'][0]['url']

            epg[program['channelId']].append({
                'start': datetime.fromtimestamp(program['diffusionDate']).astimezone().replace(microsecond=0).isoformat(),
                'stop': (datetime.fromtimestamp(program['diffusionDate'] + program['duration']).astimezone()).isoformat(),
                'title': title,
                'subtitle': subtitle,
                'episode': episode,
                'description': program['synopsis'],
                'genre': program['genre'] if program['genreDetailed'] is None else program['genreDetailed'],
                'image': image
            })

        return epg

    def _get_programs(self, period_start: int = None, period_end: int = None) -> list:
        """Returns the programs for today (default) or the specified period"""
        try:
            period = f'{int(period_start)},{int(period_end)}'
        except ValueError:
            period = 'today'

        req = Request(self.endpoint_programs.format(period=period), headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_programs).netloc
        })

        with urlopen(req) as res:
            return json.loads(res.read())
