import wx
import wx.calendar
import wx.lib.calendar
import wx.gizmos
import os.path
import random
from dictionary.database import LogDB
from word.pronunciation import AUDIO_DIR, OGG_EXTENSION
from utils import DATE_FORMAT, HIT_TEXT_DEFAULT
from word.word import Word


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
        CalendarDialog(self.parent, 'Learning tracking')

    def test_vocabulary(self, e):
        """
        Event raises when test button is clicked
        """
        TestDialog(self.parent, 'Test vocabulary')

    def configure_server(self, e):
        """
        Event raises when server configuration button is clicked
        """
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
        days = []
        for v in self.log.itervalues():
            if v[0][:7] == month_year:
                days.append(v[0][8:])
        for k in days:
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
        super(TestDialog, self).__init__(parent, wx.ID_ANY, title, size=(280, 400))
        self.is_pronounce = False
        self.log_db = LogDB()
        self.log = self.log_db.load()
        self.test_words = []
        self.answer_words = []
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
        self.Bind(wx.EVT_DATE_CHANGED, self.update_words_in_date_range)
        self.end_date_picker = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN, size=(100, 20))
        self.end_date = None
        self.words_date_range = wx.StaticText(self, -1, '0 words')
        self.nb_words_cb = wx.ComboBox(self, -1, value='10', style=wx.CB_READONLY, choices=['10', '20', '50', '100'],
                                       size=(100, 20))
        self.nb_words = None
        self.delay_cb = wx.ComboBox(self, -1, value='10', style=wx.CB_READONLY, choices=['5', '10'], size=(100, 20))
        self.delay = None
        self.answer_text = wx.StaticText(self, -1, '---', size=(70, 20))
        self.answer_text.SetForegroundColour((0, 0, 255))
        self.hit_text = wx.StaticText(self, -1, HIT_TEXT_DEFAULT, size=(70, 20))
        self.listen_word = wx.TextCtrl(self, -1, size=(70, 20))
        self.word_count = 0
        self.word_hit = 0
        self.time_remaining = -1
        self.dialog_design()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.update_words_in_date_range(None)
        self.ShowModal()

    def dialog_design(self):
        """
        Design test interface
        :return:
        """
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        option_box_sizer = self.create_option_box()
        test_box_sizer = self.create_test_box()
        main_sizer.Add(option_box_sizer, 1, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(test_box_sizer, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(main_sizer)

    def create_option_box(self):
        """
        Design option box to modify parameters
        :return:
        """
        option_box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, 'Options'), orient=wx.VERTICAL)
        option_sizer = wx.BoxSizer(wx.VERTICAL)
        option_grid_sizer = wx.GridSizer(5, 1, vgap=5)
        start_date = self.create_date('From date', self.start_date_picker)
        end_date = self.create_date('To date', self.end_date_picker)
        nb_words_in_date_range = self.create_words_date_range('Learned', self.words_date_range)
        nb_test_words = self.create_combo_box('Number of words', self.nb_words_cb)  # the number of test words
        time_delay = self.create_combo_box('Answer time (s)', self.delay_cb)  # time to answer after listen a word
        option_grid_sizer.Add(start_date)
        option_grid_sizer.Add(end_date)
        option_grid_sizer.Add(nb_words_in_date_range)
        option_grid_sizer.Add(nb_test_words, wx.ALIGN_CENTER_VERTICAL)
        option_grid_sizer.Add(time_delay, wx.ALIGN_CENTER_VERTICAL)
        option_sizer.Add(option_grid_sizer)
        option_box_sizer.Add(option_sizer, 0, wx.TOP, 10)
        return option_box_sizer

    def create_date(self, name, date_picker):
        """
        Create a date picker to choose a date from calendar
        :param name:
        :param date_picker:
        :return:
        """
        date_grid_sizer = wx.GridSizer(1, 2)
        date_label = wx.StaticText(self, -1, name, size=(110, 20))
        date_grid_sizer.Add(date_label, wx.ALIGN_CENTER_VERTICAL)
        date_grid_sizer.Add(date_picker, wx.ALIGN_CENTER_VERTICAL)
        return date_grid_sizer

    def create_words_date_range(self, name, words_date_range_text):
        """
        Create labels to show the number of learnt words from start date to end date
        :param name:
        :param words_date_range_text:
        :return:
        """
        words_date_range_sizer = wx.GridSizer(1, 2)
        words_date_range_label = wx.StaticText(self, -1, name, size=(110, 20))
        words_date_range_sizer.Add(words_date_range_label, wx.ALIGN_CENTER_VERTICAL)
        words_date_range_sizer.Add(words_date_range_text, wx.ALIGN_CENTER_VERTICAL)
        return words_date_range_sizer

    def create_combo_box(self, label, control):
        '''
        Create combo box to select a value
        :param label:
        :param control:
        :return:
        '''
        words_grid_sizer = wx.GridSizer(1, 2)
        words_label = wx.StaticText(self, -1, label, size=(110, 20))
        words_grid_sizer.Add(words_label, wx.ALIGN_CENTER_VERTICAL)
        words_grid_sizer.Add(control, wx.ALIGN_CENTER_VERTICAL)
        return words_grid_sizer

    def create_test_box(self):
        """
        Design test region including the answer and result
        :return:
        """
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
        """
        Design region to answer and show result
        :return:
        """
        answer_grid_sizer = wx.GridSizer(3, 2, vgap=7)
        answer_grid_sizer.Add(wx.StaticText(self, -1, 'You hear:', size=(70, 20)))
        answer_grid_sizer.Add(self.listen_word)
        answer_grid_sizer.Add(wx.StaticText(self, -1, 'Answer:', size=(70, 20)))
        answer_grid_sizer.Add(self.answer_text)
        answer_grid_sizer.Add(wx.StaticText(self, -1, 'Hits / Total:', size=(70, 20)))
        answer_grid_sizer.Add(self.hit_text)
        return answer_grid_sizer

    def create_led_timer(self):
        """
        A led clock to show the time remaining
        :return:
        """
        self.led = wx.gizmos.LEDNumberCtrl(self, -1, style=wx.gizmos.LED_ALIGN_CENTER)
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.update_timer)

    def create_result(self):
        """
        Create buttons to view results
        :return:
        """
        result_grid_sizer = wx.GridSizer(1, 3)
        result_mark_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/result_mark.ico'), style=wx.BORDER_NONE)
        result_mark_btn.SetToolTip(wx.ToolTip('View result detail'))
        result_mark_btn.Bind(wx.EVT_BUTTON, self.on_view_result_detail)
        result_log_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/result_log.ico'), style=wx.BORDER_NONE)
        result_log_btn.SetToolTip(wx.ToolTip('View result log'))
        result_grid_sizer.Add(result_mark_btn, wx.ALIGN_RIGHT)
        result_grid_sizer.Add(result_log_btn)
        return result_grid_sizer

    def create_control(self):
        """
        Create controls to start test
        :return:
        """
        control_grid_sizer = wx.GridSizer(1, 3)
        self.play_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/play.ico'), size=(36, 36), style=wx.BORDER_NONE)
        self.play_btn.SetBitmapDisabled(wx.Bitmap('icon/play_disable.ico'))
        self.play_btn.SetToolTip(wx.ToolTip('Listen'))
        self.play_btn.Bind(wx.EVT_BUTTON, self.on_play_test)
        control_grid_sizer.Add(wx.StaticText(self, -1, ''))
        control_grid_sizer.Add(wx.StaticText(self, -1, ''))
        control_grid_sizer.Add(self.play_btn)
        return control_grid_sizer

    def get_audio_list(self):
        """
        Get words having pronunciation
        :return:
        """
        for word, v in self.log.items():
            if os.path.exists(AUDIO_DIR + word + OGG_EXTENSION):
                self.audio_list[word] = v[0]

    def get_audio_list(self):
        """
        Get words having pronunciation
        :return:
        """
        for word, v in self.log.items():
            if os.path.exists(AUDIO_DIR + word + OGG_EXTENSION):
                self.audio_list[word] = v[0]

    def update_words_in_date_range(self, e):
        """
        Show the number of learned words in a date range
        :param e:
        :return:
        """
        start_date = self.start_date_picker.GetValue()
        start_date = start_date.Format(DATE_FORMAT)
        end_date = self.end_date_picker.GetValue()
        end_date = end_date.Format(DATE_FORMAT)
        # get words learnt from start_date to end_date
        self.test_words = [w for w, d in self.audio_list.items() if end_date >= d >= start_date]
        self.words_date_range.SetLabel('%s words' % len(self.test_words))

    def pronounce(self):
        """
        Pronounce a test word.
        Note: stop timer when the word is pronounced to avoid using answer time
        :return:
        """
        if self.is_pronounce:
            self.timer.Stop()
            word = Word(self.test_words[self.current_word_pos])
            word.pronounce()
            self.is_pronounce = False
            # start timer
            self.time_remaining = int(self.delay)
            self.timer.Start(1000)
            # set green colour to digit in led clock
            self.led.SetForegroundColour(wx.Colour(0, 255, 0))

    def update_led(self):
        """
        Update status of digit in led clock
        :return:
        """
        self.time_remaining -= 1
        if self.time_remaining < 1:
            self.answer_text.SetLabel(self.test_words[self.current_word_pos])
        elif self.time_remaining < 4:
            self.led.SetForegroundColour(wx.Colour(255, 0, 0))
        elif self.time_remaining < 6:
            self.led.SetForegroundColour(wx.Colour(255, 255, 0))

    def finish_test_a_word(self):
        """
        Show the result statistic when finish each test word
        :return:
        """
        self.is_pronounce = True
        # check the answer
        self.answer_words.append(self.listen_word.GetValue())
        if self.listen_word.GetValue() == self.test_words[self.current_word_pos]:
            self.word_hit += 1
        self.word_count += 1
        self.hit_text.SetLabel('%d/%d (%.2f)' % (self.word_hit, self.word_count,
                                                 float(self.word_hit)/float(self.word_count)))
        self.current_word_pos += 1
        # reset the answer word label
        self.answer_text.SetLabel('---')

    def finish_all_test(self):
        """
        Reset test interface and stop timer
        :return:
        """
        self.hit_text.SetForegroundColour(wx.Colour(255, 0, 0))
        self.hit_text.Refresh()
        self.play_btn.Enable()
        self.timer.Stop()

    def update_timer(self, e):
        """
        When the timer is started
        :param e:
        :return:
        """
        # when all the test word is pronounced
        if self.current_word_pos >= len(self.test_words):
            self.finish_all_test()
            return
        self.pronounce()
        if self.time_remaining > 0:
            self.update_led()
        else:
            self.finish_test_a_word()
        self.led.SetValue(str(self.time_remaining))

    def on_play_test(self, e):
        """
        Event raises when listen button is clicked
        :param e:
        :return:
        """
        self.init_param()
        if len(self.test_words) == 0:
            self.play_btn.Enable()
            return
        self.timer.Start(1000)

    def on_view_result_detail(self, e):
        result_detail = 'Answer - Listen\n'
        if len(self.answer_words) == len(self.test_words):
            for i in range(len(self.test_words)):
                result_detail += '%s. %s - %s \n' % (i + 1,  self.test_words[i], self.answer_words[i])
        result_detail_dialog = wx.MessageDialog(None, result_detail, 'Result detail', style=wx.OK | wx.ICON_INFORMATION)
        result_detail_dialog.ShowModal()

    def init_param(self):
        """
        Initialize parameters before starting test
        :return:
        """
        self.play_btn.Disable()
        self.is_pronounce = True
        self.current_word_pos = 0
        self.word_hit = 0
        self.word_count = 0
        self.answer_words = []
        self.hit_text.SetLabel(HIT_TEXT_DEFAULT)
        self.hit_text.SetForegroundColour(wx.Colour(0, 0, 0))
        self.nb_words = self.nb_words_cb.GetValue()
        self.delay = self.delay_cb.GetValue()
        self.test_words = random.sample(self.test_words, min(int(self.nb_words), len(self.test_words)))

    def on_close(self, e):
        """
        Event raises when test dialog is closed
        :param e:
        :return:
        """
        self.timer.Destroy()
        self.Destroy()


class ServerDialog(wx.Dialog):
    """
    A class to configure definition/audio/check server
    """
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.ShowModal()