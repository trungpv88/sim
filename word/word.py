#----------------------------------------------------------------------------
# Change log:
# 2014/12/24  - Version 1.0
# 2015/01/16  - Version 1.1
#----------------------------------------------------------------------------
# Goal:
# - Get word pronunciation and definition

import urllib2
import wx
import os.path
from definition import DefParser
from pronunciation import Audio, AUDIO_DIR, DICT_URL, MP3_EXTENSION, OGG_EXTENSION, GG_SEARCH_URL
from gui.utils import convert_ogg_to_string


class Word(object):
    """
    A class to process a request word (definition and pronunciation)
    """
    def __init__(self, value):
        self.word = value
        self.def_url = DICT_URL + value
        self.parser = DefParser()
        self.audio = Audio(audio_url=GG_SEARCH_URL + value + MP3_EXTENSION,
                           mp3_path=AUDIO_DIR + value + MP3_EXTENSION,
                           ogg_path=AUDIO_DIR + value + OGG_EXTENSION)

    def get_definition(self):
        """
        Get the word definition from html source page
        :return: word definition
        """
        try:
            response = urllib2.urlopen(self.def_url)
            self.parser.feed(response.read())
            response.close()
        except IOError:
            msg_dlg = wx.MessageDialog(None, "Can not find the definition of '" + self.word + "' on the server.", 'Sim',
                                       style=wx.OK | wx.ICON_EXCLAMATION)
            msg_dlg.ShowModal()
            return ''
        return self.parser.data

    def show_definition(self):
        """
        Print the word definition
        :return:
        """
        print self.parser.data

    def get_pronunciation(self):
        """
        Get the word pronunciation
        :return:
        """
        self.audio.save_mp3_file()
        self.audio.convert_mp3_to_ogg()
        path = AUDIO_DIR + self.word + OGG_EXTENSION
        self.audio.delete_mp3_file()
        if os.path.exists(path):
            return convert_ogg_to_string(path)
        else:
            return ''

    def pronounce(self):
        """
        Pronounce the word
        :return:
        """
        self.audio.init_mixer()
        self.audio.play()