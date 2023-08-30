---
title: "使用SSH和Nginx做内网HTTP映射"
description: "使用SSH和Nginx做内网HTTP映射"
date: 2018-04-29T22:53:01+08:00
categories:
  - 折腾
tags:
  - Linux
  - Nginx
---

## 场景

我想把家里监控的80端口映射到我的VPS的80端口上，从而能够通过访问VPS来访问家里的监控。

路由器是极路由，已开启SSH。

监控IP为10.0.0.10，端口80。

VPS地址为hk.gcc.ac.cn。

## 步骤

- 极路由上操作，将VPS的2222端口转发到极路由的3333端口。

```shell
ssh -R 2222:localhost:3333 hk.gcc.ac.cn
```

- 在VPS上操作，将VPS的80端口转发到VPS的2222端口，且允许外部访问（-g参数）。

```shell
ssh -g -L 80:localhost:2222 localhost
```

- 极路由上操作，设置端口转发。外部端口3333，内部10.0.0.10:80。采用Nginx反向代理。（极路由自带Nginx）这里将下面的内容保存到`/etc/nginx/vh.jiankong.conf`。

```nginx
upstream jiankong  {
    server 10.0.0.10:80;
}

server {
    listen 3333;
    location / {
        proxy_pass http://jiankong;
    }
}
```

- 注：我尝试过使用iptables进行端口转发，但是内网能访问，转发出去却不能访问。

```shell
iptables -t nat -I PREROUTING -p tcp --dport 3333 -j DNAT --to 10.0.0.10:80
```