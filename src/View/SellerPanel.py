# coding=utf-8
import os

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

        self.selectedScheduleInput = list()
        self.scheduledInput = list()
        self.scheduledStartDate = TimeUtil.getToday()
        self.exportData = list()
        self.displayWeeklyReport = True

        self.initUI()
        self.Show(True)

    def initUI(self):

        self.SetScrollRate(20, 20)
        self.SetAutoLayout(True)
        self.SetBackgroundColour('white')

        self.colorList = ['#ffffcc', '#99ffcc']

        self.vBox = wx.BoxSizer(wx.VERTICAL)

        self.setupDateInput()
        self.displayTodayData()

        self.SetSizer(self.vBox)

    def setupDateInput(self):

        optionSizer = wx.GridBagSizer(4, 4)
        optionOuterSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=u'选项')

        userGroupText = wx.StaticText(self, label=u'排班班组')
        optionSizer.Add(userGroupText, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)
        self.userGroupDropDown = wx.ListBox(self, style=wx.LB_MULTIPLE, choices=self.loadGroupList(), size=(100, 50))
        self.userGroupDropDown.Bind(wx.EVT_LISTBOX, self.onSelection)
        optionSizer.Add(self.userGroupDropDown, pos=(0, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

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

        self.deleteBtn = wx.Button(self, label=u'删除\n排班', size=(80, 66))
        self.deleteBtn.SetFont(fontBtn)
        btnSizer.Add(self.deleteBtn, pos=(1, 2), flag=wx.BOTTOM | wx.LEFT | wx.RIGHT, border=12)
        self.Bind(wx.EVT_BUTTON, self.onDeleteCalendar, self.deleteBtn)

        btnOuterSizer.Add(btnSizer)

        outerSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        outerSizer.Add(optionOuterSizer)
        outerSizer.AddSpacer(15)
        outerSizer.Add(btnOuterSizer)

        self.vBox.Add(outerSizer, wx.ALIGN_TOP | wx.ALIGN_LEFT, 10)

    def displayTodayData(self):
        gridSizer = wx.GridBagSizer(4, 4)
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(0, 4)
        self.grid.SetColLabelValue(0, u'员工名')
        self.grid.SetColLabelValue(1, u'班组名')
        self.grid.SetColLabelValue(2, u'总出勤天数')
        self.grid.SetColLabelValue(3, u'总工时')
        self.grid.AutoSize()
        gridSizer.Add(self.grid, pos=(1, 1), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.RIGHT, border=15)

        self.grid1 = wx.grid.Grid(self)
        self.grid1.CreateGrid(0, 2)
        self.grid1.SetColLabelValue(0, u'员工名')
        self.grid1.SetColLabelValue(1, u'班组名')
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
        self.appendGrid(rows)

    def appendGrid(self, rows):
        currentRowNum = self.grid.GetNumberRows()
        if currentRowNum < len(rows):
            self.grid.AppendRows(numRows=(len(rows) - currentRowNum))
        elif currentRowNum > len(rows):
            self.grid.DeleteRows(numRows=(currentRowNum - len(rows)))
        for rowNum in range(len(rows)):
            self.grid.SetCellValue(rowNum, 0, rows[rowNum][0])
            self.grid.SetCellValue(rowNum, 1, rows[rowNum][1])
            self.grid.SetCellValue(rowNum, 2, rows[rowNum][2])
            self.grid.SetCellValue(rowNum, 3, rows[rowNum][3])
        self.grid.AutoSize()
        self.vBox.Layout()

    def updateGrid1(self, rows, startDate):
        self.grid1.ClearGrid()
        currentRowNum = self.grid1.GetNumberRows()
        if currentRowNum < len(rows):
            self.grid1.AppendRows(numRows=(len(rows) - currentRowNum))
        elif currentRowNum > len(rows):
            self.grid1.DeleteRows(numRows=(currentRowNum - len(rows)))

        totalWeekNum = len(rows[0][2]) if len(rows) > 0 else 0
        currentColNum = self.grid1.GetNumberCols() - 2
        if currentColNum < totalWeekNum:
            self.grid1.AppendCols(numCols=(totalWeekNum - currentColNum))
        elif currentColNum > totalWeekNum:
            self.grid1.DeleteCols(numCols=(currentColNum - totalWeekNum))

        for totalWeekNum in range(1, totalWeekNum + 1):
            dateStr = u'第 ' + str(totalWeekNum) + u' 周\n'
            endDate = TimeUtil.getFormatedDate(startDate, 6)
            dateStr += (startDate + ' -- ' + endDate)
            self.grid1.SetColLabelValue(totalWeekNum + 1, dateStr)
            startDate = TimeUtil.getFormatedDate(endDate, 1)

        rowNum = 0
        previousGroupName = ''
        colorCnt = 0
        for item in rows:
            wokerName = item[0]
            groupName = item[1]
            workDayList = item[2]
            if groupName != previousGroupName:
                colorCnt += 1
                previousGroupName = groupName
            self.grid1.SetCellValue(rowNum, 0, wokerName)
            self.grid1.SetCellValue(rowNum, 1, groupName)
            self.grid1.SetCellBackgroundColour(rowNum, 0, self.colorList[colorCnt % 2])
            self.grid1.SetCellBackgroundColour(rowNum, 1, self.colorList[colorCnt % 2])
            for weekNum in range(len(workDayList)):
                self.grid1.SetCellValue(rowNum, weekNum + 2, ',  '.join(list(map(str, workDayList[weekNum]))))
                self.grid1.SetCellBackgroundColour(rowNum, weekNum + 2, self.colorList[colorCnt % 2])

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

        # 多一行给班组名
        self.grid2.AppendRows(1)

        totalGroupNum = len(rows[0][1]) if len(rows) > 0 else 0
        currentColNum = self.grid2.GetNumberCols() - 1
        if currentColNum < totalGroupNum:
            self.grid2.AppendCols(numCols=(totalGroupNum - currentColNum))
        elif currentColNum > totalGroupNum:
            self.grid2.DeleteCols(numCols=(currentColNum - totalGroupNum))

        self.grid2.SetCellBackgroundColour(0, 0, 'white')
        rowNum = 1
        for row in rows:
            date = row[0]
            self.grid2.SetCellValue(rowNum, 0, date)
            self.grid2.SetCellBackgroundColour(rowNum, 0, 'white')

            colCnt = 1
            for groupArrange in row[1]:
                arrangement = groupArrange[0]
                group = groupArrange[1]
                self.grid2.SetCellValue(0, colCnt, group.groupName)
                self.grid2.SetCellBackgroundColour(0, colCnt, 'white')
                self.grid2.SetCellValue(rowNum, colCnt, arrangement)
                self.grid2.SetCellBackgroundColour(rowNum, colCnt, self.colorList[colCnt % 2])
                if colCnt != 1:
                    self.grid2.SetColLabelValue(colCnt, '')
                colCnt += 1

            rowNum += 1

        self.grid2.AutoSize()
        self.vBox.Layout()

    def onSchedule(self, evt):
        self.scheduledInput = self.selectedScheduleInput
        self.startDateInput.SetValue(TimeUtil.getMonday(self.startDateInput.GetValue()))
        self.endDateInput.SetValue(TimeUtil.getSunday(self.endDateInput.GetValue()))
        self.scheduledStartDate = self.startDateInput.GetValue()
        if not self.checkInput():
            return

        self.resultList = list()
        for input in self.scheduledInput:
            scheduledWorkers = input[0]
            scheduledGroup = input[1]
            # 现在将工作和休息互换，算法不变
            s = Scheduler(workers=list(range(len(scheduledWorkers))),
                          dailyRequiredWorkerNum=len(scheduledWorkers) - int(scheduledGroup.workLoad),
                          maxRestDay=self.maxWorkDaysInput.GetValue(),
                          maxWorkDay=self.maxRestDaysInput.GetValue(),
                          isShuffle=True)
            targetDays = TimeUtil.getDayLength(self.startDateInput.GetValue(), self.endDateInput.GetValue())
            scheduleResult = s.schedule(int(targetDays))
            if scheduleResult.message.strip() != '':
                wx.MessageBox(scheduledGroup.groupName + ": " + scheduleResult.message)

            self.resultList.append([scheduleResult.restCalendar, scheduledWorkers, scheduledGroup])

        self.displayScheduleResult(self.resultList, self.scheduledStartDate)
        self.exportBtn.Enable(True)
        self.saveBtn.Enable(True)
        self.selectedScheduleInput = list()

    def displayScheduleResult(self, resultList, startDate):
        personalWorkDayDict = list()
        personalWorkDayLengthList = list()
        dailyAttendenceDict = dict()
        for result in resultList:
            calendar = result[0]
            workers = result[1]
            group = result[2]
            try:
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
                                    map(lambda date: date % 7 if date % 7 != 0 else 7,
                                        workDayList[startIndex: dateIndex])))
                            startIndex = dateIndex
                            week += 1
                    if startIndex < len(workDayList):
                        weeklyWorkDayList.append(
                            list(map(lambda date: date % 7 if date % 7 != 0 else 7,
                                     workDayList[startIndex: len(workDayList)])))
                    personalWorkDayDict.append([workers[workIndex], group.groupName, weeklyWorkDayList])

                personalTotalWorkDay = Scheduler.calculateWorkDayPerWorker(calendar)
                for i in range(len(workers)):
                    personalWorkDayLengthList.append(
                        [workers[i], group.groupName, str(personalTotalWorkDay.get(i, 0)),
                         str(personalTotalWorkDay.get(i, 0) * int(group.workHour))])
                # # 添加平均数行
                # avgWorkDayNum = math.ceil(float(len(calendar.keys())) * int(
                #     group.workLoad) / len(
                #     workers))
                # avgWorkHour = avgWorkDayNum * int(group.workHour)
                # workDayData.append([u'平均出勤天数', str(avgWorkDayNum), str(avgWorkHour)])

                for keyValuePair in sorted(calendar.items(), key=lambda d: int(d[0])):
                    currentDate = TimeUtil.getFormatedDate(startDate, int(keyValuePair[0]) - 1)
                    currentDateArrange = dailyAttendenceDict.get(currentDate, list())

                    currentDateArrange.append(
                        [",   ".join(map(str, map(lambda index: workers[index], keyValuePair[1]))), group])
                    dailyAttendenceDict[currentDate] = currentDateArrange

            except Exception as e:
                wx.MessageBox(u'出错啦: ' + str(e))

        # 按日期排序
        dailyAttendenceList = sorted(dailyAttendenceDict.items(), key=lambda d: d[0])
        self.exportData = [personalWorkDayDict, dailyAttendenceList, personalWorkDayLengthList, startDate]
        self.updateGrid(personalWorkDayLengthList)
        self.updateGrid1(personalWorkDayDict, startDate)
        self.updateGrid2(dailyAttendenceList)

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
                    personalWorkDayDict = self.exportData[0]
                    dailyAttendenceList = self.exportData[1]
                    personalWorkDayLengthList = self.exportData[2]
                    startDate = self.exportData[3]

                    firstLine = u'员工名,班组名'
                    totalWeekNum = int(len(dailyAttendenceList) / 7)
                    for totalWeekNum in range(1, totalWeekNum + 1):
                        dateStr = u',"第 ' + str(totalWeekNum) + u' 周\n'
                        endDate = TimeUtil.getFormatedDate(startDate, 6)
                        dateStr += (startDate + ' -- ' + endDate + '"')
                        firstLine += dateStr
                        startDate = TimeUtil.getFormatedDate(endDate, 1)

                    lines = [firstLine]

                    for item in personalWorkDayDict:
                        wokerName = item[0]
                        groupName = item[1]
                        workDayList = item[2]
                        lines.append(wokerName + ',' + groupName + u',' + u','.join(
                            list(map(lambda week: ' '.join(list(map(str, week))), workDayList))))

                    lines.append('\n')
                    lines.append(u'员工名,班组名,总天数,总工时（小时）')
                    # 工时
                    for i in range(len(personalWorkDayLengthList)):
                        lines.append(','.join(personalWorkDayLengthList[i]))

                    lines.append('\n')
                    lines.append(u'日期,出勤员工')
                    groupInfo = ',' + ''.join(list(map(lambda x: x[1].groupName + ',' * int(x[1].workLoad), dailyAttendenceList[0][1])))

                    innerLines = list()
                    for dailyAttendence in dailyAttendenceList:
                        date = dailyAttendence[0]
                        groupAttendenceList = dailyAttendence[1]
                        attendenceStr = date
                        for groupAttendence in groupAttendenceList:
                            attendence = groupAttendence[0]
                            attendenceStr += ',' + attendence
                        innerLines.append(attendenceStr)
                    lines.append(groupInfo)
                    lines.extend(innerLines)

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
        self.scheduleBtn.Enable(False)
        rows = list()
        self.selectedScheduleInput.clear()
        for selection in self.userGroupDropDown.GetSelections():
            groupId = self.groupInnerMap.get(selection, Group(groupId=0)).groupId
            group = GroupController().getGroup(groupId)
            users = UserController().getAllUserByGroup(groupId)
            self.selectedScheduleInput.append([list(map(lambda user: user.userName, users)), group])
            rows.extend(list(map(lambda user: [user.userName, group.groupName, '', ''], users)))
            if not (users == None or len(users) == 0):
                self.scheduleBtn.Enable(True)
        self.updateGrid(rows)

    def refreshGroupList(self):
        self.userGroupDropDown.Clear()
        groupList = self.loadGroupList()
        if len(groupList) > 0:
            self.userGroupDropDown.InsertItems(groupList, 0)

    def onSaveCalendar(self, evt):
        dlg = wx.TextEntryDialog(None, "为该排班选择一个名字", "排班方案名", "")

        if dlg.ShowModal() == wx.ID_OK:
            calName = dlg.GetValue()
            calendar = Calendar(calName, self.resultList, self.scheduledStartDate)
            eid = CalendarController().createCalendar(calendar)
            if eid == -1:
                wx.MessageBox(u'保存排班失败，请重试')
                return
            else:
                wx.MessageBox(u'保存排班[{0}]成功'.format(calName))

    def onLoadCalendar(self, evt):
        dlg = wx.SingleChoiceDialog(None, "请选择将要加载的排班方案",
                                    "方案列表",
                                    self.loadCalendarList())
        if dlg.ShowModal() == wx.ID_OK:
            # 检查该方案是否还有效
            calendar = self.calInnerMap.get(dlg.GetSelection(), Calendar(calId=0))
            # groupId = calendar.groupId
            # group = GroupController().getGroup(groupId)
            # if group == None \
            #         or group.workLoad != calendar.workLoad \
            #         or len(UserController().getAllUserByGroup(groupId)) != len(calendar.workerList):
            #     wx.MessageBox("对应班组已被删除或修改，方案无效")
            #     CalendarController().deleteCalendar(calendar.calId)
            #     return

            self.displayScheduleResult(calendar.scheduleResult, calendar.startDate)

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

    def onDeleteCalendar(self, evt):
        dlg = wx.SingleChoiceDialog(None, "请选择将要删除的排班方案",
                                    "方案列表",
                                    self.loadCalendarList())
        if dlg.ShowModal() == wx.ID_OK:
            calendar = self.calInnerMap.get(dlg.GetSelection(), Calendar(calId=0))
            CalendarController().deleteCalendar(calendar.calId)
            wx.MessageBox('删除排班方案成功')
