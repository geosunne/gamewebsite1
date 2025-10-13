# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BTW Games is a Flask-based gaming platform that aggregates browser games. The project features a complete workflow: scraping games from onlinegames.io, storing them in a SQLite database, and generating static HTML pages for deployment.

## Architecture

This is a **dual-mode** project:

1. **Flask Backend** (Development/Dynamic)
   - Flask app with SQLAlchemy ORM and SQLite database
   - RESTful API endpoints for games, categories, and statistics
   - Admin interface for game management
   - Used during development and data management

2. **Static Site Generation** (Production)
   - Python scripts generate static HTML from database content
   - Static files deployed to `static_html/` directory
   - No backend required in production (pure HTML/CSS/JS)

## Key Components

### Backend (Flask)
- **app.py** - Flask application factory with blueprint registration
- **models.py** - SQLAlchemy models (Game, Category, GamePlay, GameStats)
- **routes/api.py** - Public API endpoints (/api/games, /api/categories, etc.)
- **routes/admin.py** - Admin API endpoints (requires API key)
- **Database**: SQLite at `instance/site.db`

### Build Pipeline
1. **analyze_onlinegames_structure.py** - Web scraper that extracts game data from onlinegames.io
2. **import_games_data.py** - Imports scraped JSON into SQLite database
3. **generate_static_pages.py** - Generates static HTML for all games
4. **optimize_seo.py** - Adds meta tags, Open Graph, and structured data
5. **update_sitemap.py** - Generates sitemap.xml and robots.txt

### Orchestration
- **build_website.py** - Master build script that runs entire pipeline
- **quick_build.sh** - Bash script for rapid rebuilds (default 50 games)

## Common Commands

### Development Server
```bash
# Start Flask development server
python run.py

# Server runs on http://0.0.0.0:5000
```

### Database Operations
```bash
# Initialize database tables
python init_db.py

# Seed database with sample data
python seed_data.py

# Import scraped game data
python import_games_data.py
```

### Build Workflow

**Complete build (scrape + import + generate):**
```bash
python build_website.py --max-games 100
```

**Quick rebuild using existing data:**
```bash
./quick_build.sh --skip-scraping
```

**Build with specific options:**
```bash
python build_website.py --skip-scraping --skip-seo --serve
```

**Step-by-step manual build:**
```bash
# 1. Scrape games (creates games_data.json)
python analyze_onlinegames_structure.py --max-games 100

# 2. Import to database
python import_games_data.py

# 3. Generate static files
python generate_static_pages.py

# 4. SEO optimization
python optimize_seo.py

# 5. Generate sitemap
python update_sitemap.py
```

### Static Site Serving
```bash
# Serve static_html directory
cd static_html && python -m http.server 8001
```

## Project Structure

```
gamewebsite1/
├── app.py                          # Flask app factory
├── models.py                       # Database models
├── routes/
│   ├── api.py                     # Public API
│   ├── admin.py                   # Admin API (protected)
│   └── main.py                    # Static file routes
├── static/                        # Frontend templates (source)
│   ├── index.html                # Homepage template
│   ├── games.html                # Games list template
│   ├── game.html                 # Game page template
│   └── assets/
│       ├── js/api.js             # API client
│       └── css/
├── static_html/                   # Generated static site (output)
│   ├── index.html
│   ├── games/
│   │   └── {slug}.html           # Individual game pages
│   ├── all_games.json
│   ├── sitemap.xml
│   └── robots.txt
├── instance/
│   └── site.db                    # SQLite database
├── build_website.py               # Master build orchestrator
├── analyze_onlinegames_structure.py  # Web scraper
├── import_games_data.py           # JSON → SQLite importer
├── generate_static_pages.py       # Static HTML generator
├── optimize_seo.py                # SEO optimizer
└── update_sitemap.py              # Sitemap generator
```

## Development Workflow

### Adding New Games
1. Run scraper: `python analyze_onlinegames_structure.py --max-games 200`
2. Import: `python import_games_data.py`
3. Regenerate static: `python generate_static_pages.py`

### Modifying Templates
1. Edit files in `static/` directory
2. Run: `./quick_build.sh --skip-scraping`
3. Test: Open `static_html/index.html`

### Testing Changes
```bash
# Quick test with Flask server
python run.py

# Test static build
./quick_build.sh --skip-scraping --serve
```

## Database Schema

- **categories**: Game categories (Action, Puzzle, Racing, etc.)
- **games**: Game metadata (title, slug, description, iframe_url, rating, etc.)
- **game_plays**: Play session tracking (IP, duration, timestamp)
- **game_stats**: Daily aggregated statistics

## Important Files

- **games_data.json** - Scraped game data (intermediate format)
- **game_slugs.txt** - List of all game slugs (for validation)
- **ads.txt** - Google AdSense configuration
- **.env** - Environment variables (SECRET_KEY, DATABASE_URL)

## Deployment

The project deploys as a static site:
1. Run full build: `python build_website.py --max-games 100`
2. Deploy contents of `static_html/` directory to static hosting (Vercel, Netlify, etc.)
3. No server-side code required in production

## Configuration

Environment variables (`.env`):
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection (default: sqlite:///btw_games.db)
- `FLASK_ENV` - Environment mode (development/production)
- `GOOGLE_ANALYTICS_ID` - Analytics tracking ID
- `GOOGLE_ADSENSE_CLIENT` - AdSense client ID

## Dependencies

Core dependencies (see requirements.txt):
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-Migrate** - Database migrations
- **Flask-Marshmallow** - Serialization
- **requests** - HTTP client
- **beautifulsoup4** - Web scraping
- **lxml** - HTML parsing
