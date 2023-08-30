---
title: "Win10远程桌面账号正确但连接失败的解决方法（使用微软AzureAD的账号）"
description: "Win10远程桌面账号正确但连接失败的解决方法（使用微软AzureAD的账号）：需要修改RDP文件，添加一行：enablecredsspsupport:i:0"
date: 2018-11-11T19:17:57+08:00
categories:
  - 折腾
tags:
  - Windows
---

百度到的那些改组策略之类的完全没用，花了一个小时左右，终于在谷歌找到了答案！

https://community.spiceworks.com/topic/2048258-logon-attempt-failed-via-remote-desktop-in-windows-10

https://superuser.com/questions/951330/windows-10-remote-desktop-connection-using-azure-ad-credentials

需要修改RDP文件。

添加这一行：`enablecredsspsupport:i:0`

关于RDP文件的选项可以看这里：https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/ff393716(v=ws.10)
