import wx
import wx.calendar
import wx.lib.calendar
import wx.gizmos
from test import TestDialog
from cal import CalendarDialog
from phrase import PhraseDialog
from server import ServerDialog


class ToolBar(object):
    """
    A class to design some buttons on tool bar
    """
    def __init__(self, parent):
        self.parent = parent
        self.choose_language = 'English'

    def change_language(self, e):
        """
        Event raises when change language button is clicked
        """
        self.choose_language = wx.SingleChoiceDialog(None, 'Choose your learning language:', 'Language',
                                                ['English', 'French'])
        if self.choose_language.ShowModal() == wx.ID_OK:
            print self.choose_language.GetStringSelection()

    def track_learning(self, e):
        """
        Event raises when learning tracking button is clicked
        """
        CalendarDialog(self.parent, 'Learning Tracking')

    def test_vocabulary(self, e):
        """
        Event raises when test button is clicked
        """
        TestDialog(self.parent, 'Test Vocabulary')

    def view_phrases(self, e):
        """
        Event raises when when view phrases button is clicked
        """
        PhraseDialog(self.parent, 'Ordinary Phrases')

    def configure_server(self, e):
        """
        Event raises when server configuration button is clicked
        """
        ServerDialog(self.parent, 'View Configuration Servers')