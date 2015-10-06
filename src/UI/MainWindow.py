# coding=utf-8
import os

from src.DAL.BaseDAL import BaseDAL

__author__ = 'yzhou7'

import wx

from src.UI.SellerPanel import SellerPanel


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

        mnuimport = menufile.Append(wx.ID_ADD, u'导入员工名单', u'一行一个名字')
        mnuexit = menufile.Append(wx.ID_EXIT, u'退出', u'退出程序')

        # TODO 数据整理

        menubar.Append(menufile, u'文件')

        self.Bind(wx.EVT_MENU, self.onImport, mnuimport)
        self.Bind(wx.EVT_MENU, self.onExit, mnuexit)

        self.SetMenuBar(menubar)

    def setupPanel(self):

        nb = wx.Notebook(self)
        self.sellerPanel = SellerPanel(nb)
        nb.AddPage(self.sellerPanel, u'智能排班算法演示')

    def onAbout(self, evt):
        '''点击about的事件响应'''
        dlg = wx.MessageDialog(self, u'微信号shakazxx', u'关于', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def onExit(self, evt):
        '''点击退出'''
        self.Close(True)

    def onImport(self, evt):
        dialog = wx.FileDialog(self, u"选择要导入的数据文件",
                               os.getcwd(), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST, wildcard="*.txt")
        if dialog.ShowModal() == wx.ID_OK:
            self.onFileRead(dialog.GetPath())
        dialog.Destroy()

    def onFileRead(self, filePath):
        if filePath:
            # try:
            workerList = BaseDAL.readAll(filePath)

            self.sellerPanel.updateGrid(list(map(lambda worker: [worker, '0'], workerList)))

            wx.MessageBox(u"导入数据成功", u"导入数据", style=wx.OK | wx.ICON_EXCLAMATION)
            # except Exception, e:
            #     wx.MessageBox(u"导入数据失败，请检测数据格式，并保证文件为UTF-8格式", u"导入数据", style=wx.OK | wx.ICON_EXCLAMATION)

