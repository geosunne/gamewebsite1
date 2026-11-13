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
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from catalog_quality import has_blocked_embed

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


def collect_slugs_from_category(session, url, discovered_urls=None):
    response = session.get(url, timeout=20)
    response.raise_for_status()
    data = extract_next_data(response.text)
    if discovered_urls is not None:
        discovered_urls.extend(category_urls_from_html(response.text))
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


def category_urls_from_html(html):
    """Follow published links/related tags, without inventing provider endpoints."""
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for link in soup.find_all("a", href=True):
        url = urljoin(CRAZYGAMES_BASE, link["href"])
        parsed = urlsplit(url)
        if parsed.hostname == "www.crazygames.com" and re.fullmatch(r"/(?:c|t)/[a-z0-9-]+/?", parsed.path):
            urls.append(url)
    data = extract_next_data(html)
    related = get_nested(data, ["props", "pageProps", "tag", "relatedTags"], []) if data else []
    for tag in related:
        slug = tag.get("slug")
        if isinstance(slug, str) and re.fullmatch(r"[a-z0-9-]+", slug):
            kind = "c" if tag.get("isCategory") is True else "t"
            urls.append(f"{CRAZYGAMES_BASE}/{kind}/{slug}")
    return list(dict.fromkeys(urls))


def discover_category_urls(session):
    response = session.get(CRAZYGAMES_BASE, timeout=20)
    response.raise_for_status()
    return category_urls_from_html(response.text)


def build_source_guide(game):
    soup = BeautifulSoup(" ".join([
        game.get("descriptionFirst") or "", game.get("descriptionRest") or "",
    ]), "html.parser")

    def section_text(pattern):
        for heading in soup.find_all(re.compile(r"^h[1-6]$")):
            if not re.search(pattern, heading.get_text(" ", strip=True), re.I):
                continue
            parts = []
            for sibling in heading.find_next_siblings():
                if re.fullmatch(r"h[1-6]", sibling.name or ""):
                    break
                if sibling.name in {"p", "ul", "ol"}:
                    parts.append(sibling.get_text(" ", strip=True))
            if parts:
                return html_to_text(" ".join(parts))
        return ""

    first_paragraph = soup.find("p")
    summary = html_to_text(game.get("metaDescription") or (str(first_paragraph) if first_paragraph else game.get("descriptionFirst")) or "")
    controls = html_to_text(game.get("controls") or "")
    how_to = section_text(r"^how to play\b") or controls
    if not how_to:
        how_to = "Open the player and follow the game's tutorial or on-screen instructions."
    source_tips = section_text(r"\b(?:tips|strategy|strategies)\b")
    tips = [source_tips] if source_tips else [
        "Read the controls above before starting; keyboard, mouse, and touch inputs can differ.",
        "Check the in-game objective and tutorial before choosing a mode or spending resources.",
    ]
    return {
        "summary": summary,
        "how_to": how_to,
        "tips": tips,
        "source_url": f"{CRAZYGAMES_BASE}/game/{slugify(game.get('slug') or game.get('name'))}",
        "reviewed_on": datetime.now(timezone.utc).date().isoformat(),
        "provenance": "Source description and controls; fallback tips are general browser guidance.",
    }


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
        "content_guide": build_source_guide(game),
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
    if has_blocked_embed(record):
        return False, "blocked_provider"
    try:
        response = session.get(record["iframe_url"], timeout=15, headers={"Referer": "https://btwgame.com/"})
        response.raise_for_status()
    except requests.RequestException:
        return False, "embed_unavailable"
    if response.status_code != 200:
        return False, "embed_unavailable"
    if response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "text/html":
        return False, "embed_not_html"
    history = response.history if isinstance(response.history, list) else []
    chain = [*history, response]
    for hop in chain:
        if urlsplit(hop.url).scheme != "https":
            return False, "embed_insecure_redirect"
        host = urlsplit(hop.url).hostname or ""
        if host in {"www.crazygames.com", "crazygames.com"}:
            return False, "embed_redirected_to_listing"
        if has_blocked_embed({"iframe_url": hop.url}):
            return False, "blocked_provider"
        if hop.headers.get("X-Frame-Options", ""):
            return False, "embed_frame_restricted"
        csp = hop.headers.get("Content-Security-Policy", "")
        for policy in csp.split(","):
            for directive in policy.split(";"):
                values = directive.strip().split()
                if values and values[0].lower() == "frame-ancestors":
                    if "'none'" in values[1:] or not any(origin in {"*", "https:", "https://btwgame.com", "https://btwgame.com/"} for origin in values[1:]):
                        return False, "embed_frame_restricted"
    record["embed_checked_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record["embed_validation"] = {
        "checked_at": record["embed_checked_at"],
        "request_origin": "https://btwgame.com",
        "responses": [{
            "url": hop.url, "status": hop.status_code,
            "content_type": hop.headers.get("Content-Type", ""),
            "location": hop.headers.get("Location", ""),
            "x_frame_options": hop.headers.get("X-Frame-Options", ""),
            "content_security_policy": hop.headers.get("Content-Security-Policy", ""),
        } for hop in chain],
    }
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


