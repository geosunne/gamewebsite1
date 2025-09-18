#!/usr/bin/env python3
"""
Generate static HTML pages for all games and update all_games.json
"""
import requests
import json
import os
import time
from urllib.parse import urljoin
from datetime import datetime

BASE_URL = "http://localhost:8000"

def fetch_game_data(slug):
    """Fetch game data from API"""
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

def fetch_related_games(category_name, exclude_slug, limit=6):
    """Fetch related games from the same category"""
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

    # Generate related games HTML
    related_games_html = ""
    if related_games:
        for related_game in related_games:
            related_thumbnail = related_game.get('thumbnail_url', '')
            related_games_html += f'''
                <div class="game-card" onclick="window.location.href='{related_game["slug"]}.html'">
                    <div class="game-thumbnail">
                        {f'<img src="{related_thumbnail}" alt="{related_game["title"]}" onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'flex\';">' if related_thumbnail else ''}
                        <div class="thumbnail-fallback" style="{'display:none;' if related_thumbnail else 'display: flex; align-items: center; justify-content: center;'} font-size: 42px; height: 100%; color: var(--apple-gray);">🎮</div>
                    </div>
                    <div class="game-info">
                        <h3 class="game-card-title">{related_game["title"]}</h3>
                        <p class="game-card-description">{related_game["description"]}</p>
                    </div>
                </div>
            '''

    # Generate features HTML
    features_html = ""
    if features:
        for feature in features:
            features_html += f'''
                        <li>
                            <div class="feature-icon">✓</div>
                            <span>{feature}</span>
                        </li>
            '''

    # Generate controls HTML
    controls_html = ""
    if controls:
        for key, description in controls.items():
            controls_html += f'''
                        <div class="control-item">
                            <span class="control-key">{key}</span>
                            <span>{description}</span>
                        </div>
            '''

    # Generate tags HTML
    tags_html = ""
    if tags:
        for tag in tags:
            tags_html += f'<span class="tag">{tag}</span>'

    # Format release date
    release_date_formatted = "Coming Soon"
    if release_date:
        try:
            from datetime import datetime
            date_obj = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
            release_date_formatted = date_obj.strftime('%B %d, %Y')
        except:
            release_date_formatted = release_date

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Play {title} free online at BTW Games. {description}">
    <meta name="keywords" content="free online game, browser game, BTW Games, {category_name}, {', '.join(tags)}">
    <meta name="author" content="BTW Games">
    <meta property="og:title" content="{title} | BTW Games">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{thumbnail_url or 'https://btwgame.com/images/game-og.jpg'}">
    <meta property="og:url" content="https://btwgame.com/games/{game_data['slug']}.html">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title} | BTW Games">
    <meta name="twitter:description" content="{description}">
    <link rel="canonical" href="https://btwgame.com/games/{game_data['slug']}.html">

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

    <title>{title} | BTW Games</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --apple-blue: #007AFF;
            --apple-gray: #8E8E93;
            --apple-light-gray: #F2F2F7;
            --apple-dark: #1C1C1E;
            --apple-white: #FFFFFF;
            --apple-green: #34C759;
            --apple-red: #FF3B30;
            --shadow-light: 0 2px 15px rgba(0, 0, 0, 0.1);
            --shadow-heavy: 0 10px 40px rgba(0, 0, 0, 0.15);
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--apple-dark);
            background: linear-gradient(180deg, var(--apple-white) 0%, var(--apple-light-gray) 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        header {{
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: var(--shadow-light);
        }}

        nav {{
            padding: 20px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            font-size: 24px;
            font-weight: 600;
            color: var(--apple-blue);
            text-decoration: none;
        }}

        .back-btn {{
            background: var(--apple-blue);
            color: var(--apple-white);
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 14px;
            transition: opacity 0.3s ease;
        }}

        .back-btn:hover {{
            opacity: 0.8;
        }}

        .game-header {{
            padding: 40px 0;
            text-align: center;
        }}

        .game-title {{
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 16px;
            color: var(--apple-dark);
        }}

        .game-subtitle {{
            font-size: 20px;
            color: var(--apple-gray);
            margin-bottom: 30px;
        }}

        .game-stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 30px;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-value {{
            font-size: 24px;
            font-weight: 600;
            color: var(--apple-blue);
        }}

        .stat-label {{
            font-size: 14px;
            color: var(--apple-gray);
            margin-top: 4px;
        }}

        .game-container {{
            background: var(--apple-white);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: var(--shadow-heavy);
            margin-bottom: 40px;
            position: relative;
        }}

        .game-wrapper {{
            position: relative;
            width: 100%;
            padding-bottom: 56.25%;
            height: 0;
            overflow: hidden;
        }}

        .game-iframe {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }}

        .loading-indicator {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 18px;
            color: var(--apple-gray);
        }}

        .game-content {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 40px;
            margin-bottom: 40px;
        }}

        .game-description {{
            background: var(--apple-white);
            padding: 30px;
            border-radius: 16px;
            box-shadow: var(--shadow-light);
        }}

        .game-sidebar {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}

        .info-card {{
            background: var(--apple-white);
            padding: 24px;
            border-radius: 16px;
            box-shadow: var(--shadow-light);
        }}

        .card-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 16px;
            color: var(--apple-dark);
        }}

        .features-list {{
            list-style: none;
            padding: 0;
        }}

        .features-list li {{
            padding: 8px 0;
            border-bottom: 1px solid var(--apple-light-gray);
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .features-list li:last-child {{
            border-bottom: none;
        }}

        .feature-icon {{
            width: 20px;
            height: 20px;
            background: var(--apple-blue);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--apple-white);
            font-size: 12px;
        }}

        .controls-grid {{
            display: grid;
            gap: 12px;
        }}

        .control-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: var(--apple-light-gray);
            border-radius: 8px;
        }}

        .control-key {{
            background: var(--apple-white);
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 12px;
            min-width: 60px;
            text-align: center;
        }}

        .game-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 16px;
        }}

        .tag {{
            background: var(--apple-light-gray);
            color: var(--apple-dark);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}

        .related-games {{
            margin-top: 60px;
        }}

        .section-title {{
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 30px;
            text-align: center;
            color: var(--apple-dark);
        }}

        .games-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 24px;
        }}

        .game-card {{
            background: var(--apple-white);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--shadow-light);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}

        .game-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-heavy);
        }}

        .game-thumbnail {{
            width: 100%;
            height: 140px;
            background: linear-gradient(135deg, var(--apple-light-gray), #E5E5EA);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 42px;
            position: relative;
        }}

        .game-thumbnail img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .game-info {{
            padding: 16px;
        }}

        .game-card-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--apple-dark);
        }}

        .game-card-description {{
            color: var(--apple-gray);
            font-size: 13px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        footer {{
            background: var(--apple-dark);
            color: var(--apple-white);
            padding: 40px 0;
            text-align: center;
            margin-top: 80px;
        }}

        @media (max-width: 768px) {{
            .game-content {{
                grid-template-columns: 1fr;
                gap: 24px;
            }}

            .game-stats {{
                gap: 20px;
            }}

            .game-title {{
                font-size: 32px;
            }}

            .games-grid {{
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 16px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <nav class="container">
            <a href="../index.html" class="logo">BTW Games</a>
            <a href="../index.html" class="back-btn">← Back to Games</a>
        </nav>
    </header>

    <main class="container">
        <section class="game-header">
            <h1 class="game-title">{title}</h1>
            <p class="game-subtitle">{description}</p>

            <div class="game-stats">
                <div class="stat-item">
                    <div class="stat-value">⭐ {rating:.1f}</div>
                    <div class="stat-label">Rating</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">👥 {total_plays:,}</div>
                    <div class="stat-label">Total Plays</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">🎯 {category_name}</div>
                    <div class="stat-label">Category</div>
                </div>
            </div>
        </section>

        {'<section class="game-container" id="gameContainer">' if iframe_url else ''}
            {'<div class="game-wrapper">' if iframe_url else ''}
                {'<div class="loading-indicator">Loading game...</div>' if iframe_url else ''}
                {f'<iframe id="gameIframe" class="game-iframe" src="{iframe_url}" title="{title}" allowfullscreen loading="lazy" onload="this.previousElementSibling.style.display=\'none\'"></iframe>' if iframe_url else ''}
            {'</div>' if iframe_url else ''}
        {'</section>' if iframe_url else ''}

        <section class="game-content">
            <div class="game-description">
                <h2 class="card-title">About This Game</h2>
                <div>
                    <p>{long_description}</p>
                    <p style="margin-top: 16px; color: var(--apple-gray); font-size: 14px;">
                        Release Date: {release_date_formatted}
                    </p>
                </div>
                {f'<div class="game-tags">{tags_html}</div>' if tags_html else ''}
            </div>

            <div class="game-sidebar">
                {f'<div class="info-card"><h3 class="card-title">Game Features</h3><ul class="features-list">{features_html}</ul></div>' if features_html else ''}
                {f'<div class="info-card"><h3 class="card-title">Controls</h3><div class="controls-grid">{controls_html}</div></div>' if controls_html else ''}
            </div>
        </section>

        {f'<section class="related-games"><h2 class="section-title">More Games You Might Like</h2><div class="games-grid">{related_games_html}</div></section>' if related_games_html else ''}
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 BTW Games. All rights reserved.</p>
        </div>
    </footer>

    <script>
        // Track game view when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            // Track with Google Analytics
            if (typeof gtag !== 'undefined') {{
                gtag('event', 'game_view', {{
                    'game_name': '{title}',
                    'game_category': '{category_name}'
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
                "website": "BTW Games",
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

def main():
    """Generate all static game pages and update all_games.json"""

    print("🚀 Generating static game pages and updating all_games.json...")

    # Read game slugs
    try:
        with open('static_html/game_slugs.txt', 'r') as f:
            game_slugs = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ game_slugs.txt not found. Run the curl command first.")
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

            # Save to file
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