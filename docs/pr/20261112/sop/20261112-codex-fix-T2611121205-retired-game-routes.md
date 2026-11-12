# PR: codex/fix-T2611121205-retired-game-routes

## 背景与目标

23 个 Playhop 游戏已从目录、源码和部署产物移除，Pages 源站均返回 404；自定义域名仍对部分旧地址返回带 Age 的旧 HTML。完成按 URL、前缀及站点整体缓存清理后，复查仍可见旧响应，因此为已退役地址增加明确的 404 路由。

## 预检

- 问题：主域名 11 个旧地址仍返回 200，www 复查有 4 个旧副本；新目录、200 个新增游戏及源站数据均正确。
- 已做尝试：Cloudflare 控制台提交两批 URL 清理、11 个路径前缀及一次清除所有内容，收到成功回执；未配置 Cache Rules，旧响应仍存在，具体缓存层未证实。
- 定位入口：generate_static_pages.py 的构建出口、Cloudflare Pages Advanced Mode 与 Functions invocation routes。
- 待验证：边缘路由是否覆盖旧缓存，正常静态路径是否继续直出；本轮在隔离 worktree 完成实现与本地验证，推送后复查生产。

## 变更摘要

1. retired_games.json 记录 23 个退役游戏；site_retirements.py 生成发布目录中的 _worker.js 和 _routes.json。
2. 精确匹配 23 个游戏的无后缀、.html、尾斜杠地址，共 69 条规则；正常静态路径不进入该边缘处理器。
3. 处理器读取当前 404 页面，返回真实 HTTP 404、noindex 和 no-store，移除 Age/ETag；GET 和 HEAD 均有明确行为。
4. 合法游戏未来重新使用同一个 slug 时，构建会自动解除对应退役路由；全部恢复时删除已无用途的 Worker 产物。
5. 构建集成、Node.js 行为测试及项目验证说明同步更新。游戏数据、HTML、图片与 sitemap 链接保持不变，未保留重建产生的无内容变化时间戳。

## 验证结果

- Python 语法检查通过，静态构建及 SEO/sitemap 流程通过，仍为 1,583 个游戏、30 个分类、1,626 个 sitemap URL。
- test_seo_repairs、test_crazygames_geo、test_retired_routes：26 项测试全部通过。
- Node.js 使用会返回旧 200 页的模拟 ASSETS 验证三个 URL 形式、GET/HEAD、无条件读取当前错误页、404/no-store/noindex、清除旧缓存响应头及合法相邻游戏透传。
- 生成路由共 69 条，满足 Cloudflare 的 100 条规则上限；未使用覆盖全站的通配符。
- git diff --check 通过。生产结果需以本次推送后对实际域名的验证为准。

## 风险与回滚

退役路径引入 Pages Functions，正常静态路径由调用规则排除。需保留构建生成的两个运行文件；回滚本次合并可移除边缘处理器并恢复先前静态部署方式。没有修改数据库、凭据、DNS、缓存规则或安全设置。

## 参考

- https://developers.cloudflare.com/pages/functions/advanced-mode/
- https://developers.cloudflare.com/pages/functions/routing/
