from BaseDAL import BaseDAL
from src.Data.DailyData import DailyData
from src.Constants import Constants

__author__ = 'yzhou7'


# this class is DAL layer to load data for buyer, including
# 1. single date
# 2. all dates

class DailyDataDAL(BaseDAL):
    MATCH_ALL_DATE = '*'
    MATCH_ALL_USER = "*"

    @staticmethod
    def fetchAll():
        return DailyDataDAL.fetchAllByDate(DailyDataDAL.MATCH_ALL_DATE)

    @staticmethod
    def fetchAllByDate(date, filePath = ''):
        if filePath == '':
            filePath = Constants.BUYER_FILE_PATH
        if not BaseDAL.checkFileExist(filePath):
            # TODO fix exception
            # raise FileNotExistException(Constants.BUYER_FILE_PATH)
            print "file not exist for: " + filePath
            return DailyData("", dict())

        lines = BaseDAL.readAll(filePath)
        return DailyDataDAL.parse(lines, date)

    @staticmethod
    def fetchByNameDate(date, userName):
        if not BaseDAL.checkFileExist(Constants.BUYER_FILE_PATH):
            # TODO fix exception
            # raise FileNotExistException(Constants.BUYER_FILE_PATH)
            print "file not exist for: " + Constants.BUYER_FILE_PATH
            return list()

        lines = BaseDAL.readAll(Constants.BUYER_FILE_PATH)
        return DailyDataDAL.parse(lines, date, userName)

    @staticmethod
    def parse(lines, targetDate, targetUserName = '*'):
        date = ''
        dailyScore = dict()

        # parse line into DailyData structure
        for line in lines:
            items = line.strip().split("|")
            if len(items) < 3:
                print "line is invalid: " + line
                break
            userName = items[0].strip()
            date = items[1].strip()
            scores = items[2].strip()

            if targetUserName != DailyDataDAL.MATCH_ALL_USER \
                    and userName != targetUserName:
                continue

            if date == '':
                date = targetDate

            if date != targetDate:
                continue

            if dailyScore.has_key(userName):
                dailyScore[userName].extend(scores.split(Constants.SCORE_DELIMITER))
            else:
                dailyScore[userName] = scores.split(Constants.SCORE_DELIMITER)

        return DailyData(date, dailyScore)

    @staticmethod
    def persistAll(dailyData, filePath = ''):
        if filePath == '':
            filePath = Constants.BUYER_FILE_PATH
        date = dailyData.date
        dailyScore = dailyData.dailyScore
        lines = list()
        for (userName, scores) in dailyScore.items():
            lines.append(userName + "|" + date + "|" + " ".join(map(str, scores)))
        DailyDataDAL.writeAll(filePath, lines)

if __name__ == "__main__":
    lines = ['aa|2005-09-01|100 200',
             'aa|2005-09-02|300',
             "bb|2005-09-01|21",
             "bb|2005-09-01|2 2 222"]

    # print "no date filter"
    # print DailyDataDAL.parse(lines, "*").__dict__

    print "filter with date 2005-09-01"
    print DailyDataDAL.parse(lines, "2005-09-01").__dict__

    print "filter with date 2005-09-01 and name aa"
    print DailyDataDAL.parse(lines, "2005-09-01", "aa").__dict__

    DailyDataDAL.persistAll(DailyDataDAL.parse(lines, "2005-09-01", "aa"), "test.txt")

    print str(DailyDataDAL.fetchAllByDate('2005-09-01', 'test.txt').dailyScore)
