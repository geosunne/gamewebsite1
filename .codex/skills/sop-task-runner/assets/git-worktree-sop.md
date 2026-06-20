# Git Worktree 任务开发 SOP（本地合并版｜统一基线：spike/fullstack）

## 目标

* 避免同一目录/同一分支被多个任务并行修改导致覆盖
* 所有任务用 worktree 隔离开发，最终**在本地完成合并**
* 任意任务完成必须生成“PR 审阅单”（本地文件），形成可追溯审阅记录
* **自测必须在 worktree 中执行**，避免污染控制台目录

---

## 分支角色定义

* `main`：发布/稳定线（本地发布时由 `spike/fullstack` 合并进入）
* `spike/fullstack`：唯一开发集成线（所有任务分支都从这里拉、最终也合回这里）
* `feat/*` `fix/*` `chore/*`：任务分支（每任务一个）

---

## 强制规则（必须遵守）

1. **禁止从 `main` 拉任务分支**
2. **一个任务 = 一个分支 = 一个 worktree**
3. **任意任务“完成”的定义：必须生成 PR 审阅单（本地）**
4. **任务成果必须合并回 `spike/fullstack`（本地 merge）**
5. 控制台目录只当“指挥与合并”，不在控制台目录写业务代码/跑会写入的命令
6. **自测/构建/格式化/安装依赖/生成文件等所有可能产生写入的动作：只允许在 worktree 中运行**
7. 控制台目录长期必须保持 clean（`git status` clean）

---

## 命名规范

* `feat/<ticket>-<desc>`：新功能
* `fix/<ticket>-<desc>`：修复
* `chore/<desc>`：重构/工具/清理

示例：`feat/T123-upload-retry`

---

## 目录约定

* worktree 根目录：`../_wt/`
* worktree 目录名：分支名中的 `/` 替换为 `-`

  * `feat/T123-upload-retry` → `../_wt/feat-T123-upload-retry`

---

## 术语定义（审计口径）

* **控制台目录（Console Workspace）**：主仓库路径（repo root）

  * 仅用于：创建/管理 worktree、查看 Git 状态、以及任务完成后的本地合并回 `spike/fullstack`（以及发布时切 `main` 做 merge）
  * **必须长期保持 clean**
* **Worktree 目录（Dev Worktree）**：`../_wt/<branch>`

  * 唯一允许进行开发改动（代码/文档/配置/脚本/生成文件）的目录
  * 所有自测/构建/安装依赖等也在此运行

---

## 最高优先级规则：控制台目录零写入（零容忍）

> **极度禁止**在控制台目录对任何文件进行修改、生成、格式化、删除或新增。
> **所有改动必须且只能发生在 worktree 目录 `../_wt/<branch>` 中。**
> 任意违反一律视为**流程不合规**：变更**不得合并**，必须回滚并按 SOP 重做。

---

## 所有写操作必须显式落到 `$WT`

1. **凡是会动文件/目录的命令**（新增/修改/删除/拷贝/移动/生成产物/安装依赖/格式化/codegen/构建/测试写缓存等），**必须显式作用在 `$WT`**：

* 文件路径必须以 `"$WT/"` 开头（如 `mkdir -p "$WT/src/foo"`、`cp a "$WT/..."`）。
* 或命令显式在 `$WT` 目录执行：`git -C "$WT" ...` / `(cd "$WT" && <cmd>)`。

2. **Git 操作统一写法**：除“合并回 spike/fullstack / 清理 worktree”外，全部用：

```bash
git -C "$WT" <subcommand>
```

3. **控制台目录（repo root）零写入**：

* 禁止出现任何不带 `$WT` 前缀的写路径（如 `src/...`、`docs/...`、`./...`）。
* 在控制台目录只允许只读检查 + 合并/清理；其它一律视为不合规。

4. **硬门槛**：若 `$WT` 不存在 **或** `git -C "$WT" branch --show-current` ≠ `$BR`，**立即停止，禁止进入下一步**。

---

## 允许/禁止清单

### 控制台目录允许（白名单）

* `git worktree add/remove/prune/list`
* `git switch` / `git status` / `git log` / `git diff` / `git show`
* 任务完成后执行本地合并：

  * `git switch spike/fullstack`
  * `git merge --no-ff <branch>`
* 删除分支、清理 worktree
* **应急纠偏**：`stash` / `clean`（仅为恢复 clean，见应急章节）

### 控制台目录禁止（黑名单，包含但不限于）

