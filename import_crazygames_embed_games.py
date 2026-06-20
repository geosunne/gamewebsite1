#!/usr/bin/env python3
"""
Import embeddable CrazyGames titles into the static data source.

Only games with allowEmbed=true and a playable CrazyGames desktopUrl are added.
Existing slugs are preserved and not overwritten.
"""
import argparse
import json
import re
import time
from datetime import datetime
from html import unescape
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

CRAZYGAMES_BASE = "https://www.crazygames.com"
IMAGE_BASE = "https://imgs.crazygames.com"
OUTPUT_FILE = Path("crazygames_games.json")
DEFAULT_CATEGORY_PATHS = [
    "/t/mini",
    "/c/action",
    "/c/adventure",
    "/c/arcade",
    "/c/puzzle",
    "/c/sports",
    "/c/driving",
    "/c/casual",
]


def slugify(value):
    text = str(value or "").lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def html_to_text(value):
    soup = BeautifulSoup(value or "", "html.parser")
    return re.sub(r"\s+", " ", unescape(soup.get_text(" "))).strip()


def image_url(value, width=512):
    if not value:
        return ""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return f"{IMAGE_BASE}/{value}?format=auto&quality=80&metadata=none&width={width}"


def extract_next_data(html):
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        return None
    return json.loads(script.string)


def get_nested(data, path, default=None):
    current = data
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return current if current is not None else default


def collect_slugs_from_category(session, url):
    response = session.get(url, timeout=20)
    response.raise_for_status()
    data = extract_next_data(response.text)
    slugs = []
    if data:
        page_props = get_nested(data, ["props", "pageProps"], {})
        buckets = [
            get_nested(page_props, ["games", "items"], []),
            page_props.get("topGames", []),
            page_props.get("topMobileGames", []),
            page_props.get("linkBoostedGames", []),
            page_props.get("fillerGames", []),
        ]
        for bucket in buckets:
            for item in bucket or []:
                slug = item.get("slug") if isinstance(item, dict) else None
                if slug:
                    slugs.append(slug)

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        match = re.search(r"/game/([^/?#]+)", link["href"])
        if match:
            slugs.append(match.group(1))

    return list(dict.fromkeys(slugs))


def category_name(game):
    category = game.get("category") or {}
    raw = category.get("name") or "Casual"
    mapping = {
        ".io": "io Games",
        "Driving": "Racing",
        "Shooting": "Shooter",
        "Arcade": "Casual",
    }
    return mapping.get(raw, raw)


def parse_controls(game):
    text = html_to_text(game.get("controls") or "")
    if not text:
        return {}
    text = re.sub(r"^Controls\s*", "", text, flags=re.I).strip()
    if not text:
        return {}
    return {"Controls": text[:240]}


def build_game_record(game):
    title = game.get("name") or ""
    slug = slugify(game.get("slug") or title)
    description = html_to_text(game.get("metaDescription") or game.get("descriptionFirst") or "")
    long_description = html_to_text(" ".join([
        game.get("descriptionFirst") or "",
        game.get("descriptionRest") or "",
    ]))
    if not long_description:
        long_description = description

    desktop_url = game.get("desktopUrl") or ""
    thumbnail = ""
    covers = game.get("covers") or {}
    if isinstance(covers, dict):
        thumbnail = image_url(covers.get("16x9") or covers.get("1x1") or game.get("cover"))
    if not thumbnail:
        thumbnail = image_url(game.get("cover"))

    tags = []
    for tag in game.get("tags") or []:
        name = tag.get("name") if isinstance(tag, dict) else None
        if name:
            tags.append(name)
    tags = list(dict.fromkeys(tags))[:10]

    return {
        "source": "crazygames",
        "source_id": game.get("id"),
        "title": title,
        "slug": slug,
        "description": description or f"Play {title} online for free at BTW game.",
        "long_description": long_description or description,
        "thumbnail_url": thumbnail,
        "game_url": f"{CRAZYGAMES_BASE}/game/{slug}",
        "iframe_url": desktop_url,
        "category_name": category_name(game),
        "rating": round((game.get("rating") or 0) / 2, 1) if game.get("rating") else 0,
        "total_plays": int(game.get("upvotes") or 0),
        "is_featured": False,
        "is_new": True,
        "is_active": True,
        "tags": tags,
        "features": [
            "Free to play",
            "No download required",
            "Play in browser",
            "CrazyGames embeddable title",
        ],
        "controls": parse_controls(game),
        "release_date": game.get("addedOn") or datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


def fetch_game(session, slug):
    url = f"{CRAZYGAMES_BASE}/game/{slug}"
    response = session.get(url, timeout=20)
    response.raise_for_status()
    data = extract_next_data(response.text)
    if not data:
        return None, "missing_next_data"
    game = get_nested(data, ["props", "pageProps", "game"], {})
    if not game:
        return None, "missing_game_data"
    if not game.get("allowEmbed"):
        return None, "not_embeddable"
    if not game.get("desktopUrl"):
        return None, "missing_desktop_url"
    return build_game_record(game), "ok"


def load_existing_slugs():
    slugs = set()
    for path in [Path("static_html/all_games.json"), OUTPUT_FILE]:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        games = data.get("games", []) if isinstance(data, dict) else data
        for game in games:
            slug = game.get("slug")
            if slug:
                slugs.add(slug)
    return slugs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=40, help="Maximum new games to add")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between game detail requests")
    parser.add_argument("--category-url", action="append", default=[], help="CrazyGames category/tag URL to scan")
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; BTWGameBot/1.0; +https://btwgame.com)",
        "Accept-Language": "en-US,en;q=0.9",
    })

    category_urls = args.category_url or [urljoin(CRAZYGAMES_BASE, path) for path in DEFAULT_CATEGORY_PATHS]
    existing_slugs = load_existing_slugs()
    candidates = []
    for url in category_urls:
        print(f"Scanning {url}")
        try:
            candidates.extend(collect_slugs_from_category(session, url))
        except Exception as error:
            print(f"  failed: {error}")
    candidates = [slug for slug in dict.fromkeys(candidates) if slug not in existing_slugs]
    print(f"Candidate new slugs: {len(candidates)}")

    imported = []
    skipped = {}
    for slug in candidates:
        if len(imported) >= args.limit:
            break
        try:
            record, status = fetch_game(session, slug)
        except Exception as error:
            record, status = None, f"error:{error}"
        if record:
            imported.append(record)
            existing_slugs.add(record["slug"])
            print(f"  added: {record['title']} ({record['slug']})")
        else:
            skipped[status] = skipped.get(status, 0) + 1
            print(f"  skipped {slug}: {status}")
        time.sleep(args.delay)

    if OUTPUT_FILE.exists():
        existing_data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        existing_games = existing_data.get("games", []) if isinstance(existing_data, dict) else existing_data
    else:
        existing_games = []

    by_slug = {game["slug"]: game for game in existing_games}
    for game in imported:
        by_slug.setdefault(game["slug"], game)

    output = {
        "metadata": {
            "source": "crazygames",
            "generated_at": datetime.utcnow().isoformat(),
            "total_games": len(by_slug),
            "note": "Only allowEmbed=true CrazyGames titles are included.",
        },
        "games": list(by_slug.values()),
    }
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nImport complete")
    print(f"Added this run: {len(imported)}")
    print(f"Stored CrazyGames games: {len(by_slug)}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
