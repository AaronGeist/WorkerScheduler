# coding=utf-8
__author__ = 'yzhou7'

import sys
import wx
from src.UI.MainWindow import MainWindow

sys.setdefaultencoding('utf-8')

app = wx.App(False)
frame = MainWindow(None, u'排班助手V1')
app.MainLoop()
