---
name: VaxKavach
colors:
  surface: '#141311'
  surface-dim: '#141311'
  surface-bright: '#3b3936'
  surface-container-lowest: '#0f0e0c'
  surface-container-low: '#1c1b19'
  surface-container: '#211f1d'
  surface-container-high: '#2b2a27'
  surface-container-highest: '#363432'
  on-surface: '#e6e2de'
  on-surface-variant: '#ccc6bb'
  inverse-surface: '#e6e2de'
  inverse-on-surface: '#32302e'
  outline: '#969087'
  outline-variant: '#4a463e'
  surface-tint: '#cec5b7'
  primary: '#fffcff'
  on-primary: '#343026'
  primary-container: '#e8dfd0'
  on-primary-container: '#686256'
  inverse-primary: '#645e52'
  secondary: '#cbc6bf'
  on-secondary: '#32302c'
  secondary-container: '#4b4944'
  on-secondary-container: '#bdb8b1'
  tertiary: '#fffbff'
  on-tertiary: '#32302b'
  tertiary-container: '#e5dfd7'
  on-tertiary-container: '#65625c'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#eae1d2'
  primary-fixed-dim: '#cec5b7'
  on-primary-fixed: '#1f1b12'
  on-primary-fixed-variant: '#4b463b'
  secondary-fixed: '#e7e2db'
  secondary-fixed-dim: '#cbc6bf'
  on-secondary-fixed: '#1d1b18'
  on-secondary-fixed-variant: '#494642'
  tertiary-fixed: '#e7e2da'
  tertiary-fixed-dim: '#cbc6be'
  on-tertiary-fixed: '#1d1b17'
  on-tertiary-fixed-variant: '#494641'
  background: '#141311'
  on-background: '#e6e2de'
  surface-variant: '#363432'
  vk-bg: '#171614'
  vk-surface: '#1E1D1A'
  vk-surface-2: '#25231F'
  vk-surface-3: '#2C2A25'
  vk-cream: '#F0E8D9'
  vk-cream-soft: '#D8D0C2'
  vk-text-muted: '#A69F94'
  vk-border: '#3A3731'
  vk-border-soft: '#302E29'
  vk-healthy: '#71816F'
  vk-attention: '#A4875C'
  vk-problem: '#99655D'
  vk-info: '#667A7D'
typography:
  headline-display:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-section:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '650'
    lineHeight: 28px
  card-title:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
  metric-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.1'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  space-1: 4px
  space-2: 8px
  space-3: 12px
  space-4: 16px
  space-5: 20px
  space-6: 24px
  space-8: 32px
  space-10: 40px
  space-12: 48px
  space-16: 64px
  nav-width: 80px
  max-content-width: 1440px
---

## Brand & Style

The design system establishes a calm, clinical, and premium operational environment tailored for vaccine cold-chain monitoring. The visual persona relies on restraint, precision, and high-trust engineering rather than futuristic display.

- **Personality:** Clinical, calm, trustworthy, operational, precise, modern, premium.
- **Target Audience:** Cold-chain logistics operators, healthcare administrators, and compliance officers who require unambiguous clarity during critical operational events.
- **Emotional Response:** Reassurance, focus, control, and absolute reliability.
- **Design Style:** A refined hybrid of **Minimalism** and **Corporate Modern**, prioritizing tonal layering over heavy shadows, deep charcoal foundations, warm cream accents, and strictly muted semantic indicators.

## Colors

The palette is anchored by a dominant charcoal and warm cream relationship, utilizing desaturated, restrained semantic tones. Color is strictly functional, used exclusively to communicate state and hierarchy rather than decoration.

- **Surfaces & Backgrounds:** Deep charcoal tones (`#171614` to `#2C2A25`) build a stable Level 0 through Level 3 tonal hierarchy.
- **Text & Primary Interactions:** Warm cream (`#E8DFD0`, `#F0E8D9`) replaces harsh white for high-contrast, comfortable legibility.
- **Semantic Accents:** Muted green (`#71816F`), ochre (`#A4875C`), brick red (`#99655D`), and blue-grey (`#667A7D`) serve strictly as small indicators, thin borders, or chart lines. They must never flood entire components.

