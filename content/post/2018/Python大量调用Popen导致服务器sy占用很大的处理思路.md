---
title: "Python大量调用Popen导致服务器sy占用很大的处理思路"
description: "Python大量调用Popen导致服务器sy占用很大的处理思路"
date: 2018-08-16T23:28:05+08:00
categories:
  - 折腾
tags:
  - Linux
  - Python
---

## 背景介绍

- 我的代码是交换机监控系统，大约有27个线程，每个线程都会不断地使用`subprocess.Popen`去调用`snmpwalk`命令来收集交换机状态数据。
- 监控部署在一台树莓派2B上，CPU是4核1GHz。
- 现在收集数据速度不是很理想，因为交换机数量有700多台，大约6分钟才能刷新一次数据。当我想提高`snmpwalk`的并发量来提高收集速度的时候，我发现CPU是限制我的监控系统的瓶颈。
- 系统状态数据如下，我们可以看到，sy一项特别的大。
- 
|监控系统状态|us|sy|id|loadavg|snmpwalk平均进程数|python进程占用CPU|
|---|---|---|---|---|---|---|
|未启动|1.2|0.6|98|1.48|不存在|不存在|
|启动后|16|29|49|3.42|26|50%~70%|

- 今天面试腾讯运维开发的时候，和面试官讨论到这个问题，给了我一些启发，所以面完就马上试验一下我的想法。

## 分析与排查

- 我觉得可能的原因有：
  - 线程调度开销
  - Popen开销
  - snmpwalk开销
  - 进程调度开销
- 下面来逐个排查

 ### 线程调度开销

- 使用如下代码进行测试

```python
import threading
import time
import subprocess

def snmp(a):
    time.sleep(5)
    print(a)

for a in range(1,249):
    threading.Thread(target=snmp,args=(a,), name=a).start()
    print("Thread Start:",a)
```

- 测试结果：只有在创建线程的时候，us有明显升高，sy仅升高约2%创建完成后随即下降。
- 结论：sy升高与线程调度无关。

###  Popen开销

- 使用如下代码进行测试

```python
import threading
import time
import subprocess

def snmp(a):
    time.sleep(5)
    subprocess.Popen(["echo",str(a),], bufsize=0, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)

for a in range(1,101):
    threading.Thread(target=snmp,args=(a,), name=a).start()
    print("Thread Start:",a)
```

- 测试结果：到`subprocess.Popen`执行时，sy瞬间飙高，us约16%，sy约65%。
- 结论：sy升高与同时间大量使用Popen有关。

### snmpwalk开销

- 通过上面的代码，我们发现应该是Popen的开销，所以snmpwalk就不需要测试了。

### 进程调度开销

- 系统的平均负载小于CPU核心数，说明运行队列是有空余的，所以应该不是进程调度开销导致的。（对这方面不是很懂，我猜的，不知道对不对）

## 解决思路

-  先google一下Linux系统sys高的原因。[google链接](https://www.google.com/search?source=hp&ei=okd1W72NHIH4jwSZ9YRI&q=linux+sys+cpu+high&oq=linux+sys+&gs_l=psy-ab.1.3.0i12k1j0j0i12k1j0l3j0i12k1j0l2j0i10k1.1908.3030.0.6329.6.6.0.0.0.0.302.879.2-2j1.3.0....0...1c.1j4.64.psy-ab..3.3.874....0.UdOHRH8dc9U)
- 我找到这个：[高sys的CPU排查](https://huataihuang.gitbooks.io/cloud-atlas/os/linux/kernel/tracing/diagnose_high_sys_cpu.html)
- 我尝试使用`strace`来统计系统调用。对于上面的Popen开销测试代码，我先运行，然后在sleep(5)的时候迅速地把python的pid记下，运行strace命令，等python代码运行结束后，就会给出结果。这里的结果如下：

```shell
strace: Process 28984 attached
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
100.00    2.033028       16942       120        51 futex
  0.00    0.000000           0         6           close
  0.00    0.000000           0         1           brk
  0.00    0.000000           0         1           rt_sigaction
  0.00    0.000000           0         1           madvise
------ ----------- ----------- --------- --------- ----------------
100.00    2.033028                   129        51 total
```

- 我们可以看到，futex这项占了超多。
- 先不着急，我们再用同样的方法调试一下我的监控程序。运行了6分钟后终止，得到的结果如下：

```shell
strace: Process 29205 attached
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 99.92  374.189481       33959     11019      3144 futex
  0.02    0.082074           9      8745           pread64
  0.02    0.072160           7     11008           fcntl64
  0.02    0.058213           6      9592           fstat64
  0.01    0.030947           4      7494      5498 stat64
  0.00    0.012808         512        25           wait4
  0.00    0.009980         322        31           read
  0.00    0.007934          12       665           lstat64
  0.00    0.005470         260        21           _llseek
  0.00    0.001788          81        22           write
  0.00    0.001008           1      1338       666 open
  0.00    0.000507           9        57           mmap2
  0.00    0.000379           1       665           getcwd
  0.00    0.000300           0       666           getpid
  0.00    0.000282           0       729           close
  0.00    0.000000           0         7         7 ioctl
  0.00    0.000000           0         2           munmap
  0.00    0.000000           0         1         1 sigreturn
  0.00    0.000000           0        56           clone
  0.00    0.000000           0        56           mprotect
  0.00    0.000000           0         1           rt_sigaction
------ ----------- ----------- --------- --------- ----------------
100.00  374.473331                 52200      9316 total
```

- 很明显，是futex这项造成的，占了99.92%！
- 那futex是什么？我们用`man futex`看一下：

```text
       The  futex()  system call provides a method for waiting until a certain
       condition becomes true.  It is typically used as a  blocking  construct
       in  the  context of shared-memory synchronization.  When using futexes,
       the majority of the synchronization operations are  performed  in  user
       space.   A user-space program employs the futex() system call only when
       it is likely that the program has to block for a longer time until  the
       condition  becomes  true.  Other futex() operations can be used to wake
       any processes or threads waiting for a particular condition.
```

- 感觉是锁之类的东西，没啥头绪。
- 那就换个方向。既然是Popen导致的，那我不用Popen或者少用不就行了。今天面试腾讯运维开发的时候，面试官给了一个建议，把net-snmp的代码改了，让它可以一直运行不退出。我觉得ok，然后我下了net-snmp的源码，打算看看从哪下手，突然看到一个叫python的文件夹……！然后我点进去看了下，觉得不错，然后上网找了找资料，发现已经有人做好一个包了，用`pip3 install netsnmp-py3`进行安装。项目地址：https://github.com/xstaticxgpx/netsnmp-py3
- 安装完之后我就把调用snmp的代码修改了，现在一个Popen都没有，直接用函数来调用snmp。
- 我们来对比一下优化前后的结果。感觉不错，sy有明显的下降，同时扫描速度快了很多。

|数据|us|sy|id|loadavg|python占用CPU|扫描一栋楼所需时间|
|---|---|---|---|---|---|---|
|优化前|20|40|32|3.51|50%~90%|约6分5秒|
|优化后|14|9|74|1.09|70%|约3分23秒|

## 总结

- 我们的目的是降低sy的占用，现在目标已经达成了。
- 解决方法是尽量不调用Popen，在我这里，就是用`netsnmp-py3`提供的函数来代替Popen执行snmp命令。
- 后面的目标是，既然CPU使用率这么低，就想办法再加快数据的获取速度。
