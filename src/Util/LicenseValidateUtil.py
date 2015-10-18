# coding=utf-8
import os
import sqlite3

from src.Constants import Constants
from src.Util.TimeUtil import TimeUtil

__author__ = 'yzhou7'


class LicenseValidateUtil():
    LICENSE_TABLE_NAME = 'license'


    @staticmethod
    def validate():
        if Constants.LICENSE_PURCHASED:
            return True

        conn = sqlite3.connect(Constants.DATABASE_ROOT_PATH +
                               LicenseValidateUtil.LICENSE_TABLE_NAME + '.db')
        c = conn.cursor()

        c.execute("CREATE TABLE IF NOT EXISTS " + LicenseValidateUtil.LICENSE_TABLE_NAME +
                  "(startDate VARCHAR[10], version VARCHAR[10])")
        c.execute("SELECT startDate FROM " + LicenseValidateUtil.LICENSE_TABLE_NAME + " WHERE version=" + Constants.APPLICATION_VERSION)
        startDate = c.fetchone()
        if startDate == None:
            c.execute("INSERT INTO " + LicenseValidateUtil.LICENSE_TABLE_NAME +
                      " VALUES ('" + TimeUtil.getToday() + "','" + Constants.APPLICATION_VERSION + "')")
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return TimeUtil.getDayLength(startDate[0], TimeUtil.getToday()) < Constants.MAX_FREE_TRIAL_DAY


if __name__ == '__main__':
    print(LicenseValidateUtil.validate())
