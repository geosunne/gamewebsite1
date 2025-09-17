#!/usr/bin/env python3
"""
Run incremental game scraping with progress tracking
"""
import json
import sys
from analyze_onlinegames_structure import GameIframeExtractor

def run_incremental_scraping(max_games=100):
    """Run incremental game scraping with progress tracking"""
    print(f"🚀 Starting incremental game scraping (max: {max_games} games)...")

    extractor = GameIframeExtractor()

    # Show current status
    existing_games = extractor.load_existing_games('games_data.json')
    print(f"📊 Current games in database: {len(existing_games)}")

    try:
        print("\n🔍 Starting to analyze games from OnlineGames.io...")

        # Run the extraction
        extractor.analyze_recently_games(max_games=max_games)

        # Save with deduplication
        print("\n💾 Saving games with deduplication...")
        result = extractor.save_game_data()

        print(f"\n✅ Incremental scraping completed successfully!")
        print(f"📊 Final stats:")
        print(f"  🎮 Total games in database: {result['total_games']}")

        return True

    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error during incremental scraping: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    max_games = 100

    if len(sys.argv) > 1:
        try:
            max_games = int(sys.argv[1])
        except ValueError:
            print("Invalid max_games argument, using default 100")

    print(f"Max games to process: {max_games}")
    success = run_incremental_scraping(max_games)

    if success:
        print("\n🎯 Scraping completed! Check games_data.json for results.")
    else:
        print("\n⚠️  Scraping did not complete successfully.")

if __name__ == "__main__":
    main()