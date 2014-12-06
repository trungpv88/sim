__author__ = 'User'
import wx
import wx.calendar
import wx.lib.calendar
from dictionary.database import LogDB


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
        # calendar = wx.calendar.CalendarCtrl(self.parent, wx.ID_ANY, wx.DateTime_Now())
        # attr = wx.calendar.CalendarDateAttr(border=wx.calendar.CAL_BORDER_SQUARE, colBorder="blue")
        # calendar.SetAttr(14, attr)
        # calendar.Show()

    def test_vocabulary(self, e):
        print 'x'

    def configure_server(self, e):
        print 'y'


class CalendarDialog(wx.Dialog):
    """
    Reference: https://www.daniweb.com/software-development/python/threads/424230/wxpython-datepickerctrl-problem
    """
    def __init__(self, parent, title):
        self.log_db = LogDB()
        self.log = self.log_db.load()
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        today = wx.DateTime_Now()
        self.calendar = wx.calendar.CalendarCtrl(self, wx.ID_ANY, today, style=wx.calendar.CAL_MONDAY_FIRST)
        self.show_learnt_date(today.GetMonth() + 1, today.GetYear())
        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.Add(self.calendar, 0, wx.EXPAND | wx.ALL, border=0)
        self.calendar.Bind(wx.calendar.EVT_CALENDAR_DAY, self.on_date_selected)
        self.calendar.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.on_month_changed)
        self.calendar.Bind(wx.calendar.EVT_CALENDAR_YEAR, self.on_month_changed)
        self.label = wx.StaticText(self, wx.ID_ANY, '')
        box_sizer.Add(self.label, 0, wx.EXPAND | wx.ALL, border=20)
        self.SetSizerAndFit(box_sizer)
        self.ShowModal()

    def on_date_selected(self, e):
        date = self.calendar.GetDate()
        day = date.GetDay()
        month = date.GetMonth() + 1
        year = date.GetYear()
        date_str = "%02d-%02d-%02d" % (year, month, day)
        learnt_words = ""
        for k, v in self.log.items():
            if v[0] == date_str:
                learnt_words += k + ' '
        self.label.SetLabel(learnt_words)

    def on_month_changed(self, e):
        for i in xrange(1, 31, 1):
            self.calendar.ResetAttr(i)
        date = self.calendar.GetDate()
        self.show_learnt_date(date.GetMonth() + 1, date.GetYear())

    def show_learnt_date(self, month, year):
        month_year = "%02d-%02d" % (year, month,)
        days = {}
        for k, v in self.log.items():
            if v[0][:7] == month_year:
                days[v[0][9]] = ''
        for k in days.iterkeys():
            highlight = wx.calendar.CalendarDateAttr(border=wx.calendar.CAL_BORDER_SQUARE,
                                                     colBorder=wx.Colour(255, 255, 255),
                                                     colText=wx.Colour(255, 0, 0), colBack=wx.Colour(0, 255, 0))
            self.calendar.SetAttr(day=int(k), attr=highlight)