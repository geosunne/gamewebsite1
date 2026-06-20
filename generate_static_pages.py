#!/usr/bin/env python3
"""
Generate static HTML pages for all games and update all_games.json
"""
import requests
import json
import os
import time
from html import escape as html_escape
from urllib.parse import quote, urljoin
from datetime import datetime

BASE_URL = "http://localhost:8000"

def fetch_game_data_from_db(slug):
    """Fetch game data directly from database"""
    try:
        from app import create_app, db
        from models import Game, game_schema

        app = create_app()
        with app.app_context():
            game = Game.query.filter_by(slug=slug, is_active=True).first()
            if game:
                return game_schema.dump(game)
            return None
    except Exception as e:
        print(f"❌ Database error for {slug}: {e}")
        return None

def fetch_game_data(slug):
    """Fetch game data from database first, fallback to API"""
    # Try database first
    game_data = fetch_game_data_from_db(slug)
    if game_data:
        return game_data

    # Fallback to API if database fails
    try:
        response = requests.get(f"{BASE_URL}/api/games/slug/{slug}")
        if response.status_code == 200:
            return response.json()['game']
        else:
            print(f"Error fetching {slug}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {slug}: {e}")
        return None

def fetch_related_games_from_db(category_name, exclude_slug, limit=6):
    """Fetch related games from database"""
    try:
        from app import create_app, db
        from models import Game, Category, games_schema

        app = create_app()
        with app.app_context():
            # Find category
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                return []

            # Get related games
            games = Game.query.filter(
                Game.category_id == category.id,
                Game.slug != exclude_slug,
                Game.is_active == True
            ).order_by(Game.total_plays.desc()).limit(limit).all()

            return games_schema.dump(games)
    except Exception as e:
        print(f"❌ Database error fetching related games: {e}")
        return []

def fetch_related_games(category_name, exclude_slug, limit=6):
    """Fetch related games from database first, fallback to API"""
    # Try database first
    related = fetch_related_games_from_db(category_name, exclude_slug, limit)
    if related:
        return related

    # Fallback to API
    try:
        response = requests.get(f"{BASE_URL}/api/games", params={
            'category': category_name,
            'per_page': limit + 1  # Get one extra to exclude current game
        })
        if response.status_code == 200:
            games = response.json()['games']
            # Exclude current game and limit results
            related = [g for g in games if g['slug'] != exclude_slug][:limit]
            return related
        else:
            return []
    except Exception as e:
        print(f"Error fetching related games: {e}")
        return []

