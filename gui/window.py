__author__ = 'trungpv'
import wx
import  wx.calendar
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
        self.panel = MainPanel(self, word_list, dict_db)
        self.basic_gui()

    def basic_gui(self):
        self.menu_design()
        self.tool_bar_design()
        self.tool_strip_design()
        self.Show(True)

    def menu_design(self):
        menu_bar = wx.MenuBar()

        file_btn = wx.Menu()
        help_btn = wx.Menu()

        exit_item = wx.MenuItem(file_btn, wx.ID_EXIT, 'Exit', '...')
        file_btn.AppendItem(exit_item)
        self.Bind(wx.EVT_MENU, self.quit, exit_item)
        about_item = wx.MenuItem(help_btn, wx.ID_ABOUT, 'About', '...')
        help_btn.AppendItem(about_item)
        self.Bind(wx.EVT_MENU, self.about, about_item)
        guide_item = wx.MenuItem(help_btn, wx.ID_HELP, 'Help Topic', '...')
        help_btn.AppendItem(guide_item)
        self.Bind(wx.EVT_MENU, self.guide, guide_item)

        menu_bar.Append(file_btn, '&File')
        menu_bar.Append(help_btn, '&Help')

        self.SetMenuBar(menu_bar)

    def tool_bar_design(self):
        tool_bar = self.CreateToolBar()
        add_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Add', wx.Bitmap('icon/add_word.ico'), shortHelp='Add new word')
        play_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Play',wx.Bitmap('icon/play_pronunciation.ico'),
                                              shortHelp='Play word pronunciation')
        define_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Definition', wx.Bitmap('icon/view_definition.ico'),
                                                shortHelp='View word definitions')
        language_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Languages', wx.Bitmap('icon/dictionary.ico'),
                                                  shortHelp='Change learning language')
        calendar_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Calendar', wx.Bitmap('icon/calendar.ico'),
                                                  shortHelp='Track learning')
        test_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Test', wx.Bitmap('icon/test.ico'),
                                              shortHelp='Test your vocabulary')
        setting_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Setting', wx.Bitmap('icon/setting.ico'),
                                                 shortHelp='Configure servers')

        tool_bar.Realize()
        self.Bind(wx.EVT_TOOL, self.add_word, add_tool_btn)
        self.Bind(wx.EVT_TOOL, self.panel.play_pronunciation, play_tool_btn)
        self.Bind(wx.EVT_TOOL, self.panel.view_definition, define_tool_btn)
        self.Bind(wx.EVT_TOOL, self.change_language, language_tool_btn)
        self.Bind(wx.EVT_TOOL, self.track_learning, calendar_tool_btn)
        self.Bind(wx.EVT_TOOL, self.test_vocabulary, test_tool_btn)
        self.Bind(wx.EVT_TOOL, self.configure_server, setting_tool_btn)

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

    def about(self, e):
        """
        Event raises when about menu bar button is clicked
        :param e:
        :return:
        """
        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon('icon/logo.png', wx.BITMAP_TYPE_PNG))
        info.SetName('Sim')
        info.SetVersion('1.0')
        sim_description = """
        Sim is an cross-platform application (support for Windows and Linux) helping user learn
        vocabulary. The new words are imported automatically from google search (for pronunciation)
        and website: http://www.oxforddictionaries.com (for definition).
        It's developed in python 2.7 with some modules such as pygame, pydub (for sound), wxPython (for GUI),
        ffmpeg (dependency) ... The set of icons is found in: http://www.fatcow.com/ """
        sim_license = """
        Sim is free software; you can redistributeit and/or modify it under the terms of the GNU General Public
        License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any
        later version. """
        info.SetDescription(sim_description)
        info.SetCopyright('(C) 2014 Pham Van Trung')
        info.SetWebSite('https://github.com/trungpv88')
        info.AddDeveloper('trungpv88@gmail.com')
        info.SetLicence(sim_license)
        wx.AboutBox(info)

    def guide(self, e):
        print 'help'

    def add_word(self, e):
        """
        Event raises when add word button is clicked
        :param e:
        :return:
        """
        name_box = wx.TextEntryDialog(None, 'Please enter a new word: ', 'Sim', '')
        if name_box.ShowModal() == wx.ID_OK:
            new_word = name_box.GetValue()
            self.panel.add_new_data(new_word)

    def change_language(self, e):
        choose_language = wx.SingleChoiceDialog(None, 'Choose your learning language:', 'Language',
                                                ['English', 'French'])
        if choose_language.ShowModal() == wx.ID_OK:
            print choose_language.GetStringSelection()

    def track_learning(self, e):
        wx.calendar.CalendarCtrl(self, -1, wx.DateTime_Now(), pos=(25, 50),
                                 style=wx.calendar.CAL_SHOW_HOLIDAYS | wx.calendar.CAL_SUNDAY_FIRST |
                                       wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)

    def test_vocabulary(self, e):
        print 'x'

    def configure_server(self, e):
        print 'y'