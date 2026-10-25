#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 inbox/ 里的东西一键转成博客文章。

支持两种来源：
  · .zip  —— 飞书导出 Markdown 时，如果文档带图片就是 zip
  · .md   —— 纯文本导出，或者你自己在别处写的草稿

处理流程：
  解压 → 找到正文 md → 提取标题 → 复制图片 → 改写图片引用 → 补 front matter
  → 写入 content/<分类>/ → 原文件挪到 inbox/_done/

用法（一般由 import.cmd 调用，不用手敲）：
  uv run python _import.py writeups
  uv run python _import.py notes
  uv run python _import.py musings
"""

import itertools
import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

try:
    from markdown_it import MarkdownIt
except ImportError:      # 没装依赖时跳过 ** 修复，不影响正常导入
    MarkdownIt = None

ROOT = Path(__file__).resolve().parent
INBOX = ROOT / "inbox"
DONE = INBOX / "_done"
WORK = INBOX / "_work"
CONTENT = ROOT / "content"
IMAGES = ROOT / "static" / "images"

SECTIONS = {"writeups", "notes", "musings"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}


# ----------------------------------------------------------------------
def safe_name(name: str) -> str:
    """把标题转成能当文件名 / URL 的形式"""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip().rstrip(".")
    return (name[:80] or "untitled")


def safe_img_name(name: str) -> str:
    """图片名里的空格会让 URL 变丑（image%201.png），统一换成连字符"""
    return re.sub(r"\s+", "-", name.strip())


def find_body_md(folder: Path):
    """在解压出来的东西里找正文 md —— 取体积最大的那个，
       因为导出包里常常还带着几个无关的说明文件"""
    mds = [p for p in folder.rglob("*.md") if p.is_file()]
    return max(mds, key=lambda p: p.stat().st_size) if mds else None


def shift_headings(lines):
    """代码块外的标题整体下移一级（飞书导出会把章节也标成 #）"""
    out, in_code = [], False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue
        out.append("#" + line if re.match(r"^#{1,5}\s+\S", line) else line)
    return out


def pop_title(lines):
    """取出第一个一级标题当文章标题，并从正文删掉（避免和页面标题重复）"""
    in_code = False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            del lines[i]
            while i < len(lines) and not lines[i].strip():
                del lines[i]
            return m.group(1), lines
    return None, lines


IMG_MD_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def rewrite_images(text: str, slug: str) -> str:
    """把本地图片引用改成 /images/<slug>/文件名；外链原样不动"""
    def repl(m):
        url = m.group(1).strip()
        if url.lower().startswith(("http://", "https://", "data:")):
            return m.group(0)
        name = safe_img_name(url.replace("\\", "/").split("/")[-1])
        if not re.search(r"\.(png|jpe?g|gif|webp|bmp|svg)$", name, re.I):
            return m.group(0)
        return f"![]({('/images/' + slug + '/' + name)})"

    return IMG_MD_RE.sub(repl, text)


# ----------------------------------------------------------------------
#  飞书导出的 Markdown 经常把 ** 和行内代码挤在一起，例如
#      **`Application`**** 被替换成了壳的 Application**
#  渲染后会在页面上留下字面的 **。下面按行穷举要删掉哪几个 **，
#  取「页面上看不到 **，且保留的加粗最多」的方案。
#  代码块（``` 包起来的部分）完全不动：里面的 ** 可能是指针语法。
# ----------------------------------------------------------------------
_TAG_RE = re.compile(r"<[^>]+>")
_HTML_CODE_RE = re.compile(r"<code>.*?</code>", re.S)


def _visible_count(md, s: str):
    """返回 (页面上会看到的 ** 数量, 加粗数量)"""
    # 用 renderInline：render() 会把行首 4 空格当成代码块，
    # 那样 ** 原样保留，会误判成「没修好」。
    out = md.renderInline(s)
    plain = _TAG_RE.sub("", _HTML_CODE_RE.sub("", out))
    return plain.count("**"), out.count("<strong>")


def _fix_bold_line(md, line: str):
    """返回修好的行；本来就没问题、或找不到安全方案时返回 None"""
    if "**" not in line:
        return None

    codes = []

    def save(m):
        codes.append(m.group(0))
        return "ZZCODE%dZZ" % (len(codes) - 1)

    # 行内代码先换成占位符，避免把代码里的 ** 当成错误标记
    prot = re.sub(r"`[^`\n]*`", save, line)
    if _visible_count(md, prot)[0] == 0:
        return None

    pos = [m.start() for m in re.finditer(r"\*\*", prot)]
    if not pos or len(pos) > 14:      # 组合爆炸保护
        return None

    best = None
    for r in range(len(pos) + 1):
        for combo in itertools.combinations(pos, r):
            chars = list(prot)
            for p in combo:
                chars[p] = ""
                chars[p + 1] = ""
            cand = "".join(chars)
            bad, strong = _visible_count(md, cand)
            if bad == 0:
                score = (strong, -r)
                if best is None or score > best[0]:
                    best = (score, cand)

    if best is None:
        return None

    cand = best[1]
    for i, c in enumerate(codes):
        cand = cand.replace("ZZCODE%dZZ" % i, c)
    return cand


