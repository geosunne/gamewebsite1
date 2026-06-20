---
name: BTW game
description: Fast, playful, trustworthy browser game portal for quick casual play.
colors:
  brand-coral: "#F05A3F"
  brand-coral-dark: "#B92E1E"
  brand-orange: "#FF9F1C"
  brand-yellow: "#FFD84D"
  brand-violet: "#7B4EF6"
  brand-sky: "#1388D8"
  brand-green: "#1F9D62"
  ink: "#172033"
  ink-soft: "#4E5C73"
  page: "#F5F9FF"
  surface: "#FFFFFF"
typography:
  display:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "clamp(2.45rem, 5vw, 4.9rem)"
    fontWeight: 850
    lineHeight: 1.02
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "clamp(1.6rem, 3vw, 2.25rem)"
    fontWeight: 850
    lineHeight: 1.15
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  sm: "8px"
  md: "12px"
  lg: "16px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  section: "64px"
components:
  button-primary:
    backgroundColor: "{colors.brand-coral}"
    textColor: "{colors.surface}"
    rounded: "999px"
    padding: "11px 18px"
  card-game:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "0"
  panel-filter:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "24px"
---

# Design System: BTW game

## Creative North Star

BTW game means "By the way, play a quick game." The interface should feel like a light, colorful game shelf: fast to scan, friendly for casual players and students, and trustworthy enough for repeated use.

The current direction is a C + A hybrid: a clean App Store style catalog structure with richer arcade category color. The background stays light, the game thumbnails carry most of the visual variety, and Coral is the primary brand color for logo, buttons, focus, and selected states.

## Color Roles

- **Play Coral (#F05A3F):** Primary brand color, logo mark, CTA, selected category, focus system.
- **Coral Dark (#B92E1E):** High-contrast text on light coral surfaces.
- **Sunny Yellow (#FFD84D):** Casual and quick-break category energy.
- **Puzzle Violet (#7B4EF6):** Puzzle, strategy, and featured badges.
- **Sky Blue (#1388D8):** Racing, sports, information, and trust cues only. It is not the primary brand color.
- **Safe Green (#1F9D62):** Positive and safe states.
- **Ink (#172033):** Main text. Avoid pale gray text on tinted surfaces.

## Component Rules

- Repeated game cards use 16px radius, full borders, compact shadows only on hover.
- Primary buttons are coral pills. Secondary buttons use light coral surfaces with dark coral text.
- Category chips use color by category, but selected state is always visibly active through fill and contrast, not color alone.
- Search and filters stay practical and dense. The player should reach games quickly.
- The site does not use black backgrounds, casino red/gold urgency, neon glow, mascot-heavy styling, gradient text, glass cards, or colored side-stripe cards.

## Layout Rules

- Homepage first viewport: brand, search, category lanes, and direct links to the catalog. No heavy marketing-only hero.
- Games catalog: desktop uses a sticky category rail and a compact card grid. Mobile collapses to stacked filters and two-column game cards.
- Game detail: large playable frame first, metadata nearby, concise game information, then related games.
- Public URLs are clean: `/games/{slug}`, no `.html`, no trailing slash in canonical URLs.
