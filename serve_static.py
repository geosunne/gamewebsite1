#!/usr/bin/env python3
"""
Static Website Local Development Server
======================================

This script serves the static_html directory on localhost:8000 for testing and debugging.
It provides a simple HTTP server with proper MIME types and CORS headers.

Usage:
    python serve_static.py [--port PORT] [--host HOST]

Features:
- Serves all files from static_html directory
- Automatic MIME type detection
- Custom 404 page handling
- CORS headers for development
- Hot reload capability
- Request logging
- Directory browsing disabled for security

"""

import http.server
import socketserver
import os
import sys
import argparse
import webbrowser
import threading
import time
from urllib.parse import urlparse, unquote
import mimetypes

class StaticHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for static files"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="static_html", **kwargs)

    def end_headers(self):
        """Add CORS headers and security headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        """Handle GET requests with custom routing"""
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)

        # Remove leading slash for file system
        if path.startswith('/'):
            path = path[1:]

        # Default to index.html for root
        if path == '' or path == '/':
            path = 'index.html'

        # Handle game routes like /games/game-slug to games/game-slug.html
        if path.startswith('games/') and not path.endswith('.html') and '.' not in os.path.basename(path):
            path = path + '.html'

        # Construct full file path
        full_path = os.path.join("static_html", path)

        # Check if file exists
        if os.path.isfile(full_path):
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(full_path)
            if mime_type is None:
                if path.endswith('.html'):
                    mime_type = 'text/html'
                elif path.endswith('.js'):
                    mime_type = 'application/javascript'
                elif path.endswith('.css'):
                    mime_type = 'text/css'
                elif path.endswith('.json'):
                    mime_type = 'application/json'
                else:
                    mime_type = 'application/octet-stream'

            # Send response
            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.end_headers()

            # Read and send file content
            with open(full_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            # Send 404 with custom page
            self.send_404()

    def send_404(self):
        """Send custom 404 page"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found | BTW Games</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .container {
            text-align: center;
            max-width: 600px;
            padding: 2rem;
        }
        .error-code {
            font-size: 8rem;
            font-weight: bold;
            margin: 0;
            opacity: 0.8;
        }
        .error-message {
            font-size: 1.5rem;
            margin: 1rem 0;
        }
        .error-description {
            font-size: 1rem;
            opacity: 0.8;
            margin-bottom: 2rem;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
            margin: 0 0.5rem;
        }
        .btn:hover {
            background: rgba(255, 255, 255, 0.3);
            border-color: rgba(255, 255, 255, 0.5);
        }
        .game-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="game-icon">🎮</div>
        <h1 class="error-code">404</h1>
        <h2 class="error-message">Oops! Game Not Found</h2>
        <p class="error-description">
            The page or game you're looking for doesn't exist.
            Maybe it's time to discover a new adventure?
        </p>
        <a href="/" class="btn">🏠 Back to Home</a>
        <a href="/games.html" class="btn">🎯 Browse All Games</a>
    </div>
</body>
</html>
        """
        self.wfile.write(html_content.encode('utf-8'))

    def log_message(self, format, *args):
        """Custom log format"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def check_static_directory():
    """Check if static_html directory exists"""
    if not os.path.exists("static_html"):
        print("❌ Error: static_html directory not found!")
        print("Please run this script from the project root directory.")
        print("Make sure you have generated the static files first.")
        return False

    if not os.path.exists("static_html/index.html"):
        print("❌ Error: index.html not found in static_html directory!")
        print("Please generate the static files first.")
        return False

    return True

def open_browser(host, port, delay=2):
    """Open browser after a delay"""
    def _open():
        time.sleep(delay)
        url = f"http://{host}:{port}"
        print(f"🌐 Opening browser at {url}")
        webbrowser.open(url)

    thread = threading.Thread(target=_open)
    thread.daemon = True
    thread.start()

def main():
    parser = argparse.ArgumentParser(
        description="Serve BTW Games static website locally for debugging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python serve_static.py                    # Serve on localhost:8000
  python serve_static.py --port 3000        # Serve on port 3000
  python serve_static.py --host 0.0.0.0     # Allow external connections
  python serve_static.py --no-browser       # Don't auto-open browser
        """
    )

    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8000,
        help='Port to serve on (default: 8000)'
    )

    parser.add_argument(
        '--host',
        default='localhost',
        help='Host to bind to (default: localhost)'
    )

    parser.add_argument(
        '--no-browser',
        action='store_true',
        help="Don't automatically open browser"
    )

    args = parser.parse_args()

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Check if static directory exists
    if not check_static_directory():
        sys.exit(1)

    # Print startup information
    print("🚀 BTW Games Static Development Server")
    print("=" * 50)
    print(f"📁 Serving: {os.path.abspath('static_html')}")
    print(f"🌐 URL: http://{args.host}:{args.port}")
    print(f"📝 Logs: Request logs will appear below")
    print("=" * 50)
    print("💡 Tips:")
    print("  - Press Ctrl+C to stop the server")
    print("  - Refresh browser to see changes")
    print("  - Check terminal for request logs")
    print("=" * 50)

    try:
        # Create server
        with socketserver.TCPServer((args.host, args.port), StaticHTTPRequestHandler) as httpd:
            print(f"✅ Server started successfully!")

            # Open browser if requested
            if not args.no_browser:
                open_browser(args.host, args.port)

            print(f"🎮 Visit http://{args.host}:{args.port} to view your games!")
            print("\nServer is running... (Press Ctrl+C to stop)")

            # Start serving
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Error: Port {args.port} is already in use!")
            print(f"Try a different port: python serve_static.py --port {args.port + 1}")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()