# coding=utf-8
import os
import math

import wx
import wx.grid
import wx.lib.scrolledpanel as scrolled
from src.Controller.CalendarController import CalendarController
from src.Controller.GroupController import GroupController
from src.Controller.UserController import UserController
from src.Data.Calendar import Calendar
from src.Data.Group import Group

from src.Strategy.Scheduler import Scheduler
from src.Util.TimeUtil import TimeUtil
from src.Util.FileUtil import FileUtil

__author__ = 'yzhou7'


class SellerPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent)

        self.selectedWorkers = list()
        self.selectedGroup = None
        self.scheduledWorkers = list()
        self.scheduledGroup = None
        self.scheduledStartDate = TimeUtil.getToday()
        self.exportData = list()
        self.displayWeeklyReport = True

        self.initUI()
        self.Show(True)

    def initUI(self):

        self.SetScrollRate(20, 20)
        self.SetAutoLayout(True)
        self.SetBackgroundColour('white')

        self.vBox = wx.BoxSizer(wx.VERTICAL)

        self.setupDateInput()
        self.displayTodayData()

        self.SetSizer(self.vBox)

    def setupDateInput(self):

        optionSizer = wx.GridBagSizer(4, 4)
        optionOuterSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=u'选项')

        userGroupText = wx.StaticText(self, label=u'排班班组')
        optionSizer.Add(userGroupText, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)
        self.userGroupDropDown = wx.ListBox(self, style=wx.LB_SINGLE, choices=self.loadGroupList(), size=(100, 50))
        self.userGroupDropDown.Bind(wx.EVT_LISTBOX, self.onSelection)
        optionSizer.Add(self.userGroupDropDown, pos=(0, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        # workloadText = wx.StaticText(self, label=u'每天出勤人数')
        # optionSizer.Add(workloadText, pos=(0, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)
        #
        # self.workloadInput = wx.TextCtrl(self, value='', style=wx.TE_PROCESS_ENTER)
        # optionSizer.Add(self.workloadInput, pos=(0, 3),
        #                 flag=wx.TOP | wx.LEFT, border=12)

        minWorkDays = wx.StaticText(self, label=u'最大连续休息天数')
        optionSizer.Add(minWorkDays, pos=(1, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.maxRestDaysInput = wx.TextCtrl(self, value='3', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.maxRestDaysInput, pos=(1, 1),
                        flag=wx.TOP | wx.LEFT, border=12)

        maxWorkDaysText = wx.StaticText(self, label=u'最大连续工作天数')
        optionSizer.Add(maxWorkDaysText, pos=(1, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.maxWorkDaysInput = wx.TextCtrl(self, value='6', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.maxWorkDaysInput, pos=(1, 3),
                        flag=wx.TOP | wx.LEFT, border=12)

        startDate = wx.StaticText(self, label=u'开始日期')
        optionSizer.Add(startDate, pos=(2, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.startDateInput = wx.TextCtrl(self, value=TimeUtil.getMonday(TimeUtil.getToday()),
                                          style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT, self.OnEnterDate, self.startDateInput)
        optionSizer.Add(self.startDateInput, pos=(2, 1),
                        flag=wx.TOP | wx.LEFT, border=12)

        endDate = wx.StaticText(self, label=u'结束日期')
        optionSizer.Add(endDate, pos=(2, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.endDateInput = wx.TextCtrl(self,
                                        value=TimeUtil.getSunday(
                                            TimeUtil.getFormatedDate(self.startDateInput.GetValue(), 55)),
                                        style=wx.TE_PROCESS_ENTER)
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

        fontBtn = wx.Font(13, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.FONTWEIGHT_BOLD)
        btnOuterSizer = wx.StaticBoxSizer(wx.VERTICAL, self, u'操作')
        btnSizer = wx.GridBagSizer(4, 4)
        self.scheduleBtn = wx.Button(self, label=u'开始\n排班', size=(80, 66))
        self.scheduleBtn.SetFont(fontBtn)
        btnSizer.Add(self.scheduleBtn, pos=(0, 0), flag=wx.LEFT | wx.RIGHT, border=12)
        self.scheduleBtn.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.onSchedule, self.scheduleBtn)

        self.exportBtn = wx.Button(self, label=u'导出\n排班', size=(80, 66))
        self.exportBtn.SetFont(fontBtn)
        btnSizer.Add(self.exportBtn, pos=(1, 0), flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=12)
        self.exportBtn.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.onExport, self.exportBtn)

        self.convertDisplayBtn = wx.Button(self, label=u'切换\n排班\n格式', size=(80, 66))
        self.convertDisplayBtn.SetFont(fontBtn)
        btnSizer.Add(self.convertDisplayBtn, pos=(0, 2), span=(0, 1), flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=12)
        self.Bind(wx.EVT_BUTTON, self.onConvertDisplay, self.convertDisplayBtn)

        self.saveBtn = wx.Button(self, label=u'保存\n排班', size=(80, 66))
        self.saveBtn.SetFont(fontBtn)
        btnSizer.Add(self.saveBtn, pos=(0, 1), flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=12)
        self.saveBtn.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.onSaveCalendar, self.saveBtn)

        self.loadBtn = wx.Button(self, label=u'加载\n排班', size=(80, 66))
        self.loadBtn.SetFont(fontBtn)
        btnSizer.Add(self.loadBtn, pos=(1, 1), flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=12)
        self.Bind(wx.EVT_BUTTON, self.onLoadCalendar, self.loadBtn)

        btnOuterSizer.Add(btnSizer)

        outerSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        outerSizer.Add(optionOuterSizer)
        outerSizer.AddSpacer(15)
        outerSizer.Add(btnOuterSizer)

        self.vBox.Add(outerSizer, wx.ALIGN_TOP | wx.ALIGN_LEFT, 10)

    def displayTodayData(self):
        gridSizer = wx.GridBagSizer(4, 4)
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(0, 3)
        self.grid.SetColLabelValue(0, u'员工名')
        self.grid.SetColLabelValue(1, u'总出勤天数')
        self.grid.SetColLabelValue(2, u'总工时')
        self.grid.AutoSize()
        gridSizer.Add(self.grid, pos=(1, 1), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.RIGHT, border=15)

        self.grid1 = wx.grid.Grid(self)
        self.grid1.CreateGrid(0, 1)
        self.grid1.SetColLabelValue(0, u'员工名')
        self.grid1.AutoSize()
        gridSizer.Add(self.grid1, pos=(1, 2), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)
        if not self.displayWeeklyReport:
            self.grid1.Hide()

        self.grid2 = wx.grid.Grid(self)
        self.grid2.CreateGrid(0, 2)
        self.grid2.SetColLabelValue(0, u'日期')
        self.grid2.SetColLabelValue(1, u'出勤人员名单')
        gridSizer.Add(self.grid2, pos=(1, 3), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)
        if self.displayWeeklyReport:
            self.grid2.Hide()

        self.vBox.Add(gridSizer, wx.ALIGN_BOTTOM | wx.ALIGN_LEFT, 10)

    def updateGrid(self, rows):
        self.grid.ClearGrid()
        currentRowNum = self.grid.GetNumberRows()
        if currentRowNum < len(rows):
            self.grid.AppendRows(numRows=(len(rows) - currentRowNum))
        elif currentRowNum > len(rows):
            self.grid.DeleteRows(numRows=(currentRowNum - len(rows)))
        for rowNum in range(len(rows)):
            self.grid.SetCellValue(rowNum, 0, rows[rowNum][0])
            self.grid.SetCellValue(rowNum, 1, rows[rowNum][1])
            self.grid.SetCellValue(rowNum, 2, rows[rowNum][2])
        self.grid.AutoSize()
        self.vBox.Layout()

    def updateGrid1(self, rows, startDate):
        self.grid1.ClearGrid()
        currentRowNum = self.grid1.GetNumberRows()
        if currentRowNum < len(rows):
            self.grid1.AppendRows(numRows=(len(rows) - currentRowNum))
        elif currentRowNum > len(rows):
            self.grid1.DeleteRows(numRows=(currentRowNum - len(rows)))

        totalWeekNum = len(list(rows.values())[0]) if len(rows.values()) > 0 else 0
        currentColNum = self.grid1.GetNumberCols() - 1
        if currentColNum < totalWeekNum:
            self.grid1.AppendCols(numCols=(totalWeekNum - currentColNum))
        elif currentColNum > totalWeekNum:
            self.grid1.DeleteCols(numCols=(currentColNum - totalWeekNum))

        for totalWeekNum in range(1, totalWeekNum + 1):
            dateStr = u'第 ' + str(totalWeekNum) + u' 周\n'
            endDate = TimeUtil.getFormatedDate(startDate, 6)
            dateStr += (startDate + ' -- ' + endDate)
            self.grid1.SetColLabelValue(totalWeekNum, dateStr)
            startDate = TimeUtil.getFormatedDate(endDate, 1)

        rowNum = 0
        for (wokerName, workDayList) in rows.items():
            self.grid1.SetCellValue(rowNum, 0, wokerName)
            for weekNum in range(len(workDayList)):
                self.grid1.SetCellValue(rowNum, weekNum + 1, ',  '.join(list(map(str, workDayList[weekNum]))))
            rowNum += 1
        self.grid1.AutoSize()
        self.vBox.Layout()

    def updateGrid2(self, rows):
        self.grid2.ClearGrid()

        currentRowNum = self.grid2.GetNumberRows()
        if currentRowNum < len(rows):
            self.grid2.AppendRows(numRows=(len(rows) - currentRowNum))
        elif currentRowNum > len(rows):
            self.grid2.DeleteRows(numRows=(currentRowNum - len(rows)))

        for rowNum in range(len(rows)):
            if TimeUtil.isWeekend(rows[rowNum][0]):
                self.grid2.SetCellBackgroundColour(rowNum, 0, 'yellow')
                self.grid2.SetCellBackgroundColour(rowNum, 1, 'yellow')
            self.grid2.SetCellValue(rowNum, 0, rows[rowNum][0])
            self.grid2.SetCellValue(rowNum, 1, rows[rowNum][1])

        self.grid2.AutoSize()
        self.vBox.Layout()

    def onSchedule(self, evt):
        self.scheduledWorkers = self.selectedWorkers
        self.scheduledGroup = self.selectedGroup
        self.startDateInput.SetValue(TimeUtil.getMonday(self.startDateInput.GetValue()))
        self.endDateInput.SetValue(TimeUtil.getSunday(self.endDateInput.GetValue()))
        self.scheduledStartDate = self.startDateInput.GetValue()
        if not self.checkInput():
            return

        # 现在将工作和休息互换，算法不变
        s = Scheduler(workers=list(range(len(self.scheduledWorkers))),
                      dailyRequiredWorkerNum=len(self.scheduledWorkers) - int(self.scheduledGroup.workLoad),
                      maxRestDay=self.maxWorkDaysInput.GetValue(),
                      maxWorkDay=self.maxRestDaysInput.GetValue(),
                      isShuffle=True)
        targetDays = TimeUtil.getDayLength(self.startDateInput.GetValue(), self.endDateInput.GetValue())
        scheduleResult = s.schedule(int(targetDays))
        if scheduleResult.message.strip() != '':
            wx.MessageBox(scheduleResult.message)

        self.resultCalendar = scheduleResult.restCalendar
        self.displayScheduleResult(self.resultCalendar, self.scheduledWorkers, self.scheduledGroup.workLoad,
                                   self.scheduledStartDate)
        self.exportBtn.Enable(True)
        self.saveBtn.Enable(True)

    def displayScheduleResult(self, calendar, workers, workLoad, startDate):
        try:
            result = dict()
            workdayDict = Scheduler.getWorkDayForEachWorker(calendar, workers)
            for (workIndex, workDayList) in workdayDict.items():
                workDayList = list(map(int, workDayList))
                workDayList.sort()
                weeklyWorkDayList = list()
                week = 1
                startIndex = 0
                for dateIndex in range(len(workDayList)):
                    if int(workDayList[dateIndex]) > week * 7:
                        weeklyWorkDayList.append(
                            list(
                                map(lambda date: date % 7 if date % 7 != 0 else 7, workDayList[startIndex: dateIndex])))
                        startIndex = dateIndex
                        week += 1
                if startIndex < len(workDayList):
                    weeklyWorkDayList.append(
                        list(map(lambda date: date % 7 if date % 7 != 0 else 7,
                                 workDayList[startIndex: len(workDayList)])))
                result[workers[workIndex]] = weeklyWorkDayList
            self.exportData = result
            self.updateGrid1(result, startDate)

            self.personalTotalWorkDay = Scheduler.calculateWorkDayPerWorker(calendar)
            workDayData = list()
            for i in range(len(workers)):
                workDayData.append([workers[i], str(self.personalTotalWorkDay.get(i, 0)),
                                    str(self.personalTotalWorkDay.get(i, 0) * int(workLoad))])
            # 添加平均数行
            avgWorkDayNum = math.ceil(float(len(calendar.keys())) * int(
                workLoad) / len(
                workers))
            avgWorkHour = avgWorkDayNum * int(workLoad)
            workDayData.append([u'平均出勤天数', str(avgWorkDayNum), str(avgWorkHour)])
            self.updateGrid(workDayData)

            result = list()
            for keyValuePair in sorted(calendar.items(), key=lambda d: int(d[0])):
                result.append([TimeUtil.getFormatedDate(startDate, int(keyValuePair[0]) - 1),
                               ",   ".join(map(str, map(lambda index: workers[index], keyValuePair[1])))])
            self.updateGrid2(result)
        except Exception as e:
            wx.MessageBox(u'出错啦: ' + str(e))

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
                try:
                    data = self.exportData
                    # firstLine = u'日期,|,'
                    # firstLine += u'出勤人员名单'
                    # firstLine += ''.join([u','] * int(self.workloadInput.GetValue()))
                    # firstLine += u'|,休息人员名单,'
                    # firstLine += u''.join(
                    #     [u','] * (len(data) - int(self.workloadInput.GetValue())))
                    #
                    # lines = [firstLine]
                    # lines.extend(list(map(
                    #     lambda item: item[0] + u',|,' + u''.join(item[1].split()) + u',|,' + u''.join(
                    #         item[2].split()), data)))
                    firstLine = u'员工名'
                    totalWeekNum = int(
                        TimeUtil.getDayLength(self.startDateInput.GetValue(), self.endDateInput.GetValue()) / 7)
                    startDate = self.startDateInput.GetValue()
                    for totalWeekNum in range(1, totalWeekNum + 1):
                        dateStr = u',"第 ' + str(totalWeekNum) + u' 周\n'
                        endDate = TimeUtil.getFormatedDate(startDate, 6)
                        dateStr += (startDate + ' -- ' + endDate + '"')
                        firstLine += dateStr
                        startDate = TimeUtil.getFormatedDate(endDate, 1)

                    lines = [firstLine]

                    for (wokerName, workDayList) in data.items():
                        lines.append(wokerName + u',' + u','.join(
                            list(map(lambda week: ' '.join(list(map(str, week))), workDayList))))

                    lines.append('\n')
                    lines.append(u'员工名,总工时（小时）')
                    # 工时
                    for i in range(len(self.scheduledWorkers)):
                        lines.append(self.scheduledWorkers[i] + ',' + str(
                            self.personalTotalWorkDay.get(i, 0) * int(self.scheduledGroup.workLoad)))

                    FileUtil.writeAll(filePath, lines)
                    wx.MessageBox(u'成功导出到文件', filePath)
                except Exception as e:
                    wx.MessageBox(u'导出失败，原因为: ' + str(e))
        dialog.Destroy()

    def loadGroupList(self):
        groupList = GroupController().getAllGroup()
        groupNameList = list(map(lambda group: group.groupName, groupList))
        self.groupInnerMap = dict()
        count = 0
        for group in groupList:
            self.groupInnerMap[count] = group
            count += 1
        return groupNameList

    def onSelection(self, evt):
        groupId = self.groupInnerMap.get(evt.GetSelection(), Group(groupId=0)).groupId
        self.selectedGroup = GroupController().getGroup(groupId)
        users = UserController().getAllUserByGroup(groupId)
        self.selectedWorkers = list(map(lambda user: user.userName, users))
        rows = list(map(lambda user: [user.userName, '', ''], users))
        self.updateGrid(rows)
        if users == None or len(users) == 0:
            self.scheduleBtn.Enable(False)
        else:
            self.scheduleBtn.Enable(True)

    def refreshGroupList(self):
        self.userGroupDropDown.Clear()
        self.userGroupDropDown.InsertItems(self.loadGroupList(), 0)

    def onSaveCalendar(self, evt):
        dlg = wx.TextEntryDialog(None, "为该排班选择一个名字", "排班方案名", "")

        if dlg.ShowModal() == wx.ID_OK:
            calName = dlg.GetValue()
            calendar = Calendar(calName, self.resultCalendar, self.scheduledWorkers, self.scheduledGroup.groupId,
                                self.scheduledGroup.workLoad, self.scheduledStartDate)
            eid = CalendarController().createCalendar(calendar)
            if eid == -1:
                wx.MessageBox(u'保存排班失败，请重试')
                return

    def onLoadCalendar(self, evt):
        dlg = wx.SingleChoiceDialog(None, "请选择将要加载的排班方案",
                                    "方案列表",
                                    self.loadCalendarList())
        if dlg.ShowModal() == wx.ID_OK:
            # 检查该方案是否还有效
            calendar = self.calInnerMap.get(dlg.GetSelection(), Calendar(calId=0))
            groupId = calendar.groupId
            group = GroupController().getGroup(groupId)
            if group == None \
                    or group.workLoad != calendar.workLoad \
                    or len(UserController().getAllUserByGroup(groupId)) != len(calendar.workerList):
                wx.MessageBox("对应班组已被删除或修改，方案无效")
                CalendarController().deleteCalendar(calendar.calId)
                return

            self.displayScheduleResult(calendar.calendar, calendar.workerList, calendar.workLoad, calendar.startDate)

    def loadCalendarList(self):
        calList = CalendarController().getAllCalendar()
        calNameList = list(map(lambda cal: cal.calName, calList))
        self.calInnerMap = dict()
        count = 0
        for cal in calList:
            self.calInnerMap[count] = cal
            count += 1
        return calNameList

    def onConvertDisplay(self, evt):
        if self.displayWeeklyReport == False:
            self.displayWeeklyReport = True
            self.grid1.Show()
            self.grid2.Hide()
            self.vBox.Layout()
        else:
            self.displayWeeklyReport = False
            self.grid1.Hide()
            self.grid2.Show()
            self.vBox.Layout()
