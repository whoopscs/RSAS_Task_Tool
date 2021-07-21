# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author         :  s0nder
@Email          :  wylsyr@gmail.com
------------------------------------
@File           :  rsas_portsinfo.py
@Version        :  1.0
@Description    :  绿盟扫描报告端口提取
@CreateTime     :  2020/12/30 0018 14:27
------------------------------------
@Software       :  VSCode
"""

# here put the import lib

import re,os,xlwt,xlrd
from lxml import etree

def Main():

    final=[]
    file_list = os.listdir()

    for i in file_list:
        if os.path.splitext(i)[1] == '.html':
            fsize  = os.stat(i).st_size
            fsize = fsize / float(1024)

            if fsize < 3072:
                final.append(i)


    try:
        workbook = xlwt.Workbook(encoding='ascii')
        worksheet = workbook.add_sheet('Sheet1')
        worksheet.write(0, 0, 'ip')
        worksheet.write(0, 1, '端口')
        worksheet.write(0, 2, '协议')
        worksheet.write(0, 3, '服务')
        worksheet.write(0, 4, '状态')
        workbook.save('results.xls')
    except Exception as e:
        print(e)
        print('创建文件失败')
    
    try:
        sum_ports = 0
        for html_file in final:
    
            file_path =  html_file
    
            if os.path.isfile(file_path):
    
                print("read file: " + html_file)
    
                with open(file_path,'r', encoding='UTF-8') as file:
                    file_text = file.read()
                    html = etree.HTML(file_text)  #  初始化生成一个XPath解析对象
                    # 模糊匹配获取所有包含"端口信息"div节点后面的兄弟div节点下tr标签下td标签里的内容
                    text = html.xpath('//div[contains(text(),"端口信息")]/following-sibling::div[1]//tbody/tr/td//text()')
    
                if text != []:
                    for i in range(len(text)):
                        text[i] = text[i].strip()  # 移除字符串头尾指定的字符（默认为空格或换行符） strip去除两边 lstrip去除左边 rstrip去除右边
                    
                    #filter_text = list(filter(None, text))
                    split_text = [text[i:i + 4] for i in range(0, len(text), 4)]  # 4个为一组分割list
    
                    data = xlrd.open_workbook('results.xls')
                    table = data.sheet_by_name(u'Sheet1')  #  通过名称获取
                    row = table.nrows
    
                    print(f"Contains the number of ports  :  {str(len(split_text))}")
                    sum_ports += len(split_text)

                    for list_count in range(0, len(split_text)):
                        worksheet.write(row + list_count, 0, html_file.replace('.html', ''))

                        for rows_count in range (len(split_text[list_count])):
                            worksheet.write(row + list_count , rows_count + 1, split_text[list_count][rows_count])
                else:
                    pass

                workbook.save('results.xls')

        print(f"\n[+]绿盟报告端口提取已完成，开放端口总数：{sum_ports}个\n")
    except Exception as e:
        print(e)
        print("\n[-]运行出现错误！！！！\n")


if __name__ == "__main__":
    Main()
