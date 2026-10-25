#!/usr/bin/env python3
"""ci_check_paths.py — PR / push 路径与命名守卫（GitHub Actions 里跑）。

拦三类问题：
1. `_ops/` 或 `sources/` 混进提交（维护区与原文全文不入库）
2. `review-inbox/docs|notes` 下文件名不合规
3. 返稿文件被放到错误目录

只在 CI 里跑，不改任何文件。出错时退出码 1，PR 会标红。
"""
import os
import re
import subprocess
import sys

FORBIDDEN = ("_ops/", "sources/")

NAMING = {
    "review-inbox/docs/": (r"^\d{4}-\d{2}-\d{2}_.+_审回_.+\.docx$",
                           "<日期>_<篇名>_审回_<你的ID>.docx"),
    "review-inbox/notes/": (r"^\d{4}-\d{2}-\d{2}_.+_批注_.+\.md$",
                            "<日期>_<篇名>_批注_<你的ID>.md"),
}

ALLOWED_EXT_IN_REVIEW = (".docx", ".md")


def git(*args):
    p = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "").strip()


def changed_files():
    base = os.environ.get("BASE_REF", "").strip()
    event = os.environ.get("EVENT_NAME", "")
    if base:
        rc, out = git("diff", "--name-only", f"origin/{base}...HEAD")
    elif event == "push":
        rc, out = git("diff", "--name-only", "HEAD^", "HEAD")
        if rc != 0:  # 首次提交没有父提交
            rc, out = git("show", "--pretty=format:", "--name-only", "HEAD")
    else:
        rc, out = git("diff", "--name-only", "HEAD^", "HEAD")
    return [l.strip() for l in out.splitlines() if l.strip()] if out else []


def main():
    files = changed_files()
    errors = []

    if not files:
        print("没有检测到变更文件，跳过。")
        return 0

    print(f"检查 {len(files)} 个变更文件：")
    for f in files:
        print("  -", f)

    for f in files:
        if f.startswith(FORBIDDEN):
            errors.append(f"{f} —— 禁止入库（_ops/ 是维护区，sources/ 是原文全文）")

    for f in files:
        for prefix, (pattern, expect) in NAMING.items():
            if f.startswith(prefix):
                name = f[len(prefix):]
                if name.startswith("."):
                    continue
                if not re.match(pattern, name):
                    errors.append(f"{f} —— 命名不合规，应为 {expect}")
                if not name.endswith(ALLOWED_EXT_IN_REVIEW):
                    errors.append(f"{f} —— 返稿区只收 .docx 或 .md")

    print()
    if errors:
        print("❌ 检查未通过：")
        for e in errors:
            print("  -", e)
        print("\n修正后重新提交即可；误加的文件用 `git reset HEAD <文件>` 撤出暂存区。")
        return 1

    print("✅ 路径与命名检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
