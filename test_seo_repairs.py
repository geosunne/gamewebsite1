import json
import threading
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from catalog_quality import legacy_category_redirects, normalize_source_metrics
from generate_static_pages import (
    build_mode_notes, get_all_categories, normalize_game_data, prepare_catalog,
    standardize_game_tags,
)
from import_crazygames_embed_games import build_game_record as crazygames_record
from import_minigame_embed_games import build_game_record, extract_current_game_chunk
from serve_static import StaticHTTPRequestHandler


class SourceDataTests(unittest.TestCase):
    def test_current_game_controls_do_not_leak_from_recommendations(self):
        controls = 'Tap "FIGHT!" to start; drag troops to merge. \u00e9'
        record = {
            "app_id": "tiny-clash",
            "base": {
                "app_url": "https://tiny-clash.library.minigame.com/minigame-index.html",
                "types": ["strategy"],
                "others_option": [
                    {"key": "title", "value": "Game Controls", "type": "play"}, "$b"
                ],
            },
        }
        content = {"key": "content", "value": "$c", "type": "play"}
        recommendation = {"app_id": "cookie-mania", "base": {"controls": "Touch a cookie"}}
        flight = f"c:T{len(controls.encode('utf-8')):x}," + controls
        flight += "b:" + json.dumps(content) + "\na:" + json.dumps(record) + "\n"
        flight += "d:" + json.dumps(recommendation) + "\n"
        html = '<h1>Tiny Clash</h1><script>self.__next_f.push(' + json.dumps([1, flight]) + ')</script>'
        game = build_game_record("tiny-clash", html, html, record["base"]["app_url"])
        self.assertEqual(game["controls"], {"Controls": controls})
        self.assertNotIn("cookie", str(game))
        self.assertEqual(extract_current_game_chunk(html, "not-found"), "")
        with self.assertRaises(ValueError):
            build_game_record("not-found", html, html, "")

    def test_votes_and_heat_are_not_local_plays_and_migration_is_idempotent(self):
        for source, field in [("crazygames", "source_upvotes"), ("minigame", "source_popularity")]:
            old = {"source": source, "rating": 4.4, "total_plays": 1234}
            fixed = normalize_source_metrics(old)
            self.assertEqual(fixed[field], 1234)
            self.assertEqual(fixed["source_rating"], 4.4)
            self.assertEqual(fixed["total_plays"], 0)
            self.assertEqual(fixed["rating"], 0)
            fixed["total_plays"] = 7
            self.assertEqual(normalize_source_metrics(fixed), fixed)
            self.assertEqual(old["total_plays"], 1234)

    def test_new_crazygames_import_preserves_source_metrics(self):
        game = crazygames_record({"name": "Test", "slug": "test", "upvotes": 50, "rating": 8.8})
        self.assertEqual(game["total_plays"], 0)
        self.assertEqual(game["source_upvotes"], 50)
        self.assertEqual(game["source_rating"], 4.4)

    def test_genre_words_do_not_imply_io_or_multiplayer(self):
        game = {"title": "City Life", "description": "An online simulation game", "category_name": "Simulation"}
        tags = standardize_game_tags(game)
        self.assertNotIn("IO Game", tags)
        self.assertNotIn("Multiplayer", tags)
        self.assertNotIn("competitive", build_mode_notes("Cooking", "Cooking", ["Simulation"]))

    def test_thin_category_fallback_survives_page_normalization(self):
        raw = [
            {"slug": "flappy-bird", "title": "Flappy Bird", "category_name": "Arcade"},
            {"slug": "car-parking", "title": "Car Parking", "category_name": "Parking"},
        ]
        prepared = prepare_catalog(raw)
        self.assertEqual([g["category_name"] for g in prepared], ["Casual", "Driving"])
        self.assertEqual([normalize_game_data(g)["category_name"] for g in prepared], ["Casual", "Driving"])
        self.assertEqual(set(get_all_categories(prepared)), {"Casual", "Driving"})
        self.assertNotIn("standardized_tags", raw[0])


class GeneratedCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path("static_html")
        cls.games = json.loads((cls.root / "all_games.json").read_text(encoding="utf-8"))["games"]
        cls.categories = json.loads((cls.root / "categories.json").read_text(encoding="utf-8"))

    def test_pages_match_catalog_categories_and_sitemap(self):
        tree = ET.parse(self.root / "sitemap.xml")
        urls = [node.text for node in tree.iter() if node.tag.endswith("}loc")]
        self.assertEqual(len(urls), len(set(urls)))
        self.assertNotIn("https://btwgame.com/404", urls)
        expected_categories = {category["slug"] for category in self.categories}
        self.assertEqual({p.stem for p in (self.root / "categories").glob("*.html")}, expected_categories)
        for game in self.games:
            path = self.root / "games" / f"{game['slug']}.html"
            self.assertTrue(path.is_file(), game["slug"])
            soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
            schema = next(json.loads(s.string) for s in soup.select('script[type="application/ld+json"]') if json.loads(s.string).get("@type") in {"Game", "VideoGame"})
            self.assertEqual(schema["genre"], game["category_name"], game["slug"])
            self.assertIn(schema["url"], urls)
            if game.get("source") in {"crazygames", "minigame"}:
                self.assertEqual(game["total_plays"], 0)
                self.assertNotIn("visitor rating", soup.get_text())
            if game.get("content_status") == "needs_review":
                self.assertEqual(game["controls"], {})

    def test_internal_category_links_resolve_without_redirects(self):
        valid = {"/categories/" + category["slug"] for category in self.categories}
        for path in self.root.rglob("*.html"):
            soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
            for anchor in soup.select("a[href]"):
                url = urlsplit(urljoin("https://btwgame.com/", anchor["href"]))
                if url.netloc == "btwgame.com" and url.path.startswith("/categories/"):
                    self.assertIn(url.path, valid, f"{path}: {url.path}")

    def test_corrected_game_controls_and_game_specific_notes(self):
        cases = {
            "tiny-clash": ('FIGHT!', 'Touch a cookie'),
            "classic-sudoku": ('grid cell', 'Purchase heroes'),
            "geometr-jump": ('Short Jump', 'fidget'),
            "papas-donuteria": ('doughnuts', 'The main loop is competitive'),
        }
        for slug, (present, absent) in cases.items():
            text = (self.root / "games" / f"{slug}.html").read_text(encoding="utf-8")
            self.assertIn(present, text, slug)
            self.assertNotIn(absent, text, slug)

    def test_not_found_page_is_deployable_and_non_indexable(self):
        soup = BeautifulSoup((self.root / "404.html").read_text(encoding="utf-8"), "html.parser")
        self.assertIn("noindex", soup.find("meta", attrs={"name": "robots"})["content"])
        self.assertEqual(len(soup.find_all("h1")), 1)
        self.assertTrue(soup.find("a", href="/games"))
        self.assertFalse(soup.find("link", rel="canonical"))


class LocalHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), StaticHTTPRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_missing_paths_have_real_404_for_get_and_head(self):
        for path in ["/seo-test-not-found", "/games/seo-test-not-found"]:
            for method in ["GET", "HEAD"]:
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    urllib.request.urlopen(urllib.request.Request(self.base + path, method=method))
                response = raised.exception
                self.assertEqual(response.code, 404)
                self.assertIn("noindex", response.headers["X-Robots-Tag"])
                body = response.read()
                if method == "HEAD":
                    self.assertEqual(body, b"")
                else:
                    self.assertIn(b"Page not found", body)
                response.close()

    def test_legacy_category_redirect_rules_match_the_deployment(self):
        active = {path.stem for path in Path("static_html/categories").glob("*.html")}
        redirects = Path("static_html/_redirects").read_text(encoding="utf-8")
        for source, target in legacy_category_redirects(active).items():
            for suffix in ("", ".html", "/"):
                self.assertIn(f"{source}{suffix} {target} 308", redirects)


if __name__ == "__main__":
    unittest.main()
