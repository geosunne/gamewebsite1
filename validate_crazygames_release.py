"""Audit a weekly catalog delta locally, or verify the deployed public artifacts."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup
from PIL import Image

from catalog_quality import has_blocked_embed
from import_crazygames_embed_games import identity_keys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sitemap_urls(raw):
    return [node.text for node in ET.fromstring(raw).findall("{*}url/{*}loc")]


def check_page(raw, game):
    soup = BeautifulSoup(raw, "lxml")
    canonical = soup.find("link", rel="canonical")
    require(canonical and canonical.get("href") == f"https://btwgame.com/games/{game['slug']}", f"canonical: {game['slug']}")
    require(len(soup.find_all("h1")) == 1, f"H1: {game['slug']}")
    text = " ".join(soup.stripped_strings)
    require(game["controls"]["Controls"] in text, f"完整来源操作说明: {game['slug']}")
    require(soup.find("a", href=game["game_url"]), f"来源链接: {game['slug']}")
    schemas = [json.loads(script.string) for script in soup.select('script[type="application/ld+json"]')]
    require(any(item.get("@type") == "VideoGame" for item in schemas), f"VideoGame: {game['slug']}")
    faq = next(item for item in schemas if item.get("@type") == "FAQPage")
    require([q["name"] for q in faq["mainEntity"]] == [q.get_text() for q in soup.select(".faq-item summary")], f"FAQ: {game['slug']}")


def check_image(raw, slug):
    with Image.open(BytesIO(raw)) as image:
        require(image.format == "WEBP" and image.size == (320, 200), f"缩略图: {slug}")


def local_audit(baseline, expected):
    root = Path("static_html")
    games = json.loads((root / "all_games.json").read_text())["games"]
    old = {g["slug"]: g for g in baseline["games"]}
    current = {g["slug"]: g for g in games}
    require(len(current) == len(games), "目录 slug 重复")
    require(set(old) <= set(current), "旧游戏被移除")
    added = [g for g in games if g["slug"] not in old]
    require(len(added) == expected and len(games) - baseline["count"] == expected, "净新增数量不符")
    batch = json.loads(Path("crazygames_games.json").read_text())["metadata"]["latest_import"]
    require(set(batch["added_slugs"]) == {g["slug"] for g in added}, "本批次与目录增量不一致")
    known = set().union(*(identity_keys(g) for g in baseline["games"]))
    for game in added:
        require(not (known & identity_keys(game)), f"身份重复: {game['slug']}")
        known.update(identity_keys(game))
        require(game.get("allow_embed") is True and not has_blocked_embed(game), f"嵌入许可: {game['slug']}")
        require(game.get("source_id") and game.get("source_checked_at") and game.get("supported_devices"), f"来源事实: {game['slug']}")
        require(game.get("controls", {}).get("Controls"), f"来源操作缺失: {game['slug']}")
        require(game.get("embed_validation", {}).get("responses"), f"嵌入检查证据缺失: {game['slug']}")
        require(game["thumbnail_url"].startswith("/assets/thumbnails/"), f"非本地图片: {game['slug']}")
        check_page((root / "games" / f"{game['slug']}.html").read_text(), game)
        check_image((root / game["thumbnail_url"].lstrip("/")).read_bytes(), game["slug"])
        source_image = Path("static") / game["thumbnail_url"].lstrip("/")
        require(source_image.read_bytes() == (root / game["thumbnail_url"].lstrip("/")).read_bytes(), f"源图与部署图不符: {game['slug']}")
    for slug, game in old.items():
        for key in ("source", "source_id", "title", "iframe_url", "thumbnail_url"):
            require(game.get(key) == current[slug].get(key), f"旧游戏被意外改写: {slug}/{key}")
    require({p.stem for p in (root / "games").glob("*.html")} == set(current), "详情页与目录不一致")
    xml_urls = sitemap_urls((root / "sitemap.xml").read_bytes())
    txt_urls = (root / "sitemap.txt").read_text().splitlines()
    require(xml_urls == txt_urls and len(set(xml_urls)) == len(xml_urls), "sitemap XML/TXT 不一致或重复")
    require({f"https://btwgame.com/games/{g['slug']}" for g in games} <= set(xml_urls), "sitemap 缺游戏")
    links = 0
    pages = list(root.rglob("*.html"))
    for path in pages:
        soup = BeautifulSoup(path.read_text(), "lxml")
        if path.name != "404.html":
            canonical_path = "/" if path.name == "index.html" else "/" + str(path.relative_to(root)).removesuffix(".html")
            canonical = soup.find("link", rel="canonical")
            require(canonical and canonical.get("href") == "https://btwgame.com" + canonical_path, f"全站 canonical: {path}")
        for node in soup.select("a[href], link[href], script[src], img[src], iframe[src]"):
            url = urlsplit(urljoin("https://btwgame.com/" + str(path.relative_to(root)), node.get("href") or node["src"]))
            if url.netloc not in {"btwgame.com", "www.btwgame.com"} or url.scheme not in {"http", "https"}:
                continue
            target = root / unquote(url.path).lstrip("/")
            require(target.is_file() or (target / "index.html").is_file() or Path(str(target) + ".html").is_file(), f"内部断链: {path} -> {url.path}")
            links += 1
    for url in xml_urls:
        target = root / urlsplit(url).path.lstrip("/")
        require(target.is_file() or (target / "index.html").is_file() or Path(str(target) + ".html").is_file(), f"sitemap 地址缺文件: {url}")
    return games, added, {"baseline_count": baseline["count"], "added_count": len(added), "total_games": len(games), "sitemap_urls": len(xml_urls), "html_pages_checked": len(pages), "internal_links_checked": links, "skipped": batch["skipped"]}


def online_audit(base, games, added):
    base = base.rstrip("/")

    def get(path, mime):
        response = requests.get(base + path, timeout=30)
        require(response.status_code == 200, f"线上 HTTP {response.status_code}: {path}")
        require(mime in response.headers.get("Content-Type", ""), f"线上 MIME: {path}")
        return response

    catalog_response = get("/all_games.json", "application/json")
    remote = catalog_response.json()["games"]
    require(remote == games, "线上目录与本地发布目录不一致")
    xml = get("/sitemap.xml", "xml").content
    txt = get("/sitemap.txt", "text/plain").text
    require(sitemap_urls(xml) == txt.splitlines(), "线上 sitemap XML/TXT 不一致")
    require(sitemap_urls(xml) == sitemap_urls(Path("static_html/sitemap.xml").read_bytes()), "线上 sitemap 与本地不一致")

    def check_one(game):
        page = get(f"/games/{game['slug']}", "text/html")
        check_page(page.text, game)
        thumbnail = get(game["thumbnail_url"], "image/webp")
        check_image(thumbnail.content, game["slug"])
        require(hashlib.sha256(thumbnail.content).digest() == hashlib.sha256((Path("static_html") / game["thumbnail_url"].lstrip("/")).read_bytes()).digest(), f"线上缩略图内容不符: {game['slug']}")
        return {"slug": game["slug"], "page_status": page.status_code, "page_url": page.url, "image_status": thumbnail.status_code, "image_url": thumbnail.url}

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check_one, added))
    return {"base_url": base, "catalog_count": len(remote), "new_pages_checked": len(results), "new_images_checked": len(results), "sitemap_urls": len(sitemap_urls(xml)), "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--expected", type=int, default=200)
    parser.add_argument("--online", help="Deployed site URL; also verifies every new page and image")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    baseline = json.loads(Path(args.baseline).read_text())
    games, added, report = local_audit(baseline, args.expected)
    if args.online:
        report["online"] = online_audit(args.online, games, added)
    report["checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({key: value for key, value in report.items() if key != "online"}, ensure_ascii=False))
    if args.online:
        print(json.dumps({key: value for key, value in report["online"].items() if key != "results"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
