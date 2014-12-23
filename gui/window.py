import wx
from data_view import MainPanel
from tool_bar import ToolBar
from menu_bar import MenuBar
from status_bar import StatusBar


class WindowManager(wx.Frame):
    """
    Some code for controls based on the wxPython video tutorial of Sentdex:
    https://www.youtube.com/channel/UCfzlCWGWYyIQ0aLC5w48gBQ
    """
    def __init__(self, parent, title):
        super(WindowManager, self).__init__(parent, title=title, size=(800, 600),
                                            style=wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.CAPTION | wx.SYSTEM_MENU)
        # self.SetIcon(wx.Icon('icon/app-logo.ico'))
        self.CenterOnScreen()
        self.status_bar = StatusBar(self)
        self.panel = MainPanel(self, self.status_bar)
        self.tool_bar = ToolBar(self)
        self.menu_bar = MenuBar(self, self.panel)
        self.basic_gui()

    def basic_gui(self):
        """
        GUI design for main screen
        :return:
        """
        self.menu_design()
        self.tool_bar_design()
        self.Show(True)

    def menu_design(self):
        """
        Design buttons on menu bar
        :return:
        """
        menu_bar = wx.MenuBar()
        file_btn = wx.Menu()
        help_btn = wx.Menu()

        # 'New' menu button
        new_item = wx.MenuItem(file_btn, wx.ID_NEW, 'New...')
        new_item.SetBitmap(wx.Bitmap('icon/new_db.ico'))
        file_btn.AppendItem(new_item)
        self.Bind(wx.EVT_MENU, self.menu_bar.new, new_item)
        # 'Open' menu button
        open_item = wx.MenuItem(file_btn, wx.ID_OPEN, 'Open...')
        open_item.SetBitmap(wx.Bitmap('icon/load_db.ico'))
        file_btn.AppendItem(open_item)
        self.Bind(wx.EVT_MENU, self.menu_bar.open, open_item)
        # 'Save' menu button
        save_item = wx.MenuItem(file_btn, wx.ID_ANY, 'Save...')
        save_item.SetBitmap(wx.Bitmap('icon/save_db.ico'))
        file_btn.AppendItem(save_item)
        self.Bind(wx.EVT_MENU, self.menu_bar.save, save_item)
        # 'Save As' menu button
        save_as_item = wx.MenuItem(file_btn, wx.ID_ANY, 'Save As...')
        save_as_item.SetBitmap(wx.Bitmap('icon/save_as_db.ico'))
        file_btn.AppendItem(save_as_item)
        self.Bind(wx.EVT_MENU, self.menu_bar.save_as, save_as_item)
        # 'Exit' menu button
        exit_item = wx.MenuItem(file_btn, wx.ID_ANY, 'Exit')
        exit_item.SetBitmap(wx.Bitmap('icon/exit.ico'))
        file_btn.AppendItem(exit_item)
        self.Bind(wx.EVT_MENU, self.menu_bar.quit, exit_item)
        # 'About' menu button
        about_item = wx.MenuItem(help_btn, wx.ID_ABOUT, 'About')
        about_item.SetBitmap(wx.Bitmap('icon/about.png'))
        help_btn.AppendItem(about_item)
        self.Bind(wx.EVT_MENU, self.menu_bar.about, about_item)
        # 'Help' menu button
        guide_item = wx.MenuItem(help_btn, wx.ID_HELP, 'Help Topic')
        guide_item.SetBitmap(wx.Bitmap('icon/help.ico'))
        help_btn.AppendItem(guide_item)
        self.Bind(wx.EVT_MENU, self.menu_bar.guide, guide_item)

        menu_bar.Append(file_btn, '&System')
        menu_bar.Append(help_btn, '&Help')
        self.SetMenuBar(menu_bar)

    def tool_bar_design(self):
        """
        Design buttons on tool bar
        :return:
        """
        tool_bar = self.CreateToolBar()
        add_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Add', wx.Bitmap('icon/add_word.ico'), shortHelp='Add new word')
        delete_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Delete', wx.Bitmap('icon/delete_word.ico'),
                                                shortHelp='Delete a word')
        play_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Play', wx.Bitmap('icon/play_pronunciation.ico'),
                                              shortHelp='Play word pronunciation')
        define_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Definition', wx.Bitmap('icon/view_definition.ico'),
                                                shortHelp='View word definitions')
        calendar_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Calendar', wx.Bitmap('icon/calendar.ico'),
                                                  shortHelp='Track learning')
        test_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Test', wx.Bitmap('icon/test.ico'),
                                              shortHelp='Test your vocabulary')
        phrase_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Phrase', wx.Bitmap('icon/phrase.ico'),
                                                shortHelp='View ordinary phrases')
        setting_tool_btn = tool_bar.AddLabelTool(wx.ID_ANY, 'Setting', wx.Bitmap('icon/setting.ico'),
                                                 shortHelp='View configuration servers')

        tool_bar.Realize()
        self.Bind(wx.EVT_TOOL, self.panel.add_word, add_tool_btn)
        self.Bind(wx.EVT_TOOL, self.panel.delete_word, delete_tool_btn)
        self.Bind(wx.EVT_TOOL, self.panel.play_pronunciation, play_tool_btn)
        self.Bind(wx.EVT_TOOL, self.panel.view_definition, define_tool_btn)
        self.Bind(wx.EVT_TOOL, self.tool_bar.track_learning, calendar_tool_btn)
        self.Bind(wx.EVT_TOOL, self.tool_bar.test_vocabulary, test_tool_btn)
        self.Bind(wx.EVT_TOOL, self.tool_bar.view_phrases, phrase_tool_btn)
        self.Bind(wx.EVT_TOOL, self.tool_bar.configure_server, setting_tool_btn)