# AGENTS.md

## 0. 输出与协作要求

- 所有任务执行结果、进度、结论、风险、验证记录必须使用中文输出。
- 若需要生成并保存简报，且用户未指定路径，默认保存到 `docs/logs/YYYYMMDD/`，`YYYYMMDD` 使用生成当日日期。
- 修改代码前先读相关文件与当前 Git 状态，避免覆盖用户未提交改动。
- 不要提交 `.env`、数据库、抓取备份、系统文件等敏感或生成文件，除非用户明确要求。

## 1. 项目概览

BTW Games 是 Flask 游戏聚合站，包含两种运行模式：

- 开发/管理模式：Flask + SQLAlchemy + SQLite，提供游戏、分类、统计、后台管理 API。
- 生产发布模式：从数据库生成 `static_html/` 静态站点，部署时不需要后端服务。

核心数据流：

1. `analyze_onlinegames_structure.py` 抓取 onlinegames.io 游戏数据，生成 `games_data.json`。
2. `import_games_data.py` 导入 SQLite。
3. `generate_static_pages.py` 生成游戏详情页与 `all_games.json`。
4. `optimize_seo.py` 优化 meta、Open Graph、结构化数据。
5. `update_sitemap.py` 生成 `sitemap.xml` 和 `robots.txt`。

## 2. 关键目录与文件

- `app.py`：Flask 应用工厂，注册 API、Admin、Main blueprint。
- `models.py`：SQLAlchemy 模型与 Marshmallow schema。
- `routes/api.py`：公开 API，路径前缀 `/api`。
- `routes/admin.py`：后台 API，路径前缀 `/admin`，当前使用固定 `X-API-Key`。
- `routes/main.py`：静态页面与模板路由。
- `static/`：开发态前端页面与源资源。
- `templates/`：Flask 动态模板。
- `static_html/`：生成后的静态站点产物。
- `instance/btw_games.db`：当前有效 SQLite 数据库。
- `btw_games.db`：当前为空库，不要误用。
- `games_data.json`：抓取数据中间文件。
- `build_website.py`：完整构建编排脚本。
- `quick_build.sh`：快速构建脚本。
- `serve_static.py`：本地静态站点服务。

## 3. 当前环境注意事项

- 本机 `python` 命令可能不可用，优先使用 `python3`。
- 当前 `venv` 可能失效，曾发现其解释器指向旧机器路径。若命令失败，先重建虚拟环境。
- `requirements.txt` 曾缺 Flask 相关依赖；运行 Flask 前确认依赖完整。
- `.env` 当前可能配置 `DATABASE_URL=sqlite:///btw_games.db`，但真实数据在 `instance/btw_games.db`。运行动态服务前确认数据库 URI。
- `http://localhost:8080/v1/responses` 不是本项目接口；本项目常用端口为 Flask `5000`、静态服务 `8000/8001`。

## 4. 常用命令

### 环境准备

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

若需要补齐 Flask 依赖：

```bash
python3 -m pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Cors Flask-Marshmallow marshmallow-sqlalchemy python-dotenv
```

### 启动 Flask 开发服务

```bash
DATABASE_URL=sqlite:///instance/btw_games.db python3 run.py
```

默认访问：

- 首页：`http://localhost:5000/`
- API：`http://localhost:5000/api/games`
- 后台：`http://localhost:5000/admin`

### 数据库操作

```bash
python3 init_db.py
python3 seed_data.py
python3 import_games_data.py
```

### 静态站点构建

```bash
python3 build_website.py --skip-scraping
```

分步执行：

```bash
python3 analyze_onlinegames_structure.py --max-games 100
python3 import_games_data.py
python3 generate_static_pages.py
python3 optimize_seo.py
python3 update_sitemap.py
```

### 静态站点本地预览

```bash
python3 serve_static.py --port 8000 --no-browser
```

访问：`http://localhost:8000/`

## 5. 验证清单

修改后优先按影响范围验证：

- 后端/API：启动 Flask 后访问 `/api/stats/games`、`/api/categories`、`/api/games?per_page=3`。
- 静态产物：检查 `static_html/index.html`、`static_html/games.html`、`static_html/all_games.json`、`static_html/sitemap.xml`。
- 游戏页数量：确认 `static_html/all_games.json` 中游戏数量与 `static_html/games/*.html` 匹配。
- 前端改动：启动 `serve_static.py` 后用浏览器检查首页、游戏列表、至少一个详情页。

可用快速检查：

```bash
python3 - <<'PY'
import json, os
games = json.load(open('static_html/all_games.json', encoding='utf-8'))['games']
missing = []
for game in games:
    slug = game.get('slug') or game.get('id')
    if slug and not os.path.exists(f'static_html/games/{slug}.html'):
        missing.append(slug)
print('games:', len(games))
print('missing_pages:', len(missing))
print('missing_sample:', missing[:20])
PY
```

## 6. 开发约定

- 改模板源文件优先改 `static/` 或 `templates/`，再重新生成 `static_html/`。
- 不要手动批量编辑 `static_html/games/*.html`，除非任务明确只修静态产物。
- 生成脚本中的 HTML 字符串需注意转义，避免标题、描述、URL 注入破坏页面。
- API 变更需同步检查 `static/assets/js/api.js` 与静态页面调用方式。
- 后台管理接口当前 API Key 硬编码在 `routes/admin.py`，涉及生产部署时应改为环境变量。
- 修改抓取逻辑时保留对旧 `games_data.json` 结构的兼容，避免导入链路断裂。

## 7. 已知风险

- `.env` 中含真实 Analytics/AdSense 配置，避免在输出中重复暴露或传播。
- 当前后台认证较弱，不适合公网暴露。
- `requirements.txt` 与实际 Flask 依赖可能不一致，修环境时优先补齐并验证。
- `build_website.py` 内部可能仍调用 `python`，在没有 `python` 命令的 macOS 环境会失败。
- `static_html/` 是生成产物，体积较大，提交前确认是否需要纳入版本控制。
