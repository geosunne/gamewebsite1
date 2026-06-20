# PR: feat/T260620-full-site-redesign

## 背景 / 目标
- 按已确认的 C + A 混合方向，为 BTW game 做一版全站新视觉方向用于后续迭代。
- 主品牌色从蓝色调整为更活泼的 Coral / Orange，保留浅色、可信、快速浏览的游戏目录体验。
- 统一品牌名为 `BTW game`，含义承接 `By the way, play a quick game`。

## 变更摘要
- 新增共享样式 `static/assets/css/site.css`，定义 Coral 主色、分类色、布局、游戏卡片、目录筛选、详情页和响应式规则。
- 重写 `static/index.html` 首页，改为品牌搜索、分类入口、新游戏和热门游戏网格。
- 重写 `static/games.html` 游戏目录页，新增桌面分类 rail、搜索和排序工具条、移动端适配。
- 更新 `generate_static_pages.py` 生成的游戏详情页品牌、颜色、SEO 文案和共享 CSS 引用。
- 更新 `optimize_seo.py`：品牌名、500+ 文案、robots 允许 CSS/JS 渲染资源、首页 JSON-LD 去重。
- 修复 `serve_static.py` clean URL 路由：`/games` 优先映射 `games.html`，避免被 `static_html/games/` 目录吞掉导致 404。
- 重新生成 `static_html/`，包含 497 个游戏详情页、sitemap、robots 和静态数据。
- 更新 `PRODUCT.md`、`DESIGN.md`，记录当前设计方向与 token 约定。

## 影响范围
- 影响公开前端页面：`/`、`/games`、`/games/{slug}`。
- 影响静态生成流程、SEO 后处理、本地静态服务 clean URL 解析。
- 不修改数据库 schema、游戏数据导入逻辑、公开 API 响应结构。

## 风险与回滚
- `static_html/games/*.html` 为批量生成产物，本次 diff 较大但来源于 `generate_static_pages.py`。
- 游戏 iframe 中第三方脚本在本地 Chrome 可能出现跨域或广告相关 console 错误，生产环境是否允许由第三方源策略决定，本次未改 iframe 来源。
- 回滚方式：revert 本 merge 或回退 `static/`、`generate_static_pages.py`、`optimize_seo.py`、`serve_static.py` 后重新生成静态产物。

## 验证方式 / 结果
- `python3 -m py_compile generate_static_pages.py optimize_seo.py update_sitemap.py serve_static.py build_website.py`：通过。
- `DATABASE_URL=sqlite:////Users/bjit208/Documents/Work/code/myself/_wt/feat-T260620-full-site-redesign/instance/btw_games.db python3 generate_static_pages.py && python3 optimize_seo.py && python3 update_sitemap.py`：成功生成 497 个详情页，错误 0。
- 静态产物检查：`all_games.json` 497 条，`static_html/games/*.html` 497 个，缺失 0，`static_html/assets/css/site.css` 存在。
- URL 状态检查：`/games` 200，`/games/papas-donuteria` 200，`/games/papas-donuteria.html` 308 到 `/games/papas-donuteria`，`/games/papas-donuteria/` 308 到 `/games/papas-donuteria`。
- API 检查：`/api/categories` 200，`/api/games?per_page=3` 200。
- Playwright + 系统 Chrome 检查：`/`、`/games`、`/games/papas-donuteria` 均 200，CSS 已加载，桌面和移动无水平溢出，本地页面错误过滤后为空。

## 关键 Diff（自检）
90102f9 (HEAD -> feat/T260620-full-site-redesign, spike/fullstack) merge: chore/T260620-git-repository-hygiene
d8f8ee7 chore: add git hygiene PR note
6a743c8 chore: add git hygiene and sop runner skill
5b6735d (origin/main, origin/HEAD, main) Avoid trailing slash redirects for game pages
d84975f Add static data fallback for game API
8d60e38 Fix games page asset path
5ee4704 Merge codex/clean-url-site
757957e (codex/clean-url-site) Add product and design system docs
89571bd (origin/codex/clean-url-site) Use clean URLs for static game pages
5d1d48b Fix static SEO and game routes
d3fbddc add sitemap.xml change
b2d946b text change
438e2a3 change the text
a03c698 change the ad tag
a3af13c install monetag ads
3ea1f73 monetag
6141184 一些非静态页面的修改
cf10df0 修改了游戏的分类
de41cbf 增加了大量新游戏，更新了sitemap.xml和sitemap.txt
eb6aaf0 modify sitemap.xml

## Diff (spike/fullstack...HEAD)

