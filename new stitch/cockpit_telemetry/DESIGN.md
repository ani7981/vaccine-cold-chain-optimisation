---
name: Cockpit Telemetry
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
  on-surface-variant: '#c5c9af'
  inverse-surface: '#e2e2e8'
  inverse-on-surface: '#2f3035'
  outline: '#8f937b'
  outline-variant: '#454935'
  surface-tint: '#b0d41a'
  primary: '#ffffff'
  on-primary: '#2a3500'
  primary-container: '#ccf13c'
  on-primary-container: '#586c00'
  inverse-primary: '#536600'
  secondary: '#7bd0ff'
  on-secondary: '#00354a'
  secondary-container: '#00a6e0'
  on-secondary-container: '#00374d'
  tertiary: '#ffffff'
  on-tertiary: '#3c0091'
  tertiary-container: '#e9ddff'
  on-tertiary-container: '#7342dd'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ccf13c'
  primary-fixed-dim: '#b0d41a'
  on-primary-fixed: '#171e00'
  on-primary-fixed-variant: '#3e4c00'
  secondary-fixed: '#c4e7ff'
  secondary-fixed-dim: '#7bd0ff'
  on-secondary-fixed: '#001e2c'
  on-secondary-fixed-variant: '#004c69'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#111317'
  on-background: '#e2e2e8'
  surface-variant: '#333539'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 22px
    letterSpacing: 0em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  label-caps:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.06em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  telemetry-stat:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '700'
    lineHeight: 24px
    letterSpacing: -0.01em
  telemetry-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  dock-w: 72px
  xs: 4px
  sm: 8px
  md: 12px
  base: 16px
  lg: 20px
  xl: 24px
  2xl: 32px
  3xl: 40px
  gutter: 16px
  container-pad: 20px
---

## Brand & Style

This design system delivers an ultra-modern, high-performance telemetry aesthetic engineered for mission-critical logistics, heavy transport dispatch, and real-time fleet operations. Drawing inspiration from modern aerospace cockpits, industrial command centers, and tactical telemetry consoles, the visual style pairs deep slate-charcoal surfaces with ultra-crisp neon signal accents. 

### Visual Philosophy
- **Dark Tactical Canvas**: Deep, near-black slate backgrounds mitigate ocular fatigue in continuous multi-monitor monitoring environments while creating infinite depth.
- **Precision Luminescence**: Color is functional, reserved for actionable metrics, load states, critical route deviations, and spatial indicators. Primary chartreuse/lime acts as the master operational pulse.
- **Micro-Metric Density**: High information density structured through layered containers, micro-badges, pill toggles, and monospaced numerical readouts that command authority without cognitive overload.
- **Aerospace Tactility**: Softened corner radii (16px–24px) paired with sharp 1px glass borders (`#262C36`), floating icon navigation docks, and skeuomorphic telemetry dials (radial speedometers, horizon fuel meters, 360° navigation roses).

## Colors

The palette is tuned specifically for deep dark mode interfaces requiring extreme contrast ratios and instantaneous recognition of operational states.

### Palette Architecture
- **Surfaces**: Tonal progression ascends from deep base `#0A0C0F` through structured surface levels (`#0F1115`, `#14171D`, `#1A1E26`), establishing z-index elevation without cast shadows.
- **Primary Pulse (`#D2F843`)**: Electric chartreuse/lime reserved for primary action triggers, high-value selections, brand emblems, and operational confirmations.
- **Telemetry Indicators**:
  - **Electric Cyan (`#38BDF8`)**: Active vehicle tracking, utilization gauges, driving status, and connected hardware pings.
  - **Telemetry Violet (`#8B5CF6`)**: Resting crew states, time logs, and performance volume/area charts.
  - **Warning Amber (`#F59E0B`)**: Route deviation, moderate engine alerts, fuel status below 35%, and fragile cargo flags.
  - **Alert Crimson (`#EF4444`)**: Mechanical diagnostic failures, engine stop warnings, high risk levels, and critical cargo alerts.

## Typography

Typography prioritizes extreme data legibility and scan speed.

### Typographic Rules
- **Tabular Numerals**: All numerical metric readouts (mileage, speed, duration, GPS positions, capacity) must enable OpenType tabular figures (`font-variant-numeric: tabular-nums`) to prevent layout shifts during live data feeds.
- **Micro-Hierarchy**: Sub-labels, table category markers, and telemetry tags leverage `label-caps` in full uppercase with positive tracking (`+0.06em`) and muted coloring (`#64748B`).
- **Telemetry Numbers**: Numeric measurements (e.g., `100 mph`, `28 700 lbs`) utilize semi-bold or bold weights directly juxtaposed against smaller muted units (`mph`, `lbs`, `gal`).

## Layout & Spacing

The layout is built upon an operational command dashboard structure combining an icon rail dock, top-bar quick filters, and dynamic dashboard card grids.

### Spatial Framework
- **Master Icon Dock**: Fixed 72px left-aligned vertical dock anchored inside a floating pill-shaped container or edge bar.
- **Content Grid**: Fluid 12-column dynamic layout using 16px gutters and 20px–24px internal card padding.
- **Top Utility Rail**: Compact 48px–56px horizontal strip accommodating operational quick-chips (`Active: 6/10`, `Drivers: 6/8`), global search input, notifications pill, and user profile capsule.
- **Card Clustering**: Cards must group tightly along a disciplined 4px base rhythm. Related micro-metrics sit in sub-cards with 8px–12px padding inside master cards.
- **Breakpoints**:
  - `desktop` (≥1440px): 3-column split with simultaneous live map/3D cargo visualization and lateral detail queue.
  - `laptop` (1024px–1439px): 2-column flex grid with collapsible side queue.
  - `tablet` (768px–1023px): Tabbed command mode stacking telemetry dials beneath master feeds.

