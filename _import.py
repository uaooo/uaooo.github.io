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

import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

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
        name = url.replace("\\", "/").split("/")[-1]
        if not re.search(r"\.(png|jpe?g|gif|webp|bmp|svg)$", name, re.I):
            return m.group(0)
        return f"![]({('/images/' + slug + '/' + name)})"

    return IMG_MD_RE.sub(repl, text)


def front_matter(title: str, section: str) -> str:
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    toc = "false" if section == "musings" else "true"
    return (
        "+++\n"
        f"title = '{title}'\n"
        f"date = '{now}'\n"
        "draft = true\n"
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

    # 4. 图片：摊出来的所有图片都搬进 static/images/<slug>/
    img_dst = IMAGES / slug
    n_img = 0
    for p in work.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMG_EXT:
            img_dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, img_dst / p.name)
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

    return (f"[成功] {title}\n"
            f"        文章: content/{section}/{slug}.md\n"
            f"        图片: {n_img} 张 -> static/images/{slug}/")


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
    print("  1. 双击 serve.cmd 预览（它带 --buildDrafts，草稿也能看到）")
    print("  2. 用记事本 / VS Code 打开刚生成的那个 .md，改标题和正文")
    print("  3. 【必须】把开头的 draft = true 改成 draft = false")
    print("       不改的话线上构建会跳过它：本地预览看得见，")
    print("       线上博客永远找不到 —— 别在这里踩坑。")
    print("  4. 双击 publish.cmd 发布，约 1 分钟后线上生效")


if __name__ == "__main__":
    main()
