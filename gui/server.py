#----------------------------------------------------------------------------
# Change log:
# 2014/12/24  - Version 1.0
# 2015/01/16  - Version 1.1
#----------------------------------------------------------------------------
# Goal:
# - Show information about definition, pronunciation and image servers

import wx
from word.pronunciation import DICT_URL, GG_SEARCH_URL
from word.word_view import GOOGLE_IMAGE_SERVER
from sound import play_closing_sound


class ServerDialog(wx.Dialog):
    """
    A class to view definition/audio/check configuration server
    """
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title,  size=(600, 150))
        self.dialog_design()
        self.ShowModal()
        play_closing_sound()

    def dialog_design(self):
        """
        Design interface
        :return:
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        server_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Server URLs'), orient=wx.VERTICAL)
        close_btn = wx.Button(self, -1, 'OK', size=(80, 25))
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        word_definition_server = self.create_server_config("Definition server: ", DICT_URL)
        word_pronunciation_server = self.create_server_config("Pronunciation server: ", GG_SEARCH_URL)
        description_image_server = self.create_server_config("Image server: ", GOOGLE_IMAGE_SERVER)
        server_sizer.Add(word_definition_server, 1, wx.EXPAND | wx.BOTTOM, 10)
        server_sizer.Add(word_pronunciation_server, 1, wx.EXPAND | wx.BOTTOM, 10)
        server_sizer.Add(description_image_server, 1, wx.EXPAND, 0)
        main_sizer.Add(server_sizer, 1, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(close_btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        self.SetSizer(main_sizer)

    def create_server_config(self, name, text):
        """
        Create labels to show the number of learnt words from start date to end date
        :param name:
        :param text:
        :return:
        """
        server_config_sizer = wx.GridSizer(1, 3)
        server_label = wx.StaticText(self, -1, name, size=(150, 20))
        server_text = wx.StaticText(self, -1, text)
        server_config_sizer.Add(server_label, wx.ALIGN_CENTER_VERTICAL)
        server_config_sizer.Add(server_text, wx.ALIGN_CENTER_VERTICAL)
        return server_config_sizer

    def on_close(self, e):
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        self.Destroy()