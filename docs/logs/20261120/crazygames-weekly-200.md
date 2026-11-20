# BTW game：2026-11-20 CrazyGames 每周新增200款

## 结果与增量

- 基线：origin/main `0bdce40455330df9d3d66f27c32d1af830e5d3d4`，开始时1783款。
- 全新批次净新增200款，总数1983；CrazyGames累计665，MiniGame844，其他474。旧目录未移除，旧条目的来源、来源ID、标题、iframe、缩略图未意外改写。
- 首次命令为 `python3 import_crazygames_embed_games.py --limit 200 --discover-categories`；本批无需resume。
- 跟随来源发布链接与relatedTags扫描127个分类/标签入口，无扫描错误；740个候选中收录200，淘汰540：未开放嵌入501、重复身份22、缺来源数据16、缺操作说明1。
- 来源ID、标题、slug、iframe四类身份与基线及本批互不重复。保留Playhop过滤，全部新增明确allowEmbed布尔true。

## 来源事实与构建

200条保留来源URL/ID/核对时间、完整来源操作说明、来源玩法与设备信息。设备为来源标注：Desktop200、Android144、iOS104，不等于实机验证。所有iframe检查为HTTPS HTTP200/text/html，重定向0，无XFO/CSP拒绝嵌入；每条保留响应证据。

依次生成静态站、SEO、sitemap。200张缩略图均为本地320×200 WebP，源图与发布图一致。更新首页、完整目录、新增列表、32分类（新增Adventure）、1983个详情、FAQ及JSON-LD；sitemap XML/TXT各2022条。保留6条失效游戏sitemap排除及19款退役游戏边缘404规则。

审计脚本及既有SEO回归测试同步使用sitemap排除清单，要求有效游戏集合完全一致，拒绝漏收或重新收录已排除地址。

## 验证记录

- Python语法检查、git diff --check通过。
- `python3 -m unittest test_seo_repairs test_crazygames_geo test_retired_routes test_catalog_freshness test_home_grid test_brand_assets`：49项通过，包含Node.js边缘路由和网格逻辑检查。
- 本地增量审计：净增200、全部新增来源/操作、200张WebP尺寸/内容、全部2028个HTML页面、130070个内部链接与资源引用、canonical、FAQ与结构化数据通过。
- 两份sitemap顺序一致、无重复，游戏地址1977条，保留6款排除。目录与1983个详情页一一对应。
- 浏览器检查本地首页/目录/分类/新增详情；首页可见图片无加载失败。99 Balls播放器已通过广告加载到游戏启动菜单，后续播放器抽查另存运行证据。没有逐款完整试玩，也没有将HTTP可用视为完整可玩。

## 发布与回滚

提交前验证通过后按SOP合并spike/fullstack和main，正常推送origin/main，触发现有Cloudflare Pages Git集成。最终对应SHA部署回执、正式域名目录、200个新增页面/图片、sitemap/canonical核验见本次运行证据目录及最终聊天结论；本报告不以push成功推定部署成功。

回滚方式为回滚本次main合并提交并由Pages Git集成重新发布。第三方许可、网络和内容后续可能变化。

运行证据目录：`/Users/bjit208/.codex/automations/btw-game-200/runs/20261120T005557Z/`。

## 新增游戏清单

