# -*- coding: utf-8 -*-
"""Free"""

# mafreebox.freebox.fr/freeboxtv/playlist.m3u
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from lib.providers import ProviderInterface
from lib.utils import get_global_setting, log, LogLevel, random_ua

class FreeProvider(ProviderInterface):
    """Free provider"""
    endpoint_streams: str = 'http://mafreebox.freebox.fr/freeboxtv/playlist.m3u'
    # pylint: disable=line-too-long
    regexp_stream: str = r'#EXTINF:\d,(\d+) - ([a-zA-Z0-9 ]+) (HD|\(bas débit\))?\s(rtsp://mafreebox.freebox.fr/fbxtv_pub/stream\?namespace=1&service=(\d+)&flavour=(hd|sd|ld))'

    def get_stream_info(self, channel_id: int) -> dict:
        log('Free get stream info', LogLevel.INFO)
        return {}

    def get_streams(self) -> list:
        log('Free get streams', LogLevel.INFO)

        req = Request(self.endpoint_streams, headers={
            'User-Agent': random_ua(),
            'Host': urlparse(self.endpoint_streams).netloc
        })

        with urlopen(req) as res:
            channels = res.read().decode('utf-8')

        regexp = re.compile(self.regexp_stream)
        channels = regexp.findall(channels)
        # 0: zapping, 1: name, 2: quality full, 3: stream, 4: id, 5: quality

        single_channels = {}

        for channel in channels:
            if single_channels.get(channel[4]) is not None:
                if single_channels[channel[4]][5] == 'hd':
                    continue

                if single_channels[channel[4]][5] == 'ld' and channel[5] == 'sd':
                    continue

            single_channels[channel[4]] = channel

        streams = []

        for channel in list(single_channels.values()):
            streams.append({
                'id': channel[4],
                'name': channel[1],
                'preset': channel[0],
                'stream': channel[3],
            })

        # log(streams, LogLevel.INFO)

        return streams

    def get_epg(self) -> dict:
        log('Free get epg', LogLevel.INFO)
        return {}
