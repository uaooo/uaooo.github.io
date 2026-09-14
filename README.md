# 博客使用手册

Hugo + PaperMod 主题，部署到 GitHub Pages。

---

## 一、先改这几处 TODO

| 文件 | 位置 | 改什么 |
| --- | --- | --- |
| `hugo.toml` | `baseURL` | `https://YOURNAME.github.io/` → 你的地址，**结尾斜杠不能少** |
| `hugo.toml` | `title` | 站点名（改两处：顶层和 `[params]` 里各一处） |
| `hugo.toml` | `author` | 你的名字/ID |
| `hugo.toml` | `socialIcons` | 你的 GitHub 地址 |
| `content/about.md` | 正文 | 自我介绍 |

> 部署后线上地址由 GitHub Actions 自动注入，所以 `baseURL` 填错也不影响线上访问，
> 只影响本地预览时的链接。但仍建议改对。

---

## 二、日常操作

### 本地预览：双击 `serve.cmd`

```
C:\Users\hp\blog\serve.cmd
```

浏览器打开 http://localhost:1313/ 。改文件自动刷新，`Ctrl+C` 停止。

> **为什么用 `.cmd` 而不是 `.ps1`？**
> Windows 上双击 `.ps1` 文件的默认动作是"用记事本打开"，不会执行，所以你不会看到
> 任何报错、也不会有反应。`.cmd` 批处理则双击即运行。
>
> 另外，**不需要改任何 PowerShell 执行策略**。你这台机器的当前用户策略已经是
> `RemoteSigned`（Windows 11 默认值），本地脚本本来就允许运行。

预览带 `-D` 参数，所以 `draft: true` 的草稿也能看到——写作时不用急着改状态。

### 写新文章

```powershell
# CTF writeup（套用 archetypes/writeup.md 模板）
hugo new content writeups/2026-qiangwang-re1.md

# 逆向技术笔记（套用 archetypes/note.md）
hugo new content notes/ida-python-tips.md
```

> `hugo` 命令要**新开一个终端窗口**才能直接用（安装时更新了 PATH，旧窗口读不到）。
> 在新窗口里先 `cd C:\Users\hp\blog`。

新建的文件默认 `draft = true`，本地确认没问题后改成 `false` 才会出现在线上。

### 发布

```powershell
cd C:\Users\hp\blog
git add -A
git commit -m "add: 强网杯 re1 writeup"
git push
```

推送后 GitHub Actions 自动构建部署，约 1 分钟。进度在仓库 **Actions** 标签页看。

---

## 三、导航栏各项是什么

| 菜单 | 作用 |
| --- | --- |
| **Writeups** | `content/writeups/` 下的文章：CTF 题目题解 |
| **逆向笔记** | `content/notes/` 下的文章：工具用法、技巧沉淀 |
| **全部文章** | **按时间倒序汇总以上所有文章**，按年份分组。想看"我一共写了啥、最近写了啥"就点这里 |
| **搜索** | 站内全文搜索（按标题、摘要、正文匹配） |
| **关于** | 自我介绍页 |

下面是已移除、但你可能好奇过的东西：

- **归档**：和"全部文章"是同一个页面，之前名字起得不好，已改名。
- **标签**：给文章打关键词用的，比如一篇笔记同时涉及 `VM` 和 `反混淆`，打上标签后可以
  在 `/tags/` 页面按关键词横向找文章，不受"题解/笔记"分类限制。目前**已从导航栏移除**，
  但文章 front matter 里的 `tags` 字段仍然有效——填了就会生成对应标签页，不填就是空的。
  以后想把它加回菜单，在 `hugo.toml` 的 `[[menu.main]]` 里加一条 `url = "/tags/"` 即可。
- **随笔**：已按你的要求删除（`content/posts/` 目录已移除）。要恢复的话重新建目录并加回菜单。

---

## 四、附件和图片怎么放

这是这个博客相比飞书、CSDN 最实用的地方：**二进制附件可以直接挂上来**。

### 附件（题目 bin、exp、脚本）

放 `static/files/<文章文件名>/` 下：

```
static/files/2026-qiangwang-re1/
    chall.zip
    chall.exe
    solve.py
```

文章里这样引用：

```markdown
[下载附件](/files/2026-qiangwang-re1/chall.zip)
```

### 图片（IDA 截图、流程图）

放 `static/images/<文章文件名>/` 下：

```
static/images/2026-qiangwang-re1/
    ida-main.png
    cfg.png
```

文章里这样引用：

```markdown
![主函数反编译结果](/images/2026-qiangwang-re1/ida-main.png)
```

**约定：每篇文章一个同名目录**，避免不同文章的 `1.png` 互相覆盖。

> 关于图床：本站走"图片进仓库"的路线，好处是永不失效、可追溯，代价是仓库会变大。
> IDA 截图建议先压缩（PNG 优化或转 WebP），单张控制在 200KB 以内比较理想。

---

## 五、换成自己的背景图

背景样式都在 `assets/css/extended/custom.css`，文件顶部就是所有旋钮。换照片三步：

