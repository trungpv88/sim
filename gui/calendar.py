import wx
import wx.calendar
from dictionary.database import LogDB


class CalendarDialog(wx.Dialog):
    """
    A class to show calendar and to highlight the learning days
    """
    def __init__(self, parent, title):
        self.log_db = LogDB()
        self.log = self.log_db.load()
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(300, 250))
        today = wx.DateTime_Now()
        self.calendar = wx.calendar.CalendarCtrl(self, wx.ID_ANY, today, style=wx.calendar.CAL_MONDAY_FIRST)
        self.words = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.show_learnt_date(today.GetMonth() + 1, today.GetYear())
        self.design_interface()
        self.ShowModal()

    def design_interface(self):
        """
        Design interface for dialog
        :return:
        """
        box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        box_sizer.Add(self.calendar, 0, wx.ALL | wx.EXPAND, border=10)
        self.calendar.Bind(wx.calendar.EVT_CALENDAR_DAY, self.on_date_selected)
        self.calendar.Bind(wx.calendar.EVT_CALENDAR_MONTH, self.on_month_changed)
        self.calendar.Bind(wx.calendar.EVT_CALENDAR_YEAR, self.on_month_changed)
        word_sizer = wx.BoxSizer(wx.VERTICAL)
        month_btn = wx.Button(self, wx.ID_ANY, 'This month')
        year_btn = wx.Button(self, wx.ID_ANY, 'This year')
        month_btn.Bind(wx.EVT_BUTTON, self.show_month_chart)
        year_btn.Bind(wx.EVT_BUTTON, self.show_year_chart)
        word_sizer.Add(month_btn, 0, wx.BOTTOM | wx.EXPAND, border=10)
        word_sizer.Add(year_btn, 0, wx.BOTTOM | wx.EXPAND, border=10)
        word_sizer.Add(self.words, 1, wx.ALL | wx.EXPAND, border=0)
        box_sizer.Add(word_sizer, 1, wx.ALL | wx.EXPAND, border=10)
        self.SetSizer(box_sizer)

    def show_month_chart(self, e):
        """
        Display the number of new words in this month by line chart
        :param e:
        :return:
        """
        date = self.calendar.GetDate()
        month = date.GetMonth() + 1
        year = date.GetYear()
        month_year = "%02d-%02d" % (year, month)
        learnt_words = {}
        for i in range(31):
            learnt_words[i * 10] = 0
        for k, v in self.log.items():
            if v[0][0:7] == month_year:
                learnt_words[(int(v[0][8:10]) - 1) * 10] += 10
        LineChartDialog(self, 'Sim', month_year, learnt_words, 31, 21, 10, 10)

    def show_year_chart(self, e):
        """
        Display the number of new words in this year by line chart
        :param e:
        :return:
        """
        date = self.calendar.GetDate()
        year = date.GetYear()
        learnt_words = {}
        for i in range(12):
            learnt_words[i * 25] = 0
        for k, v in self.log.items():
            if v[0][0:4] == str(year):
                learnt_words[(int(v[0][5:7]) - 1) * 25] += 1
        LineChartDialog(self, 'Sim', str(year), learnt_words, 12, 21, 25, 1)

    def on_date_selected(self, e):
        """
        Show the learnt words of date selected
        :param e:
        :return:
        """
        date = self.calendar.GetDate()
        day = date.GetDay()
        month = date.GetMonth() + 1
        year = date.GetYear()
        date_str = "%02d-%02d-%02d" % (year, month, day)
        learnt_words = ""
        for k, v in self.log.items():
            if v[0] == date_str:
                learnt_words += k + '\n'
        self.words.SetValue(learnt_words)

    def on_month_changed(self, e):
        """
        Refresh learning days when month changed
        :param e:
        :return:
        """
        for i in xrange(1, 31, 1):
            self.calendar.ResetAttr(i)
        date = self.calendar.GetDate()
        self.show_learnt_date(date.GetMonth() + 1, date.GetYear())

    def show_learnt_date(self, month, year):
        """
        Show the learning days in month
        :param month:
        :param year:
        :return:
        """
        month_year = "%02d-%02d" % (year, month,)
        days = []
        for v in self.log.itervalues():
            if v[0][:7] == month_year:
                days.append(v[0][8:])
        for k in days:
            highlight = wx.calendar.CalendarDateAttr(border=wx.calendar.CAL_BORDER_SQUARE,
                                                     colBorder=wx.Colour(255, 255, 255),
                                                     colText=wx.Colour(255, 0, 0), colBack=wx.Colour(0, 255, 0))
            self.calendar.SetAttr(day=int(k), attr=highlight)


