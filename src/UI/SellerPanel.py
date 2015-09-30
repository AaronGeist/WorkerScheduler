from src.Strategy.ScoreCalculation import ScoreCalculation

__author__ = 'yzhou7'

import wx

from src.DAL.DailyDataDAL import DailyDataDAL
from src.Util.TimeUtil import TimeUtil


class SellerPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.initUI()
        self.SetBackgroundColour("white")
        self.Show(True)

    def initUI(self):
        self.vBox = wx.BoxSizer(wx.VERTICAL)

        self.setupDateInput()

        self.SetSizer(self.vBox)
        self.vBox.Layout()

    def setupDateInput(self):
        sizer = wx.GridBagSizer(4, 4)
        dateText = wx.StaticText(self, label='日期')
        sizer.Add(dateText, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.dateInput = wx.TextCtrl(self, value=TimeUtil.getToday(), style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.onSearchDate, self.dateInput)
        sizer.Add(self.dateInput, pos=(0, 1),
                  flag=wx.TOP | wx.LEFT, border=12)

        self.calculateButton = wx.Button(self, label='计算一天战况', size=(100, 30))
        sizer.Add(self.calculateButton, pos=(0, 2), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=12)
        self.calculateButton.Enable(True)
        self.Bind(wx.EVT_TEXT, self.OnEnter, self.dateInput)
        self.Bind(wx.EVT_BUTTON, self.onSearchDate, self.calculateButton)

        self.warnMsg = wx.StaticText(self, label='非法日期，请重新输入')
        self.warnMsg.SetForegroundColour('red')
        sizer.Add(self.warnMsg, pos=(0, 3), flag=wx.TOP | wx.LEFT, border=15)
        self.warnMsg.Hide()

        scoreText = wx.StaticText(self, label='盈亏')
        sizer.Add(scoreText, pos=(1, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.score = wx.StaticText(self, label='0')
        sizer.Add(self.score, pos=(1, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT, border=15)

        self.vBox.Add(sizer, flag=wx.ALIGN_TOP, border=10)

    def OnEnter(self, evt):
        if TimeUtil.isValidDate(self.dateInput.GetValue()):
            self.warnMsg.Hide()
            self.calculateButton.Enable(True)
        else:
            self.warnMsg.Show()
            # re-layout
            self.vBox.Layout()
            self.calculateButton.Enable(False)

    def onSearchDate(self, evt):
        dailyData = DailyDataDAL.fetchAllByDate(self.dateInput.GetValue())

        scoreSum = 0
        for (userName, scores) in dailyData.dailyScore.items():
            scoreSum -= ScoreCalculation.calculateTotal(scores)
        self.score.SetLabel(str(scoreSum))

