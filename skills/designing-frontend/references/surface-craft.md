---
summary: Border radius nesting, optical alignment, shadow-vs-border choices, image outlines, and icon craft (stroke weight, states, render size, RTL)
read_when: nesting rounded containers, centering icons, choosing between a border and a shadow, styling images, picking or styling icons, or auditing why a component "feels off" without an obvious cause
---

# Surface Craft

The details below are individually invisible and collectively decisive.
Nobody reports "the inner radius is wrong" — they report that the component feels cheap.
Every value here is a specific number, not a range to approximate.

---

## Concentric Border Radius

When one rounded element nests inside another, the outer radius must equal the inner radius plus the padding between them:

```
outerRadius = innerRadius + padding
```

Mismatched nested radii are the most common cause of "this looks off" with no nameable defect.
The two curves run non-parallel and the gap between them pinches at the corner.

```css
/* Good — concentric */
.card       { border-radius: 20px; padding: 8px; }  /* 12 + 8 */
.card-inner { border-radius: 12px; }

/* Bad — same radius on both, corners pinch */
.card       { border-radius: 12px; padding: 8px; }
.card-inner { border-radius: 12px; }
```

```jsx
// Tailwind: 16px outer radius, 8px padding, 8px inner
<div className="rounded-2xl p-2">
  <div className="rounded-lg">...</div>
</div>
```

**Where the rule stops applying:** past roughly 24px of padding the layers read as separate surfaces rather than one nested object. Choose each radius independently at that point instead of forcing the math. Same when the padding is deliberately asymmetric, or when the project's design system already owns a radius token for the inner component.

If the project defines a radius scale (`--radius-sm/md/lg`), express the concentric pair in those tokens rather than raw pixels.

---

## Optical Over Geometric Alignment

Geometric centering is what the math says. Optical centering is what the eye says. When they disagree, the eye wins.

### Buttons with a trailing or leading icon

Symmetric padding around an icon-plus-text pair looks unbalanced, because an icon carries less visual weight than a text edge. Reduce the padding on the icon side:

```css
/* Good */
.button-with-icon {
  padding-inline-start: 16px;
  padding-inline-end: 14px;   /* icon side = text side - 2px */
}

/* Bad — equal padding; the icon looks pushed out */
.button-with-icon { padding-inline: 16px; }
```

### Play triangles

A triangle's geometric center sits left of its visual center. Nudge it:

```css
.play-button svg { transform: translateX(2px); }
```

### Asymmetric glyphs (stars, arrows, carets)

Fix the SVG itself — adjust the `viewBox` or the path so the glyph sits optically centered in its own box. Then every consumer gets it right with no per-site margin hacks. Fall back to a `translate` on the wrapper only when you cannot edit the asset.

---

## Shadows for Elevation, Borders for Structure

A border that exists only to create depth should be a shadow. A border that communicates structure or state should stay a border.

| Use a shadow | Use a border |
|---|---|
| Cards and containers that need depth | Dividers between list items |
| Buttons with a "bordered" look | Table cell boundaries |
| Dropdowns, popovers, modals | Form input outlines (accessibility) |
| Anything over an image or varied backgrounds | Hairline separators in dense UI |
| Hover and focus lift | Selected-state rings |

The reason is transparency. A solid `1px` border is a fixed color chosen against one background; move that element over an image or a second surface tint and it reads wrong. A shadow ring is transparent and composites against whatever is actually behind it.

### The shadow-as-border ring

Three layers: a `0 0 0 1px` ring standing in for the border, a tight shadow for contact, and a wider one for ambient depth.

```css
:root {
  --shadow-border:
    0 0 0 1px      oklch(0 0 0 / 0.06),
    0 1px 2px -1px oklch(0 0 0 / 0.06),
    0 2px 4px 0    oklch(0 0 0 / 0.04);

  --shadow-border-hover:
    0 0 0 1px      oklch(0 0 0 / 0.08),
    0 1px 2px -1px oklch(0 0 0 / 0.08),
    0 2px 4px 0    oklch(0 0 0 / 0.06);
}

[data-theme="dark"] {
  /* Layered depth shadows are invisible on dark surfaces — keep the ring only */
  --shadow-border:       0 0 0 1px oklch(1 0 0 / 0.08);
  --shadow-border-hover: 0 0 0 1px oklch(1 0 0 / 0.13);
}

.card {
  box-shadow: var(--shadow-border);
  transition: box-shadow 150ms var(--ease-out);
}
.card:hover { box-shadow: var(--shadow-border-hover); }
```

### Which system to reach for

- **Elevation** — things that genuinely float (modals, dropdowns, a dragged card): use the `--shadow-sm/md/lg` scale in `depth-and-visual-hierarchy.md`.
- **Definition** — a card or button that needs an edge, not altitude: use `--shadow-border` above.

Do not run both on the same element. Pick the one that matches what the element is doing.

---

## Image Outlines