class LineChartDialog(wx.Dialog):
    """
    Reference: http://zetcode.com/wxpython/gdi/
    """
    def __init__(self, parent, title, chart_title, data, x_range, y_range, x_cell, y_cell):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(390, 350))
        line_box = wx.BoxSizer(wx.HORIZONTAL)
        line_chart = LineChart(self, chart_title, data, x_range, y_range, x_cell, y_cell)
        line_box.Add(line_chart, 1, wx.EXPAND | wx.ALL, 15)
        self.SetSizer(line_box)
        self.ShowModal()


class LineChart(wx.Panel):
    def __init__(self, parent, chart_title, data, x_range, y_range, x_cell, y_cell):
        wx.Panel.__init__(self, parent)
        self.y_range = y_range
        self.x_range = x_range
        self.x_cell = x_cell
        self.y_cell = y_cell
        self.chart_title = chart_title
        self.data = data
        self.days = tuple([str(d + 1) for d in range(x_range)])
        self.SetBackgroundColour('WHITE')
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.SetDeviceOrigin(40, 240)
        dc.SetAxisOrientation(True, True)
        dc.SetPen(wx.Pen('WHITE'))
        dc.DrawRectangle(1, 1, (self.x_range - 1) * 10, (self.y_range - 1) * self.y_cell)
        self.draw_axis(dc)
        self.draw_grid(dc)
        self.draw_title(dc)
        self.draw_data(dc)

    def draw_axis(self, dc):
        """
        Draw x axis and y axis
        :param dc:
        :return:
        """
        dc.SetPen(wx.Pen('#0AB1FF'))
        font = dc.GetFont()
        font.SetPointSize(8)
        dc.SetFont(font)
        dc.DrawLine(1, 1, (self.x_range - 1) * self.x_cell, 1)
        dc.DrawLine(1, 1, 1, (self.y_range - 1) * 10)
        # y axis
        for i in range(20, 220, 20):
            dc.DrawText(str(i/self.y_cell), -30, i+5)
            dc.DrawLine(2, i, -5, i)
        font.SetPointSize(5)
        dc.SetFont(font)
        # x axis
        for i in range(self.x_range):
            dc.DrawText(self.days[i], i * self.x_cell, -10)
        font.SetPointSize(8)
        dc.SetFont(font)

    def draw_grid(self, dc):
        """
        Draw grid on line chart
        :param dc:
        :return:
        """
        dc.SetPen(wx.Pen('#d5d5d5'))
        # draw horizontal lines
        for i in range(10, self.y_range * 10, 10):
            dc.DrawLine(2, i, (self.x_range - 1) * self.x_cell, i)
        # draw vertical lines
        for i in range(self.x_cell, self.x_range * self.x_cell, self.x_cell):
            dc.DrawLine(i, 2, i, (self.y_range - 1) * 10)

    def draw_title(self, dc):
        """
        Draw title of chart
        :param dc:
        :return:
        """
        font = dc.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        dc.DrawText('New words in ' + self.chart_title, 90, 235)

    def draw_data(self, dc):
        """
        Draw line chart using data given
        :param dc:
        :return:
        """
        dc.SetPen(wx.Pen(wx.RED, style=wx.SOLID))
        for i in range(0, (self.x_range - 1) * self.x_cell, self.x_cell):
            dc.DrawLinePoint((i, self.data[i]), (i + self.x_cell, self.data[i + self.x_cell]))
