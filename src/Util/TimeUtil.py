# coding=utf-8

import time
import datetime

__author__ = 'yzhou7'

class TimeUtil:
    @staticmethod
    def getToday():
        return time.strftime("%Y-%m-%d", time.localtime())

    @staticmethod
    def isValidDate(date):
        try:
            time.strptime(date, "%Y-%m-%d")
            return True
        except:
            return False

    @staticmethod
    def getDayLength(startDate, endDate):
        start = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        end = datetime.datetime.strptime(endDate, "%Y-%m-%d")
        if start > end:
            return 0
        else:
            return (end - start).days + 1

    @staticmethod
    def getFormatedDate(startDate, delta):
        start = datetime.datetime.strptime(startDate, "%Y-%m-%d")
        return (start + datetime.timedelta(days=delta)).strftime("%Y-%m-%d")


if __name__ == "__main__":
    print(TimeUtil.getToday())

    print(TimeUtil.isValidDate('2004-05-01'))

    print(TimeUtil.isValidDate("2004-02-30"))

    print(TimeUtil.getDayLength('2004-05-01', '2004-05-04'))

    print(TimeUtil.getFormatedDate('2015-05-01', 5))
