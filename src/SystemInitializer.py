# coding=utf-8
import os

from tinydb import TinyDB, where
from src.Util.TimeUtil import TimeUtil

__author__ = 'yzhou7'


class SystemInitializer:
    def __init__(self):
        pass

    # entry for system init
    @staticmethod
    def initialize():
        db = TinyDB(os.environ['LOCALAPPDATA'] + '\\scheduler.dat')
        startDate = db.search(where('startDate'))
        if len(startDate) > 0:
            if TimeUtil.getDayLength(startDate[0]['startDate'], TimeUtil.getToday()) > 2:
                return False
            else:
                return True
        else:
            db.insert({'startDate': TimeUtil.getToday()})
            return True

        # SystemInitializer.createDir()
        # SystemInitializer.createFiles()

    # @staticmethod
    # def createDir():
    #     if not os.path.exists(Constants.DATA_DIR):
    #         os.makedirs(Constants.DATA_DIR)
    #
    # @staticmethod
    # def createFiles():
    #     SystemInitializer.createBuyerFile()
    #     SystemInitializer.createSellerFile()
    #
    # @staticmethod
    # def createBuyerFile():
    #     if not os.path.exists(Constants.BUYER_FILE_PATH):
    #         file = open(Constants.BUYER_FILE_PATH, "w")
    #         file.close()
    #
    # @staticmethod
    # def createSellerFile():
    #     if not os.path.exists(Constants.SELLER_FILE_PATH):
    #         file = open(Constants.SELLER_FILE_PATH, "w")
    #         file.close()

if __name__ == '__main__':
    print(SystemInitializer.initialize())
