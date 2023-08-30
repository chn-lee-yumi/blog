---
title: "Linux下free命令看到的buffer和cache的区别"
description: "Linux的buffer和cache的区别：buffer是块设备的缓存，cache是文件系统的缓存。"
date: 2023-01-13T17:35:40+08:00
categories:
  - 学习
tags:
  - Linux
---

## 结论

- buffer是块设备的缓存
- cache是文件系统的缓存

这里的缓存包括读和写。

## 实验证明

首先看看buffer和cache的值：

```shell
root@localhost:~# cat /proc/meminfo | grep -E 'Buffers|Cache'
Buffers:          238024 kB
Cached:          1041304 kB
SwapCached:        88328 kB
```

然后用dd读取块设备100M大小，并查看结果，可以发现buffer涨了100M。

```shell
root@localhost:~# dd if=/dev/vda of=/dev/null bs=1M count=100
记录了100+0 的读入
记录了100+0 的写出
104857600字节（105 MB，100 MiB）已复制，0.334603 s，313 MB/s
root@localhost:~# cat /proc/meminfo |grep -E 'Buffers|Cache'
Buffers:          341480 kB
Cached:          1042240 kB
SwapCached:        88328 kB
```

试下再读一次，发现速度爆炸快，说明确实是直接从buffer里读取。

```shell
root@localhost:~# dd if=/dev/vda of=/dev/null bs=1M count=100
记录了100+0 的读入
记录了100+0 的写出
104857600字节（105 MB，100 MiB）已复制，0.0202984 s，5.2 GB/s
```

接着用cat读取一个33M的文件，并查看结果，可以看到cache涨了33M。

```shell
root@localhost:~# ls -lh /var/log
......
-rw-r-----  1 xrdp        adm              33M 11月  6 15:26 xrdp.log
......
root@localhost:~# cat /var/log/xrdp.log > /dev/null
root@localhost:~# cat /proc/meminfo |grep -E 'Buffers|Cache'
Buffers:          341648 kB
Cached:          1075616 kB
SwapCached:        88328 kB
```

dd写入一个100M的文件，然后执行sync，同时观察vmstat：

```shell
root@localhost:~# dd if=/dev/zero of=test.img bs=1M count=100
记录了100+0 的读入
记录了100+0 的写出
104857600字节（105 MB，100 MiB）已复制，0.0703571 s，1.5 GB/s
root@localhost:~# sync
```

可以发现dd写入速度非常快，同时cache涨了100M，但磁盘并未写入。执行sync的时候，磁盘才写入了100M。

```shell
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b 交换 空闲 缓冲 缓存   si   so    bi    bo   in   cs us sy id wa st
 0  0 214316 281576 338164 1019048    0    0     1    14    2    1  0  1 99  0  0
 0  0 214316 281416 338164 1019060    0    0     0     0  961  286  0  0 100  0  0
 0  0 214316 280808 338164 1019072    0    0     0     0 1111  294  0  1 99  0  0
 0  0 214316 280232 338164 1019080    0    0     0     0  951  294  1  1 98  0  0
 0  0 214316 280040 338164 1019088    0    0     0     0  765  279  1  0 99  0  0
 0  0 214316 176712 338164 1121500    0    0     0    44  988  352  0  7 93  0  0
 0  0 214316 176328 338164 1121508    0    0     0   300 1043  308  0  1 99  0  0
 0  0 214316 176392 338164 1121520    0    0     0     8  960  314  1  0 99  0  0
 0  0 214316 176296 338164 1121524    0    0     0     0  843  275  0  0 100  0  0
 0  0 214316 175944 338164 1121532    0    0     0   124  682  355  0  1 98  1  0
 0  0 214316 175616 338164 1121540    0    0     0 102760 1015  508  1  2 76 21  0
 0  0 214316 175752 338164 1121556    0    0     0     0  971  343  0  1 99  0  0
```

dd往块设备写入的时候buffer也是会涨的，因手头没有测试环境，这里不再实验。（听说buffer和cache都会涨）