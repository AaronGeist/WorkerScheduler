from BaseDAL import BaseDAL
from src.Exception import FileNotExistException
from src.Data.BuyerData import BuyerData
from src.Constants import Constants

__author__ = 'yzhou7'


# this class is DAL layer to load data for buyer, including
# 1. single person
# 2. all persons

class BuyerDAL(BaseDAL):
    MATCH_ALL_DATE = '*'

    @staticmethod
    def fetchAll():
        return BuyerDAL.fetchAllByDate(BuyerDAL.MATCH_ALL_DATE)

    @staticmethod
    def fetchAllByDate(date):
        if not BaseDAL.checkFileExist(Constants.BUYER_FILE_PATH):
            # TODO fix exception
            # raise FileNotExistException(Constants.BUYER_FILE_PATH)
            print "file not exist for: " + Constants.BUYER_FILE_PATH
            return list()

        lines = BaseDAL.readAll(Constants.BUYER_FILE_PATH)
        return BuyerDAL.parse(lines, date)

    @staticmethod
    def parse(lines, selectedDate):
        buyerDict = dict()

        # parse line into BuyerData structure
        for line in lines:
            items = line.strip().split("|")
            if len(items) < 3:
                print "line is invalid: " + line
                break
            buyerID = items[0]
            buyerName = items[1]
            date = items[2]
            scores = items[3]

            if selectedDate != BuyerDAL.MATCH_ALL_DATE \
                    and date != selectedDate:
                continue

            if buyerDict.has_key(buyerID):
                buyerDict[buyerID].addScores(date, scores.split(Constants.SCORE_DELIMITER))
            else:
                buyerScore = dict()
                buyerScore[date] = scores.split(Constants.SCORE_DELIMITER)
                buyerDict[buyerID] = BuyerData(buyerID, buyerName, buyerScore)

        return buyerDict.values()


if __name__ == "__main__":
    lines = ['1|aa|20050901|100 200',
             '1|aa|20050902|300',
             "2|bb|20050101|2 2 222"]

    print "no date filter"
    for i in BuyerDAL.parse(lines, "*"):
        print i.__dict__

    print "filter with date 20050901"
    for i in BuyerDAL.parse(lines, "20050901"):
        print i.__dict__