# -*- coding: utf-8 -*-
"""Orange Template"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import json
import os
import re
from urllib.error import HTTPError
from urllib.parse import urlparse, quote
from urllib.request import Request, urlopen
import xbmcvfs

from lib.providers.provider_interface import ProviderInterface
from lib.utils import get_drm, get_global_setting, log, LogLevel, random_ua, get_addon_profile, get_addon_path

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

    def _get_auth(self) -> tuple:
        timestamp = datetime.timestamp(datetime.today())
        filepath = os.path.join(xbmcvfs.translatePath(get_addon_profile()), 'auth')

        req = Request("https://chaines-tv.orange.fr", headers={
            'User-Agent': random_ua(),
            'Host': 'chaines-tv.orange.fr',
        })

        with urlopen(req) as res:
            nuxt = re.sub('.*<script>window', 'window', str(res.read()), 1)
            nuxt = re.sub('</script>.*', '', nuxt, 1)
            cookie = res.headers['Set-Cookie'].split(";")[0]
            tv_token = re.sub('.*token:"', 'Bearer ', nuxt, 1)
            tv_token = re.sub('",claims:.*', '', tv_token, 1)
            auth = {'timestamp': timestamp, 'cookie': cookie, 'tv_token': tv_token}
            with open(filepath, 'w', encoding='UTF-8') as file:
                file.write(json.dumps(auth))

        return nuxt, cookie, tv_token

    def _auth_urlopen(self, url: str, headers: dict = None) -> tuple:
        if headers is None:
            headers = {}
        timestamp = datetime.timestamp(datetime.today())
        filepath = os.path.join(xbmcvfs.translatePath(get_addon_profile()), 'auth')

        try:
            with open(filepath, encoding='UTF-8') as file:
                auth = json.loads(file.read())
        except FileNotFoundError:
            auth = {'timestamp': timestamp}

        for _ in range(2):
            if 'cookie' in auth:
                headers['cookie'] = auth['cookie']
                headers['tv_token'] = auth['tv_token']
                req = Request(url, headers=headers)

                try:
                    with urlopen(req) as res:
                        if res.code == 200:
                            return res.read(), auth['cookie'], auth['tv_token']
                except HTTPError as error:
                    if error.code == 401:
                        log(f"cookie/token invalide, âge = {int(timestamp - auth['timestamp'])}", LogLevel.INFO)
                    if error.code == 403:
                        log("cette chaine ne fait pas partie de votre offre.", LogLevel.INFO)
                        break
                    else:
                        log(f"erreur {error}", LogLevel.INFO)
                        raise

            _, auth['cookie'], auth['tv_token'] = self._get_auth()

        return None, None, None

    def get_stream_info(self, channel_id: int) -> dict:
        res, cookie, tv_token = self._auth_urlopen(self.endpoint_stream_info.format(channel_id=channel_id), headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_stream_info).netloc
        })

        if res is None:
            return False

        stream_info = json.loads(res)

        drm = get_drm()
        license_server_url = None
        for system in stream_info.get('protectionData'):
            if system.get('keySystem') == drm.value:
                license_server_url = system.get('laUrl')

        headers = f'Content-Type=&User-Agent={random_ua()}&Host={urlparse(license_server_url).netloc}'
        headers += f'&Cookie={quote(cookie)}&tv_token={quote(tv_token)}'
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
        filepath = os.path.join(xbmcvfs.translatePath(get_addon_path()), 'channels.json')
        with open(filepath, encoding='UTF-8') as file:
            channels = json.load(file)

        streams = []

        for channel in channels:
            channel_id = str(channel['idEPG'])
            logourl = None
            for logo in channel['logos']:
                if logo['definitionType'] == 'webTVSquare':
                    logourl = logo['listLogos'][0]['path']
                    break
            streams.append({
                'id': channel_id,
                'name': channel['name'],
                'preset': str(channel['displayOrder']),
                'logo': logourl,
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
