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

    def createCalendar(self, calendar):
        try:
            eid = self.getTable().insert(
                {'calName': calendar.calName, 'calendar': calendar.calendar, 'workerList': calendar.workerList,
                 'groupId': calendar.groupId, 'workLoad': calendar.workLoad, 'startDate': calendar.startDate})
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
        return Calendar(calName=result['calName'], calendar=result['calendar'], workerList=result['workerList'],
                        groupId=result['groupId'], workLoad=result['workLoad'], startDate=result['startDate'], calId=result.eid)

    def getAllCalendar(self):
        result = None
        try:
            result = self.getTable().all()
        except Exception as e:
            logging.exception(str(e))
        if result == None or len(result) == 0:
            return result
        return list(map(lambda x: Calendar(calName=x['calName'], calendar=x['calendar'], workerList=x['workerList'],
                        groupId=x['groupId'], workLoad=x['workLoad'], startDate=x['startDate'], calId=x.eid), result))

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
    newCal = Calendar('test', {'1': [1, 2, 3, 4]}, [1, 2, 3, 4], 1, 4, '2015-05-05')
    eid = c.createCalendar(newCal)
    assert eid > 0
    print(eid)
    result = c.getCalendar(eid)
    assert result != None
    print(result.calName)
    print(result.calendar)
    assert newCal.calName == result.calName
    assert newCal.calendar == result.calendar
    assert newCal.workerList == result.workerList
    assert newCal.groupId == result.groupId
    assert newCal.workLoad == result.workLoad
    assert newCal.startDate == result.startDate

    c.deleteCalendar(eid)
    assert c.getCalendar(eid) == None
