import json
import urlquick
import xbmcaddon
import xbmcgui
from codequick import Resolver, Listitem

PROGRAMS_URL = 'https://rp-live-pc.woopic.com/live-webapp/v3/applications/PC/programs?groupBy=channel&period=current&epgIds=all&mco=OFR'
CHANNEL_INFO_URL = 'https://chaines-tv.orange.fr/live-webapp/v3/applications/PC/users/me/channels/%s/stream?terminalModel=WEB_PC&terminalId=Windows10-x64-Firefox-GVASQGFQ6QJNUW5OJJICWHPI7766H7VWLMPIOZYKAUS6DCM2LMOA'
 
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')

def get_programs():
    programs_json = urlquick.get(
        PROGRAMS_URL,
        headers={ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'},
        max_age=-1
    )
    
    xbmcgui.Dialog().ok(addonname, programs_json.text)
    programs = json.loads(programs_json.text)
    return programs

def get_stream_info(id):
    channel_info_json = urlquick.get(
        CHANNEL_INFO_URL % id,
        headers={ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'},
        max_age=-1
    )
    
    channel_info = json.loads(channel_info_json.text)

    stream_info = {
        'path': channel_info.get('url'),
    }

    for system in channel_info.get('protectionData'):
        if system.get('keySystem') == 'com.widevine.alpha':
            stream_info['keySystem'] = system.get('keySystem')
            stream_info['drmToken'] = system.get('drmToken')
            stream_info['laUrl'] = system.get('laUrl')

    return stream_info
    

@Resolver.register
def get_feed_url(plugin, id, **kwargs):
    stream_info = get_stream_info(id)

    item = Listitem()
    item.path = stream_info.get('path')
    item.property['inputstream'] = 'C:/Users/Kodi/AppData/Roaming/Kodi/addons/inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = stream_info.get('keySystem')
    item.property['inputstream.adaptive.license_key'] = stream_info.get('laUrl')

    # return False
    return item