# coding=utf-8
import os
import math

import wx
from src.Util.FileUtil import FileUtil
from src.SystemInitializer import SystemInitializer
from src.View.GroupManagementPanel import GroupManagementPanel
from src.View.UserManagementPanel import UserManagementPanel
from src.View.SellerPanel import SellerPanel

__author__ = 'yzhou7'

'''
Entry window for all features
'''

class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        super(MainWindow, self).__init__(parent, title=title, size=(1024, 800))
        if not SystemInitializer.initialize():
            wx.MessageBox(u'试用时间已经超过，请联系软件作者，微信号shakazxx')
            self.Close(True)
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

        nb = wx.Notebook(self, style=wx.NB_LEFT)
        self.sellerPanel = SellerPanel(nb)
        nb.AddPage(self.sellerPanel, u'智能排班')
        self.userManagementPanel = UserManagementPanel(nb)
        nb.AddPage(self.userManagementPanel, u'员工管理')
        self.groupManagementPanel = GroupManagementPanel(nb)
        nb.AddPage(self.groupManagementPanel, u'班组管理')

        nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNBPageChanged)

        # nb = wx.Toolbook(self, wx.BK_DEFAULT)
        # self.sellerPanel = SellerPanel(nb)
        #
        # il = wx.ImageList(48, 48)
        # bmp0 = wx.Image('.\Resource\panda.ico', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        # bmp1 = wx.Image('.\Resource\panda.ico', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        # bmp2 = wx.Image('.\Resource\panda.ico', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        # index0 = il.Add(bmp0)
        # nb.AddPage(self.sellerPanel, u'智能排班', imageId=index0)
        # nb.AddPage(UserManagementPanel(nb), u'员工管理', imageId=index0)
        # nb.AddPage(GroupManagementPanel(nb), u'班组管理', imageId=index0)

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
                workerList = FileUtil.readAll(filePath)

                self.sellerPanel.updateGrid(list(map(lambda worker: [worker, '0'], workerList)))
                self.sellerPanel.workloadInput.SetValue(str(math.ceil(float(len(workerList)) * 2 / 3)))

                wx.MessageBox(u"导入数据成功", u"导入数据", style=wx.OK | wx.ICON_EXCLAMATION)
            except Exception as e:
                wx.MessageBox(u"导入数据失败，请检测数据格式，并保证文件为UTF-8格式", u"导入数据", style=wx.OK | wx.ICON_EXCLAMATION)
                # wx.MessageBox(str(e))

    def OnNBPageChanged(self, evt):
        if evt.GetSelection() == 1:
            # 更新页面
            self.userManagementPanel.refreshGrid()
            self.userManagementPanel.refreshGroupList()
