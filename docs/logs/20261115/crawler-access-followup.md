# 抓取访问核查与剩余证据边界

日期：2026-11-15。本站文件与正文检查已执行；本记录不把模拟 User-Agent 当作真实搜索爬虫。

## 已执行

- 普通浏览器可打开 BTW game 的首页、目录与详情。
- 使用 Requests 对 robots.txt、sitemap.xml、Space Waves 页面进行15次公开HTTP探测（含不同User-Agent字符串），本次均返回200。
- 使用真实Python urllib客户端对上述三个路径复查，返回403和Cloudflare 1010；同一个UA字符串通过Requests获得200，说明不能只根据User-Agent推断拦截原因。
- 已保存robots正文、请求路径、状态、CF-Ray和UTC核对时间，见 crawler-access-check.json。公开robots允许游戏HTML与渲染资产；JSON目录不作为索引页面。
- Cloudflare在Ego及现有Chrome会话中都显示登录页面。现有Chrome的Google账户已登录Search Console，但平台明确拒绝其访问btwgame.com；已检查可访问的资源选择列表，没有本站对应资源。未找到配置的Cloudflare API或Search Console凭据，无法读取实际域名日志、已验证机器人身份或URL检查结果。

## 后续在已有权限的账户中核验

1. Cloudflare选择btwgame.com，在Security Analytics/Events查本记录时间附近请求，结合CF-Ray定位urllib的1010，再检查经过验证的搜索机器人是否受到相同规则影响。
2. 区分请求指纹、IP/ASN、Bot规则及具体防火墙规则；若真实搜索机器人受误拦，应按已验证机器人身份和目标路径制定最小例外，不能仅凭UA文本放行。
3. Search Console选择实际拥有访问权的btwgame.com资源，对首页、/games、/games/space-waves和一个待确认条目进行URL检查与实时测试，核对抓取状态、Google选择的canonical及渲染正文。
4. 检查sitemap提交与解析结果、最近抓取时间、有效索引和排除原因。记录查询时段与平台回执；公开HTTP200、构建成功和Cloudflare部署成功都不能替代这些证据。

尚未得到真实爬虫或索引结果，不能声称已解决Google/Bing/AI搜索抓取问题，也不能据本次urllib403认定这些服务被拦截。
