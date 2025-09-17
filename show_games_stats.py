#!/usr/bin/env python3

"""
Show games statistics after import
"""

from app import create_app
from models import Game, Category, db

def show_games_stats():
    app = create_app()

    with app.app_context():
        print("=== BTW Games Database Statistics ===\n")

        # Total counts
        total_games = Game.query.filter(Game.is_active == True).count()
        total_categories = Category.query.count()

        print(f"📊 Total Games: {total_games}")
        print(f"📂 Total Categories: {total_categories}")
        print()

        # Games by category
        print("🎯 Games by Category:")
        categories = Category.query.all()
        for category in categories:
            game_count = Game.query.filter_by(category_id=category.id, is_active=True).count()
            print(f"   {category.name}: {game_count} games")

        print()

        # Recently added games
        print("🆕 Recently Added Games (last 10):")
        recent_games = Game.query.filter(Game.is_active == True).order_by(Game.created_at.desc()).limit(10).all()

        for i, game in enumerate(recent_games, 1):
            iframe_status = "✅" if game.iframe_url else "❌"
            thumbnail_status = "✅" if game.thumbnail_url else "❌"
            print(f"   {i:2d}. {game.title}")
            print(f"       Category: {game.category_name}")
            print(f"       Slug: {game.slug}")
            print(f"       Iframe: {iframe_status} | Thumbnail: {thumbnail_status}")

        print()

        # Games with iframe URLs
        games_with_iframe = Game.query.filter(Game.iframe_url.isnot(None), Game.is_active == True).count()
        games_with_thumbnails = Game.query.filter(Game.thumbnail_url.isnot(None), Game.is_active == True).count()

        print("📈 Content Completeness:")
        print(f"   Games with iframe URLs: {games_with_iframe}/{total_games} ({games_with_iframe/total_games*100:.1f}%)")
        print(f"   Games with thumbnails: {games_with_thumbnails}/{total_games} ({games_with_thumbnails/total_games*100:.1f}%)")

        print("\n=== End of Statistics ===")

if __name__ == '__main__':
    show_games_stats()