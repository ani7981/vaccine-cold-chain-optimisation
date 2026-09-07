# VaxKavach Design System
Version: 1.0
Status: Canonical visual source of truth

## 1. Purpose

VaxKavach is a premium vaccine cold-chain monitoring and operations product.

The interface should feel:

- calm
- clinical
- trustworthy
- operational
- precise
- modern
- premium
- easy to understand

It should NOT feel like:

- a gaming dashboard
- a cyberpunk command center
- a cryptocurrency product
- a generic SaaS admin template
- a neon telemetry console
- an overly colourful healthcare app

This document is the **canonical design source of truth** for all VaxKavach screens.

If another prompt, generated design, existing Stitch artifact, or old stylesheet conflicts with this document, **follow this document**.

---

# 2. Non-Negotiable Colour Rule

The visual identity is:

> **CHARCOAL + CREAM + MUTED COLOURS**

Use charcoal and warm cream as the dominant visual relationship.

All semantic colours must be desaturated and restrained.

### Absolutely forbidden

- neon green
- neon lime
- electric cyan
- bright royal blue
- vivid purple
- hot pink
- bright pastel backgrounds
- saturated gradients
- rainbow gradients
- glowing cyberpunk effects
- large luminous status indicators
- bright white page backgrounds

Never use colour simply for decoration.

Colour communicates state and hierarchy.

---

# 3. Canonical Colour Tokens

## Base

```css
--vk-bg: #171614;
--vk-surface: #1E1D1A;
--vk-surface-2: #25231F;
--vk-surface-3: #2C2A25;

--vk-cream: #F0E8D9;
--vk-cream-soft: #D8D0C2;
--vk-text-muted: #A69F94;

--vk-border: #3A3731;
--vk-border-soft: #302E29;
```

## Semantic colours

These are intentionally muted.

```css
--vk-healthy: #71816F;
--vk-attention: #A4875C;
--vk-problem: #99655D;
--vk-info: #667A7D;
```

These colours should normally appear as:

- small indicators
- thin borders
- small labels
- chart lines
- subtle backgrounds with low opacity

Do not flood entire cards with semantic colours.

## Interactive colour

Primary interaction should use cream, not neon.

```css
--vk-primary: #E8DFD0;
--vk-primary-text: #211F1B;

--vk-secondary: #25231F;
--vk-secondary-text: #E8DFD0;
```

A primary button is therefore a warm cream surface with dark charcoal text.

---

# 4. Colour Usage

Approximate visual distribution:

- 65–75% charcoal surfaces/background
- 15–20% warm cream/neutral text
- 5–10% muted secondary surfaces
- <5% semantic colours

Semantic colours should remain visually subordinate to the charcoal/cream foundation.

### Healthy

Use muted green.

Example:

`#71816F`

### Attention

Use muted ochre.

Example:

`#A4875C`

### Problem

Use muted brick red.

Example:

`#99655D`

### Information

Use muted blue-grey.

Example:

`#667A7D`

Never use:

`#00FF00`, `#D2F843`, `#38BDF8`, `#EF4444`, or similarly vivid equivalents.

---

# 5. Typography

Primary typeface:

**Plus Jakarta Sans**

Use a consistent hierarchy.

```text
Display / Page title: 32px / 40px / 700
Section title: 20px / 28px / 650
Card title: 16px / 24px / 600
Body: 14px / 22px / 400
Small body: 12px / 18px / 400
Label: 11px / 16px / 600
Large metric: 28–36px / 1.1 / 700
```

Use warm cream rather than pure white for primary text.

Use muted grey-beige for secondary text.

Enable tabular numerals for live metrics:

```css
font-variant-numeric: tabular-nums;
```

Avoid excessive uppercase text.

Uppercase is reserved for:

- tiny status labels
- system labels
- compact metadata

Do not make entire sections uppercase.

---

# 6. Layout

Use an 8px spacing rhythm.

Preferred spacing:

```text
4px
8px
12px
16px
20px
24px
32px
40px
48px
64px
```

