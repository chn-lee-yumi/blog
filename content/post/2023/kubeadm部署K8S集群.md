---
title: "kubeadm部署K8S集群"
description: "kubeadm+CRI-O部署K8S集群"
date: 2023-09-05T00:59:00+10:00
lastmod: 2023-11-16T18:22:00+10:00
categories:
  - 学习
tags:
  - Linux
  - K8S
---

## 安装CRI-O

这里用1.28版本。可以通过`export VERSION=1.28`修改。

### Ubuntu Jammy 22.04

```shell
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 4D64390375060AA4
export OS=xUbuntu_22.04
export VERSION=1.28
rm /usr/share/keyrings/libcontainers-archive-keyring.gpg
rm /usr/share/keyrings/libcontainers-crio-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/libcontainers-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/ /" > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
echo "deb [signed-by=/usr/share/keyrings/libcontainers-crio-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$VERSION/$OS/ /" > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable:cri-o:$VERSION.list

mkdir -p /usr/share/keyrings
curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/Release.key | gpg --dearmor -o /usr/share/keyrings/libcontainers-archive-keyring.gpg
curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$VERSION/$OS/Release.key | gpg --dearmor -o /usr/share/keyrings/libcontainers-crio-archive-keyring.gpg

apt-get update
apt-get install -y cri-o cri-o-runc containernetworking-plugins

systemctl enable crio
systemctl start crio
systemctl status crio
```

### CentOS 7

```shell
export OS=CentOS_7
export VERSION=1.28

curl -L -o /etc/yum.repos.d/devel:kubic:libcontainers:stable.repo https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/devel:kubic:libcontainers:stable.repo
curl -L -o /etc/yum.repos.d/devel:kubic:libcontainers:stable:cri-o:$VERSION.repo https://download.opensuse.org/repositories/devel:kubic:libcontainers:stable:cri-o:$VERSION/$OS/devel:kubic:libcontainers:stable:cri-o:$VERSION.repo
yum install -y cri-o containernetworking-plugins

systemctl enable crio
systemctl start crio
systemctl status crio
```

## 配置CRI-O

```shell
mkdir /var/lib/crio
mkdir /home/crio
cat << EOF | sudo tee /etc/crio/crio.conf
[crio]
root = "/home/crio"
[crio.api]

[crio.runtime]

[crio.image]
pause_image = "registry.aliyuncs.com/google_containers/pause:3.9"
[crio.network]

[crio.metrics]

[crio.tracing]

[crio.nri]

[crio.stats]

EOF
systemctl restart crio
```

## 配置CNI

注意这里`subnet`要改。

```shell
mkdir /etc/cni/net.d
cat << EOF | sudo tee /etc/cni/net.d/100-crio-bridge.conflist
{
  "cniVersion": "1.0.0",
  "name": "crio",
  "plugins": [
    {
      "type": "bridge",
      "mtu": 1420,
      "bridge": "cni0",
      "isGateway": true,
      "ipMasq": true,
      "hairpinMode": true,
      "ipam": {
        "type": "host-local",
        "routes": [
            { "dst": "0.0.0.0/0" }
        ],
        "ranges": [
            [{ "subnet": "10.9.10.0/24" }]
        ]
      }
    }
  ]
}
EOF
```

## 安装kubeadm/kubectl/kubelet

### Ubuntu

这里用1.26版本。

```shell
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.26/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.26/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
apt-get update
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl
```

### CentOS

这里默认最新版本，如果想指定版本，则修改yum命令，如：`yum install kubelet-1.26.8-0  kubeadm-1.26.8-0 kubectl-1.26.8-0 -y`。

```shell
setenforce 0
sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
enabled=1
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF
yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
systemctl enable --now kubelet
```

## 配置kubelet

注意修改`--node-ip`。

```shell
cat << EOF | sudo tee /usr/lib/systemd/system/kubelet.service.d/10-kubeadm.conf
# Note: This dropin only works with kubeadm and kubelet v1.11+
[Service]
Environment="KUBELET_KUBECONFIG_ARGS=--bootstrap-kubeconfig=/etc/kubernetes/bootstrap-kubelet.conf --kubeconfig=/etc/kubernetes/kubelet.conf"
Environment="KUBELET_CONFIG_ARGS=--config=/var/lib/kubelet/config.yaml"
# This is a file that "kubeadm init" and "kubeadm join" generates at runtime, populating the KUBELET_KUBEADM_ARGS variable dynamically
EnvironmentFile=-/var/lib/kubelet/kubeadm-flags.env
# This is a file that the user can use for overrides of the kubelet args as a last resort. Preferably, the user should use
# the .NodeRegistration.KubeletExtraArgs object in the configuration files instead. KUBELET_EXTRA_ARGS should be sourced from this file.
EnvironmentFile=-/etc/sysconfig/kubelet
ExecStart=
ExecStart=/usr/bin/kubelet $KUBELET_KUBECONFIG_ARGS $KUBELET_CONFIG_ARGS $KUBELET_KUBEADM_ARGS $KUBELET_EXTRA_ARGS
EOF
cat << EOF | sudo tee /etc/sysconfig/kubelet
KUBELET_EXTRA_ARGS="--root-dir=/home/kubelet --fail-swap-on=false --node-ip=10.9.0.12"
EOF
```

## 初始化控制平面节点(主节点执行)

```shell
kubeadm init --cri-socket unix:///var/run/crio/crio.sock --image-repository registry.aliyuncs.com/google_containers --apiserver-advertise-address=10.9.0.10 --pod-network-cidr=10.9.0.0/16
```

## 卸载

```shell
kubeadm reset --cri-socket unix:///var/run/crio/crio.sock
```

## 其它节点加入集群

`--token`和`--discovery-token-ca-cert-hash`根据kubeadm的输出改。

```shell
kubeadm join 10.9.0.10:6443 --cri-socket unix:///var/run/crio/crio.sock --token 5riq16.lqmfkw94eff6ovo2 --discovery-token-ca-cert-hash sha256:9589d683977ce5511f4cf61912b17bef41ab9696ab2d5664fa94310910811387
```

## 主节点允许调度

```shell
kubectl taint no [主节点名字] node-role.kubernetes.io/control-plane:NoSchedule-
```

## 集群扩容

新的节点和之前一样部署。但是在加入集群之前需要在主节点生成token。

```shell
kubeadm token create
```

之后正常使用`kubeadm join`加集群。

## CentOS7的坑

- `/opt/cni/bin/`这里没有CNI插件，需要自己另外下。
