# coding=utf-8

from tinydb import TinyDB
from src.Constants import Constants
from src.Data.Group import Group

__author__ = 'yzhou7'


class GroupController():
    TABLE_NAME = "group"

    def getTable(self):
        db = TinyDB(Constants.DATABASE_ROOT_PATH + Constants.UNITED_DATABASE_FILENAME)
        return db.table(self.TABLE_NAME)

    def createGroup(self, group):
        try:
            eid = self.getTable().insert({'groupName': group.groupName, 'groupDesc': group.groupDesc, 'workHour': group.workHour})
        except Exception as e:
            print(str(e))
            return -1
        return eid

    def getGroup(self, id):
        result = None
        try:
            result = self.getTable().get(eid=id)
        except Exception as e:
            print(str(e))
        if result == None:
            return result
        return Group(groupName=result['groupName'], groupDesc=result['groupDesc'], workHour=result['workHour'], groupId=result.eid)

    def getGroupName(self, id):
        group = self.getGroup(id)
        if group == None:
            return u'未分组'
        else:
            return group.groupName

    def getAllGroup(self):
        result = None
        try:
            result = self.getTable().all()
        except Exception as e:
            print(str(e))
        if result == None or len(result) == 0:
            return result
        return list(map(lambda x: Group(groupName=x['groupName'], groupDesc=x['groupDesc'], workHour=x['workHour'], groupId=x.eid), result))

    def editGroup(self, id, groupName='', groupDesc='', workHour=-1):
        isSuccess = True
        try:
            table = self.getTable()
            if groupName != '':
                table.update({'groupName': groupName}, eids=[id])
            if groupDesc != '':
                table.update({'groupDesc': groupDesc}, eids=[id])
            if workHour != -1:
                table.update({'workHour': workHour}, eids=[id])
        except Exception as e:
            print(str(e))
            isSuccess = False
        return isSuccess

    def deleteGroup(self, id):
        isSuccess = True
        try:
            self.getTable().remove(eids=[id])
        except Exception as e:
            print(str(e))
            isSuccess = False
        return isSuccess


if __name__ == '__main__':
    c = GroupController()
    newGroup = Group('test', "just for test", 7)
    eid = c.createGroup(newGroup)
    assert eid > 0
    print(eid)
    result = c.getGroup(eid)
    assert result != None
    print(result.groupName)
    print(result.groupDesc)
    print(result.workHour)
    assert newGroup.groupName == result.groupName
    assert newGroup.groupDesc == result.groupDesc
    assert newGroup.workHour == result.workHour

    c.editGroup(eid, groupName='bbbb', workHour=567)
    result = c.getGroup(eid)
    assert result.groupName == 'bbbb'
    # c.deleteGroup(eid)
    # assert c.getGroup(eid) == None


