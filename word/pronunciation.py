# -*- coding: utf-8 -*-

import unicodedata
import urllib
import wx
import pygame
import os.path
from pydub import AudioSegment
GG_SEARCH_URL = "https://ssl.gstatic.com/dictionary/static/sounds/de/0/"
DICT_URL = "http://www.oxforddictionaries.com/definition/english/"
# GG_TRANSLATE_URL = "http://translate.google.com/translate_tts?tl=en&q="
MP3_EXTENSION = ".mp3"
OGG_EXTENSION = ".ogg"
AUDIO_DIR = "tmp/"


class Audio(object):
    """
    A class to get audio file (mp3, ogg ...) from internet and process it
    Code for playing sound file using pygame based on: https://gist.github.com/juehan/1869090

    """
    def __init__(self, audio_url, mp3_path, ogg_path):
        self.audio_url = audio_url
        self.mp3_path = mp3_path
        self.ogg_path = ogg_path

    def save_mp3_file(self):
        """
        Save pronunciation file of a word from internet to local.
        This audio file is taken from google search with key words:
        define word or word definition
        :return:
        """
        try:
            if not os.path.exists(self.ogg_path):
                urllib.urlretrieve(self.audio_url, self.mp3_path)
        except:
            print "Can not connect to audio server."

    def delete_mp3_file(self):
        """
        Delete unnecessary mp3 pronunciation file.
        :return:
        """
        if os.path.exists(self.mp3_path):
            os.remove(self.mp3_path)

    def convert_mp3_to_ogg(self):
        """
        Convert mp3 file to ogg file for cross-platform.
        The support of mp3 file in pygame is limited on Linux.
        :return:
        """
        try:
            if os.path.exists(self.mp3_path):
                mp3_file = AudioSegment.from_mp3(self.mp3_path)
                mp3_file.export(self.ogg_path, format='ogg')
        except:
            msg_dlg = wx.MessageDialog(None, 'Can not find the audio file on the server.', 'Sim',
                                       style=wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()

    def play(self):
        """
        Play pronunciation file using audio module.
        :return:
        """
        try:
            if os.path.exists(unicodedata.normalize('NFKD', self.ogg_path).encode('ascii', 'ignore')):
                pygame.init()
                clock = pygame.time.Clock()
                pygame.mixer.music.load(unicode(self.ogg_path))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    clock.tick(1000)
        except:
            print "Can not play audio file"
            raise

    def get_mixer_args(self):
        """
        Get arguments for audio module in pygame
        :return:
        """
        pygame.mixer.init()
        freq, size, chan = pygame.mixer.get_init()
        return freq, size, chan

    def init_mixer(self):
        """
        Initialize parameters for audio module in pygame
        :return:
        """
        try:
            buffer_size = 3072
            freq, size, chan = self.get_mixer_args()
            pygame.mixer.init(freq, size, chan, buffer_size)
        except:
            print "Can not initialize parameters for audio module."
