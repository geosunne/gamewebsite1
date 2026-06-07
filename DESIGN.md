---
name: BTW Games
description: Fast, playful, trustworthy browser game portal for casual players and students.
colors:
  play-blue: "#007AFF"
  trust-ink: "#1C1C1E"
  soft-gray: "#8E8E93"
  cloud-bg: "#F2F2F7"
  surface: "#FFFFFF"
  success-green: "#34C759"
  alert-red: "#FF3B30"
typography:
  display:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "42px"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "normal"
  headline:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "36px"
    fontWeight: 600
    lineHeight: 1.2
  title:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.25
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 500
    lineHeight: 1.4
rounded:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "20px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "20px"
  xl: "30px"
  section: "60px"
components:
  button-primary:
    backgroundColor: "{colors.play-blue}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    padding: "12px 20px"
  card-game:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.trust-ink}"
    rounded: "{rounded.md}"
    padding: "0"
  panel-filter:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.trust-ink}"
    rounded: "{rounded.lg}"
    padding: "30px"
  input-search:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.trust-ink}"
    rounded: "{rounded.sm}"
    padding: "16px 20px"
---

# Design System: BTW Games

## 1. Overview

**Creative North Star: "Play Arcade"**

BTW Games currently uses a clean Apple-inspired surface system: white panels, light gray page backgrounds, system typography, soft cards, and one bright blue action color. This gives the site a trustworthy base, but future work should make it feel more like a lively browser game portal: faster, more playful, and richer in color without moving toward casino, preschool, or dark esports cues.

The next design direction should keep the current clarity and low-friction browsing, then add controlled arcade energy through category color roles, thumbnail-led layouts, sharper section rhythm, and small motion on cards and filters. The site should feel fun enough for children and students, but credible enough for parents, teachers, and casual adult players.

**Key Characteristics:**
- Clean white surfaces with vivid blue as the current trust anchor.
- Game thumbnails carry most visual variety.
- Cards and filters are simple, rounded, and quick to scan.
- Future color work should use a full palette in measured roles, not random decoration.
- Motion should signal play and response, never block access to content.

## 2. Colors

The current palette is restrained Apple blue on white and soft gray. The preferred evolution is a richer "Play Arcade" palette: blue remains the trust anchor, with green, coral, yellow, and violet used as category or state accents.

