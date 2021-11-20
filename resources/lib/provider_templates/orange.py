# -*- coding: utf-8 -*-
"""Orange Template"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from lib.providers.provider_interface import ProviderInterface
from lib.utils import get_drm, get_global_setting, log, LogLevel, random_ua

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

    def get_stream_info(self, channel_id: int) -> dict:
        req = Request(self.endpoint_stream_info.format(channel_id=channel_id), headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_stream_info).netloc
        })

        try:
            with urlopen(req) as res:
                stream_info = json.loads(res.read())
        except HTTPError as error:
            if error.code == 403:
                return False

        drm = get_drm()
        license_server_url = None
        for system in stream_info.get('protectionData'):
            if system.get('keySystem') == drm.value:
                license_server_url = system.get('laUrl')

        headers = f'Content-Type=&User-Agent={random_ua()}&Host={urlparse(license_server_url).netloc}'
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
        req = Request(self.endpoint_streams, headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_streams).netloc
        })

        with urlopen(req) as res:
            channels = json.loads(res.read())

        streams = []

        for channel in channels:
            streams.append({
                'id': channel['id'],
                'name': channel['name'],
                'preset': channel['zappingNumber'],
                'logo': channel['logos']['square'],
                'stream': 'plugin://plugin.video.orange.fr/channel/{id}'.format(id=channel['id']),
                'group': [group_name for group_name in self.groups if int(channel['id']) in self.groups[group_name]]
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

            start = datetime.fromtimestamp(program['diffusionDate']).astimezone().replace(microsecond=0)
            stop = datetime.fromtimestamp(program['diffusionDate'] + program['duration']).astimezone()

            if program['programType'] != 'EPISODE':
                title = program['title']
                subtitle = None
                episode = None
            else:
                title = program['season']['serie']['title']
                subtitle = program['title']
                episode = 'S{s}E{e}'.format(s=program['season']['number'], e=program['episodeNumber'])

            image = None
            if isinstance(program['covers'], list):
                for cover in program['covers']:
                    if cover['format'] == 'RATIO_16_9':
                        image = program['covers'][0]['url']

            epg[program['channelId']].append({
                'start': start.isoformat(),
                'stop': stop.isoformat(),
                'title': title,
                'subtitle': subtitle,
                'episode': episode,
                'description': program['synopsis'],
                'genre': program['genre'] if program['genreDetailed'] is None else program['genreDetailed'],
                'image': image
            })

        return epg

    # pylint: disable=no-self-use
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
