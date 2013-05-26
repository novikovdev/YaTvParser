__all__ = [
    'defaultTimeout',
    'ProgramChannelParser', 'ChannelsParser'
]

from urllib import request
from bs4 import BeautifulSoup
from datetime import datetime
from collections import namedtuple

ObjChannel = namedtuple('Channel', 'name, uri, url, url_logo, regionId')
ObjProgram = namedtuple('Program', 'channel, time, name, category')
ObjCategory = namedtuple('Category', 'name, cls')

ya_categories = (
    ObjCategory('Other', ''),
    ObjCategory('Show', 'b-tv-event_theme_grey'),
    ObjCategory('Films', 'b-tv-event_genre_films'),
    ObjCategory('ForChildren', 'b-tv-event_genre_for-children'),
    ObjCategory('Serials', 'b-tv-event_genre_series'),
    ObjCategory('Sport', 'b-tv-event_genre_sport'),
)

defaultTimeout = 10
defaultEncoding = 'utf-8'
url_yatv = "http://tv.yandex.ru"

joinYa = lambda *urls: '/'.join([url_yatv, ('/'.join(urls))])
urlopen = lambda url: request.urlopen(url, timeout=defaultTimeout)

class ProgramChannelParser(object):

    def __init__(self, channel, verbose=False):
        assert isinstance(channel, ObjChannel)
        self._verbose = (verbose == True)
        self.channel = channel
        self.url_obj = urlopen(channel.url)
        self.soup = BeautifulSoup(self.url_obj, from_encoding=defaultEncoding)

    def verbose(self, s):
        if self._verbose:
            now = datetime.now().strftime('%d.%m.%Y %H:%M:%S,%f')
            print('[{}]: {}'.format(now, s))

    def getProgram(self):
        result = []
        schedule = self.soup.find('div', {'class': 'b-tv-channel-content__schedule'})
        fcls = 'b-tv-event b-tv-event_size_l b-tv-event_show-favorites_yes{} i-bem'
        for category in ya_categories:
            assert isinstance(category, ObjCategory)
            fcls_arg = (" {}".format(category.cls)) if len(category.cls) > 0 else ''
            events = schedule.findAll('div', {'class': fcls.format(fcls_arg)})
            for event in events:
                time = event.find('span', {'class': 'b-tv-event__time'})
                data = event.find('span', {'class': 'b-tv-event-title b-tv-event__title'})
                name = data.find('a', {'class': 'b-link b-link_type_program b-link_region_yes'})
                program_obj = ObjProgram(channel=self.channel, time=time.string,
                                         name=name.string, category=category.name)
                self.verbose(program_obj)
                result.append(program_obj)
        return result

class ChannelsParser(object):

    def __init__(self, region_id, verbose=False):
        self._verbose = (verbose == True)
        self.url_channels = joinYa(region_id, 'channels')
        self.region_id = region_id
        self.init_soup()

    def verbose(self, s):
        if self._verbose:
            now = datetime.now().strftime('%d.%m.%Y %H:%M:%S,%f')
            print('[{}]: {}'.format(now, s))

    def init_soup(self):
        self.url_obj = urlopen(self.url_channels)
        self.soup = BeautifulSoup(self.url_obj, from_encoding=defaultEncoding)

    def getCurrentCity(self):
        result = self.soup.find('span', {'class': 'b-tv-region-selector__text'})
        result = result.string
        self.verbose('City = "{}"'.format(result))
        return result

    def getAllChannelsList(self):
        result = []
        channels_obj = self.soup.findAll('div', {'class': 'b-tv-channels-list__item'})
        for channel in channels_obj:
            field = channel.find('a', {'class': 'b-link b-link_type_channel b-link_region_yes'})
            name = field.renderContents().decode('utf-8').rsplit('>', 1)[-1].strip()
            uri = field['href'].strip('/')
            url = joinYa(uri)
            channel_obj = ObjChannel(name=name, regionId=self.region_id,
                                     uri=uri, url=url, url_logo=None)
            obj = ProgramChannelParser(channel_obj, verbose=self._verbose)
            self.verbose(channel_obj)
            result.append(obj)
        return result