## Elevation & Depth

This system avoids diffuse drop shadows, opting instead for structural tonal layering and micro-luminance contours.

### Depth Hierarchy
1. **Level 0 (Canvas Background)**: Deep slate tone `#0A0C0F`.
2. **Level 1 (Dock & Primary Cards)**: Surface `#14171D` with a crisp outline: `border: 1px solid #262C36`.
3. **Level 2 (Nested Telemetry Tiles & Inputs)**: Surface `#1A1E26` inset inside Level 1 cards, bounded by fine border `rgba(255, 255, 255, 0.05)`.
4. **Level 3 (Floating Overlays & Popovers)**: Surface `#222732` backed by a 12px backdrop blur (`backdrop-filter: blur(12px)`) and delicate perimeter shadow: `0 12px 32px -4px rgba(0, 0, 0, 0.65)`.

### Accent Luminescence
Active items do not cast muddy dark shadows; instead, active interactive states emit colored radial glows. An active button or selected driver card emits `box-shadow: 0 0 20px rgba(210, 248, 67, 0.15)`.

## Shapes

The interface balances soft curved cards with aerodynamic pill contours.

### Geometry Standards
- **Outer Windows & Master Containers**: 20px to 24px border radii ensure a modern cockpit console feel.
- **Nested Gauges & Sub-Cards**: 14px to 18px radii nested harmoniously within master cards.
- **Pill System (`9999px`)**: Applied strictly to status tags, quick-filter chips, user profile capsules, map search, and active mode toggles.
- **Status Indicators**: Circular indicators (8px × 8px) or miniature pill badges (4px–6px radius) for driver status and critical alerts.

## Components

### 1. Navigation Rail & Icon Dock
- Vertical floating dock (`#14171D`, border `#262C36`).
- App logo: Squircle button filled with `#14171D` housing the Chartreuse `#D2F843` geometric cross/haul symbol.
- Navigation items: 44px × 44px rounded square buttons with secondary-toned vector icons. Active state transitions to solid white background with `#090A0D` icon and subtle glow.

### 2. Operational Filter Chips
- Capsule geometry (`rounded-full`, height: 32px), background: `#1A1E26`, border: `1px solid #262C36`.
- Typography: `12px Medium`. Includes icon, descriptor (`Active:` in muted text), and value (`6/10` in white bold).
- Active state: Border shifts to `#D2F843` or filled accent tone with light chartreuse typography.

### 3. Telemetry Cards & Dials
- **Card Container**: `#14171D` base, `20px` radius, hairline stroke `#262C36`. Headers feature title, secondary context, and optional micro refresh or external link icon button.
- **Speedometer / Radial Gauges**: Semi-circular or three-quarter circular track (`rgba(255, 255, 255, 0.08)`) with dynamic gradient stroke (lime through amber to crimson). Needle in solid white with center pivot hub and digital readout centered below (`100 mph`).
- **Fuel Gauge**: Horizon-filled radial sector with dual-color fluid level curve and inline temperature readout (`3.61 gal`, `72°F`).

### 4. Alert Priority Queue Rows
- Bounded row containers with dark background `#1A1E26` and status-specific left edge accent or full perimeter micro-border:
  - Critical Engine / Fuel: Red highlight (`#EF4444`) with subtle crimson tint (`rgba(239, 68, 68, 0.08)`).
  - Route Deviation: Amber highlight (`#F59E0B`) with warm glow.
- Includes vehicle ID badge (`TX-3360-HX`), error code description, relative time, and quick-resolve action pills.

### 5. Kanban Driver Cards
- Surface: `#1A1E26` with 16px radius.
- Structure: Avatar (36px squircle/circle with status dot overlay), full name (`14px Bold`), CDL license badge tag (`#222732` fill, `11px` uppercase mono), and contact row.
- Bottom telemetry strip: Tabular data points for driving hours, distance, and safety rating, flanked by micro circular action icons (call, rest break).

### 6. Cargo 3D Visualization Grid
- High-contrast black trailer chassis frame with integrated interactive package grid matrix.
- Package items: Rendered as structural bay boxes labelled with consignment IDs (`SHP-8841`).
- Package status pills:
  - `Critical`: `#EF4444` micro-badge.
  - `High`: `#F59E0B` micro-badge.
  - `Normal`: `#38BDF8` micro-badge.
  - `Low`: `#64748B` micro-badge.
- Selected bay: Bounded by 2px `#D2F843` lime border with interactive inspect modal showing weight capacity, fragile flags, and reassignment buttons.

### 7. Action Buttons & Form Controls
- **Primary Action**: Pill or 12px rounded rectangle in `#D2F843` with `#090A0D` bold text.
- **Secondary Action**: Pill or 12px rounded rectangle in `#1A1E26` with `1px solid #262C36` and `#FFFFFF` text.
- **Toggle Switch**: Dark pill track (`#1A1E26`) transitioning to solid `#D2F843` when active, with 18px circular white thumb.