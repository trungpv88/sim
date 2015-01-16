#----------------------------------------------------------------------------
# Change log:
# 2014/12/24  - Version 1.0
# 2015/01/16  - Version 1.1
#----------------------------------------------------------------------------
# Goal:
# - Handle about, help and quit clicked button event
# - Manipulate database: new, open, save

import wx
import wx.html as html
import shutil
import os
import ntpath
from dictionary.database import DB_PATH


class MenuBar(object):
    def __init__(self, parent, panel):
        self.parent = parent
        self.panel = panel

    def open_db(self, title, op_type):
        yes_no_msg_dlg = wx.MessageDialog(None, title, 'Sim', style=wx.YES_NO | wx.ICON_EXCLAMATION)
        result_dlg = yes_no_msg_dlg.ShowModal()
        if result_dlg == wx.ID_YES:
            self.save_db()
        if result_dlg == wx.ID_NO:
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
        if op_type == 'new':
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            self.panel.new_panel()
        if op_type == 'load':
            open_dlg = wx.FileDialog(self.parent, 'Open database', '', '', 'pkl files (*.pkl)|*.pkl',
                                     wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if open_dlg.ShowModal() == wx.ID_OK:
                db_name = ntpath.basename(open_dlg.GetPath())
                shutil.copy(db_name, DB_PATH)
            self.panel.new_panel()
            open_dlg.Destroy()
        yes_no_msg_dlg.Destroy()

    def new(self, e):
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        self.open_db(title='Would you like to save current data before open new database?', op_type='new')

    def open(self, e):
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        self.open_db(title='Would you like to save current data before load a database?', op_type='load')

    @staticmethod
    def save_db():
        file_name_box = wx.TextEntryDialog(None, 'Please enter database name: ', 'Sim', '')
        while file_name_box.ShowModal() == wx.ID_OK:
            new_word = file_name_box.GetValue()
            if new_word != '':
                new_db = new_word + '.pkl'
                if not os.path.exists(new_db):
                    shutil.copy(DB_PATH, new_db)
                    break
                else:
                    dlg = wx.MessageDialog(None, 'File name exists. Would you want to overwrite this file?', 'Sim',
                                           style=wx.YES_NO | wx.ICON_EXCLAMATION)
                    if dlg.ShowModal() == wx.ID_YES:
                        if os.path.exists(new_db):
                            os.remove(new_db)
                        shutil.copy(DB_PATH, new_db)
                        break
            else:
                dlg = wx.MessageDialog(None, 'Empty file name!!', 'Sim',
                                       style=wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
        file_name_box.Destroy()

    def save(self, e):
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        self.save_db()

    def quit(self, e):
        """
        Event raises when quit menu bar button is clicked
        :param e:
        :return:
        """
        print 'Clicked button: %s' % (e.GetEventObject())
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
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        info = wx.AboutDialogInfo()
        info.SetIcon(wx.Icon('icon/logo.png', wx.BITMAP_TYPE_PNG))
        info.SetName('Sim')
        info.SetVersion('1.0')
        sim_description = """
        Sim is an cross-platform application (support for Windows and Linux) helping users learn vocabulary and manage
        their english-french learning period. The new words are imported automatically from google search (to get
        pronunciation and images) and website: http://www.oxforddictionaries.com (to get word definition). It's
        developed in python 2.7 using some modules such as pygame, pydub (for sound), wxPython (version 2.8x
        recommended) (for GUI), ffmpeg (dependency) ... The free set of icons is found in: http://www.fatcow.com/ """
        sim_license = """
        Sim is free software; you can redistribute it and/or modify it under the terms of the GNU
        General Public License as published by the Free Software Foundation;
        either version 2 of the License, or (at your option) any later version. """
        info.SetDescription(sim_description)
        info.SetCopyright('(C) 2014 Pham Van Trung')
        info.SetWebSite('http://vn.linkedin.com/in/trungpv88')
        info.AddDeveloper('trungpv88@gmail.com')
        info.SetLicence(sim_license)
        wx.AboutBox(info)

    def guide(self, e):
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        HelpDialog(self.parent, 'Help')


class HelpDialog(wx.Dialog):
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(640, 480))
        self.design_dialog()
        self.ShowModal()

    def design_dialog(self):
        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        close_btn = wx.Button(self, -1, 'OK', size=(80, 25))
        close_btn.Bind(wx.EVT_BUTTON, self.on_close)
        help_html = html.HtmlWindow(self, -1, style=wx.NO_BORDER)
        help_html.LoadPage('help.html')
        dialog_sizer.Add(help_html, 1, wx.ALL | wx.EXPAND, border=10)
        dialog_sizer.Add(close_btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        self.SetSizer(dialog_sizer)

    def on_close(self, e):
        print 'Clicked button: %s' % (e.GetEventObject().GetLabel())
        self.Destroy()