def standardize_game_tags(game_data):
    """Generate standardized tags based on game data"""
    title = game_data.get('title', '').lower()
    description = game_data.get('description', '').lower()
    category_name = game_data.get('category_name', '').lower()
    iframe_url = game_data.get('iframe_url', '') or game_data.get('game_url', '')

    tags = []

    # Platform tags based on iframe URL
    if 'gamedistribution.com' in iframe_url or 'html5' in iframe_url.lower():
        tags.append('HTML5')
    elif 'unity' in iframe_url.lower():
        tags.append('Unity')
    elif iframe_url and 'html5' not in iframe_url.lower() and 'unity' not in iframe_url.lower():
        tags.append('HTML5')  # Default for browser games

    # Genre tags based on title, description, and category
    genre_keywords = {
        'Action': ['action', 'fight', 'combat', 'battle', 'war', 'shoot', 'gun', 'zombie', 'adventure'],
        'Strategy': ['strategy', 'tower defense', 'defense', 'build', 'manage', 'city', 'empire'],
        'Puzzle': ['puzzle', 'brain', 'logic', 'solve', 'match', 'tetris', 'block'],
        'Racing': ['race', 'racing', 'car', 'drive', 'speed', 'drift', 'bike', 'motorcycle'],
        'Sports': ['sport', 'football', 'soccer', 'basketball', 'tennis', 'golf', 'baseball'],
        'Arcade': ['arcade', 'classic', 'retro', 'pixel', 'old school'],
        'Platform': ['platform', 'jump', 'run', 'climb', 'parkour'],
        'Simulation': ['simulation', 'sim', 'life', 'city', 'farm', 'cooking', 'restaurant'],
        'RPG': ['rpg', 'role', 'character', 'level up', 'quest', 'adventure'],
        'Casual': ['casual', 'relaxing', 'simple', 'easy', 'family'],
        'Multiplayer': ['multiplayer', 'online', 'vs', 'versus', 'pvp', 'co-op'],
        'Clicker': ['clicker', 'click', 'idle', 'incremental', 'tap'],
        'Educational': ['educational', 'learn', 'math', 'quiz', 'knowledge'],
        'Horror': ['horror', 'scary', 'fear', 'nightmare', 'ghost', 'monster'],
        'Rhythm': ['rhythm', 'music', 'beat', 'dance', 'sound'],
        'Card': ['card', 'poker', 'blackjack', 'solitaire', 'deck']
    }

    content_text = f"{title} {description} {category_name}"

    for genre, keywords in genre_keywords.items():
        if any(keyword in content_text for keyword in keywords):
            tags.append(genre)

    # Special game type tags
    if any(word in content_text for word in ['io', '.io']):
        tags.append('IO Game')

    if any(word in content_text for word in ['3d', 'three dimensional']):
        tags.append('3D')

    if any(word in content_text for word in ['2d', 'two dimensional', 'pixel']):
        tags.append('2D')

    # Remove duplicates and ensure we have at least some basic tags
    tags = list(dict.fromkeys(tags))  # Remove duplicates while preserving order

    # Ensure every game has at least HTML5 and one genre tag
    if not any(tag in ['HTML5', 'Unity'] for tag in tags):
        tags.insert(0, 'HTML5')

    if not any(tag in genre_keywords.keys() for tag in tags):
        if 'game' in content_text:
            tags.append('Casual')
        else:
            tags.append('Action')

    return tags[:6]  # Limit to 6 tags maximum

