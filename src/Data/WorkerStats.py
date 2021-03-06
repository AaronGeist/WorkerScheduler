# coding=utf-8
__author__ = 'yzhou7'


class WorkerStats:
    def __init__(self, targetTotalWorkDay):
        self.workDayLeft = targetTotalWorkDay
        self.arrangedWorkDay = list()
        self.startDateMap = dict()
        self.endDateMap = dict()

        self.previousWorkDate = -1
        self.accumulatedWorkDay = 0
        self.previousRestDate = -1
        self.accumulatedRestDay = 0
        self.preArrangedWorkDate = targetTotalWorkDay


class ArrangedWorkDay:
    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate