---
summary: Shadow systems, elevation, recessed elements, border techniques, and visual hierarchy patterns for web UI
read_when: adding shadows, creating depth, establishing visual hierarchy, styling buttons/CTAs, working with elevation or border effects
---

# Depth and Visual Hierarchy

## Shadow System

Define shadow levels as CSS variables so every element draws from the same system. Three levels cover nearly all use cases.

### Shadow Variables

```css
:root {
  /* Small — subtle lift for cards, buttons */
  --shadow-sm:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 1px 2px rgba(0, 0, 0, 0.15);

  /* Medium — dropdowns, popovers, active cards */
  --shadow-md:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 2px 4px rgba(0, 0, 0, 0.15),
    0 6px 12px rgba(0, 0, 0, 0.08);

  /* Large — modals, floating elements */
  --shadow-lg:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 4px 8px rgba(0, 0, 0, 0.12),
    0 16px 32px rgba(0, 0, 0, 0.12);
}
```

Each shadow combines a light inset highlight on top with dark shadows below. The inset line simulates a top-lit surface. Pairing a short dark shadow (sharp contact) with a longer light shadow (ambient diffusion) produces realistic elevation.

### When to Use Each Level

| Level | Context |
|-------|---------|
| `--shadow-sm` | Cards, buttons, inputs — most elements |
| `--shadow-md` | Dropdowns, popovers, hovered cards |
| `--shadow-lg` | Modals, dialogs, floating action buttons |

Smaller shadows feel more natural on most elements. Default to `--shadow-sm` and only escalate when an element genuinely floats above its surroundings.

### Hover Shadow Transitions

Transitioning to a bigger shadow on hover makes interactive elements feel responsive — the element appears to "lift" toward the user.

```css
.card {
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

@media (hover: hover) {
  .card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
  }
}

.card:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

Always wrap hover effects in `@media (hover: hover)` to avoid stuck states on touchscreens.

---

## Recessed Elements

The inverse of elevation. A dark inset shadow on top and a light inset shadow on bottom pushes an element "into" the page, creating a sunken or carved-out effect.

```css
.recessed {
  box-shadow:
    inset 0 2px 4px rgba(0, 0, 0, 0.15),
    inset 0 -1px 2px rgba(255, 255, 255, 0.05);
}
```

Use the recessed effect for:
- **Progress bar tracks** — the filled portion sits elevated inside a sunken container.
- **Input fields** — subtle inset shadow reinforces that users type "into" the field.
- **Table cells / well containers** — content areas that sit below the surrounding surface.

```css
.progress-track {
  background: var(--bg-base);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.15),
              inset 0 -1px 2px rgba(255, 255, 255, 0.05);
  border-radius: 999px;
  height: 0.5rem;
}

.progress-fill {
  background: var(--primary);
  box-shadow: var(--shadow-sm);
  border-radius: 999px;
  height: 100%;
}
```

---

## Border Techniques

### Top-Lit Highlight

A lighter top border sells the illusion of a light source above the element.

```css
.card {
  border: 1px solid var(--border);
  border-top-color: rgba(255, 255, 255, 0.1);
}
```

### Blending Borders into Background

In light mode, card borders should nearly disappear. Use a border color only slightly darker than the card background.

```css
:root {
  --card-border: oklch(0.88 0 0);   /* just below --bg-raised at 0.95 */
}

