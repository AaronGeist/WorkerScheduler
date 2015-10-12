# coding=utf-8
import re

from tinydb import TinyDB, where
from src.Constants import Constants
from src.Data.User import User

__author__ = 'yzhou7'


class UserController():
    TABLE_NAME = "user"

    def getTable(self):
        db = TinyDB(Constants.DATABASE_ROOT_PATH + Constants.UNITED_DATABASE_FILENAME)
        return db.table(self.TABLE_NAME)

    def createUser(self, user):
        try:
            eid = self.getTable().insert({'userName': user.userName, 'userGroup': user.userGroup})
        except Exception as e:
            print(str(e))
            return -1
        return eid

    def getUser(self, id):
        result = None
        try:
            result = self.getTable().get(eid=id)
        except Exception as e:
            print(str(e))
        if result == None:
            return result
        return User(userName=result['userName'], userGroup=result['userGroup'], userId=result.eid)

    def getAllUser(self):
        result = None
        try:
            result = self.getTable().all()
        except Exception as e:
            print(str(e))
        if result == None or len(result) == 0:
            return result
        return list(map(lambda x: User(userName=x['userName'], userGroup=x['userGroup'], userId=x.eid), result))

    def getAllUserByGroup(self, groupId):
        result = None
        try:
            result = self.getTable().search(where('userGroup') == groupId)
        except Exception as e:
            print(str(e))
        if result == None or len(result) == 0:
            return result
        return list(map(lambda x: User(userName=x['userName'], userGroup=x['userGroup'], userId=x.eid), result))

    def editUser(self, id, userName='', userGroup=-1):
        isSuccess = True
        try:
            table = self.getTable()
            if userName != '':
                table.update({'userName': userName}, eids=[id])
            if userGroup != -1:
                table.update({'userGroup': userGroup}, eids=[id])
        except Exception as e:
            print(str(e))
            isSuccess = False
        return isSuccess

    def removeGroup(self, userGroup):
        self.getTable().update({'userGroup': -1}, where('userGroup') == userGroup)

    def deleteUser(self, id):
        isSuccess = True
        try:
            self.getTable().remove(eids=[id])
        except Exception as e:
            print(str(e))
            isSuccess = False
        return isSuccess


if __name__ == '__main__':
    c = UserController()
    c.getTable().purge()
    newUser = User('test', 123)
    eid = c.createUser(newUser)
    assert eid > 0
    print(eid)
    result = c.getUser(eid)
    assert result != None
    print(result.userName)
    print(result.userGroup)
    assert newUser.userName == result.userName
    assert newUser.userGroup == result.userGroup

    result = c.getAllUser()
    assert result != None
    assert len(result) == 1
    print(result[0].userName)
    print(result[0].userGroup)
    assert newUser.userName == result[0].userName
    assert newUser.userGroup == result[0].userGroup

    result = c.getAllUserByGroup(123)
    assert result != None
    assert len(result) == 1
    print(result[0].userName)
    print(result[0].userGroup)
    assert newUser.userName == result[0].userName
    assert newUser.userGroup == result[0].userGroup

    c.editUser(eid, 'bbbb', 567)
    result = c.getUser(eid)
    assert result.userName == 'bbbb'

    c.removeGroup(567)
    result = c.getUser(eid)
    assert result.userGroup == -1
    c.deleteUser(eid)
    assert c.getUser(eid) == None