def generate_game_page(game_data, related_games):
    """Generate static HTML for a game page"""

    # Basic game information
    title = game_data.get('title', 'Unknown Game')
    description = game_data.get('description', '')
    long_description = game_data.get('long_description', description)
    thumbnail_url = game_data.get('thumbnail_url', '')
    iframe_url = game_data.get('iframe_url') or game_data.get('game_url', '')
    category_name = game_data.get('category_name', 'General')
    rating = game_data.get('rating', 0)
    total_plays = game_data.get('total_plays', 0)
    tags = standardize_game_tags(game_data)  # Use standardized tags instead of API tags
    features = game_data.get('features', [])
    controls = game_data.get('controls', {})
    release_date = game_data.get('release_date', '')
    slug = game_data.get('slug', '')
    title_html = html_escape(title)
    description_html = html_escape(description)
    long_description_html = html_escape(long_description)
    category_html = html_escape(category_name)
    title_attr = html_escape(title, quote=True)
    description_attr = html_escape(description, quote=True)
    category_param = quote(category_name)
    slug_attr = html_escape(slug, quote=True)
    iframe_attr = html_escape(iframe_url, quote=True)
    thumbnail_attr = html_escape(thumbnail_url, quote=True)

    # Generate related games HTML
    related_games_html = ""
    if related_games:
        for related_game in related_games:
            related_thumbnail = related_game.get('thumbnail_url', '')
            related_slug = html_escape(related_game.get('slug', ''))
            related_title = html_escape(related_game.get('title', ''))
            related_description = html_escape(related_game.get('description', ''))
            related_fallback = ''.join(word[0] for word in related_title.split()[:2]).upper() or '▶'
            related_img = ''
            if related_thumbnail:
                escaped_thumbnail = html_escape(related_thumbnail, quote=True)
                related_img = f'<img src="{escaped_thumbnail}" alt="{related_title}" loading="lazy" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'grid\';">'
            related_games_html += f'''
                <a class="game-card wide" href="/games/{related_slug}">
                    <div class="game-thumbnail">
                        {related_img}
                        <div class="thumbnail-fallback" style="{'display:none;' if related_thumbnail else ''}">{related_fallback}</div>
                        <div class="game-info">
                            <h3 class="game-title">{related_title}</h3>
                        </div>
                    </div>
                </a>
            '''

    # Generate features HTML
    features_html = ""
    if features:
        for feature in features:
            features_html += f'''
                        <li>
                            <div class="feature-icon">✓</div>
                            <span>{html_escape(str(feature))}</span>
                        </li>
            '''

    # Generate controls HTML
    controls_html = ""
    if controls:
        for key, description in controls.items():
            controls_html += f'''
                        <div class="control-item">
                            <span class="control-key">{html_escape(str(key))}</span>
                            <span>{html_escape(str(description))}</span>
                        </div>
            '''

    # Generate tags HTML
    tags_html = ""
    if tags:
        for tag in tags:
            tags_html += f'<span class="tag">{html_escape(str(tag))}</span>'

    # Format release date
    release_date_formatted = "Coming Soon"
    if release_date:
        try:
            from datetime import datetime
            date_obj = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
            release_date_formatted = date_obj.strftime('%B %d, %Y')
        except:
            release_date_formatted = release_date

    game_embed_html = ""
    if iframe_url:
        game_embed_html = f'''
        <section class="game-container" id="gameContainer">
            <div class="game-wrapper">
                <div class="loading-indicator">Loading game...</div>
                <iframe id="gameIframe" class="game-iframe" src="{iframe_attr}" title="{title_html}" allowfullscreen loading="lazy" onload="this.previousElementSibling.style.display='none'"></iframe>
            </div>
        </section>'''

    tags_section_html = f'<div class="game-tags">{tags_html}</div>' if tags_html else ''
    features_card_html = f'<div class="info-card"><h3 class="card-title">Game Features</h3><ul class="features-list">{features_html}</ul></div>' if features_html else ''
    controls_card_html = f'<div class="info-card"><h3 class="card-title">Controls</h3><div class="controls-grid">{controls_html}</div></div>' if controls_html else ''
    related_section_html = f'''
                <section class="related-games">
                    <div class="section-header">
                        <div>
                            <h2 class="section-title">More games to try</h2>
                            <p class="section-note">Games from the same shelf as {title_html}.</p>
                        </div>
                        <a href="/games" class="view-all-btn">View all games</a>
                    </div>
                    <div class="games-grid compact">{related_games_html}</div>
                </section>''' if related_games_html else ''

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Play {title_attr} free online at BTW game. {description_attr}">
    <meta name="keywords" content="free online game, browser game, BTW game, {category_html}, {', '.join(html_escape(str(tag)) for tag in tags)}">
    <meta name="author" content="BTW game">
    <meta property="og:title" content="{title_attr} | BTW game">
    <meta property="og:description" content="{description_attr}">
    <meta property="og:image" content="{thumbnail_attr or 'https://btwgame.com/images/game-og.jpg'}">
    <meta property="og:url" content="https://btwgame.com/games/{slug_attr}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title_attr} | BTW game">
    <meta name="twitter:description" content="{description_attr}">
    <link rel="canonical" href="https://btwgame.com/games/{slug_attr}">
    <link rel="stylesheet" href="/assets/css/site.css">

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-SM7PBYVK97"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() {{ dataLayer.push(arguments); }}
        gtag('js', new Date());
        gtag('config', 'G-SM7PBYVK97');
    </script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8930741225505243"
         crossorigin="anonymous"></script>

    <title>{title_html} | BTW game</title>
