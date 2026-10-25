#!/usr/bin/env python3
"""preflight.py — 交稿前的探活检查（BlueAlliance 翻译组）。

做什么：确认你在仓库里、分支对不对、远端通不通、今天该审哪一份。
不做什么：不看译文内容，不评价质量。

用法：python scripts/preflight.py
退出码：0 = 可以继续；1 = 有 BLOCK 级问题，先解决。
"""
import re
import subprocess
import sys
from pathlib import Path


def run(args, timeout=20):
    try:
        p = subprocess.run(["git", "-c", "core.quotepath=false", *args[1:]],
                           capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except FileNotFoundError:
        return 127, "", f"找不到命令：{args[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", "超时"


def say(tag, msg):
    print(f"[{tag}] {msg}")


def main():
    blocks, warns = [], []

    code, root, err = run(["git", "rev-parse", "--show-toplevel"])
    if code != 0 or not root:
        say("BLOCK", "当前目录不在 git 仓库里。先 cd 到仓库目录，或 git clone：")
        say("     ", "git clone https://github.com/Russell-H-0/BlueAlliance-Translation.git")
        return 1
    root_path = Path(root)
    say("OK", f"仓库目录：{root_path}")

    code, url, _ = run(["git", "remote", "get-url", "origin"], timeout=10)
    if code != 0 or "BlueAlliance-Translation" not in url:
        blocks.append("origin 不是 BlueAlliance-Translation（或没配置远端）")
        say("BLOCK", f"远端异常：{url or '未配置'}")
    else:
        say("OK", f"远端：{url}")

    code, branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], timeout=10)
    say("OK", f"当前分支：{branch}")
    if branch == "main":
        warns.append("你在 main 上。改稿前先建分支：git checkout -b review/<篇名>-<你的ID>")
        say("WARN", "当前在 main 分支，不要直接改、不要直接推")

    code, status, _ = run(["git", "status", "--porcelain"], timeout=15)
    dirty = [l for l in status.splitlines() if l.strip()]
    if dirty:
        warns.append(f"有 {len(dirty)} 个未提交改动，先处理再拉取/交稿")
        say("WARN", f"工作区不干净（{len(dirty)} 项）：")
        for l in dirty[:5]:
            say("     ", l)
        say("     ", "建议：git stash（暂存）或先提交，再继续")

    code, out, err = run(["git", "ls-remote", "--heads", "origin"], timeout=25)
    if code != 0:
        warns.append("连不上远端。网络不通时不要硬推，改走微信发文件。")
        say("WARN", f"远端不可达：{err[:120]}")
    else:
        say("OK", "远端可访问")

    drafts = sorted(root_path.glob("drafts/*_审核包.docx"))
    if drafts:
        latest = drafts[-1]
        say("待审", f"{latest.relative_to(root_path)}")
        m = re.match(r"(\d{4}-\d{2}-\d{2})_(.+?)_审核包\.docx$", latest.name)
        if m:
            date, slug = m.groups()
            say("待审", f"改完后存成：review-inbox/docs/{date}_{slug}_审回_<你的ID>.docx")
    else:
        say("待审", "drafts/ 下没有审核包。等群里发招工，或 git pull 取最新")

    print()
    if blocks:
        say("结果", "BLOCKED —— 先解决上面的 BLOCK 项")
        for b in blocks:
            say("     ", b)
        return 1
    if warns:
        say("结果", "READY（有提醒，注意即可）")
        for w in warns:
            say("     ", w)
        return 0
    say("结果", "READY")
    return 0


if __name__ == "__main__":
    sys.exit(main())
