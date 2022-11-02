#!/usr/bin/env python
# -*- coding: utf-8 -*-

# see https://github.com/heartexlabs/labelImg

import os,sys
from labelImg.labelImg import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
def get_main_app():
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    app = QApplication([])
    app.setApplicationName("labelImgTiled")
    #app.setWindowIcon(new_icon("app"))
    class_file="./predefined_classes.txt"
    save_dir="./"
    
    
    # Usage : labelImg.py image classFile saveDir
    win = MainWindow(default_filename="inputfile",
                     default_prefdef_class_file=class_file,
                     default_save_dir=save_dir)
    win.settings["SETTING_LABEL_FILE_FORMAT"]=LabelFileFormat.YOLO
    win.show()
    return app, win

def main():
    """construct main app and run it"""
    app, _win = get_main_app()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
