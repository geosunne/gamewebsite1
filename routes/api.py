from flask import Blueprint, jsonify, request
from models import Game, Category, GamePlay, GameStats, games_schema, game_schema, categories_schema, category_schema
from app import db
from sqlalchemy import desc, func, and_
from datetime import datetime, date
import json

api_bp = Blueprint('api', __name__)

# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Games API endpoints
@api_bp.route('/games', methods=['GET'])
def get_games():
    """Get all games with optional filtering and pagination"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        sort_by = request.args.get('sort', 'popular')  # popular, newest, rating, name
        featured = request.args.get('featured', type=bool)
        new = request.args.get('new', type=bool)

        # Base query
        query = Game.query.filter(Game.is_active == True)

        # Apply filters
        if category and category != 'all':
            query = query.join(Category).filter(Category.slug == category)

        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    Game.title.ilike(search_term),
                    Game.description.ilike(search_term),
                    Game.tags.contains([search])
                )
            )

        if featured is not None:
            query = query.filter(Game.is_featured == featured)

        if new is not None:
            query = query.filter(Game.is_new == new)

        # Apply sorting
        if sort_by == 'popular':
            query = query.order_by(desc(Game.total_plays))
        elif sort_by == 'newest':
            query = query.order_by(desc(Game.release_date))
        elif sort_by == 'rating':
            query = query.order_by(desc(Game.rating))
        elif sort_by == 'name':
            query = query.order_by(Game.title)

        # Pagination
        if per_page > 100:  # Limit max per_page
            per_page = 100

        paginated_games = query.paginate(
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

@api_bp.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    """Get a specific game by ID"""
    try:
        game = Game.query.filter(Game.id == game_id, Game.is_active == True).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        result = game_schema.dump(game)
        return jsonify({'game': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/games/slug/<string:slug>', methods=['GET'])
def get_game_by_slug(slug):
    """Get a specific game by slug"""
    try:
        game = Game.query.filter(Game.slug == slug, Game.is_active == True).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        result = game_schema.dump(game)
        return jsonify({'game': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/games/<int:game_id>/play', methods=['POST'])
def record_game_play(game_id):
    """Record a game play session"""
    try:
        game = Game.query.filter(Game.id == game_id, Game.is_active == True).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        # Get client information
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.headers.get('User-Agent', '')
        play_duration = request.json.get('duration', 0) if request.json else 0

        # Record game play
        game_play = GamePlay(
            game_id=game_id,
            ip_address=ip_address,
            user_agent=user_agent,
            play_duration=play_duration
        )
        db.session.add(game_play)

        # Increment game plays
        game.increment_plays()

        # Update daily stats
        today = date.today()
        game_stat = GameStats.query.filter(
            GameStats.game_id == game_id,
            GameStats.date == today
        ).first()

        if game_stat:
            game_stat.daily_plays += 1
            # Update average play duration
            if play_duration > 0:
                total_duration = game_stat.avg_play_duration * (game_stat.daily_plays - 1) + play_duration
                game_stat.avg_play_duration = total_duration / game_stat.daily_plays
        else:
            game_stat = GameStats(
                game_id=game_id,
                date=today,
                daily_plays=1,
                unique_players=1,
                avg_play_duration=play_duration
            )
            db.session.add(game_stat)

        db.session.commit()

        return jsonify({'message': 'Game play recorded successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Categories API endpoints
@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()
        result = categories_schema.dump(categories)
        return jsonify({'categories': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/categories/<int:category_id>/games', methods=['GET'])
def get_games_by_category(category_id):
    """Get games by category ID"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        paginated_games = Game.query.filter(
            Game.category_id == category_id,
            Game.is_active == True
        ).order_by(desc(Game.total_plays)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        result = games_schema.dump(paginated_games.items)

        return jsonify({
            'category': category_schema.dump(category),
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

# Statistics API endpoints
@api_bp.route('/stats/games', methods=['GET'])
def get_games_stats():
    """Get overall games statistics"""
    try:
        total_games = Game.query.filter(Game.is_active == True).count()
        total_plays = db.session.query(func.sum(Game.total_plays)).scalar() or 0
        featured_games = Game.query.filter(Game.is_featured == True, Game.is_active == True).count()
        new_games = Game.query.filter(Game.is_new == True, Game.is_active == True).count()

        # Most popular games
        popular_games = Game.query.filter(Game.is_active == True)\
            .order_by(desc(Game.total_plays))\
            .limit(5)\
            .all()

        return jsonify({
            'stats': {
                'total_games': total_games,
                'total_plays': total_plays,
                'featured_games': featured_games,
                'new_games': new_games
            },
            'popular_games': games_schema.dump(popular_games)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats/games/<int:game_id>', methods=['GET'])
def get_game_stats(game_id):
    """Get statistics for a specific game"""
    try:
        game = Game.query.filter(Game.id == game_id, Game.is_active == True).first()
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        # Get daily stats for the last 30 days
        daily_stats = GameStats.query.filter(
            GameStats.game_id == game_id
        ).order_by(desc(GameStats.date)).limit(30).all()

        return jsonify({
            'game': game_schema.dump(game),
            'daily_stats': [
                {
                    'date': stat.date.isoformat(),
                    'plays': stat.daily_plays,
                    'unique_players': stat.unique_players,
                    'avg_duration': stat.avg_play_duration
                }
                for stat in daily_stats
            ]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Search API endpoints
@api_bp.route('/search', methods=['GET'])
def search_games():
    """Search games with advanced filtering"""
    try:
        query_param = request.args.get('q', '')
        category = request.args.get('category')
        sort_by = request.args.get('sort', 'popular')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if not query_param:
            return jsonify({'error': 'Search query is required'}), 400

        # Build search query
        search_term = f'%{query_param}%'
        query = Game.query.filter(
            Game.is_active == True,
            db.or_(
                Game.title.ilike(search_term),
                Game.description.ilike(search_term),
                Game.long_description.ilike(search_term)
            )
        )

        # Category filter
        if category and category != 'all':
            query = query.join(Category).filter(Category.slug == category)

        # Sorting
        if sort_by == 'popular':
            query = query.order_by(desc(Game.total_plays))
        elif sort_by == 'newest':
            query = query.order_by(desc(Game.release_date))
        elif sort_by == 'rating':
            query = query.order_by(desc(Game.rating))
        elif sort_by == 'name':
            query = query.order_by(Game.title)

        # Pagination
        paginated_games = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        result = games_schema.dump(paginated_games.items)

        return jsonify({
            'query': query_param,
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