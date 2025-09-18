#!/usr/bin/env python3
"""
BTW Games Complete Website Builder
=================================

This script orchestrates the complete workflow for building the BTW Games website:
1. 🕷️  Scrape game data from onlinegames.io
2. 📁 Import data into the database
3. 🌐 Generate static HTML files
4. 🔧 Optimize for SEO
5. 📊 Generate sitemaps

Usage:
    python build_website.py [options]

Options:
    --max-games N        Maximum number of games to scrape (default: 100)
    --skip-scraping      Skip the scraping step, use existing games_data.json
    --skip-import        Skip database import, use existing data
    --skip-static        Skip static file generation
    --skip-seo           Skip SEO optimization
    --force              Force overwrite existing files
    --serve              Start development server after build
    --serve-port PORT    Port for development server (default: 8001)

Examples:
    python build_website.py                    # Full build with defaults
    python build_website.py --max-games 50     # Scrape max 50 games
    python build_website.py --skip-scraping    # Use existing JSON data
    python build_website.py --serve            # Build and start server
"""

import argparse
import json
import os
import sys
import time
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.WHITE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")

def print_step(step_num, title, description=""):
    """Print a step with formatting"""
    print(f"\n{Colors.CYAN}📋 Step {step_num}: {title}{Colors.NC}")
    if description:
        print(f"{Colors.YELLOW}   {description}{Colors.NC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}")

