__author__ = 'User'
import urllib2
from definition import DefParser
from pronunciation import Audio, AUDIO_DIR
DICT_URL = "http://www.oxforddictionaries.com/definition/english/"
FILE_EXTENSION = ".mp3"


class Word(object):
    def __init__(self, value):
        self.url = DICT_URL + value
        self.parser = DefParser()
        self.audio_file = value + FILE_EXTENSION
        self.audio = Audio(mp3_file=self.audio_file)

    def get_definition(self):
        response = urllib2.urlopen(self.url)
        self.parser.feed(response.read())
        response.close()
        return self.parser.data

    def show_definition(self):
        print self.parser.data

    def get_pronunciation(self):
        self.audio.save_file()

    def pronounce(self):
        self.audio.init_mixer()
        self.audio.play_mp3(AUDIO_DIR + self.audio_file)