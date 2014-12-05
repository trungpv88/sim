__author__ = 'trungpv'
from ObjectListView import ObjectListView, ColumnDefn
from word.word import Word
import os.path
import wx
from word.pronunciation import AUDIO_DIR, OGG_EXTENSION


class WordView(object):
    """
    A class for displaying word data
    """
    def __init__(self, w_id, w_value, w_definition):
        self.id = w_id
        self.value = w_value
        self.definition = w_definition


class MainPanel(wx.Panel):
    """
    http://www.blog.pythonlibrary.org/2009/12/23/wxpython-using-objectlistview-instead-of-a-listctrl/
    """
    def __init__(self, parent, word_list, dict_db):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.word_list = word_list
        self.word_list_view = {}
        self.normalize_word_list(word_list)
        self.dict_db = dict_db
        self.num_word = len(self.word_list)
        self.words = []
        # data overlay in list view
        self.dataOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.sound = self.dataOlv.AddNamedImages('user', wx.Bitmap('icon/sound.ico'))
        self.set_columns()
        # self.dataOlv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK
        # data overlay design
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.dataOlv, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)
        # load data to overlay
        self.load_data()

    @staticmethod
    def normalize_def_lines(lines):
        lines = lines.split('\n')
        normal_lines = []
        line_num = 1
        for line in lines:
            if line is not '':
                normal_line = line.replace(':', '.')  # replace last character from ':' to '.'
                # upper first character and insert space at the beginning of line
                if normal_line[0] is not ' ':
                    normal_line = ' ' + normal_line[0].upper() + normal_line[1:]
                else:
                    normal_line = normal_line[0] + normal_line[1].upper() + normal_line[2:]
                # insert definition number at beginning of line
                normal_line = str(line_num) + '.' + normal_line
                normal_lines.append(normal_line)
                line_num += 1
        return normal_lines

    def normalize_word_list(self, word_list):
        """
        Normalize content of word list.
        For example: {'hello': ['1. Hi', '2. Say in meeting']}
        :param word_list:
        :return:
        """
        for k, v in word_list.items():
            self.word_list_view[k] = self.normalize_def_lines(v)

    @staticmethod
    def normalize_def_line(word):
        word_view = ' '.join(word[0].split()[1:15])  # get 15 first words in definition
        word_view = word_view.translate(None, '.,') + ' ...'  # remove punctuations
        return word_view

    def dict_to_word_obj(self):
        """
        Convert from dictionary to WordView object
        :param word_list:dictionary
        :return:
        """
        word_id = 1
        for k, v in self.word_list_view.items():
            tmp_obj = WordView(word_id, k, self.normalize_def_line(v))
            self.words.append(tmp_obj)
            word_id += 1

    def load_data(self):
        """
        Load data from database to display on overlay
        :param word_list:
        :return:
        """
        self.dict_to_word_obj()
        self.dataOlv.SetObjects(self.words)

    def add_new_data(self, new_word):
        """
        Add a record to data overlay
        :param new_word:
        :return:
        """
        # check whether new word exists or is blank
        progress_max = 100
        progress_dlg = wx.ProgressDialog('Connecting to servers...', 'Time remaining', progress_max,
                                         style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_AUTO_HIDE)
        progress_dlg.Update(0)
        w = Word(value=new_word)
        if new_word not in self.word_list.keys() and new_word != "":
            word_def = w.get_definition()
            progress_dlg.Update(30)
            if word_def is not '':
                self.word_list[new_word] = word_def
                # save new word to database
                self.dict_db.save(self.word_list)
                progress_dlg.Update(50)
                self.num_word += 1
                word_def_lines = self.normalize_def_lines(word_def)
                word_def_line = self.normalize_def_line(word_def_lines)
                self.words.append(WordView(self.num_word, new_word, word_def_line))
                self.word_list_view[new_word] = word_def_lines
                # display new word on overlay
                self.dataOlv.SetObjects(self.words)
                progress_dlg.Update(70)
        # get new word pronunciation
        w.get_pronunciation()
        self.set_columns()  # update sound column
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
            ColumnDefn('Word', 'left', 100, 'value'),
            ColumnDefn('Definition', 'left', 550, 'definition'),
            ColumnDefn('', 'center', 20, 'music', imageGetter=image_getter)
        ])

        self.dataOlv.SetObjects(self.words)

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
            for line in self.word_list_view[obj.value]:
                word_def += line.decode('utf-8') + '\n'
            word_def += '-------------------------------------------\n'
        msg_box = wx.MessageDialog(None, word_def, 'Word Definition', style=wx.OK | wx.ICON_INFORMATION)
        msg_box.ShowModal()