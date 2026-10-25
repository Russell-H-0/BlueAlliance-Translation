# 四条命令走完一次交稿

只记这四条就够。全部在仓库目录里执行。

```bash
# 0) 第一次：把仓库拿到本地（只需一次）
git clone https://github.com/Russell-H-0/BlueAlliance-Translation.git
cd BlueAlliance-Translation

# 1) 每次开工前：取最新
git pull --ff-only

# 2) 改稿前：建自己的分支（名字自定，别用 main）
git checkout -b review/wallace-extension-yourid

# 3) 改完：把返稿文件放进 review-inbox/docs/，然后
git add review-inbox/docs/2026-10-27_wallace-extension_审回_yourid.docx
git commit -m "审回：华莱士续约（@yourid）"

# 4) 推上去（第一次加 -u）
git push -u origin HEAD
gh pr create --fill          # 没有 gh 就到网页点 "Compare & pull request"
```

## 没被邀请成协作者怎么办（fork 路线）

公开仓库人人都能读，但不是人人能直接推。push 报 403 时走这条：

1. 网页点右上角 **Fork**，得到 `你的账号/BlueAlliance-Translation`
2. `git remote add fork https://github.com/<你的账号>/BlueAlliance-Translation.git`
3. `git push -u fork HEAD`
4. 网页进你自己的 fork，点 **Contribute → Open pull request**

维护者合并后，你的 PR 会显示 Merged。

## 报错对照表

| 报错 | 真实原因 | 怎么办 |
|---|---|---|
| `403 Permission denied` | 没有写权限 | 走 fork 路线 |
| `Authentication failed` | 凭据过期 | `gh auth login` 重新登录，或配 SSH key |
| `Updates were rejected` | 远端有新提交 | 先 `git pull --rebase` 再推 |
| `CONFLICT (content)` | 同一文件两人改 | 别硬合并：把文件发群里，让维护者处理 |
| `fatal: not a git repository` | 不在仓库目录 | `cd` 到仓库根，或先 clone |
| `could not read Username` | 没配认证 | `gh auth login` |
| `failed to connect` / 超时 | 网络不通 | 放弃 git，改微信发文件 |

## 三条纪律

- 只在 `review/` 开头的分支上改，**不碰 main**
- 不 `git add -A`，只 add 自己那份文件
- `_ops/` 和 `sources/` 永远不入库，看到它们出现在暂存区就 `git reset HEAD <文件>`
