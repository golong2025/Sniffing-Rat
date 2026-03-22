# 🐀 Sniffing Rat — 流量截获探针中心 (V3.1)

一个完全平台无关的 HTTPS 流量透明拦截系统。只需将底层流量重定向到本工具监听的端口，即可对任意设备的 HTTPS 流量进行实时解析、媒体截获、凭据发现，并通过现代化 Web 仪表盘可视化展示。

---

## 核心能力

| 功能 | 说明 |
|------|------|
| 🌐 **平台无关** | 不限 OpenWrt，任何能用 `iptables` 重定向流量的环境均可部署 |
| ⚙️ **Web UI 动态配置** | 在仪表盘直接添加/修改目标 IP 和端口，**自动同步 iptables 规则**，无需 SSH |
| 🔐 **HTTPS 透明拦截** | 基于 mitmproxy，完整解密握手，获取原始参数与响应体 |
| 🖼️ **媒体截获** | 绕过微信/小红书等平台防盗链，支持 H.265 视频下载 |
| 🔄 **格式自动兼容** | 自动处理微信 `wxgf` 等私有格式，仪表盘统一输出 WebP/JPEG |
| 🔑 **凭据发现** | 自动从 POST 请求中提取未加密的用户名和密码 |

---

## 快速部署

### 1. 将项目拷贝到服务器
```bash
scp -r ./sniffing-rat root@你的服务器IP:/root/
```

### 2. 构建并启动
```bash
cd /root/sniffing-rat
docker build -t sniffing-rat:latest .
docker run -d --restart unless-stopped \
  --name sniffing-rat \
  --network host \
  --cap-add NET_ADMIN \
  -v /root/sniffing-rat/db:/app/db \
  sniffing-rat:latest
```

---

## 证书安装

系统中已经封装了一套 **通用的、永久固定的 CA 证书**（位于 `certs/` 目录中）。只需安装并信任一次，以后无论怎么重新部署都不需要再次更换。

1. 手机连接代理（IP 为服务器 IP，端口 8080）
2. 访问 `http://mitm.it` 下载证书并信任（具体见源码文档）。

---

## 免责声明

本工具仅供技术研究使用。请遵守法律法规，**严禁用于非法目的**。