def fix_bold(text: str):
    """修复正文里的 ** 错位，返回 (新正文, 仍需人工处理的行号)"""
    if MarkdownIt is None:
        return text, []

    md = MarkdownIt("commonmark")
    out, in_code, warnings = [], False, []

    for i, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or "**" not in line:
            out.append(line)
            continue

        fixed = _fix_bold_line(md, line)
        if fixed is None:
            if _visible_count(md, line)[0] > 0:
                warnings.append(i)
            out.append(line)
        else:
            out.append(fixed)

    return "\n".join(out), warnings


def front_matter(title: str, section: str) -> str:
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    toc = "false" if section == "musings" else "true"
    return (
        "+++\n"
        f"title = '{title}'\n"
        f"date = '{now}'\n"
        # 行尾这句提示是刻意写进正文里的：打开 md 第一眼就能看到
        # 该改哪一行，不用再去翻说明文档。
        "draft = true    # 内容改完后改成 false，否则线上博客看不到这篇\n"
        "summary = ''\n"
        "tags = []\n"
        f"showtoc = {toc}\n"
        "+++\n"
    )


# ----------------------------------------------------------------------
def process_one(src: Path, section: str) -> str:
    slug = safe_name(src.stem)

    work = WORK / slug
    if work.exists():
        shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True, exist_ok=True)

    # 1. 把内容摊到工作目录里
    if src.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(src) as z:
                z.extractall(work)
        except zipfile.BadZipFile:
            return f"[失败] {src.name} —— 不是有效的 zip"
    else:
        shutil.copy2(src, work / src.name)

    md_file = find_body_md(work)
    if md_file is None:
        return f"[跳过] {src.name} —— 里面没有找到 .md 文件"

    text = md_file.read_text(encoding="utf-8", errors="replace")

    # 2. 标题
    title, lines = pop_title(text.split("\n"))
    if not title:
        title = src.stem
    title = title.replace("\\", "")

    # 3. 正文：标题下移一级，图片路径改写成站内路径
    body = "\n".join(shift_headings(lines)).strip("\n")
    body = rewrite_images(body, slug)
    body, bold_warn = fix_bold(body)

    # 4. 图片：摊出来的所有图片都搬进 static/images/<slug>/
    img_dst = IMAGES / slug
    n_img = 0
    for p in work.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMG_EXT:
            img_dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, img_dst / safe_img_name(p.name))
            n_img += 1

    # 5. 落地
    out = CONTENT / section / f"{slug}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(front_matter(title, section) + body + "\n", encoding="utf-8")

    # 6. 原文件挪走，免得下次重复导入
    DONE.mkdir(parents=True, exist_ok=True)
    target = DONE / src.name
    if target.exists():
        target = DONE / f"{datetime.now().strftime('%H%M%S')}-{src.name}"
    shutil.move(str(src), str(target))
    shutil.rmtree(work, ignore_errors=True)

    # 这里打印完整绝对路径，而不是 content/notes/xxx.md 这种相对写法：
    # 要改的就是这个文件，把路径直接复制到资源管理器地址栏就能打开。
    msg = (f"[成功] {title}\n"
           f"        文章: {out}\n"
           f"        图片: {n_img} 张 -> {img_dst}")
    if bold_warn:
        msg += ("\n        注意: 正文第 "
                + ", ".join(str(n) for n in bold_warn)
                + " 行仍有 ** 残留，需要手工处理")
    return msg


def main():
    section = sys.argv[1] if len(sys.argv) > 1 else ""
    if section not in SECTIONS:
        print(f"分类必须是这三个之一：{', '.join(sorted(SECTIONS))}")
        sys.exit(1)

    INBOX.mkdir(exist_ok=True)

    items = [p for p in sorted(INBOX.iterdir())
             if p.is_file() and p.suffix.lower() in {".zip", ".md"} and not p.name.startswith("_")]

    if not items:
        print(f"inbox 里没有东西。")
        print(f"把飞书导出的 zip（或 .md）放进：{INBOX}")
        print("然后再运行一次。")
        return

    print(f"inbox 里有 {len(items)} 个文件，准备导入到「{section}」\n")
    print("=" * 60)
    for p in items:
        print(process_one(p, section))
        print()
    print("=" * 60)
    print("导入完成。接下来：")
    print("  1. 双击 serve.cmd 预览（它带 --buildDrafts，所以草稿也看得到）")
    print("  2. 用记事本打开上面「文章:」那一行的完整路径，改标题和正文")
    print("     ！！不要去 inbox 或 inbox\\_done 里找文件 ！！")
    print("        那里放的是飞书原件和它处理完的存档，")
    print("        改那边博客不会有任何变化。")
    print("        要改的永远是 content\\<分类>\\ 里的那一份。")
    print("  3. 【必须】把开头的 draft = true 改成 draft = false")
    print("       不改的话线上构建会直接跳过它：本地预览看得见，")
    print("       线上博客永远找不到 —— 最容易踩的就是这个坑。")
    print("  4. 双击 publish.cmd 发布，约 1 分钟后线上生效")


if __name__ == "__main__":
    main()
