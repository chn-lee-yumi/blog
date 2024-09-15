---
title: "Azure Linux 服务器自动重启问题"
description: "Azure Linux 服务器自动重启问题排查。原因是 Azure 自动安装补丁重启服务器。"
date: 2024-09-15T23:15:00+10:00
lastmod: 2024-09-15T23:15:00+10:00
categories:
  - 折腾
---

# 问题描述

某日登录服务器发现我用`screen`挂起来的任务没了。看了下`uptime`发现系统启动时间不对，遂登录 Azure 查看虚拟机的 `Activity log`，发现：

```text
Install OS update patches on virtual machine | Succeeded | 23 hours ago
```

这条日志的时间刚好和服务器重启时间对上了。

于是进入 `Operation > Updates`，点击上方的 `Update settings`，发现 `Patch orchestration` 这一项选择了 `Azure Managed - Safe Deployment`。

把它改成 `Customer Managed Schedules` 应该就没事了。

感觉这种默认设置有很大问题，非常坑。
