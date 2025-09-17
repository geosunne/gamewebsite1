#!/usr/bin/env python3
"""
Production runner script for BTW Games Flask application
"""

from app import create_app
import os

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')

    print(f"Starting BTW Games server on {host}:{port}")
    print(f"Debug mode: {debug_mode}")

    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )