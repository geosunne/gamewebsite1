# 静态化BTW Games网站

## 📁 文件结构

```
static_html/
├── index.html              # 首页
├── games.html             # 游戏列表页
├── assets/
│   └── js/
│       └── api.js         # 静态API客户端
├── games/                 # 游戏详情页
│   ├── monster-survivors.html
│   ├── papas-donuteria.html
│   └── ... (25个游戏页面)
├── all_games.json         # 所有游戏数据
├── new_games.json         # 新游戏数据
├── categories.json        # 分类数据
└── _redirects             # 重定向配置

```

## 🚀 部署选项

### 选项1: Netlify (推荐)
```bash
# 1. 将static_html文件夹拖拽到Netlify部署页面
# 2. 或者通过Git连接
cd static_html
git init
git add .
git commit -m "Static BTW Games"
git remote add origin your-repo-url
git push -u origin main
```

### 选项2: Cloudflare Pages
```bash
# 1. 上传到GitHub
# 2. 连接Cloudflare Pages到仓库
# 3. 构建设置：
#    - 构建命令: (留空)
#    - 构建输出目录: /
```

### 选项3: Vercel
```bash
# 使用Vercel CLI
cd static_html
npx vercel --prod
```

### 选项4: GitHub Pages
```bash
# 1. 创建GitHub仓库
# 2. 上传static_html内容到gh-pages分支
# 3. 在Settings > Pages中启用GitHub Pages
```

## ✅ 功能特性

- ✅ 完全静态化，无需服务器
- ✅ 25个游戏页面全部生成
- ✅ 响应式设计，支持移动端
- ✅ SEO优化，每个页面都有meta标签
- ✅ Google Analytics集成
- ✅ 快速加载，CDN友好
- ✅ 搜索和分类过滤功能
- ✅ 游戏嵌入和analytics追踪

## 🔧 配置说明

### 修改域名
在部署前，需要修改以下文件中的域名：
- `assets/js/api.js` - 如果需要连接后端API
- 各游戏页面的canonical URL

### Google Analytics
所有页面已配置Google Analytics ID: `G-SM7PBYVK97`

### 广告配置
已配置Google AdSense ID: `ca-pub-8930741225505243`

## 📊 统计信息

- 总页面数: 27个 (首页 + 游戏列表 + 25个游戏页面)
- 总文件大小: ~2MB
- 支持的游戏: 25个
- 分类数: 7个

## 🎯 使用方法

1. 选择上述任一部署平台
2. 上传static_html文件夹内容
3. 配置自定义域名（可选）
4. 享受超快的静态网站！

## 📝 注意事项

- 所有游戏数据都是预加载的静态数据
- 游戏播放统计只记录到本地日志
- 如需实时数据更新，需要重新生成静态文件
- 搜索功能基于客户端JavaScript实现