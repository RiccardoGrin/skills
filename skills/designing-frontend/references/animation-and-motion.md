---
summary: Whether to animate at all, timing functions and durations, entrance/exit craft, interruptibility, press feedback, theme-switch smear, 3D and SVG animation, scroll effects, loading states, and how to review motion
read_when: Adding or reviewing any transition or animation, choosing easing curves or durations, building entrance/exit or icon-swap motion, or diagnosing why an interaction feels sluggish
---

# Animation and Motion

For gesture-driven motion — drawers, sheets, carousels, swipe-to-dismiss, anything the user's finger drives directly — read `gestures-and-springs.md` instead. This file covers state-to-state motion.

## Should This Animate At All?

Answer this before writing any animation code. **How often will a user see it?**

| Frequency | Decision |
|---|---|
| 100+ times a day (keyboard shortcuts, command palette, sending a message) | No animation. Ever. |
| Tens of times a day (row hovers, list navigation, tab switches) | Instant feedback, or ≤150ms on opacity/color only |
| Occasional (modals, drawers, toasts, panel opens) | Standard animation |
| Rare or first-time (onboarding, empty states, success moments) | Room for delight |

**Never animate a keyboard-initiated action.** These are repeated hundreds of times a day; animation makes them feel slow and disconnected from the keypress. Raycast has no open/close animation, and that is the correct call for something opened that often.

An animation on a high-frequency interaction charges its attention cost on every single trigger. That is the whole argument.

Then answer **why does this animate?** The valid purposes are:

1. **Feedback** — confirm the interface heard the user (button press, submit)
2. **Orientation** — show where something came from or went (panel expands from its trigger)
3. **Continuity** — prevent a jarring pop when an element appears or disappears
4. **State indication** — make a change legible (a morphing icon)
5. **Explanation** — a marketing or onboarding animation that teaches something

If the honest answer is "it looks cool" and the user will see it often, do not animate it.

**Motion is never the only feedback channel.** Every state change an animation communicates must remain visible when it does not run: a color change, an icon swap, a label. Users with reduced motion enabled, and anyone who blinked, still need to see what happened.

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
| `ease-out` | Elements entering **and** exiting. The default for UI. |
| `ease-in-out` | Elements moving or morphing between on-screen positions |
| `ease` | Hover and color changes |
| `linear` | Constant motion — progress bars, spinners, marquees |
| `ease-in` | Almost never. See below. |
| `cubic-bezier()` | Full control over the curve |

**Do not use `ease-in` for UI.** It starts slow, which delays movement at exactly the moment the user is watching most closely. A dropdown with `ease-in` at 300ms *feels* slower than the same 300ms with `ease-out`. This applies to exits too: an exit gets `ease-out` and a shorter duration, not `ease-in`.

### House Curves

The built-in CSS easings are weak — they lack the punch that makes motion read as intentional. Define these as tokens and use them everywhere:

```css
:root {
  /* Strong ease-out — the workhorse for entrances, exits, and state changes */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);

  /* Strong ease-in-out — for elements moving between on-screen positions */
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);

  /* Crisp ease-out — cross-fades, icon swaps, tight micro-interactions */
  --ease-crisp: cubic-bezier(0.2, 0, 0, 1);

  /* iOS-style drawer curve */
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
}
```

`cubic-bezier(0.4, 0, 0.2, 1)` (the Material standard curve) is a safe generic fallback, but it is noticeably softer than `--ease-out` above. If a project has already standardised on it, match the project. Never approximate one of these curves with a similar-looking one — `cubic-bezier(0.2, 0, 0, 1)` is not `cubic-bezier(0.4, 0, 0.2, 1)`.

### Duration Guidelines

**UI animations stay under 300ms.** A 180ms dropdown feels more responsive than a 400ms one, and users read that responsiveness as the app being fast.

| Element | Duration |
|---|---|
| Button press feedback | 100-160ms |
| Tooltips, small popovers | 125-200ms |
| Dropdowns, selects, menus | 150-250ms |
| Modals, drawers, sheets | 200-500ms |
| High-frequency hover / row states | ≤150ms, opacity and color only |
| Marketing or explanatory sequences | As long as the story needs |

**Exit is faster than enter.** The user's attention has already moved to the next thing; a slow exit fights for attention it should be giving up. Enter at 300ms, exit at 150ms.

The inverse holds for deliberate actions: slow where the *user* is deciding, fast where the *system* is responding. A hold-to-delete fills over 2s linear, then snaps back in 200ms `ease-out` on release.

