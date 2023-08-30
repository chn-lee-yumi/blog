---
title: "FFmpeg转换m3u8视频的方法"
description: "FFmpeg转换m3u8视频的方法"
date: 2018-11-14T14:11:26+08:00
categories:
  - 折腾
tags:
  - FFmpeg
---

## 背景

最近需要从[荔枝网](http://www.gdtv.cn/)下载[视频](http://v.gdtv.cn/star/zbqq/2018-11-12/1728844.html)。通过F12看到视频文件是m3u8格式的，里面有很多个ts文件。

## 方法

比较笨的方法是把ts文件全部下载下来，然后再合并。但是FFmpeg可以转换m3u8文件，所以直接用一条FFMpeg命令即可。

```shell
ffmpeg.exe -i  http://vfile1.grtn.cn/2018/1542/0254/3368/154202543368.ssm/154202543368.m3u8 -c copy -bsf:a aac_adtstoasc -movflags +faststart output.mp4
```

其中`http://vfile1.grtn.cn/2018/1542/0254/3368/154202543368.ssm/154202543368.m3u8`为m3u8地址，`-c copy`表示拷贝流（无损）。

`-bsf:a aac_adtstoasc`参数介绍见：[FFmpeg官方文档对aac_adtstoasc的说明](https://blog.csdn.net/liuyl2016/article/details/53080733)

`-movflags +faststart`参数可以使得视频边下载边播放。

`output.mp4`为输出文件名。
