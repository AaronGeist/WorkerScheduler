from distutils.core import setup
import py2exe

__author__ = 'yzhou7'

setup(
    windows=[{
         'script': 'Main.py',
        'icon_resources': [(1, '.\Resource\panda1.ico')]
    }]
)
