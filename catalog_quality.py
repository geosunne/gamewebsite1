"""Shared provenance rules for imported catalog records."""
import re
from urllib.parse import urlparse


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
