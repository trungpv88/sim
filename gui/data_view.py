__author__ = 'trungpv'
from ObjectListView import ObjectListView, ColumnDefn
from word.word import Word
import wx


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
        self.w_l = {}
        self.normalize_word_list(word_list)
        self.dict_db = dict_db
        self.num_word = len(self.word_list)
        self.words = []
        # data overlay in list view
        self.dataOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.set_columns()
        self.dataOlv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK
        # data overlay design
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.dataOlv, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)
        # load data to overlay
        self.load_data()

    def normalize_word_list(self, word_list):
        """
        Normalize content of word list.
        For example: {'hello': ['1. Hi', '2. Say in meeting']}
        :param word_list:
        :return:
        """
        for k, v in word_list.items():
            lines = v.split('\n')
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
            self.w_l[k] = normal_lines

    def dict_to_word_obj(self):
        """
        Convert from dictionary to WordView object
        :param word_list:dictionary
        :return:
        """
        word_id = 1
        for k, v in self.w_l.items():
            # tmp_obj = WordView(word_id, k, v[0][3:100] + '..')
            def_view = ' '.join(v[0].split()[1:15])  # get 15 first words in definition
            def_view = def_view.translate(None, '.,') + ' ...'  # remove punctuations
            tmp_obj = WordView(word_id, k, def_view)
            self.words.append(tmp_obj)
            word_id += 1

    def load_data(self, ):
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
        if new_word not in self.word_list.keys() and new_word != "":
            w = Word(value=new_word)
            word_def = w.get_definition()
            if word_def is not '':
                self.word_list[new_word] = word_def
                # save new word to database
                self.dict_db.save(self.word_list)
                self.num_word += 1
                self.words.append(WordView(self.num_word, new_word, word_def))
                # display new word on overlay
                self.dataOlv.SetObjects(self.words)
            # get new word pronunciation
            w.get_pronunciation()

    def set_columns(self):
        """
        Column design for data overlay
        :return:
        """
        self.dataOlv.SetColumns([
            ColumnDefn('No', 'center', 50, 'id'),
            ColumnDefn('Word', 'left', 100, 'value'),
            ColumnDefn('Definition', 'left', 600, 'definition')
        ])
        self.dataOlv.SetObjects(self.words)

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
            for line in self.w_l[obj.value]:
                word_def += line.decode('utf-8') + '\n'
            word_def += '-------------------------------------------\n'
        msg_box = wx.MessageDialog(None, word_def, 'Word Definition', style=wx.OK | wx.ICON_INFORMATION)
        msg_box.ShowModal()
