# PR: feat/T260620-polish-mock-fidelity

## 背景 / 目标
- 按已确认的 C + A 混合方向，继续 polish 全站，使首页、游戏目录页和游戏详情页更接近 approved mocks。
- 保留 BTW game 的 Coral / Orange 主行动色，不回到以蓝色为主的按钮与品牌系统。
- 优先提升首屏目录感、游戏卡片密度、左侧分类导航、详情页一致性和远程缩略图慢加载时的观感。

## 变更摘要
- 首页改为 app-store catalog 首屏：左侧探索 rail、搜索、彩色分类 lane、Top games 游戏墙、信任 proof strip、FAQ / About 模块。
- 游戏目录页改为统一 app-layout：左侧 rail、集中搜索/排序/分类 chips、紧凑游戏卡片网格、底部说明与 FAQ。
- 详情页生成模板移除旧内联 CSS，复用 `static/assets/css/site.css`，统一 header、rail、游戏 iframe 区、信息卡片、proof strip 和相关游戏卡片。
- 更新共享 CSS，新增 `home-layout`、`app-layout`、`side-rail`、`play-proof`、`faq-panel`、详情页 polish 样式与响应式规则。
- 首页和目录页首屏卡片图片改为 eager 加载，并把缩略图 fallback 改为标题字母占位，避免第三方图片慢加载时看起来像空缩略图。
- 重新生成 `static_html/`，包含 497 个详情页、`all_games.json`、`sitemap.xml`、`sitemap.txt`、`robots.txt` 和 `_redirects`。

## 影响范围
- 影响公开前端页面：`/`、`/games`、`/games/{slug}`。
- 影响静态生成脚本 `generate_static_pages.py` 和静态产物。
- 不修改数据库 schema、API 响应结构、抓取逻辑或后台管理接口。

## 风险与回滚
- `static_html/games/*.html` 为批量生成产物，diff 较大但来源于 `generate_static_pages.py`。
- 第三方游戏 iframe 和广告脚本仍可能在本地/测试环境产生外部网络错误，本次未改第三方来源。
- 远程缩略图依赖 onlinegames.io，已保留 fallback 占位降低慢加载观感风险。
- 回滚方式：revert 本分支 merge，或回退 `static/`、`generate_static_pages.py` 后重新生成静态产物。

## 验证方式 / 结果
- `python3 -m py_compile generate_static_pages.py optimize_seo.py update_sitemap.py serve_static.py build_website.py`：通过。
- `DATABASE_URL=sqlite:////Users/bjit208/Documents/Work/code/myself/_wt/feat-T260620-polish-mock-fidelity/instance/btw_games.db python3 generate_static_pages.py`：成功生成 497 个详情页，错误 0。
- `python3 optimize_seo.py && python3 update_sitemap.py`：通过，sitemap 共 499 个 URL。
- 静态数据检查：`all_games.json` 497 条，`static_html/games/*.html` 497 个，缺失 0。
- HTTP 检查：`/` 200，`/games` 200，`/assets/css/site.css` 200，`/all_games.json` 200，`/api/categories` 200，`/api/games?per_page=3` 200，`/games/papas-donuteria` 200。
- Clean URL 检查：`/games/papas-donuteria.html` 308 到 `/games/papas-donuteria`，`/games/papas-donuteria/` 308 到 `/games/papas-donuteria`。
- SEO 抽查：`/`、`/games`、`/games/papas-donuteria` canonical 均为无 `.html`、无尾斜杠 URL；无 `btwgames` / `BTW Games` 品牌残留。
- Playwright + 系统 Chrome 检查：桌面和移动的 `/`、`/games`、`/games/papas-donuteria` 均 200，无横向溢出，无页面 JS 错误；详情页 iframe 区存在，首页/目录/详情关键模块存在。

## 关键 Diff（自检）
- `static/assets/css/site.css`
- `static/index.html`
- `static/games.html`
- `generate_static_pages.py`
- `static_html/`
