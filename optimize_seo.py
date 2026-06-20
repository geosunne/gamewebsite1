#!/usr/bin/env python3
import json
import os
import re
from datetime import date
from bs4 import BeautifulSoup
from xml.sax.saxutils import escape

def get_category_name(category_id):
    """Get category name by ID"""
    categories = {
        1: "Action",
        2: "Puzzle",
        3: "Racing",
        4: "Strategy",
        5: "Adventure",
        6: "Sports",
        7: "Casual"
    }
    return categories.get(category_id, "Games")

def optimize_index_html():
    """Optimize main index.html file"""
    print("🔧 Optimizing index.html...")

    with open('static_html/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Update title
    title_tag = soup.find('title')
    if title_tag:
        title_tag.string = "BTW game - Free Online Games for Quick Breaks"

    # Update meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        meta_desc['content'] = "Play 500+ free online games at BTW game. Fast browser games for quick breaks, with action, puzzle, racing, sports, and casual games."

    # Update meta keywords
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if meta_keywords:
        meta_keywords['content'] = "free online games, browser games, action games, puzzle games, racing games, strategy games, no download games, instant play games, BTW game"

    # Update Open Graph tags
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    if og_title:
        og_title['content'] = "BTW game - Free Online Games for Quick Breaks"

    og_desc = soup.find('meta', attrs={'property': 'og:description'})
    if og_desc:
        og_desc['content'] = "Play 500+ free online games instantly at BTW game. No downloads, no accounts, just quick browser play."

    og_url = soup.find('meta', attrs={'property': 'og:url'})
    if og_url:
        og_url['content'] = "https://btwgame.com/"

    twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
    if twitter_title:
        twitter_title['content'] = "BTW game - Free Online Games for Quick Breaks"

    twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
    if twitter_desc:
        twitter_desc['content'] = "Play 500+ free online games instantly at BTW game. No downloads, no accounts, just quick browser play."

    # Add structured data for website
    structured_data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "BTW game",
        "url": "https://btwgame.com/",
        "description": "Free online games platform with 500+ quick browser games",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "https://btwgame.com/games?search={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    }

    # Replace existing WebSite JSON-LD so repeated optimization runs stay idempotent.
    for existing_script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(existing_script.string or '{}')
        except json.JSONDecodeError:
            continue
        if data.get('@type') == 'WebSite':
            existing_script.extract()

    # Add JSON-LD script
    script_tag = soup.new_tag('script', type='application/ld+json')
    script_tag.string = json.dumps(structured_data, indent=2)
    soup.head.append(script_tag)

    # Add canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if not canonical:
        canonical = soup.new_tag('link', rel='canonical', href='https://btwgame.com/')
        soup.head.append(canonical)
    else:
        canonical['href'] = 'https://btwgame.com/'

    with open('static_html/index.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print("✅ index.html optimized")

def optimize_games_html():
    """Optimize games.html file"""
    print("🔧 Optimizing games.html...")

    with open('static_html/games.html', 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Update title
    title_tag = soup.find('title')
    if title_tag:
        title_tag.string = "All Games | BTW game"

    # Add meta description if not exists
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if not meta_desc:
        meta_desc = soup.new_tag('meta', name='description')
        soup.head.append(meta_desc)
    meta_desc['content'] = "Browse all 500+ free online games at BTW game. Find action, puzzle, racing, sports, and casual games that play instantly in your browser."

    # Add meta keywords if not exists
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if not meta_keywords:
        meta_keywords = soup.new_tag('meta', name='keywords')
        soup.head.append(meta_keywords)
    meta_keywords['content'] = "all games, free online games, browser games, game collection, BTW game"

    # Add canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if not canonical:
        canonical = soup.new_tag('link', rel='canonical', href='https://btwgame.com/games')
        soup.head.append(canonical)
    else:
        canonical['href'] = 'https://btwgame.com/games'

    with open('static_html/games.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print("✅ games.html optimized")

def optimize_game_pages():
    """Optimize individual game pages"""
    print("🔧 Optimizing individual game pages...")

    # Load games data
    with open('static_html/all_games.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract games array from the data structure
    games = data.get('games', []) if isinstance(data, dict) else data

    for game in games:
        game_file = f"static_html/games/{game['slug']}.html"
        if not os.path.exists(game_file):
            continue

        with open(game_file, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Update title
        title_tag = soup.find('title')
        if title_tag:
            title_tag.string = f"Play {game['title']} Online Free - BTW game"

        # Update meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = game.get('description', f"Play {game['title']} online for free at BTW game.")
            # Limit description to 160 characters for SEO
            if len(description) > 160:
                description = description[:157] + "..."
            meta_desc['content'] = description

        # Update meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            category_name = get_category_name(game.get('category_id', 7))
            tags = game.get('tags', [])
            keywords = [game['title'], f"play {game['title']}", "free online game", category_name.lower() + " game"]
            keywords.extend([tag.lower() for tag in tags[:3]])  # Add first 3 tags
            meta_keywords['content'] = ", ".join(keywords)

        # Update Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            og_title['content'] = f"Play {game['title']} Online Free"

        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc:
            description = game.get('description', f"Play {game['title']} online for free at BTW game.")
            if len(description) > 160:
                description = description[:157] + "..."
            og_desc['content'] = description

        og_url = soup.find('meta', attrs={'property': 'og:url'})
        if og_url:
            og_url['content'] = f"https://btwgame.com/games/{game['slug']}"

        # Add structured data for game
        structured_data = {
            "@context": "https://schema.org",
            "@type": "Game",
            "name": game['title'],
            "description": game.get('description', f"Play {game['title']} online for free."),
            "url": f"https://btwgame.com/games/{game['slug']}",
            "genre": get_category_name(game.get('category_id', 7)),
            "gamePlatform": "Web Browser",
            "operatingSystem": "Any",
            "applicationCategory": "Game",
            "isAccessibleForFree": True,
            "publisher": {
                "@type": "Organization",
                "name": "BTW game"
            }
        }

        if game.get('rating'):
            structured_data["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": game['rating'],
                "bestRating": 5,
                "worstRating": 1
            }

        # Add JSON-LD script
        existing_script = soup.find('script', type='application/ld+json')
        if existing_script:
            existing_script.extract()

        script_tag = soup.new_tag('script', type='application/ld+json')
        script_tag.string = json.dumps(structured_data, indent=2)
        soup.head.append(script_tag)

        # Update canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            canonical['href'] = f"https://btwgame.com/games/{game['slug']}"

        with open(game_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))

    print(f"✅ Optimized {len(games)} individual game pages")

def generate_xml_sitemap():
    """Generate XML sitemap for better SEO"""
    print("🔧 Generating XML sitemap...")

    # Load games data
    with open('static_html/all_games.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract games array from the data structure
    games = data.get('games', []) if isinstance(data, dict) else data

    today = date.today().isoformat()
    urls = ['https://btwgame.com/', 'https://btwgame.com/games']
    urls.extend(f"https://btwgame.com/games/{game['slug']}" for game in games)

    with open('static_html/sitemap.xml', 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for index, url in enumerate(urls):
            priority = '1.0' if index == 0 else '0.9' if index == 1 else '0.8'
            changefreq = 'daily' if index < 2 else 'weekly'
            f.write('    <url>\n')
            f.write(f'        <loc>{escape(url)}</loc>\n')
            f.write(f'        <lastmod>{today}</lastmod>\n')
            f.write(f'        <changefreq>{changefreq}</changefreq>\n')
            f.write(f'        <priority>{priority}</priority>\n')
            f.write('    </url>\n')
        f.write('</urlset>\n')

    print("✅ XML sitemap generated")

def optimize_robots_txt():
    """Optimize robots.txt for better crawling"""
    print("🔧 Optimizing robots.txt...")

    robots_content = '''User-agent: *
Allow: /

# Sitemap
Sitemap: https://btwgame.com/sitemap.xml
Sitemap: https://btwgame.com/sitemap.txt

# Allow indexing of all game pages
Allow: /games/
Allow: /games

# Allow render assets for search engines
Allow: /assets/js/
Allow: /assets/css/
Disallow: /*.json$

# Allow common search engine bots
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Slurp
Allow: /
'''

    with open('static_html/robots.txt', 'w', encoding='utf-8') as f:
        f.write(robots_content)

    print("✅ robots.txt optimized")

def main():
    print("🚀 Starting SEO optimization...")

    # Run all optimizations
    optimize_index_html()
    optimize_games_html()
    optimize_game_pages()
    generate_xml_sitemap()
    optimize_robots_txt()

    print("\n🎯 SEO optimization complete!")
    print("Optimized features:")
    print("  ✅ Updated meta titles and descriptions")
    print("  ✅ Enhanced Open Graph tags")
    print("  ✅ Added structured data (JSON-LD)")
    print("  ✅ Optimized canonical URLs")
    print("  ✅ Generated XML sitemap")
    print("  ✅ Enhanced robots.txt")
    print("  ✅ Improved meta keywords")

if __name__ == "__main__":
    main()
