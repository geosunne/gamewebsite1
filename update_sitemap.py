#!/usr/bin/env python3
import json

def update_sitemap():
    # Read updated games data
    with open('static_html/all_games.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract games array from the data structure
    games = data.get('games', []) if isinstance(data, dict) else data

    # Generate sitemap URLs
    base_url = "https://btwgame.com"
    urls = [
        f"{base_url}/",
        f"{base_url}/games.html"
    ]

    # Add game URLs
    for game in games:
        urls.append(f"{base_url}/games/{game['slug']}")

    # Write sitemap
    with open('static_html/sitemap.txt', 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')

    print(f"Updated sitemap.txt with {len(urls)} URLs")
    print(f"  - 2 main pages")
    print(f"  - {len(games)} game pages")

if __name__ == "__main__":
    update_sitemap()