</head>
<body>
    <header class="site-header">
        <nav class="site-nav container" aria-label="Primary navigation">
            <a href="/" class="brand-mark" aria-label="BTW game home">
                <span class="brand-icon">▶</span>
                <span class="brand-word">BTW game <span class="brand-tagline">By the way, play</span></span>
            </a>
            <div class="nav-search" role="search">
                <form onsubmit="event.preventDefault(); navSearchGames();">
                    <input type="search" class="search-bar" placeholder="Search games..." id="navSearchInput" autocomplete="off">
                    <button class="search-btn compact" type="submit">Search</button>
                </form>
            </div>
            <button class="mobile-menu" type="button" onclick="toggleMenu()" aria-label="Open navigation" aria-controls="navLinks">
                <span></span>
                <span></span>
                <span></span>
            </button>
            <ul class="nav-links" id="navLinks">
                <li><a href="/">Home</a></li>
                <li><a href="/games">All games</a></li>
                <li><a href="/games?filter=new">New</a></li>
                <li><a href="/games?filter=featured">Featured</a></li>
            </ul>
        </nav>
    </header>

    <main class="container">
        <div class="app-layout">
            <aside class="side-rail" aria-label="Game navigation">
                <section class="rail-panel">
                    <h2 class="rail-title">Explore</h2>
                    <ul class="rail-links">
                        <li><a href="/"><span class="rail-icon">⌂</span>Home</a></li>
                        <li><a href="/games"><span class="rail-icon">▦</span>All games</a></li>
                        <li><a href="/games?filter=new"><span class="rail-icon">✦</span>New games</a></li>
                        <li><a href="/games?filter=featured"><span class="rail-icon">★</span>Featured</a></li>
                    </ul>
                </section>
                <section class="rail-panel">
                    <h2 class="rail-title">Category</h2>
                    <ul class="rail-links">
                        <li><a href="/games?category={category_param}" aria-current="page"><span class="rail-icon">●</span>{category_html}</a></li>
                        <li><a href="/games?category=Action"><span class="rail-icon">✹</span>Action</a></li>
                        <li><a href="/games?category=Racing"><span class="rail-icon">⚑</span>Racing</a></li>
                        <li><a href="/games?category=Puzzle"><span class="rail-icon">✚</span>Puzzle</a></li>
                    </ul>
                </section>
                <section class="trust-card">
                    <strong>Instant play</strong>
                    <span>No account setup. Click play and keep the break moving.</span>
                </section>
            </aside>

            <div>
                <section class="game-detail-header">
                    <span class="kicker">{category_html}</span>
                    <h1 class="game-detail-title">{title_html}</h1>
                    <p class="game-detail-subtitle">{description_html}</p>
                    <div class="game-meta-row" aria-label="Game details">
                        <span class="meta-pill">Rating {rating:.1f}</span>
                        <span class="meta-pill">{total_plays:,} plays</span>
                        <span class="meta-pill">{category_html}</span>
                    </div>
                    <div class="game-action-row">
                        <a class="button-primary" href="#gameContainer">Play now</a>
                        <a class="button-secondary" href="/games?category={category_param}">More {category_html} games</a>
                    </div>
                </section>

                <div class="game-shell">
                    <div>
                        {game_embed_html}
                        <section class="play-proof" aria-label="Why play on BTW game">
                            <div class="proof-item"><span class="proof-icon">⚡</span><span><strong>Instant play</strong><span>Start in your browser</span></span></div>
                            <div class="proof-item"><span class="proof-icon">✓</span><span><strong>No downloads</strong><span>Nothing to install</span></span></div>
                            <div class="proof-item"><span class="proof-icon">★</span><span><strong>Always free</strong><span>No hidden costs</span></span></div>
                            <div class="proof-item"><span class="proof-icon">☻</span><span><strong>Friendly browsing</strong><span>Built for quick breaks</span></span></div>
                        </section>

                        <section class="game-content">
                            <div class="game-description-panel">
                                <h2 class="card-title">About {title_html}</h2>
                                <p>{long_description_html}</p>
                                <p class="release-note">Release Date: {html_escape(str(release_date_formatted))}</p>
                                {tags_section_html}
                            </div>
                        </section>
                    </div>

                    <aside class="game-sidebar" aria-label="Game help">
                        {features_card_html}
                        {controls_card_html}
                        <div class="info-card">
                            <h2 class="card-title">Game info</h2>
                            <div class="controls-grid">
                                <div class="control-item"><span>Category</span><span class="control-key">{category_html}</span></div>
                                <div class="control-item"><span>Plays</span><span class="control-key">{total_plays:,}</span></div>
                                <div class="control-item"><span>Rating</span><span class="control-key">{rating:.1f}</span></div>
                            </div>
                        </div>
                    </aside>
                </div>

                {related_section_html}
            </div>
        </div>
    </main>

    <footer class="site-footer">
        <div class="footer-content container">
            <p>&copy; 2026 BTW game. All rights reserved.</p>
            <ul class="footer-links">
                <li><a href="/">Home</a></li>
                <li><a href="/games">All games</a></li>
                <li><a href="/games?filter=new">New games</a></li>
            </ul>
        </div>
    </footer>

    <script>
        function toggleMenu() {{
            document.getElementById('navLinks').classList.toggle('active');
        }}

        function navSearchGames() {{
            const query = document.getElementById('navSearchInput').value.trim();
            window.location.href = query ? `/games?search=${{encodeURIComponent(query)}}` : '/games';
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof gtag !== 'undefined') {{
                gtag('event', 'game_view', {{
                    'game_name': '{title_attr}',
                    'game_category': '{category_html}'
                }});
            }}
        }});
    </script>
