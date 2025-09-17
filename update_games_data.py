#!/usr/bin/env python3
import json
import random

def update_games_data():
    # Read current games data
    with open('static_html/all_games.json', 'r', encoding='utf-8') as f:
        games = json.load(f)

    print(f"Original games count: {len(games)}")

    # Remove example games (games with example.com iframe_url)
    real_games = [game for game in games if 'example.com' not in game.get('iframe_url', '')]

    print(f"Games after removing examples: {len(real_games)}")
    print("Removed games:")
    for game in games:
        if 'example.com' in game.get('iframe_url', ''):
            print(f"  - {game['title']} ({game['slug']})")

    # Reset all isNew flags to False first
    for game in real_games:
        game['isNew'] = False

    # Randomly select 8-12 games to mark as new
    num_new_games = random.randint(8, 12)
    new_games = random.sample(real_games, min(num_new_games, len(real_games)))

    for game in new_games:
        game['isNew'] = True

    print(f"\nMarked {len(new_games)} games as NEW:")
    for game in new_games:
        print(f"  - {game['title']} ({game['slug']})")

    # Write updated data back
    with open('static_html/all_games.json', 'w', encoding='utf-8') as f:
        json.dump(real_games, f, indent=2, ensure_ascii=False)

    # Update new_games.json file
    new_games_only = [game for game in real_games if game['isNew']]
    with open('static_html/new_games.json', 'w', encoding='utf-8') as f:
        json.dump(new_games_only, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated files:")
    print(f"  - all_games.json: {len(real_games)} games")
    print(f"  - new_games.json: {len(new_games_only)} games")

    return real_games, new_games_only

if __name__ == "__main__":
    update_games_data()