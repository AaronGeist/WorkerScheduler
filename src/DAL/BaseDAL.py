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
        file = codecs.open(file_path, BaseDAL.ACCESS_READ_ONLY)
        result = list()
        lines = file.readlines()
        if lines:
            # coding = chardet.detect(lines[0])
            for line in lines:
                line = line.strip()
                # skip empty line
                if len(line):
                    # line = line.decode(coding['encoding']).encode(BaseDAL.DEFAULT_CODING)
                    result.append(line)
        file.close()

        # result.sort()
        return result

    @staticmethod
    def readLine(file_path):
        file = BaseDAL.loadFile(file_path, BaseDAL.ACCESS_READ_ONLY)
        result = file.readline()
        return result

    @staticmethod
    def writeAll(file_path, line_list, coding=DEFAULT_CODING_WITH_SIG):
        file = codecs.open(file_path, BaseDAL.ACCESS_WRITE_ONLY, coding)
        file.writelines([line.strip() + '\n' for line in line_list])
        file.flush()
        file.close()
        return


if __name__ == '__main__':
    path = 'c:\\Users\\yzhou7\\Desktop\\名单-ansi.txt'

    # with codecs.open(path, 'r', 'utf_8_sig') as f:
    #     lines = f.readlines()
    #     print(type(lines))
    #     print(lines)
    lines = BaseDAL.readAll(path)
    print(type(lines))
    result = map(lambda worker: worker, lines)
    print(list(result))

