# coding=utf-8
__author__ = 'yzhou7'


class User():
    def __init__(self, userName='', userGroup=0, userDesc='', userId=0):
        self.userName = userName
        self.userId = int(userId)
        self.userGroup = int(userGroup)
        self.userDesc = userDesc



