__author__ = 'yzhou7'

import wx
import wx.grid


class ScheduleData(wx.grid.PyGridTableBase):

    def __init__(self):
        wx.grid.PyGridTableBase.__init__(self)
        self._cols = ['日期', '出勤人员名单', '休息人员名单']
        self._data = list()
        self._highlighted = set()
    #
    # def SetRowLableValue(self, row, value):
    #     self._rows[row] = value
    #
    # def GetRowLabelValue(self, row):
    #     return self._rows[row]

    def SetColLabelValue(self, col, value):
        self._cols[col] = value

    def GetColLabelValue(self, col):
        return self._cols[col]

    def GetNumberRows(self):
        return len(self._data)

    def GetNumberCols(self):
        return len(self._cols)

    def GetValue(self, row, col):
        return self._data[row][col]

    def SetValue(self, row, col, val):
        self._data[row][col] = val

    def GetAttr(self, row, col, kind):
        attr = wx.grid.GridCellAttr()
        attr.SetBackgroundColour(wx.GREEN if row in self._highlighted else wx.WHITE)
        return attr

    def set_value(self, row, col, val):
        self._highlighted.add(row)
        self.SetValue(row, col, val)

    def InsertRows(self, lineList):
        self._data.extend(lineList)

    def UpdateTable(self, lineList):
        self._data = list()
        self.InsertRows(lineList)

    def Clear(self):
        self._data = list()
        self._highlighted = set()
