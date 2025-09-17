from flask import Blueprint, jsonify, request, render_template
from models import Game, Category, GameStats, games_schema, game_schema, categories_schema, category_schema
from app import db
from datetime import datetime
import json

admin_bp = Blueprint('admin', __name__)

# Admin authentication decorator (simplified for demo)
def admin_required(f):
    """Decorator to require admin authentication"""
    def decorated_function(*args, **kwargs):
        # In production, implement proper authentication
        api_key = request.headers.get('X-API-Key')
        if api_key != 'admin-api-key-change-in-production':
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Game management endpoints
@admin_bp.route('/games', methods=['GET'])
@admin_required
def admin_get_games():
    """Get all games for admin (including inactive)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        include_inactive = request.args.get('include_inactive', False, type=bool)

        query = Game.query
        if not include_inactive:
            query = query.filter(Game.is_active == True)

        paginated_games = query.order_by(Game.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        result = games_schema.dump(paginated_games.items)

        return jsonify({
            'games': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated_games.total,
                'pages': paginated_games.pages,
                'has_next': paginated_games.has_next,
                'has_prev': paginated_games.has_prev
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/games', methods=['POST'])
@admin_required
def admin_create_game():
    """Create a new game"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['title', 'slug', 'description', 'game_url', 'category_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if slug already exists
        existing_game = Game.query.filter_by(slug=data['slug']).first()
        if existing_game:
            return jsonify({'error': 'Slug already exists'}), 400

        # Check if category exists
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'error': 'Category not found'}), 400

        # Create new game
        game = Game(
            title=data['title'],
            slug=data['slug'],
            description=data['description'],
            long_description=data.get('long_description', ''),
            thumbnail_url=data.get('thumbnail_url', ''),
            game_url=data['game_url'],
            category_id=data['category_id'],
            rating=data.get('rating', 0.0),
            is_featured=data.get('is_featured', False),
            is_new=data.get('is_new', True),
            is_active=data.get('is_active', True),
            tags=data.get('tags', []),
            features=data.get('features', []),
            controls=data.get('controls', {}),
            release_date=datetime.fromisoformat(data['release_date']) if 'release_date' in data else datetime.utcnow()
        )

        db.session.add(game)
        db.session.commit()

        return jsonify({
            'message': 'Game created successfully',
            'game': game_schema.dump(game)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/games/<int:game_id>', methods=['PUT'])
@admin_required
def admin_update_game(game_id):
    """Update an existing game"""
    try:
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        data = request.get_json()

        # Update fields
        for field in ['title', 'slug', 'description', 'long_description', 'thumbnail_url',
                     'game_url', 'category_id', 'rating', 'is_featured', 'is_new', 'is_active',
                     'tags', 'features', 'controls']:
            if field in data:
                setattr(game, field, data[field])

        if 'release_date' in data:
            game.release_date = datetime.fromisoformat(data['release_date'])

        game.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Game updated successfully',
            'game': game_schema.dump(game)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/games/<int:game_id>', methods=['DELETE'])
@admin_required
def admin_delete_game(game_id):
    """Delete a game (soft delete by setting is_active to False)"""
    try:
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        # Soft delete
        game.is_active = False
        game.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'message': 'Game deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Category management endpoints
@admin_bp.route('/categories', methods=['GET'])
@admin_required
def admin_get_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()
        return jsonify({'categories': categories_schema.dump(categories)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/categories', methods=['POST'])
@admin_required
def admin_create_category():
    """Create a new category"""
    try:
        data = request.get_json()

        # Validate required fields
        if 'name' not in data or 'slug' not in data:
            return jsonify({'error': 'Name and slug are required'}), 400

        # Check if slug already exists
        existing_category = Category.query.filter_by(slug=data['slug']).first()
        if existing_category:
            return jsonify({'error': 'Slug already exists'}), 400

        category = Category(
            name=data['name'],
            slug=data['slug'],
            description=data.get('description', '')
        )

        db.session.add(category)
        db.session.commit()

        return jsonify({
            'message': 'Category created successfully',
            'category': category_schema.dump(category)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/categories/<int:category_id>', methods=['PUT'])
@admin_required
def admin_update_category(category_id):
    """Update an existing category"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        data = request.get_json()

        # Update fields
        for field in ['name', 'slug', 'description']:
            if field in data:
                setattr(category, field, data[field])

        db.session.commit()

        return jsonify({
            'message': 'Category updated successfully',
            'category': category_schema.dump(category)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def admin_delete_category(category_id):
    """Delete a category"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        # Check if category has games
        games_count = Game.query.filter_by(category_id=category_id).count()
        if games_count > 0:
            return jsonify({'error': f'Cannot delete category with {games_count} games'}), 400

        db.session.delete(category)
        db.session.commit()

        return jsonify({'message': 'Category deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Statistics endpoints
@admin_bp.route('/stats/dashboard', methods=['GET'])
@admin_required
def admin_dashboard_stats():
    """Get dashboard statistics"""
    try:
        from sqlalchemy import func
        from datetime import date, timedelta

        # Basic stats
        total_games = Game.query.filter_by(is_active=True).count()
        total_categories = Category.query.count()
        total_plays = db.session.query(func.sum(Game.total_plays)).scalar() or 0

        # Today's stats
        today = date.today()
        today_stats = GameStats.query.filter_by(date=today).all()
        today_plays = sum(stat.daily_plays for stat in today_stats)

        # Last 7 days stats
        week_ago = today - timedelta(days=7)
        week_stats = db.session.query(
            GameStats.date,
            func.sum(GameStats.daily_plays).label('total_plays')
        ).filter(
            GameStats.date >= week_ago
        ).group_by(GameStats.date).all()

        # Top games this week
        top_games = db.session.query(
            Game.title,
            func.sum(GameStats.daily_plays).label('plays')
        ).join(GameStats).filter(
            GameStats.date >= week_ago,
            Game.is_active == True
        ).group_by(Game.id, Game.title).order_by(
            func.sum(GameStats.daily_plays).desc()
        ).limit(10).all()

        return jsonify({
            'basic_stats': {
                'total_games': total_games,
                'total_categories': total_categories,
                'total_plays': total_plays,
                'today_plays': today_plays
            },
            'week_stats': [
                {
                    'date': stat.date.isoformat(),
                    'plays': stat.total_plays
                }
                for stat in week_stats
            ],
            'top_games': [
                {
                    'title': game.title,
                    'plays': game.plays
                }
                for game in top_games
            ]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Bulk operations
@admin_bp.route('/games/bulk-update', methods=['POST'])
@admin_required
def admin_bulk_update_games():
    """Bulk update games"""
    try:
        data = request.get_json()
        game_ids = data.get('game_ids', [])
        updates = data.get('updates', {})

        if not game_ids:
            return jsonify({'error': 'No game IDs provided'}), 400

        # Update games
        updated_count = 0
        for game_id in game_ids:
            game = Game.query.get(game_id)
            if game:
                for field, value in updates.items():
                    if hasattr(game, field):
                        setattr(game, field, value)
                game.updated_at = datetime.utcnow()
                updated_count += 1

        db.session.commit()

        return jsonify({
            'message': f'Successfully updated {updated_count} games',
            'updated_count': updated_count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500