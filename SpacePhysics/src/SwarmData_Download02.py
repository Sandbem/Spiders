# coding: utf-8
# INFO: Swarm数据下载
# date: 2022-01-03 Washy [CUG washy21@163.com]

import os
import re
import requests

import urllib3
urllib3.disable_warnings()

# 获取单个数据文件
def download_data(url):
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }

    res = requests.get(url, headers=headers, verify=False)
    
    return res

# 获取所有数据文件名
def getnames(url,sat):
    res = download_data(url)
    html = res.text
    
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
        
        res = download_data(fileurl)
        
        with open(filename,"wb") as f:
            f.write(res.content)

if __name__ == "__main__":
    # 卫星 A B C
    sat = "B"
    # 开始文件
    sNum = 0
    # 总文件数
    tNum = 1
    
    # 保存路径
    savepath = "./Swarm/satB/"
    
    main(sat,sNum,tNum,savepath)
    
