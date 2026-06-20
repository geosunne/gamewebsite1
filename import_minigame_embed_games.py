#!/usr/bin/env python3
"""
Import embeddable Minigame titles into the static data source.

Only games with a real *.library.minigame.com/minigame-index.html app URL are
included. The Minigame play page contains recommendation data too, so records
are extracted by matching the current app_id before reading base.app_url.
"""
import argparse
import json
import re
import time
from datetime import datetime
from html import unescape
from pathlib import Path

import requests
from bs4 import BeautifulSoup

MINIGAME_BASE = "https://minigame.com"
SITEMAP_URL = f"{MINIGAME_BASE}/api/sitemap/games/sitemap.xml"
OUTPUT_FILE = Path("minigame_games.json")

CATEGORY_MAP = {
    "action": "Action",
    "adventure": "Adventure",
    "arcade": "Casual",
    "battle": "Action",
    "board": "Puzzle",
    "car": "Racing",
    "casual": "Casual",
    "clicker": "Clicker",
    "cooking": "Cooking",
    "dress-up": "Casual",
    "driving": "Racing",
    "idle": "Clicker",
    "io": "io Games",
    "kids": "Casual",
    "mahjong": "Puzzle",
    "mini": "Casual",
    "multiplayer": "io Games",
    "parkour": "Parkour",
    "puzzle": "Puzzle",
    "racing": "Racing",
    "shooter": "Shooter",
    "simulation": "Simulation",
    "sports": "Sports",
    "strategy": "Strategy",
}


