__author__ = 'yzhou7'

import time


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

if __name__ == "__main__":
    print TimeUtil.getToday()

    print TimeUtil.isValidDate('2004-05-01')

    print TimeUtil.isValidDate("2004-02-30")
