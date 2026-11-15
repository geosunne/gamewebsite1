"""Stable, content-based page dates shared by HTML and both sitemap entry points."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup


def page_path(file, root):
    relative = file.relative_to(root).as_posix()
    return "/" if relative == "index.html" else "/" + relative.removesuffix(".html")


def content_hash(raw, html=True):
    if not html:
        return hashlib.sha256(raw.strip().encode()).hexdigest()
    soup = BeautifulSoup(raw, "html.parser")
    # Verification timestamps and the date we are calculating are not content edits.
    for node in soup.select("[data-check-timestamp], [data-page-updated]"):
        node.string = ""
        node.attrs = {key: value for key, value in node.attrs.items() if key not in {"datetime", "content"}}
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or "{}")
            entities = data if isinstance(data, list) else [data]
            for entity in entities:
                if isinstance(entity, dict) and entity.get("@type") in {"WebPage", "CollectionPage"}:
                    entity.pop("dateModified", None)
            script.string = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        except json.JSONDecodeError:
            pass
    # HTML parser formatting and inter-element indentation do not change the page.
    normalized = re.sub(r">\s+<", "><", str(soup))
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return hashlib.sha256(normalized.encode()).hexdigest()


def seed_content_dates(root="static_html"):
    """Capture existing public pages before a build changes them."""
    root = Path(root)
    manifest = root / "content_dates.json"
    if manifest.exists():
        return json.loads(manifest.read_text())["pages"]
    old_dates = {}
    try:
        for item in ET.parse(root / "sitemap.xml").getroot().findall("{*}url"):
            location, modified = item.find("{*}loc"), item.find("{*}lastmod")
            if location is not None and location.text and modified is not None:
                old_dates[location.text.removeprefix("https://btwgame.com")] = modified.text
    except (FileNotFoundError, ET.ParseError):
        pass
    pages = {}
    for file in [*root.rglob("*.html"), root / "llms.txt"]:
        if not file.is_file() or file.name == "404.html":
            continue
        path = page_path(file, root)
        pages[path] = {"sha256": content_hash(file.read_text(), file.suffix == ".html")}
        if old_dates.get(path):
            pages[path]["lastmod"] = old_dates[path]
    save_manifest(manifest, pages)
    return pages


def save_manifest(path, pages):
    path.write_text(json.dumps({"schema_version": 1, "pages": pages}, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def update_content_dates(root="static_html", now=None):
    root = Path(root)
    previous = seed_content_dates(root)
    today = (now or datetime.now(timezone.utc)).date().isoformat()
    pages = {}
    for file in [*root.rglob("*.html"), root / "llms.txt"]:
        if not file.is_file() or file.name == "404.html":
            continue
        path = page_path(file, root)
        raw = file.read_text()
        digest = content_hash(raw, file.suffix == ".html")
        old = previous.get(path, {})
        modified = old.get("lastmod", today) if old.get("sha256") == digest else today
        pages[path] = {"sha256": digest, "lastmod": modified}
        if file.suffix != ".html":
            continue
        soup = BeautifulSoup(raw, "html.parser")
        changed = False
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or "{}")
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and data.get("@type") in {"WebPage", "CollectionPage"} and data.get("dateModified") != modified:
                data["dateModified"] = modified
                script.string = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
                changed = True
        for node in soup.select("[data-page-updated]"):
            if node.get_text() != modified or node.get("datetime") != modified:
                node.string = modified
                node["datetime"] = modified
                changed = True
        if changed:
            file.write_text(str(soup))
    save_manifest(root / "content_dates.json", pages)
    if root.resolve() == (Path.cwd() / "static_html").resolve():
        for name in ("index.html", "games.html"):
            source = Path("static") / name
            published = root / name
            if source.is_file() and published.is_file():
                source.write_text(published.read_text())
    for name in ("all_games.json", "new_games.json"):
        file = root / name
        if not file.exists():
            continue
        data = json.loads(file.read_text())
        changed = False
        for game in data.get("games", []):
            modified = pages.get("/games/" + game["slug"], {}).get("lastmod")
            if modified and game.get("content_modified_at") != modified:
                game["content_modified_at"] = modified
                changed = True
        if changed:
            file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return {path: item["lastmod"] for path, item in pages.items()}
