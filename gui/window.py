from numpy.numarray.numerictypes import Object

__author__ = 'User'
import wx
from ObjectListView import ObjectListView, ColumnDefn
from word.word import Word


class WindowManager(wx.Frame):
    """
    Some code for controls based on the wxPython video tutorial of Sentdex:
    https://www.youtube.com/channel/UCfzlCWGWYyIQ0aLC5w48gBQ
    """
    def __init__(self, parent, title, word_list, dict_db):
        super(WindowManager, self).__init__(parent, title=title, size=(800, 600))
        self.word_list = word_list
        self.dict_db = dict_db
        self.CenterOnScreen()
        self.panel = MainPanel(self)
        self.panel.load_data(self.word_list)
        self.num_word = len(self.word_list)
        self.basic_gui()

    def basic_gui(self):
        self.menu_design()
        self.tool_bar_design()
        self.tool_strip_design()
        self.Show(True)

    def menu_design(self):
        menu_bar = wx.MenuBar()

        file_btn = wx.Menu()
        about_btn = wx.Menu()

        exit_item = wx.MenuItem(file_btn, wx.ID_EXIT, 'Exit', '...')
        file_btn.AppendItem(exit_item)
        self.Bind(wx.EVT_MENU, self.quit, exit_item)

        menu_bar.Append(file_btn, '&File')
        menu_bar.Append(about_btn, '&About')

        self.SetMenuBar(menu_bar)

    def tool_bar_design(self):
        tool_bar = self.CreateToolBar()
        add_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Add new word', wx.Bitmap('icon/add_word.ico'))
        tool_bar.Realize()
        self.Bind(wx.EVT_TOOL, self.add_word, add_tool_btn)

    def tool_strip_design(self):
        print ''

    def quit(self, e):
        yes_no_box = wx.MessageDialog(None, 'Are you sure you want to quit this application?', 'Sim',  wx.YES_NO)
        if yes_no_box.ShowModal() == wx.ID_YES:
            self.Close()

    def add_word(self, e):
        name_box = wx.TextEntryDialog(None, 'Please enter a new word: ', 'Sim', '')
        if name_box.ShowModal() == wx.ID_OK:
            new_word = name_box.GetValue()
            w = Word(value=new_word)
            if new_word not in self.word_list.keys():
                word_def = w.get_definition()
                if word_def is not "":
                    self.word_list[new_word] = word_def
                    self.dict_db.save(self.word_list)
                    self.num_word += 1
                    self.panel.update_data([{'id': self.num_word, 'value': new_word, 'definition': word_def}])
            w.get_pronunciation()


class WordView(object):
    def __init__(self, id, value, definition):
        self.id = id
        self.value = value
        self.definition = definition


class MainPanel(wx.Panel):
    """
    http://www.blog.pythonlibrary.org/2009/12/23/wxpython-using-objectlistview-instead-of-a-listctrl/
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.words = []
        self.dataOlv = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.set_columns()

        self.dataOlv.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.dataOlv, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def convert_to_word_obj(self, word_list):
        word_obj = []
        word_id = 1
        for k, v in word_list.items():
            tmp_obj = {}
            tmp_obj['id'] = word_id
            tmp_obj['value'] = k
            tmp_obj['definition'] = v.split('\n')[0]
            word_obj.append(tmp_obj)
            word_id += 1
        return word_obj

    def load_data(self, word_list):
        self.words += self.convert_to_word_obj(word_list)
        self.dataOlv.SetObjects(self.words)

    def update_data(self, new_word):
        self.dataOlv.SetObjects(self.words + new_word)

    def set_columns(self, data=None):
        self.dataOlv.SetColumns([
            ColumnDefn('No', 'center', 50, 'id'),
            ColumnDefn('Word', 'left', 100, 'value'),
            ColumnDefn('Definition', 'left', 700, 'definition')
        ])
        self.dataOlv.SetObjects(self.words)