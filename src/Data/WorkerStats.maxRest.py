# coding=utf-8
__author__ = 'yzhou7'

class WorkerStats:
    def __init__(self, workerId, totalRestDay, totalRestWeekendDay):
        self.workerId = workerId
        self.restDayLeftNum = totalRestDay
        self.restWeekendLeftNum = totalRestWeekendDay
        self.arrangedRestDay = list()
        self.previousRestEndDate = -1
        self.accumulatedRestDayNum = 0

class ArrangedWorkDay:
    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate