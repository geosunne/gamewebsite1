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
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlsplit

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
    return {"Controls": text}


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
        "rating": 0,
        "total_plays": 0,
        "source_rating": round((game.get("rating") or 0) / 2, 1) if game.get("rating") else 0,
        "source_rating_scale": 5,
        "source_upvotes": int(game.get("upvotes") or 0),
        "source_metrics_version": 1,
        "developer": html_to_text(game.get("developer") or ""),
        "supported_devices": ["Desktop"] + (["Android"] if game.get("androidFriendly") is True else []) + (["iOS"] if game.get("iosFriendly") is True else []),
        "source_published_at": game.get("addedOn") or "",
        "source_updated_at": game.get("lastSignificantUpdatedOn") or game.get("lastFileUpdatedOn") or "",
        "source_checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "allow_embed": game.get("allowEmbed") is True,
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
        "release_date": game.get("addedOn") or "",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
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
    if game.get("allowEmbed") is not True:
        return None, "not_embeddable"
    if not game.get("desktopUrl"):
        return None, "missing_desktop_url"
    return build_game_record(game), "ok"


def identity_keys(game):
    keys = set()
    if game.get("slug"):
        keys.add("slug:" + slugify(game["slug"]))
    if game.get("title"):
        title_key = slugify(game["title"])
        if game["title"].lower().endswith(".io"):
            title_key = title_key.removesuffix("-io")
        keys.add("title:" + title_key)
    if game.get("source") == "crazygames" and game.get("source_id"):
        keys.add("crazygames:" + str(game["source_id"]))
    if game.get("iframe_url"):
        url = urlsplit(game["iframe_url"])
        keys.add("embed:" + url.netloc.lower() + url.path.rstrip("/"))
    return keys


def load_existing_games():
    games = []
    for path in (Path("static_html/all_games.json"), OUTPUT_FILE):
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            games.extend(data.get("games", []) if isinstance(data, dict) else data)
    return games


def validate_embed(session, record):
    try:
        response = session.get(record["iframe_url"], timeout=15, headers={"Referer": "https://btwgame.com/"})
        response.raise_for_status()
    except requests.RequestException:
        return False, "embed_unavailable"
    if "text/html" not in response.headers.get("Content-Type", "").lower():
        return False, "embed_not_html"
    frame_policy = response.headers.get("X-Frame-Options", "").lower()
    if frame_policy:
        return False, "embed_frame_restricted"
    csp = response.headers.get("Content-Security-Policy", "")
    for policy in csp.split(","):
        for directive in policy.split(";"):
            values = directive.strip().split()
            if values and values[0].lower() == "frame-ancestors":
                if not any(origin in {"*", "https:", "https://btwgame.com", "https://btwgame.com/"} for origin in values[1:]):
                    return False, "embed_frame_restricted"
    if urlsplit(response.url).hostname in {"www.crazygames.com", "crazygames.com"}:
        return False, "embed_redirected_to_listing"
    record["embed_checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return True, "ok"


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
    known_keys = set().union(*(identity_keys(game) for game in load_existing_games()))
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
    checked = 0
    for slug in candidates:
        if len(imported) >= args.limit:
            break
        try:
            record, status = fetch_game(session, slug)
            if record and identity_keys(record) & known_keys:
                record, status = None, "duplicate_identity"
            if record:
                valid, status = validate_embed(session, record)
                if not valid:
                    record = None
        except Exception as error:
            record, status = None, f"error:{error}"
        checked += 1
        if record:
            imported.append(record)
            existing_slugs.add(record["slug"])
            known_keys.update(identity_keys(record))
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
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "total_games": len(by_slug),
            "note": "Only allowEmbed=true CrazyGames titles are included.",
            "latest_import": {
                "requested_limit": args.limit,
                "candidates": len(candidates),
                "checked": checked,
                "added_count": len(imported),
                "added_slugs": [game["slug"] for game in imported],
                "skipped": skipped,
            },
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
