# 安装说明（3 分钟）

这个技能只帮你搬运文件：拉稿、命名、提交、开 PR。**它不审稿；校对还是你自己做。**

## 先做一件事：确认能跑

在仓库目录里执行：

```bash
python skills/ba-git-sync/scripts/preflight.py
```

- 看到 `[结果] READY` → 你机器上能跑，继续看下面装法
- 看到 `[BLOCK]` 或报错 → 把输出整段发群里，别自己猜

## 装法一：Hermes

```bash
# 把技能目录拷到 Hermes 的 skills 目录（Windows 示例路径）
mkdir -p "$HOME/.hermes/skills/translation"        # Linux/macOS
# Windows: %USERPROFILE%\.hermes\skills\translation\
cp -r skills/ba-git-sync "$HOME/.hermes/skills/translation/"
```

新开一个会话，说「帮我拉最新稿件」或「我要审这篇」，技能就会被调起。

## 装法二：Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r skills/ba-git-sync ~/.claude/skills/
```

`SKILL.md` 的 frontmatter 只用了 `name` / `description` 这类通用字段；如果加载报错，
把 `version`、`author`、`license`、`platforms` 四行删掉再试。

## 装法三：不用技能，手动跑

不装也能干完活：

```bash
python skills/ba-git-sync/scripts/preflight.py        # 看该审哪份
# ……在 Word 里改稿，存成 ..._审回_<你的ID>.docx 放进 review-inbox/docs/
python skills/ba-git-sync/scripts/precheck_commit.py  # 提交前自检
```

然后照 `references/git-four-commands.md` 敲四条命令。

## 前置条件

| 需要 | 怎么确认 | 常见问题 |
|---|---|---|
| git | `git --version` | 没装就去 git-scm.com；Windows 装完要用 Git Bash |
| gh（要开 PR 才需要） | `gh auth status` | 没登录就 `gh auth login`，选 HTTPS + 浏览器登录 |
| python3 | `python --version` | Windows 用 `python`，Linux/macOS 用 `python3` |

## 两种身份，先搞清楚自己是哪种

- **被邀请成协作者**：能直接推分支、直接开 PR。群里找维护者要邀请。
- **没被邀请**：公开仓库谁都能读，但不能直接推——走 fork + PR（`references/git-four-commands.md` 有步骤）。
  嫌麻烦就别用 git，把文件发群里，一样算你一份校对。

## 版本

当前 `0.1.0`。规则变了会升版本号并在群里说一句，届时重新 `git pull` 再拷一次技能目录即可。
