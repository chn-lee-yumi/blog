---
title: "Setonix 的 PyTorch 环境的 ROCm 报错排查"
description: "Setonix is a hybrid CPU-GPU supercomputer housed at Pawsey Centre in Western Australia. 本文是关于 Setonix 的 PyTorch 环境的 ROCm 报错排查记录。"
date: 2024-07-12T19:55:00+10:00
lastmod: 2024-07-12T21:55:00+10:00
categories:
  - 学习
tags:
  - Linux
  - HPC
---

## 前言

Setonix 是南半球最强大的超级计算机，也是我用过的最不稳定的超级计算机。平均一个月炸一次，例如升级固件升炸了，Lustre文件系统炸了等等……

因为是用 AMD Instinct MI250X GPU，所以 PyTorch 后端用的是 ROCm。这个环境有就各种奇奇怪怪的问题。

**建议炼丹远离A卡。A卡炼丹，毁我青春！**

## PyTorch环境装不了包

First, load the module and create a virtual environment:

```bash
module load pytorch/2.2.0-rocm5.7.3
python3 -m venv venv
```

Now in the current directory, there will be a `venv` directory. Go to `venv/bin` and execute `ls -l` , we can see the `python3` is linked to the wrong file:

```text
liyumin@setonix-05:~/software/venv/bin> ls -lh
total 36K
-rw-r--r-- 1 liyumin pawsey1001 2.0K  3月 17 12:02 activate
-rw-r--r-- 1 liyumin pawsey1001  935  3月 17 12:02 activate.csh
-rw-r--r-- 1 liyumin pawsey1001 2.2K  3月 17 12:02 activate.fish
-rw-r--r-- 1 liyumin pawsey1001 8.9K  3月 17 12:02 Activate.ps1
-rwxr-xr-x 1 liyumin pawsey1001  305  3月 17 12:08 pip
-rwxr-xr-x 1 liyumin pawsey1001  305  3月 17 12:08 pip3
lrwxrwxrwx 1 liyumin pawsey1001    7  3月 17 12:03 python -> python3
lrwxrwxrwx 1 liyumin pawsey1001  100  3月 17 12:03 python3 -> /usr/bin/python3
lrwxrwxrwx 1 liyumin pawsey1001  100  3月 17 12:03 python3.10 -> python3
```

Use the commands below to fix this:

```bash
rm python3
ln -s /software/setonix/2023.08/containers/modules-long/quay.io/pawsey/pytorch/2.2.0-rocm5.7.3/bin/python3 python3
```

Now it is corrected:

```text
total 36K
-rw-r--r-- 1 liyumin pawsey1001 2.0K  3月 17 12:02 activate
-rw-r--r-- 1 liyumin pawsey1001  935  3月 17 12:02 activate.csh
-rw-r--r-- 1 liyumin pawsey1001 2.2K  3月 17 12:02 activate.fish
-rw-r--r-- 1 liyumin pawsey1001 8.9K  3月 17 12:02 Activate.ps1
-rwxr-xr-x 1 liyumin pawsey1001  305  3月 17 12:08 pip
-rwxr-xr-x 1 liyumin pawsey1001  305  3月 17 12:08 pip3
lrwxrwxrwx 1 liyumin pawsey1001    7  3月 17 12:03 python -> python3
lrwxrwxrwx 1 liyumin pawsey1001  100  3月 17 12:03 python3 -> /software/setonix/2023.08/containers/modules-long/quay.io/pawsey/pytorch/2.2.0-rocm5.7.3/bin/python3
lrwxrwxrwx 1 liyumin pawsey1001  100  3月 17 12:03 python3.10 -> python3
```

The pip in this environment is missing, we have to install it:

```bash
source ./activate
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

Then we can install Jupyter lab and other packages:

```bash
pip install jupyterlab
```

If the home partition quota is full, we have to move our `.local` directory to software partition:

```bash
mv ~/.local /software/projects/pawsey1001/`whoami`/.local/
ln -s /software/projects/pawsey1001/`whoami`/.local/ ~/.local
```

After installing Jupyter, we should add it to `PATH`, put the below line into `~/.bashrc`:

```bash
export PATH=$PATH:~/.local/bin
```

Jupyter is not working now, we still have something to do:
```text
File "/home/liyumin/.local/bin/jupyter", line 5, in <module>
  from jupyter_core.command import main
ModuleNotFoundError: No mudule named 'jupyter_core'
```

Open `~/.local/bin/jupyter` with any file editor, and modify the **first line**, change the python path to your virtual environment python path, like this:

```python
#!/software/projects/pawsey1001/liyumin/venv/bin/python3
# -*- coding: utf-8 -*-
import re
import sys
from jupyter_core.command import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
```

Now `jupyter lab` is working.

Here's my batch script, save it into `batch_script`:

```bash
#!/bin/bash -l
# Allocate slurm resources, edit as necessary
#SBATCH --account=pawsey1001-gpu
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --time=12:00:00
#SBATCH --job-name=jupyter_notebook

# Get the hostname
# We'll set up an SSH tunnel to connect to the Juypter notebook server
host=$(hostname)

# Set the port for the SSH tunnel
# This part of the script uses a loop to search for available ports on the node;
# this will allow multiple instances of GUI servers to be run from the same host node
port="8888"
pfound="0"
while [ $port -lt 65535 ] ; do
  check=$( ss -tuna | awk '{print $4}' | grep ":$port *" )
  if [ "$check" == "" ] ; then
    pfound="1"
    break
  fi
  : $((++port))
done
if [ $pfound -eq 0 ] ; then
  echo "No available communication port found to establish the SSH tunnel."
  echo "Try again later. Exiting."
  exit
