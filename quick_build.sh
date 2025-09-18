#!/bin/bash

# BTW Games Quick Build Script
# ===========================
# Fast build pipeline for development

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}🚀 BTW Games Quick Build${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_step() {
    echo -e "\n${CYAN}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Default values
MAX_GAMES=50
SKIP_SCRAPING=false
SERVE=false
PORT=8001

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --max-games)
            MAX_GAMES="$2"
            shift 2
            ;;
        --skip-scraping)
            SKIP_SCRAPING=true
            shift
            ;;
        --serve)
            SERVE=true
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --max-games N      Max games to scrape (default: 50)"
            echo "  --skip-scraping    Use existing games_data.json"
            echo "  --serve            Start server after build"
            echo "  --port N           Server port (default: 8001)"
            echo "  -h, --help         Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_header

START_TIME=$(date +%s)

# Step 1: Scraping (optional)
if [ "$SKIP_SCRAPING" = false ]; then
    print_step "Step 1: Scraping $MAX_GAMES games"
    if timeout 300 python analyze_onlinegames_structure.py --max-games $MAX_GAMES; then
        print_success "Scraping completed"
    else
        print_error "Scraping failed!"
        exit 1
    fi
else
    print_step "Step 1: Using existing games data"
    if [ ! -f "games_data.json" ]; then
        print_error "games_data.json not found! Remove --skip-scraping or run scraping first."
        exit 1
    fi
    print_success "Using existing games_data.json"
fi

# Step 2: Import to database
print_step "Step 2: Importing to database"
if python import_games_data.py; then
    print_success "Database import completed"
else
    print_error "Database import failed!"
    exit 1
fi

# Step 3: Copy templates
print_step "Step 3: Preparing static files"
mkdir -p static_html

# Copy main files
cp static/index.html static_html/
cp static/games.html static_html/
cp -r static/assets static_html/ 2>/dev/null || true

print_success "Templates copied"

# Step 4: Generate game pages
print_step "Step 4: Generating game pages"
if python generate_static_pages.py; then
    print_success "Game pages generated"
else
    print_error "Game page generation failed!"
    exit 1
fi

# Step 5: SEO optimization
print_step "Step 5: SEO optimization"
if python optimize_seo.py; then
    print_success "SEO optimization completed"
else
    print_info "SEO optimization failed, continuing..."
fi

# Step 6: Update supporting files
print_step "Step 6: Updating data files"
python update_game_slugs.py 2>/dev/null || print_info "update_game_slugs.py not found, skipping"
python update_sitemap.py 2>/dev/null || print_info "update_sitemap.py not found, skipping"
print_success "Data files updated"

# Calculate build time
END_TIME=$(date +%s)
BUILD_TIME=$((END_TIME - START_TIME))

# Summary
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}🎉 Build Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "${YELLOW}⏱️  Build time: ${BUILD_TIME} seconds${NC}"

if [ -d "static_html" ]; then
    FILE_COUNT=$(find static_html -type f | wc -l)
    echo -e "${CYAN}📁 Generated $FILE_COUNT files in static_html/${NC}"
    echo -e "${CYAN}🌐 Ready for deployment!${NC}"
fi

# Start server if requested
if [ "$SERVE" = true ]; then
    echo -e "\n${PURPLE}🚀 Starting development server...${NC}"
    if [ -f "serve_static.py" ]; then
        python serve_static.py --port $PORT
    else
        echo -e "${YELLOW}serve_static.py not found, using basic server${NC}"
        cd static_html
        python -m http.server $PORT
    fi
fi