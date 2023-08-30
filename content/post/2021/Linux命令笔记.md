---
title: "Linux命令笔记"
description: "Linux命令笔记"
date: 2021-02-15T04:20:00+08:00
lastmod: 2023-08-29T00:00:00+10:00
categories:
  - 学习
tags:
  - Linux
---

## Linux命令笔记

### 查看系统当前使用systemd还是sysvinit

```bash
dpkg -l systemd-sysv
dpkg -l sysvinit-core
```

### ipmitool修改带外管理ip

```bash
ipmitool lan print 1

ipmitool lan set 1 ipsrc static
ipmitool lan set 1 ipaddr $ipmi_ipaddr
ipmitool lan set 1 netmask $ipmi_netmask
ipmitool lan set 1 defgw ipaddr $ipmi_gateway
```

### 暂停和恢复进程

处于暂停(TASK_STOPPED)状态的进程，依然处于可运行队列，但调度器不会选择它来执行。

```bash
kill -STOP $PID
kill -CONT $PID
```

### apt update expired 报错

```bash
apt-get -o Acquire::Check-Valid-Until=false update
```

### MTU测试

```
ping -c 3 -s 1472 -M do 114.114.114.114
```

> vxlan mtu = 1450 = 1500 – 20(ip头) – 8(udp头) – 8(vxlan头) – 14(以太网头) 【cost: 50】 
> gre mtu = 1462 = 1500 – 20(ip头) – 4(gre头) – 14(以太网头)【cost: 38】 
> Wireguard = 1420【cost: 80】

### 吃满内存

```bash
tail /dev/zero
```

### sed去除彩色

```bash
sed -r 's/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g'
```

### debian apt update 缺少key

提示：
```bash
W: There is no public key available for the following key IDs:
112695A0E562B32A
```

添加key：
```bash
apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 112695A0E562B32A
```

### 杀进程

```
ps -ef |grep 'lxc exec' |grep -v grep |awk '{print $2}'|xargs kill -9
```

### 挂载loop设备

```
losetup -f
losetup /dev/loop0 Armbian_22.08.2_Orangepipc_jammy_current_5.15.69.img
```

查看分区偏移：

```
fdisk -l /dev/loop0
Disk /dev/loop0: 1.3 GiB, 1392508928 bytes, 2719744 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x60145ae2

Device       Boot Start     End Sectors  Size Id Type
/dev/loop0p1       8192 2719743 2711552  1.3G 83 Linux
```

计算偏移后挂载

```
mount -o loop,offset=$((8192*512)) /dev/loop0 /mnt
```

### 修改时区

```
timedatectl set-timezone Asia/Shanghai
```

### git添加多个remote

```
git remote add origin-github git@github.com:chn-lee-yumi/FileManager.git
git push -u origin main && git push -u origin-github main
```

### ffplay播放rtsp视频流

```
ffplay -rtsp_transport tcp -i rtsp://username:password@10.0.0.10/Streaming/Channels/301
```

### iperf3测速

```
iperf3 -s
iperf3 -c x.x.x.x
```
