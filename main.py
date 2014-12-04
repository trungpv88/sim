#!/usr/bin/env python

"""
Learning english application
"""

import wx
from dictionary.database import DataBase
from gui.window import WindowManager

if __name__ == "__main__":
    print __doc__
    dict_db = DataBase()
    word_list = dict_db.load()

    app = wx.App()
    window_manager = WindowManager(None, title="Sim", word_list=word_list, dict_db=dict_db)
    app.MainLoop()