# -*- coding: utf-8 -*-
"""Orange Caraïbe"""
from lib.provider_templates import OrangeTemplate

class OrangeCaraibeProvider(OrangeTemplate):
    """Orange Caraïbe provider"""

    # pylint: disable=line-too-long
    def __init__(self) -> None:
        super().__init__(
            endpoint_stream_info = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/users/me/channels/{channel_id}/stream?terminalModel=WEB_PC',
            endpoint_streams = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/channels?mco=OCA',
            endpoint_programs = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/programs?period={period}&mco=OCA',
            groups = {}
        )
