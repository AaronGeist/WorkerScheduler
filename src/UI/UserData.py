__author__ = 'yzhou7'

import wx
import wx.grid


# Class to display user data in grid for a selected date
class UserGridData(wx.grid.PyGridTableBase):
    _cols = ["ÓÃ»§Ãû"]
    _data = list()
    _highlighted = set()

    def GetColLabelValue(self, col):
        return self._cols[col]

    def GetNumberRows(self):
        return len(self._data)

    def GetNumberCols(self):
        return len(self._cols)

    def GetValue(self, row, col):
        return self._data[row]

    def SetValue(self, row, col, val):
        self._data[row] = val

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
