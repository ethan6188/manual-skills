---
name: product-landing-page
description: 产品官网的设计与开发全流程：单页功能介绍加下载入口，继承产品设计系统，再部署成静态站。Use when asked to design, build, polish, deploy or publish a product landing page / 官网 / 下载页, wire up its download link, or ship it behind systemd on a Linux box.
---

# 产品官网：设计、开发到上线

一页、无构建、三个文件（`index.html` / `styles.css` / `app.js`）加图片资源。风格直接继承产品自己的设计系统，功能区用 HTML 画出来的界面片段，而不是截图。验证过的做法，全部来自一次真实的设计与开发。

路径相对于本 skill 目录。按下面的顺序读：本文是主线；[references/process.md](references/process.md) 记录设计与开发的先后顺序、每步取舍和返工；[references/design.md](references/design.md) 是令牌与版面细节；[references/static-deploy.md](references/static-deploy.md) 是部署。

## 开工前

1. 找到产品自己的设计令牌（颜色、字号、圆角、分隔线、深浅色）。官网沿用它们，不另起一套配色。没有令牌时，先问用户要设计稿或应用截图，不要凭空发明。
2. 弄清楚三个事实并写在手边：当前版本号、安装包大小、下载地址。页面上的这三处必须与发行清单一致，见下文「下载入口」。
3. 确定页面唯一的主角：产品里最有辨识度的东西（吉祥物、核心界面、一个会动的状态）。其余一切保持安静。

## 页面结构

按这个顺序，每段只做一件事。细节与令牌见 [references/design.md](references/design.md)。

1. 顶栏：品牌、两到三个锚点、一个小号下载按钮。吸顶，毛玻璃。
2. 首屏：一句话主张 + 一段副文 + 主按钮与次按钮 + 一行版本与系统要求；右侧是产品窗口的 HTML 复刻，主角（如吉祥物）坐在窗口边缘，可点击切换状态。
3. 功能区：四张卡，每张是「裁切的界面片段 + 一个三级标题 + 一句话」。片段用真实组件的 HTML 搭，底部渐隐。
4. 信任区（记录数据类产品必备）：把产品的每种状态各讲一句，最后一行写清「绝不会做什么」。
5. 下载区：应用图标卡 + 一个按钮 + 三步安装说明（含需要授予的权限、首次下载的内容）。
6. 页脚：版本号与一句话定位。

文案规则：先说用户得到什么，再说怎么做到；一句话能说完的不写两句；示例内容如果是虚构的，在页面上标明「示例」。

## 构建

先本地预览，再改细节：

```bash
python3 -m http.server 8000 --directory site
```

然后用浏览器看深色、浅色、窄屏三种效果，并测键盘焦点。`prefers-reduced-motion` 下所有动画必须停。

代码风格要一开始就写对，否则代码扫描会刷出几百条：

- CSS 每行一条声明、4 空格缩进、规则之间留空行、选择器列表每个一行、能缩写的十六进制颜色用缩写。已经写成紧凑形式时，用脚本一次展开：

```bash
python3 -I scripts/css-expand.py -i site/styles.css
```

- JS 字符串用单引号。

## 下载入口

- 下载地址只在 `app.js` 顶部放一个常量，所有 `[data-download]` 链接由它填充。页面里不要写死第二份。
- 页面是 HTTPS 时，下载地址也必须是同域 HTTPS（例如 `/App.dmg`），否则浏览器会按混合内容拦截下载。
- 只暴露当前这一个安装包的入口，不要把整个发行目录开放出来；同步官网时不要改写发行清单或签名。
- 每次发版同步三样：版本号、安装包大小、下载地址。它们在页面里会出现多处（首屏说明、下载卡片、页脚），用全文搜索旧值逐处替换，漏改一处就会和发行清单对不上。
- 没有公证/签名的安装包，页面要写一句首次打开的处理方式，不要让用户自己撞上系统拦截。

## 部署成静态站

最小方案：一个 systemd 服务用 Python 自带的 `http.server` 提供目录。完整步骤与踩坑见 [references/static-deploy.md](references/static-deploy.md)。

只有「在服务器上执行一条命令」的通道、没有 scp 时，用脚本分块上传并校验哈希：

```bash
RUN='ssh root@HOST' REMOTE_DIR=/opt/site bash scripts/publish-static.sh path/to/site
```

脚本已在本机用 `RUN='bash -c'` 模拟远端跑通（多分块、哈希校验、`.DS_Store` 被排除）；真实服务器上跑过的是同一套 tar/base64/哈希流程。

## 上线后核对

```bash
for p in / /styles.css /app.js /assets/icon.png; do
  curl -s -o /dev/null -w "%{http_code} $p\n" http://HOST$p
done
curl -sI http://HOST/App.dmg | head -3
```

- 每个资源 200，下载链接返回 200 且 `Content-Length` 与页面写的大小一致。
- 域名前面如果有单点登录网关，匿名请求只会得到 302，这不能证明页面内容正确；要在登录态下目视检查一次，或直接请求源站端口。
- 站点不含任何认证。内网使用时确认前面有网关，或限制来源地址。

## 已知的坑

- 修改过 `publish-static.sh` 之后，务必真跑一遍再信它；上传脚本里的 tar 参数改动最容易没复测。
- `css-expand.py` 按逗号拆选择器，`:is(a, b)` 这类括号内带逗号的选择器会被拆坏，遇到先手改。
- 重新发布只覆盖同名文件，不会删除已移除的文件；删资源要在服务器上手动删。
