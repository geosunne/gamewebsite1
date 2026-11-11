# Playhop 清理与 CrazyGames 补充

日期：2026-11-11

## 结果

- 游戏目录：1,406 - 23 + 200 = 1,583；CrazyGames 来源：65 → 265。
- 分类：29 → 30；新增数据使 Parking 达到独立分类阈值，沿用现有分类规则。
- sitemap.xml / sitemap.txt：1,626 个唯一 URL，覆盖 1,583 个游戏、30 个分类、首页、游戏目录及 11 个信息/GEO 地址。
- 原始 OnlineGames 导入文件删除 23 条 Playhop 记录：508 → 485；未改其他来源记录。
- 删除 23 个生成游戏页和 46 张不再引用的源/部署缩略图；原始游戏 slug 清单同步删除这些入口。
- 其余 1,383 个旧游戏的来源页、iframe 和缩略图地址保持一致。

## 导入与防回归

1. 通过原有 CrazyGames 导入器扫描默认入口及首页实际发布的分类/标签；两轮完成 62 + 138 = 200 个净新增。
2. 每个新增都要求来源 allowEmbed 为布尔 true，且 iframe HTTP、HTML 内容类型、重定向、X-Frame-Options 和 CSP frame-ancestors 检查通过。
3. 按 slug、标题、CrazyGames 来源 ID 和 iframe 地址去重；200 个新增与调整前全部 1,406 个旧条目均无身份交集。
4. 新增 --discover-categories 与 --resume；续跑的 --limit 表示同一批次累计目标，metadata.latest_import.added_slugs 保存本批次完整 200 项。
5. 累计执行 473 次详情检查（包含续跑重复检查）；跳过 257 次无嵌入许可、7 次重复身份及 9 次缺少来源详情数据。
6. 新页使用来源简介、How to Play、Controls 和 Tips；缺少技巧时只补充通用浏览器提示。手工说明覆盖仍优先，SEO 后处理与页面使用同一份说明。
7. 生成器统一排除 Playhop 主域及子域；原始 OnlineGames 导入器也跳过这些地址，防止未来重新抓取或数据库重建后恢复失效页面。

## 验证

- 语法检查通过：导入器、质量规则、生成器、SEO、sitemap 和本地服务。
- 全量构建成功：1,583 个游戏页、30 个分类页、5 个推荐页、5 个信息页及 404；生成错误 0。
- test_seo_repairs 与 test_crazygames_geo：23 项测试全部通过。
- 新增 200 个页面 HTTP 200；移除 23 个页面 HTTP 404。
- 扫描 1,626 个 HTML 文件中的 25,740 个游戏链接，断链 0；页面 iframe 无 Playhop 地址。
- 新增 200 项均有源和部署两份真实 320×200 WebP 缩略图；title、description、canonical 和单个 H1 存在，新增 title/description 无重复。
- 新增 FAQ 与可见问答对应，来源及核对时间保留；sitemap 无旧 23 项、.html 或非首页尾斜杠 URL。
- Chrome 抽查：首页与目录、Parking 分类、2048 棋盘及 Skydom 启动画面；抽查页未见横向溢出或坏图。
- git diff --check 通过；未提交虚拟环境、数据库、环境变量、历史抓取备份或浏览器截图。

## 发布边界

本轮完成本地提交并合并至 spike/fullstack；未推送 main、未部署、未提交 Search Console 或 IndexNow。播放器已做来源许可和响应检查及上述浏览器抽查，不代表逐款完成全部玩法和联网流程。

## 移除的 23 个游戏

| 游戏 | Slug |
|---|---|
| Obby But You're on a Bike | obby-but-youre-on-a-bike |
| TB World | tb-world |
| Granny | granny |
| DTA 6 | dta-6 |
| Survival Race | survival-race |
| Thief Puzzle | thief-puzzle |
| Only Up Obby | only-up-obby |
| Granny 2 | granny-2 |
| Obby Prison Escape | obby-prison-escape |
| Idle Vlogger | idle-vlogger |
| Immortal: Dark Slayer | immortal-dark-slayer |
| Chess | chess |
| Obby: Find 100 Cats | obby-find-100-cats |
| Five Nights At Candy's | five-nights-at-candys |
| Five Nights At Cat Freddy | five-nights-at-cat-freddy |
| Obby: Parkour Lava | obby-parkour-lava |
| Obby: Draw and Jump | obby-draw-and-jump |
| Space Waves | space-waves |
| Rainbow Obby Parkour | rainbow-obby-parkour |
| Jelly Car Simulator | jelly-car-simulator |
| Obby: Find Sprunki | obby-find-sprunki |
| Epic Mine | epic-mine |
| Words of Wonders | words-of-wonders |

