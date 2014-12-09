__author__ = 'User'
import wx
import wx.calendar
import wx.lib.calendar
import wx.gizmos
import os.path
from dictionary.database import LogDB
from word.pronunciation import AUDIO_DIR, OGG_EXTENSION
from utils import DATE_FORMAT
from word.word import Word


class ToolBar(object):
    def __init__(self, parent):
        self.parent = parent
        self.choose_language = 'English'

    def change_language(self, e):
        self.choose_language = wx.SingleChoiceDialog(None, 'Choose your learning language:', 'Language',
                                                ['English', 'French'])
        if self.choose_language.ShowModal() == wx.ID_OK:
            print self.choose_language.GetStringSelection()

    def track_learning(self, e):
        CalendarDialog(self.parent, 'Learning tracking')

    def test_vocabulary(self, e):
        TestDialog(self.parent, 'Test vocabulary')

    def configure_server(self, e):
        ServerDialog(self.parent, 'Configure server')


class CalendarDialog(wx.Dialog):
    """
    A class to show calendar and to highlight the learning days
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
                learnt_words += k + ' '
        self.label.SetLabel(learnt_words)

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
        days = {}
        for k, v in self.log.items():
            if v[0][:7] == month_year:
                days[v[0][9]] = ''
        for k in days.iterkeys():
            highlight = wx.calendar.CalendarDateAttr(border=wx.calendar.CAL_BORDER_SQUARE,
                                                     colBorder=wx.Colour(255, 255, 255),
                                                     colText=wx.Colour(255, 0, 0), colBack=wx.Colour(0, 255, 0))
            self.calendar.SetAttr(day=int(k), attr=highlight)


class TestDialog(wx.Dialog):
    """
    A class gives some exams for user to test vocabulary
    """
    def __init__(self, parent, title):
        # wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(255, 365))
        super(TestDialog, self).__init__(parent, wx.ID_ANY, title, size=(280, 360))
        self.is_pronounce = False
        self.log_db = LogDB()
        self.log = self.log_db.load()
        self.word_list = []
        self.audio_list = {}
        self.current_word_pos = 0
        self.get_audio_list()
        self.panel = wx.Panel(self)
        self.parent = parent
        self.led = None
        self.timer = None
        self.play_btn = None
        self.start_date_picker = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN, size=(100, 20))
        self.start_date = None
        self.end_date_picker = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN, size=(100, 20))
        self.end_date = None
        self.nb_words_cb = wx.ComboBox(self, -1, value='10', style=wx.CB_READONLY, choices=['10', '20', '50', '100'],
                                       size=(100, 20))
        self.nb_words = None
        self.delay_cb = wx.ComboBox(self, -1, value='10', style=wx.CB_READONLY, choices=['5', '10'], size=(100, 20))
        self.delay = None
        self.answer_text = wx.StaticText(self, -1, '---', size=(70, 20))
        self.answer_text.SetForegroundColour((0, 0, 255))
        self.hit_text = wx.StaticText(self, -1, '-/- (--%)', size=(70, 20))
        self.listen_word = wx.TextCtrl(self, -1, size=(70, 20))
        self.word_count = 0
        self.word_hit = 0
        self.time_remaining = -1
        self.dialog_design()
        self.Bind(wx.EVT_CLOSE, self.test)
        self.ShowModal()

    def test(self, e):
        self.timer.Destroy()
        self.Destroy()

    def get_audio_list(self):
        for word, v in self.log.items():
            if os.path.exists(AUDIO_DIR + word + OGG_EXTENSION):
                self.audio_list[word] = v[0]
                self.word_list.append(word)

    def dialog_design(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        option_box_sizer = self.create_option_box()
        test_box_sizer = self.create_test_box()
        main_sizer.Add(option_box_sizer, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(test_box_sizer, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(main_sizer)

    def create_option_box(self):
        option_box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Options'), orient=wx.VERTICAL)
        option_sizer = wx.BoxSizer(wx.VERTICAL)
        option__grid_sizer = wx.GridSizer(4, 1, vgap=5)
        start_date = self.create_date('From date', self.start_date_picker)
        end_date = self.create_date('To date', self.end_date_picker)
        nb_words = self.create_combo_box('Number of words', self.nb_words_cb)
        time_delay = self.create_combo_box('Answer time (s)', self.delay_cb)
        option__grid_sizer.Add(start_date)
        option__grid_sizer.Add(end_date)
        option__grid_sizer.Add(nb_words, wx.ALIGN_CENTER_VERTICAL)
        option__grid_sizer.Add(time_delay, wx.ALIGN_CENTER_VERTICAL)
        option_sizer.Add(option__grid_sizer)
        option_box_sizer.Add(option_sizer, 0, wx.TOP, 10)
        return option_box_sizer

    def create_date(self, name, date_picker):
        date_grid_sizer = wx.GridSizer(1, 2)
        date_label = wx.StaticText(self, -1, name, size=(110, 20))
        # self.date_picker = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN, size=(100, 20))
        # date_picker = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN, size=(100, 20))
        date_grid_sizer.Add(date_label, wx.ALIGN_CENTER_VERTICAL)
        date_grid_sizer.Add(date_picker, wx.ALIGN_CENTER_VERTICAL)
        return date_grid_sizer

    def create_combo_box(self, label, control):
        words_grid_sizer = wx.GridSizer(1, 2)
        words_label = wx.StaticText(self, -1, label, size=(110, 20))
        words_grid_sizer.Add(words_label, wx.ALIGN_CENTER_VERTICAL)
        words_grid_sizer.Add(control, wx.ALIGN_CENTER_VERTICAL)
        return words_grid_sizer

    def create_test_box(self):
        test_grid_sizer = wx.GridSizer(2, 2, hgap=40, vgap=30)
        answer_sizer = self.create_answer_box()
        self.create_led_timer()
        result_sizer = self.create_result()
        control_sizer = self.create_control()
        test_grid_sizer.Add(answer_sizer)
        test_grid_sizer.Add(self.led)
        test_grid_sizer.Add(result_sizer)
        test_grid_sizer.Add(control_sizer)
        return test_grid_sizer

    def create_answer_box(self):
        answer_grid_sizer = wx.GridSizer(3, 2, vgap=7)
        answer_grid_sizer.Add(wx.StaticText(self, -1, 'You hear:', size=(70, 20)))
        answer_grid_sizer.Add(self.listen_word)
        answer_grid_sizer.Add(wx.StaticText(self, -1, 'Word answer:', size=(70, 20)))
        answer_grid_sizer.Add(self.answer_text)
        answer_grid_sizer.Add(wx.StaticText(self, -1, 'Hits / Total:', size=(70, 20)))
        answer_grid_sizer.Add(self.hit_text)
        return answer_grid_sizer

    def create_led_timer(self):
        self.led = wx.gizmos.LEDNumberCtrl(self, -1, style=wx.gizmos.LED_ALIGN_CENTER)
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.update_timer)

    def pronounce(self):
        if self.is_pronounce:
            self.timer.Stop()
            self.is_pronounce = False
            word = Word(self.word_list[self.current_word_pos])
            word.pronounce()
            self.current_word_pos += 1
            self.timer.Start(1000)

    def update_timer(self, e):
        self.pronounce()
        if self.time_remaining <= 0:
            if self.time_remaining == 0:  # because word are already pronounced at the first time
                self.is_pronounce = True
                if self.listen_word.GetValue() == self.word_list[self.current_word_pos - 1]:
                    self.word_hit += 1
                self.word_count += 1
                self.hit_text.SetLabel('%d/%d (%.2f)' % (self.word_hit, self.word_count,
                                                         float(self.word_hit)/float(self.word_count)))
            self.time_remaining = int(self.delay)
            self.answer_text.SetLabel('---')

        else:
            self.time_remaining -= 1
            if self.time_remaining < 2:
                self.answer_text.SetLabel(self.word_list[self.current_word_pos - 1])
            elif self.time_remaining < 4:
                self.led.SetForegroundColour(wx.Colour(255, 0, 0))
            elif self.time_remaining < 6:
                self.led.SetForegroundColour(wx.Colour(255, 255, 0))
            else:
                self.led.SetForegroundColour(wx.Colour(0, 255, 0))
        self.led.SetValue(str(self.time_remaining))

    def create_result(self):
        result_grid_sizer = wx.GridSizer(1, 3)
        result_mark_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/result_mark.ico'), style=wx.BORDER_NONE)
        result_mark_btn.SetToolTip(wx.ToolTip('View result detail'))
        result_log_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/result_log.ico'), style=wx.BORDER_NONE)
        result_log_btn.SetToolTip(wx.ToolTip('View result log'))
        result_grid_sizer.Add(result_mark_btn, wx.ALIGN_RIGHT)
        result_grid_sizer.Add(result_log_btn)
        return result_grid_sizer

    def create_control(self):
        control_grid_sizer = wx.GridSizer(1, 3)
        self.play_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/play.ico'), size=(36, 36), style=wx.BORDER_NONE)
        self.play_btn.SetBitmapDisabled(wx.Bitmap('icon/play_disable.ico'))
        self.play_btn.SetToolTip(wx.ToolTip('Listen'))
        self.play_btn.Bind(wx.EVT_BUTTON, self.on_play_test)
        control_grid_sizer.Add(wx.StaticText(self, -1, ''))
        control_grid_sizer.Add(wx.StaticText(self, -1, ''))
        control_grid_sizer.Add(self.play_btn)
        return control_grid_sizer

    def on_play_test(self, e):
        self.play_btn.Disable()
        self.init_param()
        self.is_pronounce = True
        self.timer.Start(1000)

    def init_param(self):
        self.start_date = self.start_date_picker.GetValue()
        self.start_date = self.start_date.Format(DATE_FORMAT)
        self.end_date = self.end_date_picker.GetValue()
        self.end_date = self.end_date.Format(DATE_FORMAT)
        self.nb_words = self.nb_words_cb.GetValue()
        self.delay = self.delay_cb.GetValue()


class ServerDialog(wx.Dialog):
    """
    A class to configure definition/audio/check server
    """
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.ShowModal()