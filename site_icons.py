"""Shared brand assets, favicon declarations, and social image metadata."""
from functools import lru_cache
from html import escape
from pathlib import Path
import shutil
from urllib.parse import urlsplit


BRAND_MARK = "/assets/icons/favicon.svg"
SOCIAL_IMAGE = "https://btwgame.com/assets/images/btw-game-share.png"
SOCIAL_IMAGE_ALT = "BTW game: By the way, play! A selection of free browser games."


ICON_LINKS = (
    {
        "rel": "icon",
        "type": "image/x-icon",
        "sizes": "16x16 32x32 48x48 64x64 96x96 128x128 256x256",
        "href": "/favicon.ico",
    },
    {
        "rel": "icon",
        "type": "image/png",
        "sizes": "96x96",
        "href": "/assets/icons/favicon-96x96.png",
    },
    {
        "rel": "apple-touch-icon",
        "sizes": "180x180",
        "href": "/assets/icons/apple-touch-icon.png",
    },
)


def render_site_icons():
    return "\n    ".join(
        "<link " + " ".join(f'{key}="{escape(value, quote=True)}"' for key, value in spec.items()) + ">"
        for spec in ICON_LINKS
    )


def ensure_site_icons(soup):
    for spec in ICON_LINKS:
        tag = soup.head.find("link", attrs={"rel": spec["rel"], "href": spec["href"]})
        if tag is None:
            tag = soup.new_tag("link")
            soup.head.append(tag)
        for name, value in spec.items():
            tag[name] = value


@lru_cache(maxsize=4096)
def social_image_size(url):
    parsed = urlsplit(url)
    if parsed.hostname not in (None, "btwgame.com", "www.btwgame.com"):
        return None
    root = Path(__file__).parent / "static"
    path = (root / parsed.path.lstrip("/")).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        return None
    from PIL import Image
    with Image.open(path) as image:
        return image.size


def social_meta_specs(image=SOCIAL_IMAGE, alt=SOCIAL_IMAGE_ALT):
    specs = [
        ("property", "og:site_name", "BTW game"),
        ("property", "og:image", image),
        ("property", "og:image:alt", alt),
        ("name", "twitter:image", image),
        ("name", "twitter:image:alt", alt),
        ("name", "theme-color", "#f05a3f"),
    ]
    size = social_image_size(image)
    if size:
        specs.extend([
            ("property", "og:image:width", str(size[0])),
            ("property", "og:image:height", str(size[1])),
        ])
    return specs


def render_social_meta(image=SOCIAL_IMAGE, alt=SOCIAL_IMAGE_ALT):
    return "\n    ".join(
        f'<meta {attribute}="{name}" content="{escape(value, quote=True)}">'
        for attribute, name, value in social_meta_specs(image, alt)
    )


def ensure_social_meta(soup, image=SOCIAL_IMAGE, alt=SOCIAL_IMAGE_ALT):
    specs = social_meta_specs(image, alt)
    names = {name for attribute, name, value in specs}
    for name in ("og:image:width", "og:image:height"):
        if name not in names:
            for tag in soup.head.find_all("meta", attrs={"property": name}):
                tag.decompose()
    for attribute, name, value in specs:
        matches = soup.head.find_all("meta", attrs={attribute: name})
        tag = matches[0] if matches else soup.new_tag("meta", attrs={attribute: name})
        for duplicate in matches[1:]:
            duplicate.decompose()
        tag["content"] = value
        if not matches:
            soup.head.append(tag)


def copy_root_favicon():
    shutil.copy2(Path("static/favicon.ico"), Path("static_html/favicon.ico"))
