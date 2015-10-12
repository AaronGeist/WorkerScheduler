# coding=utf-8

import wx
import wx.grid
import wx.lib.scrolledpanel as scrolled

from src.Controller.GroupController import GroupController
from src.Controller.UserController import UserController
from src.Data.User import User

__author__ = 'yzhou7'


class UserManagementPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent)
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
        optionOuterSizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label=u'员工属性')

        userNameText = wx.StaticText(self, label=u'员工姓名')
        optionSizer.Add(userNameText, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.userNameInput = wx.TextCtrl(self, value='', style=wx.TE_PROCESS_ENTER)
        optionSizer.Add(self.userNameInput, pos=(0, 1),
                        flag=wx.TOP | wx.LEFT, border=12)

        userGroupText = wx.StaticText(self, label=u'所属班组')
        optionSizer.Add(userGroupText, pos=(0, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        groupList = GroupController().getAllGroup()
        groupNameList = list(map(lambda group: group.groupName, groupList))
        self.userGroupDropDown = wx.ListBox(self, style=wx.LB_SINGLE, choices=groupNameList, size=(100, 50))
        optionSizer.Add(self.userGroupDropDown, pos=(0, 3),
                        flag=wx.TOP | wx.LEFT, border=12)

        optionOuterSizer.Add(optionSizer)

        fontBtn = wx.Font(13, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.FONTWEIGHT_BOLD)
        btnOuterSizer = wx.StaticBoxSizer(wx.VERTICAL, self, u'操作')
        btnSizer = wx.GridBagSizer(4, 4)
        self.createUserBtn = wx.Button(self, label=u'添加\n员工', size=(80, 66))
        self.createUserBtn.SetFont(fontBtn)
        btnSizer.Add(self.createUserBtn, pos=(0, 0), flag=wx.LEFT | wx.RIGHT, border=12)
        self.Bind(wx.EVT_BUTTON, self.onCreate, self.createUserBtn)

        self.removeGroupBtn = wx.Button(self, label=u'删除\n员工', size=(80, 66))
        self.removeGroupBtn.SetFont(fontBtn)
        btnSizer.Add(self.removeGroupBtn, pos=(0, 1), flag=wx.LEFT | wx.RIGHT, border=12)
        self.Bind(wx.EVT_BUTTON, self.onShowRemove, self.removeGroupBtn)
        self.removeIsShown = False

        btnOuterSizer.Add(btnSizer)

        outerSizer = wx.BoxSizer(orient=wx.HORIZONTAL)
        outerSizer.Add(optionOuterSizer)
        outerSizer.AddSpacer(15)
        outerSizer.Add(btnOuterSizer)

        self.vBox.Add(outerSizer, wx.ALIGN_TOP | wx.ALIGN_LEFT, 10)

    def displayTodayData(self):
        gridSizer = wx.GridBagSizer(4, 4)
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(0, 5)
        self.grid.SetColLabelValue(0, u'员工编号')
        self.grid.SetColLabelValue(1, u'员工名')
        self.grid.SetColLabelValue(2, u'所属班组')
        self.grid.SetColLabelValue(3, u'修改操作')
        self.grid.SetColLabelValue(4, u'删除操作')
        self.grid.HideCol(0)
        self.grid.HideCol(3)
        self.grid.HideCol(4)
        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.onCellChoosen, self.grid)
        controller = UserController()
        users = controller.getAllUser()
        groupController = GroupController()

        rows = list(
            map(lambda x: [x.userId, x.userName, groupController.getGroupName(x.userGroup)], users))
        self.updateGrid(rows)
        self.grid.AutoSize()
        gridSizer.Add(self.grid, pos=(1, 1), span=(1, 1), flag=wx.EXPAND | wx.TOP | wx.RIGHT, border=15)

        self.vBox.Add(gridSizer, wx.ALIGN_BOTTOM | wx.ALIGN_LEFT, 10)

    def updateGrid(self, rows):
        self.grid.ClearGrid()
        currentRowNum = self.grid.GetNumberRows()
        if currentRowNum < len(rows):
            self.grid.AppendRows(len(rows) - currentRowNum)
        for rowNum in range(len(rows)):
            self.grid.SetCellValue(rowNum, 0, str(rows[rowNum][0]))
            self.grid.SetCellValue(rowNum, 1, rows[rowNum][1])
            self.grid.SetCellValue(rowNum, 2, rows[rowNum][2])
            self.grid.SetCellValue(rowNum, 3, u'修改')
            self.grid.SetCellValue(rowNum, 4, u'删除')
        self.grid.AutoSize()
        self.vBox.Layout()

    def refreshGrid(self):
        controller = UserController()
        users = controller.getAllUser()
        groupController = GroupController()
        rows = list(
            map(lambda x: [x.userId, x.userName, groupController.getGroupName(x.userGroup)], users))
        self.updateGrid(rows)
        self.grid.AutoSize()

    def refreshGroupList(self):
        groupList = GroupController().getAllGroup()
        groupNameList = list(map(lambda group: group.groupName, groupList))
        self.userGroupDropDown.Clear()
        self.userGroupDropDown.InsertItems(groupNameList, 0)

    def onCreate(self, evt):
        if self.userNameInput.GetValue().strip() != '':
            controller = UserController()
            newUser = User(self.userNameInput.GetValue(), self.userGroupDropDown.GetSelection() + 1)
            eid = controller.createUser(newUser)
            if eid == -1:
                wx.MessageBox(u'创建用户失败')
            else:
                newUser.userId = eid

        self.insertSingleUserIntoGrid(newUser)
        self.userNameInput.Clear()
        self.userGroupDropDown.SetSelection(-1)

    def insertSingleUserIntoGrid(self, user):
        self.grid.InsertRows(0, 1)
        self.grid.SetCellValue(0, 0, str(user.userId))
        self.grid.SetCellValue(0, 1, user.userName)
        groupController = GroupController()
        self.grid.SetCellValue(0, 2, groupController.getGroupName(user.userGroup))
        self.grid.SetCellValue(0, 3, u'修改')
        self.grid.SetCellValue(0, 4, u'删除')
        self.grid.AutoSize()
        self.vBox.Layout()

    def onShowRemove(self, evt):
        if not self.removeIsShown:
            self.removeIsShown = True
            self.removeGroupBtn.SetLabelText(u'结束\n操作')
            self.grid.ShowCol(3)
            self.grid.ShowCol(4)
            self.grid.AutoSize()
        else:
            self.removeIsShown = False
            self.removeGroupBtn.SetLabelText(u'修改\n删除')
            self.grid.HideCol(3)
            self.grid.HideCol(4)
            self.grid.AutoSize()

    def onCellChoosen(self, evt):
        if evt.GetCol() == 3:
            # 修改事件
            self.userNameInput.SetValue(self.grid.GetCellValue(evt.GetRow(), 1))
            # GroupController().getUserController.getUser(self.grid.GetCellValue(evt.GetRow(), 0)).userGroup
            self.userGroupDropDown.SetSelection()
            dlg = wx.MessageDialog(None, u'确认要删除员工 [' + self.grid.GetCellValue(evt.GetRow(), 1) + u'] 吗？',
                                   'MessageDialog', wx.OK | wx.CANCEL)
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                # 确认删除
                controller = UserController()
                result = controller.deleteUser(int(self.grid.GetCellValue(evt.GetRow(), 0)))
                if result:
                    wx.MessageBox(u'删除成功')
                    self.refreshGrid()
                else:
                    wx.MessageBox(u'删除失败')
            dlg.Destroy()
        elif evt.GetCol() == 4:
            # 删除事件
            dlg = wx.MessageDialog(None, u'确认要删除员工 [' + self.grid.GetCellValue(evt.GetRow(), 1) + u'] 吗？',
                                   'MessageDialog', wx.OK | wx.CANCEL)
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                # 确认删除
                controller = UserController()
                result = controller.deleteUser(int(self.grid.GetCellValue(evt.GetRow(), 0)))
                if result:
                    wx.MessageBox(u'删除成功')
                    self.refreshGrid()
                else:
                    wx.MessageBox(u'删除失败')
            dlg.Destroy()
