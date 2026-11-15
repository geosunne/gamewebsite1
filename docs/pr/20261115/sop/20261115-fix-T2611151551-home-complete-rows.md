# PR：首页货架整行布局修复

## 背景与预检

- 问题：Hot games、New games及分类货架存在残行；Hot的两张2×2大卡会被旧脚本按1格计数，其他货架要等window.load才整理。
- 已有尝试：已有基于总格数取模的尾卡裁切，但仅读取grid结束位置，并设有分类至少两行的限制；未覆盖卡片动态移除或容器独立变宽。
- 定位：generate_static_pages.py的render_home_grid_balance_script及首页选择数量；site.css的auto-fill、spotlight span及720/420响应式网格。
- 待验证：实际网格占位、窗口变化/NEW过期后恢复裁切卡片、少量/空状态及键盘焦点。
- 基线：2327ca5e，工作区干净；从spike/fullstack创建独立任务worktree。来源、游戏数量和第三方播放器不作变更。

## 变更摘要

独立home-grid.js读取CSS start/end两端span，模拟dense网格占位，保留最长完整矩形前缀。DOM ready立即执行；ResizeObserver只响应宽度变化，MutationObserver只观察直接子项，用requestAnimationFrame合并重排。缩放时恢复尾卡再计算，少量卡片缩减列数、空提示跨满整行，焦点卡被裁切时移向可见卡。完整目录入口保留，不复制游戏凑数。

## 验证结果

- 12屏宽×12首页分区共144组实际几何检查，无缺格；Hot两张2×2大卡计数正确。
- 容器独立宽度改变、NEW删除、5项目、全过期空提示和焦点恢复均通过。
- 45项回归、Python/JS语法、布局检测与diff检查通过。
- 目录1783款不变，all_games/new_games数据语义不变。完整证据见docs/logs/20261115/home-complete-rows.md。
- 发布后按对应main提交的Cloudflare回执和正式域名几何检查收口。

## 影响与回滚

仅首页货架排布与相关脚本/CSS，保持既有货架视觉、侧栏和大卡。尾部预览卡片会按容器宽度裁切，游戏本身仍在完整目录中。回滚本任务合并提交可恢复旧行为。
