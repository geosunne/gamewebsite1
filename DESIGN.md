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
  muted: "#6D7890"
  line: "#DBE5F5"
  line-strong: "#C4D2E6"
  page: "#F5F9FF"
  page-tint: "#EEF6FF"
  surface: "#FFFFFF"
  surface-coral: "#FFF0EB"
  surface-yellow: "#FFF8D9"
  surface-green: "#EAF9F1"
  surface-violet: "#F1EDFF"
  surface-sky: "#EAF6FF"
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
    letterSpacing: "-0.02em"
  title:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 850
    lineHeight: 1.18
    letterSpacing: "0"
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0"
  label:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"
    fontSize: "0.9rem"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "0"
rounded:
  sm: "8px"
  md: "12px"
  lg: "16px"
  pill: "999px"
spacing:
  space-1: "4px"
  space-2: "8px"
  space-3: "12px"
  space-4: "16px"
  space-5: "24px"
  space-6: "32px"
  space-7: "48px"
  space-8: "64px"
components:
  button-primary:
    backgroundColor: "{colors.brand-coral}"
    textColor: "{colors.surface}"
    rounded: "{rounded.pill}"
    padding: "11px 18px"
    height: "44px"
  button-secondary:
    backgroundColor: "{colors.surface-coral}"
    textColor: "{colors.brand-coral-dark}"
    rounded: "{rounded.pill}"
    padding: "9px 14px"
    height: "40px"
  search-input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0 16px"
    height: "48px"
  game-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "0"
  home-game-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "0"
  intent-chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "8px 13px"
---

# Design System: BTW game

## 1. Overview

**Creative North Star: "The Quick-Play Shelf"**

BTW game means "By the way, play a quick game." The visual system is a bright, compact game shelf for casual players, children, and students who need to recognize a fun option fast. The site should feel lively through thumbnails, category color, and quick interactions, not through noisy decoration.

The current direction is a clean catalog structure with richer arcade color. Home is not a marketing landing page. Home is a high-density discovery surface with a preserved left navigation rail, a compact search-and-category strip, and a wide game shelf that exposes many playable choices above the fold. Detail pages put the game stage first, then title, metadata, Play next, and concise support information.

The system explicitly rejects casino or betting visual language, including dark neon, jackpot cues, slot-machine energy, aggressive red-and-gold urgency, and misleading reward patterns. It also rejects overly childish preschool styling, toy-like clutter, mascot-heavy UI, dark esports aesthetics, heavy black backgrounds, smoky gradients, and hostile shooter-lobby tone.

**Key Characteristics:**
- Fast scan density: show games early, with minimal marketing copy.
- Playful but controlled: color supports category, state, and action.
- Trust before clicks: predictable navigation, visible titles, clear metadata.
- Light and safe: no black-first theme, no betting cues, no hostile lobby mood.
- Thumbnail-led variety: game art carries most of the visual diversity.

## 2. Colors

The palette is light, coral-led, and full enough to feel game-like without becoming noisy. Coral is the action color; yellow, violet, sky, and green provide category variety and status.

### Primary
- **Play Coral**: Primary brand color for the logo mark, primary buttons, focus system, selected states, and decisive action moments.
- **Coral Dark**: High-contrast text on coral-tinted surfaces, breadcrumbs, active navigation, and secondary action labels.
- **Arcade Orange**: Used with coral in the brand mark and primary button gradients only. It should add warmth, not become the dominant theme.

### Secondary
- **Sunny Yellow**: Casual, arcade, quick-break, and warm shelf surfaces.
- **Puzzle Violet**: Puzzle, strategy, featured badges, and richer game-category contrast.
- **Sky Blue**: Racing, sports, information, and trust cues. Sky Blue is never the primary brand color.
- **Safe Green**: Positive safety states, new badges, check icons, and friendly proof points.