| 游戏 | slug | 来源 | 来源设备标注 |
| --- | --- | --- | --- |
| Stickman History Battle | stickman-history-battle | https://www.crazygames.com/game/stickman-history-battle | Desktop |
| Project Restoration | project-restoration-axt | https://www.crazygames.com/game/project-restoration-axt | Desktop, Android, iOS |
| Russian Checkers Free | russian-checkers-free | https://www.crazygames.com/game/russian-checkers-free | Desktop, Android, iOS |
| DUO With Friends | duo-with-friends | https://www.crazygames.com/game/duo-with-friends | Desktop |
| Scary Horror Escape Room | scary-horror-escape-room-games | https://www.crazygames.com/game/scary-horror-escape-room-games | Desktop, Android, iOS |
| Car Race: 3D | car-race-3d-racing-cars-games | https://www.crazygames.com/game/car-race-3d-racing-cars-games | Desktop |
| Rodha | rodha | https://www.crazygames.com/game/rodha | Desktop, Android, iOS |
| Go Escape | go-escape-nim | https://www.crazygames.com/game/go-escape-nim | Desktop, Android |
| Find The Pets | find-the-pets-cph | https://www.crazygames.com/game/find-the-pets-cph | Desktop, Android, iOS |
| Turnfight | turnfight-com-uap | https://www.crazygames.com/game/turnfight-com-uap | Desktop |
| Stickman Archer: The Wizard Hero | stickman-archer-the-wizard-hero | https://www.crazygames.com/game/stickman-archer-the-wizard-hero | Desktop, Android |
| Embercry | embercry | https://www.crazygames.com/game/embercry | Desktop, Android |
| Noob Miner 2: Escape From Prison | noob-miner-2-escape-form-prison | https://www.crazygames.com/game/noob-miner-2-escape-form-prison | Desktop, Android, iOS |
| Prison Life | prison-life-aur | https://www.crazygames.com/game/prison-life-aur | Desktop, Android |
| Bubble Pop Classic | bubble-pop-classic | https://www.crazygames.com/game/bubble-pop-classic | Desktop, Android, iOS |
| Frogger | frogger | https://www.crazygames.com/game/frogger | Desktop |
| Puzzle Bobble | puzzle-bobble | https://www.crazygames.com/game/puzzle-bobble | Desktop |
| Snakes and Ladders | snakes-and-ladders | https://www.crazygames.com/game/snakes-and-ladders | Desktop, Android, iOS |
| Smarty Bubbles | smarty-bubbles | https://www.crazygames.com/game/smarty-bubbles | Desktop, Android, iOS |
| Little Fox: Bubble Spinner Pop | little-fox-bubble-spinner-pop | https://www.crazygames.com/game/little-fox-bubble-spinner-pop | Desktop, Android, iOS |
| Bubble Woods | bubble-woods | https://www.crazygames.com/game/bubble-woods | Desktop, Android, iOS |
| 99 Balls | 99-balls | https://www.crazygames.com/game/99-balls | Desktop, Android, iOS |
| Blocks and that’s it | block-tour-kfz | https://www.crazygames.com/game/block-tour-kfz | Desktop, Android, iOS |
| TenTrix | tentrix | https://www.crazygames.com/game/tentrix | Desktop, Android, iOS |
| Wood Blocks | wood-blocks | https://www.crazygames.com/game/wood-blocks | Desktop, Android, iOS |
| Neko Sliding: Cat Puzzle | neko-sliding-cat-puzzle | https://www.crazygames.com/game/neko-sliding-cat-puzzle | Desktop, Android, iOS |
| Drop & Merge the Numbers | drop-merge-the-numbers | https://www.crazygames.com/game/drop-merge-the-numbers | Desktop, Android |
| 10x10! Classic | 10x10-classic | https://www.crazygames.com/game/10x10-classic | Desktop, Android, iOS |
| Merge to Million | merge-to-million | https://www.crazygames.com/game/merge-to-million | Desktop, Android, iOS |
| Favorite Puzzles | favorite-puzzles | https://www.crazygames.com/game/favorite-puzzles | Desktop, Android, iOS |
| Fairy Puzzle | fairy-puzzle | https://www.crazygames.com/game/fairy-puzzle | Desktop, Android, iOS |
| Puzzle Play | puzzle-play | https://www.crazygames.com/game/puzzle-play | Desktop, Android, iOS |
| Pixel Sphere 3D | pixel-sphere-3d | https://www.crazygames.com/game/pixel-sphere-3d | Desktop, Android |
| Puzzle: What a Twist! | puzzle-what-a-twist | https://www.crazygames.com/game/puzzle-what-a-twist | Desktop, Android, iOS |
| The World's Easyest Game | the-world-s-easyest-game | https://www.crazygames.com/game/the-world-s-easyest-game | Desktop, Android, iOS |
| Categories | categories | https://www.crazygames.com/game/categories | Desktop, Android, iOS |
| The Dumb Test | the-dumb-test | https://www.crazygames.com/game/the-dumb-test | Desktop, Android, iOS |
| Impossible Date | impossibe-date | https://www.crazygames.com/game/impossibe-date | Desktop, Android, iOS |
| Emoji Guess Master! | emoji-guess-master | https://www.crazygames.com/game/emoji-guess-master | Desktop, Android, iOS |
| Stupidity Test | stupidity-test | https://www.crazygames.com/game/stupidity-test | Desktop, Android, iOS |
| Hero Castle War: Tower Attack | hero-castle-war-tower-attack | https://www.crazygames.com/game/hero-castle-war-tower-attack | Desktop, Android |
| Numbers Arena | numbers-arena | https://www.crazygames.com/game/numbers-arena | Desktop, Android |
| Merge the Numbers | merge-the-numbers | https://www.crazygames.com/game/merge-the-numbers | Desktop, Android, iOS |
| Five-O | five-o | https://www.crazygames.com/game/five-o | Desktop, Android, iOS |
| Get to Zero | get-to-zero-card-game | https://www.crazygames.com/game/get-to-zero-card-game | Desktop |
| Number Line Match | number-line-match | https://www.crazygames.com/game/number-line-match | Desktop, Android, iOS |
| STACK.it | stack-it | https://www.crazygames.com/game/stack-it | Desktop, Android, iOS |
| Nuts Puzzle: Sort By Color | nuts-puzzle-sort-by-color | https://www.crazygames.com/game/nuts-puzzle-sort-by-color | Desktop, Android, iOS |
| Cricket World Cup | cricket-world-cup | https://www.crazygames.com/game/cricket-world-cup | Desktop, Android, iOS |
| Cricket Superstar League | cricket-superstar-league | https://www.crazygames.com/game/cricket-superstar-league | Desktop |
| Offroad Life 3D | offroad-life-3d | https://www.crazygames.com/game/offroad-life-3d | Desktop |
| Russian Car Driver ZIL 130 | russian-car-driver-zil-130 | https://www.crazygames.com/game/russian-car-driver-zil-130 | Desktop |
| Ultimate Truck Driving Simulator 2020 | ultimate-truck-driving-simulator-2020 | https://www.crazygames.com/game/ultimate-truck-driving-simulator-2020 | Desktop |
| Truck Driving Simulator Game | truck-driving-simulator-game | https://www.crazygames.com/game/truck-driving-simulator-game | Desktop |
| Offroad Masters Challenge | offroad-masters-challenge | https://www.crazygames.com/game/offroad-masters-challenge | Desktop |
| Gold Rush | gold-rush | https://www.crazygames.com/game/gold-rush | Desktop, Android |
| Cargo Truck Driver Simulator | cargo-truck-driver-simulator | https://www.crazygames.com/game/cargo-truck-driver-simulator | Desktop, Android, iOS |
| Stickman World War | stickman-world-war | https://www.crazygames.com/game/stickman-world-war | Desktop |
| Derby Crash 5 | derby-crash-5 | https://www.crazygames.com/game/derby-crash-5 | Desktop |
| BattleDudes.io | battledudes-io | https://www.crazygames.com/game/battledudes-io | Desktop, Android, iOS |
| Tanks Arena io: Craft & Combat | tanks-arena-io-craft-combat | https://www.crazygames.com/game/tanks-arena-io-craft-combat | Desktop, Android |
| Merge Master Tanks: Tank Wars | merge-master-tanks-tank-wars | https://www.crazygames.com/game/merge-master-tanks-tank-wars | Desktop, Android |
| Modern Cannon Strike | modern-cannon-strike | https://www.crazygames.com/game/modern-cannon-strike | Desktop, Android |
| Clash of Armor | clash-of-armor | https://www.crazygames.com/game/clash-of-armor | Desktop, Android |
| MotoCross Riders | motocross-riders | https://www.crazygames.com/game/motocross-riders | Desktop |
| Sunset Bike Racing | sunset-bike-racing | https://www.crazygames.com/game/sunset-bike-racing | Desktop, Android, iOS |
| Dirt Bike Mad Skills | dirt-bike-mad-skills | https://www.crazygames.com/game/dirt-bike-mad-skills | Desktop |
| 3D Moto Simulator 2 | 3d-moto-simulator-2 | https://www.crazygames.com/game/3d-moto-simulator-2 | Desktop |
| Bike Stunts Race Bike Games 3D | bike-stunts-race-bike-games-3d | https://www.crazygames.com/game/bike-stunts-race-bike-games-3d | Desktop |
| Airborne Motocross | airborne-motocross | https://www.crazygames.com/game/airborne-motocross | Desktop, Android, iOS |
| Moto Maniac | moto-maniac | https://www.crazygames.com/game/moto-maniac | Desktop, Android, iOS |
| StarBlast | starblastio | https://www.crazygames.com/game/starblastio | Desktop, Android, iOS |
| Airline Tycoon Idle | airline-tycoon-idle | https://www.crazygames.com/game/airline-tycoon-idle | Desktop, Android, iOS |
| Fighter Aircraft Pilot | fighter-aircraft-pilot | https://www.crazygames.com/game/fighter-aircraft-pilot | Desktop |
| Aces of the Sky: Epic Dogfights | aces-of-the-sky-epic-dogfights | https://www.crazygames.com/game/aces-of-the-sky-epic-dogfights | Desktop |
| Air Wars 3 | air-wars-3 | https://www.crazygames.com/game/air-wars-3 | Desktop |
| Mafia Takedown | murder-mafia | https://www.crazygames.com/game/murder-mafia | Desktop, Android, iOS |
| Home Flip | home-flip | https://www.crazygames.com/game/home-flip | Desktop, Android, iOS |
| Chicken Scream | chicken-scream | https://www.crazygames.com/game/chicken-scream | Desktop, Android, iOS |
| Skibidi Toilets: Infection | skibidi-toilets-infection | https://www.crazygames.com/game/skibidi-toilets-infection | Desktop |
| Suez Canal Training Simulator | suez-canal-training-simulator | https://www.crazygames.com/game/suez-canal-training-simulator | Desktop |
| The Prank King | prankster-3d | https://www.crazygames.com/game/prankster-3d | Desktop, Android |
| Cars vs Skibidi Toilet | cars-vs-skibidi-toilet | https://www.crazygames.com/game/cars-vs-skibidi-toilet | Desktop, Android |
| Smileys: Family Tree emoji | smileys-family-tree-emoji | https://www.crazygames.com/game/smileys-family-tree-emoji | Desktop, Android, iOS |
| Stick Animator | stick-animator | https://www.crazygames.com/game/stick-animator | Desktop |
| Stickman Escape School | stickman-escape-school | https://www.crazygames.com/game/stickman-escape-school | Desktop, Android, iOS |
| Slap Castle | slap-castle | https://www.crazygames.com/game/slap-castle | Desktop, Android |
| Emoji Clickers | emoji-clickers | https://www.crazygames.com/game/emoji-clickers | Desktop, Android |
| Kill the Ice Age Baby Adventure | kill-the-ice-age-baby-adventure | https://www.crazygames.com/game/kill-the-ice-age-baby-adventure | Desktop |
| Tile Jumper 3D | tile-jumper-3d | https://www.crazygames.com/game/tile-jumper-3d | Desktop, Android, iOS |
| Virtual Online Piano | virtual-piano | https://www.crazygames.com/game/virtual-piano | Desktop, Android |
| Catch Tiles: Piano Game | catch-tiles-piano-game | https://www.crazygames.com/game/catch-tiles-piano-game | Desktop, Android, iOS |
| Chainsaw Dance | chainsaw-dance | https://www.crazygames.com/game/chainsaw-dance | Desktop |
| Rhythm Capture | rhythm-capture | https://www.crazygames.com/game/rhythm-capture | Desktop |
| Screamals | screamals | https://www.crazygames.com/game/screamals | Desktop, Android, iOS |
| Color Music Hop Ball Games | color-music-hop-ball-games | https://www.crazygames.com/game/color-music-hop-ball-games | Desktop, Android, iOS |
| Italian Brainrot Clicker Game | italian-brainrot-clicker-usp | https://www.crazygames.com/game/italian-brainrot-clicker-usp | Desktop, Android, iOS |
| Stabfish.io | stabfish-io | https://www.crazygames.com/game/stabfish-io | Desktop, Android, iOS |
| Alchemy | alchemy | https://www.crazygames.com/game/alchemy | Desktop, Android, iOS |
| Animal DNA Run | animal-dna-run | https://www.crazygames.com/game/animal-dna-run | Desktop, Android, iOS |
| Skeleton Simulator | skeleton-simulator | https://www.crazygames.com/game/skeleton-simulator | Desktop |
| Quantum God | quantum-god | https://www.crazygames.com/game/quantum-god | Desktop, Android |
| Solar System Scope | solar-system-scope | https://www.crazygames.com/game/solar-system-scope | Desktop |
| myDream Universe | mydream-universe | https://www.crazygames.com/game/mydream-universe | Desktop |
| Idle World | idle-world | https://www.crazygames.com/game/idle-world | Desktop, Android |
| Fish Frenzy | fish-frenzy | https://www.crazygames.com/game/fish-frenzy | Desktop, Android, iOS |
| Cat and Granny | cat-and-granny-original | https://www.crazygames.com/game/cat-and-granny-original | Desktop, Android, iOS |
| Cat Life Simulator 3D | cat-life-simulator | https://www.crazygames.com/game/cat-life-simulator | Desktop, Android |
| Ghost Sniper | ghost-sniper | https://www.crazygames.com/game/ghost-sniper | Desktop |
| Sniper Assassin - Government Agent | sniper-assassin-government-agent | https://www.crazygames.com/game/sniper-assassin-government-agent | Desktop |
| Jungle Deer Hunting | jungle-deer-hunting | https://www.crazygames.com/game/jungle-deer-hunting | Desktop |
| Elite Sniper | elite-sniper | https://www.crazygames.com/game/elite-sniper | Desktop, Android, iOS |
| Sniper Mission | sniper-mission-blj | https://www.crazygames.com/game/sniper-mission-blj | Desktop, Android, iOS |
| Winter Clash 3D | winter-clash-3d | https://www.crazygames.com/game/winter-clash-3d | Desktop, Android, iOS |
| Sniper Clash 3D | sniper-clash-3d | https://www.crazygames.com/game/sniper-clash-3d | Desktop, Android, iOS |
| Sniper Challenge | k-sniper-challenge-3d | https://www.crazygames.com/game/k-sniper-challenge-3d | Desktop, Android, iOS |
| SNIPER | sniper | https://www.crazygames.com/game/sniper | Desktop |
| Subway Clash Remastered | subway-clash-remastered | https://www.crazygames.com/game/subway-clash-remastered | Desktop, Android, iOS |
| Spearfishing | spearfishing | https://www.crazygames.com/game/spearfishing | Desktop, Android, iOS |
| Wolf Simulator: Wild Animals 3D | wolf-simulator-wild-animals-3d | https://www.crazygames.com/game/wolf-simulator-wild-animals-3d | Desktop, Android, iOS |
| Dog Simulator 3D | dog-simulator-3d | https://www.crazygames.com/game/dog-simulator-3d | Desktop, Android, iOS |
| Skillfite.io | skillfite-io | https://www.crazygames.com/game/skillfite-io | Desktop, Android, iOS |
| Panther Family Simulator 3D | panther-family-simulator-in-jungle | https://www.crazygames.com/game/panther-family-simulator-in-jungle | Desktop |
| Fox Simulator 3D | fox-simulator-3d | https://www.crazygames.com/game/fox-simulator-3d | Desktop |
| Duck Hunt | duck-hunt | https://www.crazygames.com/game/duck-hunt | Desktop, Android, iOS |
| Panda Simulator 3D | panda-simulator-3d-animal-game | https://www.crazygames.com/game/panda-simulator-3d-animal-game | Desktop |
| Underwater Hunting | underwater-hunting | https://www.crazygames.com/game/underwater-hunting | Desktop |
| Diver Hero | diver-hero | https://www.crazygames.com/game/diver-hero | Desktop, Android, iOS |
| Crazy Roll 3D | crazy-roll-3d | https://www.crazygames.com/game/crazy-roll-3d | Desktop, Android, iOS |
| Rocking Sky Trip | rocking-sky-trip | https://www.crazygames.com/game/rocking-sky-trip | Desktop |
| Planetarium 2 | planetarium-2 | https://www.crazygames.com/game/planetarium-2 | Desktop |
| Image Crossword | image-crossword-far | https://www.crazygames.com/game/image-crossword-far | Desktop, Android |
| EvoWars.io | evowarsio | https://www.crazygames.com/game/evowarsio | Desktop, Android, iOS |
| Worms.Zone | worms-zone | https://www.crazygames.com/game/worms-zone | Desktop, Android, iOS |
| Slither.io | slitherio | https://www.crazygames.com/game/slitherio | Desktop, Android, iOS |
| Mope.io | mopeio | https://www.crazygames.com/game/mopeio | Desktop, Android, iOS |
| Chess Master | chess-master | https://www.crazygames.com/game/chess-master | Desktop, Android |
| Chessformer | chessformer | https://www.crazygames.com/game/chessformer | Desktop, Android, iOS |
| Knight of Chess | knight-of-chess | https://www.crazygames.com/game/knight-of-chess | Desktop, Android |
| 4x4 Chess: Last Man Stand | 4x4-chess | https://www.crazygames.com/game/4x4-chess | Desktop, Android |
| Chess Clicker | chess-clicker-lhi | https://www.crazygames.com/game/chess-clicker-lhi | Desktop, Android |
| Chess Nations | chess-nations | https://www.crazygames.com/game/chess-nations | Desktop, Android |
| Chess Wars | chess-wars | https://www.crazygames.com/game/chess-wars | Desktop |
| Krew.io | krewio | https://www.crazygames.com/game/krewio | Desktop, Android, iOS |
| Duo | duo-kjn | https://www.crazygames.com/game/duo-kjn | Desktop |
| Arsenal Online | arsenal-online | https://www.crazygames.com/game/arsenal-online | Desktop, Android, iOS |
| Splatmans | splatmans | https://www.crazygames.com/game/splatmans | Desktop, Android, iOS |
| Hospital Hustle | hospital-hustle | https://www.crazygames.com/game/hospital-hustle | Desktop |
| Bad Dolls | bad-dolls | https://www.crazygames.com/game/bad-dolls | Desktop, Android, iOS |
| Amazing Strange Rope Police | amazing-strange-rope-police-vice-spider | https://www.crazygames.com/game/amazing-strange-rope-police-vice-spider | Desktop |
| Cake Sort Puzzle 3D | cake-sort-puzzle-3d | https://www.crazygames.com/game/cake-sort-puzzle-3d | Desktop, Android, iOS |
| Idle Vlogger Simulator | idle-blogger-simulator | https://www.crazygames.com/game/idle-blogger-simulator | Desktop, Android, iOS |
| Money Maker Idle | money-maker-idle | https://www.crazygames.com/game/money-maker-idle | Desktop, Android, iOS |
| Ranch Adventures | ranch-adventures | https://www.crazygames.com/game/ranch-adventures | Desktop, Android, iOS |
| Dogs vs Aliens | dogs-vs-aliens | https://www.crazygames.com/game/dogs-vs-aliens | Desktop, Android, iOS |
| Doggy Tricks | happy-dog | https://www.crazygames.com/game/happy-dog | Desktop, Android |
| Shepherd Farm | shepherd-farm | https://www.crazygames.com/game/shepherd-farm | Desktop |
| Funny Food Duel | funny-food-duel | https://www.crazygames.com/game/funny-food-duel | Desktop, Android, iOS |
| Robot Dog City Simulator | robot-dog-city-simulator | https://www.crazygames.com/game/robot-dog-city-simulator | Desktop |
| Playground | playground | https://www.crazygames.com/game/playground | Desktop, Android, iOS |
| Playground Man! Ragdoll Show! | ragdoll-break | https://www.crazygames.com/game/ragdoll-break | Desktop, Android |
| Incremental Epic Hero 2 | incremental-epic-hero-2 | https://www.crazygames.com/game/incremental-epic-hero-2 | Desktop |
| Fish Eat Getting Big | fish-eat-getting-big | https://www.crazygames.com/game/fish-eat-getting-big | Desktop |
| PolyBusiness (Unofficial Monopoly) | polybusiness | https://www.crazygames.com/game/polybusiness | Desktop |
| Gun Mayhem 2 | gun-mayhem-2 | https://www.crazygames.com/game/gun-mayhem-2 | Desktop |
| Gun Mayhem | gun-mayhem | https://www.crazygames.com/game/gun-mayhem | Desktop |
| Squish | squish-uwy | https://www.crazygames.com/game/squish-uwy | Desktop |
| Stickman battle 1-4 Players | stickman-battle-1-4-players | https://www.crazygames.com/game/stickman-battle-1-4-players | Desktop, Android, iOS |
| Multiplayer Quick Tag | multiplayer-quick-tag | https://www.crazygames.com/game/multiplayer-quick-tag | Desktop, Android, iOS |
| MiniBattles | minibattles-2-3-4-5-6-player-games | https://www.crazygames.com/game/minibattles-2-3-4-5-6-player-games | Desktop, Android, iOS |
| Tank Wars | tank-wars-iaw | https://www.crazygames.com/game/tank-wars-iaw | Desktop, Android, iOS |
| Diamant: Sky Stories Match 3 | diamant-match-3-sky-story | https://www.crazygames.com/game/diamant-match-3-sky-story | Desktop, Android |
| 2048 in Flasks | 2048-in-flasks | https://www.crazygames.com/game/2048-in-flasks | Desktop, Android, iOS |
| Kaleidoscope | kaleidoscope | https://www.crazygames.com/game/kaleidoscope | Desktop |
| blue | blue | https://www.crazygames.com/game/blue | Desktop |
| Jewel Academy | jewel-academy | https://www.crazygames.com/game/jewel-academy | Desktop, Android, iOS |
| Find The Difference | find-the-difference | https://www.crazygames.com/game/find-the-difference | Desktop, Android, iOS |
| Swimming Pool Romance | swimming-pool-romance | https://www.crazygames.com/game/swimming-pool-romance | Desktop, Android, iOS |
| Monster Makeup 3D | monster-makeup-3d | https://www.crazygames.com/game/monster-makeup-3d | Desktop, Android |
| College Girl & Boy Makeover | college-girl-boy-makeover | https://www.crazygames.com/game/college-girl-boy-makeover | Desktop, Android, iOS |
| Lulu's Fashion World | lulu-s-fashion-world | https://www.crazygames.com/game/lulu-s-fashion-world | Desktop, Android |
| Fashion Store: Shop Tycoon | fashion-store-shop-tycoon | https://www.crazygames.com/game/fashion-store-shop-tycoon | Desktop, Android, iOS |
| Autumn Glam Gala | autumn-glam-gala | https://www.crazygames.com/game/autumn-glam-gala | Desktop, Android, iOS |
| Glamour Beach Life | glamour-beachlife | https://www.crazygames.com/game/glamour-beachlife | Desktop, Android, iOS |
| Superstar Family Dress Up | superstar-family-dress-up-game | https://www.crazygames.com/game/superstar-family-dress-up-game | Desktop, Android |
| Live Avatar Maker: Girls | live-avatar-maker-girls | https://www.crazygames.com/game/live-avatar-maker-girls | Desktop, Android, iOS |
| Avatar Make Up | avatar-make-up | https://www.crazygames.com/game/avatar-make-up | Desktop, Android, iOS |
| New Year Makeup Trends | new-year-makeup-trends | https://www.crazygames.com/game/new-year-makeup-trends | Desktop, Android, iOS |
| DIY Makeup Salon: SPA Makeover | diy-makeup-salon-spa-makeover | https://www.crazygames.com/game/diy-makeup-salon-spa-makeover | Desktop, Android |
| GRWM Date Night | grwm-date-night | https://www.crazygames.com/game/grwm-date-night | Desktop, Android, iOS |
| Merge Restaurant | merge-restaurant | https://www.crazygames.com/game/merge-restaurant | Desktop, Android, iOS |
| Trading Card Store Simulator | trading-card-store-simulator | https://www.crazygames.com/game/trading-card-store-simulator | Desktop, Android |
| Shop Master 3D | shop-master-3d | https://www.crazygames.com/game/shop-master-3d | Desktop, Android |
| Iza's Supermarket | iza-s-supermarket | https://www.crazygames.com/game/iza-s-supermarket | Desktop |
| Supermarket Empire | supermarket-empire | https://www.crazygames.com/game/supermarket-empire | Desktop, Android |
| Outlets Rush | outlets-rush | https://www.crazygames.com/game/outlets-rush | Desktop, Android |
| Shop Cashier Simulator 3D | shop-cashier-3d | https://www.crazygames.com/game/shop-cashier-3d | Desktop, Android, iOS |
| Food Truck Chef™: A Fun Cooking Game | food-truck-chef | https://www.crazygames.com/game/food-truck-chef | Desktop, Android |
| Pizza Maker | pizza-maker-woi | https://www.crazygames.com/game/pizza-maker-woi | Desktop, Android, iOS |
| Mom's Diary 2 | mom-s-diary-2 | https://www.crazygames.com/game/mom-s-diary-2 | Desktop, Android |
