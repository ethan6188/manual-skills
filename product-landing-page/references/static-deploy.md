# 静态站部署：systemd + Python http.server

适用：内网或自管 Linux 服务器，几个静态文件，不想装 nginx。以下问题都在一台老系统（Linux 5.10、Python 3.6、较旧的 systemd）上真实遇到过。

## 目录与服务

站点放 `/opt/site`，由一个低权限用户运行。不要用 root；端口 80 靠能力位绑定，不需要 root。

```ini
[Unit]
Description=Product website
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=SERVICE_USER
Group=SERVICE_USER
WorkingDirectory=/opt/site
ExecStart=/usr/bin/python3 -m http.server 80 --bind 0.0.0.0
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadOnlyPaths=/opt/site

[Install]
WantedBy=multi-user.target
```

把 `SERVICE_USER` 换成服务器上已有的低权限用户。安装并启动：

```bash
systemctl daemon-reload
systemctl enable --now site.service
systemctl is-active site.service
```

## 踩过的坑

- Python 3.6 的 `http.server` 没有 `--directory`。用 `WorkingDirectory=` 指定目录，不要依赖这个参数。
- 老 systemd 会忽略 `ProtectSystem=strict` 和 `ReadOnlyPaths`，只打印警告。保留它们无害，但不要把它们当成已生效的隔离。
- 端口 80 被前一次手动测试的服务占着时，新服务会一直停在 `activating`。先找到占用进程，确认它确实是自己起的测试服务再杀。判断进程是否是目标时，`/proc/PID/cmdline` 里参数以 NUL 分隔，直接 `grep 'http.server 80'` 匹配不上，要先转换：

```bash
tr '\0' ' ' < /proc/PID/cmdline | grep -q 'http.server 80' && echo match
```

- 从 macOS 打的 tar 会保留你本机的 uid（比如 501），解出来的文件属主在服务器上是陌生数字。解包加 `--no-same-owner`；已经传错的，对站点目录做一次 `chown -R root:root`。
- macOS 的 tar 会带扩展属性，服务器解包时打印一堆 `Ignoring unknown extended header keyword` 警告。打包时设置 `COPYFILE_DISABLE=1` 并加 `--no-xattrs`，同时排除 `.DS_Store`。
- 只有「远程执行命令」通道、没有 scp 时，大文件分块传：每块 100000 字节的 base64，用 `printf '%s' '块内容' >> 远端文件` 追加，最后 `base64 -d < 远端文件`，用 SHA-256 校验。base64 字母表不含单引号，放进单引号里是安全的。解码时用 `base64 -d < 文件`（重定向输入），在 macOS 与 Linux 上都能用；`base64 -d 文件` 在 macOS 上会报用法错误。
- 远程执行通道或调用它的工具可能对单次命令设超时（这次遇到的是约 40 秒）。命令被转到后台时，结果要从后台任务的输出里读，不要当成失败而重复执行。
- 远端状态用 `systemctl is-active` 判断，不要只看命令退出码。

## 验证与更新

- 发布后用 `curl` 逐个请求 `/`、样式、脚本、图片，再请求下载链接看 `Content-Length`，命令见 SKILL.md。
- 更新站点只需重新跑上传脚本，服务不用重启；静态文件由 `http.server` 每次请求直接读取。
- 前面有单点登录网关时，匿名 `curl` 只会得到 302 跳转到登录页，无法验证内容；验证要在登录态下，或直接请求源站地址。
- 这个服务没有认证，也没有 HTTPS。仅限内网，对外要放到有认证的网关后面。
