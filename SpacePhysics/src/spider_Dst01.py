''' coding: utf-8
INFO: 爬取 http://wdc.kugi.kyoto-u.ac.jp/wdc/Sec3.html 网站 Dst 数据
date: 2022-03-19 Washy [CUG washy21@163.com]
func:
    get_Dst     - 获取指定url的Dst数据
    save_Dst    - 存储Dst数据到指定路径
    update_Dst  - 更新最近一个月的Dst数据
'''

import os
import time
import requests
from bs4 import BeautifulSoup

##----------------------------------------------------------------------##
# INFO: 爬取指定年月url下的Dst指数
##----------------------------------------------------------------------##
# Inputs:
#   url         - 指定年月的url [str]
# Outputs:
#   data        - 该月份下所有的Dst数据 [list]
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/19
##----------------------------------------------------------------------##
def get_Dst(url):
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
        f.write("        unit=nT                                  "+\
            "                                                       "+\
            "                  UT\n")
        f.write("        1    2    3    4    5    6    7    8    9"+\
            "   10   11   12   13   14   15   16   17   18   19   20"+\
            "   21   22   23   24\n")
        f.write("Days\n")
        # 循环存储每一天24h的数据
        for idx in range(len(data)//101):
            # 获取一天的数据
            ddata = data[idx*101:(idx+1)*101]
            # 构造每4个字符一个数据的格式
            ddata = '  ' + ddata[:2] + ddata[3:35] + ddata[36:69] + ddata[70:]
            
            for i  in range(25):
                f.write('%4s ' % ddata[i*4:(i+1)*4])
            
            f.write('\n')

##----------------------------------------------------------------------##
# INFO: 爬取 http://wdc.kugi.kyoto-u.ac.jp/dst_final/index.html 网站的
#   Final Dst index
##----------------------------------------------------------------------##
# Inputs:
#   syear       - 开始年份 >=1957
#   eyear       - 终止年份 <=2014
#   rootpath    - 存储根目录 './Dst'
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/19
##----------------------------------------------------------------------##
def download_final(syear, eyear, rootpath='./Dst'):
    # 创建文件夹
    folderpath = os.path.join(rootpath, 'dst_final')
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    
    print(".......... downloading ..........")

    for year in range(syear, eyear+1):
        for month in range(1, 13):
            # 生成文件名
            filename = "{:d}{:02d}.txt".format(year,month)
            # 生成文件绝对路径
            filepath = os.path.join(folderpath, filename)
            # 当前年份月份对应的url
            url = "http://wdc.kugi.kyoto-u.ac.jp/dst_final/" + \
                "{:d}{:02d}/index.html".format(year, month)
            
            # 提示信息
            print("正在下载: " + filename)
            
            # 获取数据
            data = get_Dst(url)
            # 存储数据
            save_Dst(filepath, data)

    print("............ finish ............")

##----------------------------------------------------------------------##
# INFO: 爬取 http://wdc.kugi.kyoto-u.ac.jp/dst_provisional/index.html 网站的
#   Provisional Dst index
##----------------------------------------------------------------------##
# Inputs:
#   syear       - 开始年份 >=2015
#   eyear       - 终止年份 <=2019
#   rootpath    - 存储根目录 './Dst'
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/19
##----------------------------------------------------------------------##
def download_provisional(syear, eyear, rootpath='./Dst'):
    # 创建文件夹
    folderpath = os.path.join(rootpath, 'dst_provisional')
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    
    print(".......... downloading ..........")

    for year in range(syear, eyear+1):
        for month in range(1, 13):
            # 生成文件名
            filename = "{:d}{:02d}.txt".format(year,month)
            # 生成文件绝对路径
            filepath = os.path.join(folderpath, filename)
            # 当前年份月份对应的url
            url = "http://wdc.kugi.kyoto-u.ac.jp/dst_provisional/" + \
                "{:d}{:02d}/index.html".format(year, month)
            
            # 提示信息
            print("正在下载: " + filename)
            time.sleep(1)
            
            # 获取数据
            data = get_Dst(url)
            # 存储数据
            save_Dst(filepath, data)
    
    print("............ finish ............")

##----------------------------------------------------------------------##
# INFO: 爬取 http://wdc.kugi.kyoto-u.ac.jp/dst_realtime/index.html 网站最新
#   一个月的 Real-time (Quicklook) Dst index
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 存储根目录 './Dst'
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/19
##----------------------------------------------------------------------##
def update_Dst(rootpath='./Dst'):
    # 创建文件夹
    folderpath = os.path.join(rootpath, 'dst_realtime')
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    
    # 文件名
    filename = 'presentmonth.txt'
    # 文件绝对路径
    filepath = os.path.join(folderpath, filename)

    # url
    url = 'http://wdc.kugi.kyoto-u.ac.jp/dst_realtime/presentmonth/index.html'
    
    data = get_Dst(url)
    save_Dst(filepath, data)

##----------------------------------------------------------------------##
if __name__ == "__main__":
    # 
    rootpath = '/Volumes/Washy5T/SpaceWeather/Dst'
    # 
    # download_final(1957, 2014, rootpath)
    #
    # download_provisional(2015, 2019, rootpath)
    idx = 1
    while True:
        print("第{:03d}次更新: ".format(idx), end='')
        try:
            update_Dst(rootpath)
            print('更新成功 (一小时后进行下次更新)')
        except Exception as e:
            print('更新失败 (一小时后进行下次更新)')
            print('error', e)
        finally:
            idx += 1
            time.sleep(60)
    
