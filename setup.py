# coding=utf-8
from distutils.core import setup
import py2exe

__author__ = 'yzhou7'

options = {'py2exe': {
    "optimize": 2,
    "compressed": 1
}}
setup(
    windows=[{
        'script': 'Main.py',
        'icon_resources': [(1, '.\Resource\panda.ico')],
    }],
    version='1.0',
    zipfile=None,
    options=options
)
