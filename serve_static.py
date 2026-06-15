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
import http.client
import webbrowser
import threading
import time
import subprocess
from urllib.parse import urlparse, unquote
import mimetypes

API_PROXY_HOST = os.environ.get('API_PROXY_HOST', 'localhost')
API_PROXY_PORT = int(os.environ.get('API_PROXY_PORT', '5001'))
PROXY_SKIP_HEADERS = {
    'connection',
    'keep-alive',
    'proxy-authenticate',
    'proxy-authorization',
    'te',
    'trailers',
    'transfer-encoding',
    'upgrade',
    'server',
    'date',
    'access-control-allow-origin',
    'access-control-allow-methods',
    'access-control-allow-headers',
    'cache-control',
    'pragma',
    'expires',
}

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
        self.serve_static_request(include_body=True)

    def do_HEAD(self):
        """Handle HEAD requests with the same routing as GET."""
        self.serve_static_request(include_body=False)

    def serve_static_request(self, include_body=True):
        """Serve static files with clean URL routing."""
        parsed_path = urlparse(self.path)

        if parsed_path.path.startswith('/api/'):
            self.proxy_api_request()
            return

        clean_url = self.get_clean_url_redirect(parsed_path)
        if clean_url:
            self.send_response(308)
            self.send_header('Location', clean_url)
            self.end_headers()
            return

        path = unquote(parsed_path.path)

        # Remove leading slash for file system
        if path.startswith('/'):
            path = path[1:]

        # Default to index.html for root
        if path == '' or path == '/':
            path = 'index.html'

        # Construct full file path
        full_path = os.path.join("static_html", path)

        if not os.path.exists(full_path) and not os.path.splitext(path)[1]:
            html_path = os.path.join("static_html", f"{path}.html")
            if os.path.isfile(html_path):
                full_path = html_path
                path = f"{path}.html"

        if os.path.isdir(full_path):
            full_path = os.path.join(full_path, 'index.html')
            path = os.path.join(path, 'index.html')

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
            if include_body:
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
        else:
            # Send 404 with custom page
            self.send_404()

    def get_clean_url_redirect(self, parsed_path):
        """Return clean URL target for legacy .html paths."""
        path = parsed_path.path
        target = None

        if path == '/index.html':
            target = '/'
        elif path == '/games.html':
            target = '/games'
        elif path.startswith('/games/') and path.endswith('.html'):
            target = path[:-5]
        elif path.startswith('/games/') and path.endswith('/'):
            target = path.rstrip('/')

        if target and parsed_path.query:
            target = f"{target}?{parsed_path.query}"

        return target

    def do_POST(self):
        """Proxy API POST requests to the Flask backend"""
        parsed_path = urlparse(self.path)

        if parsed_path.path.startswith('/api/'):
            self.proxy_api_request()
            return

        self.send_404()

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        parsed_path = urlparse(self.path)

        if parsed_path.path.startswith('/api/'):
            self.proxy_api_request()
            return

        self.send_response(204)
        self.end_headers()

    def proxy_api_request(self):
        """Proxy /api requests to the local Flask development server"""
        body = None
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length:
            body = self.rfile.read(content_length)

        try:
            connection = http.client.HTTPConnection(API_PROXY_HOST, API_PROXY_PORT, timeout=10)
            headers = {key: value for key, value in self.headers.items() if key.lower() != 'host'}
            connection.request(self.command, self.path, body=body, headers=headers)
            response = connection.getresponse()
            response_body = response.read()

            self.send_response(response.status)
            for header, value in response.getheaders():
                if header.lower() in PROXY_SKIP_HEADERS:
                    continue
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response_body)
        except Exception as error:
            self.send_response(502)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = f'{{"error":"API proxy failed","detail":"{str(error)}"}}'
            self.wfile.write(message.encode('utf-8'))
        finally:
            try:
                connection.close()
            except Exception:
                pass

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
        <a href="/games" class="btn">🎯 Browse All Games</a>
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

def wait_for_api_backend(timeout=15):
    """Wait until the local Flask API answers requests"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            connection = http.client.HTTPConnection(API_PROXY_HOST, API_PROXY_PORT, timeout=2)
            connection.request('GET', '/api/categories')
            response = connection.getresponse()
            response.read()
            if response.status < 500:
                return True
        except Exception:
            time.sleep(0.5)
        finally:
            try:
                connection.close()
            except Exception:
                pass
    return False

def start_api_backend():
    """Start Flask API on the proxy port for local static development"""
    env = os.environ.copy()
    env['PORT'] = str(API_PROXY_PORT)
    env.setdefault('FLASK_ENV', 'development')

    process = subprocess.Popen(
        [sys.executable, 'run.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    def _log_backend():
        if not process.stdout:
            return
        for line in process.stdout:
            print(f"[api] {line.rstrip()}")

    thread = threading.Thread(target=_log_backend)
    thread.daemon = True
    thread.start()

    if wait_for_api_backend():
        print(f"✅ API backend started on http://{API_PROXY_HOST}:{API_PROXY_PORT}")
    else:
        print(f"⚠️  API backend did not respond on http://{API_PROXY_HOST}:{API_PROXY_PORT}")

    return process

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

    parser.add_argument(
        '--no-api-proxy',
        action='store_true',
        help="Don't start or proxy the local Flask API"
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

    api_process = None
    if not args.no_api_proxy:
        api_process = start_api_backend()

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
    finally:
        if api_process and api_process.poll() is None:
            api_process.terminate()
            try:
                api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_process.kill()

if __name__ == "__main__":
    main()
