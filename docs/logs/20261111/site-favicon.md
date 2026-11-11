# BTW game 网站图标修复

日期：2026-11-11。

## 原因

首页和各类页面未声明 favicon，根目录缺少 favicon.ico；原默认图片仍为旧的蓝色 btwgames 文字标识。

## 修复

- 使用当前珊瑚橙手柄品牌标志。
- 提供根目录 favicon.ico，包含 16、32、48、64、96、128、256px。
- 搜索图标使用 /assets/icons/favicon-96x96.png，格式为 PNG，方形 96×96。
- 触屏图标使用 /assets/icons/apple-touch-icon.png，180×180，不透明背景。
- 默认分享图和组织 logo 使用 /assets/icons/favicon-512x512.png，替代旧的蓝色文字图片。
- /assets/icons/favicon.svg 为可维护的矢量源；搜索声明使用 Google 文档列出的 PNG / ICO 格式。
- 共享图标声明接入页面生成器、SEO 后处理和 Flask 模板；构建自动同步根目录 ICO。

## 本地验证

- 全部 1448 个发布 HTML 的图标声明存在且无重复，文件全部可解析。
- PNG 和 ICO 尺寸正确，源目录与部署目录 ICO 内容一致。
- 图标本地 HTTP 返回 200，Content-Type 为图像类型。
- robots 允许 Googlebot 抓取首页、Googlebot-Image 抓取图标。
- 重复运行 SEO 图标注入不会新增重复标签。
- 19 项回归测试通过，1406 个游戏记录保持一致。

## 搜索结果刷新

网站发布与 Google 搜索缓存更新是两个步骤。文件上线后，Google 仍需重新抓取首页和图标，通常需数天到数周；是否显示由 Google 决定。

官方依据：https://developers.google.com/search/docs/appearance/favicon-in-search