* 使用 IDE/编辑器在控制台目录打开并保存任何文件（包括自动格式化/自动修复）
* 运行任何可能写入工作区的命令（lint fix / formatter / codegen / build / install 产生文件等）
* 对任何 tracked 文件或 `docs/` 做编辑、增删、移动
* 产生任何未跟踪文件、临时文件、构建产物、锁文件更新等

一句话：**控制台目录只负责“指挥与合并”，不负责“开发与写入”。**

---

# 标准流程（本地）

## A. 开始任务：创建 worktree + 分支（只从 spike/fullstack）

在**控制台目录（repo root）**执行（控制台只做只读检查 + worktree 管理）：

```bash
# 1) 切到唯一集成基线
git switch spike/fullstack

# 2) 必须保证控制台目录 clean（硬门槛）
git status

# 3) 定义分支与 worktree 目录
BR=feat/T123-upload-retry
WT=../_wt/${BR//\//-}

# 4) 防撞检查（推荐执行）
git worktree list

# 5) 创建 worktree（从 spike/fullstack 拉）
git worktree add -b "$BR" "$WT" spike/fullstack

# 6) 进入 worktree 后必须校验（硬门槛）
test -d "$WT"
git -C "$WT" branch --show-current

# 7) 创建后必须确保：控制台与 worktree 都是干净状态（硬门槛）
git status
git -C "$WT" status
```

**硬门槛（再次强调）**：若 `$WT` 不存在 **或** `git -C "$WT" branch --show-current` ≠ `$BR`，则立刻停止执行（退出/报错），**禁止进入下一步**。

要求：创建前确保**控制台目录与当前 worktree 都是干净状态**（`git status` / `git -C "$WT" status` 无未提交改动）。

---

## B. 开发 & 提交（小步提交）

在任务 worktree 中进行（统一使用 `git -C "$WT"`）：

```bash
git -C "$WT" status
git -C "$WT" add -A
git -C "$WT" commit -m "feat: xxx"
```

建议：每个 commit 都能独立说明“做了什么/为什么/影响面”。

---

## C. 自测（必须在 worktree 中）

> **自测/构建/安装依赖/格式化/生成文件**等所有可能写入操作，全部只能在 worktree 中执行，且必须显式落到 `$WT`。

在任务 worktree 中执行（按项目约定替换命令）：

```bash
# 示例（自行替换为项目命令）
# (cd "$WT" && pnpm test)
# (cd "$WT" && pnpm lint)
# (cd "$WT" && pnpm build)
```

---

## D. 任务完成：必须生成 PR 审阅单（本地文件）

> 由于不走远端 PR，本 SOP 将 PR 定义为“本地审阅单”，用于记录变更摘要、影响范围、验证方式、diff 关键点。
> **注意：此处涉及写文件，必须显式写入 `$WT/...` 路径。**

在任务 worktree 中执行（生成审阅单文件到 `$WT/docs/pr/...`）：

```bash
# 兜底：若新开 shell 没有 BR，则用 worktree 当前分支名
BR=${BR:-$(git -C "$WT" branch --show-current)}

mkdir -p "$WT/docs/pr"
PR_NOTE="$WT/docs/pr/$(date +%Y%m%d)-${BR//\//-}.md"

cat > "$PR_NOTE" <<EOF
# PR: $BR

## 变更摘要
- 

## 影响范围
- 

## 验证方式 / 结果
- 

## 关键 Diff（自检）
EOF

# 追加关键 diff（仅供自检/审阅）
git --no-pager -C "$WT" log --oneline --decorate -n 20 >> "$PR_NOTE"
printf "\n## Diff (spike/fullstack...HEAD)\n\n" >> "$PR_NOTE"
git --no-pager -C "$WT" diff --stat spike/fullstack...HEAD >> "$PR_NOTE"
```

最低要求：

* 审阅单必须存在
* 审阅单至少填：**变更摘要 / 影响范围 / 验证方式**

---

## E. 本地合并：合回 spike/fullstack（控制台目录执行）

回到**控制台目录（repo root）**执行（这是少数允许在控制台做的写入型 Git 动作：merge）：

```bash
git switch spike/fullstack

# 合并前必须保证控制台目录 clean（硬门槛）
git status

git merge --no-ff "$BR" -m "merge: $BR"

# 合并完成后必须回到 clean（允许合并过程中短暂状态，但结束必须 clean）
git status
```

> 合并后的验证如需执行，也必须显式在 worktree 中完成：`(cd "$WT" && <cmd>)`。
> 若需要验证 “spike/fullstack 合并态”，推荐额外创建一个专用 verify worktree 跑测试（避免污染控制台）。

