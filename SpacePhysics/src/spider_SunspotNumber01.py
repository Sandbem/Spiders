''' coding: utf-8
INFO: 爬取ftp://ftp.swpc.noaa.gov/pub/indices/old_indices下Sunspot Number.
date: 2022-03-21 Washy [CUG washy21@163.com]
'''

import os
import time
import socket
import datetime

from ftplib import FTP
from ftplib import error_perm

##----------------------------------------------------------------------##
# INFO: ftp网站连接
##----------------------------------------------------------------------##
# Inputs:
#   host        - ftp站点地址
#   port        - 端口号 默认为21
#   username    - 用户名 默认为空
#   password    - 用户密码 默认为空
# Outputs:
#   ftp         - ftp根目录
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21
##----------------------------------------------------------------------##
def ftp_connect(host, port=21, username='', password=''):
    ftp = FTP()
    ftp.encoding = 'utf-8'
    try:
        ftp.connect(host, port)  # 连接
        ftp.login(username, password)  # 登录，如果匿名登录则用空串代替即可
        # print('ftp服务器 ' + host + ' 连接成功') 
    except(socket.error, socket.gaierror):  # ftp 连接错误
        print("ERROR: cannot connect [{}:{}]" .format(host, port))
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
# INFO: 爬取 ftp.swpc.noaa.gov/pub/indices/old_indices 下最新的DSD数据
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 本地文件保存根目录
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21
##----------------------------------------------------------------------##
def download_sn(rootpath, savename, date):
    # 创建文件夹
    if not os.path.exists(rootpath):
        os.makedirs(rootpath)
    
    # ftp站点
    host = 'ftp.swpc.noaa.gov'
    # ftp文件夹路径
    folderpath = '/pub/indices/old_indices'
    
    # 实时更新文件的绝对路径
    savepath = os.path.join(rootpath, savename)
    
    # 获取当前世界时
    # date = datetime.datetime.utcnow()
    # 根据月份生成文件名
    filename = '{:d}Q{:d}_DSD.txt'.format(date[0],(date[1]-1)//3+1)

    ftp = ftp_connect(host)
    ftp.cwd(folderpath)
    if is_ftp_file(ftp, filename):
        # print('更新数据中: ', end='')
        with open(savepath, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write, 1024)
        # print('更新成功')
    else:
        print('文件不存在: ' + filename)
    
    ftp.quit()
    # print('ftp服务器 ' + host + ' 断开连接')

##----------------------------------------------------------------------##
# INFO: 对从ftp下载的数据文件进行重新存储
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 根目录
#   filepath    - 需要重新存储的原始数据文件绝对路径
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21
##----------------------------------------------------------------------##
def resave_sn(rootpath, filepath):
    # 打开数据文件
    with open(filepath, 'r') as f:
        data = f.read()
    # 去除表头
    str_list = data[638:].split()
    
    # 数据长度
    lendata = len(str_list)
    # 提取 年 月 日 黑子数
    years = str_list[0:lendata:16]
    months = str_list[1:lendata:16]
    days = str_list[2:lendata:16]
    sns = str_list[4:lendata:16]

    # 遍历所有的月份
    for each in sorted(list(set(months))):
        # 每个月份数据的起始索引
        idxm = months.index(each)
        
        # 判断是否为当前月
        if int(months[idxm]) == datetime.datetime.utcnow().month:
            folderpath = rootpath
            savename = 'presentmonth.txt'
        else:
            folderpath = os.path.join(rootpath,years[idxm])
            savename = years[idxm] + months[idxm] + '.txt'
        # 生成文件夹路径
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)
        # 生成文件名绝对路径
        savepath = os.path.join(folderpath, savename)
        # 文件已存在则开始下一循环
        if os.path.exists(savepath) and savename!='presentmonth.txt':
            continue
        
        # 另存文件
        with open(savepath, 'w') as f:
            # 生成表头
            f.write('YYYY  MM  DD  SunspotNumber\n')
            # 循环所有数据
            for idx in range(idxm,len(months)):
                # 月份不同时跳出循环
                if months[idx] != months[idxm]:
                    break
                # 存入当前月份数据
                f.write('%4s  %2s  %2s  %4s\n' % \
                    (years[idx], months[idx], days[idx], sns[idx]))

##----------------------------------------------------------------------##
# INFO: 判断上季度最后一个月数据是否存在
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 根目录
#   date        - 当前日期 [year, month]
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/22
##----------------------------------------------------------------------##
def exist_lastquarter_sn(rootpath, date):
    # 上季度的日期
    lastdate = [date[0], date[1]-3]
    # 判断是否跨年
    if lastdate[1] <= 0:
        lastdate = [date[0]-1, 12]
    else:
        # 上季度最后一个月
        lastdate[1] = 3*((lastdate[1]-1)//3+1)
    # 上季度最后一个月数据文件名
    lastsavename = '{:d}{:02d}.txt'.format(lastdate[0],lastdate[1])
    # 上季度最后一个月数据绝对路径 '%d'%lastdate[0]
    lastsavepath = os.path.join(rootpath, '%d' % lastdate[0], lastsavename)
    
    # 判断上季度最后一个月数据文件是否存在
    if os.path.exists(lastsavepath):
        return [True, lastdate] 
    else:
        return [False, lastdate]

##----------------------------------------------------------------------##
# INFO: 循环爬取数据并存储太阳黑子数数据
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 根目录
#   dt          - 每次更新间隔小时数
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21
##----------------------------------------------------------------------##
def update_sn(rootpath, dt=24):
    # 更新计数
    idx = 1
    while True:
        # 获取当前世界时
        date = datetime.datetime.utcnow()
        # 上季度最后一个月数据文件是否存在
        flag, lastdate = exist_lastquarter_sn(rootpath, \
            [date.year, date.month])
        try:
            # 判断是否需要更新上季度数据
            if not flag:
                print('更新上季度数据 (本月仅更新一次): ', end='')
                # 爬取上季度数据
                download_sn(rootpath, 'last_raw.txt', lastdate)
                # 重新存储上季度数据
                resave_sn(rootpath, os.path.join(rootpath,'last_raw.txt'))
                print('更新成功')
            
            # 打印提示信息
            print("第{:03d}次更新: ".format(idx), end='')
            # 实时更新数据
            download_sn(rootpath, 'present_raw.txt', \
                [date.year, date.month])
            # 重新存储实时更新的数据
            resave_sn(rootpath, os.path.join(rootpath,'present_raw.txt'))
            # 打印提示信息
            print('更新成功 ({:.1f}小时后进行下次更新)'.format(dt))
        except Exception as e:
            print('ERROR: ', e)
        finally:
            idx += 1
            time.sleep(3600*dt)

##----------------------------------------------------------------------##
if __name__ == '__main__':
    # 存储根目录
    rootpath = '/Volumes/Washy5T/SpaceWeather/SunspotNumber'
    # 循环更新数据 24: 每次更新的间隔小时数
    update_sn(rootpath, 24)
    # flag,lastdate = exist_lastquarter_sn(rootpath, [2022,3])
    # print(flag,lastdate)
