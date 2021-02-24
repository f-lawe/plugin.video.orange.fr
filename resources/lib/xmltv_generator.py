# -*- coding: utf-8 -*-
'''Generate XMLTV file based on the information provided by Orange'''
from datetime import datetime
from xml.dom import minidom

class XMLTVGenerator:
    '''This class provides tools to generate an XMLTV file based on the given channel and program information'''

    def __init__(self):
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
            program_element.setAttribute('stop', end.strftime('%Y%m%d%H%M%S %z'))
            program_element.setAttribute('channel', 'C{}.api.telerama.fr'.format(program['channelId']))

            if program['programType'] == 'EPISODE':
                title_element = self.document.createElement('title')
                title_element.appendChild(self.document.createTextNode(program['season']['serie']['title']))
                program_element.appendChild(title_element)

                sub_title_element = self.document.createElement('sub-title')
                sub_title_element.appendChild(self.document.createTextNode(program['title']))
                program_element.appendChild(sub_title_element)

                episode_num = '{}.{}.'.format(program['season']['number'] - 1, program['episodeNumber'] - 1)
                episode_num_element = self.document.createElement('episode-num')
                episode_num_element.setAttribute('system', 'xmltv_ns')
                episode_num_element.appendChild(self.document.createTextNode(episode_num))
                program_element.appendChild(episode_num_element)
            else:
                title_element = self.document.createElement('title')
                title_element.appendChild(self.document.createTextNode(program['title']))
                program_element.appendChild(title_element)

            desc_element = self.document.createElement('desc')
            desc_element.setAttribute('lang', 'fr')
            desc_element.appendChild(self.document.createTextNode(program['synopsis']))
            program_element.appendChild(desc_element)

            category = program['genre'] if program['genreDetailed'] is None else program['genreDetailed']
            category_element = self.document.createElement('category')
            category_element.setAttribute('lang', 'fr')
            category_element.appendChild(self.document.createTextNode(category))
            program_element.appendChild(category_element)

            length_element = self.document.createElement('length')
            length_element.setAttribute('unit', 'minutes')
            length_element.appendChild(self.document.createTextNode(str(int(program['duration'] / 60))))
            program_element.appendChild(length_element)

            if isinstance(program['covers'], list):
                for cover in program['covers']:
                    if cover['format'] == 'RATIO_16_9':
                        icon_element = self.document.createElement('icon')
                        icon_element.setAttribute('src', program['covers'][0]['url'])
                        program_element.appendChild(icon_element)

            self.document.documentElement.appendChild(program_element)

    def write(self, filepath):
        '''Write the loaded channels and programs into XMLTV file'''
        file = open(filepath, "wb")
        file.write(self.document.toprettyxml(indent="  ", encoding='utf-8'))
        file.close()
