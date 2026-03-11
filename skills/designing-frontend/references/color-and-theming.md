---
summary: Color systems, palettes, dark/light theming, and CSS variable patterns for web UI
read_when: building color palettes, implementing dark mode, choosing colors, theming a UI, working with CSS custom properties for color
---

# Color and Theming

## Color Formats

### HSL — Human-Readable Color

HSL maps directly to design decisions:
- **Hue** (0-360): which color
- **Saturation** (0-100%): how vivid
- **Lightness** (0-100%): how bright/dark

Generating shade palettes is simple arithmetic — increment lightness by 10% to get a new shade.

```css
--blue-base: hsl(220 70% 50%);
--blue-light: hsl(220 70% 60%);
--blue-lighter: hsl(220 70% 70%);
--blue-dark: hsl(220 70% 40%);
```

### OKLCH — Perceptually Uniform (Tailwind v4 Default)

OKLCH keeps saturation visually consistent across lightness changes. HSL washes out colors at high/low lightness; OKLCH does not.

Format: `oklch(lightness chroma hue)`
- **Lightness**: 0 (black) to 1 (white)
- **Chroma**: 0 (gray) to ~0.4 (max saturation). UI work rarely exceeds **0.15-0.2**.
- **Hue**: 0-360 degrees

```css
--blue-base: oklch(0.55 0.18 250);
--blue-light: oklch(0.65 0.18 250);
--blue-lighter: oklch(0.75 0.18 250);
--blue-dark: oklch(0.45 0.18 250);
```

Notice chroma stays at 0.18 across all shades — the color remains equally vivid. In HSL, the equivalent shades would appear washed out at higher lightness.

### Avoid Hex/RGB for Design Work

Hex (`#3b82f6`) and RGB (`rgb(59, 130, 246)`) encode color as red/green/blue channel intensities. They don't map to human reasoning about color. Use them only when consuming values from external tools.

---

## Building a Color Palette

A complete UI color system needs surprisingly few colors:

1. **Neutral shades** — backgrounds and text (gray scale or very low saturation)
2. **Primary/brand color** — the single dominant accent
3. **Semantic state colors** — success (green), warning (amber), error (red), info (blue)

Limit ruthlessly. Netflix uses black, white, and red. Most UIs need 3-5 intentional colors, each with 3-4 shades.

### Generating Palette Colors

**Primary to secondary** — adjust saturation and lightness, keep the hue:

```css
--primary: oklch(0.55 0.18 250);       /* blue */
--secondary: oklch(0.65 0.10 250);     /* desaturated, lighter blue */
```

**Tertiary and accent** — shift hue 60 degrees in either direction (creating a 120-degree arc):

```css
--primary: oklch(0.55 0.18 250);       /* blue, hue 250 */
--tertiary: oklch(0.55 0.15 310);      /* hue +60: purple */
--accent: oklch(0.55 0.15 190);        /* hue -60: teal */
```

### Generating Shades

Create 3-4 shades per color by incrementing lightness by ~0.1 (OKLCH) or ~10% (HSL):

```css
/* OKLCH shades */
--primary-900: oklch(0.35 0.18 250);
--primary-700: oklch(0.45 0.18 250);
--primary-500: oklch(0.55 0.18 250);   /* base */
--primary-300: oklch(0.65 0.18 250);

/* HSL equivalent approach */
--primary-900: hsl(220 70% 30%);
--primary-700: hsl(220 70% 40%);
--primary-500: hsl(220 70% 50%);     /* base */
--primary-300: hsl(220 70% 60%);
```

Ignore "color psychology" claims. What matters is legibility and contrast.

---

## Dark Mode / Light Mode

### Dark Mode Backgrounds

Use 3 background shades at low lightness, zero saturation:

```css
/* Dark mode surface layers */
--bg-base: oklch(0.00 0 0);     /* 0% — deepest background */
--bg-raised: oklch(0.05 0 0);   /* 5% — cards, sidebars */
--bg-elevated: oklch(0.15 0 0); /* 15% — popovers, floating panels */
--bg-overlay: oklch(0.10 0 0);  /* 10% — modals, dropdowns */
```

Lighter elements sit "on top" and feel closer to the user. This creates depth without shadows or borders.

### Light Mode from Dark Mode

Subtract dark mode lightness from 1.0 (or 100%):

```css
/* Light mode — inverted from dark */
--bg-base: oklch(1.00 0 0);     /* white */
--bg-raised: oklch(0.95 0 0);   /* light gray */
--bg-elevated: oklch(0.92 0 0); /* slightly darker */
--bg-overlay: oklch(0.90 0 0);  /* darker still */
```

In light mode, darker shades = elevated. The naming convention flips: what was "raised" in dark mode is still "raised" in light mode, but the lightness direction reverses.

### Text Contrast

- Dark mode: use ~90% lightness for body text, not pure white (100%). Pure white headings cause eye strain.
- Light mode: use ~15-20% lightness for body text, not pure black.

```css
/* Dark mode text */
--text-primary: oklch(0.90 0 0);
--text-secondary: oklch(0.65 0 0);
--text-muted: oklch(0.45 0 0);

/* Light mode text */
--text-primary: oklch(0.15 0 0);
--text-secondary: oklch(0.40 0 0);
--text-muted: oklch(0.60 0 0);
```

### System Preference Detection

One line adapts native elements (scrollbars, form controls) to the OS setting:

```css
:root {
  color-scheme: light dark;
}
```

For custom theming, use the media query:

