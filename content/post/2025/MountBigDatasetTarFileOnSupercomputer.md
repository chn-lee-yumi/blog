---
title: "在超级计算机中挂载大型数据集压缩包"
description: "由于超级计算机的文件系统一般设置了quota限制，如果数据集包含很多小文件，可能解压时会超出quota。本文介绍了如何在超级计算机中挂载大型数据集压缩包（tar），从而访问里面的文件而无需解压。"
date: 2025-01-20T14:25:00+08:00
lastmod: 2025-01-20T14:25:00+08:00
categories:
  - 学习
tags:
  - Linux
  - HPC
---

## 背景

我最近在搞 AffectNet 数据集，里面一百多万个文件。我用的是 Setonix 超级计算机，使用了 Lustre 文件系统，并且提供了一个 `/scratch` 分区给我们放临时文件。但是这个分区限制了文件数量为100万个，所以我在解压数据集的时候就遇到了报错。正常的解决办法是给他们提交工单，请求提高文件数量限制。澳洲的办事效率你们懂的，周一提交的工单，来回还问了几个问题，最后周五才给我扩容。求人不如求己，对于这种问题其实有替代的解决方案。

## 原理

我的数据集是用 tar 格式打包的，对于大多数的压缩包（`.tar` 文件本质上只是一个归档文件而不是压缩文件，不过这里也用"压缩包"统一称呼），其实有办法可以直接挂载到一个目录。我们用到的技术叫 `FUSE` —— Filesystem in Userspace (用户空间文件系统)。也就是说我们不需要 `root` 权限就能把压缩包挂载到某个目录上实现对里面内容的读取。经过一番搜索，`python` 下有 `ratarmount` 这个库可以实现这个功能。

## 操作步骤

因为这是超算，需要用 `module load` 加载对应的模块后才能用 `python`，所以我这里要先加载模块，然后激活我之前用的虚拟环境：

```bash
module load pytorch/2.2.0-rocm5.7.3
source /home/liyumin/software/venv/bin/activate
```

如果本来就能用 `python`，那上面的步骤可以跳过。

然后通过 `pip` 安装 `ratarmount`：

```bash
pip install ratarmount
```

装完之后就可以执行命令挂载了：

```bash
ratarmount train_set.tar train_set
```

这个命令的意思是将 `train_set.tar` 挂载到 `train_set` 目录。

有可能会遇到下面的报错：

```text
Created mount point at: /scratch/pawsey1001/liyumin/datasets/AffectNet8/train_set
fusermount: mounting over filesystem type 0x0bd00bd0 is forbidden
```

这是因为这个文件系统下面不让挂载。这个问题可以通过更换路径解决，例如我挂载到 `tmp` 目录：

```bash
ratarmount train_set.tar /tmp/train_set
```

没有报错就说明成功了。 现在我们访问 `/tmp/train_set` 目录，就等于访问 `train_set.tar` 里面的内容了。 这样子我们就实现了不解压来访问压缩包内的文件。

用完记得卸载目录：

```bash
fusermount -u /tmp/train_set
```
