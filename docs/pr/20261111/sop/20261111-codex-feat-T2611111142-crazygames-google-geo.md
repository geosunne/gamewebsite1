# PR: codex/feat-T2611111142-crazygames-google-geo

## 背景与目标

基于 CrazyGames 导入器新增一批允许嵌入的游戏，报告实际新增数量，并依据 Google AI Overviews / AI Mode 的基础 SEO 要求更新页面内容、来源及结构化数据。

## 预检

- Problem：CrazyGames 来源仅有 25 个条目；导入器只按 slug 排重，缺少来源事实、设备及播放器可用性检查；详情页大量沿用泛化说明。
- Attempts：上轮已修复分类一致性、错误控制说明、来源指标及 404，当前基线 38ce028；工作区干净，现有 1366 个游戏。
- Scoped Code Pointers：CrazyGames 的 collect_slugs_from_category、fetch_game、build_game_record；生成器的说明覆盖表、game_facts、FAQ、JSON-LD；SEO 后处理及 sitemap。
- Open Items：核验当前来源结构、明确嵌入许可、去除名称变体、核对净新增数量及页面内容；所有改动和验证在任务 worktree 完成。

## 变更摘要

1. 默认目标 40 个新增条目，检查 177 个候选中的 86 个详情，最终净新增 40 个；CrazyGames 来源 25 → 65，站点目录 1366 → 1406。
2. 严格要求 allowEmbed 为布尔 true，检查播放器 HTTP、内容类型和框架限制；按 slug、名称、来源 ID 和嵌入地址去重，包括 Voxiom.io / Voxiom 名称变体。
3. 不覆盖旧条目；排除 Voxiom.io 的重复别名，并以 Designville 补足本批次，保留来源统计。
4. 新增来源开发者、设备支持、来源日期及抓取/播放器核对时间；保留完整控制说明，不再截断为 240 个字符。
5. 40 个新页面分别补充具体简介、操作、技巧和审阅日期，补充 House of Hazards 的多人控制与 Mirrorland 的账号要求。
6. 全站事实摘要只展示已知信息，增加来源链接和日期；取消一概无需账号的宣传，首页及目录 meta 使用真实游戏数量。
7. 使用 VideoGame 与 WebPage 区分游戏和站点页面，保留面包屑和可见 FAQ 对应关系；图片使用绝对地址，避免将 BTW game 写成原游戏发行方。
8. 对照 Schema.org 检查类型和属性范围，移除不适用于游戏类型的 additionalProperty、文本形式的 about，以及无来源依据的 Any 操作系统。
9. JSON-LD 转义小于号，避免来源字符串关闭 script；补充来源许可、身份去重、控制说明、框架限制、可见事实与结构化数据的一致性测试。

## 影响范围

导入器、生成器、SEO 后处理、说明覆盖表、CrazyGames 主数据、静态部署页面、40 张源/部署缩略图、构建文档和测试。未改数据库、Flask API、环境文件、首页布局或 CSS。

新增明细见 docs/logs/20261111/crazygames-import-google-geo.md。

## 验证结果

- 导入结果：40 个净新增；跳过不允许嵌入 43 个、重复身份 2 个、缺少游戏数据 1 个。
- 构建：1406 个游戏页、29 个分类页、5 个推荐页、5 个信息页及 404，生成错误 0。
- sitemap.xml / sitemap.txt：1448 个唯一 URL，覆盖全部新增页面，未将 404 纳入。
- 19 项回归测试全部通过；首页 P0 检查 16 通过、0 警告、0 失败。
- 40 个新页面均有专属说明、来源、核对时间及本地 320×200 WebP；新页面的 FAQ 与 JSON-LD 问答相同。
- 原有 1366 个游戏的 slug、嵌入地址和缩略图地址未改变。
- 浏览器检查：Block Blaster、Getaway Shootout、Mirrorland 主体和事实显示正常；390px 的事实摘要无横向溢出。
- 来源播放器进入启动画面并创建 Canvas；Block Blaster 的 18MB 资源加载过程中出现来源端连接提示，本轮验证不等于对全部 40 款游戏完成所有模式的联网试玩。
- git diff --check 通过；未把虚拟环境、缓存、截图、数据库或凭据加入提交。

## 风险与回滚

- 第三方播放器的联网、账号和资源加载取决于提供方；本轮仅核验来源许可、访问和抽查启动状态。
- Google 的 AI 搜索没有额外专用标记要求；本次改进不构成收录或展示保证。
- 当前为本地集成，未推送、部署、提交 Search Console 或发送 IndexNow。
- 回滚可撤销本任务合并，同时恢复数据、模板、生成产物及缩略图。

## 参考

- https://developers.google.com/search/docs/appearance/ai-features
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://schema.org/VideoGame
- https://schema.org/additionalProperty
