# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  s0nder
@Email          :  wylsyr@gmail.com
------------------------------------
@File           :  main.py
@CreateTime     :  2021/1/26/0026 20:08
@Version        :  1.0
@Description    :
------------------------------------
@Software       :  VSCode
"""

# here put the import lib
import os, sys, time, re, requests, json
from core.window_login import login_window
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = login_window(mode=0)
    login_window.show()
    sys.exit(app.exec_())
