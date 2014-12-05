__author__ = 'trungpv'
from ObjectListView import ObjectListView, ColumnDefn
from word.word import Word
import os.path
import wx
from dictionary.database import DataBase, LogDB
from word.pronunciation import AUDIO_DIR, OGG_EXTENSION


class WordView(object):
    """
    A class for displaying word data
    """
    def __init__(self, w_id, w_value, w_definition, w_date):
        self.id = w_id
        self.value = w_value
        self.definition = w_definition
        self.date = w_date


class MainPanel(wx.Panel):
    """
    http://www.blog.pythonlibrary.org/2009/12/23/wxpython-using-objectlistview-instead-of-a-listctrl/
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        # get word data
        self.dict_db = DataBase()
        self.saved_words = self.dict_db.load()
        self.num_word = len(self.saved_words)
        self.view_words = []
        self.log_db = LogDB()
        self.log = self.log_db.load()
        # display words on overlay
        self.dataOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.sound = self.dataOlv.AddNamedImages('user', wx.Bitmap('icon/sound.ico'))
        self.set_columns()
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.dataOlv, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)
        self.view_data()

    @staticmethod
    def normalize_view_def(word):
        """
        Take the first definition of word to display on overlay
        :param word:
        :return:
        """
        word_view = ' '.join(word[0].split()[1:15])  # get 15 first words in definition
        word_view = word_view.translate(None, '.,') + ' ...'  # remove punctuations
        return word_view

    def saved_to_view_words(self):
        """
        Convert from saved words (taken from database under dictionary type) to view words
        :param:dictionary
        :return:
        """
        word_id = 1
        for k, v in self.saved_words.items():
            tmp_obj = WordView(word_id, k, self.normalize_view_def(v), self.log.get(k, ' ')[0])
            self.view_words.append(tmp_obj)
            word_id += 1

    def view_data(self):
        """
        Display word definition on overlay
        :param word_list:
        :return:
        """
        self.saved_to_view_words()
        self.dataOlv.SetObjects(self.view_words)

    def add_new_data(self, new_word):
        """
        Add a record to data overlay
        :param new_word:
        :return:
        """
        progress_max = 100
        progress_dlg = wx.ProgressDialog('Connecting to servers...', 'Time remaining', progress_max,
                                         style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE)
        progress_dlg.Update(0)
        w = Word(value=new_word)
        # check whether new word exists or is blank
        if new_word not in self.saved_words.keys() and new_word != "":
            # take definition from server
            word_def = w.get_definition()
            progress_dlg.Update(30)
            if word_def is not '':
                # save definition to database and get it to display on overlay
                self.num_word += 1
                now = wx.DateTime.Now()
                today = now.Format("%Y-%m-%d")
                saved_def = DataBase.normalize_saved_def(word_def)
                view_def = self.normalize_view_def(saved_def)
                self.saved_words[new_word] = saved_def
                self.dict_db.save(self.saved_words)
                progress_dlg.Update(60)
                # display definition on overlay
                self.view_words.append(WordView(self.num_word, new_word, view_def, today))
                self.dataOlv.SetObjects(self.view_words)
                progress_dlg.Update(70)
                # save date to log file
                self.log[new_word] = []
                self.log[new_word].append(today)
                self.log_db.save(self.log)
                progress_dlg.Update(80)
        # get word pronunciation from server and update 'sound' icon on overlay
        w.get_pronunciation()
        self.set_columns()  # update 'sound' icon for new word displayed on overlay
        progress_dlg.Update(100)
        progress_dlg.Destroy()

    def set_columns(self):
        """
        Column design for data overlay
        :return:
        """
        def image_getter(word):
            if os.path.exists(AUDIO_DIR + word.value + OGG_EXTENSION):
                return self.sound

        self.dataOlv.SetColumns([
            ColumnDefn('No', 'center', 50, 'id'),
            ColumnDefn('Word', 'left', 50, 'value'),
            ColumnDefn('Definition', 'left', 550, 'definition'),
            # ColumnDefn('Date', 'left', 100, 'date', stringConverter="%d-%b-%Y"),
            ColumnDefn('Date', 'left', 100, 'date'),
            ColumnDefn('', 'center', 20, 'music', imageGetter=image_getter)
        ])

        self.dataOlv.SetObjects(self.view_words)

    def add_word(self, e):
        """
        Event raises when add word button is clicked
        :param e:
        :return:
        """
        name_box = wx.TextEntryDialog(None, 'Please enter a new word: ', 'Sim', '')
        if name_box.ShowModal() == wx.ID_OK:
            new_word = name_box.GetValue()
            self.add_new_data(new_word)

    def play_pronunciation(self, e):
        """
        Event raises when play button is clicked
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObjects()
        for obj in selected_obj:
            w = Word(obj.value)
            w.pronounce()

    def view_definition(self, e):
        """
        Event raises when view definition button is clicked
        :param e:
        :return:
        """
        selected_obj = self.dataOlv.GetSelectedObjects()
        word_def = ""
        for obj in selected_obj:
            word_def += obj.value.upper() + '\n'
            for line in self.saved_words[obj.value]:
                word_def += line.decode('utf-8') + '\n'
            word_def += '-------------------------------------------\n'
        msg_box = wx.MessageDialog(None, word_def, 'Word Definition', style=wx.OK | wx.ICON_INFORMATION)
        msg_box.ShowModal()