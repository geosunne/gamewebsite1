# CrazyGames 新增游戏与 Google AI 搜索内容更新

日期：2026-11-11。当前为本地构建结果，尚未推送或部署。

## 更新数量

- 本轮净新增：40 款。
- 站点游戏目录：1366 → 1406。
- CrazyGames 来源目录：25 → 65。
- 检查游戏详情：86 个；跳过不允许嵌入 43 个、重复名称/身份 2 个、缺少游戏数据 1 个。
- 29 个分类继续保留；sitemap.xml 与 sitemap.txt 均为 1448 个唯一 URL。
- 40 张新增缩略图均缓存为本地 320×200 WebP；原有 1366 个游戏的嵌入地址和缩略图地址未改变。

## 页面更新

- 40 个新增页面分别补充具体玩法摘要、操作步骤和针对性提示，保留完整来源控制说明。
- 事实摘要标注来源提供的开发者、设备支持、价格和下载要求，未知信息不作推断。
- Mirrorland 明确标注来源要求账号；全站删除一概无需账号的承诺，区分浏览目录与第三方游戏账号。
- 增加来源链接、抓取核对日期和说明审阅日期；日期不当作游戏实际发布时间。
- VideoGame 与 WebPage 分别表示游戏实体与 BTW game 页面；BTW game 仅作为页面发布者，不冒充游戏发行方。使用类型支持的标准字段，未知操作系统不标成 Any。
- JSON-LD 的事实字段与可见文本共用数据；图片地址统一为绝对 URL，FAQ 与页面问答一致。
- 首页及目录 meta 使用实际目录数量，新增页面通过普通链接、分类和 sitemap 被发现。

## 验证

- 19 项回归测试全部通过，包括嵌入许可、身份去重、完整控制说明、来源指标、脚本转义、正文/结构化数据一致性、全站分类链接、404 与新增缩略图。
- 浏览器抽查 Block Blaster、Getaway Shootout、Mirrorland 的页面与来源播放器入口，及 390px 的事实摘要；信息区和主体无横向溢出。
- 来源播放器可进入启动页面并创建游戏 Canvas；大型资源与联网状态仍由第三方服务控制，本轮不代表对 40 款游戏所有模式完成试玩。
- 未执行 Google Search Console 提交、线上发布或 IndexNow 提交。

## Google 官方依据

[AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) 说明 AI Overviews / AI Mode 沿用基础 SEO 要求，重要信息应以文本提供，结构化数据应与可见内容一致；无需专用 AI 文件或特殊 Schema。

[Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) 用于本轮具体玩法、来源核对及避免无依据断言的内容标准。

## 新增清单

页面地址为发布后的规范路径；设备支持与开发者来自 CrazyGames 当前来源记录。

| 游戏 | 页面地址 | 分类 | 开发者 | 来源标注设备 |
| --- | --- | --- | --- | --- |
| Block Blaster | /games/block-puzzle-master | Puzzle | Onki Games | Desktop, Android, iOS |
| Build and Crush | /games/build-and-crush | Simulation | Ctrl4ltDel | Desktop |
| Getaway Shootout | /games/getaway-shootout | Two Player | New Eich Games | Desktop, Android, iOS |
| Mr. Dude: Online Multiverse Challenge | /games/mr-dude-online-multiverse-challenge | Action | SeriousGames | Desktop, Android, iOS |
| Far Orion: New Worlds | /games/far-orion-new-worlds | Strategy | FITGAME | Desktop, Android, iOS |
| Battleship | /games/battleship | Strategy | 来源未提供 | Desktop, Android, iOS |
| Duck Life | /games/ducklife | Simulation | Wix Games | Desktop |
| Cuphead | /games/cuphead | Shooter | StudioMDHR | Desktop |
| House of Hazards | /games/house-of-hazards | Two Player | New Eich Games | Desktop |
| Dead Land: Survival | /games/dead-land-survival | Survival | FITGAME | Desktop, Android, iOS |
| Pirates of the Caribbean: ToW | /games/pirates-of-the-caribbean-tow | Strategy | 来源未提供 | Desktop |
| Warlord: Fantasy RPG | /games/warlord-fantasy-rpg | Strategy | FITGAME | Desktop |
| Magic World | /games/magic-world | Match & Merge | 来源未提供 | Desktop, Android, iOS |
| Heroes Assemble | /games/heroes-assemble | Strategy | gzwegame | Desktop, Android, iOS |
| Castle Craft | /games/castle-craft | Match & Merge | Vanuplay Innovations Inc | Desktop, Android, iOS |
| Daily Room Escape | /games/daily-room-escape | Puzzle | The Article 19 Group | Desktop, Android, iOS |
| Battle Arena | /games/battle-arena | Strategy | RED BRIX WALL | Desktop, Android, iOS |
| Hex Empire | /games/hex-empire | Strategy | Meta Sauce | Desktop |
| Dark Stones: Card Battle RPG | /games/dark-stones-card-battle-rpg | Strategy | almagames | Desktop, Android, iOS |
| Mirrorland | /games/mirrorland | Strategy | Hitmakers | Desktop, Android |
| Ragdoll Archers | /games/ragdoll-archers | Shooter | Ericetto | Desktop, Android, iOS |
| Stone Grass: Mowing Simulator | /games/stone-grass-mowing-simulator | Simulation | FreePlay LLC | Desktop, Android, iOS |
| Arkadium's Bubble Shooter | /games/arkadium-s-bubble-shooter | Match & Merge | Arkadium | Desktop, Android, iOS |
| Bubble Blast | /games/bubble-blast-pwd | Match & Merge | Mnogoigrovka | Desktop, Android, iOS |
| Lumber Harvest: Tree Cutting Game | /games/lumber-harvest-tree-cutting-game | Simulation | FreePlay LLC | Desktop, Android, iOS |
| Count Masters: Stickman Games | /games/count-masters-stickman-games | Runner | FreePlay LLC | Desktop, Android, iOS |
| Bubble Fall | /games/bubble-fall | Match & Merge | SUN.STUDIO | Desktop, Android, iOS |
| Bubble Tower 3D | /games/bubble-tower-3d | Match & Merge | Famobi | Desktop, Android, iOS |
| Geometry Game | /games/geometry-dash-online | Platformer | 来源未提供 | Desktop, Android, iOS |
| Getting Over It | /games/getting-over-it | Platformer | Griffpatch | Desktop, Android, iOS |
| Squirrel with a Gun! | /games/squirrel-with-a-gun | Shooter | Mirra Games | Desktop, Android, iOS |
| Jet Rush | /games/jet-rush | Runner | 来源未提供 | Desktop, Android, iOS |
| Color Tunnel | /games/color-tunnel | Runner | Royale Gamers | Desktop |
| Stacky Bird | /games/stacky-bird | Runner | Kooapps | Desktop, Android, iOS |
| Piece of Cake: Merge and Bake | /games/piece-of-cake-merge-and-bake | Match & Merge | HG POINT LTD | Desktop, Android, iOS |
| Hidden Objects | /games/hidden-objects | Puzzle | Morion Studio | Desktop, Android, iOS |
| Color Tap: Coloring by Numbers | /games/color-tap-coloring-by-numbers | Casual | Blockbyte Games | Desktop, Android, iOS |
| Screw Out: Bolts and Nuts | /games/screw-out-bolts-and-nuts | Puzzle | Vkusnyatina | Desktop, Android, iOS |
| Farm Merge Valley | /games/farm-merge-valley | Management | 来源未提供 | Desktop, Android, iOS |
| Designville: Merge & Design | /games/designville-merge-design | Match & Merge | TAPCLAP | Desktop, Android |
