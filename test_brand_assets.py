import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from PIL import Image

from generate_static_pages import render_brand_mark
from site_icons import BRAND_MARK, SOCIAL_IMAGE, ensure_social_meta


class BrandAssetTests(unittest.TestCase):
    def test_header_uses_the_canonical_accessible_mark(self):
        soup = BeautifulSoup(render_brand_mark(), "html.parser")
        link = soup.find("a")
        self.assertEqual(link["aria-label"], "BTW game home")
        self.assertEqual(link.img["src"], BRAND_MARK)
        self.assertEqual(link.img["width"], link.img["height"])
        self.assertEqual(link.img["alt"], "")
        self.assertIsNone(link.svg)
        self.assertEqual(link.select_one(".brand-name").get_text(), "BTW game")

    def test_icon_exports_have_real_compatible_dimensions(self):
        for name, size in [("favicon-96x96.png", 96), ("favicon-512x512.png", 512), ("apple-touch-icon.png", 180)]:
            with Image.open(Path("static/assets/icons") / name) as image:
                self.assertEqual(image.size, (size, size))
                if name == "apple-touch-icon.png":
                    self.assertEqual(image.mode, "RGB")
        with Image.open("static/favicon.ico") as icon:
            self.assertEqual(icon.ico.sizes(), {(size, size) for size in (16, 32, 48, 64, 96, 128, 256)})
        with Image.open("static/assets/images/btwlogo.png") as wordmark:
            self.assertEqual(wordmark.size, (300, 75))

    def test_social_metadata_deduplicates_and_preserves_game_artwork(self):
        soup = BeautifulSoup('<html><head><meta property="og:image" content="old"><meta property="og:image" content="duplicate"></head></html>', "html.parser")
        ensure_social_meta(soup)
        ensure_social_meta(soup)
        self.assertEqual(len(soup.select('meta[property="og:image"]')), 1)
        self.assertEqual(soup.find("meta", property="og:image:width")["content"], "1200")
        catalog = json.loads(Path("static_html/all_games.json").read_text())["games"]
        game = next(game for game in catalog if game["slug"] == "2048")
        artwork = "https://btwgame.com" + game["thumbnail_url"]
        ensure_social_meta(soup, artwork, "2048 game artwork")
        self.assertEqual(soup.find("meta", property="og:image")["content"], artwork)
        self.assertEqual(soup.find("meta", property="og:image:width")["content"], "320")
        self.assertEqual(soup.find("meta", property="og:image:height")["content"], "200")
        ensure_social_meta(soup, "https://example.com/unknown.png", "External game artwork")
        self.assertIsNone(soup.find("meta", property="og:image:width"))
        self.assertIsNone(soup.find("meta", property="og:image:height"))

    def test_site_social_cover_and_organization_logo_have_separate_roles(self):
        soup = BeautifulSoup(Path("static_html/index.html").read_text(), "html.parser")
        self.assertEqual(soup.find("meta", property="og:image")["content"], SOCIAL_IMAGE)
        self.assertEqual(soup.find("meta", property="og:site_name")["content"], "BTW game")
        self.assertTrue(soup.find("meta", attrs={"name": "twitter:image:alt"})["content"])
        with Image.open(Path("static_html") / urlsplit(SOCIAL_IMAGE).path.lstrip("/")) as cover:
            self.assertEqual(cover.size, (1200, 630))
        entities = [json.loads(tag.string) for tag in soup.select('script[type="application/ld+json"]')]
        organization = next(entity for entity in entities if entity.get("@type") == "Organization")
        self.assertNotEqual(organization["logo"], SOCIAL_IMAGE)
        with Image.open(Path("static_html") / urlsplit(organization["logo"]).path.lstrip("/")) as logo:
            self.assertEqual(logo.size, (512, 512))


if __name__ == "__main__":
    unittest.main()
