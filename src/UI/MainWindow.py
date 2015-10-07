# coding=utf-8
import os

import wx
import wx.lib.scrolledpanel as scrolled
from src.DAL.BaseDAL import BaseDAL
from src.UI.SellerPanel import SellerPanel

__author__ = 'yzhou7'

'''
Entry window for all features
'''

class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        super(MainWindow, self).__init__(parent, title=title, size=(1024, 800))

        # self.panel_2 = scrolled.ScrolledPanel(self)
        # self.panel_2.SetVirtualSize(500, 500)
        # self.panel_2.SetScrollRate(20,20)

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

        menubar.Append(menufile, u'文件')

        self.Bind(wx.EVT_MENU, self.onImport, mnuimport)
        self.Bind(wx.EVT_MENU, self.onExit, mnuexit)

        self.SetMenuBar(menubar)

    def setupPanel(self):

        nb = wx.Notebook(self)
        self.sellerPanel = SellerPanel(nb)
        nb.AddPage(self.sellerPanel, u'智能排班算法演示')
        # self.SetScrollbar(wx.VERTICAL, 0, 600, 1800, True)

    def onAbout(self, evt):
        dlg = wx.MessageDialog(self, u'微信号shakazxx', u'关于', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def onExit(self, evt):
        self.Close(True)

    def onImport(self, evt):
        dialog = wx.FileDialog(self, u"选择要导入的数据文件",
                               os.getcwd(), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST, wildcard="*.txt")
        if dialog.ShowModal() == wx.ID_OK:
            self.onFileRead(dialog.GetPath())
        dialog.Destroy()

    def onFileRead(self, filePath):
        if filePath:
            try:
                workerList = BaseDAL.readAll(filePath)

                self.sellerPanel.updateGrid(list(map(lambda worker: [worker, '0'], workerList)))

                wx.MessageBox(u"导入数据成功", u"导入数据", style=wx.OK | wx.ICON_EXCLAMATION)
            except Exception as e:
                wx.MessageBox(u"导入数据失败，请检测数据格式，并保证文件为UTF-8格式", u"导入数据", style=wx.OK | wx.ICON_EXCLAMATION)
                # wx.MessageBox(str(e))

