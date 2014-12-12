import urllib2
import wx
from definition import DefParser
from pronunciation import Audio, AUDIO_DIR, DICT_URL, MP3_EXTENSION, OGG_EXTENSION, GG_SEARCH_URL


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
            return ""
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
        self.audio.delete_mp3_file()

    def pronounce(self):
        """
        Pronounce the word
        :return:
        """
        self.audio.init_mixer()
        self.audio.play()