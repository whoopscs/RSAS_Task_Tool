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
requests.packages.urllib3.disable_warnings()
from core.window_login import login_window
from PyQt5.QtWidgets import QApplication
import zipfile
from tqdm import tqdm
from jsonpath import jsonpath


version = "v2.0"


def checkForUpdates():
    # remote_address = "https://api.github.com/repos/wylsy/RSAS_Task_Tool/releases"
    remote_address = "https://gitee.com/api/v5/repos/s0nder/RSAS_Task_Tool/releases"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
    }
    try:
        res = requests.get(url=remote_address, headers=headers)
        if res.status_code == 200:
            res_json = json.loads(res.text)
            tag_name = ''.join(jsonpath(res_json, "$..tag_name"))
            if tag_name != version:
                print(f"检测到新版本：{tag_name}，当前版本：{version}")
                
                # browser_download_url = ''.join(jsonpath(res_json, "$..browser_download_url"))
                # file_name = browser_download_url.split('/')[-1]
                
                browser_download_url = ''.join(jsonpath(res_json, "$..browser_download_url")[0])
                file_name = ''.join(jsonpath(res_json, "$..assets..name"))

                file_path = os.path.join(os.getcwd(), file_name)
                res = requests.get(browser_download_url, stream=True)
                content_size = int(int(res.headers["Content-Length"]) / 1024 + 0.5)

                with open(file_path, 'wb') as fd:
                    print(f'下载更新文件：{file_name},文件大小：{content_size}KB')
                    for chunk in tqdm(iterable=res.iter_content(1024), total=content_size, unit='k', desc=None):
                        if chunk:
                            fd.write(chunk)
                time.sleep(1)
                installUpdate(file_path)
            else:
                print(f"更新检测完成！当前版本{version}，已是最新版本。")
    except Exception as e:
        print(f"更新失败! 请手动更新。{e}")


def installUpdate(file_path):
    zf = zipfile.ZipFile(file_path, mode='r')
    for names in zf.namelist():
        f = zf.extract(names, './')
    zf.close()
    os.remove(file_path)
    print('更新完成！请重新运行程序。')
    sys.exit()


if __name__ == "__main__":
    checkForUpdates()
    app = QApplication(sys.argv)
    login_window = login_window(mode=0)
    login_window.show()
    sys.exit(app.exec_())