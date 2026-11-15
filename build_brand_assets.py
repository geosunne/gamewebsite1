#!/usr/bin/env python3
"""Export the canonical SVG mark and a social cover using real catalog artwork."""
import json
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

import cairosvg
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
ICONS = ROOT / "static/assets/icons"
SELECTED_GAMES = [
    "skydom", "racing-limits", "capybara-clicker",
    "2048", "cut-the-rope-ebx", "sky-riders-buk",
    "mahjong-connect-1", "wood-block-journey", "tropical-merge",
]


def font(size, bold=False):
    names = [
        Path("/System/Library/Fonts/Supplemental") / ("Arial Bold.ttf" if bold else "Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    ]
    for path in names:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def export_icons():
    svg = (ICONS / "favicon.svg").read_bytes()
    for size in (96, 512):
        cairosvg.svg2png(bytestring=svg, write_to=str(ICONS / f"favicon-{size}x{size}.png"), output_width=size, output_height=size)
    apple = ET.fromstring(svg)
    next(element for element in apple.iter() if element.get("id") == "brand-background").set("rx", "0")
    apple_png = cairosvg.svg2png(bytestring=ET.tostring(apple), output_width=180, output_height=180)
    Image.open(BytesIO(apple_png)).convert("RGB").save(ICONS / "apple-touch-icon.png", optimize=True)
    with Image.open(ICONS / "favicon-512x512.png") as image:
        image.save(ROOT / "static/favicon.ico", sizes=[(size, size) for size in (16, 32, 48, 64, 96, 128, 256)])


def build_social_cover():
    catalog = json.loads((ROOT / "static_html/all_games.json").read_text(encoding="utf-8"))["games"]
    by_slug = {game["slug"]: game for game in catalog}
    canvas = Image.new("RGB", (1200, 630), "#ffffff")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((510, 0, 1200, 630), fill="#eef5ff")
    with Image.open(ICONS / "favicon-512x512.png") as mark:
        mark = mark.convert("RGBA").resize((82, 82), Image.Resampling.LANCZOS)
        canvas.paste(mark, (48, 90), mark)
    draw.text((148, 103), "BTW game", font=font(55, True), fill="#172033")
    draw.text((48, 234), "By the way,", font=font(49, True), fill="#172033")
    draw.text((48, 294), "play!", font=font(72, True), fill="#bc3826")
    draw.text((48, 414), "Free browser games", font=font(25), fill="#4e5c73")
    draw.text((48, 526), "btwgame.com", font=font(22, True), fill="#bc3826")
    for index, slug in enumerate(SELECTED_GAMES):
        game = by_slug[slug]
        x, y = 540 + (index % 3) * 208, 67 + (index // 3) * 168
        tile = Image.new("RGB", (192, 152), "white")
        with Image.open(ROOT / "static" / game["thumbnail_url"].lstrip("/")) as artwork:
            tile.paste(ImageOps.fit(artwork.convert("RGB"), (192, 120), method=Image.Resampling.LANCZOS), (0, 0))
        label = game["title"].replace(" (Legacy)", "")
        tile_draw = ImageDraw.Draw(tile)
        label_font = font(13, True)
        while tile_draw.textbbox((0, 0), label, font=label_font)[2] > 174:
            label = label[:-2].rstrip() + "." if not label.endswith(".") else label[:-2] + "."
        tile_draw.text((9, 128), label, font=label_font, fill="#172033")
        mask = Image.new("L", tile.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 191, 151), radius=8, fill=255)
        canvas.paste(tile, (x, y), mask)
    output = ROOT / "static/assets/images/btw-game-share.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True)
    return output


def export_wordmark():
    image = Image.new("RGBA", (300, 75))
    with Image.open(ICONS / "favicon-512x512.png") as mark:
        mark = mark.resize((58, 58), Image.Resampling.LANCZOS)
        image.paste(mark, (4, 8), mark)
    draw = ImageDraw.Draw(image)
    draw.text((76, 10), "BTW game", font=font(31, True), fill="#172033")
    draw.text((77, 46), "By the way, play!", font=font(12, True), fill="#bc3826")
    image.save(ROOT / "static/assets/images/btwlogo.png", optimize=True)


if __name__ == "__main__":
    export_icons()
    export_wordmark()
    cover = build_social_cover()
    print(f"Exported SVG-derived favicons and social cover: {cover}")
