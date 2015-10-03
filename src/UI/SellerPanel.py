# coding=utf-8
import os
from src.Strategy.Scheduler import Scheduler
from src.UI.ScheduleData import ScheduleData
from src.Util.TimeUtil import TimeUtil
from src.DAL.BaseDAL import BaseDAL

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

        workloadText = wx.StaticText(self, label=u'每天出勤人数')
        sizer.Add(workloadText, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.workloadInput = wx.TextCtrl(self, value='12', style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.workloadInput, pos=(0, 1),
                  flag=wx.TOP | wx.LEFT, border=12)

        minWorkDays = wx.StaticText(self, label=u'最小连续出勤天数')
        sizer.Add(minWorkDays, pos=(1, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.minWorkDaysInput = wx.TextCtrl(self, value='3', style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.minWorkDaysInput, pos=(1, 1),
                  flag=wx.TOP | wx.LEFT, border=12)

        maxWorkDaysText = wx.StaticText(self, label=u'最大连续出勤天数')
        sizer.Add(maxWorkDaysText, pos=(1, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.maxWorkDaysInput = wx.TextCtrl(self, value='6', style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.maxWorkDaysInput, pos=(1, 3),
                  flag=wx.TOP | wx.LEFT, border=12)

        startDate = wx.StaticText(self, label=u'开始日期')
        sizer.Add(startDate, pos=(2, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.startDateInput = wx.TextCtrl(self, value=TimeUtil.getToday(), style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT, self.OnEnterDate, self.startDateInput)
        sizer.Add(self.startDateInput, pos=(2, 1),
                  flag=wx.TOP | wx.LEFT, border=12)

        endDate = wx.StaticText(self, label=u'结束日期')
        sizer.Add(endDate, pos=(2, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.endDateInput = wx.TextCtrl(self, value=TimeUtil.getToday(), style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT, self.OnEnterDate, self.endDateInput)
        sizer.Add(self.endDateInput, pos=(2, 3),
                  flag=wx.TOP | wx.LEFT, border=12)

        self.warnMsg = wx.StaticText(self, label=u'非法日期，请重新输入')
        self.warnMsg.SetForegroundColour('red')
        sizer.Add(self.warnMsg, pos=(2, 4), flag=wx.TOP | wx.LEFT, border=15)
        self.warnMsg.Hide()

        self.scheduleBtn = wx.Button(self, label=u'开始排班', size=(80, 40))
        sizer.Add(self.scheduleBtn, pos=(3, 0), flag=wx.TOP | wx.LEFT | wx.ALIGN_RIGHT, border=12)
        self.scheduleBtn.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.onSchedule, self.scheduleBtn)

        self.exportBtn = wx.Button(self, label=u'导出排班', size=(80, 40))
        sizer.Add(self.exportBtn, pos=(3, 1), flag=wx.TOP | wx.LEFT | wx.ALIGN_RIGHT, border=12)
        self.exportBtn.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.onExport, self.exportBtn)

        self.vBox.Add(sizer, wx.ALIGN_TOP | wx.ALIGN_LEFT, 10)

    def displayTodayData(self):
        sizer = wx.GridBagSizer(4, 4)

        # set data into data grid
        self.data = UserGridData()
        self.data.InsertRows(list())
        self.grid = wx.grid.Grid(self)
        self.grid.SetTable(self.data)
        self.grid.AutoSize()
        sizer.Add(self.grid, pos=(1, 1), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.RIGHT, border=15)

        self.data1 = ScheduleData()
        self.data1.InsertRows(list())
        # self.grid1 = wx.grid.Grid(self, size=(400, 300))
        self.grid1 = wx.grid.Grid(self)
        self.grid1.SetTable(self.data1)
        self.grid1.AutoSize()
        sizer.Add(self.grid1, pos=(1, 2), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(2)
        self.vBox.Add(sizer, wx.ALIGN_BOTTOM | wx.ALIGN_LEFT, 10)

    def updateGrid(self, rows):
        self.grid.ClearGrid()
        rows = map(lambda x: [x[0].decode('utf-8', 'ignore'), x[1]], rows)
        self.scheduleBtn.Enable(True)
        self.data.InsertRows(rows)
        self.grid.SetTable(self.data)
        self.grid.AutoSize()
        self.vBox.Layout()

    def updateGrid1(self, rows):
        self.grid1.ClearGrid()
        rows = map(lambda x: [x[0], x[1].decode('utf-8', 'ignore'), x[2].decode('utf-8', 'ignore')], rows)
        self.data1.InsertRows(rows)
        self.grid1.SetTable(self.data1)
        self.grid1.AutoSize()
        self.vBox.Layout()

    def onSchedule(self, evt):
        workers = map(lambda x: x[0], self.data._data)
        if not self.checkInput():
            return
        s = Scheduler(workers, self.workloadInput.GetValue(), self.minWorkDaysInput.GetValue(),
                      self.maxWorkDaysInput.GetValue())
        targetDays = TimeUtil.getDayLength(self.startDateInput.GetValue(), self.endDateInput.GetValue())
        scheduleResult = s.schedule(int(targetDays))
        if scheduleResult.message.strip() != '':
            wx.MessageBox(scheduleResult.message)
        result = list()
        for keyValuePair in sorted(scheduleResult.workCalendar.iteritems(), key=lambda d: d[0]):
            result.append([TimeUtil.getFormatedDate(self.startDateInput.GetValue(), keyValuePair[0] - 1),
                           ",   ".join(map(str, map(lambda index: workers[index], keyValuePair[1]))),
                           ",   ".join(map(str, map(lambda index: workers[index],
                                                    scheduleResult.restCalendar[keyValuePair[0]])))
                           ])
        self.updateGrid1(result)
        self.exportBtn.Enable(True)
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
        #         wx.MessageBox("输入参数错误，排班天数 * （休息天数 + 1）必须大于等于总员工数")
        #         return False
        # except:
        #     wx.MessageBox("输入参数错误，请检查")
        #     return False
        return True

    def OnEnterDate(self, evt):
        if TimeUtil.isValidDate(self.startDateInput.GetValue()) \
                and TimeUtil.isValidDate(self.endDateInput.GetValue()) \
                and TimeUtil.getDayLength(self.startDateInput.GetValue(), self.endDateInput.GetValue()) > 0:
            self.warnMsg.Hide()
            self.scheduleBtn.Enable(True)
        else:
            self.warnMsg.Show()
            # re-layout
            self.vBox.Layout()
            self.scheduleBtn.Enable(False)

    def onExport(self, evt):
        dialog = wx.FileDialog(self, u"选择要导出的文件位置", os.getcwd(), style=wx.OPEN,
                               wildcard="*.csv")
        if dialog.ShowModal() == wx.ID_OK:
            filePath = dialog.GetPath()
            if filePath:
                data = self.data1._data
                firstLine = u'日期,|,'
                firstLine += u'出勤人员名单'
                firstLine += ''.join([u','] * int(self.workloadInput.GetValue()))
                firstLine += u'|,休息人员名单,'
                firstLine += u''.join(
                    [u','] * (len(self.data._data) - int(self.workloadInput.GetValue())))

                lines = [firstLine]
                # lines.extend(map(
                #     lambda item: item[0] + u',|,' + u','.join(item[1].split()) + u',|,' + u','.join(
                #         item[2].split()), data))
                lines.extend(map(
                    lambda item: item[0] + u',|,' + u''.join(item[1].split()) + u',|,' + u''.join(
                        item[2].split()), data))
                result = BaseDAL.writeAll(filePath, lines)
                wx.MessageBox(u'成功导出到文件', filePath)
        dialog.Destroy()
