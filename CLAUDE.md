# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a single-page web application for "Monster Survivors," a browser-based survival game hosted by AIQun Games. The project consists of a static HTML website that embeds a Unity game via iframe.

## Project Structure

- `index.html` - Main webpage containing the complete application (HTML, CSS, JavaScript)
- `ads.txt` - Google AdSense configuration file for ad serving

## Architecture

The project is a self-contained static website with:

- **Frontend**: Pure HTML/CSS/JavaScript (no build system or framework)
- **Game Integration**: Unity game embedded via iframe from `cloud.onlinegames.io`
- **Styling**: CSS-in-HTML with Apple-inspired design system using CSS custom properties
- **Monetization**: Google AdSense integration with client ID `ca-pub-8930741225505243`

## Key Features

- Responsive design with mobile-first approach
- SEO optimized with Open Graph and Twitter Card meta tags
- Smooth scrolling navigation
- Mobile hamburger menu
- Game loading states and error handling
- Performance optimizations (lazy loading, backdrop blur effects)

## Development Workflow

Since this is a static HTML project:

1. **Local Development**: Open `index.html` directly in a browser or use a simple HTTP server
2. **Testing**: Manual testing across different devices and browsers
3. **Deployment**: Direct file upload to web hosting (no build process required)

## Content Management

- Game controls and features are hardcoded in the HTML
- All styling is embedded in the `<style>` section of `index.html`
- JavaScript functionality is embedded in the `<script>` section
- No external dependencies beyond Google AdSense

## Hosting Configuration

- Game iframe source: `https://cloud.onlinegames.io/games/2025/unity/monster-survivors/index-og.html`
- Canonical URL: `https://aiqun.com`
- AdSense publisher ID configured in `ads.txt`

## Common Tasks

- **Update game controls**: Modify the controls grid in the "How to Play" section
- **Change game features**: Edit the features grid cards
- **Update styling**: Modify CSS custom properties in the `:root` section
- **Add new sections**: Insert new HTML sections following the existing container pattern
- **Mobile optimization**: Test responsive breakpoints at 768px and 480px