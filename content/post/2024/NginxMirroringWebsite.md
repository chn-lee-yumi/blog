---
title: "通过Nginx镜像网站"
description: "通过Nginx镜像网站。使用 proxy_pass 和 proxy_set_header Host $proxy_host 实现网站镜像（反向代理）。"
date: 2024-01-15T22:35:00+11:00
lastmod: 2024-01-15T22:35:00+11:00
categories:
  - 学习
tags:
  - Nginx
---

## 前言

回想起很多年以前，国内有一些google的镜像站，当时就很好奇怎么实现的。多年以后，突然想起这件事，就试了一下。理论上可以镜像任何网站。

## Nginx配置

这里以镜像百度为例子。其实重点配置只有两个：`proxy_pass`和`proxy_set_header`。本质上就是反向代理。

```conf
server {
    listen 80;
    server_name example.com;
    location / {
        proxy_pass https://www.baidu.com;
        proxy_set_header Host $proxy_host;
    }
}
```

还有种骚操作，比如某个网站要登录，可以把登录后的cookie写进配置，然后加ip访问限制，再把网站分享给别人用。这样别人访问你的镜像网站的时候就默认是登录的。举个具体例子，我在海外，想分享ChatGPT给国内的朋友用，我就可以找一台外网的服务器，给chat.openai.com做镜像，同时把自己登录后的cookie写进去。这样朋友访问我的网站的时候就可以直接用ChatGPT了。

```conf
server {
    listen 80;
    server_name example.com;
    location / {
        allow 10.0.0.2;
        deny all;
        proxy_pass https://www.baidu.com;
        proxy_set_header Host $proxy_host;
        proxy_set_header Cookie "key1=value1; key2=value2";
    }
}
```
