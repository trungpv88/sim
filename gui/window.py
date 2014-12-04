__author__ = 'trungpv'
import wx
from word.word import Word
from data_view import MainPanel, WordView


class WindowManager(wx.Frame):
    """
    Some code for controls based on the wxPython video tutorial of Sentdex:
    https://www.youtube.com/channel/UCfzlCWGWYyIQ0aLC5w48gBQ
    """
    def __init__(self, parent, title, word_list, dict_db):
        super(WindowManager, self).__init__(parent, title=title, size=(800, 600))
        self.CenterOnScreen()
        self.word_list = word_list
        self.dict_db = dict_db
        self.panel = MainPanel(self, self.word_list)
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
        """
        Event raises when quit menu bar button is clicked
        :param e:
        :return:
        """
        yes_no_box = wx.MessageDialog(None, 'Are you sure you want to quit this application?', 'Sim',  wx.YES_NO)
        if yes_no_box.ShowModal() == wx.ID_YES:
            self.Close()

    def add_word(self, e):
        """
        Event raises when add word button is clicked
        :param e:
        :return:
        """
        name_box = wx.TextEntryDialog(None, 'Please enter a new word: ', 'Sim', '')
        if name_box.ShowModal() == wx.ID_OK:
            new_word = name_box.GetValue()
            # check whether new word exists or is blank
            if new_word not in self.word_list.keys() and new_word != "":
                w = Word(value=new_word)
                word_def = w.get_definition()
                if word_def is not "":
                    self.word_list[new_word] = word_def
                    # save new word to database
                    self.dict_db.save(self.word_list)
                    self.num_word += 1
                    # display new word on overlay
                    self.panel.add_new_data(WordView(self.num_word, new_word, word_def))
                # get new word pronunciation
                w.get_pronunciation()