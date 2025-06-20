---
title: "MacOS 使用移动硬盘备份微信聊天记录"
description: "本文介绍了如何在 MacOS 上使用移动硬盘备份微信聊天记录，避免占用大量本地硬盘空间。"
date: 2025-06-20T16:01:00+10:00
categories:
  - 折腾
tags:
  - 微信
---

微信的聊天记录有多大，大家懂得都懂。我的 18 版 MacBook Pro 只有 256GB 的硬盘，实在没什么位置放微信的聊天记录。所以只能想办法用移动硬盘进行备份。

最简单的办法是先备份到 Mac，然后把备份目录复制到移动硬盘，再删除本机的备份。但是如果想增量备份的话，又得复制回去。

不过我们可以用软链接来解决这个问题。

目前的微信备份目录在 `~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/Backup` 下。我直接用`ln -s`把移动硬盘的备份目录链接到这个目录下。这样就基本完成了。

但是因为 MacOS 的沙盒机制，App 不能直接访问移动硬盘的目录，所以需要在终端中执行以下命令来允许微信访问移动硬盘：

```bash
sudo codesign --sign - --force --deep /Applications/WeChat.app
```

命令参数解释：

| 参数                         | 作用                                                   |
| -------------------------- | ---------------------------------------------------- |
| `codesign`                 | macOS 自带的工具，用于给应用、可执行文件等 **签名（Code Signing）**        |
| `--sign -`                 | 使用 `-` 表示**用临时自签名（ad-hoc 签名）**，不会使用有效证书，仅用于绕过验证或开发测试 |
| `--force`                  | 强制重签名，即使目标已经签名也会覆盖                                   |
| `--deep`                   | 深度签名，**连带签名**应用中的嵌套组件（如内部的 .framework、.dylib 等）      |
| `/Applications/WeChat.app` | 目标应用，即 **微信** 应用程序路径                                 |

执行完后，打开微信，会提示需要访问外置硬盘，点击允许，就可以正常备份了。

重新签名之后，发现了别的bug，就是微信就无法截图了。不过问题不大，可以用 MacOS 自带的截图快捷键：

- 全屏截取：`Command + Shift + 3`
- 框选截图：`Command + Shift + 4`
