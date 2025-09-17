#!/usr/bin/env python3

"""
Improved import games data from games_data.json into the database with better data processing
"""

import json
import re
import random
from datetime import datetime, timedelta
from app import create_app
from models import Game, Category, db
from sqlalchemy.exc import IntegrityError

def clean_url(url):
    """Clean URL by removing trailing spaces and validating"""
    if not url:
        return None
    cleaned = url.strip()
    if cleaned and (cleaned.startswith('http://') or cleaned.startswith('https://')):
        return cleaned
    return None

def create_slug(title):
    """Create a URL-friendly slug from title"""
    if not title:
        return None
    # Remove special characters and convert to lowercase
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    # Replace spaces and multiple hyphens with single hyphen
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    return slug[:100] if slug else None  # Limit to 100 chars

def get_or_create_category(category_name):
    """Get existing category or create new one"""
    if not category_name or category_name.strip() == '':
        category_name = 'General'

    category_name = category_name.strip()
    category_slug = create_slug(category_name)

    if not category_slug:
        category_name = 'General'
        category_slug = 'general'

    category = Category.query.filter_by(slug=category_slug).first()
    if not category:
        category = Category(
            name=category_name,
            slug=category_slug,
            description=f'Games in the {category_name} category'
        )
        db.session.add(category)
        try:
            db.session.commit()
            print(f"Created category: {category_name}")
        except IntegrityError:
            db.session.rollback()
            # Try to get it again in case another process created it
            category = Category.query.filter_by(slug=category_slug).first()
            if not category:
                raise

    return category

def generate_rating():
    """Generate a realistic rating between 3.5 and 5.0"""
    return round(random.uniform(3.5, 5.0), 1)

def generate_play_count():
    """Generate a realistic play count"""
    return random.randint(500, 50000)

def generate_tags_from_game_data(game_data):
    """Generate tags based on game title, description, and type"""
    tags = []

    title = game_data.get('title', '').lower()
    description = game_data.get('description', '').lower()
    game_type = game_data.get('game_type', '').lower()

    # Tags based on game type
    if game_type == 'flash':
        tags.append('Flash')
    elif game_type == 'html5':
        tags.append('HTML5')
    elif 'unity' in game_type.lower():
        tags.append('Unity')

    # Tags based on title keywords
    title_keywords = {
        'papa': ['Cooking', 'Restaurant', 'Time Management'],
        'parkour': ['Action', 'Platform', 'Adventure'],
        'clicker': ['Clicker', 'Idle', 'Casual'],
        'brainrot': ['Fun', 'Meme', 'Casual'],
        'drift': ['Racing', 'Cars', 'Driving'],
        'run': ['Running', 'Endless', 'Platform'],
        'merge': ['Puzzle', 'Strategy', 'Merge'],
        'obby': ['Platform', 'Adventure', 'Roblox'],
        'simulator': ['Simulation', 'Management', 'Strategy'],
        'geometry': ['Rhythm', 'Platform', 'Arcade'],
        'traffic': ['Cars', 'Management', 'Strategy'],
        'love': ['Casual', 'Fun', 'Social'],
        'pixel': ['Retro', 'Arcade', 'Pixel Art'],
        'io': ['Multiplayer', 'Online', 'Competitive']
    }

    for keyword, keyword_tags in title_keywords.items():
        if keyword in title:
            tags.extend(keyword_tags)

    # Tags based on description keywords
    desc_keywords = {
        'survival': ['Survival'],
        'puzzle': ['Puzzle'],
        'racing': ['Racing'],
        'cooking': ['Cooking'],
        'adventure': ['Adventure'],
        'action': ['Action'],
        'strategy': ['Strategy'],
        'multiplayer': ['Multiplayer'],
        '3d': ['3D'],
        'retro': ['Retro'],
        'arcade': ['Arcade'],
        'casual': ['Casual']
    }

    for keyword, keyword_tags in desc_keywords.items():
        if keyword in description:
            tags.extend(keyword_tags)

    # Remove duplicates and limit to 5 tags
    unique_tags = list(dict.fromkeys(tags))  # Preserves order
    return unique_tags[:5]

def generate_features_from_game_data(game_data):
    """Generate features based on game data"""
    features = [
        "Free to play",
        "No download required",
        "Play in browser"
    ]

    game_type = game_data.get('game_type', '').lower()
    title = game_data.get('title', '').lower()

    if game_type == 'html5':
        features.append("HTML5 compatible")
        features.append("Mobile friendly")
    elif game_type == 'flash':
        features.append("Classic Flash game")
    elif 'unity' in game_type.lower():
        features.append("Unity powered")
        features.append("3D graphics")

    if 'multiplayer' in game_data.get('description', '').lower():
        features.append("Multiplayer support")

    if any(word in title for word in ['clicker', 'idle']):
        features.append("Idle gameplay")

    if any(word in title for word in ['parkour', 'run', 'jump']):
        features.append("Fast-paced action")

    return features[:6]  # Limit to 6 features

