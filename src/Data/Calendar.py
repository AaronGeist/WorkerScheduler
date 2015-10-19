# coding=utf-8
__author__ = 'yzhou7'


class Calendar():
    def __init__(self, calName='', scheduleResult={}, startDate='', calId=0):
        self.calId = calId
        self.calName = calName
        self.scheduleResult = scheduleResult
        self.startDate = startDate
