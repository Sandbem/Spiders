# coding: utf-8
# INFO: Swarm数据下载
# date: 2021-05-23 Washy [IGG]

import os
import re
import ssl
import urllib.request as ur

# 获取单个数据文件
def down_data(url):
    req = ur.Request(url)

    req.add_header("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")
    
    res = ur.urlopen(req).read()
    
    return res

# 获取所有数据文件名
def getnames(url,sat):
    res = down_data(url)
    html = str(res,encoding="utf-8")
    
    r_name = '"SW_OPER_EFI{}_LP_1B_\d+T\d+_\d+T\d+_05\d+.CDF.ZIP"'.format(sat)
    names = re.findall(r_name,html)
    
    return names

# 主函数
def main(sat,sNum,tNum,savepath):
    # 创建数据目录
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    
    # 起始链接
    url = "https://swarm-diss.eo.esa.int/?do=list&maxfiles="+ str(tNum) + \
        "&pos="+ str(sNum) + \
        "&file=swarm%2FLevel1b%2FLatest_baselines%2FEFIx_LP%2FSat_" + sat
    
    names = getnames(url,sat)
    
    print("总文件个数: {}".format(len(names)))
    
    for each in names:
        name = each[1:-1]
        
        filename = savepath + name
        
        if os.path.exists(filename):
            print("文件已存在: {}".format(name))
            continue
        
        print("正在下载: {}".format(name))
        
        fileurl = "https://swarm-diss.eo.esa.int/?do=download&file=swarm%2"+\
            "FLevel1b%2FLatest_baselines%2FEFIx_LP%2FSat_{}%2F".format(sat)+\
            name
        
        file = down_data(fileurl)
        
        with open(filename,"wb") as f:
            f.write(file)

if __name__ == "__main__":

    ssl._create_default_https_context = ssl._create_unverified_context

    # 卫星 A B C
    sat = "B"
    # 开始文件
    sNum = 0
    # 总文件数
    tNum = 5000
    
    # 保存路径
    savepath = "/Volumes/Backup Plus/Swarm/satB/"
    
    main(sat,sNum,tNum,savepath)
    
