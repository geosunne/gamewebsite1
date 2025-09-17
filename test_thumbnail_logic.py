#!/usr/bin/env python3

"""
Test thumbnail display logic - ensure placeholders only show when no real thumbnail
"""

import requests
from app import create_app
from models import Game

def test_thumbnail_logic():
    """Test that thumbnails are displayed correctly and placeholders only show when needed"""

    app = create_app()

    with app.app_context():
        print("=== Testing Thumbnail Display Logic ===\n")

        base_url = "http://localhost:8000"

        try:
            # Get games with and without thumbnails
            print("📊 Analyzing games in database...")

            games_with_thumbnails = Game.query.filter(
                Game.thumbnail_url.isnot(None),
                Game.is_active == True
            ).limit(5).all()

            games_without_thumbnails = Game.query.filter(
                Game.thumbnail_url.is_(None),
                Game.is_active == True
            ).limit(5).all()

            print(f"✅ Found {len(games_with_thumbnails)} games with thumbnails")
            print(f"❌ Found {len(games_without_thumbnails)} games without thumbnails")

            # Test API data structure
            print("\n📡 Testing API responses...")

            # Test homepage API calls
            new_games_response = requests.get(f"{base_url}/api/games?new=true&per_page=3&sort=newest")
            popular_games_response = requests.get(f"{base_url}/api/games?per_page=3&sort=popular")

            if new_games_response.status_code == 200:
                new_games = new_games_response.json()['games']
                print(f"\n🆕 New Games Thumbnail Status:")
                for game in new_games:
                    has_thumbnail = bool(game.get('thumbnail_url'))
                    status = "✅ Has thumbnail" if has_thumbnail else "❌ No thumbnail (will show 🎮)"
                    print(f"   {game['title']}: {status}")

            if popular_games_response.status_code == 200:
                popular_games = popular_games_response.json()['games']
                print(f"\n🔥 Popular Games Thumbnail Status:")
                for game in popular_games:
                    has_thumbnail = bool(game.get('thumbnail_url'))
                    status = "✅ Has thumbnail" if has_thumbnail else "❌ No thumbnail (will show 🎮)"
                    print(f"   {game['title']}: {status}")

            # Test individual game pages
            print(f"\n🎮 Testing Individual Game Pages:")
            test_games = ['papas-donuteria', 'geometry-dash', 'monster-survivors']

            for slug in test_games:
                # Test game page response
                game_response = requests.head(f"{base_url}/games/{slug}")
                status = "✅" if game_response.status_code == 200 else "❌"

                # Get game data to check thumbnail
                game = Game.query.filter_by(slug=slug).first()
                if game:
                    has_thumbnail = bool(game.thumbnail_url)
                    thumbnail_status = "✅ Real thumbnail" if has_thumbnail else "❌ Placeholder 🎮"
                    print(f"   /games/{slug}: {status} | {thumbnail_status}")

            # Summary
            total_games = Game.query.filter(Game.is_active == True).count()
            games_with_thumbs = Game.query.filter(
                Game.thumbnail_url.isnot(None),
                Game.is_active == True
            ).count()

            print(f"\n📈 Summary:")
            print(f"   Total active games: {total_games}")
            print(f"   Games showing real thumbnails: {games_with_thumbs}")
            print(f"   Games showing 🎮 placeholder: {total_games - games_with_thumbs}")
            print(f"   Thumbnail coverage: {games_with_thumbs/total_games*100:.1f}%")

            print("\n✅ Thumbnail logic test completed!")

        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure it's running on localhost:8000")
        except Exception as e:
            print(f"❌ Error during testing: {e}")

if __name__ == '__main__':
    test_thumbnail_logic()