import wx
import wx.html as html


class MenuBar(object):
    def __init__(self, parent):
        self.parent = parent

    def new(self, e):
        print ''

    def open(self, e):
        print ''

    def save(self, e):
        print ''

    def save_as(self, e):
        print ''

    def quit(self, e):
        """
        Event raises when quit menu bar button is clicked
        :param e:
        :return:
        """
        yes_no_box = wx.MessageDialog(None, 'Are you sure you want to quit this application?', 'Sim',  wx.YES_NO)
        if yes_no_box.ShowModal() == wx.ID_YES:
            self.parent.Close()

    @staticmethod
    def about(e):
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
        Sim is an cross-platform application (support for Windows and Linux) helping user learn vocabulary.
        The new words are imported automatically from google search (for pronunciation) and website:
        http://www.oxforddictionaries.com (for definition). It's developed in python 2.7 with some modules such as
        pygame, pydub (for sound), wxPython (for GUI), ffmpeg (dependency) ...
        The set of icons is found in: http://www.fatcow.com/ """
        sim_license = """
        Sim is free software; you can redistribute it and/or modify it under the terms of the GNU
        General Public License as published by the Free Software Foundation;
        either version 2 of the License, or (at your option) any later version. """
        info.SetDescription(sim_description)
        info.SetCopyright('(C) 2014 Pham Van Trung')
        info.SetWebSite('https://github.com/trungpv88')
        info.AddDeveloper('trungpv88@gmail.com')
        info.SetLicence(sim_license)
        wx.AboutBox(info)

    def guide(self, e):
        HelpDialog(self.parent, 'Help')


class HelpDialog(wx.Dialog):
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(640, 480))
        self.design_dialog()
        self.ShowModal()

    def design_dialog(self):
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        help_html = html.HtmlWindow(self, -1, style=wx.NO_BORDER)
        help_html.LoadPage('help.html')
        dialog_sizer.Add(help_html, 1, wx.ALL | wx.EXPAND, border=10)
        self.SetSizer(dialog_sizer)