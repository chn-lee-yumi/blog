---
title: "Linux SWAP小技巧 - ZRAM"
description: "通过把 SWAP 放在 ZRAM 上来提高 SWAP 性能。"
date: 2023-05-22T12:21:12+08:00
categories:
  - 灌水
tags:
  - Linux
  - B站视频
---

## 内容精华

ZRAM 也就是压缩内存，速度比磁盘快很多。通过把 SWAP 放在 ZRAM 上来提高 SWAP 性能。

内存压缩率参考：在我的NAS上，我跑了很多的容器，还有一个神经网络模型。我在上面创建了一个4G的ZRAM用来做交换分区，并且已经全部用满了，这个时候它消耗了1.4G的物理内存，压缩率为0.35。

```shell
NAME       ALGORITHM DISKSIZE DATA COMPR TOTAL STREAMS MOUNTPOINT
/dev/zram0 lz4             4G   4G  1.3G  1.4G       4 [SWAP]
```

用`zramctl`命令来进行 ZRAM 的配置。


实现压缩的线程：`kworker/u8:1+flush-252:2`，其中`252:2`是设备号。

注意：每 GB ZRAM 需要另外消耗 6MB 内存（1TB ZRAM 消耗 6G内存，理论上你内存够可以开这么大，不过纯属娱乐了）

水了一期视频，练练英语口语。（所以这篇文章分类为`灌水`）

## B站视频

视频备选标题：
- 【Linux】内存无中生有？免费给系统增加内存！
- 内存无中生有？免费给系统增加内存！
- 【Linux】零成本内存翻倍！NAS神器！

免费给系统增加内存！你没听错，不用花一分钱，就能扩容内存！

有些人可能就会想到，我想说的是交换分区吗？是，但又不完全是。

<iframe style="height:360px;width:640px" src="//player.bilibili.com/player.html?aid=953940482&bvid=BV1Ls4y1u7ky&cid=1137867780&page=1&autoplay=0" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

## 视频文字稿

免费给系统增加内存！你没听错，不用花一分钱，就能扩容内存！

Free memory expansion for your system! You heard it right, you can expand your memory without spending a penny.

有些人可能就会想到，我想说的是交换分区吗？是，但又不完全是。首先让我来给没基础的人解释一下什么是交换分区。

Some people may think I'm referring to swap space, and yes, but not entirely. Let me explain to those without a basic understanding of what swap space is.

交换分区（又叫交换空间，Swap space）会在物理内存接近满的时候被使用。如果系统需要更多内存，比如你在Chrome浏览器里面又打开了一个新的网页，但此时物理内存已经满了，那么物理内存中不活跃的那些部分将会被移动到交换空间（比如某个你打开后一直不看的网页）。物理内存和交换空间的大小总和，就是操作系统可以使用的虚拟内存大小。所以，使用交换空间确实是相当于增加了系统的内存。

