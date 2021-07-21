# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  s0nder
@Email          :  wylsyr@gmail.com
------------------------------------
@File           :  window_main.py
@CreateTime     :  2021/1/26/0026 21:23
@Version        :  1.0
@Description    :  
------------------------------------
@Software       :  VSCode
"""

# here put the import lib
import os, sys, time, re, requests, json
requests.packages.urllib3.disable_warnings()

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QHeaderView, QGridLayout, QFileDialog
from core.ui_main import Ui_main
from core.ui_newtask import *
from core.ui_tasklist import *
from core.ui_log import *
from core.rsas_req import *


RSAS_Requests = RSAS_Requests()


class main_window(QWidget, Ui_main):
    def __init__(self, scanner_url, username, passwd, parent=None):
        super(main_window, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle("RSAS Task Tool v2.0 - ©s0nder")
        self.setWindowIcon(QtGui.QIcon('./resource/favicon.ico'))

        self.setWindowOpacity(0.95)  # 设置窗口透明度
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        # self.setWindowFlag(Qt.FramelessWindowHint)  # 隐藏边框

        #self.showMaximized()  # 窗口最大化显示
        self.center()  # 显示窗口在屏幕中间

        self.logout_pushButton.clicked.connect(self.logout_clicked)

        self.cwd = os.getcwd()  # 获取当前程序文件位置

        self.scanner_url = scanner_url
        self.username = username
        self.password = passwd

        # 任务界面提示用户名&&扫描器地址
        self.Host_label.setText(re.search(r'https://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', self.scanner_url).group(1))
        self.account_label.setText(self.username)

        # 扫描器的任务状态
        self.Status = RSAS_Status()
        self.Status.log_return.connect(self.status_finish)
        self.Status.start()

        self.center_widget_layout = QGridLayout()  # 创建网格布局对象
        self.center_widget.setLayout(self.center_widget_layout)  # 设置布局对象

        # 新建任务窗口
        self.newtask_widget = QWidget()
        self.newtask_ui = Ui_newtask_Form()
        self.newtask_ui.setupUi(self.newtask_widget)
        self.center_widget_layout.addWidget(self.newtask_widget)

        # 任务列表窗口
        self.tasklist_widget = QWidget()
        self.tasklist_ui = Ui_tasklist_Form()
        self.tasklist_ui.setupUi(self.tasklist_widget)
        self.center_widget_layout.addWidget(self.tasklist_widget)

        # 程序日志窗口
        self.log_widget = QWidget()
        self.log_ui = Ui_log_Form()
        self.log_ui.setupUi(self.log_widget)
        self.center_widget_layout.addWidget(self.log_widget)

        # 设置界面窗口
        # self.log_widget = QWidget()
        # self.log_ui = Ui_log_Form()
        # self.log_ui.setupUi(self.log_widget)
        # self.center_widget_layout.addWidget(self.log_widget)

        self.current_page = self.newtask_widget
        self.tasklist_widget.hide()
        self.log_widget.hide()

        # 切换界面绑定跳转函数
        self.pushButton.clicked.connect(self.change_to_newtask)
        self.pushButton_2.clicked.connect(self.change_to_tasklist)
        self.pushButton_3.clicked.connect(self.change_to_log)
        # self.pushButton_4.clicked.connect(self.change_to_log)

        # 新建任务界面功能加载
        self.host_scan_tab()

        class_text = RSAS_Requests.check_scan_tab()
        if class_text[0] == 'quick_task_btn':
            self.web_scan_tab()

        # 任务列表界面功能加载
        self.set_task_view()

    """
    ################################################
    #######主界面的基本展示
    ################################################
    """

    # 显示窗口在屏幕中间
    def center(self):
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 网页登录
    def url_login_clicked(self):
        RSAS_Requests.Webpage_login(self.scanner_url, self.username, self.password)

    # 注销
    windowList = []

    def logout_clicked(self):
        from core.window_login import login_window
        login_window = login_window(mode=1)
        self.windowList.append(login_window)
        self.close()
        login_window.show()

    def change_to_newtask(self):
        self.current_page.hide()
        # self.tasklist_widget.hide()  # 隐藏任务列表界面
        self.newtask_widget.show()  # 显示新建任务界面
        self.current_page = self.newtask_widget

    def change_to_tasklist(self):
        self.current_page.hide()
        # self.newtask_widget.hide()
        self.tasklist_widget.show()
        self.current_page = self.tasklist_widget

    def change_to_log(self):
        self.current_page.hide()
        self.log_widget.show()
        self.current_page = self.log_widget


    # 扫描器的任务状态
    def status_finish(self, status_msg):
        number = status_msg.split('|')
        self.Status_Ongoing_label.setText(f"{number[0]}")
        self.Status_Waiting_label.setText(f"{number[1]}")
        self.cpu_label.setText(f"{number[3]}")
        self.mem_label.setText(f"{number[4]}")
        self.disk_label.setText(f"{number[5]}")
        # self.Host_label_5.setText(f"{number[2]}")

    """
    ################################################
    #######新建任务界面的功能
    ################################################
    """

    # 主机扫描标签窗口
    def host_scan_tab(self):
        # 扫描器的漏洞模板
        self.host_template = {'0': '自动匹配扫描'}
        # 获取扫描器的漏洞模板，保存为软件的下拉框
        content_re = """<tr class=".*?">.*?<th>漏洞模板</th>.*?<td>.*?<select id='.*?'.*?style=".*?">(.*?)</select>.*?</td>.*?</tr>"""
        template_re = """<option value='(\d+)' >(.*?)</option>"""
        content = RSAS_Requests.Host_scanning_template()
        cont = re.findall(content_re, content.text, re.S | re.M)
        # 获取扫描器的漏洞模板，生成下拉框
        self.host_template.update(dict(re.findall(template_re, cont[0], re.S | re.M)))
        self.newtask_ui.TemplateList_Host_comboBox.addItems(self.host_template.values())
        self.newtask_ui.TemplateList_Host_comboBox.setCurrentIndex(0)

        self.L_wordbook = [self.newtask_ui.SMB_wordbook_checkBox, self.newtask_ui.RDP_wordbook_checkBox,
                           self.newtask_ui.TELENT_wordbook_checkBox,
                           self.newtask_ui.FTP_wordbook_checkBox, self.newtask_ui.SSH_wordbook_checkBox,
                           self.newtask_ui.POP3_wordbook_checkBox, self.newtask_ui.Tomcat_wordbook_checkBox,
                           self.newtask_ui.SQL_SERVER_wordbook_checkBox, self.newtask_ui.MySQL_wordbook_checkBox,
                           self.newtask_ui.Oracle_wordbook_checkBox, self.newtask_ui.Sybase_wordbook_checkBox,
                           self.newtask_ui.DB2_wordbook_checkBox,
                           self.newtask_ui.MONGODB_wordbook_checkBox, self.newtask_ui.SMTP_wordbook_checkBox,
                           self.newtask_ui.IMAP_wordbook_checkBox, self.newtask_ui.RTSP_wordbook_checkBox,
                           self.newtask_ui.Redis_wordbook_checkBox, self.newtask_ui.SNMP_wordbook_checkBox]

        self.newtask_ui.All_wordbook_checkBox.stateChanged.connect(self.change_all_wordbook_select)
        self.newtask_ui.SMB_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.RDP_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.TELENT_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.FTP_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.SSH_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.POP3_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.Tomcat_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.SQL_SERVER_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.MySQL_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.Oracle_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.Sybase_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.DB2_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.MONGODB_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.SMTP_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.IMAP_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.RTSP_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.Redis_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)
        self.newtask_ui.SNMP_wordbook_checkBox.stateChanged.connect(self.change_wordbook_select)

        # self.newtask_ui.HTML_Report_Host_checkBox.stateChanged.connect(self.change_report_type_select)
        # self.newtask_ui.World_Report_Host_checkBox.stateChanged.connect(self.change_report_type_select)
        # self.newtask_ui.Excel_Report_Host_checkBox.stateChanged.connect(self.change_report_type_select)
        # self.newtask_ui.PDF_Report_Host_checkBox.stateChanged.connect(self.change_report_type_select)
        #
        # self.newtask_ui.Summary_Report_Host_checkBox.stateChanged.connect(self.change_report_content_select)
        # self.newtask_ui.Host_Report_Host_checkBox.stateChanged.connect(self.change_report_content_select)

        self.newtask_ui.Load_Task_Name_Host_pushButton.clicked.connect(self.Load_Task_Name_Host)
        self.newtask_ui.Start_Host_Button.clicked.connect(self.Start_Host_Scan)

    # 口令字典全选联动
    def change_all_wordbook_select(self):
        if self.newtask_ui.All_wordbook_checkBox.checkState() == Qt.Checked:
            for i in self.L_wordbook:
                i.setChecked(True)
        elif self.newtask_ui.All_wordbook_checkBox.checkState() == Qt.Unchecked:
            for i in self.L_wordbook:
                i.setChecked(False)

    def change_wordbook_select(self):
        if self.newtask_ui.SMB_wordbook_checkBox.isChecked() and self.newtask_ui.RDP_wordbook_checkBox.isChecked() and self.newtask_ui.TELENT_wordbook_checkBox.isChecked() and self.newtask_ui.FTP_wordbook_checkBox.isChecked() and self.newtask_ui.SSH_wordbook_checkBox.isChecked() and self.newtask_ui.POP3_wordbook_checkBox.isChecked() and self.newtask_ui.Tomcat_wordbook_checkBox.isChecked() and self.newtask_ui.SQL_SERVER_wordbook_checkBox.isChecked() and self.newtask_ui.MySQL_wordbook_checkBox.isChecked() and self.newtask_ui.Oracle_wordbook_checkBox.isChecked() and self.newtask_ui.Sybase_wordbook_checkBox.isChecked() and self.newtask_ui.DB2_wordbook_checkBox.isChecked() and self.newtask_ui.MONGODB_wordbook_checkBox.isChecked() and self.newtask_ui.SMTP_wordbook_checkBox.isChecked() and self.newtask_ui.IMAP_wordbook_checkBox.isChecked() and self.newtask_ui.RTSP_wordbook_checkBox.isChecked() and self.newtask_ui.Redis_wordbook_checkBox.isChecked() and self.newtask_ui.SNMP_wordbook_checkBox.isChecked():
            self.newtask_ui.All_wordbook_checkBox.setCheckState(Qt.Checked)
        elif self.newtask_ui.SMB_wordbook_checkBox.isChecked() or self.newtask_ui.RDP_wordbook_checkBox.isChecked() or self.newtask_ui.TELENT_wordbook_checkBox.isChecked() or self.newtask_ui.FTP_wordbook_checkBox.isChecked() or self.newtask_ui.SSH_wordbook_checkBox.isChecked() or self.newtask_ui.POP3_wordbook_checkBox.isChecked() or self.newtask_ui.Tomcat_wordbook_checkBox.isChecked() or self.newtask_ui.SQL_SERVER_wordbook_checkBox.isChecked() or self.newtask_ui.MySQL_wordbook_checkBox.isChecked() or self.newtask_ui.Oracle_wordbook_checkBox.isChecked() or self.newtask_ui.Sybase_wordbook_checkBox.isChecked() or self.newtask_ui.DB2_wordbook_checkBox.isChecked() or self.newtask_ui.MONGODB_wordbook_checkBox.isChecked() or self.newtask_ui.SMTP_wordbook_checkBox.isChecked() or self.newtask_ui.IMAP_wordbook_checkBox.isChecked() or self.newtask_ui.RTSP_wordbook_checkBox.isChecked() or self.newtask_ui.Redis_wordbook_checkBox.isChecked() or self.newtask_ui.SNMP_wordbook_checkBox.isChecked():
            self.newtask_ui.All_wordbook_checkBox.setTristate()
            self.newtask_ui.All_wordbook_checkBox.setCheckState(Qt.PartiallyChecked)
        else:
            self.newtask_ui.All_wordbook_checkBox.setTristate(False)
            self.newtask_ui.All_wordbook_checkBox.setCheckState(Qt.Unchecked)

    # 报表类型选项联动
    def change_report_type_select(self):
        pass

    # 报表内容选项联动
    def change_report_content_select(self):
        pass

    # 加载Host资产文件下的资产文件到任务名称窗口
    def Load_Task_Name_Host(self):
        self.newtask_ui.Task_name_Host_textEdit.setText("")
        HostAssets_dir = './Assets_Host/'

        # 文件选择对话框
        # files, filetype = QFileDialog.getOpenFileNames(self,"选取文件",self.cwd,"All Files (*);;Text Files (*.txt)")
        #
        # if len(files) == 0:
        #     print("\n取消选择")
        #     return
        #
        # print("\n你选择的文件为:")
        # for file in files:
        #     print(file)
        # print("文件筛选器类型: ", filetype)
        #
        # #  web资产文件列表
        # HostAssets_list = []
        #
        # for file in os.listdir(HostAssets_dir):
        #     if os.path.splitext(file)[1] == '.txt':
        #         HostAssets_list.append(file)
        #         self.newtask_ui.Task_name_Host_textEdit.append(file[0:-4])

    # Host标签窗口开始任务按钮
    def Start_Host_Scan(self):
        # 获取当前下拉框的字符
        host_template_mode = self.newtask_ui.TemplateList_Host_comboBox.currentText()
        # 通过字符找到模板对应的数字，就是字典，通过值取键。扫描器的扫描模板对应不同的数字，扫描器在下任务时依照该数字选择对应的模板
        host_template_number = list(self.host_template.keys())[
            list(self.host_template.values()).index(host_template_mode)]

        # 这里就获取扫描任务的所有参数了
        # 端口扫描策略
        DefaultPort_status = self.newtask_ui.DefaultPort_radioButton.isChecked()
        FastPort_status = self.newtask_ui.FastPort_radioButton.isChecked()
        AllPost_status = self.newtask_ui.AllPort_radioButton.isChecked()
        UserPort_status = self.newtask_ui.User_SetPort_radioButton.isChecked()
        User_SetPort_Host_status = self.newtask_ui.User_SetPort_Host_lineEdit.text()
        # 主机存活测试
        Enable_Ping_status = self.newtask_ui.Enable_Ping_checkBox.isChecked()
        TcpPing_status = self.newtask_ui.TcpPing_checkBox.isChecked()
        TcpPing_SetPort_Host = self.newtask_ui.TcpPing_SetPort_Host_lineEdit.text()
        # 口令猜测
        Enable_wordbook_status = self.newtask_ui.Enable_wordbook_checkBox.isChecked()
        SMB_wordbook_status = self.newtask_ui.SMB_wordbook_checkBox.isChecked()
        RDP_wordbook_status = self.newtask_ui.RDP_wordbook_checkBox.isChecked()
        TELENT_wordbook_status = self.newtask_ui.TELENT_wordbook_checkBox.isChecked()
        FTP_wordbook_status = self.newtask_ui.FTP_wordbook_checkBox.isChecked()
        SSH_wordbook_status = self.newtask_ui.SSH_wordbook_checkBox.isChecked()
        POP3_wordbook_status = self.newtask_ui.POP3_wordbook_checkBox.isChecked()
        Tomcat_wordbook_status = self.newtask_ui.Tomcat_wordbook_checkBox.isChecked()
        SQL_SERVER_wordbook_status = self.newtask_ui.SQL_SERVER_wordbook_checkBox.isChecked()
        MySQL_wordbook_status = self.newtask_ui.MySQL_wordbook_checkBox.isChecked()
        Oracle_wordbook_status = self.newtask_ui.Oracle_wordbook_checkBox.isChecked()
        Sybase_wordbook_status = self.newtask_ui.Sybase_wordbook_checkBox.isChecked()
        DB2_wordbook_status = self.newtask_ui.DB2_wordbook_checkBox.isChecked()
        MONGODB_wordbook_status = self.newtask_ui.MONGODB_wordbook_checkBox.isChecked()
        SMTP_wordbook_status = self.newtask_ui.SMTP_wordbook_checkBox.isChecked()
        IMAP_wordbook_status = self.newtask_ui.IMAP_wordbook_checkBox.isChecked()
        RTSP_wordbook_status = self.newtask_ui.RTSP_wordbook_checkBox.isChecked()
        Redis_wordbook_status = self.newtask_ui.Redis_wordbook_checkBox.isChecked()
        SNMP_wordbook_status = self.newtask_ui.SNMP_wordbook_checkBox.isChecked()
        # 报表类型
        HTML_Report_Host_status = self.newtask_ui.HTML_Report_Host_checkBox.isChecked()
        World_Report_Host_status = self.newtask_ui.World_Report_Host_checkBox.isChecked()
        Excel_Report_Host_status = self.newtask_ui.Excel_Report_Host_checkBox.isChecked()
        PDF_Report_Host_status = self.newtask_ui.PDF_Report_Host_checkBox.isChecked()
        # 报表内容
        Summary_Report_Host_status = self.newtask_ui.Summary_Report_Host_checkBox.isChecked()
        Host_Report_Host_status = self.newtask_ui.Host_Report_Host_checkBox.isChecked()
        Auto_Report_Host_status = self.newtask_ui.Auto_Report_Host_checkBox.isChecked()
        FTP_Upload_Host_status = self.newtask_ui.FTP_Upload_Host_checkBox.isChecked()
        # 扫描时间段
        host_Scan_time_status = self.newtask_ui.Scan_Time_Host_lineEdit.text()

        # 这里可以对扫描任务名&&任务开始时间进行输入校验
        host_task_list = self.newtask_ui.Task_name_Host_textEdit.toPlainText().split("\n")
        host_task_list = [i for i in host_task_list if i != '']

        # 这里就是下任务了，使用线程，避免卡界面
        self.newtask_ui.Start_Host_Button.setChecked(True)
        self.newtask_ui.Start_Host_Button.setDisabled(True)
        self.Start_Host_Scan_Working = Start_Host_Scan_Working(host_template_number, DefaultPort_status,
                                                               FastPort_status, AllPost_status, UserPort_status,
                                                               User_SetPort_Host_status, Enable_Ping_status,
                                                               TcpPing_status, TcpPing_SetPort_Host,
                                                               Enable_wordbook_status, SMB_wordbook_status,
                                                               RDP_wordbook_status, TELENT_wordbook_status,
                                                               FTP_wordbook_status, SSH_wordbook_status,
                                                               POP3_wordbook_status, Tomcat_wordbook_status,
                                                               SQL_SERVER_wordbook_status, MySQL_wordbook_status,
                                                               Oracle_wordbook_status, Sybase_wordbook_status,
                                                               DB2_wordbook_status, MONGODB_wordbook_status,
                                                               SMTP_wordbook_status, IMAP_wordbook_status,
                                                               RTSP_wordbook_status, Redis_wordbook_status,
                                                               SNMP_wordbook_status, HTML_Report_Host_status,
                                                               World_Report_Host_status, Excel_Report_Host_status,
                                                               PDF_Report_Host_status, Summary_Report_Host_status,
                                                               Host_Report_Host_status, Auto_Report_Host_status,
                                                               FTP_Upload_Host_status, host_Scan_time_status,
                                                               host_task_list)
        self.Start_Host_Scan_Working.start_host_return.connect(self.Start_Host_Scan_Finish)
        self.Start_Host_Scan_Working.start()

    # 显示Host扫描任务下达状态
    def Start_Host_Scan_Finish(self, start_msg):
        self.newtask_ui.Working_Host_label.setText(start_msg)
        if '所有任务下达完成' in start_msg:
            self.newtask_ui.Start_Host_Button.setChecked(False)
            self.newtask_ui.Start_Host_Button.setDisabled(False)

    ####### web扫描标签窗口
    def web_scan_tab(self):
        # 扫描器的漏洞模板
        self.web_template = {'0': '自动匹配扫描'}
        # 获取扫描器的漏洞模板，保存为软件的下拉框
        content_re = """<tr class=".*?">.*?<th>漏洞模板</th>.*?<td>.*?<select id='.*?'.*?style=".*?">(.*?)</select>.*?</td>.*?</tr>"""
        template_re = """<option value="(\d+)" >(.*?)</option>"""
        content = RSAS_Requests.Web_scanning_template()
        cont = re.findall(content_re, content.text, re.S | re.M)
        # 把扫描器的漏洞模板生成下拉框
        self.web_template.update(dict(re.findall(template_re, cont[0], re.S | re.M)))
        self.newtask_ui.TemplateList_Web_comboBox.addItems(self.web_template.values())
        self.newtask_ui.TemplateList_Web_comboBox.setCurrentIndex(0)

        # 设置扫描范围下拉框的选项
        range_items = ["按域名扫描", "扫描当前目录及子目录", "只扫描任务目标链接"]
        self.newtask_ui.Scan_Range_comboBox.addItems(range_items)
        self.newtask_ui.Scan_Range_comboBox.setCurrentIndex(1)  # 设置默认值

        # 设置并发线程数默认值
        self.newtask_ui.Concurrent_Threads_lineEdit.setText("20")

        # 设置超时限制默认值
        self.newtask_ui.Webscan_Timeout_lineEdit.setText("30")

        # 设置目录猜测范围下拉框的选项
        level_items = ["0", "1", "2", "3"]
        self.newtask_ui.Dir_level_comboBox.addItems(level_items)
        self.newtask_ui.Dir_level_comboBox.setCurrentIndex(1)  # 设置默认值

        # 设置目录猜测深度默认值
        self.newtask_ui.Dir_limit_lineEdit.setText("3")

        self.newtask_ui.Start_Web_Button.clicked.connect(self.Start_Web_Scan)

    # 加载URL资产文件下的资产文件到任务名称窗口
    def Load_Task_Name_Web(self):
        self.newtask_ui.Task_name_Web_textEdit.setText("")
        self.WebAssets_dir = './Assets_URL/'

        #  web资产文件列表
        self.WebAssets_list = []

        for file in os.listdir(self.WebAssets_dir):
            if os.path.splitext(file)[1] == '.txt':
                self.WebAssets_list.append(file)
                self.newtask_ui.Task_name_Web_textEdit.append(file[0:-4])

    # 因web扫描单个任务限制15个URL，需要对任务进行拆分
    def Check_WebAssets_list(self, WebAssets_list):

        New_WebAssets_list = []

        for _task in WebAssets_list:
            task_info = _task.split('|')
            try:
                task_name = task_info[0].strip()
                task_time = task_info[1].strip()
            except Exception as e:
                task_name = _task.strip()
                task_time = ""
            with open('./Assets_URL/' + task_name + '.txt') as url_file:
                url_range = url_file.read()
            url_list = url_range.split('\n')

            while True:
                try:
                    url_list.remove('')
                except ValueError:
                    break

            print('[+] 正在进行url去重...')
            url_list_len = len(url_list)
            new_url_list = list(set(url_list))

            if len(new_url_list) < url_list_len:
                url_list = new_url_list
                print(f'[*] {task_name}检测到重复url，已经进行去重...')

            if len(url_list) > 15:
                print(f'[*] url大于15个，正在拆分任务{task_name}...')

                flag = 0

                name = 1

                dataList = []

                for line in url_list:
                    flag += 1
                    dataList.append(line)
                    if flag == 15:
                        with open('./Assets_URL/' + task_name + "--" + str(name) + ".txt",
                                  'w+') as f_target:  # str[0:-1]为切片，意思是从前面开始截取到后面-1为止
                            for data in dataList:
                                f_target.write(data + "\n")

                        dataList = []
                        if task_time == "":
                            New_WebAssets_list.append(task_name + "--" + str(name))
                        else:
                            New_WebAssets_list.append(task_name + "--" + str(name) + "|" + task_time)
                        name += 1
                        flag = 0

                # 处理最后一批行数少于15行的
                with open('./Assets_URL/' + task_name + "--" + str(name) + ".txt", 'w+') as f_target:
                    for data in dataList:
                        f_target.write(data + "\n")
                print(f'[*] 拆分任务已完成，共拆分{str(name)}子任务')
                if task_time == "":
                    New_WebAssets_list.append(task_name + "--" + str(name))
                else:
                    New_WebAssets_list.append(task_name + "--" + str(name) + "|" + task_time)
                os.remove('./Assets_URL/' + task_name + '.txt')
            else:
                New_WebAssets_list.append(_task)
        return New_WebAssets_list

    # 因web扫描会检测URL访问性，需要对资产进行校验
    def Check_URL(self):

        pass

    # Web标签窗口开始任务按钮
    def Start_Web_Scan(self):

        # 这里就获取主界面的任务参数
        # 获取扫描范围下标
        web_range_number = self.newtask_ui.Scan_Range_comboBox.currentIndex()

        # 获取扫描模板当前下拉框的字符
        web_template_mode = self.newtask_ui.TemplateList_Web_comboBox.currentText()
        # 通过字符找到模板对应的数字，就是字典，通过值取键。扫描器的扫描模板对应不同的数字，扫描器在下任务时依照该数字选择对应的模板
        web_template_number = list(self.web_template.keys())[list(self.web_template.values()).index(web_template_mode)]

        # 并发线程数
        Concurrent_Threads_status = self.newtask_ui.Concurrent_Threads_lineEdit.text()
        # 超时限制
        Webscan_Timeout_status = self.newtask_ui.Webscan_Timeout_lineEdit.text()
        # 目录猜测范围
        Dir_level_status = self.newtask_ui.Dir_level_comboBox.currentIndex()
        # 目录猜测深度
        Dir_limit_status = self.newtask_ui.Dir_limit_lineEdit.text()
        # 报表类型
        HTML_Report_Web_status = self.newtask_ui.HTML_Report_Web_checkBox.isChecked()
        World_Report_Web_status = self.newtask_ui.World_Report_Web_checkBox.isChecked()
        Excel_Report_Web_status = self.newtask_ui.Excel_Report_Web_checkBox.isChecked()
        PDF_Report_Web_status = self.newtask_ui.PDF_Report_Web_checkBox.isChecked()
        # 报表内容
        Summary_Report_Web_status = self.newtask_ui.Summary_Report_Web_checkBox.isChecked()
        Host_Report_Web_status = self.newtask_ui.Host_Report_Web_checkBox.isChecked()
        Auto_Report_Web_status = self.newtask_ui.Auto_Report_Web_checkBox.isChecked()

        Scan_time_web_status = self.newtask_ui.Scan_Time_Web_lineEdit.text()

        # todo 这里可以对扫描任务名&&任务开始时间进行输入校验
        task_list_web = self.newtask_ui.Task_name_Web_textEdit.toPlainText().split("\n")
        task_list_web = [i for i in task_list_web if i != '']
        New_WebAssets_list = self.Check_WebAssets_list(task_list_web)

        # 这里就是下任务了，使用线程，避免卡界面
        self.newtask_ui.Start_Web_Button.setChecked(True)
        self.newtask_ui.Start_Web_Button.setDisabled(True)
        self.Start_Web_Scan_Working = Start_Web_Scan_Working(web_range_number, web_template_number,
                                                             Concurrent_Threads_status, Webscan_Timeout_status,
                                                             Dir_level_status, Dir_limit_status,
                                                             HTML_Report_Web_status, World_Report_Web_status,
                                                             Excel_Report_Web_status,
                                                             PDF_Report_Web_status, Summary_Report_Web_status,
                                                             Host_Report_Web_status, Auto_Report_Web_status,
                                                             Scan_time_web_status, New_WebAssets_list)
        self.Start_Web_Scan_Working.start_web_return.connect(self.Start_Web_Scan_Finish)
        self.Start_Web_Scan_Working.start()

    # 显示Web扫描任务下达状态
    def Start_Web_Scan_Finish(self, start_msg):
        self.newtask_ui.Working_Web_label.setText(start_msg)
        if '所有任务下达完成' in start_msg:
            self.newtask_ui.Start_Web_Button.setChecked(False)
            self.newtask_ui.Start_Web_Button.setDisabled(False)



    """
    ################################################
    #######任务列表界面的基本展示
    ################################################
    """

    """
    PyQt5的Model/View/Delegate的设计模式，即Model持有数据，下与数据源交互（数据的查询、修改与添加），上与View交互，
    主要为View提供要显示的数据。View提供数据的显示和与用户交互。Delegate可以实现定制数据显示的方式和编辑方式
    """

    def set_task_view(self):
        task_list_tableView = self.tasklist_ui.task_list_tableView

        task_list_tableView.setSelectionBehavior(QHeaderView.SelectRows)  # 选择行为：行选择
        task_list_tableView.setAlternatingRowColors(True)  # 隔行变色

        task_list_tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 所有列自动拉伸，充满界面
        # 设置数据层次结构，4行4列
        self.model = QStandardItemModel(2, 6)
        # 视图加载模型
        self.model = MyModel()
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(['任务号', '任务名称', '开始时间', '结束时间', '进度', '操作'])
        task_list_tableView.setModel(self.model)

        task_num = "2333"
        task_name = "测试任务名称"
        task_start_time = "2021-02-02 22:22:22"
        task_end_time = "2021-02-02 23:33:33"
        task_progress = "100%"

        for row in range(4):
            self.model.setItem(row, 0, QStandardItem(f"{task_num}"))
            self.model.setItem(row, 1, QStandardItem(f"{task_name}"))
            self.model.setItem(row, 2, QStandardItem(f"{task_start_time}"))
            self.model.setItem(row, 3, QStandardItem(f"{task_end_time}"))
            self.model.setItem(row, 4, QStandardItem(f"{task_progress}"))


###### 重写QStandardItemModel的data函数使item居中显示
class MyModel(QStandardItemModel):
    def __init__(self):
        QStandardItemModel.__init__(self)

    def data(self, index, role=None):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return QStandardItemModel.data(self, index, role)
