---
title: "在超级计算机中通过Singularity运行容器"
description: "由于超级计算机的用户难以安装软件，因此使用Singularity运行容器是一个很好的解决方案。"
date: 2025-04-20T21:45:00+10:00
lastmod: 2025-04-20T21:45:00+10:00
categories:
  - 学习
tags:
  - Linux
  - HPC
---

## 前言

之前 DeepSeek 爆火，我就想看看能不能直接在超算（[Setonix](https://pawsey.org.au/systems/setonix/)）上跑一个满血版。DeepSeek 官方推荐了好几种部署方式。但是超算嘛，软件是很难装的，只能用已经有的模块，不过幸好超算其实也能跑容器。经过多番测试（吐槽一句：[SGLang 的 Docker 镜像居然缺依赖，不是开箱即用的](https://github.com/sgl-project/sglang/issues/4630)），最后决定使用 [AMD 打包的 vLLM Docker 镜像](https://hub.docker.com/r/rocm/vllm/tags)（因为 GPU 是 MI250X）。这篇文章主要是记录一下命令，方便后面忘了回来复习。最后的结果就是，还是没跑成功，因为 DeepSeek 满血版是 8bit 量化，但是 MI250X 不支持。需要 MI300 系列显卡才行。也可以下载转换成 16bit 的模型，不过得用4个节点才能跑起来。以后有机会再折腾。

## 操作步骤

加载 Singularity 模块：

```bash
module load singularity
```

拉取 Docker 镜像：

```bash
singularity pull docker://rocm/vllm:rocm6.3.1_instinct_vllm0.8.3_20250410
```

拉去完后会在当前目录下生成一个`.sif`文件。

运行容器：

```bash
singularity shell vllm_rocm6.3.1_instinct_vllm0.8.3_20250410.sif
```