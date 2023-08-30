---
title: "迷你Ceph集群搭建（超低配设备）"
description: "超低配设备搭建迷你Ceph集群，x86+ARMv7+ARM64异构集群。"
date: 2023-05-01T17:57:36+08:00
categories:
  - 折腾
tags:
  - RaspberryPi
  - B站视频
  - Ceph
---

## 环境

机器列表：

|IP|角色|说明|
|---|---|---|
|10.0.0.15|osd|ARMv7，512M内存，32G存储，百兆网口|
|10.0.0.16|client|ARM64，2G内存，测试集群性能用，千兆网口|
|10.0.0.17|osd|AMD64，2G内存，32G存储，百兆网口|
|10.0.0.18|mon,mgr,mds,osd|AMD64，2G内存，32G存储，百兆网口|
|10.0.0.19|osd|ARM64，1G内存，32G存储，百兆网口|

这集群有x86，有ARM，ARM里面还分ARMv7和ARM64，你问我是有意的还是不小心的？我是有意用三种架构的CPU的。

注意：老版本（14.2.21）不同架构不能混合部署，否则osd通信有问题。后续尝试17.2.5版本发现已修复，不过新版本又出现了个RAW USED不准的bug（可能是因为ARMv7是32位，只支持4G空间）以及osd无法删除的bug。