</body>
</html>'''

    return html_content

def save_all_games_json(all_games_data):
    """Save all games data to static_html/all_games.json"""
    try:
        games_json_data = {
            "metadata": {
                "total_games": len(all_games_data),
                "generated_at": datetime.now().isoformat(),
                "website": "BTW game",
                "api_base_url": BASE_URL
            },
            "games": all_games_data
        }

        with open('static_html/all_games.json', 'w', encoding='utf-8') as f:
            json.dump(games_json_data, f, indent=2, ensure_ascii=False)

        print(f"📊 Updated static_html/all_games.json with {len(all_games_data)} games")
        return True
    except Exception as e:
        print(f"❌ Error saving all_games.json: {e}")
        return False

def fetch_all_games_from_db():
    """Fetch all game slugs directly from database"""
    try:
        from app import create_app, db
        from models import Game

        app = create_app()
        with app.app_context():
            games = Game.query.filter_by(is_active=True).all()
            slugs = [game.slug for game in games]
            print(f"📊 Fetched {len(slugs)} games from database")
            return slugs
    except Exception as e:
        print(f"❌ Error fetching from database: {e}")
        return None

def main():
    """Generate all static game pages and update all_games.json"""

    print("🚀 Generating static game pages and updating all_games.json...")

    # Try to get game slugs from database first
    game_slugs = fetch_all_games_from_db()

    # Fallback to game_slugs.txt if database fetch fails
    if not game_slugs:
        print("⚠️  Database fetch failed, trying game_slugs.txt...")
        try:
            with open('static_html/game_slugs.txt', 'r') as f:
                game_slugs = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("❌ game_slugs.txt not found and database fetch failed!")
            print("💡 Make sure the database is set up or game_slugs.txt exists")
            return

    print(f"📋 Found {len(game_slugs)} games to process")

    # Create games directory
    os.makedirs('static_html/games', exist_ok=True)

    success_count = 0
    error_count = 0
    all_games_data = []

    for slug in game_slugs:
        print(f"📄 Processing {slug}...")

        # Fetch game data
        game_data = fetch_game_data(slug)
        if not game_data:
            error_count += 1
            continue

        # Add to all games collection with standardized tags
        game_data_with_tags = game_data.copy()
        game_data_with_tags['standardized_tags'] = standardize_game_tags(game_data)
        all_games_data.append(game_data_with_tags)

        # Fetch related games
        related_games = fetch_related_games(
            game_data.get('category_name', ''),
            slug,
            limit=6
        )

        # Generate HTML
        try:
            html_content = generate_game_page(game_data, related_games)

            # Keep files flat so Cloudflare Clean URLs serve /games/{slug}
            # without canonicalizing to /games/{slug}/.
            filename = f"static_html/games/{slug}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)

            success_count += 1
            print(f"✅ Generated {filename}")

        except Exception as e:
            print(f"❌ Error generating page for {slug}: {e}")
            error_count += 1

    # Save all games data to JSON
    if all_games_data:
        save_all_games_json(all_games_data)

    print(f"\n🎯 Generation complete!")
    print(f"✅ Success: {success_count} pages")
    print(f"❌ Errors: {error_count} pages")
    print(f"📁 Pages saved in: static_html/games/")
    print(f"📊 Games data saved in: static_html/all_games.json")

if __name__ == "__main__":
    main()
