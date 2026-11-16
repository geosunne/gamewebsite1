# PR: fix/T2611161520-game-sitemap-audit

## 背景 / 目标

- 用户反馈 `/games/draw-master` 页面无法游玩，并要求排查其他失效游戏地址并从 sitemap 移除。
- 预检：控制台目录原为 clean；从 `spike/fullstack` 创建独立 worktree。`update_sitemap.py` 原先无条件将 `all_games.json` 的每个游戏 slug 加入 sitemap。
- 问题摘要：Problem — 页面 shell 正常返回 200，但第三方播放器不可用。Attempts — 检查线上响应、浏览器 iframe 画面、全目录播放器 URL HTTP HEAD，并对可疑端点补做 GET / 公共 DNS 查询。Scoped Code Pointers — `update_sitemap.py`、`static_html/all_games.json`、`static_html/sitemap.xml`、`static_html/sitemap.txt`。Open Items — 第三方游戏可用性可能变化，需要在后续周期复查清单。

## 变更摘要

- 新增 `sitemap_excluded_games.json`，记录 6 个从 sitemap 排除的 slug 和检查原因。
- `update_sitemap.py` 读取该清单，并从 XML 与文本 sitemap 排除相应游戏 URL。游戏目录、详情页及播放器嵌入未修改。
- 重新生成 `static_html/sitemap.xml` 和 `static_html/sitemap.txt`，总计 1,821 个 URL，游戏页 1,777 个。

## 影响范围

- 排除地址：`draw-master`、`hopball-3d`、`music-party`、`bike-rush`、`lovely-doll-creator`、`1v1lol`。
- `draw-master`：BTW 页面返回 200，浏览器实际显示黑屏；MiniGame iframe 本身返回 200，但画布为空。
- 4 个 MiniGame iframe 主机 TLS 证书主机名不匹配。`1v1.lol` 域名在 Google 与 Cloudflare DNS 查询中均为 NXDOMAIN。
- 其他 4 个 GameMonetize iframe 的 HEAD 返回 403，但 GET 请求跟随重定向后返回游戏 HTML（206 Range 响应），故保留。其余探测 URL 的 HEAD 均返回 200。

## 风险与回滚

- 仅停止向搜索引擎提交这 6 个详情页地址；详情页仍在目录和站点中可访问。
- 如后续确认游戏恢复，可从 `sitemap_excluded_games.json` 移除相应记录后重新生成 sitemap。

## 验证方式 / 结果

- 在 worktree 隔离 Python 环境中安装 `beautifulsoup4` 后运行 `python update_sitemap.py`：成功，生成 XML / TXT 各 1,821 个 URL，6 个游戏 URL 被排除。
- Python 编译检查通过；解析 XML 并核对 manifest、目录游戏数及 XML/TXT：6 个排除地址均不存在，游戏 sitemap 为 1,777 个 URL，无重复。
- `git diff --check` 通过。未运行单元测试。

## 关键 Diff（自检）

- 修改 `update_sitemap.py` 加载排除清单并过滤游戏 slug。
- 新增排除清单及两份生成后的 sitemap 差异。
