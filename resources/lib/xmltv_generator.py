# -*- coding: utf-8 -*-
from xml.dom import minidom

from orange import get_channels, get_programs

class XMLTVGenerator:
    filepath = '../orange-fr.xml'

    def __init__(self):
        self.document = minidom.Document()
        self.tv_element = self.document.createElement('tv')
        self.document.appendChild(self.tv_element)

    def append_channels(self, channels):
        for channel in channels:
            display_name_element = self.document.createElement('display-name')
            display_name_element.appendChild(self.document.createTextNode(channel['name']))

            icon_element = self.document.createElement('icon')
            icon_element.setAttribute('src', channel['logos']['square'])

            channel_element = self.document.createElement('channel')
            channel_element.setAttribute('id', 'C{}.api.telerama.fr'.format(channel['id']))
            channel_element.appendChild(display_name_element)
            channel_element.appendChild(icon_element)
            self.tv_element.appendChild(channel_element)

    def append_programs(self, programs):
        for program in programs:
            title_element = self.document.createElement('title')
            title_element.appendChild(self.document.createTextNode(program['title']))

            desc_element = self.document.createElement('desc')
            desc_element.setAttribute('lang', 'fr')
            desc_element.appendChild(self.document.createTextNode(program['synopsis']))

            program_element = self.document.createElement('programme')
            program_element.setAttribute('channel', 'C{}.api.telerama.fr'.format(program['channelId']))
            program_element.appendChild(title_element)
            program_element.appendChild(desc_element)
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