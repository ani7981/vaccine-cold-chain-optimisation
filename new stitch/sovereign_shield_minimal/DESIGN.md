---
name: Sovereign Shield Minimal
colors:
  surface: '#111317'
  surface-dim: '#111317'
  surface-bright: '#37393e'
  surface-container-lowest: '#0c0e12'
  surface-container-low: '#1a1c20'
  surface-container: '#1e2024'
  surface-container-high: '#282a2e'
  surface-container-highest: '#333539'
  on-surface: '#e2e2e8'
  on-surface-variant: '#cac6bd'
  inverse-surface: '#e2e2e8'
  inverse-on-surface: '#2f3035'
  outline: '#939188'
  outline-variant: '#484740'
  surface-tint: '#cac6bf'
  primary: '#ffffff'
  on-primary: '#31302b'
  primary-container: '#e6e2da'
  on-primary-container: '#66645e'
  inverse-primary: '#605e58'
  secondary: '#cec5b7'
  on-secondary: '#343026'
  secondary-container: '#4b463b'
  on-secondary-container: '#bcb4a6'
  tertiary: '#ffffff'
  on-tertiary: '#213337'
  tertiary-container: '#d2e6eb'
  on-tertiary-container: '#55686b'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e6e2da'
  primary-fixed-dim: '#cac6bf'
  on-primary-fixed: '#1c1c17'
  on-primary-fixed-variant: '#484741'
  secondary-fixed: '#eae1d2'
  secondary-fixed-dim: '#cec5b7'
  on-secondary-fixed: '#1f1b12'
  on-secondary-fixed-variant: '#4b463b'
  tertiary-fixed: '#d2e6eb'
  tertiary-fixed-dim: '#b6cace'
  on-tertiary-fixed: '#0b1e22'
  on-tertiary-fixed-variant: '#374a4e'
  background: '#111317'
  on-background: '#e2e2e8'
  surface-variant: '#333539'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 44px
    fontWeight: '600'
    lineHeight: 52px
    letterSpacing: -0.03em
  display-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '500'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 26px
    fontWeight: '500'
    lineHeight: 34px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 22px
    fontWeight: '500'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 24px
    letterSpacing: 0em
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Hanken Grotesk
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.06em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '500'
    lineHeight: 12px
    letterSpacing: 0.08em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  space-xxs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-base: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  space-3xl: 4rem
  gutter-mobile: 1rem
  gutter-tablet: 1.5rem
  gutter-desktop: 2rem
  margin-mobile: 1rem
  margin-tablet: 2rem
  margin-desktop: 3rem
---

## Brand & Style

This design system embodies austere precision, clinical reliability, and quiet institutional authority. Tailored for enterprise-grade public health surveillance, vaccine integrity monitoring, and demographic record keeping, the visual direction prioritizes low cognitive overhead during critical decision-making. 

The aesthetic marries deep industrial minimalism with an analog archival atmosphere. By eschewing modern digital trends such as saturated neon indicators, glassmorphism, or artificial luminosity, the interface feels rooted, unshakeable, and deliberately understated. Deep charcoal and true neutral black slabs establish a non-distracting bedrock, allowing critical immunization metrics and status indicators to register with calm, unambiguous clarity.

## Colors

The palette relies strictly on cold-neutral dark substrates offset by warm cream values for interaction and textual legibility. There are zero warm cast tones (no bronze, taupe, or sepia) in the foundational surfaces.

### Primary Canvas & Surfaces
- **App Canvas (Deep Neutral Black):** `#0C0E12`
- **Surface Level 1 (Default Background):** `#111317`
- **Surface Level 2 (Base Card / Raised Tile):** `#1A1C20`
- **Surface Level 3 (Nested Panels / Layered Card):** `#1E2024`
- **Surface Level 4 (Elevated Modals / Popovers):** `#282A2E`
- **Surface Level 5 (Hover States / Active Rows):** `#333539`
- **Structural Dividers & Outlines:** `#2E3136`

### Text & Action Accents
- **Primary Typography & High-Priority Actions:** `#F0ECE4` (Clean, warm bone cream)
- **Secondary Actions & Refined Elements:** `#E8DFD0` (Subtle tinted ivory)
- **Secondary Text & Structural Labels:** `#9E9B95`
- **Tertiary Text, Placeholders & Inactive Icons:** `#777570`

### Muted Semantic Anchors
Semantic markers are rigorously desaturated to eliminate optical fatigue and prevent false urgency. Saturated neons, limes, and electric lights are strictly prohibited.
- **Healthy / Protected / Verified (Muted Sage Green):** `#6F7F6D`
- **Attention / Pending / Review (Muted Amber Earth):** `#987E55`
- **Problem / Critical / Expired (Muted Brick Red):** `#8F605A`
- **Informational / Neutral Metric (Muted Slate Blue-Grey):** `#64777B`

