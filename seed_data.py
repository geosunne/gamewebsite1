#!/usr/bin/env python3
"""
Seed script to populate the database with initial data
"""

from app import create_app, db
from models import Game, Category, GameStats
from datetime import datetime, date, timedelta
import json

def create_categories():
    """Create initial categories"""
    categories_data = [
        {
            'name': 'Action',
            'slug': 'action',
            'description': 'Fast-paced games with combat and challenges'
        },
        {
            'name': 'Puzzle',
            'slug': 'puzzle',
            'description': 'Brain-teasing games that challenge your logic'
        },
        {
            'name': 'Racing',
            'slug': 'racing',
            'description': 'High-speed racing and driving games'
        },
        {
            'name': 'Strategy',
            'slug': 'strategy',
            'description': 'Strategic thinking and planning games'
        },
        {
            'name': 'Adventure',
            'slug': 'adventure',
            'description': 'Exploration and story-driven games'
        },
        {
            'name': 'Sports',
            'slug': 'sports',
            'description': 'Sports and athletic games'
        }
    ]

    for cat_data in categories_data:
        existing = Category.query.filter_by(slug=cat_data['slug']).first()
        if not existing:
            category = Category(**cat_data)
            db.session.add(category)
            print(f"Created category: {cat_data['name']}")

    db.session.commit()

