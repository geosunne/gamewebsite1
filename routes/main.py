from flask import Blueprint, render_template, send_from_directory, abort
from models import Game, Category
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Serve the main index page"""
    return send_from_directory('static', 'index.html')

@main_bp.route('/games')
def games():
    """Serve the games listing page"""
    return send_from_directory('static', 'games.html')

@main_bp.route('/game')
def game_detail():
    """Serve the individual game page"""
    return send_from_directory('static', 'game.html')

@main_bp.route('/games/<slug>')
def game_detail_by_slug(slug):
    """Serve individual game page by slug"""
    game = Game.query.filter_by(slug=slug, is_active=True).first()
    if not game:
        abort(404)

    # Get related games from the same category
    related_games = Game.query.filter(
        Game.category_id == game.category_id,
        Game.id != game.id,
        Game.is_active == True
    ).limit(4).all()

    # If not enough related games, get some from other categories
    if len(related_games) < 4:
        additional_games = Game.query.filter(
            Game.id != game.id,
            Game.is_active == True
        ).limit(4 - len(related_games)).all()
        related_games.extend(additional_games)

    return render_template('game.html', game=game, related_games=related_games)

@main_bp.route('/games/monster-survivors')
def monster_survivors():
    """Redirect to the dynamic game page for Monster Survivors"""
    game = Game.query.filter_by(slug='monster-survivors').first()
    if game:
        return game_detail_by_slug('monster-survivors')
    else:
        return send_from_directory('static', 'monster-survivors.html')

@main_bp.route('/admin')
def admin_panel():
    """Serve the admin panel (basic HTML interface)"""
    return send_from_directory('static', 'admin.html')

# Static file routes
@main_bp.route('/assets/<path:filename>')
def assets(filename):
    """Serve static assets"""
    return send_from_directory('static/assets', filename)

@main_bp.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory('static', 'favicon.ico')

@main_bp.route('/ads.txt')
def ads_txt():
    """Serve ads.txt file"""
    return send_from_directory('static', 'ads.txt')

@main_bp.route('/robots.txt')
def robots_txt():
    """Serve robots.txt file"""
    return send_from_directory('static', 'robots.txt')

@main_bp.route('/sitemap.xml')
def sitemap():
    """Serve sitemap.xml file"""
    return send_from_directory('static', 'sitemap.xml')