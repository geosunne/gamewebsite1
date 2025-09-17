#!/usr/bin/env python3
import json

def update_game_slugs():
    # Read updated games data
    with open('static_html/all_games.json', 'r', encoding='utf-8') as f:
        games = json.load(f)

    # Extract slugs
    slugs = [game['slug'] for game in games]

    # Write updated slugs to file
    with open('static_html/game_slugs.txt', 'w', encoding='utf-8') as f:
        for slug in slugs:
            f.write(slug + '\n')

    print(f"Updated game_slugs.txt with {len(slugs)} game slugs")

if __name__ == "__main__":
    update_game_slugs()