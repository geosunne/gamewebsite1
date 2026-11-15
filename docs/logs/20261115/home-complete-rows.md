# 首页货架整行布局修复

日期：2026-11-15。基线：2327ca5e7df7a4679cf1a3a130b01554b45daccf。

## 原因与修复

Hot games两张大卡使用grid-column/grid-row的span简写，浏览器把span放在start位置，旧脚本只读end，因此误按1格计数，8列时保留38格形成残行。其他分区又依赖window.load，广告、图片和独立容器变化会让整理延迟或失效。

新增home-grid.js，读取start/end两端span，按dense自动放置模拟真实占格，保留最长完整矩形前缀。DOM ready即可处理，不等待全部媒体；宽度和直接子项变化分别触发ResizeObserver/MutationObserver，并用requestAnimationFrame合并更新。每次先恢复尾卡再计算，缩放可重新展示卡片；少量项目缩减列数，空提示跨整行。键盘焦点被裁切时转到当前分区可见卡片。

保留高密度游戏货架、侧栏、两张大卡和各分区View all入口。仅调整首页预览展示数量，不重复条目、不删除游戏或目录数据。

## 验证结果

- 320、360、390、420、600、720、768、980、1024、1280、1440、1728px共12个屏宽，对Hot games、New games及10分类分区逐格检查，总计144组，缺格均为0。
- 1728px：Hot games 8列×4行，显示26张卡（含2张2×2大卡）；New games 9列×2行，显示18张卡。各分类均8列×4行。
- 390px/320px：Hot games 2列×19行，New games 2列×12行，均完整填充。
- 同一窗口内把主内容容器缩至600px再恢复，全部分区仍无缺格。
- 模拟NEW直接子项删除后自动重排；仅5张卡时形成5列完整单行；模拟全部到期后显示跨满1124px的空提示。
- 焦点卡在窗口变宽后被裁切，焦点正确转至仍可见的游戏卡片。
- 45项unittest、Python/JS语法、布局检测及git diff --check通过。布局检测前后均无额外发现。
- 游戏总数仍为1783；all_games和new_games数据语义与基线一致。构建只改变首页HTML、首页布局脚本/CSS及首页内容指纹。

明细：home-row-viewports.json、home-row-dynamic.json、home-row-container.json。发布结果以最终main的Cloudflare部署回执及真实域名几何核验为准。
