# PR: chore/T260620-git-repository-hygiene

## 背景 / 目标
- 将当前项目补齐为更规范的 Git 仓库使用状态。
- 安装并纳入项目本地 `sop-task-runner` Skill。
- 建立 `spike/fullstack` 作为 SOP 集成基线，并记录后续 worktree 开发约定。

## 变更摘要
- 新增 `.gitignore`，覆盖系统文件、环境变量、本地数据库、Python 缓存、虚拟环境、本地工具状态和临时产物。
- 将 `.codex/skills/sop-task-runner/` 纳入项目，包含 Skill 主文件、TOML 配置、参考说明和模板资产。
- 更新 `AGENTS.md`，记录 `spike/fullstack` 已作为 SOP 集成基线。

## 影响范围
- 仅影响 Git 仓库协作配置、项目本地 Skill 和协作说明。
- 不改动 Flask 应用、静态页面生成逻辑、数据库模型或线上静态产物。

## 风险与回滚
- `.gitignore` 不会自动移除已经被 Git 跟踪的 `.env`、数据库、`__pycache__`、`.impeccable` 等历史文件。
- 如需彻底治理，后续应单独执行一次敏感/生成文件清理，并评估是否需要从 Git 历史中清除敏感信息。
- 回滚方式：撤销本分支 merge，或 revert 本次提交。

## 验证方式 / 结果
- `git status --short --branch`：worktree 提交前后状态符合预期。
- `git branch --list 'spike/fullstack' 'main'`：已建立 `spike/fullstack` 基线分支。
- `find .codex/skills/sop-task-runner -maxdepth 3 -type f`：Skill 文件完整。
- `git ls-files | rg '(^\.env$|^\.env\.local$|\.db$|^venv/|__pycache__|\.impeccable/|backup|\.pyc$)'`：发现历史已跟踪敏感/生成文件，已记录风险，未在本任务中批量删除。

## 关键 Diff（自检）
6a743c8 (HEAD -> chore/T260620-git-repository-hygiene) chore: add git hygiene and sop runner skill
5b6735d (origin/main, origin/HEAD, spike/fullstack, main) Avoid trailing slash redirects for game pages
d84975f Add static data fallback for game API
8d60e38 Fix games page asset path
5ee4704 Merge codex/clean-url-site
757957e (codex/clean-url-site) Add product and design system docs
89571bd (origin/codex/clean-url-site) Use clean URLs for static game pages
5d1d48b Fix static SEO and game routes
d3fbddc add sitemap.xml change
b2d946b text change
438e2a3 change the text
a03c698 change the ad tag
a3af13c install monetag ads
3ea1f73 monetag
6141184 一些非静态页面的修改
cf10df0 修改了游戏的分类
de41cbf 增加了大量新游戏，更新了sitemap.xml和sitemap.txt
eb6aaf0 modify sitemap.xml
b6a0d59 add ads.txt
f3f72e9 add logo

## Diff (spike/fullstack...HEAD)

 .codex/skills/sop-task-runner/SKILL.md             | 367 ++++++++++++++++++++
 .codex/skills/sop-task-runner/SKILL.toml           |   6 +
 .../sop-task-runner/assets/git-worktree-sop.md     | 375 +++++++++++++++++++++
 .../sop-task-runner/assets/pr_note_template.md     |  15 +
 .codex/skills/sop-task-runner/references/README.md |   7 +
 .gitignore                                         |  38 +++
 AGENTS.md                                          |   7 +-
 7 files changed, 814 insertions(+), 1 deletion(-)
