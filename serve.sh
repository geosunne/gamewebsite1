#!/bin/bash

# BTW Games Static Server Quick Launcher
# =====================================
#
# This script provides a quick way to start the static development server
# Usage: ./serve.sh [port]

set -e

# Default port
PORT=${1:-8000}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Print header
echo "🚀 BTW Games Static Development Server"
echo "======================================"

# Check if static_html directory exists
if [ ! -d "static_html" ]; then
    print_error "static_html directory not found!"
    print_error "Please run this script from the project root directory."
    print_error "Make sure you have generated the static files first."
    exit 1
fi

if [ ! -f "static_html/index.html" ]; then
    print_error "index.html not found in static_html directory!"
    print_error "Please generate the static files first."
    exit 1
fi

# Check if port is in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port $PORT is already in use!"
    print_status "Trying to find an available port..."

    # Find next available port
    NEXT_PORT=$((PORT + 1))
    while lsof -Pi :$NEXT_PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
        NEXT_PORT=$((NEXT_PORT + 1))
        if [ $NEXT_PORT -gt $((PORT + 100)) ]; then
            print_error "Could not find an available port in range $PORT-$((PORT + 100))"
            exit 1
        fi
    done

    PORT=$NEXT_PORT
    print_status "Using port $PORT instead"
fi

print_status "Starting server on port $PORT..."
print_status "Serving: $(pwd)/static_html"

# Check if Python static server script exists
if [ -f "serve_static.py" ]; then
    print_status "Using custom Python server..."
    python3 serve_static.py --port $PORT
else
    print_status "Using Python built-in server..."
    print_status "URL: http://localhost:$PORT"
    print_status "Press Ctrl+C to stop the server"
    echo "======================================"

    # Change to static_html directory and serve
    cd static_html

    # Try to open browser automatically
    if command -v open >/dev/null 2>&1; then
        # macOS
        sleep 2 && open "http://localhost:$PORT" &
    elif command -v xdg-open >/dev/null 2>&1; then
        # Linux
        sleep 2 && xdg-open "http://localhost:$PORT" &
    elif command -v start >/dev/null 2>&1; then
        # Windows
        sleep 2 && start "http://localhost:$PORT" &
    fi

    # Start Python HTTP server
    if python3 -c "import http.server" 2>/dev/null; then
        python3 -m http.server $PORT
    elif python -c "import http.server" 2>/dev/null; then
        python -m http.server $PORT
    else
        print_error "Python HTTP server module not found!"
        exit 1
    fi
fi