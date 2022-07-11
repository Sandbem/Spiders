''' coding: utf-8
INFO: 爬取ftp://ftp.swpc.noaa.gov/pub/lists/ace下太阳风和行星际磁场数据.
date: 2022-07-11 Washy [CUG washy21@163.com]
'''

import os
import socket

from ftplib import FTP
from ftplib import error_perm

##----------------------------------------------------------------------##
# INFO: ftp网站连接
##----------------------------------------------------------------------##
# Inputs:
#   host            - 主机名
#   port            - 端口号
#   ftpfoldpath     - ftp文件夹路径
# Outputs:
#   ftp             - ftp
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21,23; 07/11
##----------------------------------------------------------------------##
def ftp_connect(host,port,ftpfoldpath):
    ftp = FTP()
    ftp.encoding = 'utf-8'
    
    try:
        # 登录FTP
        ftp.connect(host, port)
        ftp.login()
        # 跳转至指定文件夹路径
        ftp.cwd(ftpfoldpath)
    except(socket.error, socket.gaierror):  # ftp 连接错误
        print("ERROR: cannot connect [{}:{}]".format(host, port))
        return None
    except error_perm:  # 用户登录认证错误
        print("ERROR: user Authentication failed ")
        return None
    
    return ftp

##----------------------------------------------------------------------##
# INFO: 判断文件在ftp中是否存在
##----------------------------------------------------------------------##
# Inputs:
#   ftp_conn        - ftp
#   filename        - 需判断的文件名
# Outputs:
#   flag            - bool值 True/False 存在/不存在
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21,23; 07/11
##----------------------------------------------------------------------##
def is_ftp_file(ftp_conn, filename):
    try:
        if filename in ftp_conn.nlst(os.path.dirname(filename)):
            return True
        else:
            return False
    except error_perm:
        return False

##----------------------------------------------------------------------##
# INFO: 下载ftp文件
##----------------------------------------------------------------------##
# Inputs:
#   ftp             - ftp
#   filename        - 需下载的文件名
#   savefilepath    - 本地保存文件名
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/07/11
##----------------------------------------------------------------------##
def ftp_savefile(ftp,filename,savefilepath):
    # FTP: 文件名是否存在
    if is_ftp_file(ftp,filename):
        # 下载指定文件到指定文件
        with open(savefilepath,'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write, 1024)
    else:
        print('FTP文件不存在: ' + filename)

##----------------------------------------------------------------------##
# INFO: 获取指定匹配规则的ftp文件名列表
##----------------------------------------------------------------------##
# Inputs:
#   ftp             - ftp
#   regular_rules   - 需下载文件名的匹配规则
# Outputs:
#   filenames       - 满足匹配规则的文件名列表
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/07/11
##----------------------------------------------------------------------##
def ftp_getfiles(ftp,regular_rules):
    # 获取满足规则的所有文件信息
    ftp_files = []
    ftp.dir(regular_rules,ftp_files.append)

    # 拆分字符串以提取文件名
    filenames = []
    for each in ftp_files:
        filenames.append(each.split()[-1])
    
    return filenames

##----------------------------------------------------------------------##
# INFO: 下载ftp文件
##----------------------------------------------------------------------##
# Inputs:
#   ftp             - ftp
#   regular_rules   - 需下载文件名的匹配规则
#   symd            - 开始日期 yyyymmdd
#   eymd            - 结束日期 yyyymmdd
#   foldpath        - 保存文件夹路径
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/07/11
##----------------------------------------------------------------------##
def download_files(ftp,regular_rules,symd,eymd,foldpath):
    # 获取满足条件的ftp文件名列表
    filenames = ftp_getfiles(ftp,regular_rules)
    
    # 循环下载列表中的ftp文件
    for i in range(len(filenames)):
        # 当前文件日期 yyyymmdd
        nymd = int(filenames[i][0:8])
        # 小于开始日期时重新循环
        if nymd<symd:
            continue
        # 大于结束日期时终止循环
        if nymd>eymd:
            break

        # 当前文件年 yyyy
        yyyy = filenames[i][0:4]
        # 当前文件月 mm
        mm = filenames[i][4:6]
        # 保存文件夹路径 yyyy/mm
        savefoldpath = os.path.join(foldpath,'{:s}/{:s}'.format(yyyy,mm))
        if not os.path.exists(savefoldpath):
            os.makedirs(savefoldpath)
        
        # 保存文件路径 yyyy/mm/filename
        savefilepath = os.path.join(savefoldpath,filenames[i])

        # 下载文件
        print("正在下载: " + filenames[i])
        ftp_savefile(ftp,filenames[i],savefilepath)
    
    # 断开服务器链接
    ftp.quit()

##----------------------------------------------------------------------##
if __name__=='__main__':
    # 根目录
    rootpath = '/Volumes/Washy1T/SpacePhysicsData/ACE'
    # 数据模式 swepam_1m mag_1m
    datamode = 'mag_1m'
    # 文件名匹配规则
    regular_rules = '*_ace_{:s}.txt'.format(datamode)
    # 开始日期
    symd = 20180101
    # 结束日期
    eymd = 20190101

    # 文件夹路径
    foldpath = os.path.join(rootpath,datamode)
    if not os.path.exists(foldpath):
        os.makedirs(foldpath)
    # 主机名
    host = 'ftp.swpc.noaa.gov'
    # 端口号
    port = 21
    # 文件夹路径
    ftpfoldpath = '/pub/lists/ace'
    # 连接ftp服务器
    ftp = ftp_connect(host,port,ftpfoldpath)
    # 下载文件
    download_files(ftp,regular_rules,symd,eymd,foldpath)
