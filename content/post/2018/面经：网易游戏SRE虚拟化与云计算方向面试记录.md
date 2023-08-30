---
title: "面经：网易游戏SRE虚拟化与云计算方向面试记录"
description: "面经：网易游戏SRE虚拟化与云计算方向面试记录"
date: 2018-11-07T14:51:00+08:00
categories:
  - 学习
tags:
  - 面试
---

## 网易游戏SRE虚拟化与云计算方向面试记录

发个面试记录造福后人。牛客的网易游戏SRE面经好像没有。总的来说面试内容都是和其它公司差不多的。

一面的问题记录如下。二面忘了，没有记录。只有两面，没有HR面。

### python深浅拷贝？

浅拷贝就是只复制拷贝对象，深拷贝会迭代复制拷贝对象里面引用到的对象。例如一个字典，浅拷贝后修改其中一个字典的key对应的value，另一个字典也会一起改变。深拷贝就不是。

### 进程间的通信有哪几种方式？

管道、消息队列、信号、共享内存、信号量、套接字

### 什么是回调函数？

把函数作为参数传给另一个函数，另一个函数可以在适当的时候调用。

### 有了解过虚拟化那块的东西吗？

### 容器有接触过吗？

### 容器基于内核的哪项技术呢？

Cgroup+Namespace

### top命令用得多吗？平均负载的三个值是什么?

### find命令是通过什么查找文件的吗？

不知道，可能是通过目录项

### 一个文件的属性存在哪里？（修改时间之类的）

inode。储存文件元信息的区域就叫做inode，中文译名为"索引节点"。每一个文件都有对应的inode，里面包含了与该文件有关的一些信息。

```
inode包含文件的元信息，具体来说有以下内容：
文件的字节数
文件拥有者的User ID
文件的Group ID
文件的读、写、执行权限
文件的时间戳，共有三个：ctime指inode上一次变动的时间，mtime指文件内容上一次变动的时间，atime指文件上一次打开的时间。
链接数，即有多少文件名指向这个inode
文件数据block的位置
可以用stat命令，查看某个文件的inode信息：
stat example.txt
```

### 文件的文件名存在哪里的？

目录块（目录文件里面）

### linux有没有看过成体系的书籍？

### TCP四次挥手的过程？

### TCP流的MSS协商是在哪个阶段完成的？

三次握手，SYN包会携带MSS的值。

### TIME_WAIT这个阶段了解吗？

### TIME_WAIT持续多长？你知道这个值跟什么有关吗？

### VLAN ID，最大是多少？为什么最大能配的是4094？

### 在shell脚本中判断一个文件是否存在？

```shell
#!/bin/sh
myFile="/root/apue/example.xml"
if [ ! -f "$myFile" ]; then
    cp  ./example.xml  /root/apue/
fi
```

附shell中常用的其它判断形式：
```shell
-a file exists. 
-b file exists and is a block special file. 
-c file exists and is a character special file. 
-d file exists and is a directory. 
-e file exists (just the same as -a). 
-f file exists and is a regular file. 
-g file exists and has its setgid(2) bit set. 
-G file exists and has the same group ID as this process. 
-k file exists and has its sticky bit set. 
-L file exists and is a symbolic link. 
-n string length is not zero. 
-o Named option is set on. 
-O file exists and is owned by the user ID of this process. 
-p file exists and is a first in, first out (FIFO) special file or 
named pipe. 
-r file exists and is readable by the current process. 
-s file exists and has a size greater than zero. 
-S file exists and is a socket. 
-t file descriptor number fildes is open and associated with a 
terminal device. 
-u file exists and has its setuid(2) bit set. 
-w file exists and is writable by the current process. 
-x file exists and is executable by the current process. 
-z string length is zero. 
```

### 运维和开发你更喜欢哪个？为什么？

### 你这边有什么想要了解的吗？

问了一下日常工作和虚拟化环境，回答说虚拟化用Openstack，存储用Ceph，SDN是自研的。