Photographs and screenshots need a hairline edge, or they float untethered beside elements that have one.

```css
img {
  outline: 1px solid oklch(0 0 0 / 0.1);   /* light mode: PURE black */
  outline-offset: -1px;                    /* draw inside the edge, hugs the radius */
}

[data-theme="dark"] img {
  outline: 1px solid oklch(1 0 0 / 0.1);   /* dark mode: PURE white */
}
```

**The color rule is not negotiable.** Pure black at 10%, pure white at 10%. Never a near-black or near-white from the palette (`slate-900`, `zinc-900`, `#0a0a0a`, `#f5f5f7`), and never the brand accent. A tinted outline picks up the hue of the surface underneath and reads as dirt on the image edge rather than as a defined boundary.

**Why `outline` and not `border`:** an outline never participates in layout, so it adds no width or height at any offset, and `outline-offset: -1px` places the ring just inside the image so it follows the corner radius instead of squaring it off.

```jsx
// Tailwind — use black/10 and white/10 specifically, never a tinted scale
<img className="outline outline-1 -outline-offset-1 outline-black/10 dark:outline-white/10" />
```

---

## Icon Craft

### Match stroke weight to adjacent text

An icon beside text carries that text's optical weight. A hairline icon next to a semibold label reads as broken; a heavy icon next to regular text shouts.

| Adjacent text | Stroke width (24px grid) |
|---|---|
| Regular (400), 14-16px | `1.5px` |
| Medium / Semibold (500-600) | `2px` |
| Bold (700), or emphasized standalone | `2.5px` |

Size icons relative to the text's cap height — `1em` to `1.25em` when inline — so the pair scales together.

One icon library per surface. Never mix sets with incompatible stroke conventions in a single toolbar.

### One SVG, recolored per state

Never ship separate assets for default, hover, selected, and disabled. Draw once with `currentColor` and let CSS state drive the color.

```html
<svg fill="none" stroke="currentColor" stroke-width="2">...</svg>
```

```css
.icon-button                        { color: var(--text-secondary); }
.icon-button:hover                  { color: var(--text-primary); }
.icon-button[aria-pressed="true"]   { color: var(--primary); }
.icon-button:disabled               { opacity: 0.4; }
```

Hardcoded fills inside the SVG (`fill="#666"`) break this. Strip them to `currentColor` on import.

### Outline default, fill active

Where a set ships both variants, use them as a state pair, never interchangeably. Outline is the resting state; fill marks selected, toggled, liked, active. If everything is filled, the active state has no signal left to use.

The swap between variants should cross-fade — exact values in the contextual icon animation section of `animation-and-motion.md`.

### Never an emoji standing in for an icon

An emoji used as a feature, step, or value icon is an instant tell. It also renders differently on every platform, so it is not a design decision you actually control. Use the project's icon set, a built SVG, or drop the icon and lead with the visual.

### Never hand-build fake chrome

Do not draw a fake browser bar with a URL pill and traffic-light dots, a fake phone frame, or a fake code window. Use a real screenshot in a plain frame, or omit the chrome entirely. Redrawn chrome invents UI the real environment already supplies, and it reads as fabricated immediately.

### Design at render size

An icon that looks great at 48px turns to mush at 16px.

- Test every icon at the smallest size it will actually render, usually `16px`. It must stay recognisable there.
- Use the set's native grid sizes (16, 20, 24). A 16px icon drawn on a 24px grid renders soft from fractional scaling.
- Always SVG, never raster, so it stays crisp at every density.

### Icons in RTL

Under `dir="rtl"`, flip only the glyphs whose meaning depends on reading direction.

| Flip | Leave alone |
|---|---|
| Back / forward arrows, navigation chevrons | Logos and brand marks |
| Text-block glyphs (align, list, indent) | Checkmarks |
| Speaker and volume waves | Physical objects: clocks, cups, pencils |
| "Send"-style directional glyphs | Media playback (play/rewind follow tape convention, stay LTR) |

```css
[dir="rtl"] .icon-directional { scale: -1 1; }
```

Analyse composite icons part by part — a badge or slash overlay may hold its position while the base glyph flips.

---

## Quick Reference

| Decision | Value |
|---|---|
| Nested rounded elements | `outer = inner + padding`, until padding exceeds ~24px |
| Button with trailing icon | Icon-side padding = text-side padding − 2px |
| Play triangle | `translateX(2px)` |
| Card or button needing an edge | `--shadow-border` ring, not a solid border |
| List divider, table rule, focus ring | Keep it a border |
| Image edge, light mode | `outline: 1px solid oklch(0 0 0 / 0.1)`, `outline-offset: -1px` |
| Image edge, dark mode | `outline: 1px solid oklch(1 0 0 / 0.1)` |
| Icon beside regular text | `1.5px` stroke |
| Icon beside semibold text | `2px` stroke |
| Icon state colors | One SVG, `currentColor`, CSS drives the rest |
| Active state icon | Filled variant; outline stays the default |