The application should breathe.

Avoid packing too many components into one viewport.

### Desktop

Persistent left navigation:

```text
72px–80px
```

Main content:

```text
max-width: 1440px where appropriate
padding: 24px–40px
```

### Content principle

Every screen should have one obvious primary object.

Do not create equal visual weight for every card.

---

# 7. Navigation

Use a persistent left navigation rail.

Items:

- Overview
- Shipments
- Map
- Problems
- History
- Fleet
- Technical
- Settings

Active navigation item should use a restrained cream treatment or slightly lighter charcoal surface.

Do NOT use neon active states.

Do NOT use a large glowing indicator.

Navigation should be quiet and secondary to page content.

---

# 8. Surfaces

Use tonal layering rather than heavy shadows.

### Level 0

Background:

`#171614`

### Level 1

Primary surface:

`#1E1D1A`

### Level 2

Nested surface:

`#25231F`

### Level 3

Floating surface:

`#2C2A25`

Use subtle borders:

```css
border: 1px solid #3A3731;
```

Do not outline every component heavily.

---

# 9. Glass / Blur

Glass is allowed but must be restrained.

Use primarily for:

- map overlays
- floating controls
- drawers
- navigation overlays
- selected shipment panels

Preferred:

```css
background: rgba(30, 29, 26, 0.78);
backdrop-filter: blur(14px);
border: 1px solid rgba(240, 232, 217, 0.08);
```

Avoid excessive translucent panels.

The product should not look like a collection of floating glass cards.

---

# 10. Border Radius

Use moderate radii.

```text
Small controls: 8px
Inputs: 10px
Cards: 12–14px
Large containers: 16px
Floating panels: 16px
Pills: 9999px
```

Do not make every component extremely rounded.

Pills are reserved for:

- status
- filters
- compact tags
- small controls

---

# 11. Buttons

## Primary

Warm cream:

```css
background: #E8DFD0;
color: #211F1B;
```

Use for the most important action.

Example:

**View Problem**

## Secondary

Charcoal:

```css
background: #25231F;
color: #E8DFD0;
border: 1px solid #3A3731;
```

## Destructive

Use muted brick red only where necessary.

Never use bright red.

---

# 12. Status Indicators

Status must never rely on colour alone.

Always use:

**indicator + text**

Examples:

`● Okay`

`● Need attention`

`● Problem`

Use small 6–8px indicators.

No glowing dots.

No flashing dots.

No giant status circles.

---

# 13. Cards

Cards should have a clear reason to exist.

A card should contain a related group of information.

Do not create:

- one card per metric
- ten tiny cards in a row
- excessive nested cards
- giant colourful KPI tiles

Prefer fewer, larger information groups.

Use whitespace to create hierarchy.

---

# 14. Tables and Lists

Tables should feel like operational lists, not database exports.

Use:

- comfortable row height
- clear column hierarchy
- subtle dividers
- cream primary values
- muted metadata

Avoid:

- excessive grid lines
- tiny text
- bright row backgrounds
- rainbow status columns

On mobile, convert tables into readable cards.

---

# 15. Charts

Charts must be calm and readable.

Use:

- charcoal background
- cream axes/text
- muted green for healthy
- muted ochre for limits/attention
- muted brick red for problem periods
- subtle gridlines

Do not use neon chart lines.

Do not use multiple saturated series unless absolutely necessary.

Charts should support a decision, not exist merely because a chart is possible.

---

# 16. Map

The Live Map is one of the visually richer screens.

Use a dark, restrained map.

Map palette:

- charcoal land
- dark blue-grey water
- subtle grey borders
- muted cream labels
- muted green healthy routes
- muted ochre attention routes
- muted brick-red problem routes

Routes must be thin and restrained.

Markers must not glow.

The selected shipment may have a very subtle halo.

No cyberpunk map aesthetic.

---

# 17. Motion

Motion should communicate operational change.

Use:

- smooth state transitions
- subtle chart updates
- restrained map movement
- soft drawer transitions
- small status transitions

