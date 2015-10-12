# coding=utf-8
import time
import datetime

__author__ = 'yzhou7'

'''
This class is designed for time/date related operations
'''


class TimeUtil:
    # Get today's date in string format YY-MM-DD
    @staticmethod
    def getToday():
        return time.strftime("%Y-%m-%d", time.localtime())

    # Validate date in format YY-MM-DD
    # return false if invalid
    @staticmethod
    def isValidDate(date):
        try:
            time.strptime(date, "%Y-%m-%d")
            return True
        except:
            return False

    # Get length between two given date (in YY-MM-DD format)
    # will include both start and end date, eg. Oct1-Oct4 is 4 days
    # return 0 if start date is later than end date
    @staticmethod
    def getDayLength(startDate, endDate):
        start = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        end = datetime.datetime.strptime(endDate, "%Y-%m-%d")
        if start > end:
            return 0
        else:
            return (end - start).days + 1

    # Get date string since N days from start date
    @staticmethod
    def getFormatedDate(startDate, delta):
        start = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        return (start + datetime.timedelta(days=delta)).strftime("%Y-%m-%d")

    @staticmethod
    def getMonday(date):
        start = datetime.datetime.strptime(date, "%Y-%m-%d")
        weekday = start.weekday()
        if weekday != 0:
            return TimeUtil.getFormatedDate(date, -weekday)
        else:
            return date

    @staticmethod
    def getSunday(date):
        start = datetime.datetime.strptime(date, "%Y-%m-%d")
        weekday = start.weekday()
        if weekday != 6:
            return TimeUtil.getFormatedDate(date, 6 - weekday)
        else:
            return date

    @staticmethod
    def isWeekend(date):
        start = datetime.datetime.strptime(date, "%Y-%m-%d")
        weekday = start.weekday()
        return weekday == 5 or weekday == 6


if __name__ == "__main__":
    print(TimeUtil.getToday())

    print(TimeUtil.isValidDate('2004-05-01'))

    # invalid date
    print(TimeUtil.isValidDate("2004-02-30"))

    # 4 days
    print(TimeUtil.getDayLength('2004-05-01', '2004-05-04'))

    print(TimeUtil.getFormatedDate('2015-05-01', 5))

    print("get monday")
    print(TimeUtil.getMonday('2015-10-11'))
    print(TimeUtil.getMonday('2015-10-10'))
    print(TimeUtil.getMonday('2015-10-09'))
    print(TimeUtil.getMonday('2015-10-08'))
    print(TimeUtil.getMonday('2015-10-07'))
    print(TimeUtil.getMonday('2015-10-06'))
    print(TimeUtil.getMonday('2015-10-05'))

    print('get sunday')
    print(TimeUtil.getSunday('2015-10-05'))
    print(TimeUtil.getSunday('2015-10-06'))
    print(TimeUtil.getSunday('2015-10-07'))
    print(TimeUtil.getSunday('2015-10-08'))
    print(TimeUtil.getSunday('2015-10-09'))
    print(TimeUtil.getSunday('2015-10-10'))
    print(TimeUtil.getSunday('2015-10-11'))

    print(TimeUtil.isWeekend(TimeUtil.getSunday('2015-10-11')))
    print(TimeUtil.isWeekend(TimeUtil.getMonday('2015-10-11')))
