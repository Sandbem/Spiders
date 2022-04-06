''' coding: utf-8
INFO: 爬取 http://wdc.kugi.kyoto-u.ac.jp/wdc/Sec3.html 网站 Dst 数据
date: 2022-03-19 Washy [CUG washy21@163.com]
func:
    get_Dst     - 获取指定url的Dst数据
    save_Dst    - 存储Dst数据到指定路径
    update_Dst  - 更新最近一个月的Dst数据
'''

import os
import datetime
import requests
import matplotlib.pyplot as plt
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
    
    date = datetime.datetime.utcnow()
    year = date.year
    month = date.month - 1
    if month == 0:
        year -= 1
        month = 12
    lastfilename = '{:d}{:02d}.txt'.format(year, month)
    lastfilepath = os.path.join(folderpath, lastfilename)
    if not os.path.exists(lastfilepath):
        print("更新上个月的数据: ", end='')
        
        lasturl = "http://wdc.kugi.kyoto-u.ac.jp/dst_realtime/lastmonth/index.html"
        lastdata = get_Dst(lasturl)
        save_Dst(lastfilepath, lastdata)

        print("更新成功 (本月仅会执行一次)")

    # 文件名
    filename = 'presentmonth.txt'
    # 文件绝对路径
    filepath = os.path.join(folderpath, filename)

    # url
    url = 'http://wdc.kugi.kyoto-u.ac.jp/dst_realtime/presentmonth/index.html'
    
    data = get_Dst(url)
    save_Dst(filepath, data)

##----------------------------------------------------------------------##
# INFO: 绘制指定文件名称的Dst数据
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 存储根目录 './Dst'
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/19
##----------------------------------------------------------------------##
def plt_Dst(filepath,savepath):
    with open(filepath, 'r') as f:
        data = f.read()
    # 去除表头
    str_list = data[255:].split()
    # 转为整型
    int_list = [int(i) for i in str_list]
    del int_list[0:len(str_list):25]
    del int_list[int_list.index(9999):]

    date = datetime.datetime.utcnow()

    plt.figure(figsize=[20,4])
    plt.plot(int_list)
    plt.grid('on',which='major')

    plt.xlim([0,744])
    plt.ylim([-500,99])
    plt.title('Realtime Dst Index    Created at ' +\
        '{} UT'.format(date))

    xticks = list(range(0,744,24))
    xticks_str = list(range(1,32))
    plt.xticks(xticks,xticks_str)

    plt.xlabel('Days')
    plt.ylabel('Dst [nT]')

    plt.savefig(savepath, dpi=300, bbox_inches='tight')

    plt.close()

##----------------------------------------------------------------------##
if __name__ == "__main__":
    import time

    # 跟路径
    rootpath = '/Volumes/Washy5T/SpaceWeather/Dst'
    # 实时图片生成
    filepath = os.path.join(rootpath,'dst_realtime/presentmonth.txt')
    savepath = os.path.join(rootpath,'dst_realtime/presentmonth.png')
    
    # 更新次数
    idx = 1
    # 死循环更新程序, 1h运行一次
    while True:
        print("第{:03d}次更新: ".format(idx), end='')
        try:
            update_Dst(rootpath)
            print('更新成功 (一小时后进行下次更新)')
            
            print("生成实时图片.")
            plt_Dst(filepath,savepath)
        except Exception as e:
            print('更新失败 (一小时后进行下次更新)')
            print('error', e)
        finally:
            idx += 1
            time.sleep(3600)
    
    
