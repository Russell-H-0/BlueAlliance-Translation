---
name: ba-git-sync
description: Sync BlueAlliance drafts and review returns via git.
version: 0.1.0
author: Russell_H0
license: MIT
platforms: [linux, macos, windows]
---

# BA Git Sync Skill

帮翻译组成员把稿件从 GitHub 仓库拉到本地、把校对结果推回去。
**这个技能只管文件搬运和格式规范，不碰任何内容判断。**

它不做的事，明确写在这里，避免误用：不核对数字、不核对引语、不改译文、不给翻译意见、
不判断稿子能不能发。校对永远是人做的，技能只负责让 git 这一段不卡人。

## When to Use

- "我要审这篇 / 拉最新稿子 / 把返稿传上去 / 帮我开个 PR"
- 成员拿到审核包后，需要知道该改哪个文件、改完怎么交
- 成员 push 失败、冲突、认不到权限，需要人话解释

不要用于：核稿质量、判断译文对错、决定发布——那些是人和维护者的活。

## Prerequisites

- `git` 可用；要开 PR 还需要 `gh` 已登录（`gh auth status`）
- 仓库已 clone 到本地（脚本会自动识别仓库根目录）
- 成员身份二选一：
  - 被邀请为仓库 collaborator：可在主仓开分支并推
  - 没被邀请：fork 到自己账号，从 fork 开 PR（步骤见 `references/git-four-commands.md`）

## How to Run

```bash
# 1) 探活：确认在仓库里、分支对、远端通、今天该审哪份
python scripts/preflight.py

# 2) 成员审完稿，把文件放进 review-inbox/api 对应目录后，提交前自检
python scripts/precheck_commit.py

# 3) 通过后按提示提交（脚本只检查，不替你提交）
git checkout -b review/<篇名>-<你的ID>
git add review-inbox/docs/<文件名>
git commit -m "审回：<中文标题>（@<你的ID>）"
git push -u origin HEAD
gh pr create --fill
```

## Quick Reference

| 目的 | 命令 |
|---|---|
| 看今天该审哪份 | `python scripts/preflight.py` |
| 提交前查有没有误带维护区文件 | `python scripts/precheck_commit.py` |
| 拉最新稿子 | `git pull --ff-only` |
| 返稿放哪 | `review-inbox/docs/`（改过的 docx）或 `review-inbox/notes/`（只写批注的 md） |
| 命名规范 | `<日期>_<篇名>_审回_<你的ID>.docx` ／ `<日期>_<篇名>_批注_<你的ID>.md` |

## Procedure

1. **跑 `preflight.py`**，把输出读给用户听。完成条件：输出里给出"待审文件"路径，且没有 BLOCK 级错误。
   - 有未提交改动 → 先问用户要不要 `git stash` 或先提交，不要擅自丢弃
   - 当前在 main → 提示先建分支，不要直接在 main 上改
2. **告诉用户改哪份**：`drafts/` 下最新的 `..._审核包.docx`，改完另存为 `..._审回_<ID>.docx` 放进 `review-inbox/docs/`。
   完成条件：用户确认文件已就位。
3. **跑 `precheck_commit.py`**。完成条件：退出码 0。
   - 报 `_ops/` 或 `sources/` 被暂存 → `git reset HEAD <file>` 后重跑，这两个目录永不入库
   - 报文件名不合规 → 按提示改名，不改内容
4. **建分支并提交**，用 `references/pr-template.md` 里的标题/正文模板。完成条件：`git log -1` 显示本次提交。
5. **推送并开 PR**。完成条件：`gh pr create` 返回 PR 链接；把链接回给用户，并说明"PR 由维护者合并，你不要自己合"。
6. **失败时**：把 git/gh 的英文报错翻成一句中文原因 + 一条兜底（"把文件发群里，我来提"）。
   重试同一条命令最多一次，不要反复试。

## Pitfalls

- **别在主分支上改。** 分支保护会拒绝直接推 main；脚本会在 main 上给 WARN。
- **别用 `git add -A`。** 会顺手带进临时文件；只 add 具体的返稿文件。
- **docx 是二进制。** PR 里看不到逐行改动，正文说明要写清改了哪几段、哪几处拿不准。
- **`_ops/` 与 `sources/` 永不入库**：前者是维护区，后者是原文全文（版权）。
- **fork 与直推的区别**：没有 write 权限时 `git push` 会 403，这不是配置错误，改走 fork。
- **别删草稿行**：删除段落属于内容修改，超出本技能范围。

## Verification

- `python scripts/preflight.py` 输出 `READY`（无 BLOCK）
- `python scripts/precheck_commit.py` 退出码 0
- `gh pr view --json url,title` 能返回刚开的 PR
- PR 页面里 GitHub Actions 的 `pr-guard` 通过（检查路径与命名）

<!-- 跨工具说明：frontmatter 只保留 name/description/version/platforms 等通用字段，
     Claude Code 等工具可直接读；不支持 SKILL.md 的 agent 请把本文件当项目说明阅读，
     核心能力在 scripts/ 里，任何环境都能手动跑。 -->
