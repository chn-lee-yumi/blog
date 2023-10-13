---
title: "1TB内存的虚拟机"
description: "1TB内存的虚拟机。开了个几百G的SWAP，然后用kvm启动虚拟机。"
date: 2022-05-03T16:01:43+08:00
lastmod: 2023-05-08T01:09:17+08:00
categories:
  - 灌水
tags:
  - 虚拟化
  - B站视频
---

## 内容精华

开了个几百G的SWAP，然后用kvm启动虚拟机。

## B站视频

<iframe style="height:360px;width:640px" src="//player.bilibili.com/player.html?aid=613389493&bvid=BV1wh4y1n7vE&cid=1121983337&page=1&autoplay=0" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

## 视频文字稿

1 TB 的运行内存，你们看到了吗？1 TB！

这其实是一台安卓虚拟机，这 1 TB 内存【是假的，不是真的】。来跑个分吧。首先是安兔兔，立即测试。【一天后】，挂了一天还是 0%，估计有啥 bug，算了。点我的设备看看，可以看到运行内存和内置存储都是 1 TB。试试存储测试。也是跑不了。给大家浏览一下其他信息吧。接下来出场的是娱乐大师。直接就跪了，打都打不开。最后出场的是 Geekbench 5 。这个成功跑完了，单核656，多核4738。是什么水平呢？看一下排名。单核比小米 9T Pro 低一点。多核比第一名还要多一千多分。

这个视频我搞了几天，要个币不过分吧？

可能有人会好奇，这个1TB内存的虚拟机是怎么创建出来的。它的宿主是一台128G内存的服务器，大家可以看到CPU是志强E5-2630v4。然后我开了个几百G的SWAP，相当于Windows下的虚拟内存，然后就能给它分配1TB的内存了，并且成功地启动了起来。