# coding=utf-8

__author__ = 'yzhou7'

class FileNotExistException(Exception):
    def __init__(self, args):
        self.args = args
