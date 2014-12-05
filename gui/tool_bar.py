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
        CalendarDialog(self.parent, 'Learning tracking')

    def test_vocabulary(self, e):
        print 'x'

    def configure_server(self, e):
        print 'y'


class CalendarDialog(wx.Dialog):
    """
    Reference: https://www.daniweb.com/software-development/python/threads/424230/wxpython-datepickerctrl-problem
    """
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.calendar = wx.calendar.CalendarCtrl(self, wx.ID_ANY, wx.DateTime_Now())
        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.Add(self.calendar, 0, wx.EXPAND|wx.ALL, border=20)
        self.calendar.Bind(wx.calendar.EVT_CALENDAR_DAY, self.on_date_selected)

        self.label = wx.StaticText(self, wx.ID_ANY, 'click on a day')
        box_sizer.Add(self.label, 0, wx.EXPAND|wx.ALL, border=20)
        self.SetSizerAndFit(box_sizer)
        self.Show(True)
        self.Centre()

    def on_date_selected(self, e):
        #date = event.GetDate()
        date = self.calendar.GetDate()
        day = date.GetDay()
        # for some strange reason month starts with zero
        month = date.GetMonth() + 1
        # year is yyyy format
        year = date.GetYear()
        # format the date string to your needs
        ds = "%02d/%02d/%d \n" % (month, day, year)
        self.label.SetLabel(ds)
