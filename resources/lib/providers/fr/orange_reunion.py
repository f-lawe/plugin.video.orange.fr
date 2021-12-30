# -*- coding: utf-8 -*-
"""Orange Réunion"""
from lib.provider_templates import OrangeTemplate

class OrangeReunionProvider(OrangeTemplate):
    """Orange Réunion provider"""

    # pylint: disable=line-too-long
    def __init__(self) -> None:
        super().__init__(
            endpoint_stream_info = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/users/me/channels/{channel_id}/stream?terminalModel=WEB_PC',
            endpoint_streams = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/channels?mco=ORE',
            endpoint_epg = 'https://mediation-tv.orange.fr/all/live/v3/applications/PC/programs?period={period}&mco=ORE',
            groups = {
                'Généralistes': \
                    [20245, 21079, 1080, 70005, 192, 4, 80, 47, 20118, 78],
                'Divertissement': \
                    [30195, 1996, 531, 70216, 57, 70397, 70398, 70399],
                'Jeunesse': \
                    [30482],
                'Découverte': \
                    [111, 30445],
                'Jeunes': \
                    [30444, 20119, 21404, 21403, 563],
                'Musique': \
                    [20458, 21399, 70150, 605],
                'Sport': \
                    [64, 2837],
                'Jeux': \
                    [1061],
                'Société': \
                    [1072],
                'Information française': \
                    [234, 481, 226, 112, 2111, 529, 1073],
                'Information internationale': \
                    [671, 53, 51, 410, 19, 525, 70239, 70240, 70241, 70242, 781, 830, 70246, 70503]
            }
        )