```css
:root {
  /* Light mode defaults */
  --bg-base: oklch(1.00 0 0);
  --text-primary: oklch(0.15 0 0);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-base: oklch(0.00 0 0);
    --text-primary: oklch(0.90 0 0);
  }
}
```

For toggle-based theming, use a class or data attribute on `body`:

```css
:root {
  --bg-base: oklch(1.00 0 0);
  --text-primary: oklch(0.15 0 0);
}

body[data-theme="dark"] {
  --bg-base: oklch(0.00 0 0);
  --text-primary: oklch(0.90 0 0);
}
```

---

## Color for Depth and Hierarchy

Layer shades to produce visual depth without heavy borders or shadows:

```css
.page       { background: var(--bg-base); }
.card       { background: var(--bg-raised); }
.dropdown   { background: var(--bg-overlay); }
```

Remove borders on elevated elements when the shade difference alone provides enough separation. If two adjacent surfaces have at least a 0.05 OKLCH lightness difference, a border is usually unnecessary.

Use primary color shades for interactive state hierarchy:

```css
.btn-primary           { background: var(--primary-500); }
.btn-primary:hover     { background: var(--primary-700); }
.btn-primary:active    { background: var(--primary-900); }
```

### Gradient Restraint

If using gradients, stick to variations of a single hue.
Multi-color gradients (blue-to-pink, rainbow effects) look amateurish in most UI contexts.

```css
/* Good: single-hue gradient */
background: linear-gradient(135deg, hsl(220 80% 50%), hsl(220 80% 35%));

/* Avoid: multi-hue gradient in UI elements */
background: linear-gradient(135deg, hsl(220 80% 50%), hsl(340 80% 50%));
```

Exception: gradients spanning analogous colors (within ~30 degrees of hue) can work for hero sections or accent elements, but not for buttons, cards, or repeated components.

---

## CSS Variables Pattern — Full Example

Organize variables by role, not by color name. This makes theme switching a single block swap.

```css
:root {
  /* Surfaces */
  --bg-base: oklch(1.00 0 0);
  --bg-raised: oklch(0.95 0 0);
  --bg-elevated: oklch(0.92 0 0);
  --bg-overlay: oklch(0.90 0 0);

  /* Text */
  --text-primary: oklch(0.15 0 0);
  --text-secondary: oklch(0.40 0 0);
  --text-muted: oklch(0.60 0 0);

  /* Brand */
  --primary: oklch(0.55 0.18 250);
  --primary-hover: oklch(0.45 0.18 250);
  --primary-active: oklch(0.35 0.18 250);
  --primary-subtle: oklch(0.90 0.05 250);  /* tinted background */

  /* Semantic */
  --success: oklch(0.55 0.15 145);
  --warning: oklch(0.70 0.15 85);
  --error: oklch(0.55 0.18 25);
  --info: oklch(0.55 0.12 250);

  /* Borders */
  --border: oklch(0.85 0 0);
  --border-strong: oklch(0.70 0 0);
}

body[data-theme="dark"] {
  /* Surfaces */
  --bg-base: oklch(0.00 0 0);
  --bg-raised: oklch(0.05 0 0);
  --bg-elevated: oklch(0.15 0 0);
  --bg-overlay: oklch(0.10 0 0);

  /* Text */
  --text-primary: oklch(0.90 0 0);
  --text-secondary: oklch(0.65 0 0);
  --text-muted: oklch(0.45 0 0);

  /* Brand — bump lightness up for dark backgrounds */
  --primary: oklch(0.65 0.18 250);
  --primary-hover: oklch(0.70 0.18 250);
  --primary-active: oklch(0.75 0.18 250);
  --primary-subtle: oklch(0.15 0.05 250);

  /* Semantic — lighter for dark backgrounds */
  --success: oklch(0.65 0.15 145);
  --warning: oklch(0.75 0.15 85);
  --error: oklch(0.65 0.18 25);
  --info: oklch(0.65 0.12 250);

  /* Borders */
  --border: oklch(0.15 0 0);
  --border-strong: oklch(0.25 0 0);
}
```

### Usage in Components

Reference roles, never raw colors:

```css
body {
  background: var(--bg-base);
  color: var(--text-primary);
}

.card {
  background: var(--bg-raised);
  border: 1px solid var(--border);
}

.alert-error {
  background: var(--error);
  color: white;
}

a {
  color: var(--primary);
}
a:hover {
  color: var(--primary-hover);
}
```

### Tailwind Integration

Map CSS variables to Tailwind's config so utility classes use your theme:

```css
/* In your CSS (Tailwind v4) */
@theme {
  --color-bg-base: var(--bg-base);
  --color-bg-raised: var(--bg-raised);
  --color-bg-elevated: var(--bg-elevated);
  --color-primary: var(--primary);
  --color-text-primary: var(--text-primary);
}
```

Then use as `bg-bg-base`, `text-text-primary`, `bg-primary`, etc.

---

## Quick Reference

| Decision | Technique |
|---|---|
| Pick a color format | OKLCH for Tailwind v4+; HSL otherwise |
| Generate shades | Increment lightness by 0.1 (OKLCH) or 10% (HSL), keep chroma/saturation fixed |
| Add accent colors | Shift hue +/- 60 degrees from primary |
| Dark mode backgrounds | 0%, 5%, 10% lightness, zero chroma |
| Light mode from dark | Subtract dark lightness from 1.0 |
| Avoid eye strain | Cap text at 90% lightness (dark mode), 15% (light mode) |
| Remove unnecessary borders | If surfaces differ by >= 0.05 lightness, border is optional |
| Name variables | By role (`--bg-raised`) not color (`--gray-200`) |
