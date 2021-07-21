# !/usr/bin/python3
# -*- coding: utf-8 -*-
'''
@Author         :  s0nder
@Email          :  wylsyr@gmail.com
------------------------------------
@File           :  rsas_扫描报告批量下载.py
@CreateTime     :  2021/02/23 15:36:00
@Version        :  1.0
@Description    :  扫描报告批量下载
------------------------------------
@Software       :  VSCode
'''

# here put the import lib
import os
import re
import time

from selenium.webdriver.support.select import Select
from msedge.selenium_tools import Edge, EdgeOptions

def driver_login(url,username,password,tasks,download_path,driver):

    url = url
    username = username 
    password = password

    driver.get(url)

    time.sleep(1)

    driver.find_element_by_id("username").click()
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").click()
    driver.find_element_by_id("password").send_keys(password)

    time.sleep(1)

    driver.find_element_by_xpath("//input[@class='submit']").click()

    time.sleep(1)

    driver.find_element_by_xpath("//span[contains(text(), '下载最近输出的报表')]/..").click()
    
    time.sleep(1)

    # 切换iframe
    driver.switch_to.frame("mainFrame")
    # 释放iframe，重新回到主页面上
    # driver.switch_to.default_content()

    time.sleep(2)

    #driver.manage().timeouts().implicitlyWait(3, TimeUnit.SECONDS)
    opt = driver.find_element_by_id("page_size")
    # print(opt.is_enabled())
    Select(opt).select_by_visible_text('100')

    time.sleep(2)

    i=1

    for task in tasks:

        dir_name = driver.find_element_by_xpath(f"//td[contains(text(),'{task}')]").text
        
        print(dir_name)
        
        try:
            dir = re.search('(?<=月份).*?(?=_202)',dir_name).group(0)
        except:
            dir = re.search('(?<=月份).*?(?=_____)',dir_name).group(0)
        
        
        # 去除字符串中的空行
        # print("".join([s for s in dir.splitlines(True) if s.strip()]))

        dir_path = download_path+dir

        file_urls = driver.find_elements_by_xpath(f"//td[contains(text(),'{task}')]/following-sibling::td[3]/a")

        for file_url in file_urls:
            set_download_path(driver,dir_path)
            # print(file_url.get_attribute("href"))
            # driver.get(file_url.get_attribute("href"))
            file_url.click()
            time.sleep(1)

        print(f"{i}项任务：{dir} 下载完成！")

        time.sleep(2)

        i++

###### 动态设置下载路径
def set_download_path(driver, path):
        """
        禁止下载弹窗，设置下载路径
        """
        path = path.rstrip(os.sep)
        ###### “此类型的文件可能会损害您的计算机。您仍然要保留XXX吗？”
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior',
                  'params': {'behavior': 'allow', 'downloadPath': path}}
        driver.execute("send_command", params)
        if not os.path.exists(path):
            os.makedirs(path)


if __name__ == "__main__":

    # 替换成你的用户名  密码
    url = "https://10.243.96.218/accounts/login_view/"
    username = "admin" 
    password = "ahydaas@2015"

    download_path = "D:\\GS\\重要系统漏洞扫描\\2021\\6月份重要系统\\扫描结果\\"
    tasks = ["10243","10244","10245","10246","10247","10248","10249","10250","10251","10252","10253","10254","10255","10256","10257","10258","10259","10260","10261","10262","10263","10264","10265","10266","10267","10268","10269","10270","10271","10272","10273","10274","10275","10276","10277","10278","10279","10280","10281","10282","10283","10284","10285","10286","10287","10288","10289","10290","10291","10292","10293","10294"]

    """edge浏览器"""
    edgedriver = "./msedgedriver.exe" #这里写本地的edgedriver的所在路径
    edge_options = EdgeOptions()
    edge_options.use_chromium = True # 使用谷歌内核
    edge_options.add_argument("headless") # 隐藏窗口启动
    # edge_options.add_argument("-inprivate") # 隐私模式
    # edge_options.add_extension(extension_path) # 加载扩展列表
    edge_options.add_argument("disable-gpu") # 禁用gpu加速，避免bug
    edge_options.add_argument('start-maximized') # 启动最大化
    edge_options.add_argument('--ignore-certificate-errors') # 绕过“你的连接不是专用连接”
    edge_options.add_experimental_option('useAutomationExtension', False) # 关闭“Microsoft Edge正由自动测试软件控制。”
    edge_options.add_experimental_option('excludeSwitches', ['enable-automation','enable-logging'])
    # 打开Edge浏览器
    driver = Edge(executable_path=edgedriver,options=edge_options)

    driver_login(url,username,password,tasks,download_path,driver)

    time.sleep(10)

    print("所有任务都已下载完成！")
