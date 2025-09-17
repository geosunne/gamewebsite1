#!/usr/bin/env python3

"""
Import games data from games_data.json into the database
"""

import json
import re
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

def import_games_from_json(json_file_path):
    """Import games from JSON file into database"""

    app = create_app()

    with app.app_context():
        try:
            # Read JSON file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            games_data = data.get('games', [])
            total_games = len(games_data)

            print(f"Found {total_games} games to import")

            imported_count = 0
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
                        print(f"Skipping '{title}': Game with slug '{slug}' already exists")
                        skipped_count += 1
                        continue

                    # Get or create category
                    category_name = game_data.get('category', '').strip()
                    category = get_or_create_category(category_name)

                    # Clean thumbnail URL
                    thumbnail_url = clean_url(game_data.get('thumbnail'))

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
                        rating=0.0,
                        total_plays=0,
                        is_featured=False,
                        is_new=True,
                        is_active=True,
                        tags=game_data.get('tags', []) if game_data.get('tags') else [],
                        features=[
                            "Free to play",
                            "No download required",
                            "Play in browser",
                            "Instant start"
                        ],
                        controls={
                            "Mouse": "Click and drag",
                            "Keyboard": "Arrow keys to move"
                        }
                    )

                    db.session.add(new_game)
                    db.session.commit()

                    imported_count += 1
                    print(f"Imported [{i}/{total_games}]: {title}")

                except Exception as e:
                    db.session.rollback()
                    error_count += 1
                    print(f"Error importing game {i} ('{title if 'title' in locals() else 'Unknown'}'): {e}")
                    continue

            print(f"\nImport completed!")
            print(f"Total processed: {total_games}")
            print(f"Successfully imported: {imported_count}")
            print(f"Skipped: {skipped_count}")
            print(f"Errors: {error_count}")

            return imported_count, skipped_count, error_count

        except Exception as e:
            print(f"Fatal error during import: {e}")
            return 0, 0, 1

if __name__ == '__main__':
    json_file = 'games_data.json'
    print(f"Starting import from {json_file}...")

    imported, skipped, errors = import_games_from_json(json_file)

    if imported > 0:
        print(f"\n✅ Successfully imported {imported} games!")
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} games")
    if errors > 0:
        print(f"❌ {errors} errors occurred")