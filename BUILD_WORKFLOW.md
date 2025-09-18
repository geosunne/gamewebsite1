# BTW Games Build Workflow

完整的网站构建流程，从游戏数据采集到静态网站生成。

## 🚀 快速开始

### 方法1: 完整自动构建 (推荐)

```bash
# 完整构建流程 (采集->导入->生成)
python build_website.py

# 自定义游戏数量
python build_website.py --max-games 50

# 构建并启动服务器
python build_website.py --serve
```

### 方法2: 快速构建脚本

```bash
# 快速构建 (默认50个游戏)
./quick_build.sh

# 跳过采集，使用现有数据
./quick_build.sh --skip-scraping

# 构建并启动服务器
./quick_build.sh --serve --port 8002
```

### 方法3: 手动分步执行

```bash
# 1. 采集游戏数据
python analyze_onlinegames_structure.py --max-games 100

# 2. 导入数据库
python import_games_data.py

# 3. 生成静态文件
python generate_static_pages.py

# 4. SEO优化
python optimize_seo.py

# 5. 更新支持文件
python update_game_slugs.py
python update_sitemap.py
```

## 📋 完整流程步骤

### 🕷️ Step 1: 游戏数据采集
- **脚本**: `analyze_onlinegames_structure.py`
- **功能**: 从 onlinegames.io 采集游戏信息
- **输出**: `games_data.json`
- **配置**: 最大游戏数量、超时设置

### 📁 Step 2: 数据库导入
- **脚本**: `import_games_data.py`
- **功能**: 将JSON数据导入SQLite数据库
- **输出**: 更新 `instance/site.db`
- **特性**: 数据去重、字段映射

### 🌐 Step 3: 静态文件生成
- **脚本**: `generate_static_pages.py`
- **功能**: 生成所有静态HTML页面
- **输出**: `static_html/` 目录
- **包含**: 主页、游戏列表、个别游戏页

### 🔧 Step 4: SEO优化
- **脚本**: `optimize_seo.py`
- **功能**: 优化meta标签、结构化数据
- **特性**: Open Graph、Twitter Cards、JSON-LD

### 📊 Step 5: 支持文件更新
- **脚本**: `update_game_slugs.py`, `update_sitemap.py`
- **功能**: 更新游戏slug列表、生成sitemap
- **输出**: `game_slugs.txt`, `sitemap.xml`, `sitemap.txt`

## ⚙️ 配置选项

### Python构建脚本选项

```bash
python build_website.py [options]

--max-games N        # 最大采集游戏数 (默认: 100)
--skip-scraping      # 跳过采集，使用现有JSON
--skip-import        # 跳过数据库导入
--skip-static        # 跳过静态文件生成
--skip-seo           # 跳过SEO优化
--force              # 强制覆盖现有文件
--serve              # 构建后启动服务器
--serve-port PORT    # 服务器端口 (默认: 8001)
```

### Bash快速构建选项

```bash
./quick_build.sh [options]

--max-games N        # 最大采集游戏数 (默认: 50)
--skip-scraping      # 跳过采集
--serve              # 构建后启动服务器
--port N             # 服务器端口 (默认: 8001)
```

## 📁 输出结构

```
static_html/
├── index.html              # 主页
├── games.html              # 游戏列表页
├── games/                  # 个别游戏页面
│   ├── monster-survivors.html
│   ├── puzzle-master.html
│   └── ...
├── assets/                 # 静态资源
│   ├── js/
│   │   └── api.js         # API客户端
│   └── css/
├── all_games.json          # 所有游戏数据
├── new_games.json          # 新游戏数据
├── categories.json         # 分类数据
├── game_slugs.txt          # 游戏slug列表
├── sitemap.xml             # XML站点地图
├── sitemap.txt             # 文本站点地图
└── robots.txt              # 搜索引擎指令
```

## 🔄 开发工作流

### 日常开发

```bash
# 1. 快速构建测试
./quick_build.sh --skip-scraping --serve

# 2. 修改模板文件 (static/*)
# 3. 重新构建
./quick_build.sh --skip-scraping

# 4. 查看结果
```

### 数据更新

```bash
# 1. 采集新数据
python build_website.py --max-games 200

# 2. 完整重建
python build_website.py --skip-scraping
```

### 生产部署准备

```bash
# 1. 完整构建
python build_website.py --max-games 100

# 2. 验证输出
ls -la static_html/

# 3. 测试本地服务
python build_website.py --skip-scraping --serve

# 4. 部署 static_html/ 目录
```

## 🐛 故障排除

### 采集失败
```bash
# 检查网络连接
curl -I https://www.onlinegames.io

# 增加超时时间
timeout 600 python analyze_onlinegames_structure.py

# 减少游戏数量
python build_website.py --max-games 20
```

### 数据库错误
```bash
# 重置数据库
rm -f instance/site.db
flask db upgrade

# 重新导入
python import_games_data.py
```

### 静态生成失败
```bash
# 检查模板文件
ls -la static/
ls -la templates/

# 手动生成
python generate_static_pages.py

# 检查权限
chmod -R 755 static_html/
```

### 服务器启动失败
```bash
# 检查端口占用
lsof -i :8001

# 使用不同端口
python build_website.py --serve --serve-port 8002

# 使用基础服务器
cd static_html && python -m http.server 8003
```

## 📊 性能优化

### 构建速度优化
- 使用 `--skip-scraping` 跳过采集
- 减少 `--max-games` 数量
- 并行执行非依赖步骤

### 输出优化
- 压缩图片和资源
- 最小化CSS/JS
- 优化HTML结构

## 🚀 部署选项

### 静态托管平台
- **Vercel**: 直接部署 `static_html/`
- **Netlify**: 拖拽部署
- **GitHub Pages**: 推送到 gh-pages 分支
- **Cloudflare Workers**: 使用 Workers Sites

### 传统服务器
```bash
# Nginx配置
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/static_html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 💡 最佳实践

1. **定期更新**: 每周运行一次完整构建
2. **数据备份**: 备份 `games_data.json` 和数据库
3. **版本控制**: 排除 `static_html/` 和数据文件
4. **监控**: 检查构建日志和错误
5. **测试**: 本地验证后再部署

## 📞 支持

如果遇到问题：
1. 检查依赖是否安装完整
2. 查看错误日志
3. 确认网络连接
4. 验证文件权限
5. 查阅此文档的故障排除部分