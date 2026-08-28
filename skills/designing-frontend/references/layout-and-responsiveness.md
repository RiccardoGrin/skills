---
summary: Flexbox and Grid patterns, responsive techniques, container queries, logical properties and RTL, safe areas, content-driven breakpoints, string growth, position properties, and image optimization
read_when: Building layouts with flexbox or grid, making designs responsive, choosing breakpoints, handling mobile safe areas or RTL, optimizing images, using container queries
---

# Layout Systems and Responsive Design

## Mental Model: Everything is a Box

Every HTML element renders as a rectangular box. Responsive design is the art of dynamically rearranging these boxes into rows and columns based on available space.

Before writing any HTML, sketch a **family tree** (document hierarchy) of parent-child relationships. This prevents sunk-cost layouts that fight the natural document flow. Always know which element is the flex/grid container and which elements are its children before coding.

---

## Flexbox vs Grid

Use flexbox for one-dimensional layouts (a single row or column of items). Use grid for two-dimensional layouts (rows AND columns simultaneously). When in doubt: if items need to align across both axes, use grid.

### When to Use Flexbox

Flexbox lets **children** determine their own sizing. Use it for navbars, card rows, form layouts, centering, and any layout where items should grow/shrink naturally.

```css
/* Basic flex row with natural sizing */
.row {
  display: flex;
  gap: 1rem;
}

/* Children grow equally to fill space */
.row > * {
  flex: 1 1 0%;
}

/* Children size based on content, then grow proportionally */
.row > .sidebar {
  flex: 1 1 auto;
}
.row > .main {
  flex: 3 1 auto;
}
```

**Key gotchas:**

- `flex-basis: auto` causes unequal growth because `flex-grow` distributes *remaining* space after content is accounted for. Use `flex: 1 1 0%` for truly equal columns.
- `flex-grow` is proportional — `flex-grow: 2` gets twice the extra space as `flex-grow: 1`, not a fixed 2x width.
- Flex children with `position: sticky` need `align-self: flex-start` or the sticky effect won't work.

### When to Use Grid

Grid lets the **parent** control positioning. Use it for page-level layouts, uniform card grids, and any layout requiring explicit row/column alignment.

```css
/* Fixed two-column layout */
.page {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 1.5rem;
}

/* Responsive card grid — no media queries needed */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
```

`repeat(auto-fit, minmax(280px, 1fr))` is the single most useful grid pattern — cards wrap automatically when space runs out.

---

## Responsive Techniques

### Fluid Sizing with clamp()

Use `clamp(min, preferred, max)` instead of hardcoded pixels for typography and spacing that scales smoothly without breakpoints.

```css
/* Fluid typography: 16px minimum, scales with viewport, caps at 24px */
h1 {
  font-size: clamp(1rem, 2.5vw + 0.5rem, 1.5rem);
}

/* Fluid padding */
.container {
  padding: clamp(1rem, 4vw, 3rem);
}

/* Fluid gap */
.grid {
  gap: clamp(0.75rem, 2vw, 2rem);
}
```

The middle value (`preferred`) typically combines a viewport unit with a rem offset for a smooth scaling curve.

### Viewport Units

```css
/* Full-height hero section */
.hero {
  min-height: 100dvh; /* dvh accounts for mobile browser chrome */
}

/* Width-based sizing */
.wide-element {
  width: min(90vw, 1200px); /* Responsive with a max cap */
  margin-inline: auto;
}
```

Prefer `dvh` (dynamic viewport height) over `vh` on mobile — `vh` includes the browser address bar area, causing overflow.

### Breakpoints Come From the Content

Break where the layout actually stops fitting, not at `768px` because a preset says so. The real breakpoint is where the sidebar squeezes the main column below its minimum readable measure, or the card grid drops below a usable column width.

**Collapse late.** A layout that keeps its expanded structure for as long as it genuinely fits stays stable and familiar. Collapsing early throws away space the user paid for.

Test the smallest and largest supported sizes first — those break first — then the sizes between.

### Media Queries

Use media queries for behavior changes that flex/grid alone cannot handle: hiding elements, converting layouts, swapping interaction patterns.