系统采用ubuntu或debian。参考文档：[https://docs.ceph.com/en/quincy/install/manual-deployment](https://docs.ceph.com/en/quincy/install/manual-deployment)

**官方推荐内存最少4G，我最低用512M内存的板子，纯属娱乐。**

## 部署步骤

【可选】增加软件源`/etc/apt/sources.list.d/ceph.list`：

```shell
deb https://mirrors.tuna.tsinghua.edu.cn/ceph/debian-quincy/ bullseye main
```

【可选】添加公钥：

```shell
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E84AC2C0460F3994
```

在所有ceph节点和客户端安装软件包：

```shell
apt-get update
apt-get install -y ceph ceph-mds ceph-volume
```

在所有ceph节点和客户端创建配置文件`/etc/ceph/ceph.conf`：

```conf
[global]
fsid = 4a0137cc-1081-41e4-bacd-5ecddc63ae2d
mon initial members = intel-compute-stick
mon host = 10.0.0.17
public network = 10.0.0.0/24
cluster network = 10.0.0.0/24
osd journal size = 64
osd pool default size = 2
osd pool default min size = 1
osd pool default pg num = 64
osd pool default pgp num = 64
osd crush chooseleaf type = 1
```

在mon节点执行初始化命令：

```shell
ceph-authtool --create-keyring /tmp/ceph.mon.keyring --gen-key -n mon. --cap mon 'allow *'
ceph-authtool --create-keyring /etc/ceph/ceph.client.admin.keyring --gen-key -n client.admin --cap mon 'allow *' --cap osd 'allow *' --cap mds 'allow *' --cap mgr 'allow *'
ceph-authtool --create-keyring /var/lib/ceph/bootstrap-osd/ceph.keyring --gen-key -n client.bootstrap-osd --cap mon 'profile bootstrap-osd' --cap mgr 'allow r'
ceph-authtool /tmp/ceph.mon.keyring --import-keyring /etc/ceph/ceph.client.admin.keyring
ceph-authtool /tmp/ceph.mon.keyring --import-keyring /var/lib/ceph/bootstrap-osd/ceph.keyring
chown ceph:ceph /tmp/ceph.mon.keyring
monmaptool --create --add intel-compute-stick 10.0.0.17 --fsid 4a0137cc-1081-41e4-bacd-5ecddc63ae2d /tmp/monmap
sudo -u ceph mkdir /var/lib/ceph/mon/ceph-intel-compute-stick
sudo -u ceph ceph-mon --mkfs -i intel-compute-stick --monmap /tmp/monmap --keyring /tmp/ceph.mon.keyring
systemctl start ceph-mon@intel-compute-stick
```

部署MGR：

```shell
name=intel-compute-stick
mkdir -p /var/lib/ceph/mgr/ceph-$name
ceph auth get-or-create mgr.$name mon 'allow profile mgr' osd 'allow *' mds 'allow *' > /var/lib/ceph/mgr/ceph-$name/keyring
ceph-mgr -i $name
```

【旧版本需要做此操作】在ARMv7架构的osd节点修改文件`nano /usr/lib/python3/dist-packages/ceph_argparse.py`，将`timeout = kwargs.pop('timeout', 0)`改成`timeout = 24 * 60 * 60`。

**将`/var/lib/ceph/bootstrap-osd/ceph.keyring`同步到所有osd节点。**

部署OSD：

```shell
truncate --size 16G osd.img
losetup /dev/loop5 /root/osd.img 
ceph-volume raw prepare --data /dev/loop5 --bluestore
systemctl start ceph-osd@{osd-num} # 注意这个num要和前面输出一致
```

部署mds：

```shell
mkdir -p /var/lib/ceph/mds/ceph-intel-compute-stick
ceph-authtool --create-keyring /var/lib/ceph/mds/ceph-intel-compute-stick/keyring --gen-key -n mds.intel-compute-stick
ceph auth add mds.intel-compute-stick osd "allow rwx" mds "allow *" mon "allow profile mds" -i /var/lib/ceph/mds/ceph-intel-compute-stick/keyring
```

修改`/etc/ceph/ceph.conf`，增加如下内容

```conf
[mds.intel-compute-stick]
host = intel-compute-stick
```

执行命令：

```shell
ceph-mds --cluster ceph -i intel-compute-stick -m 10.0.0.17:6789
systemctl start ceph.target
```

创建cephfs：

```shell
ceph osd pool create perf_test 64
ceph osd pool create cephfs_data 64
ceph osd pool create cephfs_metadata 16
ceph fs new cephfs cephfs_metadata cephfs_data
ceph fs authorize cephfs client.cephfs_user / rw
# 将上面的输出复制到客户端`/etc/ceph/ceph.client.cephfs_user.keyring`文件中
```

挂载cephfs：

```shell
mkdir /mnt/cephfs
mount -t ceph cephfs_user@.cephfs=/ /mnt/cephfs
```

## 其它命令

显示 bluestore 缓存的当前值：`ceph daemon /var/run/ceph/ceph-osd.1.asok config show | grep bluestore_cache_size`

设置OSD缓存用量：`ceph daemon /var/run/ceph/ceph-osd.1.asok config set bluestore_cache_size_ssd 134217128`

`ceph-volume raw list`

重启后重新挂载osd：`ceph-volume raw activate --device /dev/loop5 --no-systemd`

手动删除osd：`ceph osd out {osd-num}`

`ceph osd safe-to-destroy osd.2`

`ceph osd destroy {id} --yes-i-really-mean-it`

## 性能测试

|节点数|随机写(IOPS)|随机读(IOPS)|顺序写(MiB/s)|顺序读(MiB/s)|rados写(MB/s)|rados读(MB/s)|rados随机(MB/s)|
|-----|-----|-----|-----|-----|-----|--------|--------|
|2|1603|5295|8.01|21.8|10.6733|21.5597|22.2359|
|3|1310|6058|14.0|27.9|12.952|28.0797|29.3502|
|4|1392|4087|15.5|32.3|15.3398|33.2157|34.9272|

![fio随机读写.png](fio%E9%9A%8F%E6%9C%BA%E8%AF%BB%E5%86%99.png)

![fio顺序读写.png](fio%E9%A1%BA%E5%BA%8F%E8%AF%BB%E5%86%99.png)

![rados性能测试.png](rados%E6%80%A7%E8%83%BD%E6%B5%8B%E8%AF%95.png)

### 两节点

![两节点状态截图.png](%E4%B8%A4%E8%8A%82%E7%82%B9%E7%8A%B6%E6%80%81%E6%88%AA%E5%9B%BE.png)

cephfs：

- dd写入：16.3 MB/s (dd if=/dev/zero of=test.img bs=1M count=1024)
- dd读取：17.9 MB/s (echo 3 > /proc/sys/vm/drop_caches; dd if=test.img of=/dev/null bs=1M)
- fio随机写：1603
- fio随机读：5295
- fio顺序写：8201KiB/s
- fio顺序读：21.8MiB/s

rados bench -p perf_test 30 write --no-cleanup

```shell
hints = 1
Maintaining 16 concurrent writes of 4194304 bytes to objects of size 4194304 for up to 30 seconds or 0 objects
Object prefix: benchmark_data_orangepi3-lts_2101
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0       0         0         0         0         0           -           0
    1      16        16         0         0         0           -           0
    2      16        16         0         0         0           -           0
    3      16        16         0         0         0           -           0
    4      16        19         3   2.99955         3     3.64087     3.38759
    5      16        22         6   4.79925        12     4.34316     3.83332
    6      16        25         9   5.99904        12     5.38901     4.34105
    7      16        28        12   6.85602        12     6.50295     4.87251
    8      16        31        15   7.49875        12     4.71442      4.9794
    9      16        36        20   8.88738        20     4.61761     5.24509
   10      16        38        22   8.79849         8     9.75918     5.40151
   11      16        41        25   9.08934        12     5.56684     5.44177
   12      16        46        30   9.99826        20     3.34787     5.21296
   13      16        49        33   10.1521        12     4.10847     5.17286
   14      16        51        35   9.99824         8     3.49611     5.16674
   15      16        55        39   10.3982        16     6.06545       5.098
   16      16        58        42   10.4981        12     6.23518     5.07308
   17      16        59        43   10.1158         4     6.45517     5.10522
   18      16        62        46   10.2204        12     6.48019     5.08282
   19      16        63        47   9.89297         4     6.57521     5.11457
2023-04-18T15:12:33.881436+0800 min lat: 1.95623 max lat: 9.75918 avg lat: 5.12979
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
   20      16        68        52   10.3981        20     6.95187     5.12979
   21      16        68        52   9.90296         0           -     5.12979
   22      16        70        54    9.8164         4     7.85105     5.23762
   23      16        72        56   9.73736         8      8.1019     5.33872
   24      16        76        60   9.99818        16     8.86371     5.40133
   25      16        77        61   9.75822         4     3.14892      5.3644
   26      16        80        64   9.84436        12     9.63972     5.45864
   27      16        82        66     9.776         8     3.18262     5.48564
   28      16        84        68   9.71252         8     3.89847     5.52669
   29      16        87        71   9.79132        12     9.72659     5.63168
   30      16        91        75   9.99818        16     9.93409     5.63449
   31      13        91        78   10.0627        12     4.09479     5.65952
   32      11        91        80   9.99817         8      4.0216     5.68887
   33       6        91        85   10.3012        20     3.65814      5.7294
   34       1        91        90   10.5863        20     4.55552     5.71818
Total time run:         34.1039
Total writes made:      91
Write size:             4194304
Object size:            4194304
Bandwidth (MB/sec):     10.6733
Stddev Bandwidth:       6.19765
Max bandwidth (MB/sec): 20
Min bandwidth (MB/sec): 0
Average IOPS:           2
Stddev IOPS:            1.58086
Max IOPS:               5
Min IOPS:               0
Average Latency(s):     5.70886
Stddev Latency(s):      2.2914
Max latency(s):         11.0174
Min latency(s):         1.95623
```

rados bench -p perf_test 30 seq

```shell
hints = 1
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0       0         0         0         0         0           -           0
    1      16        18         2   7.99563         8    0.749535    0.640048
    2      16        24         8   15.9934        24     1.82768      1.2209
    3      16        30        14   18.6602        24     2.90052     1.76318
    4      16        36        20   19.9939        24     3.22248     2.10121
    5      16        41        25   19.9941        20     2.38014     2.20456
    6      16        46        30   19.9943        20     3.69409     2.33743
    7      16        52        36   20.5655        24     3.58809      2.4047
    8      16        58        42   20.9942        24     3.94671     2.48664
    9      15        63        48   21.3151        24     2.99373     2.55527
   10      16        69        53   21.1832        20     3.06825     2.56988
   11      16        75        59   21.4387        24     3.56289     2.56456
   12      16        80        64   21.3185        20     1.57452     2.55362
   13      16        86        70   21.5243        24     1.79171     2.56933
   14      16        91        75   21.4152        20      4.4904      2.6246
   15      10        91        81   21.5871        24      4.2782     2.67077
   16       4        91        87   21.7375        24     2.84972     2.68923
Total time run:       16.8834
Total reads made:     91
Read size:            4194304
Object size:          4194304
Bandwidth (MB/sec):   21.5597
Average IOPS:         5
Stddev IOPS:          1.03078
Max IOPS:             6
Min IOPS:             2
Average Latency(s):   2.69827
Max latency(s):       4.4904
Min latency(s):       0.530561
```

rados bench -p perf_test 30 rand

```shell
hints = 1
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0       0         0         0         0         0           -           0
    1      16        20         4   15.9921        16    0.756867    0.562019
    2      16        26        10   19.9929        24     1.82705     1.09684
    3      16        32        16   21.3269        24     2.89898     1.63216
    4      16        38        22   21.9939        24      2.8592     1.96528
    5      16        42        26   20.7945        16     2.89643     2.08897
    6      16        48        32   21.3279        24     3.25362     2.24424
    7      16        54        38   21.7089        24     2.53504     2.33103
    8      16        60        44   21.9947        24     2.49214     2.39352
    9      16        66        50   22.2169        24      2.8506     2.46248
   10      16        70        54   21.5948        16     2.89337     2.49112
   11      16        76        60   21.8128        24     2.13852     2.49727
   12      16        82        66   21.9946        24     2.53781     2.54012
   13      16        88        72   22.1485        24     2.53625     2.57632
   14      16        94        78   22.2804        24     2.89682     2.59727
   15      15        98        83   22.1192        20     2.80375     2.61577
   16      16       104        88   21.9865        20     2.54292     2.62566
   17      16       110        94   22.1046        24     2.84867     2.64381
   18      16       116       100   22.2097        24     3.20428     2.65252
   19      16       122       106   22.3036        24      2.5454      2.6641
2023-04-18T15:13:26.426279+0800 min lat: 0.367019 max lat: 3.92008 avg lat: 2.6753
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
   20      16       127       111   22.1883        20     2.84974      2.6753
   21      16       132       116   22.0838        20     2.90241     2.68289
   22      16       138       122   22.1707        24     3.20846     2.68523
   23      16       144       128     22.25        24     3.25698     2.69284
   24      16       150       134   22.3228        24     3.26158     2.69223
   25      16       155       139   22.2297        20     1.06362     2.67481
   26      16       160       144   22.1438        20      3.9225     2.67843
   27      16       166       150   22.2124        24     4.27967     2.68765
   28      16       172       156    22.276        24     4.33003     2.69881
   29      16       178       162   22.3353        24      3.9836     2.71073
   30      16       183       167   22.2573        20     2.13414     2.71708
   31      11       183       172   22.1844        20     3.57702     2.72915
   32       5       183       178    22.241        24     3.63257     2.73706
Total time run:       32.9197
Total reads made:     183
Read size:            4194304
Object size:          4194304
Bandwidth (MB/sec):   22.2359
Average IOPS:         5
Stddev IOPS:          0.669015
Max IOPS:             6
Min IOPS:             4
Average Latency(s):   2.74483
Max latency(s):       4.63637
Min latency(s):       0.367019
```

### 三节点

![三节点状态截图.png](%E4%B8%89%E8%8A%82%E7%82%B9%E7%8A%B6%E6%80%81%E6%88%AA%E5%9B%BE.png)

cephfs：

- dd写入：21.3 MB/s (dd if=/dev/zero of=test.img bs=1M count=1024)
- dd读取：19.5 MB/s (echo 3 > /proc/sys/vm/drop_caches; dd if=test.img of=/dev/null bs=1M)
- fio随机写：1310
- fio随机读：6058
- fio顺序写：14.0MiB/s
- fio顺序读：27.9MiB/s

rados bench -p perf_test 30 write --no-cleanup

```shell
hints = 1
Maintaining 16 concurrent writes of 4194304 bytes to objects of size 4194304 for up to 30 seconds or 0 objects
Object prefix: benchmark_data_orangepi3-lts_2188
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0       0         0         0         0         0           -           0
    1      16        16         0         0         0           -           0
    2      16        17         1   1.99967         2     1.99725     1.99725
    3      16        19         3   3.99915         8     2.92674     2.50932
    4      16        21         5   4.99899         8     3.68936     2.91102
    5      16        25         9   7.19858        16     4.44208     3.50803
    6      16        29        13   8.66497        16     3.32056     3.77577
    7      16        31        15   8.56977         8     6.59867     3.95511
    8      16        33        17   8.49837         8     2.95588     3.89244
    9      16        39        23   10.2203        24     8.91377      4.5287
   10      16        42        26    10.398        12     4.00285     4.61726
   11      16        46        30    10.907        16     1.88708     4.32788
   12      16        48        32   10.6647         8     3.22648     4.22892
   13      16        52        36   11.0748        16     1.51764     4.17041
   14      16        53        37   10.5695         4     2.53073      4.1261
   15      16        55        39   10.3981         8     8.91467     4.39938
   16      16        60        44   10.9979        20     7.31564      4.7521
   17      16        61        45   10.5862         4     2.00639     4.69108
   18      16        66        50    11.109        20     2.34879     4.76501
   19      16        69        53   11.1558        12     2.87372     4.81177
2023-04-18T15:18:28.656929+0800 min lat: 1.51764 max lat: 10.6957 avg lat: 4.81906
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
   20      16        74        58   11.5978        20     2.18304     4.81906
   21      16        75        59   11.2359         4     7.06397     4.85711
   22      16        80        64   11.6341        20     3.49498     4.85191
   23      16        80        64   11.1283         0           -     4.85191
   24      16        82        66   10.9979         4      6.3591     4.83667
   25      16        84        68   10.8779         8     6.34421     4.91693
   26      16        89        73   11.2286        20     8.52854     5.06126
   27      16        92        76   11.2571        12     5.63676     5.07197
   28      16        97        81   11.5692        20     6.39309     5.04017
   29      16       100        84    11.584        12     7.29099     5.01084
   30      16       105        89   11.8644        20     2.50054     4.96138
   31      10       105        95   12.2558        24     9.50269     4.94482
   32       4       105       101   12.6226        24     4.52251     4.83104
Total time run:         32.4273
Total writes made:      105
Write size:             4194304
Object size:            4194304
Bandwidth (MB/sec):     12.952
Stddev Bandwidth:       7.39196
Max bandwidth (MB/sec): 24
Min bandwidth (MB/sec): 0
Average IOPS:           3
Stddev IOPS:            1.87271
Max IOPS:               6
Min IOPS:               0
Average Latency(s):     4.774
Stddev Latency(s):      2.42686
Max latency(s):         10.6957
Min latency(s):         1.51764
```

rados bench -p perf_test 30 seq

```shell
hints = 1
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0       0         0         0         0         0           -           0
    1      16        19         3   11.9944        12    0.935954    0.768977
    2      16        26        10   19.9933        28     1.96017     1.31348
    3      16        33        17   22.6602        28     2.77006     1.68533
    4      16        42        26   25.9932        36     2.27413     1.75351
    5      16        51        35   27.9931        36     2.27554     1.77164
    6      16        59        43   28.6598        32     2.90927     1.80862
    7      16        65        49   27.9935        24     1.89015     1.83058
    8      16        72        56   27.9936        28    0.468285     1.88307
    9      16        81        65   28.8824        36    0.785162     1.90263
   10      15        88        73   29.1822        32      2.5208     1.94424
   11      16        95        79   28.7108        24      2.0044     1.96069
   12      16       103        87   28.9843        32     3.24909     1.95645
   13       9       105        96   29.5231        36     2.53005     1.97092
   14       3       105       102   29.1284        24     1.87098     2.00023
Total time run:       14.9574
Total reads made:     105
Read size:            4194304
Object size:          4194304
Bandwidth (MB/sec):   28.0797
Average IOPS:         7
Stddev IOPS:          1.68379
Max IOPS:             9
Min IOPS:             3
Average Latency(s):   2.02704
Max latency(s):       3.42015
Min latency(s):       0.417385
```

rados bench -p perf_test 30 rand

```shell
hints = 1
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0       0         0         0         0         0           -           0
    1      16        22         6    23.986        24    0.824307    0.603606
    2      16        31        15   29.9884        36     1.90078     1.13916
    3      16        40        24   31.9898        36     2.15175     1.41768
    4      16        47        31   30.9908        28     1.42468      1.5251
    5      16        55        39    31.191        32     2.52356      1.5776
    6      16        63        47   31.3248        32     2.89946     1.61864
    7      16        71        55   31.4203        32    0.368204     1.66398
    8      16        78        62   30.9915        28     2.37269     1.70559
    9      16        87        71   31.5467        36     2.84709     1.77106
   10      16        95        79   31.5911        32     1.07912     1.79016
   11      16       104        88   31.9911        36     1.44303     1.80956
   12      16       112        96   31.9913        32     1.42344      1.8181
   13      16       119       103   31.6838        28     2.69186     1.80644
   14      16       127       111   31.7059        32     3.20146     1.82418
   15      16       133       117   31.1918        24    0.423103     1.84334
   16      16       141       125   31.2418        32    0.992599     1.85535
   17      16       148       132   31.0508        28     0.97594     1.84928
   18      16       155       139   30.8809        28     1.49825      1.8682
   19      16       161       145   30.5185        24     4.27347     1.90106
2023-04-18T15:19:17.492678+0800 min lat: 0.366624 max lat: 4.73499 avg lat: 1.92024
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
   20      15       167       152   30.3887        28     4.73499     1.92024
   21      16       175       159   30.2746        28    0.367838     1.90697
   22      16       184       168   30.5345        36    0.745395     1.90833
   23      16       193       177   30.7718        36     1.09359     1.92217
   24      16       199       183   30.4895        24     4.54686     1.95203
   25      16       207       191   30.5496        32     4.18695     1.97411
   26      16       215       199   30.6052        32     1.11538     1.96496
   27      16       223       207   30.6566        32     1.41712     1.96474
   28      16       230       214   30.5616        28     2.08073     1.98234
   29      16       236       220   30.3352        24      2.4372     2.00951
   30      16       241       225   29.9906        20     3.20498       2.026
   31       9       241       232   29.9262        28     2.49127     2.02668
   32       3       241       238   29.7409        24      2.5638     2.05061
Total time run:       32.8447
Total reads made:     241
Read size:            4194304
Object size:          4194304
Bandwidth (MB/sec):   29.3502
Average IOPS:         7
Stddev IOPS:          1.10534
Max IOPS:             9
Min IOPS:             5
Average Latency(s):   2.06437
Max latency(s):       4.91188
Min latency(s):       0.366624
```

### 四节点

![四节点状态截图.png](%E5%9B%9B%E8%8A%82%E7%82%B9%E7%8A%B6%E6%80%81%E6%88%AA%E5%9B%BE.png)

cephfs：

- dd写入：22.0 MB/s (dd if=/dev/zero of=test.img bs=1M count=1024)
- dd读取：19.7 MB/s (echo 3 > /proc/sys/vm/drop_caches; dd if=test.img of=/dev/null bs=1M)
- fio随机写：1392
- fio随机读：4087
- fio顺序写：15.5MiB/s
- fio顺序读：32.3MiB/s

rados bench -p perf_test 30 write --no-cleanup

```shell
hints = 1
Maintaining 16 concurrent writes of 4194304 bytes to objects of size 4194304 for up to 30 seconds or 0 objects
Object prefix: benchmark_data_orangepi3-lts_35619
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0       0         0         0         0         0           -           0
    1      16        16         0         0         0           -           0
    2      16        17         1   1.99975         2     1.78202     1.78202
    3      16        20         4   5.33256        12     2.84877     2.43044
    4      16        21         5   4.99923         4     3.74263     2.69287
    5      16        23         7    5.5991         8     4.76583     2.85451
    6      16        32        16   10.6649        36     5.86804     3.70616
    7      16        34        18    10.284         8     1.92668      3.4596
    8      16        39        23    11.498        20     7.93078      3.6863
    9      16        42        26   11.5535        12     8.75803     3.93689
   10      16        47        31   12.3978        20     9.69823     3.95612
   11      16        50        34   12.3614        12     3.04304      3.9946
   12      16        54        38   12.6644        16     3.45564     3.99375
   13      16        60        44    13.536        24     3.44875     3.95588
   14      16        63        47   13.4261        12     1.81607     3.85018
   15      16        67        51   13.5975        16     2.73712     3.76863
   16      16        71        55   13.7475        16     4.15855     3.72367
   17      16        76        60    14.115        20     10.2432     3.75291
   18      16        79        63   13.9973        12     2.17743     3.81827
   19      16        83        67   14.1024        16     8.20002     3.90448
2023-04-30T16:14:03.140857+0800 min lat: 1.0234 max lat: 10.2441 avg lat: 3.90471
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
   20      16        84        68   13.5973         4     3.91999     3.90471
   21      16        87        71   13.5211        12     3.44596     3.99304
   22      16        93        77   13.9972        24     3.23659     3.97209
   23      16        96        80   13.9102        12     1.23555     4.00768
   24      16       102        86   14.3305        24     1.35805     4.04373
   25      16       103        87   13.9172         4     6.09656     4.06732
   26      16       107        91   13.9972        16      3.5407     4.08549
   27      16       109        93    13.775         8     6.03469     4.08524
   28      16       118       102   14.5686        36     2.17569     4.06772
   29      16       121       105   14.4799        12     4.49289     4.11014
   30      16       125       109   14.5305        16     2.87309     4.08652
   31       9       125       116   14.9648        28     2.25205      4.0526
   32       6       125       119   14.8721        12     1.79392     4.00744
Total time run:         32.5949
Total writes made:      125
Write size:             4194304
Object size:            4194304
Bandwidth (MB/sec):     15.3398
Stddev Bandwidth:       8.72312
Max bandwidth (MB/sec): 36
Min bandwidth (MB/sec): 0
Average IOPS:           3
Stddev IOPS:            2.20611
Max IOPS:               9
Min IOPS:               0
Average Latency(s):     4.0305
Stddev Latency(s):      2.20517
Max latency(s):         10.2441
Min latency(s):         1.0234
```

rados bench -p perf_test 30 seq

```shell
hints = 1
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0       0         0         0         0         0           -           0
    1      16        20         4   15.9905        16    0.853527    0.650566
    2      16        32        16    31.987        48     1.92335      1.1849
    3      15        42        27   35.9872        44    0.728561     1.28407
    4      16        54        38   37.9873        44     1.45691     1.36427
    5      16        63        47   37.5885        36    0.867527     1.32744
    6      16        71        55   36.6558        32    0.388871     1.33514
    7      16        81        65   37.1323        40    0.402616     1.36986
    8      16        90        74     36.99        36      1.0629     1.41874
    9      16        99        83   36.8793        36     1.75055     1.48116
   10      16       106        90   35.9908        28    0.407852     1.52166
   11      16       117       101   36.7179        44     1.74839     1.55673
   12      13       125       112    37.324        44     1.12977     1.56548
   13       6       125       119   36.6064        28     2.87119      1.5828
   14       3       125       122   34.8488        12     3.12215     1.61803
   15       1       125       124   33.0589         8      3.1234     1.64145
Total time run:       15.0531
Total reads made:     125
Read size:            4194304
Object size:          4194304
Bandwidth (MB/sec):   33.2157
Average IOPS:         8
Stddev IOPS:          3.12745
Max IOPS:             12
Min IOPS:             2
Average Latency(s):   1.65394
Max latency(s):       4.13081
Min latency(s):       0.388871
```

rados bench -p perf_test 30 rand

```shell
hints = 1
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0       0         0         0         0         0           -           0
    1      16        22         6   23.9897        24    0.745057    0.560803
    2      16        34        18   35.9886        48    0.372282    0.938734
    3      16        45        29   38.6558        44     2.19349     1.17867
    4      16        54        38   37.9898        36     1.37898     1.21186
    5      16        63        47   37.5905        36    0.368202     1.26999
    6      16        73        57   37.9907        40    0.369987     1.34372
    7      16        84        68   38.8479        44    0.379556     1.35436
    8      15        92        77   38.4844        36    0.366431     1.35522
    9      16        98        82   36.4306        20    0.369742     1.38116
   10      16       108        92   36.7866        40     1.07875     1.40909
   11      16       119       103   37.4414        44    0.411923     1.42015
   12      16       128       112   37.3207        36    0.721847     1.46517
   13      15       136       121   37.2149        36     3.88744     1.51544
   14      16       145       129   36.8421        32     1.48207     1.53257
   15      16       153       137    36.519        32    0.374107     1.56824
   16      16       162       146   36.4861        36    0.369296     1.56676
   17      16       174       158   37.1627        48     0.73181     1.55813
   18      16       179       163   36.2091        20    0.402144     1.57222
   19      16       190       174   36.6186        44     0.37141     1.58182
2023-04-30T16:16:14.252493+0800 min lat: 0.366431 max lat: 5.00059 avg lat: 1.59628
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
   20      16       201       185   36.9871        44    0.707558     1.59628
   21      16       212       196   37.3204        44     0.72207     1.59639
   22      16       222       206   37.4418        40     4.26157     1.60271
   23      16       231       215   37.3786        36    0.863178     1.59685
   24      16       240       224   37.3208        36    0.703603     1.59669
   25      16       248       232   37.1078        32     3.21437       1.601
   26      16       260       244   37.5262        48    0.545021     1.58514
   27      16       269       253   37.4695        36     4.48831     1.59588
   28      16       277       261   37.2739        32    0.369147     1.59645
   29      16       287       271   37.3677        40    0.732066     1.60558
   30      16       295       279   37.1885        32    0.421207     1.61968
   31       8       295       287    37.021        32     4.43585     1.63341
   32       5       295       290   36.2391        12     4.24594     1.66179
   33       3       295       292   35.3834         8     3.91917     1.67774
Total time run:       33.7845
Total reads made:     295
Read size:            4194304
Object size:          4194304
Bandwidth (MB/sec):   34.9272
Average IOPS:         8
Stddev IOPS:          2.41248
Max IOPS:             12
Min IOPS:             2
Average Latency(s):   1.70153
Max latency(s):       5.00059
Min latency(s):       0.366431
```

## 卸载命令

```shell
apt remove ceph-* --purge -y
rm osd.img
rm -rf /var/lib/ceph/
rm -rf /usr/share/ceph
reboot
```

## B站视频

我在家用了一块512M内存的ARMv7板子、一块1G内存的ARM64板子和一块2G内存的AMD64的HTPC和一根2G内存的Intel电脑棒搭建了一个Ceph集群。其中HTPC作为mon,mgr,mds,osd，而其它三个设备作为osd。他们都是百兆网络。我的目的是为了学习Ceph集群的搭建，此外也对Ceph集群的性能比较感兴趣。因此我用了一块ARM64的板子（有千兆网络）作为客户端，挂载cephfs进行性能测试。除了cephfs，我还用rados进行了性能测试。我测试了两节点、三节点和四节点的情况下的性能并进行了对比。我的Ceph集群是双副本的。总的来说顺序读写随着节点越多，性能越好，但随机读写因节点数量太少，暂时看不出趋势。

<iframe style="height:360px;width:640px" src="//player.bilibili.com/player.html?aid=740669089&bvid=BV1Lk4y1E7LZ&cid=1115026484&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

## 视频文字稿

低配设备搭建Ceph集群，性能如何？(分布式存储)

上次我用家里的电子垃圾搭了一个k8s集群，这次我来搭一个Ceph集群。

Ceph是一个开源的分布式存储系统。我这次用了一块ARMv7的板子，只有512M内存，还有一块1G内存ARM64板子（树莓派3B），另外用了一根Intel的电脑棒和一台HTPC，都是2G内存的。官方文档里面建议内存最少4G，不过我搭这个集群只是图一乐。

我本来还想用256M内存的那块板子的，但是内存太小，经过优化还是跑不起来，所以只能放弃。

我是根据官方文档来手动部署的，我一开始用的比较旧的版本，然后遇到一堆坑，后面换了新版就正常了，虽然新版也是各种bug，但是不影响我测试。

我使用双副本配置，所有的存储节点都是百兆内网。我另外使用一个千兆内网的ARM64板子作为客户端，对集群进行性能测试。我首先挂载了cephfs。也就是基于Ceph的分布式文件系统。挂载之后，在上面读写，这些读写请求会分发到所有的存储节点上，所以理论上存储节点越多，读写速度就越快。

我分别对两节点、三节点和四节点的情况进行测试。首先挂载cephfs并用fio进行性能测试，结果如图，随机读写性能比较差，而且和节点数量关系不大，原因可能是存储节点的闪存比较垃圾。不过连续读写都随着节点数量增加而增加，在两节点和三节点的时候，连续读取基本能跑满存储节点带宽。另外我还用rados进行了性能测试，结果如图，都是随节点数量增加而增加，不过不是线性增长。

如果大家喜欢这期视频，欢迎点赞投币收藏转发，有什么想说也可以在评论区留言。