## Typography

The typographic hierarchy couples the crisp, geometric authority of **Hanken Grotesk** with the strict, data-dense precision of **JetBrains Mono**.

- **Editorial Headings & Narrative Text:** Set in Hanken Grotesk. Characters are optically tracked tighter in display weights to preserve an architectural silhouette.
- **Data Densities, Status Identifiers, Batch IDs, and Vials:** Explicitly assigned to JetBrains Mono. Monospaced tracking ensures rapid scanning of dates, timestamps, batch certificates, and clinical dosages without alignment shifts.
- Letter casing for labels (`label-md`, `label-sm`) defaults to uppercase for clinical telemetry and data markers.

## Layout & Spacing

This design system uses a strict 8-point base spatial system (with a 4-point sub-grid for compact, analytical components). Content resides across structural grid configurations:

- **Desktop (1200px+):** 12-column fluid grid, 32px gutters, dynamic side margins capped at 1440px max-width container or full-bleed modular cockpit dashboards.
- **Tablet (768px – 1199px):** 8-column layout, 24px gutters, 32px margin boundaries. Two-column clinical workflows collapse into singular layered panels.
- **Mobile (<768px):** 4-column layout, 16px gutters, 16px outer safety margins. Multi-metric comparison ribbons collapse into vertical tabular stacks.

## Elevation & Depth

Visual hierarchy is communicated strictly through **tonal layering** and **low-contrast structural outlines**. 

- **No Dropshadows:** Drop shadows, outer blurs, and luminous glows are entirely absent.
- **Surface Elevation:** Depth progresses monotonically:
  - Base viewport: `#0C0E12`
  - Workspace Canvas: `#111317`
  - Static Containers: `#1A1C20` bordered with a 1px solid line (`#2E3136`)
  - Elevated Interaction/Modals: `#282A2E` bordered with `#333539`
- **Dividers & Containment:** A hairline outline (1px, `#2E3136`) delineates interactive zones. When stacked, lower surfaces never cast illumination over background planes; they simply present a brighter, cleaner border boundary.

## Shapes

The design system maintains a structured, architectural geometry through **Soft (Level 1)** corner radii. 

- Form inputs, segmented tabs, and secondary buttons utilize `0.25rem` (4px).
- Cards, data display frames, and modal boundaries utilize `0.5rem` (8px).
- Status indicator tags and metric badges never exceed `0.25rem` (4px) to retain an engineering-first demeanor; fully circular pills are avoided except for solitary binary micro-dots (6px × 6px status indicators).

## Components

### Buttons
- **Primary:** Solid warm cream (`#F0ECE4`) background with deep neutral black text (`#0C0E12`), font weight 500. Hover state eases to `#E8DFD0`. Active state applies an interior hairline border of `#333539`.
- **Secondary:** Surface background (`#1A1C20`), 1px solid border (`#2E3136`), text `#F0ECE4`. Hover transforms background to `#282A2E` and border to `#777570`.
- **Ghost / Utility:** Transparent fill, `#9E9B95` text. Hover shifts to `#1E2024` surface with `#F0ECE4` text.

### Chips & Semantic Status Badges
- Built using `#111317` base fill and a 1px solid border tint matching the assigned status color at 40% alpha.
- Typography is strictly `label-md` in JetBrains Mono.
- Statuses display a 6px solid square or dot alongside the label:
  - **Healthy:** `#6F7F6D`
  - **Attention:** `#987E55`
  - **Problem:** `#8F605A`
  - **Info:** `#64777B`

### Input Fields & Controls
- **Text Inputs:** Background `#111317`, 1px border `#2E3136`, text `#F0ECE4`, placeholder `#777570`. Focus state shifts the border to `#E8DFD0` with zero outer ring glow.
- **Checkboxes & Radios:** Minimalist 16px squares/circles, background `#111317`, border `#2E3136`. Checked state fills the box with `#F0ECE4` bearing a `#0C0E12` checkmark glyph.

### Cards & Grouping Structures
- Structural cards employ `#1A1C20` fill, 1px border `#2E3136`, and `0.5rem` radius.
- Card headers feature JetBrains Mono label metadata at the top right, with Hanken Grotesk titles anchored on the left.

### Data Tables & Logs
- Header rows use `#111317` with `label-sm` monospaced column descriptions in `#777570`.
- Data rows feature subtle bottom borders (`#1E2024`), expanding to surface hover state `#282A2E` without transition latency for immediate feedback.