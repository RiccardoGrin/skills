---
summary: CSS transitions, keyframe animations, timing functions, 3D effects, SVG animation, scroll effects, and loading states
read_when: Adding transitions, animations, scroll effects, loading animations, or SVG animation
---

# Animation and Motion

## Core Motion Primitives

All web animations combine five transform functions plus opacity:

```css
.element {
  transform: translate(10px, 20px) scale(1.1) rotate(15deg) skew(5deg);
  opacity: 0.8;
}
```

Use CSS `transition` for state-to-state changes (hover, focus, active). Use CSS `animation` with `@keyframes` for choreographed multi-step sequences.

```css
/* State-to-state */
.button {
  transition: transform 200ms ease-out, box-shadow 200ms ease-out;
}
.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Choreographed sequence */
@keyframes slide-in {
  0%   { transform: translateX(-100%); opacity: 0; }
  60%  { transform: translateX(5%); opacity: 1; }
  100% { transform: translateX(0); }
}
.panel { animation: slide-in 400ms ease-out forwards; }
```

## Timing Functions

Timing functions control the feel of every animation. They define distance-over-time: a slow start means speed picks up later.

| Function | Use case |
|---|---|
| `linear` | Progress bars, continuous rotation |
| `ease` | General-purpose default |
| `ease-in` | Elements exiting the screen |
| `ease-out` | Elements entering the screen |
| `ease-in-out` | Elements moving between positions |
| `cubic-bezier()` | Full control over the curve |

Three essential `cubic-bezier` values:

```css
/* Standard — slight acceleration then deceleration */
transition: transform 250ms cubic-bezier(0.4, 0, 0.2, 1);

/* Decelerate — fast entry, gentle stop (entrances) */
transition: transform 250ms cubic-bezier(0, 0, 0.2, 1);

/* Accelerate — gentle start, fast exit (exits) */
transition: transform 200ms cubic-bezier(0.4, 0, 1, 1);
```

### Duration Guidelines

- **150-300ms** — micro-interactions (button press, toggle, tooltip)
- **300-500ms** — layout transitions (panel slide, accordion, modal)
- **500ms+** — only for emphasis or dramatic reveals; use sparingly

## 3D Effects

CSS `perspective` controls the intensity of 3D transforms. Smaller values produce more dramatic depth; larger values are subtler.

```css
/* Card flip */
.card-container {
  perspective: 800px;
}
.card {
  transform-style: preserve-3d;
  transition: transform 500ms ease-in-out;
}
.card .back {
  backface-visibility: hidden;
  transform: rotateY(180deg);
}
.card .front {
  backface-visibility: hidden;
}
.card-container:hover .card {
  transform: rotateY(180deg);
}
```

```css
/* Subtle tilt on hover */
.tile {
  perspective: 1200px;
  transition: transform 300ms ease-out;
}
.tile:hover {
  transform: rotateX(3deg) rotateY(-3deg);
}
```

## Path Animations

`offset-path` lets elements follow arbitrary paths — box edges, circles, or SVG curves.

```css
/* Follow a circular path */
.orbit {
  offset-path: circle(120px);
  animation: follow-path 3s linear infinite;
}

/* Follow an SVG curve */
.along-curve {
  offset-path: path("M 0,100 Q 150,0 300,100 T 600,100");
  animation: follow-path 2s ease-in-out forwards;
}

@keyframes follow-path {
  from { offset-distance: 0%; }
  to   { offset-distance: 100%; }
}
```

## SVG Animations

### Line Drawing / Tracing

Set `pathLength="1"` on the SVG path, then animate `stroke-dashoffset`:

```css
/* SVG markup: <path pathLength="1" class="draw" d="..." /> */
.draw {
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  animation: trace 1.5s ease-out forwards;
}
@keyframes trace {
  to { stroke-dashoffset: 0; }
}
```

### Shimmering Gradient

Use `animateTransform` to rotate a gradient behind a clipping shape:

```html
<defs>
  <linearGradient id="shimmer" gradientTransform="rotate(0)">
    <stop offset="0%" stop-color="#ddd" />
    <stop offset="50%" stop-color="#fff" />
    <stop offset="100%" stop-color="#ddd" />
    <animateTransform attributeName="gradientTransform"
      type="translate" from="-1 0" to="1 0"
      dur="1.5s" repeatCount="indefinite" />
  </linearGradient>
</defs>
```

### Shape Morphing

Source and target SVG paths must have the same number of control points. If they don't, use [Shapeshifter.design](https://shapeshifter.design) to add compatible points.

