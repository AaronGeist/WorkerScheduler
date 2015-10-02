# coding=utf-8
import os
from src.DAL.DailyDataDAL import DailyDataDAL
from src.Util.TimeUtil import TimeUtil

__author__ = 'yzhou7'

import wx

from src.UI.BuyerPanel import BuyerPanel
from src.UI.SellerPanel import SellerPanel
from src.SystemInitializer import SystemInitializer


# this class provides entry point for all clients
# it should have the following functions:
# 1. view all buyers's data
# 2. query single buyer'data
# 3. clean up out-of-data data

class MainWindow(wx.Frame):
    '''定义一个窗口类'''

    def __init__(self, parent, title):
        super(MainWindow, self).__init__(parent, title=title, size=(800, 600))
        self.initUI()
        self.Show(True)

    def initUI(self):
        self.setupMenuBar()
        # menu bar should be drawn first
        # or panel sizer/layout will work wrongly
        self.setupPanel()

    def setupMenuBar(self):
        self.CreateStatusBar()

        menubar = wx.MenuBar()
        menufile = wx.Menu()

        # mnuclear = menufile.Append(wx.ID_CLEAR, '清理过期数据', '清理过期数据')
        # mnuimport = menufile.Append(wx.ID_ADD, '导入数据', '导入制定文件格式的数据')
        # mnuabout = menufile.Append(wx.ID_ABOUT, '关于', '关于本程序')
        mnuexit = menufile.Append(wx.ID_EXIT, u'退出', u'退出程序')

        # TODO 数据整理

        menubar.Append(menufile, u'文件')

        # self.Bind(wx.EVT_MENU, self.onImport, mnuimport)
        # self.Bind(wx.EVT_MENU, self.onClear, mnuclear)
        # self.Bind(wx.EVT_MENU, self.onAbout, mnuabout)
        self.Bind(wx.EVT_MENU, self.onExit, mnuexit)

        self.SetMenuBar(menubar)

    def setupPanel(self):

        nb = wx.Notebook(self)
        # self.buyerPanel = BuyerPanel(nb)
        # nb.AddPage(self.buyerPanel, "智能排班", select=True)
        nb.AddPage(SellerPanel(nb), u'智能排班算法演示')

    def onAbout(self, evt):
        '''点击about的事件响应'''
        dlg = wx.MessageDialog(self, u'微信号shakazxx', u'关于', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def onExit(self, evt):
        '''点击退出'''
        self.Close(True)

    def onImport(self, evt):
        dialog = wx.FileDialog(self, u"选择要导入的数据文件", os.getcwd(), style=wx.OPEN, wildcard="*.txt")
        if dialog.ShowModal() == wx.ID_OK:
            self.onFileRead(dialog.GetPath())
            # self.SetTitle(self.filename)
        dialog.Destroy()

    def onFileRead(self, filePath):
        if filePath:
            try:
                lines = DailyDataDAL.readAll(filePath)
                dailyData = DailyDataDAL.parse(lines, TimeUtil.getToday())
                DailyDataDAL.persistAll(dailyData)

                newDailyData = DailyDataDAL.fetchAllByDate(TimeUtil.getToday())
                self.buyerPanel.updateGrid(newDailyData.toStringList())

                wx.MessageBox(u"导入数据成功", u"导入数据", style=wx.OK | wx.ICON_EXCLAMATION)
            except:
                wx.MessageBox(u"导入数据失败，请检测数据格式", u"导入数据", style=wx.OK | wx.ICON_EXCLAMATION)

    def onClear(self, evt):
        pass
