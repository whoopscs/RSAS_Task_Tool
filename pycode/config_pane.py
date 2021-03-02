# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  sqandan
@Email          :  aadmin@111.com
------------------------------------
@File           :  config_pane.py
@CreateTime     :  2021/1/26/0026 20:45
@Version        :  1.0
@Description    :  
------------------------------------
@Software       :  VSCode
"""
# here put the import lib
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QDialog, QFrame, QVBoxLayout, QLineEdit, QPushButton


################################################
#######配置页面对话框
################################################
class configdialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('配置界面')
        self.resize(300, 200)
        self.setFixedSize(self.width(), self.height())
        ###### 设置只显示关闭按钮
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        ###### 设置界面控件
        self.frame = QFrame(self)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.alignment()
        self.lineEdit_host = QLineEdit()
        self.lineEdit_host.setPlaceholderText("请输入ip地址")
        self.verticalLayout.addWidget(self.lineEdit_host)

        self.lineEdit_port = QLineEdit()
        self.lineEdit_port.setPlaceholderText("默认端口443")
        self.verticalLayout.addWidget(self.lineEdit_port)

        self.pushButton_enter = QPushButton()
        self.pushButton_enter.setText("确定")
        self.verticalLayout.addWidget(self.pushButton_enter)

        self.pushButton_quit = QPushButton()
        self.pushButton_quit.setText("取消")
        self.verticalLayout.addWidget(self.pushButton_quit)

        ###### 绑定按钮事件
        self.pushButton_enter.clicked.connect(self.pushButton_enter_clicked)
        self.pushButton_quit.clicked.connect(self.pushButton_quit_clicked)

        ###### 初始化配置信息
        self.init_config_info()

    ###### 初始化配置信息
    def init_config_info(self):
        settings = QSettings("config.ini", QSettings.IniFormat)
        the_host = settings.value("host")
        the_port = settings.value("port")
        self.set_host_port(the_host, the_port)

    ###### 确定按钮
    def pushButton_enter_clicked(self):
        global host
        global port
        if self.lineEdit_host.text() == "":
            self.pushButton_quit_clicked
        elif self.lineEdit_port.text() == "":
            host = self.lineEdit_host.text()
            port = "443"
            self.save_host_port(host, port)
            self.accept()
        else:
            host = self.lineEdit_host.text()
            port = self.lineEdit_port.text()
            self.save_host_port(host,port)
            self.accept()


    ###### 取消按钮
    def pushButton_quit_clicked(self):
        self.accept()

    ###### 初始化配置页面信息
    def set_host_port(self, host, port):
        self.lineEdit_host.setText(host)
        if port == None:
            self.lineEdit_port.setText("443")
        else:
            self.lineEdit_port.setText(port)

    ###### 保存配置页面信息
    def save_host_port(self, host, port):
        settings = QSettings("config.ini", QSettings.IniFormat)
        settings.setValue("host", host)
        settings.setValue("port", port)
