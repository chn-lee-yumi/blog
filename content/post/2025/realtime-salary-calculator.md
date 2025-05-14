---
title: "使用AI开发一个实时工资计算器"
description: "使用AI一分钟开发一个实时工资计算器/实时收入计算器。实时显示当前收入。输入时薪和工作时长，点击开始计时，画面会显示当前已赚工资。"
date: 2025-05-14T10:37:00+10:00
categories:
  - 折腾
tags:
  - AI
---

## 背景

为什么做这个项目呢？这是偶然间看到的一个idea，但是网上没找到相关的实现。于是我就想自己实现一个，反正写个prompt就搞定了。

三月十四日做的项目，还水了一个B站视频（[我用AI做了一个每秒工资计算器，实时显示每秒工资，看看摸鱼赚了多少钱？！](https://www.bilibili.com/video/BV197QPYBEjn/)）。

实测Claude效果最好，聊天内容[点击这里](https://claude.ai/chat/f520af3c-6248-4d4b-9fc2-829e13546c1b)查看。

ChatGPT、Deepseek、Gemini的效果感觉都有点烂。

源码放到了[GitHub](https://github.com/chn-lee-yumi/salary_calculator/tree/main)。网页部署在[salary.gcc.ac.cn](https://salary.gcc.ac.cn/)，浏览器打开就能用。

五一之后不知道为什么突然火了，可能因为长假结束大家都不想上班。现在大家都在做这种工具，同类网站满天飞。所以写个博客吧。

## Prompt

只要把下面的prompt复制粘贴到LLM里就可以了，例如DeepSeek。

```text
我想做一个实时显示当前已赚工资的网站（要求用单个html页面实现）。

用户交互过程：
1. 输入时薪和工作时长
2. 点击开始计时
3. 画面显示当前已赚工资，这个数值应该不断上涨，画面下面还有进度条、时长、每秒收入等数据

要求：
1. 收入每满100元天上撒金币
2. 画面流畅，数字更新流畅
3. 页面非常绚丽，加入很多特效
4. 注意性能优化，不能跑满cpu
5. 输出一个html文件
```

## B站视频

<div style="max-width: 100%; aspect-ratio: 16 / 9;">
    <iframe style="width: 100%; height: 100%; border: 0;" src="//player.bilibili.com/player.html?isOutside=true&aid=114155717724423&bvid=BV197QPYBEjn&cid=28848947542&p=1&autoplay=0" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>
</div>