## Typography

Typography relies on **Plus Jakarta Sans** for a clean, highly legible, and humanist geometric structure. 

- **Hierarchy:** Strict application of scale prevents visual clutter. Primary text uses warm cream (`#F0E8D9`) instead of pure white, paired with muted grey-beige (`#A69F94`) for secondary metadata.
- **Tabular Numerals:** All live metrics and telemetry data must enforce `font-variant-numeric: tabular-nums` to maintain vertical alignment during rapid updates.
- **Case Rules:** Uppercase styling is strictly reserved for tiny status labels, system metadata, and compact indicators. Never apply uppercase to entire blocks or sections.

## Layout & Spacing

The layout model enforces a disciplined 8px spacing rhythm, giving the interface room to breathe and preventing cognitive overload in high-stakes environments.

- **Desktop Structure:** Features a persistent left navigation rail (72px–80px) paired with a max-width container of 1440px and generous internal padding (24px–40px).
- **Content Principle:** Every viewport must emphasize a single, unambiguous primary object. Avoid uniform visual weight across sibling components.
- **Responsive Adaptation:** Desktop layouts utilize multi-column grids and side navigation; tablets compress secondary panels; mobile viewports prioritize current state, primary actions, and key context using bottom sheets and collapsible sections.

## Elevation & Depth

Depth is communicated primarily through **tonal layering** rather than heavy drop shadows or glowing effects, reinforcing a solid, physical-grade architectural feel.

- **Surface Tiers:** Surfaces step upward from Level 0 background (`#171614`) through Level 1 primary surfaces (`#1E1D1A`), Level 2 nested containers (`#25231F`), up to Level 3 floating panels (`#2C2A25`).
- **Borders:** Components are separated by crisp, subtle borders (`1px solid #3A3731`) rather than high-contrast outlines.
- **Glassmorphism:** Restrained backdrop blurring (`backdrop-filter: blur(14px)` over `rgba(30, 29, 26, 0.78)`) is strictly reserved for map overlays, floating controls, and active slide-over panels.

## Shapes

The shape language uses moderate, purposeful radii to maintain a modern yet professional demeanor.

- **Radii Scale:** Small controls use 8px, inputs use 10px, standard cards use 12px–14px, and large containers or floating panels use 16px.
- **Pills:** Fully rounded pills (`9999px`) are strictly reserved for status indicators, active filters, compact tags, and inline micro-controls. Avoid over-rounding structural layout containers.

## Components

Components must be designed for operational efficiency, immediate legibility, and absolute clarity.

- **Buttons:** Primary actions utilize warm cream surfaces (`#E8DFD0`) with dark charcoal text (`#211F1B`). Secondary actions use dark charcoal surfaces (`#25231F`) with cream text and subtle borders. Destructive actions rely on muted brick red (`#99655D`) exclusively.
- **Status Indicators:** Never rely on color alone. Status components must always pair a compact 6–8px solid indicator with explicit text (e.g., `● Okay`, `● Need attention`). Glowing, pulsing, or animated dots are strictly forbidden.
- **Input Fields:** Built with a 10px corner radius, dark nested background (`#25231F`), and subtle borders (`#3A3731`), shifting to soft cream borders upon focus.
- **Cards & Information Groups:** Cards must group related operational telemetry logically. Avoid excessive card splitting, one-card-per-metric anti-patterns, or luminous KPI tiles. 
- **Tables & Lists:** Styled as clean operational lists with comfortable row heights, clear column hierarchies, and cream primary text. Avoid excessive gridlines or bright row backgrounds.
- **Navigation:** Persistent left rail with quiet, unlit active states utilizing a restrained cream treatment or slightly lighter charcoal surface.