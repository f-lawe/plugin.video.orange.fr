# -*- coding: utf-8 -*-
from orange import get_channels

class M3UGenerator:
    filepath = '../data/orange-fr.m3u'

    def __init__(self):
        self.entries = ['#EXTM3U tvg-shift=0']

    def _load_channels(self, channels):
        channels.sort(key=lambda x: x.get('zappingNumber'))

        current_zapping_number = 1
        loaded_channels = []

        for channel in channels:
            next_zapping_number = channel['zappingNumber']

            for zapping_number in range(current_zapping_number, next_zapping_number)[:-1]:
                loaded_channels.append(None)

            loaded_channels.append(channel)
            current_zapping_number = next_zapping_number

        return loaded_channels

    def _channel_entry(self, channel):
        return """
##\t{name}
#EXTINF:-1 tvg-name="{zapping_number}" tvg-id="C{id}.api.telerama.fr" tvg-logo="{logo}" group-title="channels",{name}
plugin://plugin.video.orange.fr/channel/{id}""" \
        .format(
            id=channel['id'],
            name=channel['name'],
            logo=channel['logos']['square'],
            zapping_number=channel['zappingNumber'])

    def _empty_entry(self, zapping_number):
        return """
##\tPLACEHOLDER
#EXTINF:-1 tvg-name="{zapping_number}" tvg-id="" tvg-logo="" group-title="-",
http://null""" \
        .format(zapping_number=zapping_number)

    def append_channels(self, channels):
        channels = self._load_channels(channels)

        for zapping_number, channel in enumerate(channels):
            self.entries.append(self._empty_entry(zapping_number) if channel == None else self._channel_entry(channel))

    def write(self):
        file = open(self.filepath, 'wb')
        file.writelines('{}\n'.format(entry).encode('utf-8') for entry in self.entries)
        file.close()

def main():
    generator = M3UGenerator()
    generator.append_channels(get_channels())
    generator.write()

if __name__ == '__main__':
    main()