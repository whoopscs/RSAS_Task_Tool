# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  s0nder
@Email          :  wylsyr@gmail.com
------------------------------------
@File           :  rsas_req.py
@CreateTime     :  2021/1/30/0030 19:09
@Version        :  1.0
@Description    :
------------------------------------
@Software       :  VSCode
"""

# here put the import lib
import os, sys, time, re, requests, json
requests.packages.urllib3.disable_warnings()

from lxml import etree
from PyQt5.QtCore import QThread, pyqtSignal

# sys.path.append("..\\")
from resource.selenium import webdriver
from resource.msedge.selenium_tools import Edge, EdgeOptions



"""
################################################
####### 所有的与扫描器交互的请求都在这里执行
################################################
"""


s = requests.Session()

log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
detail_time = time.strftime("%Y-%m-%d %H:%M:%S")

def output_log(output):
    log_name = time.strftime("%Y-%m-%d")
    log_time = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(f'./log/{log_name}.txt', 'a+') as f:
        print(log_time + "  " + output)
        f.write(log_time + "  " + output + "\n")


class RSAS_Requests:

    def __init__(self):
        pass

    ######  登录请求
    def RSAS_Login(self, scanner_url, username, password):
        global SCANNER_URL
        SCANNER_URL = scanner_url if not scanner_url.endswith('/') else scanner_url[0:-1]
        self.SCANNER_ADDRESS = SCANNER_URL.split('://')[1]

        self.USERNAME = username
        self.PASSWORD = password

        # output_log('[+] 正在登陆扫描器...')
        # 生成用于登录页面的初始请求头
        s.headers = {
            'Host': f'{self.SCANNER_ADDRESS}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': f'{SCANNER_URL}',
            'Upgrade-Insecure-Requests': '1',
        }

        # output_log('[+] 正在获取csrfmiddlewaretoken...')
        # 访问登陆页面，获取用于登录的csrfmiddlewaretoken
        res = s.get(f'{SCANNER_URL}/accounts/login/?next=/', verify=False)
        csrfmiddlewaretoken = re.findall("""<input type='hidden' name='csrfmiddlewaretoken' value="(.*)">""", res.text)[
            0]
        if csrfmiddlewaretoken:
            # output_log('[+] 获取csfrmiddlewaretoken成功，正在重构请求头并发送payload...')
            pass
        else:
            output_log('[!] 获取csrfmiddlewaretoken失败！')
            exit(0)

        data = {
            'username': self.USERNAME,
            'password': self.PASSWORD,
            'csrfmiddlewaretoken': csrfmiddlewaretoken
        }
        # 提交登录请求
        cookie_html = s.post(f'{SCANNER_URL}/accounts/login_view/', data=data, verify=False, allow_redirects=False,
                             timeout=3)

        return cookie_html

    ###### 判断扫描器支持的扫描模块
    def check_scan_tab(self):
        s.headers['Referer'] = SCANNER_URL
        s.cookies['left_menustatue_NSFOCUSRSAS'] = f"0|0|{SCANNER_URL}/task/task_entry/"
        content = s.get(f'{SCANNER_URL}/task/task_entry/', verify=False)
        html = etree.HTML(content.text)
        class_text = html.xpath('//ul[@id="web_scan"]//input[@type="button"]/@class')

        return class_text

    ###### 获取主机扫描任务的扫描模板
    def Host_scanning_template(self):
        # 更新请求头用于新建信息
        s.headers['Referer'] = f'{SCANNER_URL}/task/task_entry/'
        s.cookies['left_menustatue_NSFOCUSRSAS'] = f"0|0|{SCANNER_URL}/task/task_entry/"
        content = s.get(f'{SCANNER_URL}/task/index/1', verify=False, allow_redirects=False)

        return content

    ###### 获取Web扫描任务的扫描模板
    def Web_scanning_template(self):
        # 更新请求头用于新建信息
        s.headers['Referer'] = f'{SCANNER_URL}/task/task_entry/'
        s.cookies['left_menustatue_NSFOCUSRSAS'] = f"0|0|{SCANNER_URL}/task/task_entry/"
        content = s.get(f'{SCANNER_URL}/task/index/8', verify=False, allow_redirects=False)

        return content

    def Webpage_login(self, scanner_url, username, password):
        """edge浏览器"""
        edgedriver = "./resource/msedgedriver.exe"  # 这里写本地的edgedriver的所在路径
        edge_options = EdgeOptions()
        edge_options.use_chromium = True  # 使用谷歌内核
        edge_options.add_argument("disable-gpu")  # 禁用gpu加速，避免bug
        edge_options.add_argument('start-maximized')  # 启动最大化
        edge_options.add_argument('--ignore-certificate-errors')  # 绕过“你的连接不是专用连接”
        edge_options.add_experimental_option('useAutomationExtension', False)  # 关闭“Microsoft Edge正由自动测试软件控制。”
        edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver = Edge(executable_path=edgedriver, options=edge_options)

        driver.get(scanner_url)

        time.sleep(1)
        driver.find_element_by_id('username').click()
        driver.find_element_by_id('username').send_keys(username)
        driver.find_element_by_id('password').click()
        driver.find_element_by_id('password').send_keys(password)
        driver.find_element_by_class_name('submit').click()
        time.sleep(1)
        driver.find_element_by_id('two01').click()



"""
################################################
#######主机扫描多线程下任务鸭
################################################
"""

class Start_Host_Scan_Working(QThread):
    start_host_return = pyqtSignal(str)

    def __init__(self, host_template_number, DefaultPort_status,
                                                               FastPort_status, AllPost_status, UserPort_status,
                                                               User_SetPort_Host_status, Enable_Ping_status,
                                                               TcpPing_status, TcpPing_SetPort_Host,
                                                               Enable_wordbook_status, SMB_wordbook_status,
                                                               RDP_wordbook_status, TELENT_wordbook_status,
                                                               FTP_wordbook_status, SSH_wordbook_status,
                                                               POP3_wordbook_status,Tomcat_wordbook_status,
                                                               SQL_SERVER_wordbook_status, MySQL_wordbook_status,
                                                               Oracle_wordbook_status, Sybase_wordbook_status,
                                                               DB2_wordbook_status, MONGODB_wordbook_status,
                                                               SMTP_wordbook_status, IMAP_wordbook_status,
                                                               RTSP_wordbook_status, Redis_wordbook_status,
                                                               SNMP_wordbook_status, HTML_Report_Host_status,
                                                               World_Report_Host_status, Excel_Report_Host_status,
                                                               PDF_Report_Host_status, Summary_Report_Host_status,
                                                               Host_Report_Host_status, Auto_Report_Host_status,
                                                               FTP_Upload_Host_status, host_Scan_time_status, host_task_list):
        super(Start_Host_Scan_Working, self).__init__()
        self.host_template_number = host_template_number
        self.DefaultPort_status = DefaultPort_status
        self.FastPort_status = FastPort_status
        self.AllPost_status = AllPost_status
        self.UserPort_status = UserPort_status
        self.User_SetPort_Host_status = User_SetPort_Host_status
        self.Enable_Ping_status = Enable_Ping_status
        self.TcpPing_status = TcpPing_status
        self.TcpPing_SetPort_Host = TcpPing_SetPort_Host
        self.Enable_wordbook_status = Enable_wordbook_status
        self.SMB_wordbook_status = SMB_wordbook_status
        self.RDP_wordbook_status = RDP_wordbook_status
        self.TELENT_wordbook_status = TELENT_wordbook_status
        self.FTP_wordbook_status = FTP_wordbook_status
        self.SSH_wordbook_status = SSH_wordbook_status
        self.POP3_wordbook_status = POP3_wordbook_status
        self.Tomcat_wordbook_status = Tomcat_wordbook_status
        self.SQL_SERVER_wordbook_status = SQL_SERVER_wordbook_status
        self.MySQL_wordbook_status = MySQL_wordbook_status
        self.Oracle_wordbook_status = Oracle_wordbook_status
        self.Sybase_wordbook_status = Sybase_wordbook_status
        self.DB2_wordbook_status = DB2_wordbook_status
        self.MONGODB_wordbook_status = MONGODB_wordbook_status
        self.SMTP_wordbook_status = SMTP_wordbook_status
        self.IMAP_wordbook_status = IMAP_wordbook_status
        self.RTSP_wordbook_status = RTSP_wordbook_status
        self.Redis_wordbook_status = Redis_wordbook_status
        self.SNMP_wordbook_status = SNMP_wordbook_status
        self.HTML_Report_Host_status = HTML_Report_Host_status
        self.World_Report_Host_status = World_Report_Host_status
        self.Excel_Report_Host_status = Excel_Report_Host_status
        self.PDF_Report_Host_status = PDF_Report_Host_status
        self.Summary_Report_Host_status = Summary_Report_Host_status
        self.Host_Report_Host_status = Host_Report_Host_status
        self.Auto_Report_Host_status = Auto_Report_Host_status
        self.FTP_Upload_Host_status = FTP_Upload_Host_status
        self.host_Scan_time_status = host_Scan_time_status
        self.task_list_host = host_task_list

    def run(self):

        # 更新请求头用于新建信息
        s.headers['Referer'] = f'{SCANNER_URL}/task/task_entry/'
        s.cookies['left_menustatue_NSFOCUSRSAS'] = f"0|0|{SCANNER_URL}/task/task_entry/"
        content = s.get(f'{SCANNER_URL}/task/index/1', verify=False, allow_redirects=False)

        ###### 获取主机扫描任务的csrfmiddlewaretoken
        global host_csrfmiddlewaretoken
        host_csrfmiddlewaretoken = re.findall("""csrfmiddlewaretoken":\'(.+)\'""", content.text)[0]
        # output_log("[+] 主机扫描的csrfmiddlewaretoken获取成功！")

        ###### 扫描器下的任务要很多的参数，下边都是POST请求要发送的准备数据

        # 端口扫描策略
        if self.DefaultPort_status == True:
            port_strategy = 'standard'
            port_strategy_userports = '1-100,443,445'
        if self.FastPort_status == True:
            port_strategy = 'fast'
        if self.AllPost_status == True:
            port_strategy = 'allports'
            port_strategy_userports = '1-65535'

        # todo 端口扫描策略自定义端口
        if self.UserPort_status == True:
            port_strategy = 'user'
            if self.User_SetPort_Host_status == None:
                port_strategy_userports = '1-100,443,445'
            else:
                port_strategy_userports = self.User_SetPort_Host_status

        # todo 主机存活测试自定义端口
        if self.TcpPing_status == True:
            live_tcp = 'on'
            if self.TcpPing_SetPort_Host == None:
                live_tcp_ports = '21,22,23,25,80,443,445,139,3389,6000'
            else:
                live_tcp_ports = self.TcpPing_SetPort_Host
        else:
            live_tcp = ''
            live_tcp_ports = ''

        if self.Auto_Report_Host_status == True:
            report_ifcreate = 'yes'
        else:
            report_ifcreate = ''

        if self.FTP_Upload_Host_status == True:
            send_ftp = 'yes'
        else:
            send_ftp = ''

        # 扫描时间段
        if self.host_Scan_time_status == '':
            self.host_Scan_time = ""
        else:
            self.host_Scan_time = self.host_Scan_time_status

        i = 1
        for _task in self.task_list_host:
            self.start_host_return.emit(f'共{len(self.task_list_host)}个任务，正在下达第{i}个任务...')
            task_info = _task.split('|')
            try:
                task_name = task_info[0].strip()
                task_time = task_info[1].strip()
                task_start_time = 'timing'
            except Exception as e:
                task_name = _task.strip()
                task_time = detail_time
                task_start_time = 'immediate'

            iplist = ''
            loginarray = []
            ips = set()
            try:
                with open('./Assets_Host/' + task_name + '.txt') as cent:
                    for ip in cent:
                        ips.add(ip.strip())
                    _iplist = [i for i in list(ips) if i != '']

                    for i in range(len(_iplist)):
                        loginarray.append(
                            {"ip_range": "{}".format(_iplist[i]), "admin_id": "", "protocol": "", "port": "", "os": "",
                             "user_name": "", "user_pwd": "", "ostpls": [], "apptpls": [], "dbtpls": [], "virttpls": [],
                             "devtpls": [], "statustpls": "", "tpl_industry": "", "tpllist": [], "tpllistlen": 0,
                             "jhosts": [],
                             "tpltype": "", "protect": "", "protect_level": "", "jump_ifuse": "", "host_ifsave": "",
                             "oracle_ifuse": "", "ora_username": "", "ora_userpwd": "", "ora_port": "",
                             "ora_usersid": "",
                             "weblogic_ifuse": "", "weblogic_system": "", "weblogic_version": "", "weblogic_user": "",
                             "weblogic_path": ""})
                        iplist += ';' + _iplist[i]
            except Exception as e:
                self.start_host_return.emit('警告！找不到相关资产，请检查！'.format(len(self.task_list_host), i))
                output_log(f'[!] 找不到任务资产：{task_name}，请检查！')
                with open('log.txt', 'a') as content:
                    content.write(f'找不到任务资产：{task_name}\n')
                time.sleep(1)
                break

            host_payload = {
                "csrfmiddlewaretoken": host_csrfmiddlewaretoken,
                "vul_or_pwd": "vul",
                "config_task": "taskname",
                "task_config": "",
                "diff": "write something",
                "target": "ip",
                "ipList": iplist[1:],
                "domainList": "",
                "name": task_name,
                "exec": task_start_time,
                "exec_timing_date": task_time,
                "exec_everyday_time": "00:00",
                "exec_everyweek_day": "1",
                "exec_everyweek_time": "00:00",
                "exec_emonthdate_day": "1",
                "exec_emonthdate_time": "00:00",
                "exec_emonthweek_pre": "1",
                "exec_emonthweek_day": "1",
                "exec_emonthweek_time": "00:00",
                "tpl": self.host_template_number,
                "login_check_type": "login_check_type_vul",
                "isguesspwd": "yes",
                "exec_range": self.host_Scan_time,
                "scan_pri": "2",
                "taskdesc": "",
                "report_type_html": "html",
                "report_type_doc": "doc",
                "report_type_xls": "xls",
                "report_type_pdf": "pdf",
                "report_content_sum": "sum",
                "report_content_host": "host",
                "report_tpl_sum": "10003",
                "report_tpl_host": "10004",
                "report_ifcreate": report_ifcreate,
                "send_ftp": send_ftp,
                "report_ifsent_type": "html",
                "report_ifsent_email": "",
                "port_strategy": port_strategy,
                "port_strategy_userports": port_strategy_userports,
                "port_speed": "3",
                "port_tcp": "T",
                "live": "on",
                "live_icmp": "on",
                "live_tcp": live_tcp,
                "live_tcp_ports": live_tcp_ports,
                "scan_level": "3",
                "timeout_plugins": "40",
                "timeout_read": "5",
                "alert_msg": "远程安全评估系统将对您的主机进行安全评估。",
                "scan_oracle": "yes",
                "encoding": "GBK",
                "bvs_task": "no",

                "pwd_smb": "yes",
                "pwd_type_smb": "c",
                "pwd_user_smb": "smb_user.default",
                "pwd_pass_smb": "smb_pass.default",

                "pwd_rdp": "yes",
                "pwd_type_rdp": "c",
                "pwd_user_rdp": "rdp_user.default",
                "pwd_pass_rdp": "rdp_pass.default",

                "pwd_telnet": "yes",
                "pwd_type_telnet": "c",
                "pwd_user_telnet": "telnet_user.default",
                "pwd_pass_telnet": "telnet_pass.default",
                "pwd_userpass_telnet": "telnet_userpass.default",

                "pwd_ftp": "yes",
                "pwd_type_ftp": "c",
                "pwd_user_ftp": "ftp_user.default",
                "pwd_pass_ftp": "ftp_pass.default",

                "pwd_ssh": "yes",
                "pwd_type_ssh": "c",
                "pwd_user_ssh": "ssh_user.default",
                "pwd_pass_ssh": "ssh_pass.default",
                "pwd_userpass_ssh": "ssh_userpass.default",

                "pwd_pop3": "yes",
                "pwd_type_pop3": "c",
                "pwd_user_pop3": "pop3_user.default",
                "pwd_pass_pop3": "pop3_pass.default",

                "pwd_tomcat": "yes",
                "pwd_type_tomcat": "c",
                "pwd_user_tomcat": "tomcat_user.default",
                "pwd_pass_tomcat": "tomcat_pass.default",

                "pwd_mssql": "yes",
                "pwd_type_mssql": "c",
                "pwd_user_mssql": "mssql_user.default",
                "pwd_pass_mssql": "mssql_pass.default",

                "pwd_mysql": "yes",
                "pwd_type_mysql": "c",
                "pwd_user_mysql": "mysql_user.default",
                "pwd_pass_mysql": "mysql_pass.default",

                "pwd_oracle": "yes",
                "pwd_type_oracle": "c",
                "pwd_user_oracle": "oracle_user.default",
                "pwd_pass_oracle": "oracle_pass.default",

                "pwd_sybase": "yes",
                "pwd_type_sybase": "c",
                "pwd_user_sybase": "sybase_user.default",
                "pwd_pass_sybase": "sybase_pass.default",

                "pwd_db2": "yes",
                "pwd_type_db2": "c",
                "pwd_user_db2": "db2_user.default",
                "pwd_pass_db2": "db2_pass.default",

                "pwd_mongodb": "yes",
                "pwd_type_mongodb": "c",
                "pwd_user_mongodb": "mongodb_user.default",
                "pwd_pass_mongodb": "mongodb_pass.default",

                "pwd_smtp": "yes",
                "pwd_type_smtp": "c",
                "pwd_user_smtp": "smtp_user.default",
                "pwd_pass_smtp": "smtp_pass.default",

                "pwd_imap": "yes",
                "pwd_type_imap": "c",
                "pwd_user_imap": "imap_user.default",
                "pwd_pass_imap": "imap_pass.default",

                "pwd_rtsp": "yes",
                "pwd_type_rtsp": "c",
                "pwd_user_rtsp": "rtsp_user.default",
                "pwd_pass_rtsp": "rtsp_pass.default",

                "pwd_redis": "yes",
                "pwd_pass_redis": "redis_pass.default",

                "pwd_snmp": "yes",
                "pwd_pass_snmp": "snmp_pass.default",

                "pwd_timeout": "5",
                "pwd_timeout_time": "120",
                "pwd_interval": "0",
                "pwd_num": "0",
                "pwd_threadnum": "5",
                "loginarray": loginarray
            }

            # 是否进行存活探测
            if self.Enable_Ping_status == False:
                host_payload.pop('live')
                host_payload.pop('live_icmp')
                host_payload.pop('live_tcp')
                host_payload.pop('live_tcp_ports')

            # 是否启用口令猜测，最少勾选一项，默认一直勾选SSH
            if self.Enable_wordbook_status == True:
                if self.SMB_wordbook_status == False:
                    host_payload.pop('pwd_smb')
                    host_payload.pop('pwd_type_smb')
                    host_payload.pop('pwd_user_smb')
                    host_payload.pop('pwd_pass_smb')
                    host_payload.pop('pwd_userpass_smb')

                if self.RDP_wordbook_status == False:
                    host_payload.pop('pwd_rdp')
                    host_payload.pop('pwd_type_rdp')
                    host_payload.pop('pwd_user_rdp')
                    host_payload.pop('pwd_pass_rdp')

                if self.TELENT_wordbook_status == False:
                    host_payload.pop('pwd_telnet')
                    host_payload.pop('pwd_type_telnet')
                    host_payload.pop('pwd_user_telnet')
                    host_payload.pop('pwd_pass_telnet')
                    host_payload.pop('pwd_userpass_telnet')

                if self.FTP_wordbook_status == False:
                    host_payload.pop('pwd_ftp')
                    host_payload.pop('pwd_type_ftp')
                    host_payload.pop('pwd_user_ftp')
                    host_payload.pop('pwd_pass_ftp')

                # if self.SSH_wordbook_status == False:
                #     host_payload.pop('pwd_ssh')
                #     host_payload.pop('pwd_type_ssh')
                #     host_payload.pop('pwd_user_ssh')
                #     host_payload.pop('pwd_pass_ssh')
                #     host_payload.pop('pwd_userpass_ssh')

                if self.Tomcat_wordbook_status == False:
                    host_payload.pop('pwd_tomcat')
                    host_payload.pop('pwd_type_tomcat')
                    host_payload.pop('pwd_user_tomcat')
                    host_payload.pop('pwd_pass_tomcat')

                if self.POP3_wordbook_status == False:
                    host_payload.pop('pwd_pop3')
                    host_payload.pop('pwd_type_pop3')
                    host_payload.pop('pwd_user_pop3')
                    host_payload.pop('pwd_pass_pop3')

                if self.SQL_SERVER_wordbook_status == False:
                    host_payload.pop('pwd_mssql')
                    host_payload.pop('pwd_type_mssql')
                    host_payload.pop('pwd_user_mssql')
                    host_payload.pop('pwd_pass_mssql')

                if self.MySQL_wordbook_status == False:
                    host_payload.pop('pwd_mysql')
                    host_payload.pop('pwd_type_mysql')
                    host_payload.pop('pwd_user_mysql')
                    host_payload.pop('pwd_pass_mysql')

                if self.Oracle_wordbook_status == False:
                    host_payload.pop('pwd_oracle')
                    host_payload.pop('pwd_type_oracle')
                    host_payload.pop('pwd_user_oracle')
                    host_payload.pop('pwd_pass_oracle')

                if self.Sybase_wordbook_status == False:
                    host_payload.pop('pwd_sybase')
                    host_payload.pop('pwd_type_sybase')
                    host_payload.pop('pwd_user_sybase')
                    host_payload.pop('pwd_pass_sybase')

                if self.DB2_wordbook_status == False:
                    host_payload.pop('pwd_db2')
                    host_payload.pop('pwd_type_db2')
                    host_payload.pop('pwd_user_db2')
                    host_payload.pop('pwd_pass_db2')

                if self.MONGODB_wordbook_status == False:
                    host_payload.pop('pwd_mongodb')
                    host_payload.pop('pwd_type_mongodb')
                    host_payload.pop('pwd_user_mongodb')
                    host_payload.pop('pwd_pass_mongodb')

                if self.SMTP_wordbook_status == False:
                    host_payload.pop('pwd_smtp')
                    host_payload.pop('pwd_type_smtp')
                    host_payload.pop('pwd_user_smtp')
                    host_payload.pop('pwd_pass_smtp')

                if self.IMAP_wordbook_status == False:
                    host_payload.pop('pwd_imap')
                    host_payload.pop('pwd_type_imap')
                    host_payload.pop('pwd_user_imap')
                    host_payload.pop('pwd_pass_imap')

                if self.RTSP_wordbook_status == False:
                    host_payload.pop('pwd_rtsp')
                    host_payload.pop('pwd_type_rtsp')
                    host_payload.pop('pwd_user_rtsp')
                    host_payload.pop('pwd_pass_rtsp')

                if self.Redis_wordbook_status == False:
                    host_payload.pop('pwd_redis')
                    host_payload.pop('pwd_pass_redis')

                if self.SNMP_wordbook_status == False:
                    host_payload.pop('pwd_snmp')
                    host_payload.pop('pwd_pass_snmp')
            else:
                host_payload.pop('isguesspwd')

                # host_payload.pop('pwd_smb')
                # host_payload.pop('pwd_type_smb')
                # host_payload.pop('pwd_user_smb')
                # host_payload.pop('pwd_pass_smb')
                # host_payload.pop('pwd_userpass_smb')

                host_payload.pop('pwd_rdp')
                host_payload.pop('pwd_type_rdp')
                host_payload.pop('pwd_user_rdp')
                host_payload.pop('pwd_pass_rdp')

                # host_payload.pop('pwd_telnet')
                # host_payload.pop('pwd_type_telnet')
                # host_payload.pop('pwd_user_telnet')
                # host_payload.pop('pwd_pass_telnet')
                # host_payload.pop('pwd_userpass_telnet')

                host_payload.pop('pwd_ftp')
                host_payload.pop('pwd_type_ftp')
                host_payload.pop('pwd_user_ftp')
                host_payload.pop('pwd_pass_ftp')

                # host_payload.pop('pwd_ssh')
                # host_payload.pop('pwd_type_ssh')
                # host_payload.pop('pwd_user_ssh')
                # host_payload.pop('pwd_pass_ssh')
                # host_payload.pop('pwd_userpass_ssh')

                host_payload.pop('pwd_tomcat')
                host_payload.pop('pwd_type_tomcat')
                host_payload.pop('pwd_user_tomcat')
                host_payload.pop('pwd_pass_tomcat')

                host_payload.pop('pwd_pop3')
                host_payload.pop('pwd_type_pop3')
                host_payload.pop('pwd_user_pop3')
                host_payload.pop('pwd_pass_pop3')

                host_payload.pop('pwd_mssql')
                host_payload.pop('pwd_type_mssql')
                host_payload.pop('pwd_user_mssql')
                host_payload.pop('pwd_pass_mssql')

                host_payload.pop('pwd_mysql')
                host_payload.pop('pwd_type_mysql')
                host_payload.pop('pwd_user_mysql')
                host_payload.pop('pwd_pass_mysql')

                host_payload.pop('pwd_oracle')
                host_payload.pop('pwd_type_oracle')
                host_payload.pop('pwd_user_oracle')
                host_payload.pop('pwd_pass_oracle')

                host_payload.pop('pwd_sybase')
                host_payload.pop('pwd_type_sybase')
                host_payload.pop('pwd_user_sybase')
                host_payload.pop('pwd_pass_sybase')

                host_payload.pop('pwd_db2')
                host_payload.pop('pwd_type_db2')
                host_payload.pop('pwd_user_db2')
                host_payload.pop('pwd_pass_db2')

                host_payload.pop('pwd_mongodb')
                host_payload.pop('pwd_type_mongodb')
                host_payload.pop('pwd_user_mongodb')
                host_payload.pop('pwd_pass_mongodb')

                host_payload.pop('pwd_smtp')
                host_payload.pop('pwd_type_smtp')
                host_payload.pop('pwd_user_smtp')
                host_payload.pop('pwd_pass_smtp')

                host_payload.pop('pwd_imap')
                host_payload.pop('pwd_type_imap')
                host_payload.pop('pwd_user_imap')
                host_payload.pop('pwd_pass_imap')

                host_payload.pop('pwd_rtsp')
                host_payload.pop('pwd_type_rtsp')
                host_payload.pop('pwd_user_rtsp')
                host_payload.pop('pwd_pass_rtsp')

                host_payload.pop('pwd_redis')
                host_payload.pop('pwd_pass_redis')

                host_payload.pop('pwd_snmp')
                host_payload.pop('pwd_pass_snmp')

                # host_payload.pop('pwd_timeout')
                # host_payload.pop('pwd_timeout_time')
                # host_payload.pop('pwd_interval')
                # host_payload.pop('pwd_num')
                # host_payload.pop('pwd_threadnum')

            # 最少勾选一项报表类型，默认一直勾选HTML报表
            if self.World_Report_Host_status == False:
                host_payload.pop('report_type_doc')
            if self.Excel_Report_Host_status == False:
                host_payload.pop('report_type_xls')
            if self.PDF_Report_Host_status == False:
                host_payload.pop('report_type_pdf')

            # 最少勾选一项报表内容，默认一直勾选综述报表
            if self.Host_Report_Host_status == False:
                host_payload.pop('report_content_host')
            if self.Auto_Report_Host_status == False:
                host_payload.pop('report_ifcreate')

            # 更新请求头用于新建信息
            s.headers['Accept'] = '*/*'
            s.headers['Content-Type'] = 'application/x-www-form-urlencoded'
            s.headers['Origin'] = f'{SCANNER_URL}'
            s.headers['Connection'] = 'close'
            s.headers['Referer'] = f'{SCANNER_URL}/task/index/1'
            s.headers['X-Requested-With'] = 'XMLHttpRequest'
            s.cookies['left_menustatue_NSFOCUSRSAS'] = f"0|0|{SCANNER_URL}/task/task_entry/"

            ###### 到了这里才是下任务的请求包
            host_resp = s.post(f'{SCANNER_URL}/task/vul/tasksubmit', data=host_payload, verify=False)
            # print(host_resp.text)
            if 'suc' in host_resp.text:
                self.start_host_return.emit(f"共{len(self.task_list_host)}个任务，任务 {host_resp.text.split(':')[2]} 创建成功...")
                output_log(f"新建扫描任务成功，任务编号：{host_resp.text.split(':')[2]} ，任务名称：{task_name}")
            else:
                self.start_host_return.emit(f'第{i}个任务下达任务失败...(详情见log.txt)')
                output_log(f"新建任务失败：{task_name} ，报错信息：{json.loads(host_resp.text[1:-1])}")
                with open('log.txt', 'a') as content:
                    content.write(log_time)
                    content.write(f'     新建任务失败：{task_name}     报错信息：')
                    content.write(host_resp.text + '\n')
                time.sleep(1)
            i += 1
            time.sleep(1)
        self.start_host_return.emit(f'共{len(self.task_list_host)}个任务，所有任务下达完成...')



