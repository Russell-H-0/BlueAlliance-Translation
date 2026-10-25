#!/usr/bin/env python3
"""precheck_commit.py — 提交前自检（BlueAlliance 翻译组）。

查三件事：
1. 暂存区里有没有 `_ops/`（维护区）或 `sources/`（原文全文，版权不入库）
2. 返稿文件名是否合规
3. 是不是在 main 上直接提交

不查译文内容。
用法：python scripts/precheck_commit.py
退出码：0 = 可以提交；1 = 有问题，先按提示修正。
"""
import re
import subprocess
import sys

FORBIDDEN_PREFIXES = ("_ops/", "sources/")
ALLOWED_IN_REVIEW = {
    "review-inbox/docs/": re.compile(r"^\d{4}-\d{2}-\d{2}_.+_审回_.+\.docx$"),
    "review-inbox/notes/": re.compile(r"^\d{4}-\d{2}-\d{2}_.+_批注_.+\.md$"),
}


def run(args):
    p = subprocess.run(["git", "-c", "core.quotepath=false", *args[1:]],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def say(tag, msg):
    print(f"[{tag}] {msg}")


def main():
    code, root, _ = run(["git", "rev-parse", "--show-toplevel"])
    if code != 0:
        say("BLOCK", "当前目录不在 git 仓库里")
        return 1

    code, staged_txt, _ = run(["git", "diff", "--cached", "--name-only"])
    staged = [l.strip() for l in staged_txt.splitlines() if l.strip()]

    code, branch, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    problems, warns = [], []

    if branch == "main":
        warns.append("你在 main 上提交。建议改到 review/<篇名>-<你的ID> 分支再推")

    if not staged:
        warns.append("暂存区是空的：先 git add 你那份返稿文件")
        say("WARN", "暂存区为空，没什么可检查的")
        return 0

    say("OK", f"待提交 {len(staged)} 个文件（分支 {branch}）")
    for f in staged:
        say("     ", f)

    for f in staged:
        if f.startswith(FORBIDDEN_PREFIXES):
            problems.append(f"禁止入库的目录：{f}（_ops/ 是维护区，sources/ 是原文全文）")

    for f in staged:
        for prefix, pattern in ALLOWED_IN_REVIEW.items():
            if f.startswith(prefix):
                name = f[len(prefix):]
                if not pattern.match(name):
                    expect = ("<日期>_<篇名>_审回_<你的ID>.docx" if "docs" in prefix
                              else "<日期>_<篇名>_批注_<你的ID>.md")
                    problems.append(f"命名不合规：{f}（应为 {expect}）")

    print()
    if problems:
        say("结果", "不能提交 —— 先修正：")
        for p in problems:
            say("     ", p)
        say("提示", "误加的文件用 git reset HEAD <文件> 撤出暂存区（不会删文件）")
        return 1

    if warns:
        for w in warns:
            say("WARN", w)
    say("结果", "通过，可以 commit 了")
    return 0


if __name__ == "__main__":
    sys.exit(main())