def check_candidate(slug, headers, known_keys):
    """Use an independent session for each bounded concurrent request."""
    try:
        with requests.Session() as session:
            session.headers.update(headers)
            record, status = fetch_game(session, slug)
            if record and identity_keys(record) & known_keys:
                return None, "duplicate_identity"
            if record:
                if not record.get("controls"):
                    return None, "missing_source_controls"
                valid, status = validate_embed(session, record)
                if not valid:
                    record = None
            return record, status
    except Exception as error:
        return None, f"error:{error}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=40, help="Maximum new games to add")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between candidate check batches")
    parser.add_argument("--workers", type=int, default=4, choices=range(1, 5), help="Bounded concurrent candidate checks (1-4)")
    parser.add_argument("--category-url", action="append", default=[], help="CrazyGames category/tag URL to scan")
    parser.add_argument("--discover-categories", action="store_true", help="Also scan category and tag links published on the CrazyGames homepage")
    parser.add_argument("--resume", action="store_true", help="Continue the latest import batch toward --limit, retaining its added games")
    args = parser.parse_args()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; BTWGameBot/1.0; +https://btwgame.com)",
        "Accept-Language": "en-US,en;q=0.9",
    })

    category_urls = args.category_url or [urljoin(CRAZYGAMES_BASE, path) for path in DEFAULT_CATEGORY_PATHS]
    if args.discover_categories:
        category_urls = list(dict.fromkeys(category_urls + discover_category_urls(session)))
    existing_slugs = load_existing_slugs()
    known_keys = set().union(*(identity_keys(game) for game in load_existing_games()))
    candidates = []
    discovered_urls = []
    scanned_urls = set()
    scan_errors = []
    for url in category_urls:
        print(f"Scanning {url}")
        try:
            candidates.extend(collect_slugs_from_category(session, url, discovered_urls))
            scanned_urls.add(url)
        except Exception as error:
            scan_errors.append({"url": url, "error": str(error)})
            print(f"  failed: {error}")
    candidates = [slug for slug in dict.fromkeys(candidates) if slug not in existing_slugs]
    print(f"Candidate new slugs: {len(candidates)}")

    previous_batch = {}
    previous_games = []
    if args.resume and OUTPUT_FILE.exists():
        previous_data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
        previous_batch = previous_data.get("metadata", {}).get("latest_import", {})
        previous_slugs = set(previous_batch.get("added_slugs", []))
        previous_games = [game for game in previous_data.get("games", []) if game["slug"] in previous_slugs]
        if len(previous_games) >= args.limit:
            parser.error("The previous batch is already complete; start a fresh batch without --resume")
    imported = previous_games.copy()
    skipped = previous_batch.get("skipped", {}).copy()
    checked = previous_batch.get("checked", 0)
    checked_slugs = set(previous_batch.get("checked_slugs", []))
    # Older batches did not retain rejected slugs; imported slugs are already excluded.
    candidate_set = set(candidates)
    index = 0
    while len(imported) < args.limit:
        if index >= len(candidates):
            if not args.discover_categories:
                break
            next_urls = [url for url in dict.fromkeys(discovered_urls) if url not in scanned_urls]
            if not next_urls:
                break
            # Expand one published category at a time, stopping once the target is met.
            url = next_urls[0]
            scanned_urls.add(url)
            print(f"Expanding {url}")
            try:
                for slug in collect_slugs_from_category(session, url, discovered_urls):
                    if slug not in existing_slugs and slug not in candidate_set:
                        candidates.append(slug)
                        candidate_set.add(slug)
            except Exception as error:
                scan_errors.append({"url": url, "error": str(error)})
                print(f"  failed: {error}")
            continue
        batch = []
        while index < len(candidates) and len(batch) < min(args.workers, args.limit - len(imported)):
            slug = candidates[index]
            index += 1
            if slug not in checked_slugs:
                batch.append(slug)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(check_candidate, slug, dict(session.headers), known_keys.copy()) for slug in batch]
            for slug, future in zip(batch, futures):
                record, status = future.result()
                if record and identity_keys(record) & known_keys:
                    record, status = None, "duplicate_identity"
                checked += 1
                checked_slugs.add(slug)
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
                "started_at": previous_batch.get("started_at") or started_at,
                "requested_limit": args.limit,
                "candidates": len(set(candidates) | checked_slugs),
                "resumed_from_count": len(previous_games),
                "checked": checked,
                "checked_slugs": sorted(checked_slugs),
                "scanned_urls": sorted(scanned_urls),
                "scan_errors": scan_errors,
                "added_count": len(imported),
                "added_slugs": [game["slug"] for game in imported],
                "skipped": skipped,
            },
        },
        "games": list(by_slug.values()),
    }
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nImport complete")
    print(f"Added this run: {len(imported) - len(previous_games)}")
    print(f"Added to batch: {len(imported)}")
    print(f"Stored CrazyGames games: {len(by_slug)}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
