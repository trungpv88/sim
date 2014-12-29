#!/usr/bin/env python

"""
Learning languages (english and french) application
"""

import wx
from gui.window import WindowManager

if __name__ == "__main__":
    print __doc__

    app = wx.App(redirect=False)
    window_manager = WindowManager(None, title="Sim")
    app.MainLoop()