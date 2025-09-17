#!/usr/bin/env python3

"""
Test homepage games display and links
"""

import requests
import json
from app import create_app
from models import Game

def test_homepage_games():
    """Test that homepage displays games with correct links and thumbnails"""

    app = create_app()

    with app.app_context():
        print("=== Testing Homepage Games ===\n")

        base_url = "http://localhost:8000"

        try:
            # Test API endpoints used by homepage
            print("📡 Testing API endpoints...")

            # Test new games endpoint
            new_games_response = requests.get(f"{base_url}/api/games?new=true&per_page=6&sort=newest")
            print(f"New games API: {new_games_response.status_code}")

            # Test popular games endpoint
            popular_games_response = requests.get(f"{base_url}/api/games?per_page=6&sort=popular")
            print(f"Popular games API: {popular_games_response.status_code}")

            if new_games_response.status_code == 200:
                new_games = new_games_response.json()['games']
                print(f"✅ Found {len(new_games)} new games")

                print("\n🆕 New Games with Thumbnails:")
                for i, game in enumerate(new_games[:3], 1):
                    has_thumbnail = bool(game.get('thumbnail_url'))
                    thumbnail_status = "✅" if has_thumbnail else "❌"

                    print(f"   {i}. {game['title']}")
                    print(f"      Link: /games/{game['slug']}")
                    print(f"      Thumbnail: {thumbnail_status}")
                    if has_thumbnail:
                        print(f"      URL: {game['thumbnail_url'][:50]}...")

            if popular_games_response.status_code == 200:
                popular_games = popular_games_response.json()['games']
                print(f"\n✅ Found {len(popular_games)} popular games")

                print("\n🔥 Popular Games with Thumbnails:")
                for i, game in enumerate(popular_games[:3], 1):
                    has_thumbnail = bool(game.get('thumbnail_url'))
                    thumbnail_status = "✅" if has_thumbnail else "❌"

                    print(f"   {i}. {game['title']}")
                    print(f"      Link: /games/{game['slug']}")
                    print(f"      Thumbnail: {thumbnail_status}")
                    if has_thumbnail:
                        print(f"      URL: {game['thumbnail_url'][:50]}...")

            # Test some individual game pages
            print(f"\n🎮 Testing Individual Game Pages:")
            test_games = ['monster-survivors', 'papas-donuteria', 'geometry-dash']

            for slug in test_games:
                game_response = requests.head(f"{base_url}/games/{slug}")
                status = "✅" if game_response.status_code == 200 else "❌"
                print(f"   /games/{slug}: {status} ({game_response.status_code})")

            # Count games with/without thumbnails
            print(f"\n📊 Database Statistics:")
            total_games = Game.query.filter(Game.is_active == True).count()
            games_with_thumbnails = Game.query.filter(
                Game.thumbnail_url.isnot(None),
                Game.is_active == True
            ).count()

            print(f"   Total active games: {total_games}")
            print(f"   Games with thumbnails: {games_with_thumbnails}")
            print(f"   Thumbnail coverage: {games_with_thumbnails/total_games*100:.1f}%")

            print("\n✅ Homepage testing completed!")

        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure it's running on localhost:8000")
        except Exception as e:
            print(f"❌ Error during testing: {e}")

if __name__ == '__main__':
    test_homepage_games()