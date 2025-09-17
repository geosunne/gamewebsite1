#!/usr/bin/env python3

"""
Script to add iframe_url to existing games
"""

from app import create_app
from models import Game, db

def update_games_with_iframe_urls():
    app = create_app()

    with app.app_context():
        # Get all games
        games = Game.query.all()

        for game in games:
            print(f"Updating game: {game.title} (ID: {game.id}, Slug: {game.slug})")

            # For now, set iframe_url to be the same as game_url
            # In a real scenario, you would have specific iframe URLs
            if game.game_url and not game.iframe_url:
                game.iframe_url = game.game_url
                print(f"  Set iframe_url to: {game.iframe_url}")

            # Special case for Monster Survivors
            if game.slug == 'monster-survivors':
                game.iframe_url = 'https://cloud.onlinegames.io/games/2025/unity/monster-survivors/index-og.html'
                print(f"  Updated Monster Survivors iframe_url to: {game.iframe_url}")

        # Commit all changes
        try:
            db.session.commit()
            print(f"\nSuccessfully updated {len(games)} games with iframe URLs")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating games: {e}")
            return False

    return True

if __name__ == '__main__':
    print("Starting iframe URL update...")
    success = update_games_with_iframe_urls()
    if success:
        print("Update completed successfully!")
    else:
        print("Update failed!")