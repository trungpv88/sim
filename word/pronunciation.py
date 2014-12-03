__author__ = 'User'
import urllib
import pygame
import os.path
from pydub import AudioSegment
GG_SEARCH_URL = "https://ssl.gstatic.com/dictionary/static/sounds/de/0/"
DICT_URL = "http://www.oxforddictionaries.com/definition/english/"
# GG_TRANSLATE_URL = "http://translate.google.com/translate_tts?tl=en&q="
MP3_EXTENSION = ".mp3"
OGG_EXTENSION = ".ogg"
AUDIO_DIR = "audio/"


class Audio(object):
    """
    Code for playing sound file using pygame based on: https://gist.github.com/juehan/1869090

    """
    def __init__(self, audio_url, mp3_path, ogg_path):
        self.audio_url = audio_url
        self.mp3_path = mp3_path
        self.ogg_path = ogg_path

    def save_file(self):
        if not os.path.exists(self.ogg_path):
            urllib.urlretrieve(self.audio_url, self.mp3_path)

    def delete_mp3_file(self):
        if os.path.exists(self.mp3_path):
            os.remove(self.mp3_path)

    def convert_mp3_to_ogg(self):
        if os.path.exists(self.mp3_path):
            mp3_file = AudioSegment.from_mp3(self.mp3_path)
            mp3_file.export(self.ogg_path, format='ogg')

    def play(self):
        pygame.init()
        clock = pygame.time.Clock()
        pygame.mixer.music.load(self.ogg_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            clock.tick(1000)

    def get_mixer_args(self):
        pygame.mixer.init()
        freq, size, chan = pygame.mixer.get_init()
        return freq, size, chan

    def init_mixer(self):
        buffer_size = 3072
        freq, size, chan = self.get_mixer_args()
        pygame.mixer.init(freq, size, chan, buffer_size)
