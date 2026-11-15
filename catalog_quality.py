"""Shared provenance rules for imported catalog records."""
import re
import subprocess
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse


def catalog_datetime(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def is_recent_game(game, now=None):
    """NEW means first added to this catalog within the last fourteen days."""
    added = catalog_datetime(game.get("catalog_added_at"))
    now = now or datetime.now(timezone.utc)
    return bool(added and now - timedelta(days=14) < added <= now)


@lru_cache(maxsize=1)
def first_catalog_entries():
    """Recover legacy first-publication evidence once, without source release dates."""
    result = {}
    try:
        history = subprocess.check_output([
            "git", "log", "--reverse", "--diff-filter=A", "--format=COMMIT:%cI:%H",
            "--name-only", "--", "static_html/games",
        ], cwd=Path(__file__).resolve().parent, text=True)
    except (OSError, subprocess.CalledProcessError):
        return result
    stamp, commit = "", ""
    for line in history.splitlines():
        if line.startswith("COMMIT:"):
            stamp, commit = line.removeprefix("COMMIT:").rsplit(":", 1)
        elif line.startswith("static_html/games/") and line.endswith(".html") and stamp:
            result.setdefault(Path(line).stem, (stamp, commit))
    return result


def apply_catalog_provenance(game, now=None):
    game = game.copy()
    now = now or datetime.now(timezone.utc)
    if not catalog_datetime(game.get("catalog_added_at")):
        entry = first_catalog_entries().get(game.get("slug"))
        if not entry and game.get("slug"):
            try:
                history = subprocess.check_output([
                    "git", "log", "--follow", "--diff-filter=A", "--format=%cI|%H", "--",
                    f"static_html/games/{game['slug']}.html",
                ], cwd=Path(__file__).resolve().parent, text=True).splitlines()
                if history:
                    stamp, commit = history[-1].split("|", 1)
                    entry = (stamp, commit)
                    first_catalog_entries()[game['slug']] = entry
            except (OSError, subprocess.CalledProcessError):
                pass
        if entry:
            game["catalog_added_at"], game["catalog_added_commit"] = entry
            game["catalog_added_evidence"] = "first_committed_game_page"
        else:
            game["catalog_added_at"] = now.isoformat(timespec="seconds")
            game["catalog_added_evidence"] = "first_observed_catalog_build"
    game["is_new"] = is_recent_game(game, now)
    game.pop("isNew", None)
    game["controls_status"] = "recorded" if game.get("controls") else "not_confirmed"
    game["device_status"] = "recorded" if game.get("supported_devices") else "not_confirmed"
    return game


def merge_catalog_record(old, extra):
    """Merge source inputs without rolling back newer, independent evidence."""
    def source_stamp(record):
        stamps = [catalog_datetime(record.get(key)) for key in ('source_checked_at', 'source_check_attempted_at')]
        return max((stamp for stamp in stamps if stamp), default=None)

    merged = {**old, **extra}
    old_stamp, extra_stamp = source_stamp(old), source_stamp(extra)
    prefer_old = bool(old_stamp and (not extra_stamp or old_stamp > extra_stamp))
    if prefer_old:
        fields = {'title', 'description', 'long_description', 'tags', 'controls', 'supported_devices',
                  'developer', 'content_guide', 'content_status', 'content_parse_version', 'account_required',
                  'game_url', 'iframe_url'}
        fields.update(key for key in old if key.startswith('source_'))
        merged.update({key: old[key] for key in fields if key in old})
    selected_source = old if prefer_old else extra
    selected_stamp = old_stamp if prefer_old else extra_stamp
    if selected_stamp and selected_source.get('source_check_status') == 'confirmed' and selected_source.get('controls'):
        if merged.get('content_status') == 'needs_review' and selected_source.get('content_status') != 'needs_review':
            merged.pop('content_status')
        merged.pop('source_check_reason', None)
    for prefix, key in (('player_', 'player_checked_at'), ('editorial_', 'editorial_reviewed_at'), ('embed_', 'embed_checked_at')):
        left, right = catalog_datetime(old.get(key)), catalog_datetime(extra.get(key))
        selected = old if left and (not right or left > right) else extra if right else None
        if selected:
            for name in list(merged):
                if name.startswith(prefix):
                    merged.pop(name)
            merged.update({name: value for name, value in selected.items() if name.startswith(prefix)})
    for key in ('catalog_added_at', 'catalog_added_commit', 'catalog_added_evidence', 'content_modified_at'):
        if old.get(key):
            merged[key] = old[key]
    if old.get('source_metrics_version') == 1:
        merged['total_plays'] = old.get('total_plays') or 0
        merged['rating'] = old.get('rating') or 0
    if (old.get('thumbnail_url') or '').startswith('/assets/'):
        merged.update({key: old[key] for key in ('thumbnail', 'thumbnail_url', 'original_thumbnail_url') if key in old})
    return merged


def has_blocked_embed(game):
    # Playhop app pages reject third-party framing, including BTW game.
    host = urlparse(game.get("iframe_url") or game.get("game_url") or "").hostname or ""
    return host == "playhop.com" or host.endswith(".playhop.com")


def clean_source_text(value):
    text = str(value or "")
    text = re.sub(r"\\u([0-9a-fA-F]{4})", lambda match: chr(int(match[1], 16)), text)
    text = text.replace('\\"', '"').replace("\\n", " ").replace("\\r", " ")
    text = re.sub(r"\\\s+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def record_source(game):
    source = game.get("source")
    if source:
        return source
    host = urlparse(game.get("game_url") or "").hostname or ""
    if host in {"crazygames.com", "www.crazygames.com"}:
        return "crazygames"
    if host in {"minigame.com", "www.minigame.com"}:
        return "minigame"
    return ""


def normalize_source_metrics(game):
    game = game.copy()
    source = record_source(game)
    if source not in {"crazygames", "minigame"}:
        return game
    game["source"] = source
    if game.get("source_metrics_version") != 1:
        game.setdefault("source_rating", game.get("rating") or 0)
        game.setdefault("source_rating_scale", 5)
        metric = "source_upvotes" if source == "crazygames" else "source_popularity"
        game.setdefault(metric, game.get("total_plays") or 0)
        # The legacy importer stored external votes/heat as local play counts.
        game["total_plays"] = 0
        game["rating"] = 0
        game["source_metrics_version"] = 1
    return game


def source_rating(game):
    return game.get("source_rating") or game.get("rating") or 0


def catalog_popularity(game):
    return game.get("total_plays") or game.get("source_upvotes") or game.get("source_popularity") or 0


def legacy_category_redirects(active_slugs):
    replacements = {
        "clicker": "idle-and-clicker",
        "arcade": "casual",
        "parking": "driving",
        "multiplayer": "io-games",
        "adventure": None,
    }
    return {
        f"/categories/{slug}": f"/categories/{target}" if target in active_slugs else "/games"
        for slug, target in replacements.items()
        if slug not in active_slugs
    }
