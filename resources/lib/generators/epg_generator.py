# -*- coding: utf-8 -*-
"""Generate XMLTV file based on the provided channels and programs"""
from datetime import datetime
from xml.dom import minidom

from lib.providers import ProviderInterface

class EPGGenerator:
    """This class provides tools to generate an XMLTV file based on the given channel and program information"""

    def __init__(self, provider: ProviderInterface):
        implementation = minidom.getDOMImplementation('')
        doctype = implementation.createDocumentType('tv', None, 'xmltv.dtd')
        self.document = implementation.createDocument(None, 'tv', doctype)
        self.document.documentElement.setAttribute('source-info-url', 'https://mediation-tv.orange.fr')
        self.document.documentElement.setAttribute('source-data-url', 'https://mediation-tv.orange.fr')
        self.provider = provider
        self._load_streams()
        self._load_epg()

    def _load_streams(self):
        """Add channels to the XML document"""
        for stream in self.provider.get_streams():
            channel_element = self.document.createElement('channel')
            channel_element.setAttribute('id', stream['id'])

            display_name_element = self.document.createElement('display-name')
            display_name_element.appendChild(self.document.createTextNode(stream['name']))
            channel_element.appendChild(display_name_element)

            icon_element = self.document.createElement('icon')
            icon_element.setAttribute('src', stream['logo'])
            channel_element.appendChild(icon_element)

            self.document.documentElement.appendChild(channel_element)

    def _load_epg(self):
        """Add programs to the XML document"""
        for channel_id, programs in self.provider.get_epg().items():
            for program in programs:
                program_element = self.document.createElement('programme')
                program_element.setAttribute(
                    'start',
                    datetime.fromisoformat(program['start']).strftime('%Y%m%d%H%M%S %z')
                )
                program_element.setAttribute(
                    'stop',
                    datetime.fromisoformat(program['stop']).strftime('%Y%m%d%H%M%S %z')
                )
                program_element.setAttribute('channel', channel_id)

                title_element = self.document.createElement('title')
                title_element.appendChild(self.document.createTextNode(program['title']))
                program_element.appendChild(title_element)

                if program['subtitle'] is not None:
                    sub_title_element = self.document.createElement('sub-title')
                    sub_title_element.appendChild(self.document.createTextNode(program['subtitle']))
                    program_element.appendChild(sub_title_element)

                desc_element = self.document.createElement('desc')
                desc_element.setAttribute('lang', 'fr')
                desc_element.appendChild(self.document.createTextNode(program['description']))
                program_element.appendChild(desc_element)

                category_element = self.document.createElement('category')
                category_element.appendChild(self.document.createTextNode(program['genre']))
                program_element.appendChild(category_element)

                icon_element = self.document.createElement('icon')
                icon_element.setAttribute('src', program['image'])
                program_element.appendChild(icon_element)

                if program['episode'] is not None:
                    episode_num_element = self.document.createElement('episode-num')
                    episode_num_element.setAttribute('system', 'onscreen')
                    episode_num_element.appendChild(self.document.createTextNode(program['episode']))
                    program_element.appendChild(episode_num_element)

                self.document.documentElement.appendChild(program_element)

    def write(self, filepath):
        """Write the loaded channels and programs into XMLTV file"""
        with open(filepath, 'wb') as file:
            file.write(self.document.toprettyxml(indent='  ', encoding='utf-8'))
