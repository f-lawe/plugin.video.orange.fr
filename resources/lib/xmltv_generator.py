# -*- coding: utf-8 -*-
from xml.dom import minidom
from datetime import datetime

from orange import get_channels, get_programs

class XMLTVGenerator:
    filepath = '../orange-fr.xml'

    def __init__(self):
        self.document = minidom.Document()
        self.tv_element = self.document.createElement('tv')
        self.document.appendChild(self.tv_element)

    def append_channels(self, channels):
        for channel in channels:
            channel_element = self.document.createElement('channel')
            channel_element.setAttribute('id', 'C{}.api.telerama.fr'.format(channel['id']))

            display_name_element = self.document.createElement('display-name')
            display_name_element.appendChild(self.document.createTextNode(channel['name']))
            channel_element.appendChild(display_name_element)

            icon_element = self.document.createElement('icon')
            icon_element.setAttribute('src', channel['logos']['square'])
            channel_element.appendChild(icon_element)

            self.tv_element.appendChild(channel_element)

    def append_programs(self, programs):
        for program in programs:
            start = datetime.fromtimestamp(program['diffusionDate']).astimezone()
            end = datetime.fromtimestamp(program['diffusionDate'] + program['duration']).astimezone()
            
            program_element = self.document.createElement('programme')
            program_element.setAttribute('channel', 'C{}.api.telerama.fr'.format(program['channelId']))
            program_element.setAttribute('start', start.strftime('%Y%m%d%H%M%S %z'))
            program_element.setAttribute('end', end.strftime('%Y%m%d%H%M%S %z'))
            
            title_element = self.document.createElement('title')
            title_element.appendChild(self.document.createTextNode(program['title']))
            program_element.appendChild(title_element)

            desc_element = self.document.createElement('desc')
            desc_element.setAttribute('lang', 'fr')
            desc_element.appendChild(self.document.createTextNode(program['synopsis']))
            program_element.appendChild(desc_element)

            category_element = self.document.createElement('category')
            category_element.setAttribute('lang', 'fr')
            category_element.appendChild(self.document.createTextNode(str(program['genre'])))
            program_element.appendChild(category_element)

            length_element = self.document.createElement('length')
            length_element.setAttribute('unit', 'seconds')
            length_element.appendChild(self.document.createTextNode(str(program['duration'])))
            program_element.appendChild(length_element)

            if isinstance(program['covers'], list):
                for cover in program['covers']:
                    if cover['format'] == 'RATIO_16_9':
                        icon_element = self.document.createElement('icon')
                        icon_element.setAttribute('src', program['covers'][0]['url'])
                        program_element.appendChild(icon_element)

            self.tv_element.appendChild(program_element)

    def write(self):
        file = open(self.filepath, "wb")
        file.write(self.document.toprettyxml().encode('utf-8'))
        file.close()

def main():
    generator = XMLTVGenerator()
    generator.append_channels(get_channels())
    generator.append_programs(get_programs('today'))
    generator.write()

if __name__ == '__main__':
    main()