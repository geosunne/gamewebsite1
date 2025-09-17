from app import db, ma
from datetime import datetime
from sqlalchemy import JSON

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    games = db.relationship('Game', backref='category_obj', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    long_description = db.Column(db.Text)
    thumbnail_url = db.Column(db.String(255))
    game_url = db.Column(db.String(255), nullable=False)
    iframe_url = db.Column(db.String(255))  # Specific iframe URL for embedding

    # Category
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    # Game metadata
    rating = db.Column(db.Float, default=0.0)
    total_plays = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)

    # Game details
    tags = db.Column(JSON)  # Store as JSON array
    features = db.Column(JSON)  # Store as JSON array
    controls = db.Column(JSON)  # Store as JSON object

    # Timestamps
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    game_plays = db.relationship('GamePlay', backref='game', lazy=True, cascade='all, delete-orphan')
    game_stats = db.relationship('GameStats', backref='game', lazy=True, cascade='all, delete-orphan')

    @property
    def category_name(self):
        return self.category_obj.name if self.category_obj else None

    def increment_plays(self):
        """Increment the total plays count"""
        self.total_plays += 1
        db.session.commit()

    def update_rating(self):
        """Update rating based on game stats"""
        # Calculate average rating from game_stats if needed
        pass

    def __repr__(self):
        return f'<Game {self.title}>'

class GamePlay(db.Model):
    __tablename__ = 'game_plays'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    ip_address = db.Column(db.String(45))  # IPv6 support
    user_agent = db.Column(db.Text)
    play_duration = db.Column(db.Integer)  # Duration in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<GamePlay {self.game_id} at {self.created_at}>'

class GameStats(db.Model):
    __tablename__ = 'game_stats'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    daily_plays = db.Column(db.Integer, default=0)
    unique_players = db.Column(db.Integer, default=0)
    avg_play_duration = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint to ensure one record per game per date
    __table_args__ = (db.UniqueConstraint('game_id', 'date', name='_game_date_uc'),)

    def __repr__(self):
        return f'<GameStats {self.game_id} on {self.date}>'

# Marshmallow schemas for serialization
class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        include_relationships = True
        load_instance = True

class GameSchema(ma.SQLAlchemyAutoSchema):
    category_name = ma.String(dump_only=True)

    class Meta:
        model = Game
        include_relationships = True
        load_instance = True

class GamePlaySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GamePlay
        include_relationships = True
        load_instance = True

class GameStatsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GameStats
        include_relationships = True
        load_instance = True

# Initialize schemas
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
game_schema = GameSchema()
games_schema = GameSchema(many=True)
game_play_schema = GamePlaySchema()
game_stats_schema = GameStatsSchema()