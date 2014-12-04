__author__ = 'trungpv'
from ObjectListView import ObjectListView, ColumnDefn
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
    def __init__(self, parent, word_list):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
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
        self.load_data(word_list)

    def dict_to_word_obj(self, word_list):
        """
        Convert from dictionary to WordView object
        :param word_list:dictionary
        :return:
        """
        word_id = 1
        for k, v in word_list.items():
            tmp_obj = WordView(word_id, k, v.split('\n')[0])
            self.words.append(tmp_obj)
            word_id += 1

    def load_data(self, word_list):
        """
        Load data from database to display on overlay
        :param word_list:
        :return:
        """
        self.dict_to_word_obj(word_list)
        self.dataOlv.SetObjects(self.words)

    def add_new_data(self, new_word):
        """
        Add a record to data overlay
        :param new_word:
        :return:
        """
        self.words.append(new_word)
        self.dataOlv.SetObjects(self.words)

    def set_columns(self):
        """
        Column design for data overlay
        :return:
        """
        self.dataOlv.SetColumns([
            ColumnDefn('No', 'center', 50, 'id'),
            ColumnDefn('Word', 'left', 100, 'value'),
            ColumnDefn('Definition', 'left', 700, 'definition')
        ])
        self.dataOlv.SetObjects(self.words)