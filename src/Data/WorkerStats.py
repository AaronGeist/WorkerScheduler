# coding=utf-8
__author__ = 'yzhou7'

class WorkerStats:

    def __init__(self, workerId, targetTotalWorkDay):
        self.workerId = workerId
        self.workDayLeft = targetTotalWorkDay
        self.arrangedWorkDay = list()
        self.previousDate = -1
        self.accumulatedWorkDay = 0
        self.totalWorkDay = 0

class ArrangedWorkDay:

    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate