#!/usr/bin/env python3
"""
OnlineGames.io Game Iframe Extractor
This script extracts all game iframe addresses from the OnlineGames.io website
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse
import re
from collections import defaultdict, Counter

class GameIframeExtractor:
    def __init__(self, base_url="https://www.onlinegames.io"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.visited_urls = set()
        self.game_data = {
            'games': [],
            'iframe_sources': set(),
            'total_games': 0
        }
    
    def get_page_content(self, url):
        """Fetch page content with error handling"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def debug_find_recently_section(self):
        """Debug function to help identify the correct selector for 'section recently'"""
        print("Debugging: Looking for 'section recently' elements...")
        content = self.get_page_content(self.base_url)
        if not content:
            return
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Try different selectors
        selectors_to_try = [
            ('div', lambda x: x and 'section' in x and 'recently' in x),
            ('section', lambda x: x and 'recently' in x),
            ('div', lambda x: x and 'recently' in x),
            ('div', lambda x: x and 'section' in x),
        ]
        
        for tag, class_func in selectors_to_try:
            elements = soup.find_all(tag, class_=class_func)
            if elements:
                print(f"Found {len(elements)} elements with tag '{tag}' and class containing 'recently' or 'section':")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    classes = elem.get('class', [])
                    print(f"  {i+1}. Classes: {classes}")
                    print(f"     Text preview: {elem.get_text(strip=True)[:100]}...")
        
        # Also look for elements containing "recently" in text
        recently_text_elements = soup.find_all(string=lambda text: text and 'recently' in text.lower())
        if recently_text_elements:
            print(f"\nFound {len(recently_text_elements)} text elements containing 'recently':")
            for i, text_elem in enumerate(recently_text_elements[:3]):
                parent = text_elem.parent
                print(f"  {i+1}. Parent tag: {parent.name if parent else 'None'}")
                print(f"     Parent classes: {parent.get('class', []) if parent else 'None'}")
                print(f"     Text: {text_elem.strip()[:100]}...")
    
    def extract_game_links_from_recently_section(self):
        """Extract game page links specifically from the 'section recently' div"""
        print("Extracting game page links from 'section recently'...")
        content = self.get_page_content(self.base_url)
        if not content:
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        game_links = []
        
        # Find the div with class containing 'section recently'
        recently_section = soup.find('div', class_=lambda x: x and 'section' in x and 'recently' in x)
        
        if not recently_section:
            # Try alternative selectors
            recently_section = soup.find('section', class_=lambda x: x and 'recently' in x)
        
        if not recently_section:
            # Try finding by text content
            recently_text = soup.find(string=lambda text: text and 'recently' in text.lower())
            if recently_text:
                recently_section = recently_text.parent
                # Go up to find the container div
                while recently_section and recently_section.name not in ['div', 'section']:
                    recently_section = recently_section.parent
        
        if not recently_section:
            print("❌ Could not find 'section recently' div")
            print("Running debug to help identify the correct selector...")
            self.debug_find_recently_section()
            return []
        
        print("✅ Found 'section recently' section")
        print(f"Section tag: {recently_section.name}")
        print(f"Section classes: {recently_section.get('class', [])}")
        
        # Find all links within this section
        links = recently_section.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            title = link.get_text(strip=True)
            
            if href and title and len(title) > 2:
                # Check if this looks like a game link
                if self.is_game_link(href, title):
                    full_url = urljoin(self.base_url, href)
                    
                    # Try to extract thumbnail from the link or its parent
                    thumbnail = self.extract_thumbnail_from_link(link)
                    
                    game_links.append({
                        'title': title,
                        'url': full_url,
                        'relative_path': href,
                        'thumbnail': thumbnail
                    })
        
        print(f"Found {len(game_links)} game links in 'section recently'")
        return game_links
    
    def is_game_link(self, href, title):
        """Check if a link is likely a game page"""
        # Skip certain types of links
        skip_patterns = ['tag', 'category', 'about', 'contact', 'privacy', 'terms']
        if any(pattern in href.lower() for pattern in skip_patterns):
            return False
        
        # Look for game indicators
        game_indicators = ['game', 'play', 'online']
        if any(indicator in href.lower() for indicator in game_indicators):
            return True
        
        # Check if title looks like a game name
        if len(title) > 3 and not any(skip in title.lower() for skip in ['home', 'about', 'contact', 'privacy']):
            return True
        
        return False
    
    def extract_thumbnail_from_link(self, link_element):
        """Extract thumbnail from a game link element"""
        # Look for img tag within the link
        img = link_element.find('img')
        if img:
            src = img.get('src')
            if src and self.is_valid_image_url(src):
                return self.normalize_image_url(src)
        
        # Look for img tag in parent elements
        parent = link_element.parent
        while parent and parent.name != 'body':
            img = parent.find('img')
            if img:
                src = img.get('src')
                if src and self.is_valid_image_url(src):
                    return self.normalize_image_url(src)
            parent = parent.parent
        
        return ''
    
    def extract_game_info_from_page(self, url, game_title, main_page_thumbnail=''):
        """Extract iframe sources and game introduction information from a specific game page"""
        print(f"  Analyzing: {game_title}")
        content = self.get_page_content(url)
        if not content:
            return None
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Initialize game info
        game_info = {
            'title': game_title,
            'url': url,
            'iframes': [],
            'description': '',
            'tags': [],
            'category': '',
            'rating': '',
            'play_count': '',
            'game_type': '',
            'thumbnail': '',
            'thumbnail_alt': ''
        }
        
        # Extract iframe sources
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src')
            if src:
                # Clean and normalize the iframe source
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(self.base_url, src)
                
                iframe_data = {
                    'src': src,
                    'width': iframe.get('width', ''),
                    'height': iframe.get('height', ''),
                    'frameborder': iframe.get('frameborder', ''),
                    'allowfullscreen': iframe.get('allowfullscreen', ''),
                    'sandbox': iframe.get('sandbox', '')
                }
                
                game_info['iframes'].append(iframe_data)
                self.game_data['iframe_sources'].add(src)
        
        # Extract game description/introduction
        description_selectors = [
            'meta[name="description"]',
            '.game-description',
            '.description',
            '.game-info',
            '.intro',
            'p'
        ]
        
        for selector in description_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                if selector.startswith('meta'):
                    desc_text = desc_elem.get('content', '')
                else:
                    desc_text = desc_elem.get_text(strip=True)
                
                if desc_text and len(desc_text) > 20:
                    game_info['description'] = desc_text[:500]  # Limit to 500 chars
                    break
        
        # Extract tags/categories
        tag_selectors = [
            '.tags a',
            '.tag',
            '.category',
            '.game-tags a',
            'meta[name="keywords"]'
        ]
        
        for selector in tag_selectors:
            tag_elements = soup.select(selector)
            for tag_elem in tag_elements:
                if selector.startswith('meta'):
                    tag_text = tag_elem.get('content', '')
                    if tag_text:
                        tags = [tag.strip() for tag in tag_text.split(',')]
                        game_info['tags'].extend(tags[:5])  # Limit to 5 tags
                else:
                    tag_text = tag_elem.get_text(strip=True)
                    if tag_text and len(tag_text) < 50:
                        game_info['tags'].append(tag_text)
        
        # Remove duplicates and limit tags
        game_info['tags'] = list(set(game_info['tags']))[:5]
        
        # Extract category
        category_selectors = [
            '.breadcrumb a:last-child',
            '.category-name',
            '.game-category'
        ]
        
        for selector in category_selectors:
            cat_elem = soup.select_one(selector)
            if cat_elem:
                game_info['category'] = cat_elem.get_text(strip=True)
                break
        
        # Extract rating if available
        rating_elem = soup.select_one('.rating, .score, .stars')
        if rating_elem:
            game_info['rating'] = rating_elem.get_text(strip=True)
        
        # Extract play count if available
        play_count_elem = soup.select_one('.play-count, .views, .plays')
        if play_count_elem:
            game_info['play_count'] = play_count_elem.get_text(strip=True)
        
        # Extract thumbnail image
        thumbnail_selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            '.game-thumbnail img',
            '.thumbnail img',
            '.game-image img',
            '.preview img',
            '.screenshot img',
            'img[alt*="thumbnail"]',
            'img[alt*="preview"]',
            'img[alt*="screenshot"]',
            '.game-container img',
            'img'
        ]
        
        for selector in thumbnail_selectors:
            if selector.startswith('meta'):
                # Handle meta tags
                meta_elem = soup.select_one(selector)
                if meta_elem:
                    img_src = meta_elem.get('content', '')
                    if img_src and self.is_valid_image_url(img_src):
                        game_info['thumbnail'] = self.normalize_image_url(img_src)
                        break
            else:
                # Handle img tags
                img_elem = soup.select_one(selector)
                if img_elem:
                    img_src = img_elem.get('src', '')
                    if img_src and self.is_valid_image_url(img_src):
                        game_info['thumbnail'] = self.normalize_image_url(img_src)
                        game_info['thumbnail_alt'] = img_elem.get('alt', '')
                        break
        
        # If no thumbnail found on the page, use the one from main page
        if not game_info['thumbnail'] and main_page_thumbnail:
            game_info['thumbnail'] = main_page_thumbnail
        
        # Determine game type based on iframe source
        if game_info['iframes']:
            iframe_src = game_info['iframes'][0]['src']
            if 'unity' in iframe_src.lower():
                game_info['game_type'] = 'Unity'
            elif 'flash' in iframe_src.lower():
                game_info['game_type'] = 'Flash'
            elif 'html5' in iframe_src.lower():
                game_info['game_type'] = 'HTML5'
            else:
                game_info['game_type'] = 'Web'
        
        return game_info
    
    def is_valid_image_url(self, url):
        """Check if the URL is a valid image URL"""
        if not url or len(url) < 10:
            return False
        
        # Skip data URLs and very small images
        if url.startswith('data:') or url.startswith('blob:'):
            return False
        
        # Check for common image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
        url_lower = url.lower()
        
        # Check if URL contains image extension
        has_image_ext = any(ext in url_lower for ext in image_extensions)
        
        # Check if URL looks like an image (contains image-related keywords)
        image_keywords = ['image', 'img', 'photo', 'picture', 'thumbnail', 'preview', 'screenshot']
        has_image_keyword = any(keyword in url_lower for keyword in image_keywords)
        
        # Skip obvious non-image URLs
        skip_keywords = ['icon', 'logo', 'avatar', 'favicon', 'button', 'arrow']
        has_skip_keyword = any(keyword in url_lower for keyword in skip_keywords)
        
        return (has_image_ext or has_image_keyword) and not has_skip_keyword
    
    def normalize_image_url(self, url):
        """Normalize image URL to absolute URL"""
        if not url:
            return ''
        
        # Handle protocol-relative URLs
        if url.startswith('//'):
            return 'https:' + url
        
        # Handle relative URLs
        if url.startswith('/'):
            return urljoin(self.base_url, url)
        
        # Handle relative URLs without leading slash
        if not url.startswith(('http://', 'https://')):
            return urljoin(self.base_url, url)
        
        return url
    
    def analyze_recently_games(self, max_games=50):
        """Analyze games from the 'section recently' to extract iframe sources and game info"""
        print("Starting analysis of 'Recently Played' games...")
        
        # First, get game links from the recently section
        game_links = self.extract_game_links_from_recently_section()
        
        if not game_links:
            print("No game links found in 'section recently'!")
            return
        
        # Limit the number of games to analyze
        games_to_analyze = game_links[:max_games]
        print(f"Analyzing {len(games_to_analyze)} games from 'Recently Played' section...")
        
        for i, game_link in enumerate(games_to_analyze, 1):
            print(f"\n[{i}/{len(games_to_analyze)}] Processing: {game_link['title']}")
            
            # Extract game info including iframes and description
            game_info = self.extract_game_info_from_page(
                game_link['url'], 
                game_link['title'], 
                game_link.get('thumbnail', '')
            )
            
            if game_info:
                self.game_data['games'].append(game_info)
                iframe_count = len(game_info['iframes'])
                desc_length = len(game_info['description'])
                thumbnail_status = "✅" if game_info['thumbnail'] else "❌"
                print(f"  ✅ Found {iframe_count} iframe(s), description: {desc_length} chars, thumbnail: {thumbnail_status}")
            else:
                print(f"  ❌ No game info found")
            
            # Add a small delay to be respectful to the server
            time.sleep(0.3)
        
        self.game_data['total_games'] = len(self.game_data['games'])
        print(f"\n✅ Analysis complete! Processed {self.game_data['total_games']} games from 'Recently Played' section")
    
    def save_game_data(self, filename='games_data.json'):
        """Save the extracted game data to a JSON file"""
        data = {
            'website': self.base_url,
            'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_games': self.game_data['total_games'],
            'games': self.game_data['games']
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Game data saved to {filename}")
        return data
    

def main():
    """Main function to extract game data from 'Recently Played' section"""
    print("Starting OnlineGames.io game data extraction from 'Recently Played' section...")
    
    extractor = GameIframeExtractor()
    
    try:
        # Analyze 50 games from the 'Recently Played' section
        extractor.analyze_recently_games(max_games=50)
        
        # Save the extracted data
        extractor.save_game_data()
        
        print("\n✅ Game data extraction completed successfully!")
        print(f"📁 Generated file: games_data.json")
        print(f"📊 Total games processed: {extractor.game_data['total_games']}")
        
    except Exception as e:
        print(f"❌ Error during game data extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