**Perceived performance is real.** A faster-spinning spinner makes an identical load time feel shorter. A tooltip that opens instantly after the first one in a toolbar makes the whole toolbar feel faster.

## Transitions vs Keyframes: Interruptibility

A CSS transition interpolates toward whatever the latest state is, so it can be interrupted and retargeted mid-flight. A `@keyframes` animation runs a fixed timeline and restarts from the beginning when re-triggered.

| | Transitions | Keyframes |
|---|---|---|
| Interruptible | Yes, retargets mid-flight | No, restarts |
| Use for | Interactive state changes: hover, toggle, open/close | One-shot staged sequences: page entrances, loading loops |

Anything a user can trigger rapidly — a toast queue, a toggle, a drawer — must be a transition. With keyframes, closing mid-open snaps or replays, and it reads as broken.

```css
/* Good — clicking again mid-animation reverses smoothly */
.drawer { transform: translateX(-100%); transition: transform 200ms var(--ease-out); }
.drawer.open { transform: translateX(0); }
```

## Entrance and Exit Craft

### Never animate from `scale(0)`

Nothing in the physical world appears from nothing. An element scaling up from zero looks like it materialised out of the void.

```css
/* Bad */ .entering { transform: scale(0); }
/* Good */ .entering { transform: scale(0.95); opacity: 0; }
```

Start at `0.9`-`0.95` paired with opacity. Even a barely visible initial size makes the entrance read as a real object arriving.

### Popovers scale from their trigger

The default `transform-origin: center` is wrong for almost every anchored surface. A popover, dropdown, tooltip, or context menu should scale out of the element that opened it, so the spatial relationship is obvious.

```css
.popover { transform-origin: var(--transform-origin); }  /* set from the trigger position */
```

**Modals are the exception** — they are not anchored to a trigger and stay centered.

### Enter with `@starting-style`

The modern way to animate entry with no JavaScript, replacing the `useEffect(() => setMounted(true))` pattern:

```css
.toast {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 300ms var(--ease-out), transform 300ms var(--ease-out);

  @starting-style {
    opacity: 0;
    transform: translateY(100%);
  }
}
```

Percentage translate values are relative to the element's own size, so `translateY(100%)` moves a toast exactly its own height regardless of content. Prefer percentages over hardcoded pixels for offscreen positioning.

### Split and stagger infrequent entrances

Where a staged entrance genuinely communicates hierarchy — a page hero on first load, a success state, an empty state — split the content into semantic chunks and stagger them. Animating one container gets you far less for the same cost.

- Stagger groups (title, description, actions) by ~100ms
- Optionally split a headline into words at ~80ms
- Combine `opacity`, `translateY` (~12px), and `blur(4px) → 0`
- Keep total stagger short. Long cascades make the interface feel slow, and stagger must never block interaction.

```css
.stagger-item {
  opacity: 0;
  transform: translateY(12px);
  filter: blur(4px);
  animation: fade-in-up 400ms var(--ease-out) forwards;
}
.stagger-item:nth-child(1) { animation-delay: 0ms; }
.stagger-item:nth-child(2) { animation-delay: 100ms; }
.stagger-item:nth-child(3) { animation-delay: 200ms; }

@keyframes fade-in-up {
  to { opacity: 1; transform: translateY(0); filter: blur(0); }
}
```

Never stagger routine interactions — row hovers, keystrokes, repeated tab changes.

### Exits stay subtle

Use a small fixed `translateY` (about `-12px`), not the element's full height, and keep some directional movement so the eye knows where it went. Where motion adds no information and the interaction repeats often, remove the element immediately instead.

```css
.item-exit {
  opacity: 0;
  transform: translateY(-12px);
  transition: opacity 150ms var(--ease-out), transform 150ms var(--ease-out);
}
```

### Contextual icon swaps

When an icon changes by state (play → pause, bookmark → bookmarked, outline → filled), cross-fade it rather than toggling visibility. Use exactly these values:

- `scale`: `0.25` → `1`
- `opacity`: `0` → `1`
- `filter`: `blur(4px)` → `blur(0px)`
- With a spring: `{ type: "spring", duration: 0.3, bounce: 0 }` — bounce is always `0`
- Without a motion library: keep both icons in the DOM, one absolutely positioned, and cross-fade with `--ease-crisp` over 300ms. Both icons animate, and no dependency is added.

Animate icons that appear on hover, change state, or indicate loading and success. Do not animate static navigation icons, decorative icons, or icons that are always visible.

### Blur to mask an imperfect crossfade

When a crossfade between two states feels wrong no matter the easing or duration, it is because the eye is seeing two distinct objects overlap. A brief `filter: blur(2px)` during the transition blends them into one perceived transformation.

