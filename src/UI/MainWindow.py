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
    '''����һ��������'''

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

        # mnuclear = menufile.Append(wx.ID_CLEAR, '�����������', '�����������')
        # mnuimport = menufile.Append(wx.ID_ADD, '��������', '�����ƶ��ļ���ʽ������')
        # mnuabout = menufile.Append(wx.ID_ABOUT, '����', '���ڱ�����')
        mnuexit = menufile.Append(wx.ID_EXIT, '�˳�', '�˳�����')

        # TODO ��������

        menubar.Append(menufile, '�ļ�')

        # self.Bind(wx.EVT_MENU, self.onImport, mnuimport)
        # self.Bind(wx.EVT_MENU, self.onClear, mnuclear)
        # self.Bind(wx.EVT_MENU, self.onAbout, mnuabout)
        self.Bind(wx.EVT_MENU, self.onExit, mnuexit)

        self.SetMenuBar(menubar)

    def setupPanel(self):

        nb = wx.Notebook(self)
        # self.buyerPanel = BuyerPanel(nb)
        # nb.AddPage(self.buyerPanel, "�����Ű�", select=True)
        nb.AddPage(SellerPanel(nb), '�����Ű��㷨��ʾ')

    def onAbout(self, evt):
        '''���about���¼���Ӧ'''
        dlg = wx.MessageDialog(self, '΢�ź�shakazxx', '����', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def onExit(self, evt):
        '''����˳�'''
        self.Close(True)

    def onImport(self, evt):
        dialog = wx.FileDialog(self, "ѡ��Ҫ����������ļ�", os.getcwd(), style=wx.OPEN, wildcard="*.txt")
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

                wx.MessageBox("�������ݳɹ�", "��������", style=wx.OK | wx.ICON_EXCLAMATION)
            except:
                wx.MessageBox("��������ʧ�ܣ��������ݸ�ʽ", "��������", style=wx.OK | wx.ICON_EXCLAMATION)

    def onClear(self, evt):
        pass
