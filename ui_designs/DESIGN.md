---
name: Emerald Protocol
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1b1b1b'
  surface-container: '#1f1f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353535'
  on-surface: '#e2e2e2'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#e2e2e2'
  inverse-on-surface: '#303030'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#95d3ba'
  on-secondary: '#003829'
  secondary-container: '#0b513d'
  on-secondary-container: '#83c2a9'
  tertiary: '#ffb3af'
  on-tertiary: '#650911'
  tertiary-container: '#fc7c78'
  on-tertiary-container: '#711419'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#b0f0d6'
  secondary-fixed-dim: '#95d3ba'
  on-secondary-fixed: '#002117'
  on-secondary-fixed-variant: '#0b513d'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3af'
  on-tertiary-fixed: '#410005'
  on-tertiary-fixed-variant: '#842225'
  background: '#131313'
  on-background: '#e2e2e2'
  surface-variant: '#353535'
typography:
  headline-lg:
    fontFamily: JetBrains Mono
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: JetBrains Mono
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: JetBrains Mono
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.2'
  subheading-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '300'
    lineHeight: '1.5'
    letterSpacing: 0.15em
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: Space Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.05em
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.4'
spacing:
  unit: 4px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
  container-max: 1440px
---

## Brand & Style

This design system establishes a premium, retro-futuristic hacker aesthetic optimized for high-performance distributed computing. The brand personality is technical, cold, and authoritative—evoking the feeling of a sophisticated command-and-control interface.

The design style is a hybrid of **Minimalism** and **Modern Retro-Futurism**. It utilizes a "pitch-black" foundation to maximize the vibrance of its emerald primary color, creating a high-contrast environment that demands focus. Visual metaphors are drawn from mainframe terminals and tactical displays, refined through a high-end lens with generous whitespace and ultra-thin structural lines. It avoids the clutter of traditional "cyberpunk" styles in favor of a clean, systematic, and expensive feel.

## Colors

The palette is strictly anchored in monochrome blacks and a singular emerald spectrum. 

- **Primary Emerald (#10B981):** Used for critical data, active states, and primary typography. It should "glow" against the background.
- **Deep Emerald (#064E3B):** Reserved for low-priority UI elements, inactive borders, and subtle containers.
- **Pitch Black (#000000):** The absolute background for all primary views, ensuring infinite depth.
- **Accent Emerald (#34D399):** High-brightness variant for hover states and micro-interactions.

Secondary accents like "Warning Red" should be used sparingly and only for system errors, maintaining the monochromatic integrity of the interface.

## Typography

The typography system relies on the tension between a brutalist, technical monospace and a sophisticated, airy sans-serif.

**Headlines** use *JetBrains Mono* in heavy weights. This provides the "hacker" DNA, feeling structured and unyielding. 

**Subheadings and Body** use *Hanken Grotesk* with increased letter-spacing. This adds the "premium" layer, making the technical data readable and elegant. 

For **Labels and Data Points**, *Space Mono* is used to maintain the terminal aesthetic at small scales. All subheadings should be set in uppercase with wide tracking (15%+) to evoke high-end architectural documentation.

## Layout & Spacing

This design system employs a **Fixed Grid** philosophy to maintain the rigidity of a technical instrument. 

- **Grid:** A 12-column grid for desktop, 8-column for tablet, and 4-column for mobile.
- **Rhythm:** An 8px base unit drives all padding and margins to ensure mathematical alignment.
- **Density:** High whitespace is required. Content should be "islanded" within the pitch-black void, never cramped.
- **Structural Lines:** Use 1px emerald borders (opacity 10-20%) instead of background shifts to define sections, mimicking blueprint or CAD layouts.

## Elevation & Depth

In a pitch-black environment, depth is conveyed through **Light Emission** rather than shadows.

1.  **Tonal Layers:** There is no "surface" color; the background is always black. Higher elevation is indicated by increased border opacity or subtle background tints (e.g., Emerald at 4% opacity).
2.  **Glow (Bloom):** High-priority elements use a soft emerald outer glow (blur: 20px, opacity: 15%) to simulate a CRT phosphor effect.
3.  **Thin Outlines:** Hierarchy is defined by border thickness and intensity. 1px solid Emerald for active containers; 1px dashed or 20% opacity for inactive ones.
4.  **Backdrop Blurs:** Use sparingly behind floating panels (modals) with a 20px blur to maintain focus on the technical data underneath without losing the sense of space.

## Shapes

The shape language is strictly **Sharp (0px)**. 

To maintain the precision of a distributed computing tool, all buttons, inputs, and cards must have square corners. This reinforces the technical, "no-nonsense" character of the system. 

The only exception is for specific iconography or "node" visualizations (like the brain-circuit logo), which may use small 2px or 4px radii to indicate connectivity points. All structural UI elements remain perfectly angular.

## Components

### Buttons
- **Primary:** No fill. 1px solid Emerald border. Text is Emerald Mono, Uppercase. On hover: Emerald fill, Black text, subtle Bloom effect.
- **Ghost:** No border. Emerald text. On hover: 10% Emerald background tint.

### Input Fields
- **Default:** Bottom-border only (1px Emerald). Monospace font.
- **Focus:** Full 1px border with a "scanning" animation (a subtle highlight line that moves across the border).

### Cards / Containers
- No background color. 1px Emerald border at 20% opacity. 
- Header section separated by a 1px solid line.
- Use "Corner Markers" (L-shaped accents) on the four corners for high-priority modules.

### Status Chips
- Square corners. Small monospace text. 
- Use a "pulse" animation for active nodes/daemons (a small Emerald square that fades in/out).

### Lists & Data Tables
- No row backgrounds. 1px horizontal dividers only.
- Right-aligned numerical data in Monospace for perfect vertical alignment.
- Use thin vertical "guides" for column separation in complex data views.