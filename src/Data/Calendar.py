# coding=utf-8
__author__ = 'yzhou7'


class Calendar():
    def __init__(self, calName='', calendar={}, workerList=[], groupId=0, workLoad=0, startDate='', calId=0):
        self.calId = calId
        self.calName = calName
        self.calendar = calendar
        self.workerList = workerList
        self.groupId = groupId
        self.workLoad = workLoad
        self.startDate = startDate
