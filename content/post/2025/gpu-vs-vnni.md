---
title: "GPU vs VNNI 性能简单对比"
description: "NVIDIA GPU 和 Intel Xeon Gold 5318Y 使用 VNNI 指令集跑模型的性能对比。"
date: 2025-06-14T12:14:00+10:00
categories:
  - 折腾
tags:
  - AI
---

## 背景

最近在研究模型量化，手上有一台 Intel Xeon Gold 5318Y x 2 的服务器。Xeon Gold 5318Y 支持 VNNI 指令集。看看现在的 CPU 和 GPU 性能差距怎么样。

## 测试环境

我用了 Stable Diffusion 1.5 模型来进行测试。代码如下：

### GPU

```python
from diffusers import StableDiffusionPipeline
import torch

model_id = "sd-legacy/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

prompt = "a photo of an astronaut riding a horse on mars"
image = pipe(prompt).images[0] 
```

### CPU

```python
from optimum.intel.openvino import OVDiffusionPipeline

model_id = "OpenVINO/stable-diffusion-v1-5-int8-ov"
pipeline = OVDiffusionPipeline.from_pretrained(model_id)

prompt = "sailing ship in storm by Rembrandt"
images = pipeline(prompt, num_inference_steps=20).images
```

## 测试结果

CPU 用了 int8 量化，实际计算应该是使用 VNNI 指令集进行加速，GPU 用了 float16。

两颗 5318Y CPU 速度是 2.08s/it。K80 GPU 速度是 1.44s/it。GTX 2080 Ti 速度是 3.60it/s （注意单位 s/it 和 it/s）。

以 CPU 为基准，K80 的速度大概是 CPU 的 2.08 / 1.44 = 1.44 倍，GTX 2080 Ti 的速度大概是 CPU 的 3.60 * 2.08 = 7.49 倍。

感觉现在的 CPU 直接跑量化模型，性能还是可以的。虽然不算快，但是速度还算可以接受，已经接近十年前的 GPU 水平了。不过如果最新的 GPU 比（支持 float8 的），还是会被完爆。