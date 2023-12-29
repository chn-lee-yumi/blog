---
title: "构建Python的Windows整合包教程"
description: "构建Python的Windows整合包教程"
date: 2023-12-18T19:06:00+11:00
categories:
  - 折腾
tags:
  - Windows
  - Python
---

## 前言

之前的开源项目[本地素材搜索](https://github.com/chn-lee-yumi/MaterialSearch)有很多人想要Windows整合包，因为Windows下配置环境太过麻烦，很多小白都不会安装。所以我尝试了一下做一个整合包。

## 步骤

1. 新建一个文件夹`MaterialSearchWindows`
2. 下载[项目代码](https://github.com/chn-lee-yumi/MaterialSearch/archive/refs/tags/v0.0.0-20231218.zip)并解压，将代码复制到`MaterialSearchWindows/MaterialSearch`目录下。
3. 下载python。因为pytorch在Windows下支持的最高版本为Python3.10，所以只能下载Python3.10的包。直接下载[Windows installer (64-bit)](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)并以用户权限安装到指定文件夹，这里直接安装到`MaterialSearch`。
4. 用pip安装依赖，如`.\python -m pip install -r .\MaterialSearch\requirements.txt --index-url=https://download.pytorch.org/whl/cu118 --extra-index-url=https://pypi.org/simple/`
5. 新建一个`运行.bat`，内容如下。然后执行`运行.bat`，等待模型下载完毕。
    ```powershell
    SET TRANSFORMERS_CACHE=..\huggingface
    cd MaterialSearch
    ..\python main.py
    ```
6. 然后修改`运行.bat`为如下内容：
    ```powershell
    :: 下面配置扫描路径，多个路径之间用逗号分隔
    SET ASSETS_PATH=C:/Users/Administrator/Pictures,C:/Users/Administrator/Videos
    :: 下面配置设备，cpu或cuda
    SET DEVICE=cpu
    SET DEVICE_TEXT=cpu
    :: 下面的不要改
    SET PATH=%PATH%;..\
    SET TRANSFORMERS_OFFLINE=1
    SET TRANSFORMERS_CACHE=..\huggingface
    cd MaterialSearch
    ..\python main.py
    ```
7. 下载[FFMpeg](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z)，解压后将`ffmpeg.exe`复制到`MaterialSearchWindows`目录。
8. 最后所有文件夹一起打包压缩。后续执行程序，执行`运行.bat`即可。

目录结构如下：

```text
MaterialSearch
 |
 |- 运行.bat (前面自己创建的脚本)
 |- MaterialSearch (代码目录)
     |
     |- main.py
     |- .env
     |- ... (其它代码文件)
 |- python.exe
 |- huggingface (huggingface模型存放目录)
 |- ... (Python相关文件)
```