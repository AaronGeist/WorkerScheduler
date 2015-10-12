# coding=utf-8
import os

__author__ = 'yzhou7'


class Constants:

    # System level
    MAIN_WINDOW_TITLE = u'排班助手V1'
    APPLICATION_NAME = u'MyPocket'
    APPLICATION_VERSION = u'0.1'

    # License
    LICENSE_PURCHASED = True

    PATH_DELIMETER = '\\'

    # Database
    DATABASE_ROOT_PATH = os.environ['LOCALAPPDATA'] + PATH_DELIMETER + APPLICATION_NAME + PATH_DELIMETER
    UNITED_DATABASE_FILENAME = APPLICATION_NAME + '.db'
    UNITED_DATABASE_PATH = DATABASE_ROOT_PATH + UNITED_DATABASE_FILENAME