Swap space is used when physical memory becomes nearly full. If the system requires more memory, such as opening a new webpage in Chrome browser, but the physical memory is already full, the inactive parts of physical memory (such as a webpage that hasn't been viewed) will be moved to swap space. The total size of physical memory and swap space is the virtual memory size that the operating system can use. Therefore, using swap space is equivalent to increasing the system's memory.

但是，一般来说，我们的交换空间都放在硬盘上，在触发内存交换的时候，因为硬盘读写速度远远不及内存，系统就会变得很慢，同时因为内存交换使用了大量的I/O，导致硬盘响应时间变长，你会觉得电脑变得很卡。

However, typically our swap space is located on a hard disk. When memory swapping occurs, the system becomes slow because the speed of hard disk reading and writing is far lower than that of memory. Additionally, since memory swapping uses a lot of I/O, it causes longer hard disk response times, making the computer feel sluggish.

所以，有没有什么办法可以既增加内存，又不让电脑变得非常卡呢？这就是我这个视频想说的内容。

So, is there a way to increase memory without slowing down the computer? That's what this video is all about.

确实是有的，而且这种方法已经应用在了很多设备上了，比如路由器、树莓派、香橙派、NanoPi，以及手机。这种技术叫做ZRAM，也就是压缩内存。在Linux下面，我们可以创建一块压缩内存，并且把它当成硬盘一样使用。即使是压缩内存，它的读写速度和延迟也比硬盘好很多很多。我们可以把交换空间放在压缩内存上面。

Indeed, there is, and this method has already been applied to many devices, such as routers, Raspberry Pi, Orange Pi, NanoPi, and even smartphones. This technology is called ZRAM, which means compressed memory. Under Linux, one can create a block of compressed memory and use it like a hard disk. Even though it is compressed memory, its read/write speed and latency are much better than that of a hard disk. We can place the swap space in the compressed memory.

这里我们做个简单的测试，用fio工具来测试内存盘、压缩内存、硬盘的读写速度。

Here, we perform a simple test using the fio tool to test the read/write speed of memory disks, compressed memory, and hard disks.

速度最高的是tmpfs，也就是内存盘的速度，然后是压缩内存的速度，比内存盘低了一些。最低的是硬盘的速度。可以看到，压缩内存全面碾压硬盘。

The fastest speed is tmpfs, which is the speed of memory disk, followed by the speed of compressed memory, which is slightly slower than that of memory disk. The slowest speed is hard disk. As we can see, compressed memory crushes hard disk in every aspect.

通过压缩内存和交换空间的组合使用，我们可以达到在增加内存的同时，节省硬盘空间，延长硬盘寿命。在触发内存交换的时候，因为压缩内存速度非常快，所以系统不会变得很卡。

By using a combination of compressed memory and swap space, we can increase memory while saving hard disk space and extending hard disk life. When memory swapping is triggered, because the speed of compressed memory is extremely fast, the system won't become sluggish.

当然ZRAM也是有代价的，那就是需要消耗CPU来对内存进行压缩，不过在我看来，这个代价可以忽略不计，因为这个消耗真的很小。ZRAM也不是万能的，它有大小限制。如果你用硬盘做交换空间，硬盘有多大，你的交换空间就能设置多大。但是如果把交换空间设置在ZRAM上，交换空间的大小将取决于物理内存的大小和压缩率。理想的极限情况下，ZRAM压缩后占用的空间不能超过物理内存大小。压缩率会随着压缩算法和具体的内存数据而变化。我可以给个参考，在我的NAS上，我跑了很多的容器，还有一个神经网络模型。我在上面创建了一个4G的ZRAM用来做交换分区，并且已经全部用满了，这个时候它消耗了1.4G的物理内存，压缩率为0.35。

Of course, there is a cost to ZRAM, which is the need to consume CPU to compress memory. However, in my opinion, the cost can be ignored because it is really small. ZRAM is not omnipotent; it has a size limit. If you use a hard disk as swap space, the size of swap space depends on the size of the hard disk. But if you set the swap space on ZRAM, the size of the swap space will depend on the physical memory size and compression ratio. In the ideal extreme case, the space occupied after ZRAM compression cannot exceed the physical memory size. The compression ratio will vary with different compression algorithms and specific memory data. As a reference, I've run multiple containers and a neural network model on my NAS. I created a 4G ZRAM for swap space and have used it all up. At this point, it consumes 1.4G of physical memory, and the compression ratio is 0.35.

最后我来介绍一下如何手动创建ZRAM并且用它来做交换分区吧。

Finally, let me introduce how to manually create ZRAM and use it for swap space.

首先加载ZRAM内核模块，然后用zramctl这个命令来创建一个压缩内存设备，这里我给它分配了4G。现在用zramctl命令看一下，可以看到现在我们有一个叫/dev/zram0的设备，容量是4G。接着我们用mkswap来创建交换分区，然后用swapon来启用它。最后执行free命令看看，我们成功地增加了4G的内存！

Firstly, load the ZRAM kernel module, then use the zramctl command to create a compressed memory device. Here, I allocated 4G. Now use the zramctl command to check; we can see that we now have a device named /dev/zram0 with a capacity of 4G. Then use mkswap to create swap space and use swapon to enable it. Finally, execute the free command to see that we have successfully added 4G of memory!

以上就是这个视频的全部内容，如果你喜欢这个视频，求三连和转发，有什么想说的也欢迎弹幕或评论区留言。

That's all the content of this video. If you have any questions, feel free to leave your comment.