### Neutral
- **Ink**: Main text and headings. Use this whenever readability matters.
- **Ink Soft**: Secondary copy, card descriptions, and metadata.
- **Muted**: Low-priority labels and counts only.
- **Line and Line Strong**: Structural borders for cards, inputs, rails, and panels.
- **Page and Page Tint**: Light app background. Background warmth comes from coral and yellow accents, not beige defaults.
- **Surface**: Cards, rails, inputs, and panels.
- **Tinted Surfaces**: Coral, yellow, green, violet, and sky tints are for category chips, lanes, proof blocks, and soft panels.

### Named Rules

**The Coral Action Rule.** Coral owns primary action, active state, logo energy, and focus. Do not let blue become the main CTA color.

**The Thumbnail Variety Rule.** When a screen feels flat, increase useful game thumbnails or category tints before adding unrelated decoration.

**The No Casino Palette Rule.** Never use red-and-gold urgency, black neon, jackpot shine, or slot-machine color logic.

## 3. Typography

**Display Font:** system sans stack with `-apple-system`, BlinkMacSystemFont, Segoe UI, system-ui, sans-serif.
**Body Font:** the same system sans stack.
**Label/Mono Font:** no separate mono font.

**Character:** Dense, friendly, and highly legible. The type should feel like a polished app catalog, not a magazine, casino, preschool toy shelf, or esports lobby.

### Hierarchy
- **Display** (850, `clamp(2.45rem, 5vw, 4.9rem)`, 1.02): Page-scale statements only. Do not use display scale inside compact panels or cards.
- **Headline** (850, `clamp(1.6rem, 3vw, 2.25rem)`, 1.15): Section headers such as Top games, New games, and catalog titles.
- **Title** (850, `1.05rem`, 1.18): Game card titles, lane labels, compact panel headers, and navigation emphasis.
- **Body** (400, `1rem`, 1.6): Descriptive copy, FAQ text, and game descriptions. Keep long copy near 65 to 75ch.
- **Label** (800, `0.9rem`, 1.2): Buttons, chips, badges, metadata, filters, and side rail items.

### Named Rules

**The Compact Surface Rule.** Cards, sidebars, chips, and toolbars use title or label scale, never hero-scale typography.

**The No Tracked Eyebrow Rule.** Do not repeat tiny uppercase tracked labels above every section. The site may use one clear brand kicker, but section rhythm must come from density, spacing, and thumbnails.

## 4. Elevation

BTW game uses a hybrid of borders, soft tinted surfaces, and compact shadows. Static surfaces are mostly defined by a 1px line and light fill. Shadows are reserved for sticky headers, rails, panel lift, hover feedback, and the large game stage on detail pages.

### Shadow Vocabulary
- **Low Surface** (`0 2px 8px rgba(23, 32, 51, 0.08)`): Rails, cards, info panels, and quiet containers.
- **Tight Hover** (`0 4px 8px rgba(23, 32, 51, 0.1)`): Game card hover and compact lift.
- **Mid Popover** (`0 10px 20px rgba(23, 32, 51, 0.12)`): Mobile nav dropdown and elevated overlays.
- **Stage Lift** (`0 14px 28px rgba(23, 32, 51, 0.14)`): Game iframe container only.
- **Coral Action Glow** (`0 6px 12px rgba(240, 90, 63, 0.22)`): Primary buttons and the logo mark.

### Named Rules

**The Border-First Rule.** Use a full 1px border plus surface tint for structure. Never use a colored side stripe.

**The Compact Shadow Rule.** Card shadows stay tight. If the blur exceeds 16px on a normal card, the component is too decorative.

## 5. Components

### Buttons
- **Shape:** Full pill for actions (`999px` radius).
- **Primary:** Coral-to-red-orange fill, white text, 44px minimum height, bold label, compact glow.
- **Hover / Focus:** Hover lifts by 1px with a stronger coral glow. Focus uses a 4px translucent coral ring.
- **Secondary:** Light coral surface, coral dark text, 1px coral-tint border, 40px minimum height.

