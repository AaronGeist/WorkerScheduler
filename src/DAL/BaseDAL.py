# coding=utf-8

import os
import codecs

__author__ = 'yzhou7'


class BaseDAL:
    ACCESS_READ_ONLY = "r"
    ACCESS_WRITE_ONLY = "w"
    DEFAULT_CODING = 'utf-8'
    DEFAULT_CODING_WITH_SIG = 'utf_8_sig'

    @staticmethod
    def checkFileExist(file_path):
        return os.path.exists(file_path) and os.path.isfile(file_path)

    @staticmethod
    def loadFile(file_path, access_mode, coding=DEFAULT_CODING_WITH_SIG):
        file = codecs.open(file_path, access_mode, coding)
        return file

    # return lines in list
    @staticmethod
    def readAll(file_path):
        result = list()
        try:
            # support for default ascii format
            with codecs.open(file_path, BaseDAL.ACCESS_READ_ONLY) as file:
                lines = file.readlines()
        except Exception as e:
            print(str(e))
            try:
                # support for utf-8 with sig
                with codecs.open(file_path, BaseDAL.ACCESS_READ_ONLY, BaseDAL.DEFAULT_CODING_WITH_SIG) as file:
                    lines = file.readlines()
            except Exception as ee:
                print(str(ee))
                return result

        if lines:
            for line in lines:
                line = line.strip()
                # skip empty line
                if len(line):
                    result.append(line)

        return result

    @staticmethod
    def readLine(file_path):
        result = ''
        try:
            # support for default ascii format
            with codecs.open(file_path, BaseDAL.ACCESS_READ_ONLY) as file:
                result = file.readline()
        except Exception as e:
            print(str(e))
            try:
                # support for utf-8 with sig
                with codecs.open(file_path, BaseDAL.ACCESS_READ_ONLY, BaseDAL.DEFAULT_CODING_WITH_SIG) as file:
                    result = file.readline()
            except Exception as ee:
                print(str(ee))
                return result

        return result

    @staticmethod
    def writeAll(file_path, line_list, coding=DEFAULT_CODING_WITH_SIG):
        with codecs.open(file_path, BaseDAL.ACCESS_WRITE_ONLY, coding) as file:
            file.writelines([line.strip() + '\n' for line in line_list])
            file.flush()


if __name__ == '__main__':
    path = '..\\TestResource\\name-ansi.txt'

    lines = BaseDAL.readAll(path)
    result = map(lambda worker: worker, lines)
    print(list(result))
    assert len(list(result)) <= 0

    path = '..\\TestResource\\name-utf8.txt'

    lines = BaseDAL.readAll(path)
    result = map(lambda worker: worker, lines)
    print(list(result))
    assert len(list(result)) <= 0