1. 把图片丢进 `static/images/`，比如 `static/images/bg.jpg`
2. 打开 `custom.css`，把 `--bg-photo: none;` 改成 `--bg-photo: url("/images/bg.jpg");`
3. 把 `--bg-dim: transparent;` 改成 `--bg-dim: rgba(0, 0, 0, 0.55);`

**第 3 步别漏**。照片本身通常很花，不压暗的话正文会糊在照片里，尤其是代码块之外的段落文字。
`0.55` 是压暗程度，觉得暗就调到 `0.4`，觉得花就调到 `0.7`。

其他可调项：

| 变量 | 作用 |
| --- | --- |
| `--glow-opacity` | 光斑强度（照片背景建议设成 `0`，避免和照片打架） |
| `--entry` | 卡片底色透明度，数字越小越透 |
| `--glass-blur` | 毛玻璃模糊半径，越大越磨砂 |
| `--bg-gradient` | 默认渐变配色，想换色改这里 |

改完存盘，预览会自动重建。**如果没生效，Ctrl+C 停掉重新运行**——Hugo 有时缓存不到
新增的 assets 文件，必要时删掉 `public/` 和 `resources/` 再启动。

> 代码块和行内代码的底色是刻意保持不透明的，不受背景影响。写 writeup 时反编译代码是核心
> 内容，压在花纹背景上没法读。

---

## 六、部署到 GitHub Pages

### 第 1 步：建仓库

在 GitHub 新建仓库，名字建议就用 **`<你的用户名>.github.io`**（例如 `hp.github.io`）。
这样最终地址就是 `https://<用户名>.github.io/`，最干净。

公开（Public）即可。**不要**勾选 "Add a README file"，本地已经有了。

### 第 2 步：先配好 git 身份

本机目前还没配，不配的话 `commit` 会直接失败：

```powershell
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

### 第 3 步：关联并推送

把 `YOURNAME` 换成你的用户名：

```powershell
cd C:\Users\hp\blog
git remote add origin https://github.com/YOURNAME/YOURNAME.github.io.git
git branch -M main
git add -A
git commit -m "init: hugo blog"
git push -u origin main
```

推送时可能弹窗要求登录 GitHub，按提示授权即可。

### 第 4 步：打开 Pages

仓库页面 → **Settings** → 左侧 **Pages** → **Build and deployment** →
**Source** 选 **GitHub Actions**（不要选 "Deploy from a branch"）。

### 第 5 步：等构建

回到 **Actions** 标签页，看到绿色对勾就成功了。访问 `https://YOURNAME.github.io/`。

以后每次 `git push` 都会自动重新部署，不用再做任何配置。

---

## 七、目录结构

```
blog/
├── hugo.toml                # 全站配置（站点名、菜单、高亮、分类法）
├── serve.cmd                # 本地预览（双击运行）
├── serve.ps1                # 同上，PowerShell 版（备用）
├── archetypes/              # 新建文章时的模板
│   ├── writeup.md           #   → hugo new content writeups/xxx.md
│   ├── note.md              #   → hugo new content notes/xxx.md
│   └── default.md
├── content/                 # 所有文章（Markdown）
│   ├── writeups/            # CTF 题解
│   ├── notes/               # 逆向笔记
│   ├── about.md             # 关于页
│   ├── archives.md          # 全部文章页
│   └── search.md            # 搜索页
├── assets/css/extended/
│   └── custom.css           # 背景与毛玻璃样式（改这里）
├── static/
│   ├── files/               # 题目附件、脚本
│   └── images/              # 文章配图、背景图
├── themes/PaperMod/         # 主题（普通目录，clone 下来就能用）
└── .github/workflows/       # 自动部署配置
```

`public/` 和 `resources/` 是构建产物，已忽略，不用管。

---

## 八、其它调整

### 换默认亮/暗色

`hugo.toml` 里改 `defaultTheme`，可选 `dark` / `light` / `auto`。右上角本来就有切换按钮，
访客可以自己切，这里只决定"第一次打开时是什么"。

### 写数学公式（密码学、算法逆向常用）

1. `hugo.toml` → `[params]` 里把 `math = false` 改成 `true`
2. 需要公式的那篇文章 front matter 里加 `math = true`

然后可以用 `$...$`（行内）和 `$$...$$`（独立成行）。

### 想继续简化分类

目前只有 `writeups/` 和 `notes/` 两个目录。如果连这两个都不想分，可以合并成一个目录
（比如 `content/re/`），改起来不影响已写的文章，需要时告诉我。

### 按赛事归档

文章 front matter 里的 `events` 字段可以用来标记比赛名：

```toml
events = ['2026 强网杯']
```

会生成 `/events/` 页面。目前导航栏没放入口，需要的话加一条 `[[menu.main]]` 即可。

### 换主题

主题是普通目录，不涉及 submodule。换法：把新主题放进 `themes/`，改 `hugo.toml` 里的
`theme = "新主题目录名"`。文章一个字都不用动。

---

## 九、参考

- Hugo 文档：https://gohugo.io/documentation/
- PaperMod 文档：https://github.com/adityatelange/hugo-PaperMod/wiki
- Chroma 支持的语言列表：https://gohugo.io/content-management/syntax-highlighting/
