import json
import unittest
from pathlib import Path
from unittest.mock import Mock
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from PIL import Image

from generate_static_pages import game_guide, generate_game_page, jsonld_script, prepare_catalog
from import_crazygames_embed_games import build_game_record, build_source_guide, discover_category_urls, fetch_game, identity_keys, validate_embed
from optimize_seo import ensure_game_schema_fields


class ImportQualityTests(unittest.TestCase):
    def test_discovery_accepts_published_absolute_and_relative_category_links(self):
        session = Mock()
        session.get.return_value.text = (
            '<a href="https://www.crazygames.com/c/puzzle">Puzzle</a>'
            '<a href="/t/mini">Mini</a><a href="/c/puzzle">Puzzle</a>'
            '<a href="https://other.example/c/sports">Other site</a>'
        )
        self.assertEqual(discover_category_urls(session), [
            "https://www.crazygames.com/c/puzzle", "https://www.crazygames.com/t/mini",
        ])

    def test_source_guide_preserves_instructions_without_inventing_controls(self):
        source = {
            "name": "Example", "slug": "example", "metaDescription": "Fit pieces into the grid.",
            "descriptionFirst": "<p>Fit pieces into the grid.</p>",
            "descriptionRest": "<h2>How to Play</h2><p>Drag pieces to fill a row.</p><h2>Tips</h2><p>Leave space for large pieces.</p><h2>More Games</h2><p>Unrelated game.</p>",
            "controls": "<p>Use the mouse.</p>",
        }
        guide = build_source_guide(source)
        self.assertEqual(guide["summary"], source["metaDescription"])
        self.assertEqual(guide["how_to"], "Drag pieces to fill a row.")
        self.assertEqual(guide["tips"], ["Leave space for large pieces."])
        self.assertNotIn("Unrelated", str(guide))
        empty = build_source_guide({"name": "Unknown"})
        self.assertNotIn("WASD", str(empty))

    def test_io_name_alias_is_not_a_new_game(self):
        self.assertTrue(identity_keys({"title": "Voxiom.io"}) & identity_keys({"title": "Voxiom"}))
        self.assertFalse(identity_keys({"title": "Radio"}) & identity_keys({"title": "Rad"}))

    def test_source_facts_and_complete_controls_survive_import(self):
        controls = "Use the left mouse button. " * 20
        game = build_game_record({
            "name": "Example", "slug": "example", "allowEmbed": True,
            "desktopUrl": "https://games.crazygames.com/en_US/example/index.html",
            "developer": "Example Studio", "controls": controls,
            "androidFriendly": True, "iosFriendly": False,
            "upvotes": 123, "rating": 8.8, "addedOn": "2025-01-01",
        })
        self.assertEqual(game["controls"]["Controls"], controls.strip())
        self.assertEqual(game["supported_devices"], ["Desktop", "Android"])
        self.assertEqual(game["developer"], "Example Studio")
        self.assertEqual(game["source_published_at"], "2025-01-01")
        self.assertEqual(game["source_upvotes"], 123)
        self.assertEqual(game["total_plays"], 0)

    def test_embedding_permission_must_be_an_explicit_boolean(self):
        for value in [False, "false", None]:
            response = Mock()
            response.text = '<script id="__NEXT_DATA__" type="application/json">' + json.dumps({
                "props": {"pageProps": {"game": {"name": "Example", "allowEmbed": value}}}
            }) + '</script>'
            session = Mock()
            session.get.return_value = response
            game, reason = fetch_game(session, "example")
            self.assertIsNone(game)
            self.assertEqual(reason, "not_embeddable")

    def test_unusable_or_frame_restricted_builds_are_rejected(self):
        record = {"iframe_url": "https://games.crazygames.com/en_US/example/index.html"}
        for headers, final_url, expected in [
            ({"Content-Type": "text/html", "X-Frame-Options": "SAMEORIGIN"}, record["iframe_url"], False),
            ({"Content-Type": "text/html", "Content-Security-Policy": "frame-ancestors 'self'"}, record["iframe_url"], False),
            ({"Content-Type": "text/html", "Content-Security-Policy": "frame-ancestors https://btwgame.com"}, record["iframe_url"], True),
            ({"Content-Type": "text/html"}, "https://www.crazygames.com/game/example", False),
            ({"Content-Type": "application/json"}, record["iframe_url"], False),
        ]:
            response = Mock(headers=headers, url=final_url)
            session = Mock()
            session.get.return_value = response
            self.assertEqual(validate_embed(session, record.copy())[0], expected)

    def test_jsonld_text_cannot_close_its_script_element(self):
        value = {"name": "Example </script><script>alert(1)</script>"}
        soup = BeautifulSoup(jsonld_script(value), "html.parser")
        scripts = soup.find_all("script")
        self.assertEqual(len(scripts), 1)
        self.assertEqual(json.loads(scripts[0].string), value)