def create_games():
    """Create initial games"""

    # Get categories
    action_cat = Category.query.filter_by(slug='action').first()
    puzzle_cat = Category.query.filter_by(slug='puzzle').first()
    racing_cat = Category.query.filter_by(slug='racing').first()
    strategy_cat = Category.query.filter_by(slug='strategy').first()
    adventure_cat = Category.query.filter_by(slug='adventure').first()

    games_data = [
        {
            'title': 'Monster Survivors',
            'slug': 'monster-survivors',
            'description': 'An intense survival game where you battle endless waves of monsters',
            'long_description': 'Monster Survivors is an exhilarating browser-based survival game that puts you in the heart of relentless monster waves. As the last defender standing, you must use your wits, reflexes, and an arsenal of weapons to survive as long as possible against increasingly difficult enemies.',
            'thumbnail_url': 'https://btwgame.com/images/monster-survivors-thumb.jpg',
            'game_url': 'https://cloud.onlinegames.io/games/2025/unity/monster-survivors/index-og.html',
            'category_id': action_cat.id,
            'rating': 4.5,
            'total_plays': 15420,
            'is_featured': True,
            'is_new': False,
            'tags': ['Survival', 'Action', 'Shooter'],
            'features': ['Intense Combat', 'Easy Controls', 'Progressive Difficulty', 'Achievements', 'Power-ups', 'Strategic Gameplay'],
            'controls': {
                'WASD': 'Move your character',
                'Mouse': 'Aim your weapon',
                'Left Click': 'Fire weapon',
                'Space': 'Special ability',
                'E': 'Interact / Pick up',
                'ESC': 'Pause menu'
            },
            'release_date': datetime(2024, 12, 1)
        },
        {
            'title': 'Puzzle Master',
            'slug': 'puzzle-master',
            'description': 'Challenge your mind with hundreds of brain-teasing puzzles',
            'long_description': 'Puzzle Master offers a comprehensive collection of brain-teasing challenges designed to test your logical thinking and problem-solving skills. With over 500 unique puzzles across multiple difficulty levels.',
            'thumbnail_url': 'https://btwgame.com/images/puzzle-master-thumb.jpg',
            'game_url': 'https://example.com/puzzle-master',
            'category_id': puzzle_cat.id,
            'rating': 4.3,
            'total_plays': 8750,
            'is_featured': True,
            'is_new': False,
            'tags': ['Puzzle', 'Brain', 'Logic'],
            'features': ['500+ Puzzles', 'Multiple Difficulty Levels', 'Hint System', 'Progress Tracking', 'Daily Challenges'],
            'controls': {
                'Mouse': 'Click to interact',
                'Space': 'Hint',
                'R': 'Reset puzzle',
                'ESC': 'Menu'
            },
            'release_date': datetime(2024, 11, 15)
        },
        {
            'title': 'Racing Fever',
            'slug': 'racing-fever',
            'description': 'High-speed racing action with stunning graphics and realistic physics',
            'long_description': 'Experience the thrill of high-speed racing with Racing Fever. Featuring stunning graphics, realistic physics, and multiple tracks, this game delivers an authentic racing experience.',
            'thumbnail_url': 'https://btwgame.com/images/racing-fever-thumb.jpg',
            'game_url': 'https://example.com/racing-fever',
            'category_id': racing_cat.id,
            'rating': 4.7,
            'total_plays': 22100,
            'is_featured': False,
            'is_new': True,
            'tags': ['Racing', 'Cars', 'Speed'],
            'features': ['Realistic Physics', 'Multiple Tracks', 'Car Customization', 'Tournament Mode', 'Leaderboards'],
            'controls': {
                'Arrow Keys': 'Steer and accelerate',
                'Space': 'Handbrake',
                'C': 'Change camera',
                'N': 'Nitro boost'
            },
            'release_date': datetime(2025, 1, 10)
        },
        {
            'title': 'Space Explorer',
            'slug': 'space-explorer',
            'description': 'Explore the vast universe and discover new planets and civilizations',
            'long_description': 'Embark on an epic journey through space in Space Explorer. Discover new planets, encounter alien civilizations, and uncover the mysteries of the universe in this immersive space exploration game.',
            'thumbnail_url': 'https://btwgame.com/images/space-explorer-thumb.jpg',
            'game_url': 'https://example.com/space-explorer',
            'category_id': adventure_cat.id,
            'rating': 4.4,
            'total_plays': 12300,
            'is_featured': False,
            'is_new': True,
            'tags': ['Space', 'Exploration', 'Sci-Fi'],
            'features': ['Open World', 'Planet Exploration', 'Resource Management', 'Alien Encounters', 'Spaceship Upgrades'],
            'controls': {
                'WASD': 'Move spaceship',
                'Mouse': 'Look around',
                'Left Click': 'Interact',
                'Space': 'Boost',
                'M': 'Map'
            },
            'release_date': datetime(2025, 1, 5)
        },
        {
            'title': 'Tower Defense Pro',
            'slug': 'tower-defense-pro',
            'description': 'Defend your base against waves of enemies with strategic tower placement',
            'long_description': 'Tower Defense Pro challenges you to defend your base against endless waves of enemies using strategic tower placement and upgrades. Plan your defense carefully and utilize different tower types to succeed.',
            'thumbnail_url': 'https://btwgame.com/images/tower-defense-thumb.jpg',
            'game_url': 'https://example.com/tower-defense-pro',
            'category_id': strategy_cat.id,
            'rating': 4.6,
            'total_plays': 18900,
            'is_featured': True,
            'is_new': False,
            'tags': ['Strategy', 'Defense', 'Tower'],
            'features': ['Multiple Tower Types', 'Upgrade System', 'Boss Battles', 'Multiple Maps', 'Achievement System'],
            'controls': {
                'Mouse': 'Select and place towers',
                'Space': 'Pause/Resume',
                'U': 'Upgrade tower',
                'S': 'Sell tower'
            },
            'release_date': datetime(2024, 10, 20)
        },
        {
            'title': 'Ninja Warrior',
            'slug': 'ninja-warrior',
            'description': 'Master the art of stealth and combat in this action-packed ninja adventure',
            'long_description': 'Become a master ninja in this action-packed adventure. Use stealth, combat skills, and ancient weapons to complete challenging missions and defeat powerful enemies.',
            'thumbnail_url': 'https://btwgame.com/images/ninja-warrior-thumb.jpg',
            'game_url': 'https://example.com/ninja-warrior',
            'category_id': action_cat.id,
            'rating': 4.2,
            'total_plays': 9800,
            'is_featured': False,
            'is_new': True,
            'tags': ['Ninja', 'Action', 'Stealth'],
            'features': ['Stealth Gameplay', 'Combat System', 'Multiple Weapons', 'Challenging Levels', 'Boss Fights'],
            'controls': {
                'Arrow Keys': 'Move',
                'Z': 'Attack',
                'X': 'Jump',
                'C': 'Stealth mode',
                'Space': 'Throw shuriken'
            },
            'release_date': datetime(2025, 1, 3)
        }
    ]

    for game_data in games_data:
        existing = Game.query.filter_by(slug=game_data['slug']).first()
        if not existing:
            game = Game(**game_data)
            db.session.add(game)
            print(f"Created game: {game_data['title']}")

    db.session.commit()

def create_sample_stats():
    """Create sample game statistics"""
    games = Game.query.all()

    # Create stats for the last 30 days
    for i in range(30):
        stat_date = date.today() - timedelta(days=i)

        for game in games:
            # Generate random stats based on game popularity
            base_plays = max(10, game.total_plays // 100)
            daily_plays = max(1, base_plays + (i % 7) * 2)  # More plays on certain days

            existing_stat = GameStats.query.filter_by(
                game_id=game.id,
                date=stat_date
            ).first()

            if not existing_stat:
                game_stat = GameStats(
                    game_id=game.id,
                    date=stat_date,
                    daily_plays=daily_plays,
                    unique_players=max(1, daily_plays // 2),
                    avg_play_duration=300 + (i % 10) * 30  # 5-10 minutes average
                )
                db.session.add(game_stat)

    db.session.commit()
    print("Created sample game statistics")

def main():
    """Main seeding function"""
    app = create_app()

    with app.app_context():
        print("Creating database tables...")
        db.create_all()

        print("Seeding categories...")
        create_categories()

        print("Seeding games...")
        create_games()

        print("Creating sample statistics...")
        create_sample_stats()

        print("Database seeding completed!")

if __name__ == '__main__':
    main()