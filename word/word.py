__author__ = 'User'
import urllib2
from definition import DefParser
from pronunciation import Audio, AUDIO_DIR, DICT_URL, MP3_EXTENSION, OGG_EXTENSION, GG_SEARCH_URL


class Word(object):
    def __init__(self, value):
        self.def_url = DICT_URL + value
        self.parser = DefParser()
        self.audio = Audio(audio_url=GG_SEARCH_URL + value + MP3_EXTENSION,
                           mp3_path=AUDIO_DIR + value + MP3_EXTENSION,
                           ogg_path=AUDIO_DIR + value + OGG_EXTENSION)

    def get_definition(self):
        response = urllib2.urlopen(self.def_url)
        self.parser.feed(response.read())
        response.close()
        return self.parser.data

    def show_definition(self):
        print self.parser.data

    def get_pronunciation(self):
        self.audio.save_file()
        self.audio.convert_mp3_to_ogg()
        self.audio.delete_mp3_file()

    def pronounce(self):
        self.audio.init_mixer()
        self.audio.play()