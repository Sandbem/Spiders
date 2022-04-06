# Space Physics Spiders

Washy 2022-03-24

## 简介

- 功能：从国内外已有的公开数据网站爬取所需的数据。

## 更新内容

- `2022-03-31` 增加Gim Map数据爬虫。

- `2022-03-24` 首次提交。能够爬取Swarm卫星数据、Dst指数、太阳黑子数。

## Swarm卫星数据

- 文件名：`SwarmData_Download.py`

## Dst指数

- 文件名：`spider_Dst.py`
- 数据网站：`http://wdc.kugi.kyoto-u.ac.jp/wdc/Sec3.html`
- 更新速度：1小时更新一次数据
- 存储路径：`./Dst/20xxxx.txt` 示例 `./SpaceWeather/Dst/202203.txt`
- 函数功能：

  - `get_Dst_month(year,month)` 获取指定年月的原始Dst数据，返回`data`
  - `save_Dst(filepath,data)` 将`data`存储至`filepath`处，无返回值
  - `download_Dst_all(rootpath)` 下载所有的Dst数据，并存储至`rootpath`

## 太阳黑子数

- 文件名：`spider_SunspotNumber.py`
- 数据网站：`ftp://ftp.swpc.noaa.gov/pub/indices/old_indices` 
- 更新速度：1天更新一次数据
- 存储路径：`./SunspotNumber/20xxxx.txt` 示例`./SpaceWeather/SunspotNumber/202203.txt`

## Gim Map

- 文件名：`spider_GimMap.py`
- 数据网站：`ftp://ftp.gipp.org.cn/product/ionex`
- 存储路径：`./GimMap/20xx/xxx/.Z` 示例`./GimMap/2022/089/usrg0890.22i.Z`