### Primary
- **Play Blue** (#007AFF): Current primary action color. Use for main links, selected filters, primary CTAs, and trustworthy system cues.

### Secondary
- **Success Green** (#34C759): Current positive state color. Use for safe badges, availability, and light success feedback. It can become a puzzle or casual category accent in future UI.
- **Alert Red** (#FF3B30): Current warning color. Use sparingly for destructive or error states only. Do not use it for urgency or casino-like attention.

### Tertiary
- **Future Arcade Accents:** Add richer category accents in implementation, such as sunny yellow, berry violet, and coral, but keep each role named and purposeful. Do not introduce neon gradients or jackpot-style red-and-gold pairings.

### Neutral
- **Trust Ink** (#1C1C1E): Main text and high-priority UI labels.
- **Soft Gray** (#8E8E93): Supporting text. Use with care because it can fail contrast on tinted backgrounds.
- **Cloud Background** (#F2F2F7): Page background and quiet dividers.
- **Surface White** (#FFFFFF): Cards, nav, filters, and game containers.

### Named Rules
**The Thumbnail First Rule.** Game thumbnails provide the richest visual diversity. UI colors organize and guide, they do not compete with game artwork.

**The No Casino Rule.** Never combine red, gold, black, and glow effects in ways that suggest betting, jackpots, rewards, or false urgency.

**The Color Role Rule.** Every new accent needs a role: category, state, or action. No decorative color added only to fill space.

## 3. Typography

**Display Font:** System UI stack, with Apple, Segoe UI, Roboto, Helvetica, Arial fallbacks.
**Body Font:** System UI stack.
**Label/Mono Font:** No distinct label or mono family is currently used.

**Character:** The typography is practical, familiar, and fast. It should stay readable for students and children, with stronger hierarchy added through weight, size, and spacing rather than decorative fonts.

### Hierarchy
- **Display** (700, 42px, 1.15): Page titles and major landing headings. Future hero work may use `clamp()`, maxing at 6rem.
- **Headline** (600, 36px, 1.2): Section titles such as game groups and content sections.
- **Title** (600, 20px, 1.25): Card titles, feature headings, and filter panel headings.
- **Body** (400, 16px, 1.6): Descriptions and supporting copy. Keep long prose within 65 to 75ch.
- **Label** (500, 14px, 1.4): Result counts, filter labels, badges, and compact UI text.

### Named Rules
**The Fast Scan Rule.** A player should understand a game card from its thumbnail and title without reading body copy.

**The No Shouting Rule.** Avoid all-caps body copy and oversized display type. Playful does not mean loud.

## 4. Elevation

The current system uses soft ambient shadows to separate cards, filters, the sticky header, and game containers from the page background. This is acceptable for trust and clarity, but future passes should reduce broad shadow blur on repeated cards and use color, spacing, and thumbnail depth for playfulness.

### Shadow Vocabulary
- **Ambient Low** (`0 2px 15px rgba(0, 0, 0, 0.1)`): Current default for header, cards, filters, and content panels.
- **Ambient High** (`0 10px 40px rgba(0, 0, 0, 0.15)`): Current hover or major container shadow. Use only for game frame, overlays, or active hover states.

### Named Rules
**The State Shadow Rule.** Repeated game cards should be mostly flat at rest. Stronger shadow belongs to hover, focus, or active play surfaces.

## 5. Components

### Buttons
- **Shape:** Rounded rectangle, usually 12px. Pills are acceptable for filters and compact chips.
- **Primary:** Play Blue background, Surface White text, medium padding.
- **Hover / Focus:** Use a clear color or outline shift, plus small transform only when reduced motion is not requested.
- **Secondary / Ghost:** Use white or transparent backgrounds with Play Blue text and clear focus rings.

### Chips
- **Style:** Filter chips use rounded outlines or filled selected states.
- **State:** Selected chips should use Play Blue or a named category accent with enough contrast. Do not rely on color alone; include weight, border, or icon state.

### Cards / Containers
- **Corner Style:** Game and content cards currently use 16px to 20px. Future cards should stay at 16px or below unless they are large play surfaces.
- **Background:** Surface White on Cloud Background.
- **Shadow Strategy:** Ambient Low at rest, Ambient High only on major hover or game container states.
- **Border:** Prefer subtle full borders or no border. Do not use colored side stripes.
- **Internal Padding:** 30px for panels, compact card interiors for game grids.

### Inputs / Fields
- **Style:** White surface, 2px Cloud Background border, 12px radius, 16px vertical padding.
- **Focus:** Play Blue border. Add a visible outline or subtle focus ring in future passes.
- **Error / Disabled:** Error should use Alert Red with text, icon, or helper copy. Disabled fields need opacity plus cursor and label state.

### Navigation
- **Style:** Sticky white header with system typography, Play Blue logo, dark text links, and hover color shift.
- **Mobile:** Hamburger menu should stay simple, with generous tap targets and clear open state.

### Game Cards
- **Character:** Fast, visual, thumbnail-led.
- **Behavior:** Entire card may be clickable, but focus states must be visible and keyboard reachable.
- **Future Color:** Add category accents as small tags or bottom bars only when they improve scanning. Avoid casino-like badges.

## 6. Do's and Don'ts

### Do:
- **Do** keep Play Blue (#007AFF) as the trust anchor until a richer palette is implemented.
- **Do** add color through named category roles, for example action, puzzle, racing, cooking, and casual.
- **Do** keep text contrast at WCAG AA or better, especially Soft Gray (#8E8E93) on light or tinted backgrounds.
- **Do** use thumbnails as the main source of visual variety.
- **Do** use small, responsive hover and focus motion that respects `prefers-reduced-motion`.
- **Do** keep card radii at 16px or below for repeated grids, and reserve 20px for large panels.

### Don't:
- **Don't** use casino or betting visual language, including dark neon, jackpot cues, slot-machine energy, aggressive red-and-gold urgency, and misleading reward patterns.
- **Don't** make the site low-childhood, toy-like, mascot-heavy, or preschool in tone.
- **Don't** use dark esports styling, heavy black backgrounds, smoky gradients, or hostile shooter-lobby tone.
- **Don't** use gradient text.
- **Don't** use colored side-stripe borders on cards, alerts, or list items.
- **Don't** pair a 1px decorative border with a broad 16px+ blur shadow on the same repeated card.
- **Don't** add random color accents without category, state, or action meaning.