def slugify(value):
    text = str(value or "").lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def clean_text(value):
    text = unescape(str(value or ""))
    replacements = {
        "Â": "",
        "â": "'",
        "â": "'",
        "â": '"',
        "â": '"',
        "â": "-",
        "â": "-",
        "â¦": "...",
        "\u00a0": " ",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return re.sub(r"\s+", " ", text).strip()


def html_to_text(value):
    soup = BeautifulSoup(value or "", "html.parser")
    return clean_text(soup.get_text(" "))


def get_meta(soup, name=None, prop=None):
    attrs = {"name": name} if name else {"property": prop}
    tag = soup.find("meta", attrs=attrs)
    return clean_text(tag.get("content")) if tag and tag.get("content") else ""


def extract_sitemap_slugs(session):
    response = session.get(SITEMAP_URL, timeout=30)
    response.raise_for_status()
    slugs = []
    for loc in re.findall(r"<loc>(.*?)</loc>", response.text):
        match = re.match(r"https://minigame\.com/en/game/([^/]+)/info$", loc)
        if match:
            slugs.append(match.group(1))
    return list(dict.fromkeys(slugs))


def extract_current_game_chunk(html, slug):
    marker = f'\\"app_id\\":\\"{slug}\\"'
    index = html.find(marker)
    if index < 0:
        index = html.find(f"app_id\\\\\":\\\\\"{slug}\\\\\"")
    if index < 0:
        index = html.find(slug)
    return html[index:index + 20000] if index >= 0 else ""


def extract_app_url(play_html, slug):
    chunk = extract_current_game_chunk(play_html, slug)
    match = re.search(
        r'app_url\\?":\\?"(https://[^"\\]+\.library\.minigame\.com/minigame-index\.html)',
        chunk,
    )
    if not match:
        return ""
    return match.group(1).replace("\\/", "/")


def extract_json_string(chunk, key):
    match = re.search(rf'{re.escape(key)}\\?":\\?"([^"\\]*)', chunk)
    if not match:
        return ""
    value = match.group(1).replace("\\/", "/").replace("\\n", " ")
    return clean_text(value)


def extract_string_array(chunk, key):
    match = re.search(rf'{re.escape(key)}\\?":\[(.*?)\]', chunk)
    if not match:
        return []
    return [clean_text(item) for item in re.findall(r'\\"([^"\\]+)\\"', match.group(1)) if clean_text(item)]


def normalize_category(types, title, description):
    for raw_type in types:
        key = slugify(raw_type)
        if key in CATEGORY_MAP:
            return CATEGORY_MAP[key]
    text = f"{title} {description}".lower()
    keyword_map = [
        ("shooter", "Shooter"),
        ("shoot", "Shooter"),
        ("racing", "Racing"),
        ("car", "Racing"),
        ("truck", "Racing"),
        ("puzzle", "Puzzle"),
        ("mahjong", "Puzzle"),
        ("parkour", "Parkour"),
        ("sports", "Sports"),
        ("football", "Sports"),
        ("basketball", "Sports"),
        ("cooking", "Cooking"),
        ("idle", "Clicker"),
        ("clicker", "Clicker"),
        ("strategy", "Strategy"),
        ("simulator", "Simulation"),
    ]
    for needle, category in keyword_map:
        if needle in text:
            return category
    return "Casual"


def parse_info_page(info_html):
    soup = BeautifulSoup(info_html, "html.parser")
    h1 = soup.find("h1")
    title = clean_text(h1.get_text(" ", strip=True)) if h1 else ""
    description = get_meta(soup, name="description")
    page_title = clean_text(soup.title.get_text(" ", strip=True)) if soup.title else ""
    image = get_meta(soup, prop="og:image") or get_meta(soup, name="twitter:image")
    return title, description, page_title, image


def extract_content_sections(chunk):
    sections = []
    for match in re.finditer(
        r'\\"key\\":\\"(title|content)\\",\\"value\\":\\"(.*?)\\",\\"type\\":\\"play\\"',
        chunk,
        flags=re.S,
    ):
        sections.append((match.group(1), clean_text(match.group(2).replace("\\n", " "))))

    content = {}
    current_title = ""
    for key, value in sections:
        if key == "title":
            current_title = value
        elif key == "content" and current_title:
            content[current_title] = value
            current_title = ""
    return content


def validate_iframe_url(session, iframe_url):
    if not iframe_url:
        return False, "missing_app_url"
    try:
        response = session.get(iframe_url, timeout=15, allow_redirects=True)
    except Exception as error:
        return False, f"iframe_error:{error}"
    if response.status_code != 200:
        return False, f"iframe_status:{response.status_code}"
    if response.headers.get("x-frame-options"):
        return False, "iframe_x_frame_options"
    csp = response.headers.get("content-security-policy") or ""
    if "frame-ancestors" in csp.lower():
        return False, "iframe_csp_frame_ancestors"
    return True, "ok"


def build_game_record(slug, play_html, info_html, app_url):
    chunk = extract_current_game_chunk(play_html, slug)
    title, meta_description, page_title, image = parse_info_page(info_html)
    display_name = extract_json_string(chunk, "display_name")
    title = title or display_name or slug.replace("-", " ").title()

    description = (
        meta_description
        or extract_json_string(chunk, "meta_description")
        or extract_json_string(chunk, "content")
        or f"Play {title} online for free at BTW game."
    )
    description = clean_text(description)

    sections = extract_content_sections(chunk)
    long_description = " ".join(value for value in sections.values() if value)
    if not long_description:
        long_description = description

    types = extract_string_array(chunk, "types")
    tags = extract_string_array(chunk, "contentArray")
    tags = list(dict.fromkeys([tag for tag in tags + types if tag]))[:10]

    thumbnail = (
        extract_json_string(chunk, "banner")
        or image
        or extract_json_string(chunk, "big_icon")
        or extract_json_string(chunk, "icon")
    )
    controls_text = ""
    for heading, value in sections.items():
        if "control" in heading.lower():
            controls_text = value
            break

    rating_raw = extract_json_string(chunk, "rating")
    try:
        rating = float(rating_raw) if rating_raw else 0
    except ValueError:
        rating = 0

    hot_raw = extract_json_string(chunk, "hot_degree")
    try:
        total_plays = int(float(hot_raw)) if hot_raw else 0
    except ValueError:
        total_plays = 0

    release_date = extract_json_string(chunk, "publish_v2_local") or extract_json_string(chunk, "created_at")
    category_name = normalize_category(types, title, description)

    return {
        "source": "minigame",
        "source_id": extract_json_string(chunk, "id") or slug,
        "title": title,
        "slug": slugify(slug),
        "description": description,
        "long_description": long_description,
        "thumbnail_url": thumbnail,
        "game_url": f"{MINIGAME_BASE}/en/game/{slug}/info",
        "iframe_url": app_url,
        "category_name": category_name,
        "rating": rating,
        "total_plays": total_plays,
        "is_featured": False,
        "is_new": True,
        "is_active": True,
        "tags": tags,
        "features": [
            "Free to play",
            "No download required",
            "Play in browser",
            "Minigame embeddable title",
        ],
        "controls": {"Controls": controls_text} if controls_text else {},
        "release_date": release_date or datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "source_page_title": page_title,
    }


def load_games_from_file(path):
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("games", []) if isinstance(data, dict) else data


def load_existing_slugs():
    slugs = set()
    for path in [Path("static_html/all_games.json"), OUTPUT_FILE]:
        for game in load_games_from_file(path):
            slug = game.get("slug")
            if slug:
                slugs.add(slug)
    return slugs


def save_output(games, skipped):
    output = {
        "metadata": {
            "source": "minigame",
            "generated_at": datetime.utcnow().isoformat(),
            "total_games": len(games),
            "note": "Only Minigame titles with real iframeable library app URLs are included.",
            "skipped": skipped,
        },
        "games": games,
    }
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_game(session, slug, validate=True):
    play_url = f"{MINIGAME_BASE}/en/game/{slug}/play/pc"
    info_url = f"{MINIGAME_BASE}/en/game/{slug}/info"

    play_response = session.get(play_url, timeout=25)
    play_response.raise_for_status()
    app_url = extract_app_url(play_response.text, slug)
    if validate:
        ok, status = validate_iframe_url(session, app_url)
        if not ok:
            return None, status

    info_response = session.get(info_url, timeout=25)
    info_response.raise_for_status()
    return build_game_record(slug, play_response.text, info_response.text, app_url), "ok"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Maximum new games to add; 0 means all")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between game requests")
    parser.add_argument("--save-every", type=int, default=25, help="Persist output every N imported games")
    parser.add_argument("--no-validate", action="store_true", help="Skip iframe response validation")
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; BTWGameBot/1.0; +https://btwgame.com)",
        "Accept-Language": "en-US,en;q=0.9",
    })

    existing_output = load_games_from_file(OUTPUT_FILE)
    by_slug = {game["slug"]: game for game in existing_output if game.get("slug")}
    existing_slugs = load_existing_slugs()

    sitemap_slugs = extract_sitemap_slugs(session)
    candidates = [slug for slug in sitemap_slugs if slugify(slug) not in existing_slugs]
    if args.limit:
        candidates = candidates[:args.limit]

    print(f"Minigame English slugs: {len(sitemap_slugs)}")
    print(f"Existing Minigame stored: {len(by_slug)}")
    print(f"Candidate new slugs: {len(candidates)}")

    imported = []
    skipped = {}
    for index, slug in enumerate(candidates, start=1):
        try:
            record, status = fetch_game(session, slug, validate=not args.no_validate)
        except Exception as error:
            record, status = None, f"error:{error}"

        if record:
            by_slug.setdefault(record["slug"], record)
            existing_slugs.add(record["slug"])
            imported.append(record)
            print(f"[{index}/{len(candidates)}] added: {record['title']} ({record['slug']})")
        else:
            skipped[status] = skipped.get(status, 0) + 1
            print(f"[{index}/{len(candidates)}] skipped {slug}: {status}")

        if args.save_every and len(imported) and len(imported) % args.save_every == 0:
            save_output(list(by_slug.values()), skipped)
            print(f"  saved checkpoint: {len(by_slug)} games")

        time.sleep(args.delay)

    save_output(list(by_slug.values()), skipped)

    print("\nImport complete")
    print(f"Added this run: {len(imported)}")
    print(f"Stored Minigame games: {len(by_slug)}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
