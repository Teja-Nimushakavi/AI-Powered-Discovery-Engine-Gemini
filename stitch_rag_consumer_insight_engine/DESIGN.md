---
name: Lumina Analytics
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#434655'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#712ae2'
  on-secondary: '#ffffff'
  secondary-container: '#8a4cfc'
  on-secondary-container: '#fffbff'
  tertiary: '#005a82'
  on-tertiary: '#ffffff'
  tertiary-container: '#0074a6'
  on-tertiary-container: '#e4f2ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#eaddff'
  secondary-fixed-dim: '#d2bbff'
  on-secondary-fixed: '#25005a'
  on-secondary-fixed-variant: '#5a00c6'
  tertiary-fixed: '#c9e6ff'
  tertiary-fixed-dim: '#89ceff'
  on-tertiary-fixed: '#001e2f'
  on-tertiary-fixed-variant: '#004c6e'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-padding: 24px
  gutter: 16px
  section-gap: 32px
  glass-padding: 20px
---

## Brand & Style
The brand personality is authoritative yet visionary, catering to enterprise decision-makers who require clarity within complex AI datasets. The design system employs a **Refined Glassmorphism** style, moving away from "frosted" clichés toward a high-fidelity, professional execution. 

The emotional response should be one of "effortless intelligence"—where the UI feels lightweight and translucent, suggesting that the AI insights are surfacing naturally from a deep pool of data. Visuals focus on precision, utilizing micro-gradients and subtle backdrop blurs to establish a sense of modern, multi-layered depth without compromising data density.

## Colors
The palette is rooted in a pristine off-white environment to ensure the glass effects remain legible.
- **Primary & Secondary:** A vibrant gradient transition from Blue (#2563eb) to Purple (#7c3aed) is reserved for high-priority actions, AI "aha" moments, and active states.
- **Surface:** The core surface uses a semi-transparent white with a 12px backdrop blur. This allows background elements to bleed through softly, creating a sense of physical layering.
- **Typography:** Primary text uses a deep Navy-Slate for maximum contrast against glass surfaces, while secondary text uses a muted Gray-Slate to maintain hierarchy in metadata and labels.

## Typography
This design system utilizes a dual-font strategy to balance character with utility. 
- **Plus Jakarta Sans** is used for all headings and display metrics. Its modern, slightly wide apertures lend a futuristic and approachable feel to the RAG Discovery Engine's insights.
- **Inter** handles all functional body text, data tables, and interface labels. It is chosen for its exceptional legibility at small sizes and its neutral, systematic tone that doesn't distract from data visualization.
- **Hierarchy:** Use `label-md` for small eyebrow headers above metrics to establish a clear vertical rhythm.

## Layout & Spacing
The layout follows a **Fluid Grid** model with a fixed maximum width for high-resolution desktop monitors to prevent line-length fatigue in analytics views.
- **Grid:** A 12-column grid system is used for the main dashboard content.
- **Rhythm:** An 8px base unit drives all spacing. Standardize on 24px (3x) for card internal padding to allow the glass backgrounds enough "breathing room" to be perceived.
- **Breakpoints:** 
  - **Desktop (1280px+):** Sidebar is persistent; 12 columns.
  - **Tablet (768px - 1279px):** Sidebar collapses to icons; 8 columns.
  - **Mobile (<768px):** Single column stack; margins reduced to 16px.

## Elevation & Depth
Depth is not communicated through heavy shadows, but through **Tonal Stacking** and **Backdrop Blurs**.
- **Level 0 (Background):** Solid off-white (#f8fafc).
- **Level 1 (Cards/Panels):** Semi-transparent white (85% opacity) with 12px blur and a 1px border at 8% black. This creates the "Glass" effect.
- **Level 2 (Popovers/Modals):** Same as Level 1 but with a soft ambient shadow (0 8px 30px rgba(0, 0, 0, 0.04)) to indicate temporary interaction layers.
- **Interactive States:** On hover, a glass card should increase its border opacity from 8% to 15% and slightly decrease the blur value to 8px to feel "closer" to the user.

## Shapes
The shape language is professional and balanced. 
- **Cards & Modals:** Use `rounded-lg` (1rem / 16px) to maintain a soft, modern aesthetic that feels premium.
- **Input Fields & Buttons:** Use `rounded-md` (0.5rem / 8px) to provide a more structured, precise feeling for interactive elements.
- **Status Tags/Chips:** Use `rounded-full` (Pill-shaped) to distinguish them from functional buttons.

## Components
- **Buttons:** 
  - *Primary:* Gradient background (Blue to Purple), white text, no border.
  - *Secondary:* Glass background, 1px border (#000 8%), Navy text.
- **Input Fields:** Background is a slightly more opaque white (95%) to ensure text entry clarity. Focus state uses a 2px Blue primary border.
- **Analytics Cards:** Must include a subtle internal "glow" using an inset top-left white shadow to simulate light hitting the edge of the glass.
- **Data Visualizations:** Use a custom-curated palette of "Vibrant Blue," "Electric Purple," and "Cyan" for chart lines. Avoid harsh reds or oranges unless indicating critical system errors.
- **Sidebar:** A persistent vertical navigation on the left with a blurred glass background that spans the full height of the viewport.
- **AI-Discovery Insight:** A specialized card component with a thin 2px gradient border to distinguish AI-generated suggestions from standard raw data metrics.