def run_command(command, description, check_output=False):
    """Run a command and handle errors"""
    print(f"{Colors.PURPLE}🔧 {description}...{Colors.NC}")

    try:
        if check_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=True)
            return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        if hasattr(e, 'stderr') and e.stderr:
            print_error(f"Error: {e.stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print_step("0", "Dependency Check", "Verifying required tools and packages")

    dependencies = [
        ("python", "Python interpreter"),
        ("pip", "Python package manager"),
    ]

    missing = []
    for cmd, desc in dependencies:
        if not shutil.which(cmd):
            missing.append(f"{cmd} ({desc})")

    if missing:
        print_error("Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        return False

    # Check Python packages
    try:
        import requests
        from bs4 import BeautifulSoup
        print_success("All dependencies are available")
        return True
    except ImportError as e:
        print_error(f"Missing Python package: {e}")
        print_info("Run: pip install requests beautifulsoup4")
        return False

def scrape_games(max_games=100):
    """Step 1: Scrape game data"""
    print_step("1", "Game Data Scraping", f"Scraping up to {max_games} games from onlinegames.io")

    if not os.path.exists("analyze_onlinegames_structure.py"):
        print_error("analyze_onlinegames_structure.py not found!")
        return False

    # Backup existing data if it exists
    if os.path.exists("games_data.json"):
        backup_name = f"games_data_backup_{int(time.time())}.json"
        shutil.copy("games_data.json", backup_name)
        print_info(f"Backed up existing data to {backup_name}")

    # Run scraping script
    command = f"timeout 600 python analyze_onlinegames_structure.py --max-games {max_games}"
    success = run_command(command, f"Scraping {max_games} games")

    if success and os.path.exists("games_data.json"):
        # Check scraped data
        try:
            with open("games_data.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                print_success(f"Successfully scraped {len(data)} games")
                return True
        except Exception as e:
            print_error(f"Failed to read scraped data: {e}")
            return False
    else:
        print_error("Scraping failed or no data generated")
        return False

def import_to_database():
    """Step 2: Import data to database"""
    print_step("2", "Database Import", "Importing scraped data into the database")

    if not os.path.exists("games_data.json"):
        print_error("games_data.json not found! Run scraping first.")
        return False

    if not os.path.exists("import_games_data.py"):
        print_error("import_games_data.py not found!")
        return False

    # Run import script
    success = run_command("python import_games_data.py", "Importing games to database")

    if success:
        print_success("Database import completed")
        return True
    else:
        print_error("Database import failed")
        return False

def generate_static_files():
    """Step 3: Generate static HTML files"""
    print_step("3", "Static File Generation", "Creating static HTML files for deployment")

    if not os.path.exists("generate_static_pages.py"):
        print_error("generate_static_pages.py not found!")
        return False

    # Create static_html directory if it doesn't exist
    os.makedirs("static_html", exist_ok=True)

    # Copy main templates
    templates_to_copy = [
        ("static/index.html", "static_html/index.html"),
        ("static/games.html", "static_html/games.html"),
        ("static/assets", "static_html/assets"),
    ]

    for src, dst in templates_to_copy:
        if os.path.exists(src):
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print_info(f"Copied {src} → {dst}")

    # Generate individual game pages
    success = run_command("python generate_static_pages.py", "Generating individual game pages")

    if success:
        print_success("Static file generation completed")
        return True
    else:
        print_error("Static file generation failed")
        return False

def optimize_seo():
    """Step 4: SEO Optimization"""
    print_step("4", "SEO Optimization", "Optimizing meta tags and structured data")

    if not os.path.exists("optimize_seo.py"):
        print_error("optimize_seo.py not found!")
        return False

    success = run_command("python optimize_seo.py", "Optimizing SEO")

    if success:
        print_success("SEO optimization completed")
        return True
    else:
        print_error("SEO optimization failed")
        return False

def update_data_files():
    """Step 5: Update supporting data files"""
    print_step("5", "Data Files Update", "Updating slugs, sitemaps, and supporting files")

    scripts = [
        ("update_game_slugs.py", "Updating game slugs"),
        ("update_sitemap.py", "Updating sitemap"),
    ]

    for script, description in scripts:
        if os.path.exists(script):
            success = run_command(f"python {script}", description)
            if not success:
                print_warning(f"Failed to run {script}, continuing...")
        else:
            print_warning(f"{script} not found, skipping...")

    print_success("Data files updated")
    return True

def cleanup_and_finalize():
    """Step 6: Cleanup and finalization"""
    print_step("6", "Cleanup & Finalization", "Cleaning up temporary files and finalizing build")

    # Remove any temporary files
    temp_files = [
        "*.pyc",
        "__pycache__",
        "*.tmp",
    ]

    # Count files in static_html
    if os.path.exists("static_html"):
        total_files = sum(len(files) for _, _, files in os.walk("static_html"))
        total_dirs = sum(len(dirs) for _, dirs, _ in os.walk("static_html"))

        print_info(f"Generated {total_files} files in {total_dirs} directories")

        # Check key files
        key_files = ["index.html", "games.html", "sitemap.xml", "robots.txt"]
        for file in key_files:
            if os.path.exists(f"static_html/{file}"):
                print_success(f"✓ {file}")
            else:
                print_warning(f"✗ {file} missing")

    print_success("Build finalized")
    return True

def serve_website(port=8001):
    """Start development server"""
    print_step("7", "Development Server", f"Starting server on port {port}")

    if not os.path.exists("static_html/index.html"):
        print_error("Static files not found! Run build first.")
        return False

    try:
        if os.path.exists("serve_static.py"):
            command = f"python serve_static.py --port {port}"
            print_info(f"Starting server: {command}")
            print_info(f"Visit: http://localhost:{port}")
            print_info("Press Ctrl+C to stop")
            subprocess.run(command, shell=True)
        else:
            # Fallback to Python's built-in server
            os.chdir("static_html")
            command = f"python -m http.server {port}"
            print_info(f"Starting basic server: {command}")
            print_info(f"Visit: http://localhost:{port}")
            subprocess.run(command, shell=True)
    except KeyboardInterrupt:
        print_info("\nServer stopped by user")
    except Exception as e:
        print_error(f"Failed to start server: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="BTW Games Complete Website Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("--max-games", type=int, default=100,
                        help="Maximum number of games to scrape (default: 100)")
    parser.add_argument("--skip-scraping", action="store_true",
                        help="Skip the scraping step")
    parser.add_argument("--skip-import", action="store_true",
                        help="Skip database import")
    parser.add_argument("--skip-static", action="store_true",
                        help="Skip static file generation")
    parser.add_argument("--skip-seo", action="store_true",
                        help="Skip SEO optimization")
    parser.add_argument("--force", action="store_true",
                        help="Force overwrite existing files")
    parser.add_argument("--serve", action="store_true",
                        help="Start development server after build")
    parser.add_argument("--serve-port", type=int, default=8001,
                        help="Port for development server (default: 8001)")

    args = parser.parse_args()

    # Print header
    print_header("🚀 BTW Games Website Builder")
    print(f"{Colors.WHITE}Building complete gaming website with automated pipeline{Colors.NC}")

    start_time = time.time()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    success_steps = 0
    total_steps = 0

    try:
        # Step 1: Scraping
        if not args.skip_scraping:
            total_steps += 1
            if scrape_games(args.max_games):
                success_steps += 1
            else:
                print_error("Scraping failed! Aborting.")
                sys.exit(1)

        # Step 2: Database Import
        if not args.skip_import:
            total_steps += 1
            if import_to_database():
                success_steps += 1
            else:
                print_error("Database import failed! Aborting.")
                sys.exit(1)

        # Step 3: Static Generation
        if not args.skip_static:
            total_steps += 1
            if generate_static_files():
                success_steps += 1
            else:
                print_error("Static generation failed! Aborting.")
                sys.exit(1)

        # Step 4: SEO Optimization
        if not args.skip_seo:
            total_steps += 1
            if optimize_seo():
                success_steps += 1
            else:
                print_warning("SEO optimization failed, continuing...")

        # Step 5: Update data files
        total_steps += 1
        if update_data_files():
            success_steps += 1

        # Step 6: Cleanup
        total_steps += 1
        if cleanup_and_finalize():
            success_steps += 1

        # Calculate build time
        build_time = time.time() - start_time

        # Print summary
        print_header("🎉 Build Complete!")
        print(f"{Colors.GREEN}✅ Success: {success_steps}/{total_steps} steps completed{Colors.NC}")
        print(f"{Colors.BLUE}⏱️  Build time: {build_time:.1f} seconds{Colors.NC}")

        if os.path.exists("static_html"):
            print(f"{Colors.CYAN}📁 Output: static_html/ directory{Colors.NC}")
            print(f"{Colors.CYAN}🌐 Ready for deployment!{Colors.NC}")

        # Start server if requested
        if args.serve:
            serve_website(args.serve_port)

    except KeyboardInterrupt:
        print_error("\nBuild interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()