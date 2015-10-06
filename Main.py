# coding=utf-8
__author__ = 'yzhou7'

import wx
from src.UI.MainWindow import MainWindow

app = wx.App(False)
frame = MainWindow(None, u'排班助手V1')
app.MainLoop()
