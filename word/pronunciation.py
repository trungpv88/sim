__author__ = 'User'
import urllib
import pygame
import os.path
GG_SEARCH_URL = "https://ssl.gstatic.com/dictionary/static/sounds/de/0/"
# GG_TRANSLATE_URL = "http://translate.google.com/translate_tts?tl=en&q="
AUDIO_DIR = "audio/"


class Audio(object):
    """
    Code for playing mp3 file using pygame based on: https://gist.github.com/juehan/1869090

    """
    def __init__(self, mp3_file):
        self.file = mp3_file

    def save_file(self):
        file_url = GG_SEARCH_URL + self.file
        file_path = AUDIO_DIR + self.file
        if not os.path.exists(file_path):
            urllib.urlretrieve(file_url, file_path)

    def play_mp3(self, file_path):
        pygame.init()
        pygame.mixer.init()
        clock = pygame.time.Clock()
        pygame.mixer.music.load(file_path)
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
