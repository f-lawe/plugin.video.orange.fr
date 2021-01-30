import json, urllib2, urlparse, sys
import xbmc, xbmcaddon, xbmcgui, xbmcplugin

ADDON_NAME          = xbmcaddon.Addon().getAddonInfo('name')
USER_AGENT          = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'
HOST                = 'chaines-tv.orange.fr'
CHANNEL_INFO_URL    = 'https://chaines-tv.orange.fr/live-webapp/v3/applications/PC/users/me/channels/{}/stream?terminalModel=WEB_PC&terminalId=Windows10-x64-Firefox-GVASQGFQ6QJNUW5OJJICWHPI7766H7VWLMPIOZYKAUS6DCM2LMOA'

def log(msg, level):
    xbmc.log('{}: {}'.format(ADDON_NAME, msg), level)

def get_channel_info(channel_id):
    request = urllib2.Request(CHANNEL_INFO_URL.format(channel_id), headers={
        'User-Agent': USER_AGENT,
        'Host': HOST
    })

    channel_info = urllib2.urlopen(request).read()
    channel_info = json.loads(channel_info)

    stream_info = {
        'path': channel_info.get('url'),
    }

    for system in channel_info.get('protectionData'):
        if system.get('keySystem') == 'com.widevine.alpha':
            stream_info['keySystem'] = system.get('keySystem')
            stream_info['drmToken'] = system.get('drmToken')
            stream_info['laUrl'] = system.get('laUrl')

    return stream_info

def get_channel_stream_item(channel_id):
    channel_info = get_channel_info(channel_id)

    license_server_url = channel_info['laUrl']
    headers = 'User-Agent={}&Host={}'.format(USER_AGENT, HOST)
    post_data = 'R{SSM}'
    response = 'B'

    license_key = '{}|{}|{}|{}'.format(license_server_url, headers, post_data, response)
    log(license_key, xbmc.LOGNOTICE)

    listitem = xbmcgui.ListItem(path=channel_info['path'])
    listitem.setMimeType('application/xml+dash')
    listitem.setContentLookup(False)
    listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
    listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
    listitem.setProperty('inputstream.adaptive.license_key', license_key)

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

def main():
    if(len(sys.argv) > 3):
        args = urlparse.parse_qs(sys.argv[2][1:])
        log('Loading channel {}'.format(args['channel_id'][0]), xbmc.LOGNOTICE)
        get_channel_stream_item(args['channel_id'][0])

if __name__ == '__main__':
    main()