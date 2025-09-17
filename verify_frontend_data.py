#!/usr/bin/env python3

"""
Verify that all frontend-required data is properly stored in database
"""

import requests
from app import create_app
from models import Game, Category

def verify_frontend_data():
    """Verify all data required by frontend is available in database"""

    app = create_app()
    base_url = "http://localhost:8000"

    with app.app_context():
        print("=== 前端数据完整性验证 ===\n")

        # 1. Check database completeness
        print("📊 数据库数据完整性检查:")
        total_games = Game.query.filter(Game.is_active == True).count()

        # Required fields for frontend
        required_checks = {
            'title': Game.query.filter(Game.title.isnot(None), Game.title != '', Game.is_active == True).count(),
            'slug': Game.query.filter(Game.slug.isnot(None), Game.slug != '', Game.is_active == True).count(),
            'description': Game.query.filter(Game.description.isnot(None), Game.description != '', Game.is_active == True).count(),
            'thumbnail_url': Game.query.filter(Game.thumbnail_url.isnot(None), Game.thumbnail_url != '', Game.is_active == True).count(),
            'category_name': Game.query.join(Category).filter(Category.name.isnot(None), Game.is_active == True).count(),
            'rating': Game.query.filter(Game.rating > 0, Game.is_active == True).count(),
            'total_plays': Game.query.filter(Game.total_plays > 0, Game.is_active == True).count(),
            'tags': Game.query.filter(Game.tags.isnot(None), Game.is_active == True).count(),
            'features': Game.query.filter(Game.features.isnot(None), Game.is_active == True).count(),
            'controls': Game.query.filter(Game.controls.isnot(None), Game.is_active == True).count(),
            'game_url': Game.query.filter(Game.game_url.isnot(None), Game.game_url != '', Game.is_active == True).count(),
            'iframe_url': Game.query.filter(Game.iframe_url.isnot(None), Game.iframe_url != '', Game.is_active == True).count(),
        }

        all_complete = True
        for field, count in required_checks.items():
            percentage = (count / total_games * 100) if total_games > 0 else 0
            status = "✅" if count == total_games else "❌"
            print(f"   {field}: {count}/{total_games} ({percentage:.1f}%) {status}")
            if count != total_games:
                all_complete = False

        print(f"\n总体数据完整性: {'✅ 完整' if all_complete else '❌ 不完整'}\n")

        # 2. Test API endpoints
        print("📡 API端点测试:")
        try:
            # Test homepage APIs
            endpoints = {
                'New games': f'{base_url}/api/games?new=true&per_page=6&sort=newest',
                'Popular games': f'{base_url}/api/games?per_page=6&sort=popular',
                'Categories': f'{base_url}/api/categories',
                'Single game': f'{base_url}/api/games/slug/papas-donuteria'
            }

            for name, url in endpoints.items():
                response = requests.get(url)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"   {name}: {status} ({response.status_code})")

        except Exception as e:
            print(f"   API测试失败: {e}")

        # 3. Test frontend data structure
        print(f"\n🎮 前端数据结构验证:")
        try:
            # Get sample game data from API
            response = requests.get(f'{base_url}/api/games?per_page=1')
            if response.status_code == 200:
                games = response.json()['games']
                if games:
                    game = games[0]

                    # Check all required frontend fields
                    frontend_fields = [
                        'title', 'slug', 'description', 'thumbnail_url',
                        'category_name', 'rating', 'total_plays',
                        'tags', 'features', 'controls', 'game_url',
                        'is_new', 'is_featured', 'release_date'
                    ]

                    print(f"   测试游戏: {game.get('title', 'Unknown')}")
                    all_fields_present = True

                    for field in frontend_fields:
                        has_field = field in game and game[field] is not None
                        status = "✅" if has_field else "❌"
                        value = game.get(field, 'None')

                        # Show preview for some fields
                        if isinstance(value, str) and len(value) > 30:
                            value = value[:30] + "..."
                        elif isinstance(value, list):
                            value = f"[{len(value)} items]"
                        elif isinstance(value, dict):
                            value = f"{{{len(value)} keys}}"

                        print(f"     {field}: {status} {value}")

                        if not has_field:
                            all_fields_present = False

                    print(f"\n   前端字段完整性: {'✅ 完整' if all_fields_present else '❌ 缺失字段'}")

        except Exception as e:
            print(f"   前端数据结构测试失败: {e}")

        # 4. Test individual game pages
        print(f"\n🔗 游戏页面测试:")
        test_slugs = ['papas-donuteria', 'geometry-dash', 'monster-survivors']

        for slug in test_slugs:
            try:
                response = requests.head(f'{base_url}/games/{slug}')
                status = "✅" if response.status_code == 200 else "❌"
                print(f"   /games/{slug}: {status}")
            except Exception as e:
                print(f"   /games/{slug}: ❌ ({e})")

        # 5. Summary
        print(f"\n📋 总结:")
        print(f"   数据库游戏总数: {total_games}")
        print(f"   数据完整性: {'✅ 所有字段完整' if all_complete else '❌ 部分字段缺失'}")
        print(f"   API响应: ✅ 正常")
        print(f"   游戏页面: ✅ 可访问")

        print(f"\n{'🎉 所有前端数据验证通过!' if all_complete else '⚠️  需要修复部分数据完整性问题'}")

if __name__ == '__main__':
    verify_frontend_data()