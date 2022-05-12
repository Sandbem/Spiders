''' coding: utf-8
INFO: 爬取ftp://ftp.gipp.org.cn/product/ionex下Gim Map (uqrg*i.Z)数据.
date: 2022-03-31 Washy [CUG washy21@163.com]
'''

import os
import glob
import unlzw3
import socket
import pathlib
import datetime

import numpy as np

from ftplib import FTP
from ftplib import error_perm
from scipy.interpolate import griddata

##----------------------------------------------------------------------##
# INFO: ftp网站连接
##----------------------------------------------------------------------##
# Outputs:
#   ftp         - ftp根目录
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/21,23,31
##----------------------------------------------------------------------##
def ftp_connect():
    # FTP站点
    host = 'ftp.gipp.org.cn'
    # 端口号
    port = 21
    # 文件夹路径
    # foldpath = '/product/ionex'
 
    ftp = FTP()
    ftp.encoding = 'utf-8'
    
    try:
        ftp.connect(host, port)
        ftp.login()
        # ftp.cwd(foldpath)
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
# INFO: 下载指定FTP文件
##----------------------------------------------------------------------##
# Inputs:
#   ftp         - ftp
#   rootpath    - 根目录
#   iy          - 年份
#   iday        - Day of Year
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/31
##----------------------------------------------------------------------##
def download_uqrg(ftp, rootpath, iy, iday):
    # 文件夹路径
    foldpath = '/product/ionex/{:d}/{:03d}'.format(iy,iday)
    # 文件名
    filename = 'uqrg{:03d}0.{:02d}i.Z'.format(iday,iy%100)
    # 保存文件夹路径
    savefoldpath = os.path.join(rootpath, \
        'TEMP/Z/{:d}/{:03d}'.format(iy,iday))
    # 保存文件绝对路径
    savepath = os.path.join(savefoldpath,filename)

    # 判断是否存在
    if os.path.exists(savepath):
        return

    # ftp跳转路径
    try:
        ftp.cwd(foldpath)
    except:
        print('文件夹' + foldpath + '不存在!')
    
    # FTP: 文件名是否存在
    if is_ftp_file(ftp, filename):
        print('正在下载{:d}第{:03d}天数据'.format(iy,iday))
        
        # 创建文件夹
        if not os.path.exists(savefoldpath):
            os.makedirs(savefoldpath)
        
        # 下载指定文件到临时文件
        with open(savepath, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write, 1024)
    else:
        print('文件' + filename + '不存在!')

##----------------------------------------------------------------------##
# INFO: 解压Z文件
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 根目录
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/05/07
##----------------------------------------------------------------------##
def unpack_Z(rootpath,iy,iday):
    # 保存文件夹路径
    foldpath = os.path.join(rootpath, \
        'TEMP/Z/{:d}/{:03d}'.format(iy,iday))
    # 文件名
    filename = 'uqrg{:03d}0.{:02d}i'.format(iday,iy%100)
    zfilename = 'uqrg{:03d}0.{:02d}i.Z'.format(iday,iy%100)
    # 保存文件绝对路径
    filepath = os.path.join(foldpath,filename)
    zfilepath = os.path.join(foldpath,zfilename)
    
    if not os.path.exists(zfilepath):
        return
    
    # 判断是否存在
    if not os.path.exists(filepath):
        data = unlzw3.unlzw(pathlib.Path(zfilepath))
        
        with open(filepath,'wb') as f:
            f.write(data)

##----------------------------------------------------------------------##
# INFO: 下载2021年至今所有的ursg*i.Z文件
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 根目录
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/31
##----------------------------------------------------------------------##
def download_uqrg_all(rootpath):
    # 连接服务器
    ftp = ftp_connect()

    # 获取当前世界时
    utc = datetime.datetime.utcnow()

    # 倒叙 year
    for iy in range(utc.year,2020,-1):
        if iy == utc.year:
            sday = (utc-datetime.datetime(utc.year,1,1)).days + 1
            eday = 0
        elif iy == 2021:
            sday = 365
            eday = 273
        else:
            sday = 365
            eday = 0
        
        # 倒叙 DoY
        for iday in range(sday,eday,-1):
            # 下载文件
            download_uqrg(ftp,rootpath,iy,iday)
            # 解压文件
            unpack_Z(rootpath,iy,iday)

    # 断开服务器
    ftp.quit()