def generate_controls_from_game_data(game_data):
    """Generate controls based on game data"""
    title = game_data.get('title', '').lower()
    game_type = game_data.get('game_type', '').lower()

    # Basic controls
    controls = {}

    if any(word in title for word in ['clicker', 'click']):
        controls = {
            "Mouse": "Click to play",
            "Left Click": "Main action"
        }
    elif any(word in title for word in ['parkour', 'run', 'jump', 'geometry']):
        controls = {
            "Arrow Keys": "Move left/right",
            "Spacebar": "Jump",
            "Mouse": "Navigate menus"
        }
    elif any(word in title for word in ['drift', 'racing', 'car', 'traffic']):
        controls = {
            "Arrow Keys": "Steer and accelerate",
            "WASD": "Alternative controls",
            "Spacebar": "Handbrake"
        }
    elif any(word in title for word in ['papa', 'cooking']):
        controls = {
            "Mouse": "Click and drag ingredients",
            "Left Click": "Select items",
            "Drag & Drop": "Prepare orders"
        }
    elif 'io' in title:
        controls = {
            "Mouse": "Move and aim",
            "Left Click": "Primary action",
            "Right Click": "Secondary action",
            "WASD": "Alternative movement"
        }
    else:
        # Default controls
        controls = {
            "Mouse": "Click and interact",
            "Arrow Keys": "Navigate",
            "Spacebar": "Action"
        }

    return controls

def import_games_from_json_improved(json_file_path):
    """Import games from JSON file into database with improved data processing"""

    app = create_app()

    with app.app_context():
        try:
            # Read JSON file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            games_data = data.get('games', [])
            total_games = len(games_data)

            print(f"Found {total_games} games to import with improved processing")

            imported_count = 0
            updated_count = 0
            skipped_count = 0
            error_count = 0

            for i, game_data in enumerate(games_data, 1):
                try:
                    title = game_data.get('title', '').strip()
                    description = game_data.get('description', '').strip()

                    # Skip if no title or description
                    if not title or not description:
                        print(f"Skipping game {i}: Missing title or description")
                        skipped_count += 1
                        continue

                    # Skip if no iframe source
                    iframes = game_data.get('iframes', [])
                    if not iframes or not iframes[0].get('src'):
                        print(f"Skipping '{title}': No iframe source found")
                        skipped_count += 1
                        continue

                    # Get iframe URL and clean it
                    iframe_url = clean_url(iframes[0]['src'])
                    if not iframe_url:
                        print(f"Skipping '{title}': Invalid iframe URL")
                        skipped_count += 1
                        continue

                    # Create slug
                    slug = create_slug(title)
                    if not slug:
                        print(f"Skipping '{title}': Could not create valid slug")
                        skipped_count += 1
                        continue

                    # Check if game already exists
                    existing_game = Game.query.filter_by(slug=slug).first()

                    if existing_game:
                        # Update existing game with better data
                        print(f"Updating existing game: {title}")

                        # Generate missing data
                        if existing_game.rating == 0.0:
                            existing_game.rating = generate_rating()

                        if existing_game.total_plays == 0:
                            existing_game.total_plays = generate_play_count()

                        if not existing_game.tags:
                            existing_game.tags = generate_tags_from_game_data(game_data)

                        if not existing_game.features or len(existing_game.features) <= 4:
                            existing_game.features = generate_features_from_game_data(game_data)

                        if not existing_game.controls or len(existing_game.controls) <= 2:
                            existing_game.controls = generate_controls_from_game_data(game_data)

                        db.session.commit()
                        updated_count += 1
                        continue

                    # Get or create category
                    category_name = game_data.get('category', '').strip()
                    category = get_or_create_category(category_name)

                    # Clean thumbnail URL
                    thumbnail_url = clean_url(game_data.get('thumbnail'))

                    # Generate realistic game data
                    rating = generate_rating()
                    total_plays = generate_play_count()
                    tags = generate_tags_from_game_data(game_data)
                    features = generate_features_from_game_data(game_data)
                    controls = generate_controls_from_game_data(game_data)

                    # Generate a realistic release date (within last 2 years)
                    days_ago = random.randint(0, 730)
                    release_date = datetime.now() - timedelta(days=days_ago)

                    # Create game object
                    new_game = Game(
                        title=title[:100],  # Limit to 100 chars
                        slug=slug,
                        description=description[:1000],  # Limit to 1000 chars
                        long_description=description,
                        thumbnail_url=thumbnail_url,
                        game_url=iframe_url,
                        iframe_url=iframe_url,
                        category_id=category.id,
                        rating=rating,
                        total_plays=total_plays,
                        is_featured=False,
                        is_new=True,
                        is_active=True,
                        tags=tags,
                        features=features,
                        controls=controls,
                        release_date=release_date
                    )

                    db.session.add(new_game)
                    db.session.commit()

                    imported_count += 1
                    print(f"Imported [{i}/{total_games}]: {title}")
                    print(f"  Rating: {rating} | Plays: {total_plays:,} | Tags: {len(tags)}")

                except Exception as e:
                    db.session.rollback()
                    error_count += 1
                    print(f"Error importing game {i} ('{title if 'title' in locals() else 'Unknown'}'): {e}")
                    continue

            print(f"\nImproved import completed!")
            print(f"Total processed: {total_games}")
            print(f"Successfully imported: {imported_count}")
            print(f"Updated existing: {updated_count}")
            print(f"Skipped: {skipped_count}")
            print(f"Errors: {error_count}")

            return imported_count, updated_count, skipped_count, error_count

        except Exception as e:
            print(f"Fatal error during import: {e}")
            return 0, 0, 0, 1

if __name__ == '__main__':
    json_file = 'games_data.json'
    print(f"Starting improved import from {json_file}...")

    imported, updated, skipped, errors = import_games_from_json_improved(json_file)

    if imported > 0:
        print(f"\n✅ Successfully imported {imported} new games!")
    if updated > 0:
        print(f"🔄 Updated {updated} existing games with better data!")
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} games")
    if errors > 0:
        print(f"❌ {errors} errors occurred")