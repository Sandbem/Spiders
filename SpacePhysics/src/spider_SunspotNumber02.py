''' coding: utf-8
INFO: 爬取ftp://ftp.swpc.noaa.gov/pub/indices/old_indices下Sunspot Number.
date: 2022-03-21,23 Washy [CUG washy21@163.com]
'''

import os
import sys
import socket
import datetime

from ftplib import FTP
from ftplib import error_perm

##----------------------------------------------------------------------##
# INFO: ftp网站连接
##----------------------------------------------------------------------##
# Outputs:
#   ftp         - ftp根目录
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21,23
##----------------------------------------------------------------------##
def ftp_connect():
    # FTP站点
    host = 'ftp.swpc.noaa.gov'
    # 端口号
    port = 21
    # 文件夹路径
    folderpath = '/pub/indices/old_indices'
 
    ftp = FTP()
    ftp.encoding = 'utf-8'
    
    try:
        ftp.connect(host, port)
        ftp.login()
        ftp.cwd(folderpath)
    except(socket.error, socket.gaierror):  # ftp 连接错误
        print("ERROR: cannot connect [{}:{}]".format(host, port))
        return None
    except error_perm:  # 用户登录认证错误
        print("ERROR: user Authentication failed ")
        return None
    
    return ftp

def is_ftp_file(ftp_conn, filename):
    try:
        if filename in ftp_conn.nlst(os.path.dirname(filename)):
            return True
        else:
            return False
    except error_perm:
        return False

##----------------------------------------------------------------------##
# INFO: 对从ftp下载的数据文件进行重新存储
##----------------------------------------------------------------------##
# Inputs:
#   folderpath  - 重新存储数据的文件夹绝对路径
#   filepath    - 需要重新存储的原始数据文件绝对路径
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21,23
##----------------------------------------------------------------------##
def resave_quarter_sn(folderpath, filepath, idxf=13, flag=True):
    # 打开数据文件
    with open(filepath, 'r') as f:
        # 跳过前13行
        for i in range(idxf): next(f)
        # 读取数据
        data = f.read().split()

    # 提取 年 月 日 太阳黑子数
    data_y = data[0::16]
    data_m = data[1::16]
    data_d = data[2::16]
    data_sn = data[4::16]

    # 遍历所有的月份
    for each in sorted(list(set(data_m))):
        # 每个月份数据的起始索引
        idxm = data_m.index(each)
        # 保存文件名
        savename = data_y[idxm] + data_m[idxm] + '.txt'
        # 保存文件名绝对路径
        savepath = os.path.join(folderpath, savename)
        
        # 文件已存在则开始下一循环
        if os.path.exists(savepath) and flag:
            continue
        
        print('正在下载: ' + savename)
        # 另存文件
        f = open(savepath, 'w')
        # 生成表头
        f.write('YYYY  MM  DD  SunspotNumber\n')
        # 循环所有数据
        for idx in range(idxm,len(data_m)):
            # 月份不同时跳出循环
            if data_m[idx] != data_m[idxm]:
                break
            # 存入当前月份数据
            f.write('%4s  %2s  %2s  %4s\n' % (data_y[idx], data_m[idx], \
                data_d[idx], data_sn[idx]))
        # 关闭文件
        f.close()

##----------------------------------------------------------------------##
# INFO: 下载指定FTP文件并重新存储
##----------------------------------------------------------------------##
# Inputs:
#   ftp         - ftp
#   rootpath    - 根目录
#   filename    - FTP文件名
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21,23
##----------------------------------------------------------------------##
def download_sn(ftp, rootpath, filename):
    # 创建文件夹
    folderpath = os.path.join(rootpath, 'SunspotNumber/Data')
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
    # 临时文件
    tempfilepath = os.path.join(folderpath, 'temp.txt')
    # FTP: 文件名是否存在
    if is_ftp_file(ftp, filename):
        # 下载指定文件到临时文件
        with open(tempfilepath, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write, 1024)
    else:
        print('文件不存在: ' + filename)
        sys.exit()
    
    year = int(filename[:4])
    if year==1997 or year in range(2000,2007):
        idxf = 12
    else:
        idxf = 13
    # 判断是否跳过本年数据
    if year==datetime.datetime.utcnow().year:
        flag = False
    else:
        flag = True
    # 数据重新存储
    resave_quarter_sn(folderpath, tempfilepath, idxf, flag)

##----------------------------------------------------------------------##
# INFO: 下载2018年至今的太阳黑子数
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 根目录
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21,23
##----------------------------------------------------------------------##
def download_sn_all(rootpath):
    # 连接站点
    ftp = ftp_connect()
    
    # 获取当前世界时
    date = datetime.datetime.utcnow()
    
    # # 爬取1997年至2017年的数据
    # for year in range(1997,2018):
    #     # FTP文件名
    #     filename = '{:d}_DSD.txt'.format(year)
    #     # 下载数据
    #     download_sn(ftp, rootpath, filename)
    
    # 爬取2018年至前一年的数据
    for year in range(2018, date.year):
        for idx in range(1,5):
            # FTP文件名
            filename = '{:d}Q{:d}_DSD.txt'.format(year,idx)
            # 下载数据
            download_sn(ftp,rootpath,filename)
    
    # 本年索引上限
    idx_now = (date.month-1)//3 + 2
    # 爬取本年的数据
    for idx in range(1,idx_now):
        # FTP文件名
        filename = '{:d}Q{:d}_DSD.txt'.format(date.year,idx)
        # 下载数据
        download_sn(ftp,rootpath,filename)
    
    # 断开站点
    ftp.quit()

##----------------------------------------------------------------------##
if __name__ == '__main__':
    # 存储根目录
    rootpath = '/Volumes/Washy5T/SpaceWeather'
    # 下载所有的太阳黑子数
    download_sn_all(rootpath)
