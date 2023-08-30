---
title: "在路由器上跑Debian"
description: "通过Debootstrap生成Debian镜像然后在路由器上通过chroot运行。"
date: 2017-01-30T23:08:05+08:00
categories:
  - 折腾
tags:
  - Linux
  - OpenWRT
---

首先，你需要知道什么是[Debootstrap](https://wiki.debian.org/Debootstrap/)。

然后阅读此文档第一部分：[EmDebianCrossDebootstrap](https://wiki.debian.org/EmDebian/CrossDebootstrap)。

我们可以看到有多种方法可以实现我们的目的。**我的路由器CPU是MT7621，是mipsel架构的**。

我使用的是第二部分的方法：[QEMU/debootstrap approach](https://wiki.debian.org/EmDebian/CrossDebootstrap#QEMU.2Fdebootstrap_approach)。

我使用的是Ubuntu。

按照上面的要求，安装需要的包：

```shell
apt-get install binfmt-support qemu qemu-user-static debootstrap
```

然后随便新建个目录，例如：

```shell
mkdir mipsel_debian
```

然后运行bootstrap，**注意arch要改过来，后面Jessie是你想要的版本，再后面mipsel_debian是刚刚新建的目录，最后是[镜像地址](http://www.debian.org/mirror/list)**。

```shell
debootstrap --foreign --arch mipsel jessie mipsel_debian http://ftp.cn.debian.org/debian/
```

搞定之后接着按文档教程走。有些地方改一下就行了。

```shell
cp /usr/bin/qemu-mipsel-static mipsel_debian/usr/bin
DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true LC_ALL=C LANGUAGE=C LANG=C 
chroot mipsel_debian /debootstrap/debootstrap --second-stage
DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true LC_ALL=C LANGUAGE=C LANG=C
chroot mipsel_debian dpkg --configure -a
```

然后就完成了。把整个目录拷到u盘，u盘插到路由器上，ssh进路由器，chroot进去就能用了。
chroot前要做一些工作，参考[Debootstrap](https://wiki.debian.org/Debootstrap/)：

```shell
mount /dev mipsel_debian/dev
mount /sys mipsel_debian/sys
mount /proc mipsel_debian/proc
cp /proc/mounts mipsel_debian/etc/mtab
```

最后chroot进去：

```shell
chroot mipsel_debian /bin/bash
```

如果想用ssh，在chroot前可能还需要下面这一步：

```shell
mount /dev/pts mipsel_debian/dev/pts
```
