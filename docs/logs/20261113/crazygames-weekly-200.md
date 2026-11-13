# BTW game：2026-11-13 CrazyGames 新增 200 款

## 本地交付结果

- 远端基线：`fa82e654bd02770208598cb0cf2c03e8adff7f01`；目录从 **1,583 → 1,783**，净新增 **200**，未移除任何基线游戏。
- CrazyGames 来源累计 **465** 款；分类 **31** 个；XML/TXT sitemap 顺序一致、均为 **1,827** 条。
- 首轮使用指定全新命令，收录 93 款；只续跑本次未完成批次，沿来源发布的分类/关联标签补充 107 款。共扫描 73 个分类/标签入口，无扫描错误。
- 累计检查 559 次：收录 200，未获 allowEmbed 许可 331，重复身份 17，缺少游戏数据 10，缺少来源操作说明 1。首轮候选 360，续跑候选有重叠，不能把两轮候选数量直接相加。
- 按来源 ID、标题、slug、iframe 去重；新增 200 款与基线身份没有交集，新增之间无重复。

## 来源及产物

所有新增明确 `allow_embed=true`，均保留真实来源地址、来源 ID、UTC 核对时间、来源设备信息、完整来源操作说明、来源玩法说明，以及 iframe 响应链中的 HTTP 状态、MIME、重定向、X-Frame-Options 和 CSP。全部 iframe 检查最终 HTTP 200 / text/html，无嵌入拒绝。

每款生成源目录和发布目录两份一致的 **320×200 WebP**。主页、完整目录、新增列表、分类、详情、FAQ 和 JSON-LD 已同步构建。

原退役的 `space-waves`、`words-of-wonders`、`thief-puzzle`、`immortal-dark-slayer` 获得新的合法 CrazyGames 嵌入来源，依据既有规则解除其退役路由；其余 19 款保留 57 条精确 404 规则。新增 Arcade 分类使原 Arcade→Casual 重定向按既有规则解除。Playhop 来源仍被排除。

## 验证

- 按顺序执行 `python3 generate_static_pages.py --data-file static_html/all_games.json`、`python3 optimize_seo.py`、`python3 update_sitemap.py`，均成功。
- Python 语法检查和 `python3 -m unittest test_seo_repairs test_crazygames_geo test_retired_routes`：**28 项通过**，包含 Node.js 边缘行为测试。
- 本地审计：净增量、全站 canonical、1,827 个 HTML 文件、112,231 个内部链接/资源引用、新增完整操作说明、来源链接、可见 FAQ/结构化数据、图片格式尺寸和两份图片内容均通过。
- 基线 1,583 款的 source、source_id、title、iframe_url、thumbnail_url 与原记录保持一致。
- 浏览器检查：首页、目录显示 1,783 款、新增 Arcade 分类及三个新增详情页。Space Waves 在提供方自带 Continue offline 流程后显示实际游戏画面；Words of Wonders 与 Pool Club 的播放器外壳及游戏资源开始加载，但本地提供方联网提示/后续加载不能作为完整玩法验证。
- 未把 HTTP/HTML 可用或 allowEmbed 许可等同于第三方登录、云存档、广告或逐款完整试玩成功；线上播放器另在部署后抽查。

## 发布与证据

本报告记录提交前的验证结果；发布状态必须由对应 main 提交的 Cloudflare Pages 检查和真实域名核验确定。自动化运行记录保存在 `$CODEX_HOME/automations/btw-game-200/`，最终聊天报告给出 main SHA、Cloudflare 部署和线上核验结果。

- `crazygames-weekly-baseline.json`：开始时目录身份及 SHA-256 基线。
- `crazygames-local-validation.json`：本地审计汇总。
- `crazygames_games.json` 的 `metadata.latest_import`：本批次清单、淘汰汇总与扫描入口。
- `validate_crazygames_release.py`：可复用的本地/部署后全新增页面和图片验证入口。

## 本次新增清单