"""
################################################
#######Web扫描多线程下任务鸭
################################################
"""

class Start_Web_Scan_Working(QThread):
    start_web_return = pyqtSignal(str)

    def __init__(self, web_range_number, web_template_number,
                 Concurrent_Threads_status, Webscan_Timeout_status,
                 Dir_level_status, Dir_limit_status, HTML_Report_Web_status,
                 World_Report_Web_status, Excel_Report_Web_status,
                 PDF_Report_Web_status, Summary_Report_Web_status,
                 Host_Report_Web_status, Auto_Report_Web_status,
                 Scan_time_web_status, New_WebAssets_list):
        super(Start_Web_Scan_Working, self).__init__()

        self.web_range = web_range_number
        self.web_template = web_template_number
        self.Concurrent_Threads_status = Concurrent_Threads_status
        self.Webscan_Timeout_status = Webscan_Timeout_status
        self.Dir_level_status = Dir_level_status
        self.Dir_limit_status = Dir_limit_status
        self.HTML_Report_Web_status = HTML_Report_Web_status
        self.World_Report_Web_status = World_Report_Web_status
        self.Excel_Report_Web_status = Excel_Report_Web_status
        self.PDF_Report_Web_status = PDF_Report_Web_status
        self.Summary_Report_Web_status = Summary_Report_Web_status
        self.Host_Report_Web_status = Host_Report_Web_status
        self.Auto_Report_Web_status = Auto_Report_Web_status
        self.Scan_time_web_status = Scan_time_web_status
        self.task_list_web = New_WebAssets_list

    def run(self):

        # 更新请求头用于新建信息
        s.headers['Referer'] = f'{SCANNER_URL}/task/task_entry/'
        s.cookies['left_menustatue_NSFOCUSRSAS'] = f"0|0|{SCANNER_URL}/task/task_entry/"
        content = s.get(f'{SCANNER_URL}/task/index/8', verify=False, allow_redirects=False)

        ###### 获取Web扫描任务的csrfmiddlewaretoken
        global web_csrfmiddlewaretoken
        web_csrfmiddlewaretoken = re.findall("""csrfmiddlewaretoken":\'(.+)\'""", content.text)[0]
        output_log("[+] Web扫描的csrfmiddlewaretoken获取成功！")

        ###### 扫描器下的任务要很多的参数，下边都是POST请求要发送的准备数据
        # 扫描时间段
        if self.Scan_time_web_status == '':
            self.Scan_time_web = ""
        else:
            self.Scan_time_web = self.Scan_time_web_status

        i = 1
        for _task in self.task_list_web:
            self.start_web_return.emit(f'共{len(self.task_list_web)}个任务，正在下达第{i}个任务...')
            task_info = _task.split('|')
            try:
                task_name = task_info[0].strip()
                task_time = task_info[1].strip()
                task_start_time = 'timing'
            except Exception as e:
                task_name = _task.strip()
                task_time = servertime
                task_start_time = 'immediate'

            # web扫描任务名称和资产处理
            urllist = ''
            global url_count
            url_count = 0
            try:
                with open('./Assets_URL/' + task_name + '.txt') as cent:
                    for url in cent:
                        urllist += ';' + url.strip()
                        url_count += 1
            except Exception as e:
                self.start_web_return.emit('警告！找不到相关资产，请检查！'.format(len(self.task_list_web), i))
                output_log(f'[!] 找不到任务资产：{task_name}，请检查！')
                with open('log.txt', 'a') as content:
                    content.write(f'找不到任务资产：{task_name}\n')
                time.sleep(1)
                break

            web_payload = {
                'csrfmiddlewaretoken': web_csrfmiddlewaretoken,
                'target_count': url_count,  # 该参数输入扫描地址数量
                'config_task': 'taskname',
                'task_config': '',
                'task_target': urllist[1:],  # 该参数输入扫描地址
                'task_name': task_name,  # 该参数输入任务名称
                'scan_method': self.web_range,  # 该参数输入漏洞模板
                'subdomains_scan': '0',
                'subdomains': '',
                'exec': task_start_time,  # 该参数输入扫描时间属性
                'exec_timing_date': task_time,  # 该参数输入扫描时间
                'exec_everyday_time': '00:00',
                'exec_everyweek_day': '1',
                'exec_everyweek_time': '00:00',
                'exec_emonthdate_day': '1',
                'exec_emonthdate_time': '00:00',
                'exec_emonthweek_pre': '1',
                'exec_emonthweek_day': '1',
                'exec_emonthweek_time': '00:00',
                'tpl': self.web_template,  # 该参数控制漏洞模板
                'ws_proxy_type': 'HTTP',
                'ws_proxy_auth': 'Basic',
                'ws_proxy_server': '',
                'ws_proxy_port': '',
                'ws_proxy_username': '',
                'ws_proxy_password': '',
                'cron_range': self.Scan_time_web,  # 该参数控制扫描时间段
                'dispatchLevel': '2',
                'target_description': '',
                'report_type_html': 'html',
                'report_type_doc': 'doc',
                'report_type_xls': 'xls',
                'report_type_pdf': 'pdf',
                'summarizeReport': 'yes',
                'oneSiteReport': 'yes',
                'sum_report_tpl': '201',
                'site_report_tpl': '301',
                'auto_export': 'yes',
                'sendReport_type': 'html',
                'email_address': '',
                'plugin_threads': self.Concurrent_Threads_status,  # 该参数控制并发线程数
                'webscan_timeout': self.Webscan_Timeout_status,  # 该参数控制超时限制
                'page_encoding': '0',
                'coding': 'UTF8',
                'login_ifuse': 'yes',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
                'dir_level': self.Dir_level_status,  # 该参数控制目录猜测范围
                'dir_limit': self.Dir_limit_status,  # 该参数控制目录猜测深度
                'filetype_to_check_backup': 'shtml,php,jsp,asp,aspx',
                'backup_filetype': 'bak,old',
                'scan_type': '0',
                'dir_files_limit': '-1',  # 该参数控制单文件目录数
                'dir_depth_limit': '15',  # 该参数控制目录深度
                'scan_link_limit': '-1',  # 该参数控制链接总数
                'case_sensitive': '1',
                'if_javascript': '1',
                'if_repeat': '2',
                'protocalarray': '[{"target": "%s", "protocal_type": "auto", "protocal_name": "", "protocal_pwd": "", "login_scan_type": "no", "cookies": "", "cookie_type": "set_cookie", "black_links": "", "wihte_links": "", "form_switch": "yes", "form_cont": "no", "form_str": ""}]' %urllist[1],
            }

            # 最少勾选一项报表类型，默认一直勾选HTML报表
            if self.World_Report_Web_status == False:
                web_payload.pop('report_type_doc')
            if self.Excel_Report_Web_status == False:
                web_payload.pop('report_type_xls')
            if self.PDF_Report_Web_status == False:
                web_payload.pop('report_type_pdf')

            # 最少勾选一项报表内容，默认一直勾选综述报表
            if self.Host_Report_Web_status == False:
                web_payload.pop('oneSiteReport')

            if self.Auto_Report_Web_status == False:
                web_payload.pop('auto_export')

            # 更新请求头用于新建信息
            s.headers['Accept'] = '*/*'
            s.headers['Content-Type'] = 'application/x-www-form-urlencoded'
            s.headers['Origin'] = f'{SCANNER_URL}'
            s.headers['Connection'] = 'close'
            s.headers['Referer'] = f'{SCANNER_URL}/task/index/8'
            s.headers['X-Requested-With'] = 'XMLHttpRequest'
            s.cookies['left_menustatue_NSFOCUSRSAS'] = f"0|0|{SCANNER_URL}/task/task_entry/"

            ###### 到了这里才是下任务的请求包
            web_resp = s.post(f'{SCANNER_URL}/task/vul/web_newtask/', data=web_payload, verify=False)

            if 'suc' in web_resp.text:
                self.start_web_return.emit(f"共{len(self.task_list_web)}个任务，任务 {web_resp.text.split(':')[2]} 创建成功...")
                output_log(f"新建扫描任务成功，任务编号：{web_resp.text.split(':')[2]} ，任务名称：{task_name}")
            else:
                self.start_web_return.emit(f'第{i}个任务下达任务失败...(详情见log.txt)')
                output_log(f"新建任务失败：{task_name} ，报错信息：{json.loads(web_resp.text[1:-1])}")
                with open('log.txt', 'a') as content:
                    content.write(log_time)
                    content.write(f'     新建任务失败：{task_name}     报错信息：')
                    content.write(web_resp.text + '\n')
                time.sleep(1)
            i += 1
            time.sleep(1)
        self.start_web_return.emit(f'共{len(self.task_list_web)}个任务，所有任务下达完成...')


