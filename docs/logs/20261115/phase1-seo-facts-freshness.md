# BTW game 第一阶段：事实与真实更新信号

日期：2026-11-15。基线：e790cd5218e00bad28594b4ddd760bc5b795ed4f。

## 交付结果

- 游戏目录保持1,783款、31分类、1,827个sitemap URL；slug、标题、来源ID、来源页、iframe和缩略图地址的整体身份摘要与基线完全一致。本阶段净新增和移除均为0。
- 20个重点游戏来源说明已复核，均有完整来源控制说明；iframe均通过HTTP200、HTML类型、重定向、X-Frame-Options和CSP检查。这是地址及元数据证据，不是20款完整试玩。
- 19个Minigame条目仍无法获取可确认的当前游戏记录，保留`needs_review`并在事实卡、操作说明及FAQ中明确待确认；不据此认定游戏下架，也未编造操作或设备支持。
- 缺少控制元数据从604条降至603条；本阶段优先完成20个重点页面，其余缺失项继续以明确的未确认状态展示。
- 根据Git首次页面加入记录恢复全部游戏的首次收录日期，追踪重命名历史；NEW按14天窗口计算，1,782→423。来源发布日期、元数据刷新和构建时间不会重新激活NEW。浏览器、NEW筛选、兼容API和new_games.json使用相同时间窗口；无新游戏时不再用旧游戏补位。
- 修正Space Waves、Duck Life 4为Arcade；Minis Ball回退为Casual；Pool Club依据源数据回退为Sports。明确的玩法描述优先于泛化关键词，避免world等泛词抢占Simulation分类；目录、详情、FAQ、结构化数据及相关分类同步。
- 首页不再把混合排序说明成本站玩家最常打开；明确来源赞票、来源热度和历史目录计数的差异。详情将历史数值标为Catalog play count；编辑政策公开排序依据与核验范围。
- 来源核对、编辑审核、播放器观察各有独立记录。自动导入只产生来源核对时间，不再自动宣称编辑review。未知账号和设备条件明确标为未确认；Mirrorland的账号要求由来源正文和播放器账号提示共同支持。

## 页面日期与构建

site_content_dates.py维护公开页面内容指纹及lastmod；static_html/content_dates.json是可核对的日期清单。两条sitemap生成入口共用同一实现，页面可见日期、WebPage/CollectionPage dateModified及sitemap lastmod保持一致。

指纹排除自身更新时间以及来源/审核/播放器核对时间；仅重查来源、调整JSON-LD键顺序或重新构建不会制造内容更新。页面正文、事实或相关链接发生变化时才记录新日期。首次迁移从旧sitemap保留既有日期。

本轮对通用事实展示、说明文案和日期展示做了实际变更，大部分页面本次日期为11月15日；这不是为了让每轮构建重复更新日期。重复构建验证确认：1,827页面的指纹、HTML字节、两个静态源页面以及games数组完全不变。较新的来源和独立播放器/编辑记录不会被较旧的复核覆盖回退。

## 验证结果

- 41项unittest通过，包含Node.js退役边缘行为、Python/浏览器14天边界、来源日期与编辑审核分离、缺失说明展示、来源与独立观察的新旧记录合并、真实内容变更与重复构建测试。
- Python语法、两个浏览器JS语法、git diff --check通过；本轮设计检测无新增发现。
- 全目录审计：1,783个游戏页、可见FAQ/Schema、canonical、页面日期、NEW目录、31分类、sitemap一致；115,399个内部链接/资源引用无缺失。
- 浏览器：首页排序说明、NEW筛选423项、Space Waves事实与日期、Mirrorland账号要求、待确认页面和390px窄屏说明已检查。窄屏说明面板宽366px，文案可见。
- 播放器仅作有限观察：Space Waves教程画面；Mirrorland账号要求画面，未注册账户或进入玩法；Dinosaur Game有画布但未确认可玩画面。未逐款完整试玩。

## 抓取核查边界

Requests的15次公开探测均200；真实urllib客户端对robots、sitemap、详情三个路径返回Cloudflare403/1010。不同客户端的结果不能直接代表真实Google、Bing或AI搜索机器人。

Cloudflare仍需登录；现有Chrome的Google账户已登录Search Console，但没有btwgame.com资源访问权，也没有已配置API凭据，因此真实机器人日志、Google选择的canonical和索引结果尚未核验。待核验步骤与回执范围见crawler-access-followup.md；没有修改防火墙配置或承诺索引、排名和引用增长。

## 文件与发布

- phase1-source-audit.json：20重点＋19待确认的来源与HTTP证据。
- phase1-baseline.json：初始目录身份摘要。
- full-catalog-validation.json：全目录核验。
- repeat-build-validation.json：重复构建证明。
- crawler-access-check.json、crawler-access-followup.md：公开抓取探测和未完成的账户内核验。
- category-corrections.json：分类前后对照。
- catalog_fact_checks.json：生成器应用的事实核对记录。

本报告记录提交前验证；对应main SHA、Cloudflare部署及真实域名核验以本轮自动化运行记录和最终聊天结果为准。保留既有Cloudflare Pages Git集成，按授权合并并推送后核查对应提交。