```css
/* Sidebar becomes top bar on mobile */
.sidebar {
  position: sticky;
  top: 0;
  width: 250px;
}

@media (max-width: 768px) {
  .layout {
    flex-direction: column;
  }
  .sidebar {
    width: 100%;
    position: static;
  }
}

/* Only apply hover effects on devices that support hover */
@media (hover: hover) {
  .card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
}
```

Wrapping hover effects in `@media (hover: hover)` prevents stuck hover states on touchscreens.

### Container Queries

For component-level responsiveness, use container queries instead of viewport-based media queries.
Container queries let a component adapt to its parent's size, not the viewport — essential for reusable components.

```css
.card-container {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
  }
}

@container (max-width: 399px) {
  .card {
    display: flex;
    flex-direction: column;
  }
}
```

Use `container-type: inline-size` on the parent. Components inside respond to the container width, not the viewport.
Prefer container queries over media queries when building reusable components that may appear in different layout contexts.

---

## Position Properties

| Property   | Use Case                                    |
| ---------- | ------------------------------------------- |
| `static`   | Default flow. Rarely set explicitly.        |
| `relative` | Offset from normal position; anchor for absolute children. |
| `absolute` | Layered/overlapping elements within a `relative` parent.   |
| `sticky`   | Headers, sidebars that stick on scroll.     |
| `fixed`    | Modals, toasts, floating action buttons.    |

```css
/* Sticky header */
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--bg-base);
}

/* Badge overlapping a card corner */
.card {
  position: relative;
}
.card .badge {
  position: absolute;
  top: -0.5rem;
  right: -0.5rem;
}
```

Never use `position: absolute` for page layout — that is flexbox/grid territory.

---

## Card Layouts

Cards with `border-radius`, `box-shadow`, and consistent padding are a reliable quick-win pattern for presenting grouped content.

```css
.card {
  border-radius: 0.75rem;
  box-shadow: var(--shadow-sm);
  padding: 1.5rem;
  background: var(--bg-raised);
}

/* Maintain proportions on card media */
.card img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 0.5rem;
}
```

```html
<div class="card-grid">
  <article class="card">
    <img src="photo.webp" alt="Description" />
    <h3>Title</h3>
    <p>Card content here.</p>
  </article>
  <!-- more cards -->
</div>
```

Use `aspect-ratio` on media elements so they maintain proportions without height hacks.

---

## Images and Media

### Responsive Image Serving

Use `<picture>` with `<source>` elements to serve different images based on screen size.

```html
<picture>
  <source
    media="(max-width: 640px)"
    srcset="hero-mobile.webp"
    type="image/webp"
  />
  <source
    media="(min-width: 641px)"
    srcset="hero-desktop.webp"
    type="image/webp"
  />
  <img src="hero-fallback.jpg" alt="Hero image" />
</picture>
```

### Image Optimization Checklist

- **Convert to WebP** for ~50% file size reduction over JPEG/PNG.
- **Use SVGs for icons** — lightweight, infinitely scalable, stylable with CSS, and respond to dark mode via `currentColor`.
- **Set explicit dimensions** or `aspect-ratio` to prevent layout shift (CLS).
- **Use `loading="lazy"`** on below-the-fold images.

```html
<!-- Lazy-loaded responsive image -->
<img
  src="photo.webp"
  alt="Description"
  width="800"
  height="450"
  loading="lazy"
  style="aspect-ratio: 16/9; object-fit: cover; width: 100%;"
/>
```

```css
/* SVG icon that adapts to dark mode */
.icon {
  color: currentColor;
  width: 1.5rem;
  height: 1.5rem;
}
```

---

## Common Responsive Patterns

### Centered Container with Max Width

```css
.container {
  width: min(90%, 1200px);
  margin-inline: auto;
  padding-inline: clamp(1rem, 4vw, 2rem);
}
```

### Holy Grail Layout

```css
.page {
  display: grid;
  grid-template: "header header" auto
                 "sidebar main" 1fr
                 "footer footer" auto
                 / 250px 1fr;
  min-height: 100dvh;
}

@media (max-width: 768px) {
  .page {
    grid-template: "header" auto
                   "main" 1fr
                   "footer" auto
                   / 1fr;
  }
  .sidebar { display: none; }
}
```

### Flex Wrap for Natural Reflow

```css
/* Items wrap naturally without media queries */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-list > * {
  flex: 0 1 auto; /* Don't grow, shrink if needed, size by content */
}
```

