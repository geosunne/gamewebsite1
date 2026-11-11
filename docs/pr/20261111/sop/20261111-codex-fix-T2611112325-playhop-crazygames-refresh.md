# PR: codex/fix-T2611112325-playhop-crazygames-refresh

## 背景与目标

移除线上 Epic Mine 所属的 23 个 Playhop 游戏，补充 200 个允许嵌入且不与原目录重复的 CrazyGames 游戏，并同步生成页面、导航入口、SEO 与 sitemap。

## 预检

- 问题：Playhop 的 frame-ancestors 不允许 BTW game，另有 4 个目标返回 404；共 23 个目录页使用这些地址。
- 已有证据：上一轮已检查线上响应与浏览器；当前 main 与 spike/fullstack 均为 7c25d9a，工作区干净。
- 定位入口：catalog_quality.py、generate_static_pages.py 的 prepare_catalog/build_static_catalog、两个导入器、optimize_seo.py、games_data.json 和静态产物。
- 待办：在独立 worktree 清理记录、扩大 CrazyGames 候选发现、补齐 200 个有效条目、重建并验证，最后本地合并。

## 变更摘要

- 构建及 OnlineGames 导入统一排除 Playhop 来源，原始数据移除 23 条，生成目录和游戏页不再引用它们。
- CrazyGames 导入增加已发布分类发现与批次续跑，新增恰好 200 项，来源总数 265，站点总数 1,583。
- 新增页使用实际来源说明与完整操作信息，手工说明覆盖保留；SEO 后处理不覆盖这些说明。
- 同步所有列表、详情、FAQ、JSON-LD、30 个分类、1,626 条 sitemap 和 200 张本地缩略图。
- 删除 23 个旧页面、46 张无引用缩略图，清理旧 slug 入口；未修改数据库或环境文件。

## 影响范围

来源数据、导入器、质量规则、静态生成与 SEO、回归测试、静态部署目录及源缩略图。无布局/CSS、后台认证或 API 合同变更。

## 验证结果

- 语法检查、完整生成/SEO/sitemap 流程、23 项回归测试及 git diff --check 均通过。
- 目录 1,406 - 23 + 200 = 1,583；新增身份与原 1,406 项无交集，其余 1,383 项的来源页/iframe/缩略图地址不变。
- 200 个新页 HTTP 200，23 个旧页 HTTP 404，1,626 个 HTML 文件的 25,740 个游戏链接无断链。
- 新增缩略图均为真实 320×200 WebP，元数据和 canonical 完整，title/description 无重复。
- Chrome 抽查首页、目录、Parking、2048 棋盘及 Skydom 启动画面，未见嵌入拒绝。
- 完整清单和证据边界：docs/logs/20261111/playhop-removal-crazygames-200.md。

## 风险与回滚

第三方资源、账号及联网能力由提供方决定；本轮未逐一完成 200 款游戏的完整流程。本轮仅本地集成，未推送部署或提交搜索平台。需要回滚时撤销本任务合并，连同来源数据、模板、页面和缩略图一起恢复。
