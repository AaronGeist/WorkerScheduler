# coding=utf-8

import hashlib
import sqlite3
from src.Constants import Constants
from src.Data.User import User

__author__ = 'yzhou7'


class UserController():
    USER_TABLE_NAME = "user"

    def createUser(self, user):

        try:
            conn = sqlite3.connect(Constants.DATABASE_ROOT_PATH + Constants.UNITED_DATABASE_FILENAME)
            c = conn.cursor()
            c.execute("INSERT INTO " + self.USER_TABLE_NAME + " VALUES ('%s', '%s', %d)" % (
                user.userName, user.password, user.level))
            conn.commit()
        except Exception as e:
            print(str(e))
            return False
        finally:
            conn.close()
        return True

    def getUser(self, userName):
        result = None
        try:
            conn = sqlite3.connect(Constants.DATABASE_ROOT_PATH + Constants.UNITED_DATABASE_FILENAME)
            c = conn.cursor()
            c.execute("SELECT * FROM " + self.USER_TABLE_NAME + " WHERE username='%s'" % userName)
            result = c.fetchone()
        except Exception as e:
            print(str(e))
        finally:
            conn.close()
        if result == None:
            return result
        return User(result[0], result[1], result[2])

    def editUser(self, userName='', password='', level=0):
        isSuccess = True
        try:
            conn = sqlite3.connect(Constants.DATABASE_ROOT_PATH + Constants.UNITED_DATABASE_FILENAME)
            c = conn.cursor()
            c.execute("UPDATE " + self.USER_TABLE_NAME + " WHERE username='%s'" % userName)
            conn.commit()
        except Exception as e:
            print(str(e))
            isSuccess = False
        finally:
            conn.close()
        return isSuccess

    def deleteUser(self, userName):
        isSuccess = True
        try:
            conn = sqlite3.connect(Constants.DATABASE_ROOT_PATH + Constants.UNITED_DATABASE_FILENAME)
            c = conn.cursor()
            c.execute("DELETE FROM " + self.USER_TABLE_NAME + " WHERE username='%s'" % userName)
            conn.commit()
        except Exception as e:
            print(str(e))
            isSuccess = False
        finally:
            conn.close()
        return isSuccess


if __name__ == '__main__':
    c = UserController()
    newUser = User('test', '123', 10)
    print(c.createUser(newUser))
    result = c.getUser('test')
    assert newUser.level == result.level

    assert c.deleteUser('test') == True
    assert c.getUser('test') == None
