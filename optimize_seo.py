#!/usr/bin/env python3
import json
import os
import re
from bs4 import BeautifulSoup

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
        title_tag.string = "BTW Games - Free Online Games | Play 50+ Browser Games Instantly"

    # Update meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        meta_desc['content'] = "Play 50+ free online games at BTW Games! Enjoy action, puzzle, racing, and strategy games instantly in your browser. No downloads required."

    # Update meta keywords
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if meta_keywords:
        meta_keywords['content'] = "free online games, browser games, action games, puzzle games, racing games, strategy games, no download games, instant play games, BTW Games"

    # Update Open Graph tags
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    if og_title:
        og_title['content'] = "BTW Games - Free Online Games Collection"

    og_desc = soup.find('meta', attrs={'property': 'og:description'})
    if og_desc:
        og_desc['content'] = "Play 50+ free online games instantly! Action, puzzle, racing, strategy games and more. No downloads needed."

    # Add structured data for website
    structured_data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "BTW Games",
        "url": "https://btwgame.com",
        "description": "Free online games platform with 50+ browser games",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "https://btwgame.com/games.html?search={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    }

    # Add JSON-LD script
    script_tag = soup.new_tag('script', type='application/ld+json')
    script_tag.string = json.dumps(structured_data, indent=2)
    soup.head.append(script_tag)

    # Add canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if not canonical:
        canonical = soup.new_tag('link', rel='canonical', href='https://btwgame.com/')
        soup.head.append(canonical)

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
        title_tag.string = "All Games - BTW Games | 50+ Free Online Browser Games"

    # Add meta description if not exists
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if not meta_desc:
        meta_desc = soup.new_tag('meta', name='description')
        soup.head.append(meta_desc)
    meta_desc['content'] = "Browse all 50+ free online games at BTW Games. Find action, puzzle, racing, and strategy games. Play instantly in your browser with no downloads."

    # Add meta keywords if not exists
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if not meta_keywords:
        meta_keywords = soup.new_tag('meta', name='keywords')
        soup.head.append(meta_keywords)
    meta_keywords['content'] = "all games, free online games, browser games, game collection, BTW Games"

    # Add canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if not canonical:
        canonical = soup.new_tag('link', rel='canonical', href='https://btwgame.com/games.html')
        soup.head.append(canonical)

    with open('static_html/games.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print("✅ games.html optimized")

def optimize_game_pages():
    """Optimize individual game pages"""
    print("🔧 Optimizing individual game pages...")

    # Load games data
    with open('static_html/all_games.json', 'r', encoding='utf-8') as f:
        games = json.load(f)

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
            title_tag.string = f"Play {game['title']} Online Free - BTW Games"

        # Update meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = game.get('description', f"Play {game['title']} online for free at BTW Games.")
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
            description = game.get('description', f"Play {game['title']} online for free at BTW Games.")
            if len(description) > 160:
                description = description[:157] + "..."
            og_desc['content'] = description

        og_url = soup.find('meta', attrs={'property': 'og:url'})
        if og_url:
            og_url['content'] = f"https://btwgame.com/games/{game['slug']}.html"

        # Add structured data for game
        structured_data = {
            "@context": "https://schema.org",
            "@type": "Game",
            "name": game['title'],
            "description": game.get('description', f"Play {game['title']} online for free."),
            "url": f"https://btwgame.com/games/{game['slug']}.html",
            "genre": get_category_name(game.get('category_id', 7)),
            "gamePlatform": "Web Browser",
            "operatingSystem": "Any",
            "applicationCategory": "Game",
            "isAccessibleForFree": True,
            "publisher": {
                "@type": "Organization",
                "name": "BTW Games"
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
            canonical['href'] = f"https://btwgame.com/games/{game['slug']}.html"

        with open(game_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))

    print(f"✅ Optimized {len(games)} individual game pages")

def generate_xml_sitemap():
    """Generate XML sitemap for better SEO"""
    print("🔧 Generating XML sitemap...")

    # Load games data
    with open('static_html/all_games.json', 'r', encoding='utf-8') as f:
        games = json.load(f)

    # Create XML sitemap
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://btwgame.com/</loc>
        <lastmod>2025-01-20</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://btwgame.com/games.html</loc>
        <lastmod>2025-01-20</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
'''

    for game in games:
        xml_content += f'''    <url>
        <loc>https://btwgame.com/games/{game['slug']}.html</loc>
        <lastmod>2025-01-20</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
'''

    xml_content += '</urlset>'

    with open('static_html/sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(xml_content)

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
Allow: /games.html

# Block assets that don't need indexing
Disallow: /assets/js/
Disallow: /assets/css/
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

    # Change to project directory
    os.chdir('/Users/jiaoyang/Work/code/gamewebsite1')

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