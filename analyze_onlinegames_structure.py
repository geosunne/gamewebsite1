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

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available. Install with: pip install selenium")

class GameIframeExtractor:
    def __init__(self, base_url="https://www.onlinegames.io", use_selenium=True):
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
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None

    def init_selenium_driver(self):
        """Initialize Selenium WebDriver with Chrome"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium is not available")
            return False

        if self.driver:
            return True

        try:
            print("🔧 Initializing Selenium WebDriver...")
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'user-agent={self.session.headers["User-Agent"]}')

            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Selenium WebDriver initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Selenium: {e}")
            self.use_selenium = False
            return False

    def close_selenium_driver(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("✅ Selenium WebDriver closed")

    def click_view_more_until_done(self, url, max_clicks=50):
        """Click 'view-more' button until no more games are loaded"""
        if not self.use_selenium:
            print("⚠️  Selenium not available, falling back to requests")
            return self.get_page_content(url)

        if not self.init_selenium_driver():
            return self.get_page_content(url)

        try:
            print(f"🌐 Loading page with Selenium: {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for initial page load

            # Count initial games
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            initial_game_count = len(soup.find_all('a', href=True))
            print(f"  Initial game links: {initial_game_count}")

            clicks = 0
            consecutive_no_change = 0
            last_game_count = initial_game_count

            while clicks < max_clicks:
                try:
                    # Look for "view-more" button
                    view_more_selectors = [
                        (By.CLASS_NAME, 'view-more'),
                        (By.XPATH, "//button[contains(@class, 'view-more')]"),
                        (By.XPATH, "//a[contains(@class, 'view-more')]"),
                        (By.XPATH, "//button[contains(text(), 'Load More')]"),
                        (By.XPATH, "//button[contains(text(), 'View More')]"),
                    ]

                    button_found = False
                    for by, selector in view_more_selectors:
                        try:
                            button = WebDriverWait(self.driver, 2).until(
                                EC.presence_of_element_located((by, selector))
                            )

                            if button and button.is_displayed() and button.is_enabled():
                                # Scroll to button
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(0.5)

                                # Click button using JavaScript to avoid interception
                                try:
                                    self.driver.execute_script("arguments[0].click();", button)
                                except:
                                    # Fallback to regular click
                                    button.click()

                                clicks += 1
                                button_found = True
                                print(f"  🖱️  Clicked 'view-more' button (click #{clicks})")

                                # Wait for content to load
                                time.sleep(1.5)

                                # Check if new games were loaded
                                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                                current_game_count = len(soup.find_all('a', href=True))

                                if current_game_count > last_game_count:
                                    print(f"    ✅ Loaded more games: {current_game_count} total (+{current_game_count - last_game_count})")
                                    last_game_count = current_game_count
                                    consecutive_no_change = 0
                                else:
                                    consecutive_no_change += 1
                                    print(f"    ⚠️  No new games loaded ({consecutive_no_change}/3)")

                                    if consecutive_no_change >= 3:
                                        print(f"  ✅ No more new games after {consecutive_no_change} attempts")
                                        break

                                break  # Exit selector loop
                        except (TimeoutException, NoSuchElementException):
                            continue

                    if not button_found:
                        print(f"  ℹ️  No 'view-more' button found (after {clicks} clicks)")
                        break

                except Exception as e:
                    print(f"  ⚠️  Error clicking button: {e}")
                    break

            # Get final page content
            final_content = self.driver.page_source
            soup = BeautifulSoup(final_content, 'html.parser')
            final_game_count = len(soup.find_all('a', href=True))

            print(f"  📊 Final game links: {final_game_count} (loaded {final_game_count - initial_game_count} more)")
            print(f"  🖱️  Total clicks: {clicks}")

            return final_content

        except Exception as e:
            print(f"❌ Error during Selenium page load: {e}")
            return self.get_page_content(url)

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

        # Use Selenium to click "view-more" button and load all games
        if self.use_selenium:
            content = self.click_view_more_until_done(self.base_url)
        else:
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
    
    def analyze_recently_games(self, max_games):
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
            
            # Skip games with URLs containing "/t/"
            if '/t/' in game_link['url']:
                print(f"  ⏭️  Skipping game with /t/ in URL: {game_link['url']}")
                continue
            
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
    
    def load_existing_games(self, filename='games_data.json'):
        """Load existing games from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                return existing_data.get('games', [])
        except FileNotFoundError:
            print(f"No existing {filename} found, starting fresh")
            return []
        except Exception as e:
            print(f"Error loading existing games: {e}")
            return []

    def get_existing_game_urls(self, existing_games):
        """Get set of existing game URLs for deduplication"""
        return set(game.get('url', '') for game in existing_games)

    def save_game_data(self, filename='games_data.json'):
        """Save the extracted game data to a JSON file, merging with existing data"""
        # Load existing games
        existing_games = self.load_existing_games(filename)
        existing_urls = self.get_existing_game_urls(existing_games)

        # Filter out games that already exist
        new_games = []
        skipped_count = 0

        for game in self.game_data['games']:
            if game['url'] not in existing_urls:
                new_games.append(game)
            else:
                skipped_count += 1
                print(f"  ⏭️  Skipping existing game: {game['title']}")

        # Merge with existing games
        all_games = existing_games + new_games

        data = {
            'website': self.base_url,
            'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_games': len(all_games),
            'games': all_games
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n📊 Summary:")
        print(f"  📁 File: {filename}")
        print(f"  🆕 New games added: {len(new_games)}")
        print(f"  ⏭️  Existing games skipped: {skipped_count}")
        print(f"  📈 Total games in file: {len(all_games)}")

        return data
    

def main():
    """Main function to extract game data from 'Recently Played' section"""
    import argparse

    parser = argparse.ArgumentParser(description='Extract game data from OnlineGames.io')
    parser.add_argument('--max-games', type=int, default=200,
                        help='Maximum number of games to extract')
    parser.add_argument('--use-selenium', action='store_true', default=True,
                        help='Use Selenium to load dynamic content (default: True)')
    parser.add_argument('--no-selenium', dest='use_selenium', action='store_false',
                        help='Disable Selenium and use simple requests')

    args = parser.parse_args()

    print("Starting OnlineGames.io game data extraction from 'Recently Played' section...")

    extractor = GameIframeExtractor(use_selenium=args.use_selenium)

    try:
        # Analyze games from the 'Recently Played' section
        extractor.analyze_recently_games(max_games=args.max_games)

        # Save the extracted data
        extractor.save_game_data()

        print("\n✅ Game data extraction completed successfully!")
        print(f"📁 Generated file: games_data.json")
        print(f"📊 Total games processed: {extractor.game_data['total_games']}")

    except Exception as e:
        print(f"❌ Error during game data extraction: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close Selenium driver if it was used
        extractor.close_selenium_driver()

if __name__ == "__main__":
    main()