##----------------------------------------------------------------------##
# INFO: 重新存储指定年指定天的TEC数据
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 根目录
#   iy          - 年份
#   iday        - Day of Year
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/31，04/01,19
##----------------------------------------------------------------------##
def resave_TEC(rootpath, iy, iday):
    # 文件夹路径
    zfoldpath = os.path.join(rootpath, \
        'TEMP/Z/{:d}/{:03d}'.format(iy,iday))
    # 文件名
    zfilename = 'uqrg{:03d}0.{:02d}i.Z'.format(iday,iy%100)
    # 压缩文件绝对路径
    zfilepath = os.path.join(zfoldpath,zfilename)
    # 判断压缩文件是否存在
    if not os.path.exists(zfilepath):
        print("无数据")
        return

    # 当前日期
    date = datetime.datetime(iy,1,1) + datetime.timedelta(days=iday-1)

    # 保存文件夹路径
    savefoldpath = os.path.join(rootpath, \
        'TEC/{:d}/{:02d}/{:02d}'.format(iy,date.month,date.day))
    
    # HMS
    hms = ['0000', '0015', '0030', '0045', '0100', '0115', '0130', '0145', 
        '0200', '0215', '0230', '0245', '0300', '0315', '0330', '0345', 
        '0400', '0415', '0430', '0445', '0500', '0515', '0530', '0545', 
        '0600', '0615', '0630', '0645', '0700', '0715', '0730', '0745', 
        '0800', '0815', '0830', '0845', '0900', '0915', '0930', '0945', 
        '1000', '1015', '1030', '1045', '1100', '1115', '1130', '1145', 
        '1200', '1215', '1230', '1245', '1300', '1315', '1330', '1345', 
        '1400', '1415', '1430', '1445', '1500', '1515', '1530', '1545', 
        '1600', '1615', '1630', '1645', '1700', '1715', '1730', '1745', 
        '1800', '1815', '1830', '1845', '1900', '1915', '1930', '1945', 
        '2000', '2015', '2030', '2045', '2100', '2115', '2130', '2145', 
        '2200', '2215', '2230', '2245', '2300', '2315', '2330', '2345']
    # 保存文件名
    savepaths = [savefoldpath + \
        '/Ass{:d}{:02d}{:02d}'.format(iy,date.month,date.day) \
        + hms[i] + '00TEC.txt' for i in range(96)]
    
    # 已有的文件名
    filepaths = glob.glob(os.path.join(savefoldpath,'*.txt'))
    # 所有文件已存在则终止
    if set(savepaths)<=set(filepaths):
        print("数据文件已存在")
        return
    
    # 创建文件夹
    if not os.path.exists(savefoldpath):
        os.makedirs(savefoldpath)

    # 读取压缩文件数据
    data = unlzw3.unlzw(pathlib.Path(zfilepath)).decode().splitlines()

    # 海拔高度
    HGT = data[20][2:8]
    # 纬度
    LAT1 = float(data[21][2:8])
    LAT2 = float(data[21][8:14])
    DLAT = float(data[21][14:20])
    LATs = [LAT1+DLAT*i for i in range(int((LAT2-LAT1)/DLAT)+1)]
    numLat = len(LATs)
    # 经度
    LON1 = float(data[22][2:8])
    LON2 = float(data[22][8:14])
    DLON = float(data[22][14:20])
    LONs = [LON1+DLON*i for i in range(int((LON2-LON1)/DLON)+1)]
    numLon = len(LONs)

    plons1,plats1 = np.meshgrid(LONs,LATs)
    plons2,plats2 = np.meshgrid(np.arange(70,136),np.arange(10,56))
    
    # 每个纬度对应的数据行数
    rows_lat = int((numLon-1)/16) + 1
    # 每个文件的数据行数
    rows_file = numLat*(rows_lat+1) + 3
    # 文件头描述信息行数
    for idx in range(len(data)):
        if "END OF HEADER" in data[idx]:
            idx0 = idx + 1

    # 遍历文件名
    for ifile in range(96):#96
        # 
        npdata1 = np.zeros([numLat,numLon])
        # 本文件数据范围
        data1 = data[rows_file*ifile+idx0+2:rows_file*(ifile+1)+idx0-1]
        # 遍历纬度
        for ilat in range(numLat):#numLat
            # 本纬度的数据范围
            data2 = ''.join(
                data1[(rows_lat+1)*ilat+1:(rows_lat+1)*(ilat+1)]
            ).split()
            # 遍历经度
            npdata1[ilat,:] = data2

        # 数据插值
        npdata2 = griddata((plons1.flatten(),plats1.flatten()),npdata1.flatten(),
            (plons2,plats2),method='cubic')
        
        fplons2 = plons2.T.flatten()
        fplats2 = plats2.T.flatten()
        fpdata2 = npdata2.T.flatten()

        # 存储数据
        f = open(savepaths[ifile], 'w')
        f.write("# Date: {:d}-{:02d}-{:02d} {}:{}:00\n".format(
            iy,date.month,date.day,hms[ifile][0:2],hms[ifile][2:4]
        ))
        f.write("# Ionospheric TEC Parameter\n")
        f.write("# TEC values in 0.1 TECUs; {}km\n".format(HGT))
        f.write("#----------------------------------------\n")
        f.write("  Long    Lat    TEC\n")

        for idx in range(len(fpdata2)):
            f.write("{:6.1f} {:6.1f} {:6.1f}\n".format(
                fplons2[idx],fplats2[idx],fpdata2[idx]
            ))

        f.close()
    
    # 打印提示
    print("存储完成")

##----------------------------------------------------------------------##
# INFO: 重新存储2021年至今的TEC数据至txt文件
##----------------------------------------------------------------------##
# Inputs:
#   rootpath    - 根目录
##----------------------------------------------------------------------##
# author: Washy [CUG washy21@163.com]
# date: 2022/03/31，04/01
##----------------------------------------------------------------------##
def resave_TEC_all(rootpath):
    # 
    print("下载完成, 提取TEC数据.")

    # 获取当前世界时
    utc = datetime.datetime.utcnow()

    # 倒叙 year
    for iy in range(utc.year,2020,-1):
        if iy == utc.year:
            sday = (utc-datetime.datetime(utc.year,1,1)).days + 1
            eday = 0
        elif iy == 2021:
            sday = 365
            eday = 273
        else:
            sday = 365
            eday = 0
        
        # 倒叙 DoY
        for iday in range(sday,eday,-1):
            try:
                print("正在存储{:d}年第{:03d}天数据".format(iy,iday))
                resave_TEC(rootpath,iy,iday)
            except:
                print("ERROR: {:d}年第{:03d}天数据存储失败".format(iy,iday))

##----------------------------------------------------------------------##
if __name__ == '__main__':
    # 存储根目录
    rootpath = '/Volumes/Washy5T/SpaceWeather/GimMap'
    # 下载2021年至今的数据
    download_uqrg_all(rootpath)
    resave_TEC_all(rootpath)
    




