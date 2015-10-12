# coding=utf-8
import wx

from src.Constants import Constants
from src.View.MainWindow import MainWindow

__author__ = 'yzhou7'

app = wx.App(False)
frame = MainWindow(None, Constants.MAIN_WINDOW_TITLE)
app.MainLoop()