Keep blur under 20px — heavy blur is expensive, especially in Safari.

### Skip enter animations on first paint

An element already in its default state should animate on later state changes, not on page load. With `AnimatePresence`, that is `initial={false}`. Verify on a full refresh afterwards: this is wrong for anything that relies on its `initial` prop for a genuine first-load entrance, like a staggered hero.

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

- Animate only `transform`, `opacity`, and `filter` — they run on the compositor thread and avoid layout/paint.
- Avoid animating `width`, `height`, `top`, `left`, `margin`, `padding` — these trigger expensive layout recalculations.
- **Never `transition: all`.** Name the exact properties. `all` makes the browser watch every property, animates ones you never intended (colors, padding, shadows), and blocks optimisations. In Tailwind, prefer `transition-[opacity,scale]` over `transition-all`; note that `transition-transform` already covers `transform, translate, scale, rotate`.
- Use `will-change` sparingly, and only for properties the GPU can actually composite.

| Property | GPU-compositable | Worth a `will-change` |
|---|---|---|
| `transform` | Yes | Yes |
| `opacity` | Yes | Yes |
| `filter` (blur, brightness) | Yes | Yes |
| `clip-path` | Newer Chromium only | Rarely — not reliable cross-browser |
| `top`, `left`, `width`, `height` | No | No |
| `background`, `border`, `color` | No | No |

`will-change` pre-promotes an element to its own compositing layer, avoiding a one-time promotion stutter on the first frame. Each layer costs memory, so add it when you have *observed* first-frame stutter, never preemptively. Safari benefits most. Never `will-change: all`.

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

### Press Feedback

Every pressable element scales down on `:active`. It is the cheapest possible signal that the interface heard the user.

```css
.button {
  transition: scale 150ms var(--ease-out);
}
.button:active {
  scale: 0.96;
}
```

Use `0.96`. Below `0.95` reads as exaggerated, above `0.98` is invisible. Provide a way to switch it off (a `static` prop) for elements where the motion would distract — a row in a dense table, a control that fires on every keystroke.

### Suppress Transitions on Theme Switch

Flipping light/dark changes `color`, `background-color`, `border-color`, and `box-shadow` on nearly every element at once. Every transition on those properties fires together, and the switch reads as a slow smear instead of an instant change.

Inject a stylesheet that kills every transition, force a reflow so the new colors commit while it still applies, then remove it on the next frame:

```js
const style = document.createElement('style');
style.append(document.createTextNode('*,*::before,*::after{transition:none !important}'));
document.head.append(style);

void document.body.offsetHeight;   // read for its side effect: forces a sync style flush

requestAnimationFrame(() => {
  requestAnimationFrame(() => style.remove());
});
```

Wrap both the in-app toggle and the OS-level `prefers-color-scheme` change listener. `next-themes` ships this as `disableTransitionOnChange`.

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

---

## Reviewing Animation

Motion defects are invisible at full speed. Slow it down.

- **Replay at 10% speed** in the browser's Animations panel, or temporarily multiply durations by 5. What feels vaguely off at full speed is nameable at 10%.
- **What to look for in slow motion:** do colors blend, or do you see two distinct states overlapping? Does the easing start or stop abruptly? Is the `transform-origin` correct, or does the element grow from the wrong point? Are opacity, transform, and color actually in sync?
- **Step frame by frame** to catch timing drift between coordinated properties.
- **Review the next day with fresh eyes.** You will see imperfections you were blind to while building.
- **Test gestures on a real device**, not a simulator. Connect a phone to the dev server over the local network.

### Common Defects

| Symptom | Cause | Fix |
|---|---|---|
| Feels sluggish despite a short duration | `ease-in` on a UI element | `--ease-out` |
| Element pops out of nowhere | `scale(0)` entry | `scale(0.95)` + opacity |
| Popover grows from the wrong place | `transform-origin: center` | Origin at the trigger (modals exempt) |
| Reopening mid-close snaps | Keyframes on an interactive element | CSS transition |
| Unintended properties animate | `transition: all` | Name exact properties |
| Theme toggle smears the page | Every transition fires at once | Suppress transitions for the swap |
| Everything arrives at once | No stagger on a staged entrance | 100ms between semantic groups |
| Exit steals attention from what's next | Exit as long and dramatic as the enter | Shorter, smaller, `ease-out` |
| First frame stutters | Layer promoted at animation start | `will-change: transform`, sparingly |
| Change is invisible with reduced motion on | Motion is the only feedback channel | Add a static cue: color, icon, label |
