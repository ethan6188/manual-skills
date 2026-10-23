# 具体写法

下面的值都出自这次上线的页面。数值是示范，真正使用时换成你产品自己的令牌。

## 令牌

深色只覆盖同一组变量，不写第二套选择器。

```css
:root {
    --bg: #fff;
    --card: #f5f5f7;
    --text: #1d1d1f;
    --text-2: #6e6e73;
    --text-3: #86868b;
    --hairline: rgba(0, 0, 0, 0.08);
    --control-border: rgba(0, 0, 0, 0.12);
    --link: #06c;
    --accent: #007aff;
    --focus: rgba(0, 122, 255, 0.55);
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg: #1e1e1e;
        --card: #2a2a2c;
        --text: #f2f2f2;
        --text-2: #aeaeb2;
        --text-3: #8e8e93;
        --hairline: rgba(255, 255, 255, 0.07);
        --link: #4da3ff;
    }
}
```

## 字号与版面

- 字体栈：`-apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Helvetica Neue", sans-serif`。
- 首屏标题 `clamp(36px, 4.6vw, 56px)`，字重 600，字距 `-0.02em`，行高 1.22。正文 16px / 1.7，副文 18px，次要信息 13px。
- 容器宽 1120px，两侧留 24px；章节上下各 112px，章节之间只有一条发际线。
- 首屏两栏 5:6，左文右图；窄屏改单列，锚点隐藏，只留下载按钮。
- 圆角分层：窗口 12，功能片段外框 16，卡片 10，按钮 10，小标签 6。

## 产品窗口复刻

1px 发际线边框、12px 圆角、一层大而轻的阴影，这是全页唯一的真投影。标题栏 44px，左侧三个交通灯，右侧状态点。

```css
.win {
    background: var(--bg);
    border: 1px solid var(--hairline);
    border-radius: 12px;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.14), 0 2px 6px rgba(0, 0, 0, 0.06);
    overflow: hidden;
}
```

## 功能片段卡

固定高度，裁切，底部渐隐。里面的面板贴左上，只有左上角圆角，看起来是窗口的一角。

```css
.shot {
    position: relative;
    height: 300px;
    overflow: hidden;
    border-radius: 16px;
    padding: 32px 0 0 32px;
    box-shadow: inset 0 0 0 1px var(--hairline);
}

.shot::after {
    content: "";
    position: absolute;
    inset: auto 0 0 0;
    height: 72px;
    background: linear-gradient(to bottom, transparent, color-mix(in srgb, var(--card) 92%, transparent));
    pointer-events: none;
}
```

## 主角的状态表

一张表驱动所有视图。按钮和主角点击都走同一个函数，三处显示不会不一致。

```js
const POSES = {
  observing: { note: '正在观察并记录。', status: '正在记录', rec: true },
  paused: { note: '已暂停记录。', status: '已暂停', rec: false },
};

function setPose(name) {
  const p = POSES[name];
  pet.querySelectorAll('img').forEach((img) => img.classList.toggle('on', img.dataset.pose === name));
  buttons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.pose === name)));
  note.textContent = p.note;
  statusText.textContent = p.status;
  status.dataset.rec = p.rec ? 'on' : 'off';
}
```

图片切换用 0.18s 透明度过渡。录制点只在 `data-rec="on"` 时呼吸：

```css
.status[data-rec="on"] .dot {
    background: var(--recording);
    animation: pulse 2.4s ease-in-out infinite;
}
```

## 焦点

```css
:focus-visible {
    outline: 3px solid var(--focus);
    outline-offset: 2px;
    border-radius: 6px;
}
```