| 游戏 | slug | 来源 | 设备 |
| --- | --- | --- | --- |
| Space Waves | space-waves | https://www.crazygames.com/game/space-waves | Desktop, Android, iOS |
| Words of Wonders | words-of-wonders | https://www.crazygames.com/game/words-of-wonders | Desktop, Android, iOS |
| Daily Puzzle | daily-puzzle | https://www.crazygames.com/game/daily-puzzle | Desktop, Android |
| Kitty Scramble: Word Stacks | kitty-scramble | https://www.crazygames.com/game/kitty-scramble | Desktop, Android, iOS |
| 911: Prey | 911-prey | https://www.crazygames.com/game/911-prey | Desktop, Android |
| Exhibit of Sorrows | exhibit-of-sorrows | https://www.crazygames.com/game/exhibit-of-sorrows | Desktop, Android, iOS |
| Haunted School | haunted-school-horror-game | https://www.crazygames.com/game/haunted-school-horror-game | Desktop, Android |
| Horror Tale | horror-tale-kidnapper | https://www.crazygames.com/game/horror-tale-kidnapper | Desktop, Android |
| Horror Tale 2: Samantha | horror-tale-2-samantha | https://www.crazygames.com/game/horror-tale-2-samantha | Desktop, Android |
| Skinwalker | skinwalker | https://www.crazygames.com/game/skinwalker | Desktop, Android, iOS |
| 911: Cannibal | 911-cannibal | https://www.crazygames.com/game/911-cannibal | Desktop, Android |
| Nuclear Day | nuclear-day | https://www.crazygames.com/game/nuclear-day | Desktop |
| Escape From Prison Multiplayer | escape-from-prison-multiplayer | https://www.crazygames.com/game/escape-from-prison-multiplayer | Desktop, Android, iOS |
| House of Celestina | house-of-celestina | https://www.crazygames.com/game/house-of-celestina | Desktop |
| Slenderman Must Die: Silent Streets | slenderman-must-die-silent-streets | https://www.crazygames.com/game/slenderman-must-die-silent-streets | Desktop |
| Slendrina Must Die: The Forest | slendrina-must-die-the-forest | https://www.crazygames.com/game/slendrina-must-die-the-forest | Desktop |
| Level EATEN! | level-eaten | https://www.crazygames.com/game/level-eaten | Desktop |
| Appel | appel | https://www.crazygames.com/game/appel | Desktop |
| The Epic Party | the-epic-party | https://www.crazygames.com/game/the-epic-party | Desktop |
| Miner Cat 4 | miner-cat-4 | https://www.crazygames.com/game/miner-cat-4 | Desktop |
| Arena | arena | https://www.crazygames.com/game/arena | Desktop |
| Bomb Defuse Online | talking-and-nobody-explosion | https://www.crazygames.com/game/talking-and-nobody-explosion | Desktop, Android, iOS |
| The Chick Chase | the-chick-chase | https://www.crazygames.com/game/the-chick-chase | Desktop |
| Animals Minigame Party | animals-minigame-party | https://www.crazygames.com/game/animals-minigame-party | Desktop |
| KNOCKOUTS! | knockouts | https://www.crazygames.com/game/knockouts | Desktop |
| Geometry Dash Subzero | geometry-neon-dash-subzero | https://www.crazygames.com/game/geometry-neon-dash-subzero | Desktop, Android, iOS |
| Golf Mania | golf-mania | https://www.crazygames.com/game/golf-mania | Desktop, Android, iOS |
| Fabby Golf! | fabby-golf | https://www.crazygames.com/game/fabby-golf | Desktop, Android |
| Bounce Blocku Golf | bounce-blocku-golf | https://www.crazygames.com/game/bounce-blocku-golf | Desktop, Android, iOS |
| ESPN Arcade Baseball | espn-arcade-baseball | https://www.crazygames.com/game/espn-arcade-baseball | Desktop, Android, iOS |
| Hotfoot Baseball | hotfoot-baseball | https://www.crazygames.com/game/hotfoot-baseball | Desktop, Android, iOS |
| Baseball Pro | baseball-pro | https://www.crazygames.com/game/baseball-pro | Desktop, Android, iOS |
| Free Kick Classic (3D Free Kick) | free-kick-classic | https://www.crazygames.com/game/free-kick-classic | Desktop, Android, iOS |
| Soccer Dash | soccer-dash | https://www.crazygames.com/game/soccer-dash | Desktop, Android, iOS |
| Penalty Shootout: Multi League | penalty-shootout-multi-league | https://www.crazygames.com/game/penalty-shootout-multi-league | Desktop, Android, iOS |
| PSG Soccer Freestyle | psg-soccer-freestyle-hgj | https://www.crazygames.com/game/psg-soccer-freestyle-hgj | Desktop, Android |
| SocCar | soccar | https://www.crazygames.com/game/soccar | Desktop |
| CG FC 26 | cg-fc-24 | https://www.crazygames.com/game/cg-fc-24 | Desktop, Android, iOS |
| Axis Football League | axis-football-league | https://www.crazygames.com/game/axis-football-league | Desktop |
| Bloons Tower Defense 2 | bloons-tower-defense-2 | https://www.crazygames.com/game/bloons-tower-defense-2 | Desktop |
| Kiomet | kiomet-com | https://www.crazygames.com/game/kiomet-com | Desktop, Android |
| Rolling Balls Sea Race | roling-balls-sea-race | https://www.crazygames.com/game/roling-balls-sea-race | Desktop |
| Crazy Grand Prix | crazy-grand-prix | https://www.crazygames.com/game/crazy-grand-prix | Desktop |
| Super Star Car | super-star-car | https://www.crazygames.com/game/super-star-car | Desktop |
| Racing in City | racing-in-city | https://www.crazygames.com/game/racing-in-city | Desktop, Android |
| Street Racer 2 | street-racer-2 | https://www.crazygames.com/game/street-racer-2 | Desktop, Android, iOS |
| Race Clicker: Tap Tap Game | race-clicker-tap-tap-game | https://www.crazygames.com/game/race-clicker-tap-tap-game | Desktop, Android, iOS |
| Death Chase | death-chase | https://www.crazygames.com/game/death-chase | Desktop |
| Fall Beans | fall-beans | https://www.crazygames.com/game/fall-beans | Desktop |
| Super Bike The Champion | super-bike-the-champion | https://www.crazygames.com/game/super-bike-the-champion | Desktop |
| Save My Pets | save-my-pets | https://www.crazygames.com/game/save-my-pets | Desktop, Android |
| Doodle Road | doodle-road | https://www.crazygames.com/game/doodle-road | Desktop, Android, iOS |
| Draw Climber | draw-climber | https://www.crazygames.com/game/draw-climber | Desktop, Android, iOS |
| Draw Crash Race | draw-crash-race | https://www.crazygames.com/game/draw-crash-race | Desktop, Android, iOS |
| DOP Noob: Draw to Save | dop-noob-draw-to-save | https://www.crazygames.com/game/dop-noob-draw-to-save | Desktop, Android |
| Draw Tattoo | draw-tattoo | https://www.crazygames.com/game/draw-tattoo | Desktop, Android, iOS |
| Ragdoll Throw Challenge | ragdoll-throw-challenge | https://www.crazygames.com/game/ragdoll-throw-challenge | Desktop, Android, iOS |
| Basketball Skills | basketball-skills | https://www.crazygames.com/game/basketball-skills | Desktop, Android |
| Basket Battle | basket-battle-zmg | https://www.crazygames.com/game/basket-battle-zmg | Desktop, Android, iOS |
| Basketball Clash | basketball-clash | https://www.crazygames.com/game/basketball-clash | Desktop, Android |
| Super Crime Steel War Hero | super-crime-steel-war-hero | https://www.crazygames.com/game/super-crime-steel-war-hero | Desktop |
| Moto X3M 4 Winter | moto-x3m-4 | https://www.crazygames.com/game/moto-x3m-4 | Desktop, Android, iOS |
| Riders Downhill Racing | riders-downhill-racing | https://www.crazygames.com/game/riders-downhill-racing | Desktop |
| Trial Mania | trial-mania | https://www.crazygames.com/game/trial-mania | Desktop, Android, iOS |
| Super MX - Last Season | super-mx-last-season | https://www.crazygames.com/game/super-mx-last-season | Desktop |
| Xtreme Moto Mayhem | xtreme-moto-mayhem | https://www.crazygames.com/game/xtreme-moto-mayhem | Desktop, Android, iOS |
| Super MX - The Champion | super-mx-motocross-simulator | https://www.crazygames.com/game/super-mx-motocross-simulator | Desktop |
| TileMan.io | tileman-io | https://www.crazygames.com/game/tileman-io | Desktop, Android, iOS |
| Squid Game Online | squid-game-online | https://www.crazygames.com/game/squid-game-online | Desktop |
| Crazy Office: Slap and Smash! | crazy-office-slap-and-smash | https://www.crazygames.com/game/crazy-office-slap-and-smash | Desktop, Android, iOS |
| Thief Puzzle | thief-puzzle | https://www.crazygames.com/game/thief-puzzle | Desktop, Android, iOS |
| Bridge Race | bridge-race | https://www.crazygames.com/game/bridge-race | Desktop, Android, iOS |
| Stickman Project | stickman-project-bnw | https://www.crazygames.com/game/stickman-project-bnw | Desktop, Android, iOS |
| Amazing Crime Strange Stickman | amazing-crime-strange-stickman | https://www.crazygames.com/game/amazing-crime-strange-stickman | Desktop |
| Stickman Prison: Counter Assault | stickman-prison-counter-assault | https://www.crazygames.com/game/stickman-prison-counter-assault | Desktop |
| Stickman Fighting 3D | stickman-fighting-3d | https://www.crazygames.com/game/stickman-fighting-3d | Desktop |
| Motherload | motherload | https://www.crazygames.com/game/motherload | Desktop |
| Bartender The Right Mix | bartender-the-right-mix | https://www.crazygames.com/game/bartender-the-right-mix | Desktop, Android, iOS |
| The Visitor | the-visitor | https://www.crazygames.com/game/the-visitor | Desktop, Android, iOS |
| The Waitress | the-waitress | https://www.crazygames.com/game/the-waitress | Desktop, Android, iOS |
| Hobo | hobo | https://www.crazygames.com/game/hobo | Desktop |
| Age Of War | age-of-war | https://www.crazygames.com/game/age-of-war | Desktop, Android, iOS |
| The Idiot Test | the-idiot-test | https://www.crazygames.com/game/the-idiot-test | Desktop, Android, iOS |
| Pool Club | pool-club | https://www.crazygames.com/game/pool-club | Desktop, Android, iOS |
| Billiards | billiards | https://www.crazygames.com/game/billiards | Desktop, Android, iOS |
| Cue Billiard Club | cue-billiard-club | https://www.crazygames.com/game/cue-billiard-club | Desktop |
| Mafia Billiard Tricks | mafia-billiard-tricks | https://www.crazygames.com/game/mafia-billiard-tricks | Desktop, Android, iOS |
| Blast Billiards 4 | blast-billiards-4 | https://www.crazygames.com/game/blast-billiards-4 | Desktop, Android, iOS |
| Billiards Pool 8 | billiards-pool-8 | https://www.crazygames.com/game/billiards-pool-8 | Desktop, Android, iOS |
| Pool Hustlers | pool-hustlers | https://www.crazygames.com/game/pool-hustlers | Desktop, Android, iOS |
| The Best Russian Billiards | the-best-russian-billiards | https://www.crazygames.com/game/the-best-russian-billiards | Desktop |
| Royal Pool | royal-pool | https://www.crazygames.com/game/royal-pool | Desktop, Android, iOS |
| Pool Bubbles | pool-bubbles | https://www.crazygames.com/game/pool-bubbles | Desktop |
| Rooftop Run | rooftop-run | https://www.crazygames.com/game/rooftop-run | Desktop, Android, iOS |
| Sprinter | sprinter | https://www.crazygames.com/game/sprinter | Desktop |
| Gearshift One | gearshift-one | https://www.crazygames.com/game/gearshift-one | Desktop |
| Monster Cars: Ultimate Simulator | monster-cars-ultimate-simulator | https://www.crazygames.com/game/monster-cars-ultimate-simulator | Desktop |
| Monster Truck Demolition Derby | monster-truck-demolition-derby | https://www.crazygames.com/game/monster-truck-demolition-derby | Desktop |
| Monster Puzzle | monster-puzzle | https://www.crazygames.com/game/monster-puzzle | Desktop |
| Gas Monsters | gas-monsters | https://www.crazygames.com/game/gas-monsters | Desktop |
| Monster Truck Arena | monster-truck-arena | https://www.crazygames.com/game/monster-truck-arena | Desktop, Android |
| Offroad Muddy Trucks | offroad-muddy-trucks | https://www.crazygames.com/game/offroad-muddy-trucks | Desktop |
| Car Inspector: Truck | car-inpsector-truck | https://www.crazygames.com/game/car-inpsector-truck | Desktop |
| Real Simulator: Monster Truck | real-simulator-monster-truck | https://www.crazygames.com/game/real-simulator-monster-truck | Desktop |
| Hard Wheels | hard-wheels | https://www.crazygames.com/game/hard-wheels | Desktop, Android, iOS |
| Mad Truck Challenge Special | mad-truck-challenge-special | https://www.crazygames.com/game/mad-truck-challenge-special | Desktop, Android |
| Monsters' Wheels Special | monsters-wheels-special | https://www.crazygames.com/game/monsters-wheels-special | Desktop, Android |
| Find Me: Lost Objects | find-me-lost-objects | https://www.crazygames.com/game/find-me-lost-objects | Desktop, Android |
| Daily Kitchen Escape | daily-kitchen-escape | https://www.crazygames.com/game/daily-kitchen-escape | Desktop, Android, iOS |
| Paint Room Escape | paint-room-escape | https://www.crazygames.com/game/paint-room-escape | Desktop, Android, iOS |
| Drive Quest | drive-quest-car-game | https://www.crazygames.com/game/drive-quest-car-game | Desktop, Android, iOS |
| Burnout Drift | burnout-drift | https://www.crazygames.com/game/burnout-drift | Desktop |
| Derby Crash 4 | derby-crash-4 | https://www.crazygames.com/game/derby-crash-4 | Desktop |
| Imposter Battle Royale | imposter-battle-royale | https://www.crazygames.com/game/imposter-battle-royale | Desktop |
| WarCall.io | warcall-io | https://www.crazygames.com/game/warcall-io | Desktop, Android, iOS |
| GoBattle.io | gobattleio | https://www.crazygames.com/game/gobattleio | Desktop, Android, iOS |
| Pilot Royale: Battlegrounds | pilot-royale-battlegrounds | https://www.crazygames.com/game/pilot-royale-battlegrounds | Desktop |
| Battle Royale Survival | battle-royale-survival | https://www.crazygames.com/game/battle-royale-survival | Desktop |
| Offroad Cargo Transport Truck | offroad-cargo-transport-truck | https://www.crazygames.com/game/offroad-cargo-transport-truck | Desktop |
| Big Euro Truck Driving | big-euro-truck-driving | https://www.crazygames.com/game/big-euro-truck-driving | Desktop |
| Garage Parking | garage-parking | https://www.crazygames.com/game/garage-parking | Desktop |
| Russian Kamaz Truck Driver | russian-kamaz-truck-driver | https://www.crazygames.com/game/russian-kamaz-truck-driver | Desktop |
| Kamaz Truck Driver | kamaz-truck-driver | https://www.crazygames.com/game/kamaz-truck-driver | Desktop |
| World Z Defense - Zombie Defense | world-z-defense-zombie-defense | https://www.crazygames.com/game/world-z-defense-zombie-defense | Desktop, Android, iOS |
| Dead Zed | dead-zed | https://www.crazygames.com/game/dead-zed | Desktop, Android, iOS |
| Stick Epic Fighter | stick-epic-fighter | https://www.crazygames.com/game/stick-epic-fighter | Desktop, Android, iOS |
| Mini Mine | minimine | https://www.crazygames.com/game/minimine | Desktop, Android, iOS |
| Lime Playground Sandbox | lime-playground-sandbox | https://www.crazygames.com/game/lime-playground-sandbox | Desktop, Android, iOS |
| Stickman Epic | stickman-epic | https://www.crazygames.com/game/stickman-epic | Desktop, Android, iOS |
| Zombie Hunters Online | zombie-hunters-online | https://www.crazygames.com/game/zombie-hunters-online | Desktop, Android, iOS |
| Bank Heist | bank-heist | https://www.crazygames.com/game/bank-heist | Desktop |
| Crazy Pixel Apocalypse | crazy-pixel-apocalypse | https://www.crazygames.com/game/crazy-pixel-apocalypse | Desktop |
| Wood Screw: Bolts Puzzle | wood-screw-bolts-puzzle | https://www.crazygames.com/game/wood-screw-bolts-puzzle | Desktop, Android |
| Super Robo - Adventure | super-robo-adventure | https://www.crazygames.com/game/super-robo-adventure | Desktop |
| Super Smash Flash | super-smash-flash | https://www.crazygames.com/game/super-smash-flash | Desktop |
| Donkey Kong Returns | donkey-kong-returns | https://www.crazygames.com/game/donkey-kong-returns | Desktop |
| Ringo Starfish | ringo-starfish | https://www.crazygames.com/game/ringo-starfish | Desktop, Android, iOS |
| Steve's World | steve-s-world | https://www.crazygames.com/game/steve-s-world | Desktop, Android, iOS |
| Super Billy Boy | super-billy-boy | https://www.crazygames.com/game/super-billy-boy | Desktop, Android, iOS |
| Solitaire Reverse | solitaire-reverse | https://www.crazygames.com/game/solitaire-reverse | Desktop, Android, iOS |
| Tri Peaks Social | tri-peaks-solitaire | https://www.crazygames.com/game/tri-peaks-solitaire | Desktop, Android, iOS |
| Emerland Solitaire Card Game | emerland-solitaire-card-game | https://www.crazygames.com/game/emerland-solitaire-card-game | Desktop |
| Backpack Battles | backpack-battles | https://www.crazygames.com/game/backpack-battles | Desktop |
| Autogun Heroes | autogun-heroes-izk | https://www.crazygames.com/game/autogun-heroes-izk | Desktop, Android |
| Goober Dash | goober-dash | https://www.crazygames.com/game/goober-dash | Desktop, Android, iOS |
| Crazy Miners | crazy-miners-multiplayer | https://www.crazygames.com/game/crazy-miners-multiplayer | Desktop, Android, iOS |
| Punchers | punchers | https://www.crazygames.com/game/punchers | Desktop, Android |
| Drunken Boxing | drunken-boxers | https://www.crazygames.com/game/drunken-boxers | Desktop, Android, iOS |
| Fight Arena Online | fight-arena-online | https://www.crazygames.com/game/fight-arena-online | Desktop, Android |
| Ragdoll Fight | ragdoll-fight | https://www.crazygames.com/game/ragdoll-fight | Desktop |
| Funny Ragdoll Wrestlers | funny-ragdoll-wrestlers | https://www.crazygames.com/game/funny-ragdoll-wrestlers | Desktop |
| Smash Block Arena | smash-block-arena | https://www.crazygames.com/game/smash-block-arena | Desktop, Android |
| Darts Club | darts-club | https://www.crazygames.com/game/darts-club | Desktop |
| Archery World Tour | archery-world-tour | https://www.crazygames.com/game/archery-world-tour | Desktop, Android, iOS |
| Feeling Arrow | feeling-arrow | https://www.crazygames.com/game/feeling-arrow | Desktop, Android |
| cowz.io | cowz-io | https://www.crazygames.com/game/cowz-io | Desktop |
| Snake Shooter: Tower Battle | snake-shooter-cbu | https://www.crazygames.com/game/snake-shooter-cbu | Desktop |
| Archer Ragdoll Masters | archer-ragdoll-masters | https://www.crazygames.com/game/archer-ragdoll-masters | Desktop, Android, iOS |
| Slingshot Fortress | slingshot-fortress | https://www.crazygames.com/game/slingshot-fortress | Desktop, Android |
| Archers Arena | archers-arena | https://www.crazygames.com/game/archers-arena | Desktop, Android, iOS |
| Apple Shooter | apple-shooter | https://www.crazygames.com/game/apple-shooter | Desktop, Android, iOS |
| Love Archer | love-archer | https://www.crazygames.com/game/love-archer | Desktop, Android, iOS |
| Tower Archer | tower-archer | https://www.crazygames.com/game/tower-archer | Desktop |
| Wild Archer: Castle Defense | wild-archer-castle-defense | https://www.crazygames.com/game/wild-archer-castle-defense | Desktop, Android |
| Bloons Player Pack 1 | bloons-player-pack-1 | https://www.crazygames.com/game/bloons-player-pack-1 | Desktop, Android, iOS |
| City Car Driving Simulator: Stunt | city-car-driving-simulator-ultimate | https://www.crazygames.com/game/city-car-driving-simulator-ultimate | Desktop, Android |
| Drift Escape | drift-escape | https://www.crazygames.com/game/drift-escape | Desktop, Android |
| Vegas Clash 3D | vegas-clash-3d-yxd | https://www.crazygames.com/game/vegas-clash-3d-yxd | Desktop, Android, iOS |
| Bank Robbery | bank-robbery | https://www.crazygames.com/game/bank-robbery | Desktop |
| Jailbreak: Hide or Attack! | jailbreak-hide-or-attack | https://www.crazygames.com/game/jailbreak-hide-or-attack | Desktop, Android |
| Puppet Fighter 2 Player | puppet-fighter-2-player | https://www.crazygames.com/game/puppet-fighter-2-player | Desktop, Android, iOS |
| Immortal: Dark Slayer | immortal-dark-slayer | https://www.crazygames.com/game/immortal-dark-slayer | Desktop, Android, iOS |
| Grand Action Simulator: New York | grand-action-simulator-new-york-car-gang | https://www.crazygames.com/game/grand-action-simulator-new-york-car-gang | Desktop |
| Godzilla Daikaiju Battle Royale | godzilla-daikaiju-battle-royale | https://www.crazygames.com/game/godzilla-daikaiju-battle-royale | Desktop |
| Javelin Fighting | javelin-fighting | https://www.crazygames.com/game/javelin-fighting | Desktop |
| Swords & Souls | swords-souls | https://www.crazygames.com/game/swords-souls | Desktop |
| Gladiator Fights | gladiator-fights | https://www.crazygames.com/game/gladiator-fights | Desktop, Android, iOS |
| Stronghold Dude | stronghold-dude | https://www.crazygames.com/game/stronghold-dude | Desktop |
| Striker Dummies | striker-dummies | https://www.crazygames.com/game/striker-dummies | Desktop |
| Electric Man | electric-man | https://www.crazygames.com/game/electric-man | Desktop |
| Your Chronicle | your-chronicle | https://www.crazygames.com/game/your-chronicle | Desktop |
| Immortals Revenge | immortals-revenge | https://www.crazygames.com/game/immortals-revenge | Desktop |
| Idle Saga | idle-saga | https://www.crazygames.com/game/idle-saga | Desktop, Android, iOS |
| War Lands | war-lands | https://www.crazygames.com/game/war-lands | Desktop |
| Duck Life: Battle (Demo) | duck-life-battle | https://www.crazygames.com/game/duck-life-battle | Desktop |
| Tailed Demon Slayer | tailed-demon-slayer | https://www.crazygames.com/game/tailed-demon-slayer | Desktop, Android |
| Woods of Nevia: Forest Survival | woods-of-nevia-forest-survival | https://www.crazygames.com/game/woods-of-nevia-forest-survival | Desktop, Android, iOS |
| Scavenger Hunt - Multiplayer | scavenger-hunt-multiplayer | https://www.crazygames.com/game/scavenger-hunt-multiplayer | Desktop |
| Detective Holmes: Hidden Object | detective-holmes-hidden-object-game-jbm | https://www.crazygames.com/game/detective-holmes-hidden-object-game-jbm | Desktop |
| Detective IQ: Brain Games | detective-iq-brain-games-ekr | https://www.crazygames.com/game/detective-iq-brain-games-ekr | Desktop, Android |
| Seeing Things | seeing-things | https://www.crazygames.com/game/seeing-things | Desktop |
| Night Incident | murderer | https://www.crazygames.com/game/murderer | Desktop |
| Everytown | everytown | https://www.crazygames.com/game/everytown | Desktop, Android |
| Gold Digger FRVR | gold-digger-frvr | https://www.crazygames.com/game/gold-digger-frvr | Desktop, Android, iOS |
| Craft Drill | idle-craft-drill | https://www.crazygames.com/game/idle-craft-drill | Desktop, Android, iOS |
| Schoolboy Escape: Runaway | schoolboy-escape-runaway | https://www.crazygames.com/game/schoolboy-escape-runaway | Desktop, Android |
| Escape or Die 2 | escape-or-die-2 | https://www.crazygames.com/game/escape-or-die-2 | Desktop, Android |
| The White Room | the-white-room | https://www.crazygames.com/game/the-white-room | Desktop, Android |
| Mirror Room Escape | mirror-room-escape | https://www.crazygames.com/game/mirror-room-escape | Desktop, Android, iOS |
| Riddle School | riddle-school | https://www.crazygames.com/game/riddle-school | Desktop, Android, iOS |
