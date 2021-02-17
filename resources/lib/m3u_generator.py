# -*- coding: utf-8 -*-
'''Generate M3U list based on available channels'''
from orange import get_channels # pylint: disable=import-error

class M3UGenerator:
    '''This class provides tools to generate a M3U list based on the given channel information'''

    def __init__(self, filepath):
        self.entries = ['#EXTM3U tvg-shift=0']
        self.filepath = filepath

    def _load_dummy_channels(self, channels):
        '''Add empty slots in order to keep channel zapping number in Kodi'''
        channels.sort(key=lambda x: x.get('zappingNumber'))

        current_zapping_number = 1
        loaded_channels = []

        for channel in channels:
            next_zapping_number = channel['zappingNumber']

            for _ in range(current_zapping_number, next_zapping_number)[:-1]:
                loaded_channels.append(None)

            loaded_channels.append(channel)
            current_zapping_number = next_zapping_number

        return loaded_channels

    def _channel_entry(self, channel):
        '''Regular channel template'''
        return '''
##\t{name}
#EXTINF:-1 tvg-name="{zapping_number}" tvg-id="C{id}.api.telerama.fr" tvg-logo="{logo}" group-title="channels",{name}
plugin://plugin.video.orange.fr/channel/{id}''' \
        .format(
            id=channel['id'],
            name=channel['name'],
            logo=channel['logos']['square'],
            zapping_number=channel['zappingNumber'])

    def _empty_entry(self, zapping_number):
        '''Dummy placeholder template'''
        return '''
##\tPLACEHOLDER
#EXTINF:-1 tvg-name="{zapping_number}" tvg-id="" tvg-logo="" group-title="-",
http://null''' \
        .format(zapping_number=zapping_number)

    def append_channels(self, channels):
        '''Append the provided channels to the current list'''
        channels = self._load_dummy_channels(channels)

        self.entries = ['#EXTM3U tvg-shift=0']
        for key, channel in enumerate(channels):
            self.entries.append(self._empty_entry(key + 1) if not channel else self._channel_entry(channel))

    def write(self):
        '''Write the loaded channels into M3U file'''
        file = open(self.filepath, 'wb')
        file.writelines('{}\n'.format(entry).encode('utf-8') for entry in self.entries)
        file.close()

def main():
    '''Script entry point: load channels into m3u list'''
    generator = M3UGenerator(filepath='../data/orange-fr.m3u')
    generator.append_channels(get_channels())
    generator.write()

if __name__ == '__main__':
    main()
