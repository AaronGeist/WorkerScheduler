__author__ = 'yzhou7'

class WorkerStats:

    def __init__(self, targetTotalWorkDay):
        self.workDayLeft = targetTotalWorkDay
        self.arrangedWorkDay = list()

class ArrangedWorkDay:

    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate