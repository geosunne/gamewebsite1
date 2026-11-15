# PR: codex/fix-T2611151707-brand-identity

## 背景与目标

落实与 watersort.ai 对比后确认的品牌优化：修复页头白色手柄按键消失、统一品牌图形来源、完善独立分享封面及移动端 Logo 组合，并发布到生产。

## 预检

- 问题：页头 SVG 的按键与主体同为白色，favicon 却有对比色按键；站点大图分享使用 512px 方形图标，移动端 slogan 约 10.56px。
- 已做尝试：线上桌面/窄屏和图标文件对比；当前 ICO、96px PNG、180px Apple 图标及方形 Organization.logo 均可访问。
- 定位入口：generate_static_pages.py 的品牌和 head 渲染，site_icons.py、optimize_seo.py、site.css 及 favicon.svg。
- 待验证：共享母版导出、页面与 SEO 后处理一致性、游戏图片角色、窄屏排版、线上资源和发布结果。

## 变更摘要

1. 页头直接引用 favicon.svg 母版，修复不可见按键；加入 W 形桥接及紫、绿按键，保留珊瑚橙方向。
2. build_brand_assets.py 从母版导出 96/512px PNG、多尺寸 ICO、180px 全底色 Apple 图标和兼容的 300×75 横版 Logo。requirements 和项目说明同步补充导出依赖。
3. 生成 1200×630 分享封面，使用九个现有目录游戏的真实缩略图、BTW game、By the way, play! 及域名。
4. 统一默认分享图片、og:site_name、图片尺寸与替代文字、twitter:image:alt、theme-color。游戏页保留游戏图片，Organization.logo 保留方形图标。
5. 桌面 slogan 为 12px；720px 及以下使用图标和品牌名的紧凑组合。修复页脚链接不换行导致的窄屏横向溢出。
6. 重新生成静态站，品牌图形覆盖全部页面；游戏目录为 1,783 项、分类 31 个、sitemap 1,827 条。

## 验证结果

- 品牌资产导出、Python 语法检查、完整生成、SEO 和 sitemap 构建通过。
- test_seo_repairs、test_crazygames_geo、test_retired_routes、test_catalog_freshness、test_home_grid、test_brand_assets：49 项测试全部通过。
- 全量检查 1,827 个 HTML 的母版引用；1,826 个成功页面的分享 metadata 无重复，所有本地图片的声明尺寸与真实文件相同。一个既有远程游戏图片不填写无法确认的尺寸；404 保留非索引错误页语义。
- 1,783 项游戏数据与基线相同，sitemap.xml/sitemap.txt 一致，退役路由和已有游戏图片的用途检查通过。
- Ego Lite 两轮本地检查：1440px 桌面、390px 窄屏、分类页和游戏页。窄屏 width/clientWidth/scrollWidth 均为 390px；图标为 34px，slogan 隐藏，桌面图标 38px、slogan 12px。
- 分享封面、96px favicon、兼容横版 Logo 和桌面/窄屏截图均已目视核验。git diff --check 通过。
- 生产部署及公网校验在本次推送后执行，以最终发布结果为准。

## 影响范围与回滚

生产静态站的品牌展示、分享 metadata、品牌导出工具、静态产物、设计说明及验证。图标导出需要 CairoSVG、Pillow 和系统 Cairo；常规游戏构建直接复制已提交的资产。搜索引擎图标展示取决于后续抓取和选择。需要回滚时撤销本任务合并并重新发布对应静态产物。
