# coding=utf-8

import os
import sqlite3

from src.Constants import Constants
from src.Util.LicenseValidateUtil import LicenseValidateUtil

__author__ = 'yzhou7'


class SystemInitializer:
    def __init__(self):
        pass

    # entry for system init
    @staticmethod
    def initialize():
        SystemInitializer.createDir()
        # SystemInitializer.createDB()
        # SystemInitializer.createFiles()
        return LicenseValidateUtil.validate()

    @staticmethod
    def createDir():
        validationPath = os.environ['LOCALAPPDATA'] + Constants.PATH_DELIMETER + Constants.APPLICATION_NAME
        if not os.path.exists(validationPath):
            os.makedirs(validationPath)

    # @staticmethod
    # def createDB():
    #     conn = sqlite3.connect(Constants.UNITED_DATABASE_PATH)
    #     cur = conn.cursor()
    #     cur.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR[30], usergroup INTEGER DEFAULT 0)")
    #     cur.execute("CREATE TABLE IF NOT EXISTS class (id INTEGER PRIMARY KEY AUTOINCREMENT, groupname VARCHAR[30], workhour INTEGER DEFAULT 8)")
    #     cur.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR[20], usergroup INTEGER DEFAULT 0)")
    #     conn.commit()
    #     conn.close()
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
