# -*- coding: utf-8 -*-
"""IPTV Manager Integration module"""
import json
import socket

from lib.providers import ProviderInterface

class IPTVManager:
    """IPTV Manager interface"""

    def __init__(self, port: int, provider: ProviderInterface):
        """Initialize IPTV Manager object"""
        self.port = port
        self.provider = provider

    # pylint: disable=no-self-argument
    def via_socket(func):
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
    def send_channels(self) -> dict:
        """Return JSON-STREAMS formatted python datastructure to IPTV Manager"""
        return { 'version': 1, 'streams': self.provider.get_streams() }

    @via_socket
    def send_epg(self) -> dict:
        """Return JSON-EPG formatted python data structure to IPTV Manager"""
        return { 'version': 1, 'epg': self.provider.get_epg(days=6) }
