#----------------------------------------------------------------------------
# Change log:
# 2014/12/24  - Version 1.0
# 2015/01/16  - Version 1.1
#             - Change result detail screen
#----------------------------------------------------------------------------
# Goal:
# - Test user's memory by a learnt words test
# - Before test: choose start/end date, the test words number and the time interval for each listening word
# - In test: enter a word that user heard to a text box, the correct word will appear at that last second
# - After test: display the result with highlight words (blue for True and red for False)

import wx
from wx import gizmos
import wx.richtext
import random
import os.path
from dictionary.database import DataBase
from utils import DATE_FORMAT, HIT_TEXT_DEFAULT
from word.word import Word
from word.pronunciation import AUDIO_DIR, OGG_EXTENSION
from utils import convert_string_to_ogg
from sound import play_closing_sound, play_opening_sound


class TestDialog(wx.Dialog):
    """
    A class gives some exams for user to test vocabulary
    """
    def __init__(self, parent, title):
        # wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(255, 365))
        super(TestDialog, self).__init__(parent, wx.ID_ANY, title, size=(320, 400))
        self.is_pronounce = False
        self.db = DataBase()
        self.dict_db = self.db.load()
        self.word_date = {}
        self.get_date()
        self.create_audio_list()
        self.test_words = []
        self.answer_words = []
        self.current_word_pos = 0
        self.panel = wx.Panel(self)
        self.parent = parent
        self.led = None
        self.timer = None
        self.play_btn = None
        self.start_date_picker = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN, size=(130, 20))
        self.start_date = None
        self.Bind(wx.EVT_DATE_CHANGED, self.update_words_in_date_range)
        self.end_date_picker = wx.DatePickerCtrl(self, -1, style=wx.DP_DROPDOWN, size=(130, 20))
        self.end_date = None
        self.words_date_range = wx.StaticText(self, -1, '0 words', size=(130, 20))
        self.nb_words_cb = wx.ComboBox(self, -1, value='10', style=wx.CB_READONLY,
                                       choices=['10', '20', '50', '100', '200', '500', '1000'], size=(130, 20))
        self.nb_words = None
        self.delay_cb = wx.ComboBox(self, -1, value='10', style=wx.CB_READONLY, choices=['5', '10'], size=(130, 20))
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

    def get_date(self):
        """
        Get word date from dictionary extracted from database
        :return:
        """
        for w, v in self.dict_db[0].items():
            # check whether audio file exists
            if len(v.get('audio', '')) > 0:
                self.word_date[w] = v['date']

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
        """
        Create combo box to select a value
        :param label:
        :param control:
        :return:
        """
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
        return wx.StaticText(self, -1, '')

    def create_control(self):
        """
        Create controls to start test
        :return:
        """
        control_grid_sizer = wx.GridSizer(1, 3)
        self.play_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/play.ico'), size=(40, 40), style=wx.BORDER_NONE)
        self.play_btn.SetBitmapDisabled(wx.Bitmap('icon/play_disable.ico'))
        self.play_btn.SetBitmapHover(wx.Bitmap('icon/play_hover2.ico'))
        self.play_btn.SetToolTip(wx.ToolTip('Listen'))
        self.play_btn.Bind(wx.EVT_BUTTON, self.on_play_test)
        result_mark_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/result_mark.ico'), size=(40, 40),
                                          style=wx.BORDER_NONE)
        result_mark_btn.SetToolTip(wx.ToolTip('View result detail'))
        result_mark_btn.SetBitmapHover(wx.Bitmap('icon/result_mark_hover.ico'))
        result_mark_btn.Bind(wx.EVT_BUTTON, self.on_view_result_detail)
        close_btn = wx.BitmapButton(self, -1, wx.Bitmap('icon/close.ico'), size=(40, 40), style=wx.BORDER_NONE)
        close_btn.SetToolTip(wx.ToolTip('Close'))
        close_btn.SetBitmapHover(wx.Bitmap('icon/close_hover.ico'))
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        control_grid_sizer.Add(self.play_btn)
        control_grid_sizer.Add(result_mark_btn)
        control_grid_sizer.Add(close_btn)
        return control_grid_sizer

    def create_audio_list(self):
        """
        Get words having pronunciation
        :return:
        """
        for word, v in self.word_date.items():
            audio_str = self.dict_db[0][word].get('audio', '')
            path = unicode(AUDIO_DIR + word + OGG_EXTENSION)
            if not os.path.exists(path) and len(audio_str) > 0:
                convert_string_to_ogg(audio_str, path)

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
        self.test_words = [w for w, d in self.word_date.items() if end_date >= d >= start_date]
        self.words_date_range.SetLabel('%s audio-words' % len(self.test_words))

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
        self.listen_word.SetValue('')
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
        """
        Show answer and listen words
        :param e:
        :return:
        """
        result_detail = 'Answer - Listen\n'
        # only show result when finishing test
        if len(self.answer_words) == len(self.test_words):
            Result(self, self.answer_words, self.test_words)
            for i in range(len(self.test_words)):
                result_detail += '%s. %s - %s ' % (i + 1,  self.test_words[i], self.answer_words[i])
                # result_detail_dialog = wx.MessageDialog(None, result_detail, 'Result detail', style=wx.OK | wx.ICON_INFORMATION)
                # result_detail_dialog.ShowModal()

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
        play_closing_sound()
        self.timer.Destroy()
        self.Destroy()


class Result(wx.Dialog):
    def __init__(self, parent, answer_words, correct_words):
        super(Result, self).__init__(parent, wx.ID_ANY, 'Test detail', size=(300, 300))
        self.answer_words = answer_words
        self.correct_words = correct_words
        self.design_interface()
        play_opening_sound()
        self.ShowModal()
        play_closing_sound()

    def design_interface(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        result_boxer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Result'), orient=wx.VERTICAL)
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        content_text = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        content_text.SetInsertionPoint(0)
        for i in range(len(self.correct_words)):
            content = '%s. %s - %s ' % (i + 1, self.correct_words[i], self.answer_words[i] or 'N/A')
            colored_start_pos = len(content_text.GetLabel())
            content_text.AppendText(content)
            colored_end_pos = len(content_text.GetLabel())
            if self.correct_words[i] == self.answer_words[i]:
                content_text.SetStyle(colored_start_pos, colored_end_pos, wx.TextAttr("blue", "white"))
            else:
                content_text.SetStyle(colored_start_pos, colored_end_pos, wx.TextAttr("red", "white"))
        content_sizer.Add(content_text, 1, wx.EXPAND | wx.ALL, 1)
        result_boxer.Add(content_sizer, 1, wx.EXPAND | wx.ALL)
        main_sizer.Add(result_boxer, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(main_sizer)