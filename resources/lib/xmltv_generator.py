# -*- coding: utf-8 -*-
'''Generate XMLTV file based on the information provided by Orange'''
from xml.dom import minidom
from datetime import datetime

from orange import get_channels, get_programs

class XMLTVGenerator:
    '''This class provides tools to generate an XMLTV file based on the given channel and program information'''

    def __init__(self, filepath):
        self.filepath = filepath
        implementation = minidom.getDOMImplementation('')
        doctype = implementation.createDocumentType('tv', None, 'xmltv.dtd')
        self.document = implementation.createDocument(None, 'tv', doctype)
        self.document.documentElement.setAttribute('source-info-url', 'https://rp-live.orange.fr')
        self.document.documentElement.setAttribute('source-data-url', 'https://rp-live.orange.fr')

    def append_channels(self, channels):
        '''Add channels to the XML document'''
        for channel in channels:
            channel_element = self.document.createElement('channel')
            channel_element.setAttribute('id', 'C{}.api.telerama.fr'.format(channel['id']))

            display_name_element = self.document.createElement('display-name')
            display_name_element.appendChild(self.document.createTextNode(channel['name']))
            channel_element.appendChild(display_name_element)

            icon_element = self.document.createElement('icon')
            icon_element.setAttribute('src', channel['logos']['square'])
            channel_element.appendChild(icon_element)

            self.document.documentElement.appendChild(channel_element)

    def append_programs(self, programs):
        '''Add programs to the XML document'''
        for program in programs:
            start = datetime.fromtimestamp(program['diffusionDate']).astimezone()
            end = datetime.fromtimestamp(program['diffusionDate'] + program['duration']).astimezone()

            program_element = self.document.createElement('programme')
            program_element.setAttribute('start', start.strftime('%Y%m%d%H%M%S %z'))
            program_element.setAttribute('end', end.strftime('%Y%m%d%H%M%S %z'))
            program_element.setAttribute('channel', 'C{}.api.telerama.fr'.format(program['channelId']))

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

            self.document.documentElement.appendChild(program_element)

    def write(self):
        '''Write the loaded channels and programs into XMLTV file'''
        file = open(self.filepath, "wb")
        file.write(self.document.toprettyxml(indent="  ", encoding='utf-8'))
        file.close()

def main():
    '''Script entry point'''
    generator = XMLTVGenerator(filepath='../data/orange-fr.xml')
    generator.append_channels(get_channels())
    generator.append_programs(get_programs('today'))
    generator.write()

if __name__ == '__main__':
    main()
