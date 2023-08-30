---
title: "pillow安装出错的解决办法"
description: "pillow安装出错的解决办法"
date: 2018-07-18T23:08:56+08:00
categories:
  - 折腾
tags:
  - Linux
  - Python
---

最近想尝试一下使用face_recognition进行人脸识别，需要使用pillow包，但是在安装时出现了一大长串错误。百度不到适合我的解决方法，于是上pillow官网看了下[安装指南](https://pillow.readthedocs.io/en/latest/installation.html#building-on-linux "安装指南")，原因和解决办法记录如下：
我看到这句：

> Zlib and libjpeg are required by default.

检查了一下我的系统后，发现缺少了`zlib`库。所以运行下面的命令进行安装。（命令里面包含了其它的包，我不知道是不是必须了，我都顺便安装了。我用python3，如果使用python2，需要修改一下包名。）

```python
apt-get install python3-dev python3-setuptools libtiff5-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev  tcl8.6-dev tk8.6-dev python3-tk
```

然后重新安装pillow：

```python
pip3 install pillow
```

安装成功，没有报错。