```css
@keyframes morph {
  from { d: path("M 10,80 Q 50,10 90,80 T 170,80"); }
  to   { d: path("M 10,50 Q 50,90 90,50 T 170,50"); }
}
.morphing-path {
  animation: morph 800ms ease-in-out alternate infinite;
}
```

## JavaScript Animations

`element.animate()` works like CSS keyframes but accepts dynamic runtime values.

```js
// Animate between two positions calculated at runtime
const startRect = elA.getBoundingClientRect();
const endRect = elB.getBoundingClientRect();
const dx = endRect.left - startRect.left;
const dy = endRect.top - startRect.top;

elA.animate([
  { transform: 'translate(0, 0)', opacity: 1 },
  { transform: `translate(${dx}px, ${dy}px)`, opacity: 0.5 }
], {
  duration: 350,
  easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
  fill: 'forwards'
});
```

Use `getBoundingClientRect()` to calculate coordinates between elements for FLIP-style animations (First, Last, Invert, Play).

## Scroll Effects

### CSS Scroll Snapping

Two lines for carousel-like scroll behavior:

```css
.scroll-container {
  scroll-snap-type: x mandatory;
  overflow-x: auto;
  display: flex;
  gap: 1rem;
}
.scroll-container > * {
  scroll-snap-align: start;
  flex: 0 0 80%;
}
```

Options for `scroll-snap-type`:
- `mandatory` — always snaps to a snap point
- `proximity` — snaps only when close to a point

Options for `scroll-snap-align`:
- `start`, `center`, `end` — where the child aligns within the container

### Scroll-Driven Animations (modern browsers)

```css
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(30px); }
  to   { opacity: 1; transform: translateY(0); }
}
.reveal {
  animation: fade-in-up linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

## Best Practices

### Respect Reduced Motion

Always provide a reduced-motion fallback. This is a hard requirement for accessibility.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Or scope it per-element for finer control:

```css
.card {
  transition: transform 300ms ease-out;
}
@media (prefers-reduced-motion: reduce) {
  .card {
    transition: none;
  }
}
```

### Guard Hover Animations

Wrap hover-triggered animations so touch devices don't get stuck states:

```css
@media (hover: hover) {
  .card:hover {
    transform: translateY(-4px) scale(1.02);
  }
}
```

### Purpose-Driven Motion

Animations should serve one of three UX goals:

1. **Feedback** — confirm an action happened (button press, form submit)
2. **Orientation** — show where something came from or went (page transitions, expanding panels)
3. **Delight** — add personality without slowing the user down (subtle entrance effects)

If an animation doesn't serve one of these, remove it.

### Performance

- Animate only `transform` and `opacity` — they run on the compositor thread and avoid layout/paint.
- Avoid animating `width`, `height`, `top`, `left`, `margin`, `padding` — these trigger expensive layout recalculations.
- Use `will-change: transform` sparingly and only on elements that will actually animate.

```css
/* Good — compositor-only properties */
.efficient {
  transition: transform 200ms ease-out, opacity 200ms ease-out;
}

/* Bad — triggers layout recalc every frame */
.expensive {
  transition: width 200ms ease-out, left 200ms ease-out;
}
```

### Interactive Feedback States

Beyond hover/focus, design post-action feedback:

- **Button click:** Gray out and disable on click, show spinner or loading text. Re-enable on completion or failure.
- **Save/favorite:** Fill in the icon on tap (outline heart → filled heart) with a brief scale animation
- **Notification dots:** Add colored dots or badges when new content appears or actions complete
- **Toast confirmations:** After completing an action (save, delete, send), show a brief toast notification

```css
/* Button loading state */
.btn-loading {
  opacity: 0.6;
  pointer-events: none;
  position: relative;
}

.btn-loading::after {
  content: "";
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
  margin-left: 0.5rem;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### Skeleton Loading Animation

Use skeleton screens instead of spinners for content areas:

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--bg-raised) 25%,
    var(--bg-elevated) 50%,
    var(--bg-raised) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 0.25rem;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

Create skeleton elements matching the shape and size of the content they replace.

### Context-Dependent Animation Intensity

- **Marketing/landing pages:** Can use more dramatic animations (parallax, scroll-triggered reveals, hero animations)
- **Dashboards/SaaS:** Keep animations tame and functional. Chart hover states, subtle transitions, quick feedback. Users are here to work, not watch.
- **Forms/data entry:** Minimal animation. Inline validation, focus transitions, submit feedback only.
