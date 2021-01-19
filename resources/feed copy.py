import url_quick
import xbmcaddon
import xbmcgui
from codequick import Resolver, Listitem

PROGRAMS_URL = 'https://rp-live-pc.woopic.com/live-webapp/v3/applications/PC/programs?groupBy=channel&period=current&epgIds=all&mco=OFR'
 
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')

def get_programs():
    programs_json = urlquick.get(
        PROGRAMS_URL,
        headers={ 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'},
        max_age=-1
    )

    programs = json.loads(programs_json.text)
    return programs

@Resolver.register
def get_feed_url(plugin, id, **kwargs):
    # programs = get_programs()
    # xbmcgui.Dialog().ok(addonname, "IN GET FEED FUNCTION: {}".format(id))

    item = Listitem()
    item.path = "https://cdn.ott-na-live-rti.cdnfr.orange.fr/Iq6ByE0sV6TAjEy5Zic_s4NNiNA/1-64/1/1610927114/OTV-14856e4a-e50f-4cd6-a9b4-324da5ab18d2/bpk-tv/livetv_france2_ctv/DASH-CE/index.mpd?bpk-service=Live&device=pc&delay=0&minrate=416000&maxrate=3200000&audio=fra&subtitle=none"
    item.property['inputstream'] = 'C:/Users/Kodi/AppData/Roaming/Kodi/addons/inputstream.adaptive'
    item.property['inputstream.adaptive.manifest_type'] = 'mpd'
    item.property['inputstream.adaptive.license_type'] = 'com.widevine.alpha'
    item.property['inputstream.adaptive.license_key'] = 'zcLu9HEewivHf6/jb8FdQmptwdGt5K4LTBa8dJ24kFI56/LqIT6T1UKV+2RHvEEE5lIzbODbzQzqcj7r82UL5EzRpMs1jfLz8XdnI/eMR1ra/9T/BsO5gVEs17loZiiwrj7+Qqp1WkigMLOovzyguN/IbU3wjOspBH6tyPpMIzPEQxn63hfTYuolLus+uWtOKIRqagVj4B00AdYHgNezh5UXyTSUhbmNdSklenZESUM='

    return False
    # return item