Do NOT use:

- bouncing cards
- flashing alerts
- glowing animations
- animated backgrounds
- excessive parallax
- constant decorative motion
- neon pulses

The application should remain calm even while live data changes.

---

# 18. Screen Personality

Each screen has a distinct job.

### Landing

Cinematic, explanatory, memorable.

### Overview

Calm operational summary.

### Shipments

Clean directory.

### Live Map

Spatial and visual.

### Shipment Details

Narrative + evidence.

### Problem Details

Investigation + reasoning.

### Problems

Operational queue.

### History

Chronological memory.

### Fleet

Physical infrastructure.

### Technical

Engineering transparency.

### Settings

Demo control centre.

Do not make every screen look like the same dashboard.

---

# 19. Information Density

Use a three-level information hierarchy.

## Level 1 — Immediate

What the operator needs to know immediately.

Examples:

- Problem
- Temperature
- Location
- Status
- Recommended action

## Level 2 — Context

Useful supporting information.

Examples:

- Route
- Outside temperature
- Door
- Transit delay
- Timeline

## Level 3 — Technical

Only when requested.

Examples:

- rule evaluation
- raw readings
- hashes
- event IDs
- sensor identifiers
- MKT

Do not put Level 3 information on Overview.

---

# 20. Language

Use plain operational language.

Preferred:

**Temperature problem**

not:

**Temperature excursion**

**Recommended action**

not:

**Corrective action**

**Live data**

not:

**Telemetry**

**History**

not:

**Audit trail**

**Current location**

not:

**Geospatial position**

Technical terminology may appear in Technical.

---

# 21. Data Display Conventions

Use Indian conventions consistently.

Temperature:

**°C**

Time:

**24-hour**

Timezone:

**IST / UTC+5:30**

Date:

**DD-MM-YYYY**

Currency:

**₹**

Routes and locations should use realistic Indian locations.

Example:

**Chennai → Vellore**

---

# 22. Demo Label

The prototype must clearly identify simulated data.

Use:

**SIMULATED TELEMETRY — DEMO MODE**

This label should be visible but unobtrusive.

Never imply that simulated data is live production data.

---

# 23. Accessibility

Maintain strong contrast.

Use text and icons alongside colour.

Do not rely on:

- green vs red alone
- tiny labels
- hover-only information

Interactive elements must have clear focus states.

Touch targets should be comfortable on mobile.

---

# 24. Responsive Behaviour

Desktop layouts should not simply be scaled down.

### Desktop

Use side navigation and multi-column layouts where useful.

### Tablet

Compress secondary information and collapse supporting panels.

### Mobile

Prioritize:

1. current state
2. primary action
3. key context
4. supporting information
5. technical details

Use bottom sheets and collapsible sections where appropriate.

---

# 25. Anti-Pattern Checklist

Before considering a screen finished, check:

- Is charcoal the dominant surface?
- Is warm cream the dominant text/accent?
- Are semantic colours muted?
- Is there any neon?
- Is there any bright pastel?
- Are there unnecessary gradients?
- Are there too many cards?
- Are too many things visually highlighted?
- Can the user identify the primary action immediately?
- Is the screen's single purpose obvious?
- Does it look like VaxKavach rather than a generic dashboard?

If any answer is wrong, simplify the screen.

---

# 26. Implementation Rule

The old Stitch-generated telemetry palette must NOT be treated as authoritative.

In particular, do not inherit or reintroduce:

- chartreuse/lime primary accents
- electric cyan
- saturated violet
- vivid crimson
- glowing accent shadows

Replace them with the canonical VaxKavach tokens in this document.

All future Stitch prompts and implementation work should reference this design system.

---

# 27. Core Visual Principle

VaxKavach should look like:

> **A calm, premium cold-chain operations system that happens to handle complex data.**

Not:

> **A complex data system trying to look futuristic.**

When in doubt:

**remove colour, remove decoration, increase whitespace, strengthen hierarchy.**