body[data-theme="dark"] {
  --card-border: oklch(0.12 0 0);   /* just above --bg-raised at 0.05 */
}
```

### Gradient Backgrounds

Use existing shade values in subtle gradients for visual richness without introducing new colors.

```css
.hero {
  background: linear-gradient(
    to bottom,
    var(--bg-raised),
    var(--bg-base)
  );
}
```

### When to Remove Borders

Remove borders when color contrast alone provides enough separation. If two adjacent surfaces differ by at least 0.05 OKLCH lightness, a border is usually unnecessary and adds visual noise.

---

## Visual Hierarchy

### The Core Principle

Hierarchy determines what users see first, second, and third. Control it with three levers: **size**, **weight**, and **color/contrast**.

Start with small changes. De-emphasizing secondary elements is often more effective than making the primary element bigger or bolder. Reducing contrast on metadata, timestamps, and labels draws more attention to headlines and key data without touching them at all.

```css
/* Instead of making the title huge, dim everything else */
.card-title   { color: var(--text-primary); font-weight: 600; }
.card-meta    { color: var(--text-muted); font-size: 0.875rem; }
.card-body    { color: var(--text-secondary); }
```

### HTML Tags Do Not Dictate Visual Size

An `<h3>` inside a sidebar might be smaller than a `<p>` in a hero section. Choose visual treatment by context, not by tag.

```css
/* Sidebar heading — small and understated */
.sidebar h3 {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

/* Hero paragraph — large and prominent */
.hero p {
  font-size: 1.25rem;
  color: var(--text-primary);
}
```

### Gestalt Similarity

Consistent shape, size, and color for similar items lets the brain process a group as a whole before examining individual details. When list items, cards, or nav links share identical visual treatment, users instantly recognize them as peers.

Break similarity deliberately to draw attention. A single card with a colored border or different background stands out because it violates the established pattern.

### Chart Design

Charts are data communication tools, not decoration.

- Always include axis labels and clear value markers
- Hover states: highlight hovered element, dim others, show tooltip with exact value
- Avoid: rounded bar tops (obscure exact values), 3D effects, excessive gradients, decorative elements
- Simple charts convey more useful information than beautiful ones
- In dashboards, keep chart animations subtle — data changes should be clear, not flashy

### Icon Hierarchy

- Use one icon library consistently (Lucide, Phosphor, Heroicons, Feather)
- Match icon stroke width to typography weight for visual harmony
- Filled icons = active/selected state; outline icons = inactive/default state
- Always pair non-obvious icons with text labels or tooltips
- Different icon styles in visually separate areas (sidebar vs content) is acceptable; within the same area, keep them uniform

---

## Button and CTA Hierarchy

Define distinct visual levels so users instantly know which action is primary.

```css
/* Primary — brand color, high contrast, commands attention */
.btn-primary {
  background: var(--primary);
  color: white;
  box-shadow: var(--shadow-sm);
  border: none;
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease, box-shadow 0.15s ease;
}

@media (hover: hover) {
  .btn-primary:hover {
    background: var(--primary-hover);
    box-shadow: var(--shadow-md);
  }
}

.btn-primary:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Secondary — neutral, lower visual weight */
.btn-secondary {
  background: var(--bg-raised);
  color: var(--text-primary);
  border: 1px solid var(--border);
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease;
}

@media (hover: hover) {
  .btn-secondary:hover {
    background: var(--bg-overlay);
  }
}

.btn-secondary:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Ghost / tertiary — text-only, minimal footprint */
.btn-ghost {
  background: transparent;
  color: var(--primary);
  border: none;
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease;
}

@media (hover: hover) {
  .btn-ghost:hover {
    background: var(--primary-subtle);
  }
}

.btn-ghost:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
```

Place primary and secondary buttons side by side — the visual gap between them should be immediately obvious without reading labels.

---

## Depth Philosophy

Use depth sparingly. When everything is elevated, nothing is. Reserve shadows and elevation for elements that genuinely float above the page: modals, dropdowns, interactive cards.

### Theme-Agnostic Depth

All depth techniques work across light and dark mode when built on CSS variables. The shadow values above use `rgba` which adapts naturally — on dark backgrounds, shadows blend in more subtly, which is correct behavior since dark mode already uses background lightness for layering.

### Elevation via Background Lightness

In dark mode, lighter shades = elevated. In light mode, darker shades = elevated. This is the primary depth mechanism — shadows are secondary.

```css
/* Surface hierarchy via lightness */
.page       { background: var(--bg-base); }
.card       { background: var(--bg-raised); }
.dropdown   { background: var(--bg-overlay); }
```

Combine background elevation with shadows only when you need a stronger floating effect (modals, popovers). For inline cards and sections, background difference alone is often sufficient.

---

## Quick Reference

| Decision | Technique |
|---|---|
| Default shadow for most elements | `--shadow-sm` (small, subtle) |
| Interactive hover feedback | Transition from `--shadow-sm` to `--shadow-md` + slight `translateY` |
| Sunken/recessed containers | Dark inset shadow on top, light inset shadow on bottom |
| Top-lit realism | Light `border-top-color` or inset highlight |
| Emphasize primary content | De-emphasize secondary content instead (reduce contrast, shrink metadata) |
| Button hierarchy | Primary = brand fill, secondary = neutral/outline, ghost = text-only |
| Dark mode depth | Lighter background = higher elevation; shadows play a supporting role |
| Remove visual clutter | Drop borders when surfaces differ by >= 0.05 OKLCH lightness |