## 新增的 200 个游戏

| 游戏 | Slug | 分类 |
|---|---|---|
| Mahjong Connect (Legacy) | mahjong-connect-1 | Mahjong & Card |
| Skydom | skydom | Match & Merge |
| Skydom: Reforged | skydom-reforged | Match & Merge |
| Wood Block Journey | wood-block-journey | Match & Merge |
| 2048 | 2048 | Match & Merge |
| Little Alchemy 2 | little-alchemy-2 | Survival |
| Marble Run | marble-run | Simulation |
| Word Scramble | word-scramble | Word & Trivia |
| Candy Riddles | candy-riddles | Cooking |
| Fairyland Merge & Magic | fairyland-merge-and-magic | Survival |
| Tropical Merge | tropical-merge | Management |
| Mahjong Online | mahjong-classic-webgl | Mahjong & Card |
| Classic Solitaire | classic-solitaire | Mahjong & Card |
| Spider Solitaire 2 Suits | spider-solitaire-2-suits | Mahjong & Card |
| Golf Solitaire | golf-solitaire | Mahjong & Card |
| 10x10 | 10x10 | Match & Merge |
| Sandtrix | sandtrix | Match & Merge |
| BlockBuster Puzzle | blockbuster-puzzle | Match & Merge |
| Yahtzee Online | yahtzee-online | Puzzle |
| Poly Art | poly-art-3d | Puzzle |
| Escape or Die | escape-or-die | Puzzle |
| Creepy Granny Scream: Scary Freddy | creepy-granny-scream-scary-freddy | Horror |
| Bolts and Nuts | bolts-and-nuts | Shooter |
| Cut the Rope | cut-the-rope-ebx | Match & Merge |
| Nonogram | nonogram | Puzzle |
| 8 Ball Pool Billiards Multiplayer | 8-ball-pool-billiards-multiplayer | Mahjong & Card |
| 8 Ball Billiards Classic | 8-ball-billiards-classic | Mahjong & Card |
| Mini Golf Club | mini-golf-club | Two Player |
| Crazy Flips 3D | crazy-flips-3d | Sports |
| 2 Minute Football QB Legend | qb-legend | Soccer |
| Table Tennis World Tour | table-tennis-world-tour | Sports |
| Baseball | baseball | Sports |
| 3D Bowling | 3d-bowling | Two Player |
| Ragdoll Soccer 2 Players | ragdoll-soccer-2-players | Two Player |
| Penalty Shooters 2 | penalty-shooters-2 | Soccer |
| Basketball Superstars | basketball-superstars | Basketball |
| Basketball Orbit | basketball-orbit | Basketball |
| The Speedy Golf | speedy-golf | Sports |
| Return Man 2 | return-man-2 | Soccer |
| 4th and Goal 2019 | 4th-and-goal-2019 | Soccer |
| Wrestle Bros | wrestle-bros | Two Player |
| Swords and Sandals 2 | swords-and-sandals-2 | Action |
| Bowman | bowman | Two Player |
| Traffic Rider | traffic-rider-vvq | Racing |
| Racing Limits | racing-limits | Two Player |
| Sky Riders | sky-riders-buk | Driving |
| Rally Racer Dirt | rally-racer-dirt | Two Player |
| Demolition Derby 3 | demolition-derby-3 | Racing |
| MX Offroad Master | mx-offroad-master | Two Player |
| Madness Cars Destroy | madness-car-destroy | Survival |
| Mr. Racer - Car Racing | mr-racer-car-racing | Racing |
| Rush Hour | rush-hour-owq | Racing |
| Offroad Island | offroad-island | Driving |
| Truck Simulator: Russia | truck-simulator-russia | Driving |
| Parking Jam | parking-jam-dqq | Parking |
| Parking Fury 3D: Side Hustle | parking-fury-3d-side-hustle | Parking |
| Country Life Meadows | country-life-meadows | Management |
| OpenGuessr - Geo Guessing | openguessr | Word & Trivia |
| Word Search | word-search | Word & Trivia |
| Tile Guru | tile-guru | Match & Merge |
| Happy Wheels | happy-wheels | Action |
| Bloons Tower Defense | bloons-tower-defense | Tower Defense |
| Bullet Force | bullet-force-multiplayer | Shooter |
| Open House | open-house | Match & Merge |
| AOD - Art Of Defense | aod-art-of-defense | Tower Defense |
| Tower Swap | tower-swap | Tower Defense |
| What's The Difference? | what-s-the-difference-online | Puzzle |
| WorldGuessr Free GeoGuessr | worldguessr | Word & Trivia |
| SkillWarz | skillwarz | Two Player |
| Space Wars Battleground | space-wars-battleground | Survival |
| Cubes 2048.io | cubes-2048-io | Management |
| Man Runner 2048 | man-runner-2048 | Runner |
| Fruit Merge: Juicy Drop Game | fruit-merge-juicy-drop-game-nyf | Match & Merge |
| Capybara Clicker | capybara-clicker | Idle & Clicker |
| Pixel Warfare | pixel-warfare | Two Player |
| Obby World: Squid Escape | obby-world-squid-escape | Obby |
| Mancala Classic | mancala-classic | Two Player |
| Sweety Ludo | sweety-ludo | Mahjong & Card |
| Connect 4 Online Multiplayer | 4-in-a-row-connected-multiplayer-online | Two Player |
| Puzzle Wood Block | puzzle-wood-block | Shooter |
| Hidden Object: Clues and Mysteries | hidden-object-clues-and-mysteries | Match & Merge |
| Leek Factory Tycoon | leek-factory-tycoon | Idle & Clicker |
| Idle Zombie Wave: Survivors | idle-zombie-wave | Idle & Clicker |
| Empire City | empire-city | Management |
| Gridpunk - 3v3 Battle Royale | gridpunk-3v3-battle-royale | Shooter |
| Elemental Merge | elemental-merge | Action |
| Tavern Rumble: Roguelike Card | tavern-rumble-roguelike-card | Mahjong & Card |
| Guess Their Answer | guess-their-answer | Word & Trivia |
| Paint the Flag | paint-the-flag | Word & Trivia |
| MemeBattle: What's That Meme? | memebattle-what-s-that-meme | Mahjong & Card |
| ToT or Trivia | tot-or-trivia | Word & Trivia |
| Logo Quiz: Game World Trivia | logo-quiz-game-world-trivia | Word & Trivia |
| Geography Quiz: Flags and Capitals | world-geography-flags-and-capitals | Word & Trivia |
| Google Feud | google-feud | Word & Trivia |
| QuizzLand Trivia | quizzland-lite | Word & Trivia |
| Yes or No Challenge | yes-or-no-challenge | Word & Trivia |
| Find Them All! | find-them-all | Word & Trivia |
| Brain Teaser | brain-teaser | Word & Trivia |
| GeoQuizle | geoquizle-ser | Word & Trivia |
| Hedgies | hedgies | Cooking |
| Supermarket Simulator: Store Manager | supermarket-simulator-cashier-game | Management |
| Planet Smash Destruction | solar-smash | Shooter |
| Dragon Simulator 3D | dragon-simulator-3d | Action |
| Tiger Simulator 3D | tiger-simulator-3d | Survival |
| Horse Simulator 3D | horse-family-animal-simulator-3d | Survival |
| BuildNow GG | buildnow-gg | Two Player |
| BodyCamera Shooter | bodycamera-shooter | Two Player |
| Assault Bots | bot-machines | Driving |
| Forward Assault Remix | forward-assault | Shooter |
| Horde Killer: You vs 100 | horde-killer-you-vs-100 | Survival |
| Tanks 3D | tanks-3d | Two Player |
| Sniper Shot: Bullet Time | sniper-shot-bullet-time | Sniper |
| Wild Hunter 3D | wild-hunter-3d | Shooter |
| SCAR | scar | Survival |
| Pixel Gun 3D | pixel-gun-3d | Shooter |
| Rocket Bot Royale | rocket-bot-royale | Two Player |
| Age of Tanks Warriors: TD War | age-of-tanks-warriors-td-war | Tower Defense |
| Zombs Royale (ZombsRoyale.io) | zombsroyaleio | Word & Trivia |
| Daily Word Search | word-search-lyg | Word & Trivia |
| Wording | wording | Word & Trivia |
| Crossword | crossword | Word & Trivia |
| Crocword | crocword | Word & Trivia |
| Word Duel | word-duel | Word & Trivia |
| Waffle Words | waffle-words | Word & Trivia |
| Cryptoword | cryptoword | Word & Trivia |
| Word Fishing | word-fishing | Word & Trivia |
| Miniblox | miniblox | Two Player |
| CubeRealm.io | cuberealm-io | Two Player |
| Poxel.io | poxel-io | Two Player |
| Agar.io | agario | io Games |
| Holey.io Battle Royale | holey-io-battle-royale | Management |
| Worm Hunt | worm-hunt | Action |
| Kour.io | kour-io | Shooter |
| Diep.io | diepio | Survival |
| EvoWorld.io (FlyOrDie.io) | flyordieio | Management |
| Ducklings | ducklings | Driving |
| Backgammon Online | classic-backgammon | Two Player |
| Chess Online Multiplayer | chess-online-multiplayer-game | Mahjong & Card |
| English Checkers Free | checkers-free | Two Player |
| Table Tower Online | table-tower-online | Two Player |
| Guess Who Online | guess-who-multiplayer | Word & Trivia |
| Social Solitaire | social-solitaire | Mahjong & Card |
| Classic Card Games Collection | classic-card-games-collection | Mahjong & Card |
| Kings and Queens Solitaire TriPeaks | kings-and-queens-solitaire-tripeaks | Mahjong & Card |
| Solitaire Crime Stories | solitaire-crime-stories | Mahjong & Card |
| Whooo? | whooo | Word & Trivia |
| Mr. Mine | mister-mine | Idle & Clicker |
| Idle Inventor | idle-inventor | Idle & Clicker |
| Planet Clicker 2 | planet-clicker-2 | Idle & Clicker |
| Babel Tower | babel-tower | Idle & Clicker |
| Crusher Clicker | crusher-clicker | Idle & Clicker |
| Planet Clicker | planet-clicker | Idle & Clicker |
| Doge Miner | doge-miner | Idle & Clicker |
| Clicker Heroes | clicker-heroes | Idle & Clicker |
| Money Factory | money-factory-aqs | Idle & Clicker |
| Corn Tycoon | corn-tycoon | Idle & Clicker |
| Block Wall Destroyer | block-wall-destroyer | Idle & Clicker |
| Planet Life Idle | planet-life-idle | Idle & Clicker |
| Revolution Idle X | revolution-idle-x-demo | Idle & Clicker |
| Street Life | street-life | Idle & Clicker |
| Bloons Tower Defense 4 | bloons-tower-defense-4 | Tower Defense |
| Cursed Treasure 2 | cursed-treasure-2 | Tower Defense |
| TimeWarriors | timewarriors | Tower Defense |
| Kingdom Rush | kingdom-rush | Tower Defense |
| City Takeover | city-takeover | Strategy |
| Raid Heroes: Total War | raid-heroes-total-war-cgb | Tower Defense |
| Funny Battle Simulator 2 | funny-battle-simulator-2 | Shooter |
| Stick War | stick-war | Strategy |
| Merge & Construct | merge-construct | Driving |
| Sandbox City | sandbox-city-cars-zombies-ragdolls | Horror |
| GrindCraft | grindcraft | Idle & Clicker |
| Mine Shooter: Save Your World | mine-shooter-save-your-world | Survival |
| WorldZ | worldz | Survival |
| Match Arena | match-arena | Two Player |
| Night City Racing | night-city-racing | Two Player |
| Forgotten Treasure 2 | forgotten-treasure-2-match-3 | Match & Merge |
| MatchVentures | matchventures | Match & Merge |
| Mahjong Tower | mahjong-tower-2 | Mahjong & Card |
| Mahjong Titans | mahjong-titans | Mahjong & Card |
| Butterfly Shimai | butterfly-shimai | Mahjong & Card |
| Mahjong Unlimited | mahjong-unlimited | Mahjong & Card |
| War Mahjong | war-mahjong | Mahjong & Card |
| Mahjong Connect 2 (Legacy) | mahjong-connect-2-2 | Mahjong & Card |
| Celtic Mahjong Solitaire | celtic-mahjong-solitaire | Mahjong & Card |
| Mahjong Gardens | mahjong-gardens | Mahjong & Card |
| Mahjong 3D Classic | mahjong-3d-classic | Mahjong & Card |
| Tasty Match: Mahjong Pairs | tasty-match-mahjong-pairs | Mahjong & Card |
| Valentine Mahjong | valentine-mahjong | Mahjong & Card |
| Om Nom Connect Classic | om-nom-connect-classic | Mahjong & Card |
| Scandinavian Mahjong | scandinavian-mahjong | Mahjong & Card |
| Fashion Battle | fashion-battle | Beauty |
| Fashion Week 2025 | fashion-week-2025 | Beauty |
| Valentine's Day Proposal | valentine-s-day-proposal | Beauty |
| Fashion Famous | fashion-famous | Beauty |
| Holographic Trends | holographic-trends | Dress Up |
| College Girls Team Makeover | college-girls-team-makeover | Beauty |
| Fashion Challenge: Catwalk Run | fashion-challenge-catwalk-run | Beauty |
| Model Wedding | model-wedding-girls-games | Beauty |
| Room Escape: Strange Case | room-escape-strange-case | Horror |
| Escape Room: Strange Case 2 | escape-room-strange-case-2 | Horror |
