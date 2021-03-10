# -*- coding: utf-8 -*-
"""Generate playlist based on available channels"""

class PlaylistGenerator:
    """This class provides tools to generate a playlist based on the given channel information"""

    def __init__(self):
        self.entries = ['#EXTM3U', '']

    # pylint: disable=line-too-long
    def append_streams(self, streams):
        """Append the provided streams to the current list"""

        stream_template = [
            '##\t{name}',
            '#EXTINF:-1 tvg-name="{name}" tvg-id="{id}" tvg-logo="{logo}" tvg-chno="{chno}" group-title="Orange TV France",{name}',
            '{stream}'
        ]

        self.entries = ['#EXTM3U tvg-shift=0']
        for stream in streams:
            self.entries.append(stream_template[0].format(name=stream['name']))
            self.entries.append(stream_template[1].format(
                name=stream['name'],
                id=stream['id'],
                logo=stream['logo'],
                chno=stream['preset']
            ))
            self.entries.append(stream_template[2].format(stream=stream['stream']))
            self.entries.append('')

    def write(self, filepath):
        """Write the loaded channels into M3U8 file"""
        file = open(filepath, 'wb')
        file.writelines('{}\n'.format(entry).encode('utf-8') for entry in self.entries)
        file.close()
