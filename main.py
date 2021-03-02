# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  sqandan
@Email          :  aadmin@111.com
------------------------------------
@File           :  main.py
@CreateTime     :  2021/1/26/0026 20:08
@Version        :  1.0
@Description    :
------------------------------------
@Software       :  VSCode
"""
# here put the import lib
import sys
from pycode.login_pane import login_pane
from PyQt5.QtWidgets import QApplication

################################################
#######程序入门
################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = login_pane(mode=0)
    login_window.show()
    sys.exit(app.exec_())
