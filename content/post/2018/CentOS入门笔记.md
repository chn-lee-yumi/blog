---
title: "CentOS入门笔记"
description: "CentOS入门笔记，基本命令"
date: 2018-08-08T18:41:50+08:00
categories:
  - 学习
tags:
  - Linux
---

## RPM

### 查询

- `rpm -q 软件名称` 查询已安装的软件的包名
- `rpm -qa` 查询所有已安装的RPM包
- `rpm -qf 文件路径` 查询文件所在的包名
- `rpm -ql 软件名称` 查询软件的RPM包中文件的安装路径（如`rpm -ql wireshark| grep bin` 查找wireshark安装的可执行文件的路径）
- `rpm -qi 软件名称` 查询已安装的软件包的信息
- `rpm -qpi RPM包路径` 查询（未安装的）RPM包的信息

### 安装

- `rpm -i RPM包路径` 安装RPM包
- `-i` install，安装
- `-v` verbose，显示安装过程的详细信息
- `-h` hash，用`#`显示进度条（100%为20个`#`）
- `rpm -ivh RPM包路径` 安装RPM包，显示详细信息，显示进度条

### 升级

- `rpm -U RPM包路径` 升级
- `rpm -Uvh RPM包路径` 升级，显示详细信息，显示进度条

### 卸载

- `rpm -e 软件名称` 卸载软件

## YUM

### 查询

- `yum list installed` 列出安装的软件
- `yum list all` 列出所有软件
- `yum list 软件名称` 列出软件
- `yum info 软件名称` 查询软件信息
- `yum grouplist` 列出包组
- `yum groupinfo 包组名称` 查询包组信息

### 安装

- `yum install 软件名称` 安装软件
- `yum -y install 软件名称` 安装软件，所有选项默认yes
- `yum groupinstall 包组名称` 安装包组

### 升级

- `yum update 软件名称` 升级软件
- `yum groupupdate 包组名称` 升级包组

### 卸载

- `yum remove 软件名称` 卸载软件
- `yum groupremove 包组名称` 卸载包组
