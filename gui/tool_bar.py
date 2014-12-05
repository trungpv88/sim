__author__ = 'User'
import wx
import wx.calendar


class ToolBar(object):
    def __init__(self, parent):
        self.parent = parent

    def change_language(self, e):
        choose_language = wx.SingleChoiceDialog(None, 'Choose your learning language:', 'Language',
                                                ['English', 'French'])
        if choose_language.ShowModal() == wx.ID_OK:
            print choose_language.GetStringSelection()

    def track_learning(self, e):
        wx.calendar.CalendarCtrl(self.parent, -1, wx.DateTime_Now(), pos=(25, 50),
                                 style=wx.calendar.CAL_SHOW_HOLIDAYS | wx.calendar.CAL_SUNDAY_FIRST |
                                       wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)

    def test_vocabulary(self, e):
        print 'x'

    def configure_server(self, e):
        print 'y'