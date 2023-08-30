---
title: "极路由使用fping（交叉编译）"
description: "交叉编译fping"
date: 2016-05-01T12:06:44+08:00
categories:
  - 折腾
tags:
  - Linux
  - OpenWRT
---

首先搭建环境 ，参考链接：https://code.hiwifi.com/wiki/hiwifi/sdk-howto

这里系统用Ubuntu Kylin 14.04 amd64

过程：

```shell
apt-get install subversion git build-essential libncurses5-dev zlib1g-dev gawk unzip gettext libssl-dev intltool openjdk-6-jre-headless optipng
ln -sf bash /bin/sh
cd /home
mkdir hiwifi
useradd -d /home/hiwifi hiwifi
passwd hiwifi
****** （这里是改密码）
******
chmod 777 /home/hiwifi
login
hiwifi （这里是登录）
******
wget http://hiwifi-sdk.oss.aliyuncs.com/HC5661s-mediatek-sdk.tar.bz2 （注：这是极1S的交叉编译工具，只支持64位系统）
tar xjf HC5661s-mediatek-sdk.tar.bz2
cd OpenWrt-SDK-mediatek-for-redhat-x86_64-gcc-4.6-linaro_uClibc-0.9.33.2 （不用输这么长，按tab键自动补全）
./scripts/cross-compile.sh ./
```

然后随便编一个helloworld，编译完放极路由上，正常运行。

---

交叉编译环境搭建完之后，运行`./scripts/cross-compile.sh ./`

然后准备编译fping：

```shell
wget http://www.fping.org/dist/fping-3.13.tar.gz
tar xzf fping-3.13.tar.gz
cd fping-3.13
./configure
```

输出:

```
checking build system type... mipsel-unknown-linux-uclibc

checking host system type... mipsel-unknown-linux-uclibc

checking target system type... mipsel-unknown-linux-uclibc

checking for a BSD-compatible install... /usr/bin/install -c

checking whether build environment is sane... yes

checking for a thread-safe mkdir -p... /bin/mkdir -p

checking for gawk... gawk

checking whether make sets $(MAKE)... yes

checking whether make supports nested variables... yes

checking whether to enable maintainer-specific portions of Makefiles... no

checking for gcc... gcc

checking whether the C compiler works... yes

checking for C compiler default output file name... a.out

checking for suffix of executables... 

checking whether we are cross compiling... configure: error: in `/home/hiwifi/fping-3.13':

configure: error: cannot run C compiled programs.

If you meant to cross compile, use `--host'.

See `config.log' for more details
```

然后看一下帮助： `./configure -h`

于是再次configure：`./configure --host=mips`

成功！

直接make，然后： `cd src`

看到fping了！

把这个文件复制到极路由上，加执行权限，就能用了。