"""
################################################
#######线程获取扫描器进行&等待任务数量，以及扫描时间
################################################
"""

class RSAS_Status(QThread):
    log_return = pyqtSignal(str)

    def __init__(self):
        super(RSAS_Status, self).__init__()

    def run(self):
        task_re = """<input type='hidden' value='(.*?)' id = 'taskids' />"""
        time_re = """<span id ="sys_time">(.*?)</span>"""
        # 更新请求头用于新建信息
        s.headers['Connection'] = 'keep-alive'
        s.headers['Referer'] = f'{SCANNER_URL}'
        while True:
            ###### 获取当前运行任务数量
            now_task = s.get(SCANNER_URL + '/system/get_task_num/', verify=False, allow_redirects=False)
            nowtask_num = now_task.text

            ###### 获取等待扫描任务数量
            wait_task = s.get(SCANNER_URL + '/system/get_remain_task/', verify=False, allow_redirects=False)
            waittask_num = wait_task.text

            ###### 获取扫描器的时间
            global servertime
            sys_time = s.get(SCANNER_URL + '/system/getInfo/', verify=False, allow_redirects=False)
            json_response = sys_time.content.decode()
            server_time = json.loads(json_response).get('time')
            server_cpu = json.loads(json_response).get('cpu')
            server_mem = json.loads(json_response).get('mem')
            server_disk = json.loads(json_response).get('disk')

            self.log_return.emit(f'{nowtask_num}|{waittask_num}|{server_time}|{server_cpu}|{server_mem}|{server_disk}')
            time.sleep(10)
