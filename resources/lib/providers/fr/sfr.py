# -*- coding: utf-8 -*-
"""SFR"""

# https://ncdn-live-pctv.pfd.sfr.net/sdash/LIVE$TF1/index.mpd/Manifest?start=LIVE&end=END&device=dash_dyn_wide
# https://ncdn-live-pctv.pfd.sfr.net/sdash/LIVE$NEUF_FRANCE2/index.mpd/Manifest?start=LIVE&end=END&device=dash_dyn_wide
# https://ncdn-live-pctv.pfd.sfr.net/sdash/LIVE$NEUF_W9/index.mpd/Manifest?start=LIVE&end=END&device=dash_dyn_wide

from datetime import date, datetime, timedelta
import json
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from lib.providers import ProviderInterface
from lib.utils import get_global_setting, log, LogLevel, random_ua

class SFRProvider(ProviderInterface):
    """SFR provider"""
    endpoint_streams: str = 'https://ws-backendtv.sfr.fr/sekai-service-plan/public/v2/service-list?app=gen8&device=browser'
    endpoint_epg: str = 'https://static-cdn.tv.sfr.net/data/epg/gen8/guide_web_{day}.json'

    def get_stream_info(self, channel_id: int) -> dict:
        return {}

    def get_streams(self) -> list:
        req = Request(self.endpoint_streams, headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_streams).netloc
        })

        with urlopen(req) as res:
            channels = json.loads(res.read())

        streams = []

        for channel in channels:
            channel_id: str = channel['npvrId']
            channel_logo: str = None

            for image in channel['images']:
                if image['type'] == 'color':
                    channel_logo = image['url']

            streams.append({
                'id': channel['epgId'],
                'name': channel['name'],
                'preset': channel['zappingId'],
                'logo': channel_logo,
                'stream': f'plugin://plugin.video.orange.fr/channel/{channel_id}',
                'group': channel['categories']
            })

        return streams

    def get_epg(self) -> dict:
        days_to_display = range(
            -int(get_global_setting('epg.pastdaystodisplay')),
            int(get_global_setting('epg.futuredaystodisplay'))
        )

        epg = {}

        for day_to_display in days_to_display:
            day = datetime.combine(
                date.today() + timedelta(days=day_to_display),
                datetime.min.time()
            )

            self._get_epg_chunk(epg=epg, day=day.strftime('%Y%m%d'))

        return epg

    # pylint: disable=no-self-use
    def _get_epg_chunk(self, epg: dict, day: str):
        req = Request(self.endpoint_epg.format(day=day), headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_epg).netloc
        })

        with urlopen(req) as res:
            epg_chunk = json.loads(res.read())

        for channel_id in epg_chunk['epg']:
            if not channel_id in epg:
                epg[channel_id] = []

            for program in epg_chunk['epg'][channel_id]:
                episode = None
                if 'episodeNumber' in program and 'seasonNumber' in program:
                    episode_number = program['episodeNumber'] if program['episodeNumber'] > 9 else '0' + str(program['episodeNumber'])
                    season_number = program['seasonNumber'] if program['seasonNumber'] > 9 else '0' + str(program['seasonNumber'])
                    episode = f'S{season_number}E{episode_number}'

                image = None
                if isinstance(program.get('images'), list):
                    for program_image in program['images']:
                        if program_image['type'] == 'landscape' and program_image['withTitle'] is True:
                            image = program_image['url']

                epg[channel_id].append({
                    'start': (datetime.fromtimestamp(program['startDate'] / 1000).astimezone()).isoformat(),
                    'stop': (datetime.fromtimestamp(program['endDate'] / 1000).astimezone()).isoformat(),
                    'title': program.get('title'),
                    'subtitle': program.get('subTitle'),
                    'episode': episode,
                    'description': program.get('longSynopsis'),
                    'genre': program.get('genre'),
                    'image': image
                })
