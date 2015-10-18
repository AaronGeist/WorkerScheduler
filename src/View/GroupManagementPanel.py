# coding=utf-8
import re

import wx
import wx.grid
import wx.lib.scrolledpanel as scrolled

from src.Controller.GroupController import GroupController
from src.Controller.UserController import UserController
from src.Data.Group import Group

__author__ = 'yzhou7'


class GroupManagementPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent)
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
        optionOuterSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=u'班组属性')

        groupNameText = wx.StaticText(self, label=u'组名')
        optionSizer.Add(groupNameText, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.groupIdInput = wx.TextCtrl(self, value='', style=wx.TE_PROCESS_ENTER)
        self.groupIdInput.Hide()

        self.groupNameInput = wx.TextCtrl(self, value='', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.groupNameInput, pos=(0, 1),
                        flag=wx.TOP | wx.LEFT, border=12)

        groupMemoText = wx.StaticText(self, label=u'备注')
        optionSizer.Add(groupMemoText, pos=(0, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.groupMemoInput = wx.TextCtrl(self, value='', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.groupMemoInput, pos=(0, 3),
                        flag=wx.TOP | wx.LEFT, border=12)

        workingHourText = wx.StaticText(self, label=u'每日工时')
        optionSizer.Add(workingHourText, pos=(1, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.workingHourInput = wx.TextCtrl(self, value='', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.workingHourInput, pos=(1, 1),
                        flag=wx.TOP | wx.LEFT, border=12)

        workLoadText = wx.StaticText(self, label=u'每日出勤人数')
        optionSizer.Add(workLoadText, pos=(1, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.workLoadInput = wx.TextCtrl(self, value='', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.workLoadInput, pos=(1, 3),
                        flag=wx.TOP | wx.LEFT, border=12)

        optionOuterSizer.Add(optionSizer)

        fontBtn = wx.Font(13, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.FONTWEIGHT_BOLD)
        btnOuterSizer = wx.StaticBoxSizer(wx.VERTICAL, self, u'操作')
        btnSizer = wx.GridBagSizer(4, 4)
        self.createGroupBtn = wx.Button(self, label=u'添加\n班组', size=(80, 66))
        self.createGroupBtn.SetFont(fontBtn)
        btnSizer.Add(self.createGroupBtn, pos=(0, 0), flag=wx.LEFT | wx.RIGHT, border=12)
        self.Bind(wx.EVT_BUTTON, self.onCreate, self.createGroupBtn)
        self.removeGroupBtn = wx.Button(self, label=u'修改\n删除', size=(80, 66))
        self.removeGroupBtn.SetFont(fontBtn)
        btnSizer.Add(self.removeGroupBtn, pos=(0, 1), flag=wx.LEFT | wx.RIGHT, border=12)
        self.Bind(wx.EVT_BUTTON, self.onShowRemove, self.removeGroupBtn)
        self.removeIsShown = False
        self.modifyGroupBtn = wx.Button(self, label=u'确认\n修改', size=(80, 66))
        self.modifyGroupBtn.SetFont(fontBtn)
        btnSizer.Add(self.modifyGroupBtn, pos=(0, 2), flag=wx.LEFT | wx.RIGHT, border=12)
        self.modifyGroupBtn.Hide()
        self.Bind(wx.EVT_BUTTON, self.onModifyGroup, self.modifyGroupBtn)

        btnOuterSizer.Add(btnSizer)

        outerSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        outerSizer.Add(optionOuterSizer)
        outerSizer.AddSpacer(15)
        outerSizer.Add(btnOuterSizer)

        self.vBox.Add(outerSizer, wx.ALIGN_TOP | wx.ALIGN_LEFT, 10)

    def displayTodayData(self):
        gridSizer = wx.GridBagSizer(4, 4)
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(0, 7)
        self.grid.SetColLabelValue(0, u'班组编号')
        self.grid.SetColLabelValue(1, u'班组名')
        self.grid.SetColLabelValue(2, u'备注')
        self.grid.SetColLabelValue(3, u'每日工时')
        self.grid.SetColLabelValue(4, u'每日出勤人数')
        self.grid.SetColLabelValue(5, u'修改操作')
        self.grid.SetColLabelValue(6, u'删除操作')
        controller = GroupController()
        groups = controller.getAllGroup()
        self.updateGrid(list(map(lambda x: [str(x.groupId), x.groupName, x.groupDesc, str(x.workHour), str(x.workLoad)], groups)))
        # 编号用来进行组操作，不用显示
        self.grid.HideCol(0)
        self.grid.HideCol(5)
        self.grid.HideCol(6)
        self.grid.AutoSize()
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onCellChoosen, self.grid)
        gridSizer.Add(self.grid, pos=(1, 1), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.RIGHT, border=15)

        self.vBox.Add(gridSizer, wx.ALIGN_BOTTOM | wx.ALIGN_LEFT, 10)

    def updateGrid(self, rows):
        self.grid.ClearGrid()
        currentRowNum = self.grid.GetNumberRows()
        if currentRowNum < len(rows):
            self.grid.AppendRows(len(rows) - currentRowNum)
        for rowNum in range(len(rows)):
            self.grid.SetCellValue(rowNum, 0, rows[rowNum][0])
            self.grid.SetCellValue(rowNum, 1, rows[rowNum][1])
            self.grid.SetCellValue(rowNum, 2, rows[rowNum][2])
            self.grid.SetCellValue(rowNum, 3, rows[rowNum][3])
            self.grid.SetCellValue(rowNum, 4, rows[rowNum][4])
            self.grid.SetCellValue(rowNum, 5, '修改')
            self.grid.SetCellValue(rowNum, 6, '删除')
        self.grid.AutoSize()
        self.vBox.Layout()

    def refreshGrid(self):
        controller = GroupController()
        groups = controller.getAllGroup()
        self.updateGrid(
            list(map(lambda x: [str(x.groupId), x.groupName, x.groupDesc, str(x.workHour), str(x.workLoad)], groups)))

    def onCreate(self, evt):
        newGroup = Group(self.groupNameInput.GetValue().strip(), self.groupMemoInput.GetValue().strip(),
                         self.workingHourInput.GetValue().strip(), self.workLoadInput.GetValue().strip())
        if self.validateGroup(newGroup):
            controller = GroupController()
            eid = controller.createGroup(newGroup)
            if eid == -1:
                wx.MessageBox(u'创建班组失败')
                return
            newGroup.groupId = eid
            self.insertSingleUserIntoGrid(newGroup)
            self.groupNameInput.Clear()
            self.groupMemoInput.Clear()
            self.workingHourInput.Clear()
            self.workLoadInput.Clear()

    def validateGroup(self, group):
        errorMsg = ''
        if group.groupName == '':
            errorMsg = u'班组名不能为空'
        elif re.match(r'\d+$', group.workHour) == None:
            errorMsg = u'每日工时必须为正整数'
        elif int(group.workHour) <= 0 or int(group.workHour) > 24:
            errorMsg = u'每日工时不合理'

        if errorMsg != '':
            wx.MessageBox(errorMsg)
            return False
        else:
            return True

    def insertSingleUserIntoGrid(self, group):
        self.grid.InsertRows(0, 1)
        self.grid.SetCellValue(0, 0, str(group.groupId))
        self.grid.SetCellValue(0, 1, group.groupName)
        self.grid.SetCellValue(0, 2, group.groupDesc)
        self.grid.SetCellValue(0, 3, str(group.workHour))
        self.grid.SetCellValue(0, 4, str(group.workLoad))
        self.grid.SetCellValue(0, 5, u'修改')
        self.grid.SetCellValue(0, 6, u'删除')
        self.grid.AutoSize()
        self.vBox.Layout()

    def onShowRemove(self, evt):
        if not self.removeIsShown:
            self.removeIsShown = True
            self.removeGroupBtn.SetLabelText(u'结束\n操作')
            self.grid.ShowCol(5)
            self.grid.ShowCol(6)
            self.grid.AutoSize()
        else:
            self.removeIsShown = False
            self.removeGroupBtn.SetLabelText(u'修改\n删除')
            self.grid.HideCol(5)
            self.grid.HideCol(6)
            self.resetModify()
            self.grid.AutoSize()

    def onCellChoosen(self, evt):
        if evt.GetCol() == 5:
            # 修改事件
            self.groupIdInput.SetValue(self.grid.GetCellValue(evt.GetRow(), 0))
            self.groupNameInput.SetValue(self.grid.GetCellValue(evt.GetRow(), 1))
            self.groupMemoInput.SetValue(self.grid.GetCellValue(evt.GetRow(), 2))
            self.workingHourInput.SetValue(self.grid.GetCellValue(evt.GetRow(), 3))
            self.workLoadInput.SetValue(self.grid.GetCellValue(evt.GetRow(), 4))
            self.modifyGroupBtn.Show()
            self.vBox.Layout()
            # TODO 高亮编辑区
        elif evt.GetCol() == 6:
            # 删除事件
            # wx.MessageBox(str(self.grid.GetCellValue(evt.GetRow(), 0)))
            dlg = wx.MessageDialog(None, u'确认要删除班组 [' + self.grid.GetCellValue(evt.GetRow(), 1) + u'] 吗？',
                                   'MessageDialog', wx.OK | wx.CANCEL)
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                # 确认删除
                controller = GroupController()
                result = controller.deleteGroup(int(self.grid.GetCellValue(evt.GetRow(), 0)))
                if result:
                    userController = UserController()
                    userController.removeGroup(int(self.grid.GetCellValue(evt.GetRow(), 0)))
                    self.grid.DeleteRows(pos=evt.GetRow())

                if result:
                    wx.MessageBox(u'删除成功')
                else:
                    wx.MessageBox(u'删除失败')
            dlg.Destroy()

    def onModifyGroup(self, evt):
        if self.validateGroup(Group(self.groupNameInput.GetValue().strip(), self.groupMemoInput.GetValue().strip(),
                                    self.workingHourInput.GetValue().strip())):
            dlg = wx.MessageDialog(None, u'确认要修改班组 [' + self.groupNameInput.GetValue().strip() + u'] 吗？',
                                   'MessageDialog', wx.OK | wx.CANCEL)
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                # 确认修改
                controller = GroupController()
                result = controller.editGroup(int(self.groupIdInput.GetValue()),
                                              self.groupNameInput.GetValue().strip(),
                                              self.groupMemoInput.GetValue().strip(),
                                              self.workingHourInput.GetValue().strip(),
                                              self.workLoadInput.GetValue().strip())
                if result:
                    wx.MessageBox(u'修改成功')
                    self.refreshGrid()

                else:
                    wx.MessageBox(u'修改失败')
            self.resetModify()
            dlg.Destroy()

    def resetModify(self):
        self.modifyGroupBtn.Hide()
        self.groupIdInput.Clear()
        self.groupNameInput.Clear()
        self.groupMemoInput.Clear()
        self.workingHourInput.Clear()
        self.workLoadInput.Clear()
        self.vBox.Layout()
