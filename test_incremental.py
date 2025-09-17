#!/usr/bin/env python3
"""
Test the incremental game addition functionality
"""
import json
from analyze_onlinegames_structure import GameIframeExtractor

def test_incremental_addition():
    """Test that existing games are skipped"""
    print("Testing incremental game addition...")

    # Create extractor instance
    extractor = GameIframeExtractor()

    # Load existing games
    existing_games = extractor.load_existing_games('games_data.json')
    existing_urls = extractor.get_existing_game_urls(existing_games)

    print(f"📊 Current games in database: {len(existing_games)}")
    print(f"📊 Unique URLs in database: {len(existing_urls)}")

    # Show first few existing URLs
    if existing_urls:
        print("\n🔍 Sample existing URLs:")
        for i, url in enumerate(list(existing_urls)[:5]):
            print(f"  {i+1}. {url}")

    # Test the deduplication logic
    test_game = {
        'title': 'Test Game',
        'url': list(existing_urls)[0] if existing_urls else 'https://example.com/new-game',
        'description': 'Test description',
        'iframes': []
    }

    print(f"\n🧪 Testing with existing URL: {test_game['url']}")

    # Simulate adding this game
    extractor.game_data['games'] = [test_game]

    # Test save functionality (dry run)
    existing_games_before = extractor.load_existing_games('games_data.json')
    existing_urls_before = extractor.get_existing_game_urls(existing_games_before)

    new_games = []
    skipped_count = 0

    for game in extractor.game_data['games']:
        if game['url'] not in existing_urls_before:
            new_games.append(game)
            print(f"  ✅ Would add new game: {game['title']}")
        else:
            skipped_count += 1
            print(f"  ⏭️  Would skip existing game: {game['title']}")

    print(f"\n📊 Test Results:")
    print(f"  🆕 New games to add: {len(new_games)}")
    print(f"  ⏭️  Games to skip: {skipped_count}")

    return len(new_games), skipped_count

if __name__ == "__main__":
    test_incremental_addition()