---

## F. 清理 worktree

合并完成后，在控制台目录执行（允许）：

```bash
git worktree remove "$WT"
git worktree prune
git branch -d "$BR"
```

---

# 发布流程（本地）：spike/fullstack → main

当需要发布/进入稳定线时（在控制台目录执行）：

```bash
git switch main
git status
git merge --no-ff spike/fullstack -m "release: spike/fullstack -> main"
git status
```

---

# 应急处理：控制台目录出现改动（默认用 stash 恢复 clean）

> 允许在控制台目录执行 `stash` / `clean`，**目的仅限：让控制台目录恢复 clean** 后继续按 SOP。
> **禁止**把控制台目录的改动作为“正常开发成果”保留或提交。
> 若这些改动确实需要交付：必须**迁移到 worktree** 后再提交（控制台只做纠偏清理）。

## 标准应急流程（必须按顺序执行）

### 1) 收起控制台改动（含 untracked）

```bash
git stash push -u -m "console-dirty: <原因简述>"
```

### 2) 立刻确认控制台是否 clean（硬门槛）

```bash
git status
```

### 3) 仅当仍不 clean：清理 ignored 产物（谨慎）

> 只在你确认剩下的是可删的构建/缓存等 **ignored** 文件时使用。

```bash
git clean -fdX
git status
```

## 迁移说明（如 stash 内容需要交付）

* ✅ 正确做法：把 stash 的内容迁移到对应 worktree 后再提交
* ❌ 禁止做法：在控制台 `stash pop/apply` 后继续开发或直接 commit

推荐迁移方式（patch；写入落在 `/tmp`，不污染 repo root）：

```bash
# 控制台目录导出 patch（选一个 stash@{n}）
git stash list
git stash show -p stash@{0} > /tmp/console.patch

# 到目标 worktree 应用（显式落到 $WT）
git -C "$WT" apply /tmp/console.patch
git -C "$WT" status
# 然后在 worktree 内正常 add/commit
```

迁移确认无误后，可在控制台删除 stash：

```bash
git stash drop stash@{0}
```

> 应急处理结束的硬性要求：**控制台目录必须回到 clean，否则禁止继续“创建 worktree / 合并 / 清理 / 发布”等关键动作。**

---

# 禁止项（常见踩坑）

* ❌ 从 `main` 拉任务分支
* ❌ 在控制台目录直接写业务代码/改文件
* ❌ 在控制台目录跑会写入的命令（build/install/lint fix/codegen…）
* ❌ 一个分支承载多个任务
* ❌ 任务完成不生成 PR 审阅单
* ❌ 不经 merge（靠复制文件覆盖）把改动“合进去”
* ❌ 合并后控制台目录不 clean
* ❌ 出现任何不显式落到 `$WT` 的写路径（如 `docs/...`、`src/...`、`./...`）

---

# 合规判定（审计口径）

满足任一条即判定不合规、不得合并：

* 控制台目录出现与合并无关的工作区变更（`git status` 非 clean）
* 任意改动无法对应到 worktree 目录提交记录
* 未生成或未按要求填写 `docs/pr/<yyyymmdd>-<branch>.md`（该文件必须写入 `$WT/docs/pr/...`）
* 自测/构建/安装依赖等在控制台目录执行导致写入
* 任意写操作未显式落到 `$WT`（不带 `$WT/` 前缀、也不在 `git -C "$WT"` / `(cd "$WT" && ...)` 作用域内）

---

# 强制自检（必须执行）

* 在控制台目录进行任何关键动作前/后（创建 worktree、合并、清理、发布），必须确认：**`git status` 为 clean**
* 在进入任何“开发/自测/生成文件”步骤前，必须确认（硬门槛）：

  * `$WT` 存在：`test -d "$WT"`
  * 分支匹配：`git -C "$WT" branch --show-current` == `$BR`
  * worktree 干净：`git -C "$WT" status` 为 clean（除非你正在进行本次任务开发）

---

# 任务结束检查清单

* [ ] 我是在 worktree 目录里开发，且所有写操作都显式落到 `$WT`
* [ ] 分支来自 `spike/fullstack`
* [ ] 已提交必要 commit（小步提交）
* [ ] **自测已在 worktree 中执行并通过**
* [ ] **已生成 PR 审阅单（`$WT/docs/pr/...`）且填写完整**
* [ ] 已本地合并回 `spike/fullstack`
* [ ] 合并后控制台目录 `git status` 为 clean
* [ ] 每次任务结束必须删除功能分支（清理 worktree + prune + 删除任务分支）
