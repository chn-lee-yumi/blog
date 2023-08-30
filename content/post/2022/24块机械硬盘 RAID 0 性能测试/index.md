---
title: "24块机械硬盘 RAID 0 性能测试"
description: "24块机械硬盘 RAID 0 性能测试"
date: 2022-02-07T01:15:00+08:00
categories:
  - 折腾
tags:
  - 硬件
  - B站视频
  - RAID
---

## 测试环境

服务器型号是戴尔的 R730xd，RAID 卡是 PERC H330 Mini，上面插了 24 块 1.2T 的 2.5 寸企业级 SAS 机械硬盘。

测试工具为fio。

## 单盘性能测试

4K随机写：343 IOPS

![单盘随机写.png](%E5%8D%95%E7%9B%98%E9%9A%8F%E6%9C%BA%E5%86%99.png)

4K随机读：428 IOPS

![单盘随机读.png](%E5%8D%95%E7%9B%98%E9%9A%8F%E6%9C%BA%E8%AF%BB.png)

顺序写：205.8 MB/s

![单盘顺序写.png](%E5%8D%95%E7%9B%98%E9%A1%BA%E5%BA%8F%E5%86%99.png)

顺序读：205.0 MB/s

![单盘顺序读.png](%E5%8D%95%E7%9B%98%E9%A1%BA%E5%BA%8F%E8%AF%BB.png)

## 24块盘组 RAID 0 测试

图里面的26.2T就是24块1.2T组成的raid。

![组建raid0.jpeg](%E7%BB%84%E5%BB%BAraid0.jpeg)

4K随机写：1192 IOPS

![24盘随机写.png](24%E7%9B%98%E9%9A%8F%E6%9C%BA%E5%86%99.png)

4K随机读：1236 IOPS

![24盘随机读.png](24%E7%9B%98%E9%9A%8F%E6%9C%BA%E8%AF%BB.png)

顺序写：3689.5 MB/s

![24盘顺序写.png](24%E7%9B%98%E9%A1%BA%E5%BA%8F%E5%86%99.png)

顺序读：4644.3 MB/s

![24盘顺序读.png](24%E7%9B%98%E9%A1%BA%E5%BA%8F%E8%AF%BB.png)

## 结果汇总

![总结表格.png](%E6%80%BB%E7%BB%93%E8%A1%A8%E6%A0%BC.png)

## B站视频

<iframe style="height:360px;width:640px" src="//player.bilibili.com/player.html?aid=485709242&bvid=BV1zT411h7Pc&cid=1117059965&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

## 视频文字稿

RAID 0 一时爽，数据火葬场。可能很多人还不知道什么是 RAID，所以我首先来简单科普一下，如果已经了解的小伙伴可以直接把进度条往后拉。

RAID 就是指磁盘阵列（Redundant Arrays of Independent Disks）。它分为很多种不同的级别。平时常见的有 RAID 0，RAID 1，RAID 5，RAID 6，以及 RAID 10。RAID 0 会把所有数据平分到所有的硬盘上，实现读写性能加倍，但如果其中一块盘坏了，所有的数据都会丢失。所以江湖上流传着一句话：RAID 0 一时爽，数据火葬场。RAID 1 也称为磁盘镜像，也就是 RAID 1 里面的所有盘存储的内容都是一样的，这样只要剩下一块盘没坏，数据就还在。RAID 1 可以实现读取性能加倍，但是写入性能和单块盘(基本)一样。RAID 5 至少需要三块硬盘才能做。它会用一块盘的空间作为校验，性能和安全性都比单盘有所提升，但不及 RAID 1，可以看成是一个折中选择。RAID 6 和 RAID 5 类似，但是至少需要四块硬盘才能做。它用了两块盘的空间作为校验，安全性比 RAID 5 更高。RAID 10 相当于先做 RAID 1，再做 RAID 0，同时有 RAID 0 和 RAID 1 的特点。

我们用 Linux 下常用的 fio 工具来进行性能测试。

首先我们来测一下单块盘的性能。4K 随机写 343 IOPS，4K 随机读 428 IOPS，顺序写 205.8 MB/s，顺序读 205.0 MB/s。

接下来我们将 24 块盘组成一个 RAID 0。注意，这里组的是硬 RAID，不是软 RAID。硬 RAID 就是通过硬件来实现 RAID 功能，我这里用的是 PERC H330 Mini 这块卡，可以通过 Megacli 这个命令来创建 RAID。软 RAID 就是通过软件来实现 RAID 功能，Linux 下常用 mdadm 命令来创建软 RAID。在这里，我用 Megacli 来创建了一个 24 盘的 RAID 0，并采用 WriteThrough 模式，也就是数据直接写入硬盘，不经过缓存。并且开启了 ReadAhead，也就是预读模式，可以提高顺序读取性能，但会降低随机读取性能。同时使用 Direct，也就是使用 RAID 卡的缓存提高读取命中率。这样，我们的 24 盘 RAID 0 就创建好了。这里的 26.2T 就是 24 块 1.2T 盘组成的 RAID。

有细心的同学可能会发现，`1.2 * 24 = 28.8`，这里应该是 28.8T 才对啊，我可是经过了九年义务教育的，你别骗我。这是因为硬盘厂商对容量的算法和操作系统不一样。硬盘厂商是用的十进制来计算，1TB等于1000GB，但操作系统用的是二进制，1TB等于1024GB，所以按照这个来计算的话，这24块盘的容量就是 `1.2*1000^4/1024^4*24=26.19`，保留一位小数显示出来就是26.2。

性能测试结果是，4K 随机写 1192 IOPS，4K 随机读 1236 IOPS，顺序写 3689.5 MB/s，顺序读 4644.3 MB/s。

和单盘结果对比一下，24 块盘的情况下，4K 随机写的性能是单盘的 347.5%，4K 随机读是单盘的 288.8%，顺序写是单盘的 1793%，顺序读是单盘的 2266%。
