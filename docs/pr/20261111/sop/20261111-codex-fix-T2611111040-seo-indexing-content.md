# PR: codex/fix-T2611111040-seo-indexing-content

## 背景与目标

修复 SEO 审计前四项问题：线上未知路径返回首页 200、游戏说明串入其他游戏内容、分类数据与详情页不一致、外部赞票/热度混入本站游玩次数。

## 开工预检

- Problem：Cloudflare Pages 缺少部署根目录 404.html；22 个详情页的分类与目录不同；3 个分类地址没有页面；Tiny Clash 等条目的控制说明来自其他游戏。
- Attempts：已核查线上状态码、全站静态链接、1366 条目录数据与历史 PR；历史说明模板仍因 io 子串误判生成竞技玩法。
- Scoped Code Pointers：生成器的 normalize_game_data、generate_listing_pages、generate_game_page；Minigame 的固定长度文本截取；CrazyGames 的 upvotes 字段映射；本地静态服务器及跳转生成器。
- Open Items：在隔离 worktree 重建和验证全部产物；部署后再核验线上 404。未做远端推送、部署或 IndexNow 提交。
- 基线：spike/fullstack 先从当前 main 快进同步，再创建任务 worktree；控制台目录保持干净。

## 变更摘要

1. 生成带 noindex 的部署根目录 404.html，提供游戏目录及推荐游戏入口；本地未知路径 GET/HEAD 返回真实 404，并使用同一份页面。
2. Minigame 按当前 app_id 解析完整 Flight 数据记录，处理引用、转义字符串和按 UTF-8 字节计数的文本记录，避免混入推荐游戏。
3. 重新核对 844 个 Minigame 条目：825 个取得当前记录；19 个源站记录无法确认，移除不可信控制说明及旧长描述，清空不可信标签，保留原游戏与缩略图地址并标记待复核。
4. 补充 Tiny Clash、Classic Sudoku、Papa's Donuteria、Dinosaur Game 和 Geometry Jump 的具体说明及分类修正；普通说明按明确分类生成，避免把 simulation/action 误认为 io。
5. 分类只在 prepare_catalog 计算一次；目录、详情页及面包屑使用同一结果，相关分类只链接实际生成的页面。
6. 清理不再生成的分类 HTML；旧 Arcade、Parking、Multiplayer、Clicker 和 Adventure 入口由同一规则生成 308 兼容跳转，本地预览与部署配置一致。
7. 外部评分、CrazyGames 赞票及 Minigame 热度分别保存为 source_rating、source_upvotes 和 source_popularity；不再计入本站 total_plays，详情页注明评分和赞票来源。
8. 增加从完整目录快照重建的选项，避免依赖本地 Flask/API；同步静态部署产物及构建文档。

## 验证

影响范围：静态生成器、两个外部来源导入器、共享数据校正规则、SEO 后处理、sitemap/兼容跳转、本地静态服务、存量来源 JSON、静态部署产物及回归测试。未修改 Flask API 或数据库。

- Python 语法检查：通过。
- 生成 1366 个游戏详情页、29 个分类页、5 个推荐页、5 个信息页及 404.html，生成错误 0。
- sitemap.xml 与 sitemap.txt 均包含 1408 个唯一 URL，错误页不进入 sitemap。
- 回归测试覆盖当前记录解析、推荐内容隔离、指标迁移幂等性、io 误判、分类回退、全站分类链接、目录/详情分类一致性、修正后的操作说明及 GET/HEAD 404。
- 最终 11 项回归测试全部通过；仅保留原有 utcnow 调用在 Python 3.14 下的弃用提示，不影响测试。
- 实际 HTTP 检查：17 个旧分类/游戏 URL 的 308 与 Location 正确，兼容查询参数；首页、目录、Puzzle 分类、Tiny Clash 均返回 200。
- 浏览器检查：404 页面在 1440px 和 390px 下均返回 404，包含 noindex，无横向溢出，6 张推荐缩略图正常显示；Layers Roll 明确展示 CrazyGames 评分和赞票，不显示虚构本站游玩量。
- 重复构建前后全量 games 数组的 SHA-256 一致；全部 1366 个 slug、iframe_url 和 thumbnail_url 均保留原值。
- 错误套用的竞技提示从 896 页减少至实际 io 分类的 21 页；目录与详情分类不一致数和失效分类链接均为 0。
- git diff --check 通过，语法检查通过；未提交环境文件、数据库、虚拟环境、下载缓存和浏览器截图。

## 待复核记录

源站未返回可确认的当前游戏记录：merge-rush-z、minis-ball、plants-vs-zombies、horror-spranky-beats、crowd-city、bus-jam、hopball-3d、goods-master、decompression-game、toy-adventure、fish-go-io、music-party、triple-match、fingertip-piano、screw-pin-puzzle、bike-rush、lovely-doll-creator、jigsort-puzzles、dreader-horror-maze。

## 风险与回滚

- 页面内容与分类来源已经修正，不代表对 1366 个嵌入游戏逐个完成试玩。
- 线上 404 修复需要部署包含根目录 404.html 的静态产物后生效。
- 外部热度仅作为目录排序信号，不能解释为本站游玩量。
- 修改数据库、环境变量、后台 API 和未授权的其他 SEO 优化项不在本次范围内。
- 回滚可撤销本任务合并；本轮保留全部 1366 个游戏 URL。