### Chips
- **Style:** Intent chips and metadata pills are full pills with 1px borders, dense padding, and bold labels.
- **Color:** Category chips may use coral, yellow, violet, sky, and green tints. Selected or action states must be visibly active through fill and contrast, not color alone.
- **Density:** Chips should stay scan-friendly. Keep label text short and avoid explanatory copy inside chips.

### Cards / Containers
- **Corner Style:** Game cards use 16px radius in general grids and 12px radius in high-density homepage grids.
- **Background:** Cards use white surfaces with thumbnail-led visual interest. Fallback thumbnails use soft yellow, coral, and sky gradients.
- **Shadow Strategy:** Resting cards use border structure. Hover may use Tight Hover only.
- **Border:** Full 1px borders. Colored side stripes are prohibited.
- **Internal Padding:** Game cards have no outer padding; the thumbnail is the card.

### Inputs / Fields
- **Style:** White surface, 1px strong line border, 12px radius, 48px minimum height.
- **Focus:** Use the coral focus ring. Do not switch the focus system to blue.
- **Placeholder:** Placeholder text must remain readable, darker than pale gray.

### Navigation
- **Header:** Sticky, white translucent surface with subtle border and blur. The header stays practical and compact.
- **Side rail:** Desktop homepage keeps the left rail visible. Rail panels are 200px wide in the high-density home layout, sticky below the header, and use compact nav rows.
- **Mobile:** Side rail collapses away below 980px. The mobile menu uses a 44px circular control and a full-width dropdown.
- **Active state:** Active nav items use coral dark text on a coral-tinted background.

### Home Discovery Shelf

Home uses a compact discovery panel instead of a large marketing hero. It contains a short brand kicker, a direct headline, search, and horizontally scrolling intent chips. The page container may widen to 1360px to preserve the left rail while increasing game density.

### Game Cards

Game thumbnails are the primary content. Homepage game cards use a compact 16:10 thumbnail, 12px radius, dense gaps, and occasional spotlight cards that span two columns and two rows. Titles sit on a dark gradient overlay inside the thumbnail.

### Game Detail Stage

Game detail pages use a large playable iframe first, with title, breadcrumbs, actions, and metadata immediately below. Desktop detail pages include a sticky Play next panel on the right. Supporting proof points, descriptions, controls, and related games follow the stage.

## 6. Do's and Don'ts

### Do:
- **Do** keep the homepage as a high-density game shelf with visible games above the fold.
- **Do** preserve the desktop left side rail on home and catalog-like surfaces unless the viewport requires collapse.
- **Do** use the 1360px container when the page needs both navigation and dense game display.
- **Do** let thumbnails carry visual variety before adding decorative backgrounds.
- **Do** use coral for primary actions, focus, and selected states.
- **Do** keep body text on tinted surfaces dark enough for WCAG AA contrast.
- **Do** keep mobile layouts two-column for game grids when titles still fit.
- **Do** support reduced motion. Hover lifts and transitions must have a reduced-motion fallback.

### Don't:
- **Don't** use casino or betting visual language, including dark neon, jackpot cues, slot-machine energy, aggressive red-and-gold urgency, and misleading reward patterns.
- **Don't** use overly childish preschool styling, toy-like clutter, or mascot-heavy UI.
- **Don't** use dark esports aesthetics, heavy black backgrounds, smoky gradients, or hostile shooter-lobby tone.
- **Don't** make blue the main brand or CTA color. Sky Blue is a support color only.
- **Don't** replace game thumbnails with unrelated decoration or empty colored panels when real thumbnails exist.
- **Don't** use gradient text, glass cards as a default, colored side-stripe cards, or repeated tiny uppercase section eyebrows.
- **Don't** nest cards inside cards. Use spacing, dividers, and full-width panels instead.
- **Don't** make homepage hero copy push games far below the fold.
