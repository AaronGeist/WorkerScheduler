# coding=utf-8
__author__ = 'yzhou7'

import os
import cPickle

class BaseDAL:
    ACCESS_READ_ONLY = "r"
    ACCESS_WRITE_ONLY = "a"

    @staticmethod
    def checkFileExist(file_path):
        return os.path.exists(file_path) and os.path.isfile(file_path)

    @staticmethod
    def loadFile(file_path, access_mode):
        file = open(file_path, access_mode)
        return file

    # return lines in list
    @staticmethod
    def readAll(file_path):
        file = BaseDAL.loadFile(file_path, BaseDAL.ACCESS_READ_ONLY)
        result = list()
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            # skip empty line
            if len(line):
                result.append(line)
        file.close()

        # result.sort()
        return result

    @staticmethod
    def readAllInCpickle(file_path):
        file = BaseDAL.loadFile(file_path, BaseDAL.ACCESS_READ_ONLY)
        result = cPickle.load(file)
        file.close()
        return result

    @staticmethod
    def readLine(file_path):
        file = BaseDAL.loadFile(file_path, BaseDAL.ACCESS_READ_ONLY)
        result = file.readline()
        return result

    @staticmethod
    def writeAll(file_path, line_list):
        file = BaseDAL.loadFile(file_path, BaseDAL.ACCESS_WRITE_ONLY)
        file.writelines([line.strip() + '\n' for line in line_list])
        file.close()
        return

    @staticmethod
    def writeAllInCpickle(file_path, dict):
        file = BaseDAL.loadFile(file_path, BaseDAL.ACCESS_WRITE_ONLY)
        # json.dump(dict, file)
        cPickle.dump(dict, file)
        file.close()
        return
