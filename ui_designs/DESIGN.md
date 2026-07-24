---
name: Monolith Engineering
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f4'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#4c4546'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f0f1f1'
  outline: '#7e7576'
  outline-variant: '#cfc4c5'
  surface-tint: '#5e5e5e'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#1b1b1b'
  on-primary-container: '#848484'
  inverse-primary: '#c6c6c6'
  secondary: '#5e5e5e'
  on-secondary: '#ffffff'
  secondary-container: '#e1dfdf'
  on-secondary-container: '#626262'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#1b1b1b'
  on-tertiary-container: '#848484'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2e2e2'
  primary-fixed-dim: '#c6c6c6'
  on-primary-fixed: '#1b1b1b'
  on-primary-fixed-variant: '#474747'
  secondary-fixed: '#e4e2e2'
  secondary-fixed-dim: '#c7c6c6'
  on-secondary-fixed: '#1b1c1c'
  on-secondary-fixed-variant: '#464747'
  tertiary-fixed: '#e2e2e2'
  tertiary-fixed-dim: '#c6c6c6'
  on-tertiary-fixed: '#1b1b1b'
  on-tertiary-fixed-variant: '#474747'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
  border-base: '#EAEAEA'
  border-hover: '#D1D1D1'
  success-emerald: '#10B981'
  error-crimson: '#EF4444'
  bg-subtle: '#FAFAFA'
typography:
  display:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  mono-label:
    fontFamily: courierPrime
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
spacing:
  unit: 4px
  gutter: 16px
  margin-sm: 8px
  margin-md: 16px
  margin-lg: 24px
  container-max: 1200px
---

## Brand & Style

This design system embodies a high-density, engineering-focused aesthetic characterized by extreme precision and functional minimalism. It is designed for power users who value information density, speed, and clarity over decorative flourishes. 

The visual language is "Stark Light Mode," drawing heavily from modern developer tools. It utilizes a strict flat design philosophy—discarding all shadows, gradients, and blurs in favor of structural integrity provided by thin lines and high-contrast typography. The emotional response is one of efficiency, reliability, and technical sophistication.

## Colors

The palette is strictly monochrome to ensure focus remains on content and functionality. 
- **Core Surface:** Pure white (#FFFFFF) is the exclusive background for primary workspaces.
- **Accents:** Emerald Green and Crimson Red are used sparingly and solely for functional status indicators (Success/Active vs. Error/Offline).
- **Secondary Text:** Muted slate gray (#666666) provides hierarchy without sacrificing legibility.
- **Borders:** A consistent light gray (#EAEAEA) defines the structure, darkening slightly on interaction to provide feedback without depth.

## Typography

The system utilizes **Inter** for all UI elements to maintain a clean, systematic appearance. 
- **Headlines:** Set in pitch black (#000000) with tight letter-spacing for a "machined" look.
- **Body:** Standardized at 14px for most interfaces to maintain high information density.
- **Data/Code:** Where technical values or IDs are presented, use a secondary monospace font (Courier Prime) to distinguish data from UI labels.
- **Hierarchy:** Contrast is achieved through font weight and color (Black vs. Gray) rather than large scale variations.

## Layout & Spacing

This system uses a strict 4px grid. Layouts should favor a **fixed-fluid hybrid** approach: sidebars and utility panels use fixed widths (e.g., 240px or 64px), while the primary work area is fluid.

- **High Density:** Padding within components is kept to a minimum (8px to 12px) to allow more data to be visible on-screen simultaneously.
- **Grid:** Use a 12-column grid for marketing or dashboard layouts, but rely on flexible flexbox/grid containers for application views.
- **Borders as Dividers:** Use 1px borders (#EAEAEA) instead of whitespace to separate distinct functional areas.

## Elevation & Depth

This design system is strictly 2D. 
- **No Shadows:** Do not use `box-shadow` or any depth-simulating effects.
- **Tonal Separation:** Elevation is conveyed through color alone. For example, a "raised" element like a modal or dropdown is given a 1px border and a subtle background change (#FAFAFA) or remains white with a slightly darker border than the base surface.
- **Active States:** Active or focused items are indicated by a 1px solid black border or a background fill of #000000 with white text.

## Shapes

The shape language is industrial and sharp. 
- **Sharp Corners:** All buttons, input fields, cards, and containers must have 0px border-radius.
- **Consistency:** Square corners emphasize the technical, "grid-based" nature of the product.
- **Visual Rhythm:** Geometric precision is key; all boxes must align perfectly with the 4px spacing grid.

## Components

### Buttons
- **Primary:** Solid black background, white text, sharp corners.
- **Secondary:** White background, 1px #EAEAEA border, black text.
- **Hover State:** Secondary buttons change border to #D1D1D1; Primary buttons reduce opacity slightly (to 0.9).

### Input Fields
- **Default:** 1px #EAEAEA border, white background, 14px text.
- **Focus:** 1px black border. No "glow" or shadow.
- **Error:** 1px #EF4444 (Crimson) border.

### Chips & Tags
- Small, 12px text, light gray background (#F5F5F5) or subtle 1px border. Used for status or categories.

### Lists & Tables
- High density. 1px bottom border on rows. 
- Hover state: Background changes to #FAFAFA.
- Use #666666 for secondary data columns.

### Cards
- No shadows. Defined solely by a 1px #EAEAEA border. 
- Headers inside cards should be separated by a 1px horizontal line.