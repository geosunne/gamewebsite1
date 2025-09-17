#!/usr/bin/env python3
"""
Initialize the SQLite database
"""

import os
from app import create_app, db

def init_database():
    """Initialize the database with tables"""
    app = create_app()

    with app.app_context():
        # Create database file directory if it doesn't exist
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"Created directory: {db_dir}")

        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_database()