class RenderedFactsTests(unittest.TestCase):
    def test_page_and_game_entities_match_visible_facts_after_seo_processing(self):
        game = prepare_catalog([{
            "title": "Example Game", "slug": "example-game", "category_name": "Puzzle",
            "source": "crazygames", "source_metrics_version": 1,
            "source_upvotes": 123, "source_rating": 4.4, "rating": 0, "total_plays": 0,
            "developer": "Example Studio", "supported_devices": ["Desktop"],
            "source_checked_at": "2026-11-11T04:00:00+00:00",
            "thumbnail_url": "/assets/thumbnails/example.webp",
            "game_url": "https://www.crazygames.com/game/example-game",
            "iframe_url": "https://games.crazygames.com/en_US/example-game/index.html",
            "controls": {"Mouse": "Select a tile"}, "tags": [],
        }])[0]
        soup = BeautifulSoup(generate_game_page(game, []), "html.parser")
        ensure_game_schema_fields(soup, game)
        schemas = [json.loads(script.string) for script in soup.select('script[type="application/ld+json"]')]
        entity = next(schema for schema in schemas if schema["@type"] == "VideoGame")
        page = next(schema for schema in schemas if schema["@type"] == "WebPage")
        self.assertEqual(page["mainEntity"]["@id"], entity["@id"])
        self.assertEqual(page["citation"]["url"], game["game_url"])
        self.assertNotIn("publisher", entity)
        self.assertEqual(page["publisher"]["@id"], "https://btwgame.com/#organization")
        self.assertEqual(entity["image"], "https://btwgame.com/assets/thumbnails/example.webp")
        facts = {row.dt.get_text(): row.dd.get_text() for row in soup.select(".fact-summary-grid > div")}
        self.assertEqual(facts["Game name"], entity["name"])
        self.assertEqual(facts["Category"], entity["genre"])
        self.assertEqual(facts["Devices"], ", ".join(entity["availableOnDevice"]))
        self.assertNotIn("additionalProperty", entity)
        self.assertEqual(facts["Devices"], "Desktop")
        self.assertNotIn("mobile browsers", soup.get_text())

    def test_import_batch_is_present_with_guides_sources_and_cached_images(self):
        data = json.loads(Path("crazygames_games.json").read_text(encoding="utf-8"))
        batch = data["metadata"]["latest_import"]
        catalog = json.loads(Path("static_html/all_games.json").read_text(encoding="utf-8"))["games"]
        by_slug = {game["slug"]: game for game in catalog}
        self.assertEqual(batch["added_count"], len(set(batch["added_slugs"])))
        self.assertEqual(len(data["games"]), sum(game.get("source") == "crazygames" for game in catalog))
        for slug in batch["added_slugs"]:
            game = by_slug[slug]
            self.assertTrue(game["allow_embed"])
            self.assertTrue(game["embed_checked_at"])
            self.assertTrue(game["source_checked_at"])
            guide = game_guide(game)
            self.assertTrue(guide["summary"])
            self.assertTrue(guide["how_to"])
            self.assertTrue(guide["tips"])
            self.assertEqual(urlparse(guide["source_url"]).hostname, "www.crazygames.com")
            self.assertTrue(game["thumbnail_url"].startswith("/assets/thumbnails/"), slug)
            with Image.open(Path("static_html") / game["thumbnail_url"].lstrip("/")) as thumbnail:
                self.assertEqual(thumbnail.size, (320, 200))
            soup = BeautifulSoup(Path(f"static_html/games/{slug}.html").read_text(encoding="utf-8"), "html.parser")
            self.assertIn(guide["summary"], soup.get_text())
            self.assertTrue(soup.find("a", href=guide["source_url"]))
            schemas = [json.loads(script.string) for script in soup.select('script[type="application/ld+json"]')]
            faq = next(schema for schema in schemas if schema["@type"] == "FAQPage")
            visible_questions = [node.get_text() for node in soup.select(".faq-item summary")]
            self.assertEqual([item["name"] for item in faq["mainEntity"]], visible_questions)
            for schema in schemas:
                if schema["@type"] == "VideoGame":
                    self.assertTrue(schema["image"].startswith("https://"))

    def test_account_requirement_is_not_overridden_by_site_marketing(self):
        soup = BeautifulSoup(Path("static_html/games/mirrorland.html").read_text(encoding="utf-8"), "html.parser")
        self.assertIn("Required by the game provider", soup.get_text())
        self.assertIn("Does Mirrorland require an account?", soup.get_text())
        for path in ["index.html", "games.html"]:
            text = Path("static_html", path).read_text(encoding="utf-8").lower()
            self.assertNotIn("no accounts", text)
            self.assertNotIn("without downloads or accounts", text)


if __name__ == "__main__":
    unittest.main()
