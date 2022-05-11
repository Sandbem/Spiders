''' coding: utf-8
INFO: 爬取 http://wdc.kugi.kyoto-u.ac.jp/wdc/Sec3.html 网站 Dst 数据
date: 2022-03-19,22,23 Washy [CUG washy21@163.com]
func:
    get_Dst_month       - 获取指定url的Dst数据
    save_Dst            - 存储Dst数据到指定路径
    download_Dst_all    - 下载所有的Dst数据
'''

import os
import sys 
import time
import requests
import datetime

from bs4 import BeautifulSoup

##----------------------------------------------------------------------##
# INFO: 爬取指定年月的Dst指数
##----------------------------------------------------------------------##
# Inputs:
#   year        - 年 [int]
#   month       - 月 [int]
# Outputs:
#   data        - 该月份下所有的Dst数据 [list]
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/19,22,23
##----------------------------------------------------------------------##
def get_Dst_month(year, month):
    # 判断year month属于哪个文件夹
    if year>=1957 and year<=2014:
        dst_version = 'dst_final'
    elif year>=2015 and year<=2019:
        dst_version = 'dst_provisional'
    elif year>=2020:
        dst_version = 'dst_realtime'
    else:
        print('ERROR: Data Not Found!')
        # 终止程序
        sys.exit()

    # 当前年份月份对应的url
    url = "http://wdc.kugi.kyoto-u.ac.jp/" + dst_version + \
        "/{:d}{:02d}/index.html".format(year, month)
    
    # 伪装浏览器请求头
    UserAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ' + \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.' + \
        '51 Safari/537.36'
    # 获取网页内容
    res = requests.get(url, headers={'user-agent': UserAgent})
    # 将网页内容转成bs4 soup格式
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 获取pre节点的文本信息并去除换行符 (410字符之后为Dst数据)
    return soup.pre.get_text()[410:].replace('\n', '')

##----------------------------------------------------------------------##
# INFO: 保存Dst数据到指定文件
##----------------------------------------------------------------------##
# Inputs:
#   filepath    - 指定文件的绝对路径 [str]
#   data        - 指定年月的Dst数据 [str]
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/19
##----------------------------------------------------------------------##
def save_Dst(filepath, data):
    with open(filepath, 'w') as f:
        # 文件头说明
        f.write("        unit=nT                                  " + \
            "                                                     " + \
            "                    UT\n")
        f.write("        1    2    3    4    5    6    7    8    9" + \
            "   10   11   12   13   14   15   16   17   18   19   " + \
            "20   21   22   23   24\n")
        f.write("Days\n")
        # 循环存储每一天24h的数据
        for idx in range(len(data)//101):
            # 获取一天的数据
            ddata = data[idx*101:(idx+1)*101]
            # 构造每4个字符一个数据的格式
            ddata = '  ' + ddata[:2] + ddata[3:35] + ddata[36:68] + \
                ddata[69:]
            
            for i  in range(25):
                f.write('%4s ' % ddata[i*4:(i+1)*4])
            
            f.write('\n')

##----------------------------------------------------------------------##
# INFO: 下载所有的Dst数据到指定文件夹
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 根目录 [str]
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/22,23
##----------------------------------------------------------------------##
def download_Dst_all(rootpath):
    # 文件夹路径
    folderpath = os.path.join(rootpath, 'Dst/Data')
    # 创建文件夹
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    # 获取当前时间
    date = datetime.datetime.utcnow()
    # 下载所有的历史数据 1957-?
    for year in range(2018, date.year):
        for month in range(1,13):
            # 生成文件名
            filename = "{:d}{:02d}.txt".format(year,month)
            # 生成文件绝对路径
            filepath = os.path.join(folderpath, filename)
            # 文件已存在则跳过
            if os.path.exists(filepath):
                print("文件已存在: " + filename)
                continue
            # 提示信息
            print("正在下载: " + filename)
            time.sleep(1)
            # 获取数据
            data = get_Dst_month(year, month)
            # 存储数据
            save_Dst(filepath, data)
    
    # 下载本年数据
    for month in range(1,date.month+1):
        # 生成文件名
        filename = "{:d}{:02d}.txt".format(date.year,month)
        # 生成文件绝对路径
        filepath = os.path.join(folderpath, filename)
        # 提示信息
        print("正在下载: " + filename)
        time.sleep(1)
        # 获取数据
        data = get_Dst_month(date.year, month)
        # 存储数据
        save_Dst(filepath, data)

##----------------------------------------------------------------------##
if __name__ == '__main__':
    # 根目录
    rootpath = '/Volumes/Washy5T/SpaceWeather'
    # 主函数
    download_Dst_all(rootpath)