---

## Logical Properties and RTL

Express direction-dependent horizontal position as leading/trailing, not left/right, so the layout mirrors automatically under `dir="rtl"`. This costs nothing today and is the difference between a one-line locale switch and a rewrite later.

| Physical (avoid) | Logical (use) |
|---|---|
| `margin-left` | `margin-inline-start` |
| `padding-right` | `padding-inline-end` |
| `left: 0` | `inset-inline-start: 0` |
| `text-align: left` | `text-align: start` |
| `border-right` | `border-inline-end` |

```html
<!-- Tailwind logical utilities -->
<div class="ms-4 pe-6 text-start">...</div>

<!-- Breaks in RTL -->
<div class="ml-4 pr-6 text-left">...</div>
```

Reserve physical properties for genuinely physical geometry: positioning against a device notch, matching a hardware gesture direction.

Where arrangement encodes progression — star ratings, step indicators, progress bars — the sequence mirrors in RTL, and stars fill from the trailing side. Flexbox and grid with logical properties mirror automatically; hand-positioned elements do not. Digit order inside a number never reverses.

Icon mirroring rules are in `surface-craft.md`.

---

## Content Bleeds, Controls Float

Two layers behave differently at the viewport edge:

- **Content layer** — backgrounds, hero media, and scrollable lists extend edge to edge.
- **Control layer** — text and interactive elements stay inside the layout margins and safe areas, floating above the content.

```css
/* Full-bleed media inside a constrained article */
.article {
  display: grid;
  grid-template-columns: 1fr min(65ch, calc(100% - 48px)) 1fr;
}
.article > *            { grid-column: 2; }
.article > .full-bleed  { grid-column: 1 / -1; }
```

### Safe Areas

On devices with rounded corners, notches, and gesture bars, anything pinned to an edge needs `env(safe-area-inset-*)` padding or it sits under system UI.

```css
.fab {
  position: fixed;
  inset-inline-end: calc(16px + env(safe-area-inset-right));
  bottom:            calc(16px + env(safe-area-inset-bottom));
}

.action-bar {
  padding-inline: 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}
```

### Inset Buttons From the Edges

In content layouts, a full-width button glued to the viewport looks like system chrome and clips against curved corners. Keep it inside the layout margins with a visible radius — start near `16px` inline margin on mobile. The button can still span the full content width inside them.

Edge-to-edge actions are valid only when they are deliberately platform chrome and account for safe areas.

---

## Progressive Disclosure Needs an Affordance

Hiding complexity is good. Hiding it with no cue is a trap — content nobody knows exists may as well not exist.

- **Peeking items.** In a horizontal scroller or carousel, size items so the next one peeks `16-32px` past the container edge. A row of cards that ends exactly at the edge looks complete, and nobody scrolls it.
- **Disclosure controls.** Label them with what is hidden: "Show 12 more results", never "More".
- **Truncation cues.** Clamped text shows an ellipsis and a way to expand.

```css
.scroller {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-inline: 24px;
  scroll-padding-inline: 24px;
  scroll-snap-type: x mandatory;
}
.scroller > * {
  flex: 0 0 calc(100% - 48px - 24px);   /* container − margins − peek */
  scroll-snap-align: start;
}
```

---

## Plan for Growth and Clipping

Layouts fail in two directions: content grows, and viewports shrink.

**String expansion.** Translated strings grow, and short source strings grow proportionally more — a one-word button label is the riskiest text on the screen. Never budget a fixed percentage.

- No fixed widths sized to an English label. Use `max-width` plus wrapping.
- No fixed heights on text containers. Use `min-height` where a floor is needed.
- Buttons size themselves from their label via `padding-inline`, never a hardcoded width.
- Test with pseudo-localization or one long-string locale before shipping.

```css
/* Good — the label defines the size */
.button { padding-inline: 16px; white-space: nowrap; }

/* Bad — German will overflow or truncate */
.button { width: 96px; overflow: hidden; }
```

**Clipping.** Never park a critical action where it can be cut off: the bottom edge of a resizable pane, below the fold of a fixed-height modal, behind an expanding keyboard. Keep primary actions in stable chrome — a sticky footer with safe-area padding, or the top of the view. Where a modal's content scrolls, its action row does not.
