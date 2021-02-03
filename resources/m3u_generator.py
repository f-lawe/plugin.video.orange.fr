from urllib import request
from html.parser import HTMLParser

ORANGE_HOME_URL = 'https://chaines-tv.orange.fr/'
USER_AGENT      = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'  
HOST            = 'chaines-tv.orange.fr'

CHANNEL_DIV_CLASSNAME = 'list-item-wrapper wptv-xsmall-1 wptv-medium-3 wptv-large-4'
CHANNEL_IMG_CLASSNAME = 'poster-logo bottom-left'

M3U_FILEPATH = './orange-fr.m3u'
M3U_INFO_LINE = '#EXTINF:-1 tvg-id="C%s.api.telerama.fr" tvg-logo="%s",%s'
M3U_URL_LINE = 'plugin://script.orange.fr/?channel_id=%s'

CHANNELS = {}

class Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.channel_id = False

    def handle_starttag(self, tag, attrs):
        if(tag == 'div'):
            new_attrs = parse_attrs(attrs)

            if(new_attrs.get('class') == CHANNEL_DIV_CLASSNAME):
                self.channel_id = new_attrs['id']

        if(tag == 'img'):
            new_attrs = parse_attrs(attrs)

            if(new_attrs.get('class') == CHANNEL_IMG_CLASSNAME):
                CHANNELS[self.channel_id] = {
                    'img_url': new_attrs['src'],
                    'name': new_attrs['alt']
                }

def parse_attrs(attrs):
    new_attrs = {}

    for attr in attrs:
        new_attrs[attr[0]] = attr[1]
    
    return new_attrs

def get_channels_info():
    req = request.Request(ORANGE_HOME_URL, headers={
        'User-Agent': USER_AGENT,
        'Host': HOST
    })

    res = request.urlopen(req).read().decode('utf-8')

    parser = Parser()
    parser.feed(res)

def write_m3u():
    file = open(M3U_FILEPATH, "w")
    file.write('#EXTM3U tvg-shift=0' + '\n\n')

    for id, channel in CHANNELS.items():
        file.write('##\t' + channel['name'] + '\n')
        file.write('##\t' + channel['name'] + '\n')
        file.write(M3U_INFO_LINE % (id, channel['img_url'], channel['name']) + '\n')
        file.write(M3U_URL_LINE % (id) + '\n')
        file.write('\n')

def generate_m3u():
    get_channels_info()
    write_m3u()

def main():
    generate_m3u()

if __name__ == '__main__':
    main()