fi

echo "*****************************************************"
echo "Setup - from your laptop do:"
echo "ssh -L ${port}:${host}:${port} $USER@$PAWSEY_CLUSTER.pawsey.org.au"
echo "*****"
echo "The launch directory is: $dir"
echo "*****************************************************"
echo ""

#Launch the notebook
export OMP_NUM_THREADS=1
module load pytorch/2.2.0-rocm5.7.3
source /home/liyumin/software/venv/bin/activate

srun -N 1 -n 1 -c 8 --gres=gpu:1 --gpus-per-task=1 --gpu-bind=closest jupyter lab \
  --no-browser \
  --port=${port} --ip=0.0.0.0 \
  --notebook-dir=${dir}
```

Remember to change the virtual environment path to your own: `/home/liyumin/software/venv/bin/activate`

And submit the task: `sbatch batch_script`

Wait until the task status is running: `squeue --me`

Then we will have a file like `slurm-{task_id}.out`

There will be information in this file:

```text
*****************************************************
Setup - from your laptop do:
ssh -L 8888:nid002240:8888 liyumin@setonix.pawsey.org.au
*****
The launch directory is: 
*****************************************************

[I 2024-04-07 22:55:07.485 ServerApp] jupyter_lsp | extension was successfully linked.
[I 2024-04-07 22:55:07.488 ServerApp] jupyter_server_terminals | extension was successfully linked.
[I 2024-04-07 22:55:07.492 ServerApp] jupyterlab | extension was successfully linked.
[I 2024-04-07 22:55:07.844 ServerApp] notebook_shim | extension was successfully linked.
[I 2024-04-07 22:55:07.942 ServerApp] notebook_shim | extension was successfully loaded.
[I 2024-04-07 22:55:07.944 ServerApp] jupyter_lsp | extension was successfully loaded.
[I 2024-04-07 22:55:07.946 ServerApp] jupyter_server_terminals | extension was successfully loaded.
[I 2024-04-07 22:55:07.954 LabApp] JupyterLab extension loaded from /home/liyumin/.local/lib/python3.10/site-packages/jupyterlab
[I 2024-04-07 22:55:07.954 LabApp] JupyterLab application directory is /software/projects/pawsey1001/liyumin/.local/share/jupyter/lab
[I 2024-04-07 22:55:07.955 LabApp] Extension Manager is 'pypi'.
[I 2024-04-07 22:55:08.001 ServerApp] jupyterlab | extension was successfully loaded.
[I 2024-04-07 22:55:08.001 ServerApp] Serving notebooks from local directory: 
[I 2024-04-07 22:55:08.001 ServerApp] Jupyter Server 2.13.0 is running at:
[I 2024-04-07 22:55:08.001 ServerApp] http://nid002240:8888/lab?token=d8a8b968d5b8a8af2cc4f5adb42674d2368bcb9fd657c370
[I 2024-04-07 22:55:08.001 ServerApp]     http://127.0.0.1:8888/lab?token=d8a8b968d5b8a8af2cc4f5adb42674d2368bcb9fd657c370
[I 2024-04-07 22:55:08.001 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[C 2024-04-07 22:55:08.008 ServerApp] 
    
    To access the server, open this file in a browser:
        file:///home/liyumin/.local/share/jupyter/runtime/jpserver-67643-open.html
    Or copy and paste one of these URLs:
        http://nid002240:8888/lab?token=d8a8b968d5b8a8af2cc4f5adb42674d2368bcb9fd657c370
        http://127.0.0.1:8888/lab?token=d8a8b968d5b8a8af2cc4f5adb42674d2368bcb9fd657c370
```

Run that `ssh -L` command in your local machine and open the link in the browser: http://127.0.0.1:8888/lab?token=xxxxxx

We are all done!

To cancel the task, use `scancel {task_id}` or `File > Shut Down` in Jupyter Lab to stop consuming the SUs.

你问我为什么是英文？因为这是其实是我发给别人的邮件内容，写的时候是英文写的。懒得翻译了。

## 一跑模型就报错

```text
MIOpen Error: /long_pathname_so_that_rpms_can_package_the_debug_info/src/extlibs/ML
Open /src/include/miopen/kern_db.hpp:180: Internal error while accessing SQLite database: attempt to write a readonly database
Traceback (most recent call last):
  ...
RuntimeError: miopenStatusInternalError
```

网上搜不到解决办法。提工单也不回复，无语了，只能自己解决。

随便试了下，发现换一台机器有概率可以解决。经排查，只有部分机器有这个问题，所以我把它归咎于环境问题。

我们在执行`sbatch`命令的时候，可以通过`--exclude`参数把有问题的节点去掉：

```text
sbatch --exclude=nid00[2056,2112,2826,2860,2868,2872,2928,2930,2932,2942,2946,2948,2984,2986,2988,2990,2994,3000] batch_script
```

## N卡正常，A卡莫名其妙 Loss NaN

我在测试某个开源模型，在我加了一个`nn.Linear`后，模型的 Loss 直接炸了，变成了`NaN`。

同样的代码在N卡下运行正常。

经过仔细排查，手动设置这一层的权重，并打印出数值进行手动计算比较，发现这玩意儿居然能算错数。也就是说数据经过了这个`nn.Linear`之后，得到的数值和理论值不一致。

尝试减少 `lr` 和 `batch_size`，发现当 `batch_size <= 2` 的时候得出来的数值是正确的。

百思不解，后来发现他们的代码开启了 AMP。然后我试了下把 AMP 关掉，结果就正常了。

虽然A卡支持 AMP，但是我也不知道为什么会有这种玄学问题。以后用A卡都不敢开 AMP 了。
