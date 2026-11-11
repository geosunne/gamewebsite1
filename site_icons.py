"""Shared favicon declarations for static pages and SEO post-processing."""
from html import escape
from pathlib import Path
import shutil


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


def copy_root_favicon():
    shutil.copy2(Path("static/favicon.ico"), Path("static_html/favicon.ico"))
