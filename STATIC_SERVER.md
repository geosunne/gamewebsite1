# BTW Games Static Development Server

快速启动静态网站进行本地调试和测试。

## 🚀 快速开始

### 方法1: 使用 Python 脚本 (推荐)

```bash
# 基本用法
python serve_static.py

# 自定义端口
python serve_static.py --port 3000

# 允许外部访问
python serve_static.py --host 0.0.0.0

# 不自动打开浏览器
python serve_static.py --no-browser

# 查看帮助
python serve_static.py --help
```

### 方法2: 使用 Bash 脚本

```bash
# 默认端口 8000
./serve.sh

# 自定义端口
./serve.sh 3000
```

### 方法3: 直接使用 Python HTTP 服务器

```bash
cd static_html
python -m http.server 8000
```

## 📁 目录结构

确保你的项目有以下结构：

```
gamewebsite1/
├── static_html/           # 静态文件目录
│   ├── index.html        # 主页
│   ├── games.html        # 游戏列表页
│   ├── games/            # 个别游戏页面
│   │   ├── monster-survivors.html
│   │   └── ...
│   ├── assets/           # 静态资源
│   │   ├── js/
│   │   └── css/
│   ├── sitemap.xml       # XML站点地图
│   ├── sitemap.txt       # 文本站点地图
│   └── robots.txt        # 搜索引擎指令
├── serve_static.py       # Python 服务器脚本
├── serve.sh              # Bash 快捷脚本
└── STATIC_SERVER.md      # 本文档
```

## ✨ 特性

### Python 服务器脚本特性:
- ✅ 智能路由处理
- ✅ 自动MIME类型检测
- ✅ 自定义404页面
- ✅ CORS头支持
- ✅ 请求日志记录
- ✅ 自动打开浏览器
- ✅ 端口冲突检测

### Bash 脚本特性:
- ✅ 端口冲突自动处理
- ✅ 彩色输出提示
- ✅ 跨平台浏览器启动
- ✅ 错误检查和验证

## 🔧 路由处理

Python服务器支持以下路由:

- `/` → `static_html/index.html`
- `/games.html` → `static_html/games.html`
- `/games/monster-survivors` → `static_html/games/monster-survivors.html`
- `/assets/js/api.js` → `static_html/assets/js/api.js`
- 其他静态文件按路径直接映射

## 🐛 调试功能

### 查看请求日志
Python服务器会显示所有HTTP请求:
```
[2025-01-20 15:30:45] "GET / HTTP/1.1" 200 -
[2025-01-20 15:30:46] "GET /assets/js/api.js HTTP/1.1" 200 -
[2025-01-20 15:30:47] "GET /games/monster-survivors HTTP/1.1" 200 -
```

### 自定义404页面
访问不存在的页面会显示友好的404页面，包含返回链接。

### CORS支持
开发服务器添加了CORS头，支持前端API调用。

## 🛠️ 故障排除

### 端口被占用
```bash
# 检查端口使用情况
lsof -i :8000

# 使用不同端口
python serve_static.py --port 3000
./serve.sh 3000
```

### 静态文件未找到
```bash
# 确保在项目根目录
pwd

# 检查静态文件是否存在
ls static_html/

# 重新生成静态文件
python generate_static_pages.py
```

### Python模块错误
```bash
# 检查Python版本
python --version

# 确保使用Python 3
python3 serve_static.py
```

## 📱 移动设备测试

### 局域网访问
```bash
# 允许局域网访问
python serve_static.py --host 0.0.0.0

# 查找本机IP
ifconfig | grep "inet "
```

然后在移动设备上访问: `http://[你的IP]:8000`

## 🔄 开发工作流

1. **修改源文件** (templates, data, etc.)
2. **重新生成静态文件**:
   ```bash
   python generate_static_pages.py
   ```
3. **启动开发服务器**:
   ```bash
   python serve_static.py
   ```
4. **在浏览器中测试**
5. **刷新页面查看更改**

## 📊 性能优化

开发服务器包含以下优化:
- 禁用缓存头 (方便开发)
- 压缩响应 (自动)
- 快速文件服务
- 最小化日志开销

## 🚀 生产部署

此服务器仅用于开发！生产环境请使用:
- Nginx
- Apache
- Cloudflare Workers
- Vercel
- Netlify

## 💡 提示

- 使用 `Ctrl+C` 停止服务器
- 修改文件后刷新浏览器即可看到更改
- 使用浏览器开发工具检查网络请求
- 检查控制台错误和警告