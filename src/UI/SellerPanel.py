# coding=utf-8
import os

import wx
import wx.grid
import wx.lib.scrolledpanel as scrolled

from src.Strategy.Scheduler import Scheduler
from src.Util.TimeUtil import TimeUtil
from src.DAL.BaseDAL import BaseDAL

__author__ = 'yzhou7'


class SellerPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent)
        self.workers = list()
        self.exportData = list()
        self.initUI()
        self.Show(True)

    def initUI(self):

        self.SetScrollRate(20, 20)
        self.SetAutoLayout(True)

        self.vBox = wx.BoxSizer(wx.VERTICAL)

        self.setupDateInput()
        self.displayTodayData()

        self.SetSizer(self.vBox)

    def setupDateInput(self):

        optionSizer = wx.GridBagSizer(4, 4)
        optionOuterSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=u'选项')

        workloadText = wx.StaticText(self, label=u'每天出勤人数')
        optionSizer.Add(workloadText, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.workloadInput = wx.TextCtrl(self, value='12', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.workloadInput, pos=(0, 1),
                  flag=wx.TOP | wx.LEFT, border=12)

        workloadText = wx.StaticText(self, label=u'每天工作小时数')
        optionSizer.Add(workloadText, pos=(0, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.workHourInput = wx.TextCtrl(self, value='8', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.workHourInput, pos=(0, 3),
                  flag=wx.TOP | wx.LEFT, border=12)

        minWorkDays = wx.StaticText(self, label=u'最小连续出勤天数')
        optionSizer.Add(minWorkDays, pos=(1, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.minWorkDaysInput = wx.TextCtrl(self, value='3', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.minWorkDaysInput, pos=(1, 1),
                  flag=wx.TOP | wx.LEFT, border=12)

        maxWorkDaysText = wx.StaticText(self, label=u'最大连续出勤天数')
        optionSizer.Add(maxWorkDaysText, pos=(1, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.maxWorkDaysInput = wx.TextCtrl(self, value='6', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.maxWorkDaysInput, pos=(1, 3),
                  flag=wx.TOP | wx.LEFT, border=12)

        startDate = wx.StaticText(self, label=u'开始日期')
        optionSizer.Add(startDate, pos=(2, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.startDateInput = wx.TextCtrl(self, value=TimeUtil.getToday(), style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT, self.OnEnterDate, self.startDateInput)
        optionSizer.Add(self.startDateInput, pos=(2, 1),
                  flag=wx.TOP | wx.LEFT, border=12)

        endDate = wx.StaticText(self, label=u'结束日期')
        optionSizer.Add(endDate, pos=(2, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.endDateInput = wx.TextCtrl(self, value=TimeUtil.getFormatedDate(TimeUtil.getToday(), 30), style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT, self.OnEnterDate, self.endDateInput)
        optionSizer.Add(self.endDateInput, pos=(2, 3),
                  flag=wx.TOP | wx.LEFT, border=12)

        blankMsg = wx.StaticText(self, label=u' ')
        optionSizer.Add(blankMsg, pos=(3, 0), flag=wx.TOP | wx.LEFT, border=15)

        self.warnMsg = wx.StaticText(self, label=u'非法日期，请重新输入')
        self.warnMsg.SetForegroundColour('red')
        optionSizer.Add(self.warnMsg, pos=(3, 1), span=(1, 3), flag=wx.TOP | wx.LEFT, border=15)
        self.warnMsg.Hide()

        optionOuterSizer.Add(optionSizer)

        fontBtn = wx.Font(13, wx.FONTFAMILY_MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD)
        btnOuterSizer = wx.StaticBoxSizer(wx.VERTICAL, self, u'操作')
        btnSizer = wx.GridBagSizer(4, 4)
        self.scheduleBtn = wx.Button(self, label=u'开始\n排班', size=(80, 66))
        self.scheduleBtn.SetFont(fontBtn)
        btnSizer.Add(self.scheduleBtn, pos=(0, 0), flag= wx.LEFT | wx.RIGHT, border=12)
        self.scheduleBtn.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.onSchedule, self.scheduleBtn)

        self.exportBtn = wx.Button(self, label=u'导出\n排班', size=(80, 66))
        self.exportBtn.SetFont(fontBtn)
        btnSizer.Add(self.exportBtn, pos=(1, 0), flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=12)
        self.exportBtn.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.onExport, self.exportBtn)

        btnOuterSizer.Add(btnSizer)

        outerSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        outerSizer.Add(optionOuterSizer)
        outerSizer.AddSpacer(15)
        outerSizer.Add(btnOuterSizer)

        self.vBox.Add(outerSizer, wx.ALIGN_TOP | wx.ALIGN_LEFT, 10)


    def displayTodayData(self):
        gridSizer = wx.GridBagSizer(4, 4)
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(0, 2)
        self.grid.SetColLabelValue(0, u'员工名')
        self.grid.SetColLabelValue(1, u'总出勤天数')
        self.grid.AutoSize()
        gridSizer.Add(self.grid, pos=(1, 1), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.RIGHT, border=15)

        self.grid1 = wx.grid.Grid(self)
        self.grid1.CreateGrid(0, 3)
        self.grid1.SetColLabelValue(0, u'日期')
        self.grid1.SetColLabelValue(1, u'出勤人员名单')
        self.grid1.SetColLabelValue(2, u'休息人员名单')
        self.grid1.AutoSize()
        gridSizer.Add(self.grid1, pos=(1, 2), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.vBox.Add(gridSizer, wx.ALIGN_BOTTOM | wx.ALIGN_LEFT, 10)


    def updateGrid(self, rows):
        self.scheduleBtn.Enable(True)
        self.workers = rows
        self.grid.ClearGrid()
        currentRowNum = self.grid.GetNumberRows()
        if currentRowNum < len(rows):
            self.grid.AppendRows(len(rows) - currentRowNum)
        for rowNum in range(len(rows)):
            self.grid.SetCellValue(rowNum, 0, rows[rowNum][0])
            self.grid.SetCellValue(rowNum, 1, rows[rowNum][1])
        self.grid.AutoSize()
        self.vBox.Layout()


    def updateGrid1(self, rows):
        self.grid1.ClearGrid()
        currentRowNum = self.grid1.GetNumberRows()
        if currentRowNum < len(rows):
            self.grid1.AppendRows(len(rows) - currentRowNum)
        for rowNum in range(len(rows)):
            self.grid1.SetCellValue(rowNum, 0, rows[rowNum][0])
            self.grid1.SetCellValue(rowNum, 1, rows[rowNum][1])
            self.grid1.SetCellValue(rowNum, 2, rows[rowNum][2])
        self.grid1.AutoSize()
        self.vBox.Layout()


    def onSchedule(self, evt):
        if not self.checkInput():
            return
        s = Scheduler(self.workers, self.workloadInput.GetValue(), self.minWorkDaysInput.GetValue(),
                      self.maxWorkDaysInput.GetValue())
        targetDays = TimeUtil.getDayLength(self.startDateInput.GetValue(), self.endDateInput.GetValue())
        scheduleResult = s.schedule(int(targetDays))
        if scheduleResult.message.strip() != '':
            wx.MessageBox(scheduleResult.message)
        result = list()
        for keyValuePair in sorted(scheduleResult.workCalendar.items(), key=lambda d: d[0]):
            result.append([TimeUtil.getFormatedDate(self.startDateInput.GetValue(), keyValuePair[0] - 1),
                           ",   ".join(map(str, map(lambda index: self.workers[index][0], keyValuePair[1]))),
                           ",   ".join(map(str, map(lambda index: self.workers[index][0],
                                                    scheduleResult.restCalendar[keyValuePair[0]])))
                           ])
        self.exportData = result
        self.updateGrid1(result)
        self.exportBtn.Enable(True)
        personalTotalWorkDay = scheduleResult.personalTotalWorkDay
        workDayData = list()
        for i in range(len(self.workers)):
            workDayData.append([self.workers[i][0], str(personalTotalWorkDay.get(i, 0))])
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
        dialog = wx.FileDialog(self, u"选择要导出的文件位置", os.getcwd(), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                               wildcard="*.csv")
        if dialog.ShowModal() == wx.ID_OK:
            filePath = dialog.GetPath()
            if filePath:
                data = self.exportData
                firstLine = u'日期,|,'
                firstLine += u'出勤人员名单'
                firstLine += ''.join([u','] * int(self.workloadInput.GetValue()))
                firstLine += u'|,休息人员名单,'
                firstLine += u''.join(
                    [u','] * (len(data) - int(self.workloadInput.GetValue())))

                lines = [firstLine]
                lines.extend(list(map(
                    lambda item: item[0] + u',|,' + u''.join(item[1].split()) + u',|,' + u''.join(
                        item[2].split()), data)))
                result = BaseDAL.writeAll(filePath, lines)
                wx.MessageBox(u'成功导出到文件', filePath)
        dialog.Destroy()
