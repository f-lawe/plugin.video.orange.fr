# -*- coding: utf-8 -*-
"""IPTV Manager Integration module"""
from datetime import datetime
import json
import socket

import xbmc

from .utils import log

class IPTVManager:
    """IPTV Manager interface"""

    def __init__(self, port, **kwargs):
        """Initialize IPTV Manager object"""
        self.port = port
        self.fetch_channels = kwargs.get('channels_loader')
        self.fetch_programs = kwargs.get('programs_loader')

    def via_socket(func): # pylint: disable=no-self-argument
        """Send the output of the wrapped function to socket"""

        def send(self):
            """Decorator to send over a socket"""
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', self.port))
            try:
                sock.sendall(json.dumps(func(self)).encode()) # pylint: disable=not-callable
            finally:
                sock.close()

        return send

    @via_socket
    def send_channels(self):
        """Return JSON-STREAMS formatted python datastructure to IPTV Manager"""
        channels = self.fetch_channels()
        streams = []

        for channel in channels:
            streams.append({
                'id': channel['id'],
                'name': channel['name'],
                'preset': channel['zappingNumber'],
                'logo': channel['logos']['square'],
                'stream': 'plugin://plugin.video.orange.fr/channel/{id}'.format(id=channel['id'])
            })

        return { 'version': 1, 'streams': streams }

    @via_socket
    def send_epg(self):
        """Return JSON-EPG formatted python data structure to IPTV Manager"""
        programs = self.fetch_programs()
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

        return { 'version': 1, 'epg': epg }
