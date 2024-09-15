---
title: "神经网络训练一开始准确率很高然后逐渐下降的问题排查"
description: "神经网络训练，一开始准确率很高，然后逐渐下降。一个很神奇的现象的排查。最后发现原因是没有设置shuffle=True。"
date: 2024-08-18T22:02:00+10:00
lastmod: 2024-08-18T22:02:00+10:00
categories:
  - 学习
tags:
  - AI
---

## 现象

神经网络训练，一开始准确率很高，然后逐渐下降。如下所示：

```text
Epoch 	 Time 	 Train Loss 	 Train ACC 	 Val Loss 	 Val ACC 	 Test Loss 	 Test ACC 	 LR
1	 197.8234 	 0.0053 	 0.8645 	 0.0412 	 0.1443 	 0.0412 	 0.1443 	 0.0100
2	 108.6638 	 0.0084 	 0.7311 	 0.0272 	 0.1443 	 0.0272 	 0.1443 	 0.0100
3	 108.4892 	 0.0095 	 0.6777 	 0.0267 	 0.1443 	 0.0267 	 0.1443 	 0.0100
4	 108.8819 	 0.0087 	 0.7102 	 0.0269 	 0.1443 	 0.0269 	 0.1443 	 0.0100
5	 108.8337 	 0.0065 	 0.7712 	 0.0504 	 0.1443 	 0.0504 	 0.1443 	 0.0100
6	 109.4179 	 0.0061 	 0.8071 	 0.0624 	 0.1443 	 0.0624 	 0.1443 	 0.0100
7	 109.2300 	 0.0057 	 0.8349 	 0.0762 	 0.1443 	 0.0762 	 0.1443 	 0.0075
8	 109.2820 	 0.0101 	 0.6432 	 0.0245 	 0.1443 	 0.0245 	 0.1443 	 0.0075
```

具体现象是 Train ACC 一开始特别高，但 Val ACC 很低。随着 epoch 增加， Train ACC 开始下降，Val ACC 几乎不变。

## 排查过程

把 Argumentation 部分的代码删了，发现还是这样。我是用分布式训练，所以我把进程数量改成了1再试，发现还是这样。

最后掏出了积灰的单机训练代码，逐部分调试，最后发现原因是 Dataloader 的 `shuffle=False`。开启 shuffle 后，数据就正常了。

为啥之前不开 shuffle 呢，我也忘了……分布式训练时可以在`DistributedSampler`可以设置`shuffle=False`。代码如下所示：

```python
trainsampler = DistributedSampler(train, shuffle=True)
trainloader = DataLoader(train, batch_size=128, num_workers=6, sampler=trainsampler)
```

