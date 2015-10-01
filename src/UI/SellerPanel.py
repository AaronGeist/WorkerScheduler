import os
from src.Strategy.Scheduler import Scheduler
from src.UI.ScheduleData import ScheduleData

__author__ = 'yzhou7'

import wx

from src.DAL.DailyDataDAL import DailyDataDAL
from src.UI.UserData import UserGridData


class SellerPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour("white")
        self.initUI()
        self.Show(True)

    def initUI(self):
        self.vBox = wx.BoxSizer(wx.VERTICAL)

        self.setupDateInput()
        self.displayTodayData()

        self.SetSizer(self.vBox)
        # self.vBox.Layout()

    def setupDateInput(self):

        sizer = wx.GridBagSizer(4, 4)

        workerNumText = wx.StaticText(self, label='������')
        sizer.Add(workerNumText, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.workerNumInput = wx.TextCtrl(self, value='5', style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.workerNumInput, pos=(0, 1),
                  flag=wx.TOP | wx.LEFT, border=12)

        targetDaysText = wx.StaticText(self, label='�Ű�����')
        sizer.Add(targetDaysText, pos=(0, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.tagetDaysInput = wx.TextCtrl(self, value='30', style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.tagetDaysInput, pos=(0, 3),
                  flag=wx.TOP | wx.LEFT, border=12)

        workloadText = wx.StaticText(self, label='ÿ���������')
        sizer.Add(workloadText, pos=(0, 4), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.workloadInput = wx.TextCtrl(self, value='3', style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.workloadInput, pos=(0, 5),
                  flag=wx.TOP | wx.LEFT, border=12)

        minWorkDays = wx.StaticText(self, label='��С������������')
        sizer.Add(minWorkDays, pos=(1, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.minWorkDaysInput = wx.TextCtrl(self, value='3', style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.minWorkDaysInput, pos=(1, 1),
                  flag=wx.TOP | wx.LEFT, border=12)

        maxWorkDaysText = wx.StaticText(self, label='���������������')
        sizer.Add(maxWorkDaysText, pos=(1, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.maxWorkDaysInput = wx.TextCtrl(self, value='5', style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.maxWorkDaysInput, pos=(1, 3),
                  flag=wx.TOP | wx.LEFT, border=12)

        self.vBox.Add(sizer, wx.ALIGN_TOP | wx.ALIGN_LEFT, 10)

    def displayTodayData(self):
        sizer = wx.GridBagSizer(4, 4)

        # set data into data grid
        self.data = UserGridData()
        self.data.InsertRows(list())
        self.grid = wx.grid.Grid(self, size=(300, 300))
        self.grid.SetTable(self.data)
        self.grid.SetColLabelValue(0, 'Ա����')
        self.grid.SetColLabelValue(1, '�ܳ�������')
        self.grid.AutoSize()
        sizer.Add(self.grid, pos=(1, 1), span=(1, 1), flag=wx.EXPAND | wx.TOP, border=5)

        self.data1 = ScheduleData()
        self.data1.InsertRows(list())
        self.grid1 = wx.grid.Grid(self, size=(400, 300))
        self.grid1.SetTable(self.data1)
        self.grid1.AutoSize()
        sizer.Add(self.grid1, pos=(1, 2), span=(1, 1), flag=wx.EXPAND | wx.TOP, border=5)

        self.searchBtn = wx.Button(self, label='��ʼ�Ű�', size=(100, 20))
        sizer.Add(self.searchBtn, pos=(2, 3))
        self.searchBtn.Enable(True)
        self.Bind(wx.EVT_BUTTON, self.onSchedule, self.searchBtn)

        sizer.AddGrowableRow(1)
        self.vBox.Add(sizer, wx.ALIGN_BOTTOM | wx.ALIGN_LEFT, 10)

    def updateGrid(self, rows):
        self.grid.ClearGrid()
        self.data.InsertRows(rows)
        self.grid.SetTable(self.data)
        self.grid.AutoSize()
        self.vBox.Layout()

    def updateGrid1(self, rows):
        self.grid1.ClearGrid()
        self.data1.InsertRows(rows)
        self.grid1.SetTable(self.data1)
        self.grid1.AutoSize()
        self.vBox.Layout()

    def onSchedule(self, evt):
        workers = range(1, int(self.workerNumInput.GetValue()) + 1)
        if not self.checkInput():
            return

        s = Scheduler(workers, self.workloadInput.GetValue(), self.minWorkDaysInput.GetValue(),
                      self.maxWorkDaysInput.GetValue())
        scheduleResult = s.schedule(self.tagetDaysInput.GetValue())

        if scheduleResult.message.strip() != '':
            wx.MessageBox(scheduleResult.message.decode('utf-8', 'ignore'))
        else:
            wx.MessageBox("�Ű�ɹ�")

        result = list()
        for keyValuePair in sorted(scheduleResult.calendar.iteritems(), key=lambda d: d[0]):
            result.append([keyValuePair[0],
                           "    ".join(map(str, map(lambda index: workers[index], keyValuePair[1]))),
                           "��Ϣ����"
                           ])
        self.updateGrid1(result)

        personalTotalWorkDay = scheduleResult.personalTotalWorkDay
        workDayData = list()

        for i in range(0, len(workers)):
            workDayData.append([workers[i], personalTotalWorkDay.get(i, 0)])
        self.updateGrid(workDayData)

    def checkInput(self):
        # try:
        #     workload = int(self.workloadInput.GetValue())
        #     maxRestDay = int(self.minWorkDaysInput.GetValue()) + 1
        #     workers = len(self.data._data)
        #     if (maxRestDay * workload) < workers:
        #         wx.MessageBox("������������Ű����� * ����Ϣ���� + 1��������ڵ�����Ա����")
        #         return False
        # except:
        #     wx.MessageBox("���������������")
        #     return False
        return True

    def onImport(self, evt):
        dialog = wx.FileDialog(self, "ѡ��Ҫ����������ļ�", os.getcwd(), style=wx.OPEN, wildcard="*.txt")
        if dialog.ShowModal() == wx.ID_OK:
            self.onFileRead(dialog.GetPath())
            # self.SetTitle(self.filename)
        dialog.Destroy()

    def onFileRead(self, filePath):
        if filePath:
            # try:
            lines = DailyDataDAL.readAll(filePath)
            self.updateGrid(lines)
            wx.MessageBox("�������ݳɹ�" + ' '.join(lines), "��������", style=wx.OK | wx.ICON_EXCLAMATION)
            # except:
            #     wx.MessageBox("��������ʧ�ܣ��������ݸ�ʽ", "��������", style=wx.OK | wx.ICON_EXCLAMATION)
