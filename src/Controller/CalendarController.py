# coding=utf-8
import logging

from tinydb import TinyDB
from src.Constants import Constants
from src.Data.Calendar import Calendar
from src.Data.Group import Group

__author__ = 'yzhou7'


class CalendarController():
    TABLE_NAME = "calendar"

    def getTable(self):
        db = TinyDB(Constants.DATABASE_ROOT_PATH + Constants.UNITED_DATABASE_FILENAME)
        return db.table(self.TABLE_NAME)

    def parseScheduleResult(self, scheduleResult):
        newResult = list()
        for result in scheduleResult:
            calendar = result[0]
            workers = result[1]
            group = result[2]
            newResult.append([calendar, workers, group.groupName, group.groupId, group.workHour, group.workLoad])
        return newResult

    def generateScheduleResult(self, scheduleResult):
        newResult = list()
        for result in scheduleResult:
            calendar = result[0]
            workers = result[1]
            group = Group(groupName=result[2], groupId=result[3], workHour=result[4], workLoad=result[5])
            newResult.append([calendar, workers, group])
        return newResult

    def createCalendar(self, calendar):
        try:
            eid = self.getTable().insert(
                {'calName': calendar.calName, 'scheduleResult': self.parseScheduleResult(calendar.scheduleResult),
                 'startDate': calendar.startDate})
        except Exception as e:
            logging.exception(str(e))
            return -1
        return eid

    def getCalendar(self, id):
        result = None
        try:
            result = self.getTable().get(eid=id)
        except Exception as e:
            logging.exception(str(e))
        if result == None:
            return result
        return Calendar(calName=result['calName'], scheduleResult=self.generateScheduleResult(result['scheduleResult']),
                        startDate=result['startDate'], calId=result.eid)

    def getAllCalendar(self):
        result = None
        try:
            result = self.getTable().all()
        except Exception as e:
            logging.exception(str(e))
        if result == None or len(result) == 0:
            return result
        return list(map(lambda x: Calendar(calName=x['calName'], scheduleResult=self.generateScheduleResult(x['scheduleResult']),
                                           startDate=x['startDate'],
                                           calId=x.eid), result))

    def deleteCalendar(self, id):
        isSuccess = True
        try:
            self.getTable().remove(eids=[id])
        except Exception as e:
            logging.exception(str(e))
            isSuccess = False
        return isSuccess


if __name__ == '__main__':
    c = CalendarController()
    newCal = Calendar('test', [[{'1': [1, 2, 3, 4]}, [1, 2, 3, 4], Group('test', '', 1, 4, 2)]], '2015-05-05')
    eid = c.createCalendar(newCal)
    assert eid > 0
    print(eid)
    result = c.getCalendar(eid)
    assert result != None
    print(result.calName)
    print(result.scheduleResult)
    assert newCal.calName == result.calName
    assert newCal.scheduleResult[0][0] == result.scheduleResult[0][0]
    assert newCal.scheduleResult[0][1] == result.scheduleResult[0][1]
    assert newCal.scheduleResult[0][2].groupId == result.scheduleResult[0][2].groupId
    assert newCal.scheduleResult[0][2].groupName == result.scheduleResult[0][2].groupName
    assert newCal.scheduleResult[0][2].workLoad == result.scheduleResult[0][2].workLoad
    assert newCal.scheduleResult[0][2].workHour == result.scheduleResult[0][2].workHour
    assert newCal.startDate == result.startDate

    c.deleteCalendar(eid)
    assert c.getCalendar(eid) == None
