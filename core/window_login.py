# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  s0nder
@Email          :  wylsyr@gmail.com
------------------------------------
@File           :  login_pane.py
@CreateTime     :  2021/1/26/0026 20:28
@Version        :  1.0
@Description    :
------------------------------------
@Software       :  VSCode
"""

# here put the import lib
import os, sys, time, re, requests, json
requests.packages.urllib3.disable_warnings()

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QDesktopWidget
from core.ui_login import Ui_LoginForm
from core.window_config import *
from core.window_mian import main_window
from core.rsas_req import *


RSAS_Requests = RSAS_Requests()
dt = time.strftime('%Y-%m-%d %H:%M:%S')



"""
################################################
#######登录界面
################################################
"""

class login_window(QWidget, Ui_LoginForm):
    def __init__(self, mode=0, parent=None):
        super(login_window, self).__init__(parent)
        self.mode = mode
        self.setupUi(self)

        self.setWindowTitle("登陆")
        self.setWindowIcon(QtGui.QIcon('./resource/favicon.ico'))

        ######  登录页面头图设置 完美显示图片，并自适应大小
        pix = QtGui.QPixmap("./resource/bg7699.png")
        self.login_top_bg_label.setPixmap(pix)
        self.login_top_bg_label.setScaledContents(True)

        ###### 显示窗口在屏幕中间
        self.center()

        ###### 初始化登录信息
        self.init_login_info()

        ###### 自动登录
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.goto_autologin)
        self.timer.setSingleShot(True)
        self.timer.start(1000)

        # with open('log.txt', 'a') as f3:
        #     f3.write('\n' + f'-------------------------------------------  {dt} -------------------------------------------' + '\n' + '\n')

        ###### 检查配置文件
        try:
            with open('config.ini') as content:
                pass
            self.read_config()
        except Exception as e:
            output_log("[!] 配置文件未找到，初次使用请配置扫描器信息...")
            settings = QSettings("config.ini", QSettings.IniFormat)
            settings.setValue("host", "")
            settings.setValue("port", "")
            settings.setValue("account", "")
            settings.setValue("password", "")
            settings.setValue("remeberpassword", "")
            settings.setValue("autologin", "")
            self.open_config_pane()

        ###### 创建资产文件夹
        try:
            os.mkdir('Assets_Host')
            os.mkdir('Assets_URL')
            os.mkdir('log')
        except Exception as e:
            pass

    ###### 显示窗口在屏幕中间
    def center(self):
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    ###### 从配置文件取出扫描器的配置信息
    def read_config(self):
        settings = QSettings("config.ini", QSettings.IniFormat)
        self.host = settings.value("host")
        self.port = settings.value("port")
        global SCANNER_URL
        if self.port == '443':
            SCANNER_URL = f'https://{self.host}'
        else:
            SCANNER_URL = f'https://{self.host}:{self.port}'

    ###### 跳转配置信息页面
    def open_config_pane(self):
        dialog = configdialog()
        if dialog.exec_() == QDialog.Accepted:
            output_log("[+] 扫描器配置信息保存成功。")
            self.read_config()

    ###### 自动登录 and 记住密码 联动
    def auto_login(self, checked):
        if checked:
            self.remember_passwd_checkBox.setChecked(True)

    ###### 记住密码 and 自动登录 联动
    def remember_pwd(self, checked):
        if not checked:
            self.Auto_login_checkBox.setChecked(False)

    ###### 账户 and 密码 and 登录按钮  有效性联动
    def enable_login_btn(self):
        account = self.username_lineEdit.text()
        passwd = self.passwd_lineEdit.text()
        if len(account) > 0 and len(passwd) > 0:
            self.login_pushButton.setEnabled(True)
        else:
            self.login_pushButton.setEnabled(False)

    ###### 登录按钮事件
    def ckeck_login(self):
        self.on_pushButton_enter_clicked()

    ###### 网页登录按钮事件
    def open_url_link(self):
        QDesktopServices.openUrl(QUrl(SCANNER_URL))

    ###### 自动登录
    def goto_autologin(self):
        if self.Auto_login_checkBox.isChecked() == True and self.mode == 0:
            self.on_pushButton_enter_clicked()

    ###### 保存登录信息
    def save_login_info(self):
        settings = QSettings("config.ini", QSettings.IniFormat)
        settings.setValue("host", self.host)
        settings.setValue("port", self.port)

        settings.setValue("account", self.username_lineEdit.text())
        settings.setValue("password", self.passwd_lineEdit.text())

        settings.setValue("remeberpassword", self.remember_passwd_checkBox.isChecked())
        settings.setValue("autologin", self.Auto_login_checkBox.isChecked())

    ###### 初始化登录信息
    def init_login_info(self):
        settings = QSettings("config.ini", QSettings.IniFormat)
        the_account = settings.value("account")
        the_password = settings.value("password")

        the_remeberpassword = settings.value("remeberpassword")
        the_autologin = settings.value("autologin")

        self.username_lineEdit.setText(the_account)
        if the_remeberpassword == "true" or the_remeberpassword == True:
            self.remember_passwd_checkBox.setChecked(True)
            self.passwd_lineEdit.setText(the_password)

        if the_autologin == "true" or the_autologin == True:
            self.Auto_login_checkBox.setChecked(True)

    windowList = []

    ###### 登录事件执行
    def on_pushButton_enter_clicked(self):
        self.username = self.username_lineEdit.text()
        self.passwd = self.passwd_lineEdit.text()
        output_log(f'[+] 配置信息读取成功，用户名：{self.username} 扫描器地址：{self.host} 扫描器端口：{self.port}')
        try:
            ###### 登陆扫描器
            cooker = RSAS_Requests.RSAS_Login(SCANNER_URL, self.username, self.passwd)
            ######  获取重定向的url地址
            if cooker.headers['location'] == '/':
                ######  到这里就是登陆成功了，开始保存登录信息
                self.save_login_info()
                output_log('[+] 扫描器登录成功！')
                try:
                    ######  关闭登录界面，打开主界面
                    # output_log('[+] 正在初始化主页面...')
                    task_window = main_window(SCANNER_URL, self.username, self.passwd)
                    self.windowList.append(task_window)
                    self.close()
                    task_window.show()
                except Exception as e:
                    output_log('[!] 主页面初始化失败！')
                    QtWidgets.QMessageBox.information(None, "初始化失败！", f"{e}",
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                      QtWidgets.QMessageBox.Yes)
        except Exception as e:
            output_log('[!] 扫描器登录失败！',Exception)
            QtWidgets.QMessageBox.about(None, '登录失败！', '密码错误！')

