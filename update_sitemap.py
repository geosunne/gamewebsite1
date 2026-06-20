#!/usr/bin/env python3
import json
import os
from datetime import date
from xml.sax.saxutils import escape

def update_sitemap():
    # Read updated games data
    with open('static_html/all_games.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract games array from the data structure
    games = data.get('games', []) if isinstance(data, dict) else data
    categories = []
    if os.path.exists('static_html/categories.json'):
        with open('static_html/categories.json', 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
            categories = categories_data if isinstance(categories_data, list) else []

    # Generate sitemap URLs
    base_url = "https://btwgame.com"
    urls = [
        f"{base_url}/",
        f"{base_url}/games"
    ]

    # Add category URLs
    for category in categories:
        urls.append(f"{base_url}/categories/{category['slug']}")

    # Add game URLs
    for game in games:
        urls.append(f"{base_url}/games/{game['slug']}")

    # Write sitemap
    with open('static_html/sitemap.txt', 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')

    print(f"Updated sitemap.txt with {len(urls)} URLs")
    print(f"  - 2 main pages")
    print(f"  - {len(categories)} category pages")
    print(f"  - {len(games)} game pages")

    today = date.today().isoformat()
    with open('static_html/sitemap.xml', 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for index, url in enumerate(urls):
            priority = '1.0' if index == 0 else '0.9' if index == 1 else '0.8'
            changefreq = 'daily' if index < 2 else 'weekly'
            f.write('    <url>\n')
            f.write(f'        <loc>{escape(url)}</loc>\n')
            f.write(f'        <lastmod>{today}</lastmod>\n')
            f.write(f'        <changefreq>{changefreq}</changefreq>\n')
            f.write(f'        <priority>{priority}</priority>\n')
            f.write('    </url>\n')
        f.write('</urlset>\n')

    print(f"Updated sitemap.xml with {len(urls)} URLs")

    with open('static_html/_redirects', 'w', encoding='utf-8') as f:
        f.write('/index.html / 308\n')
        f.write('/games.html /games 308\n')
        f.write('/categories/:slug.html /categories/:slug 308\n')
        f.write('/categories/:slug/ /categories/:slug 308\n')
        f.write('/games/:slug.html /games/:slug 308\n')
        f.write('/games/:slug/ /games/:slug 308\n')
        f.write('/games/jailbreak-prison-escapeâ /games/jailbreak-prison-escape 308\n')
        f.write('/games/jailbreak-prison-escapeâ.html /games/jailbreak-prison-escape 308\n')
        f.write('/games/jailbreak-prison-escape%C3%A2 /games/jailbreak-prison-escape 308\n')
        f.write('/games/jailbreak-prison-escape%C3%A2.html /games/jailbreak-prison-escape 308\n')

    print("Updated _redirects for legacy .html URLs")

if __name__ == "__main__":
    update_sitemap()
