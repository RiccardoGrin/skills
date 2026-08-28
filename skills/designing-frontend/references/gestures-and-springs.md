---
summary: Spring physics, interruptible motion, drag tracking, velocity handoff, momentum projection, and rubber-banding for gesture-driven interfaces
read_when: building a drawer, sheet, carousel, slider, swipe-to-dismiss, drag-and-drop, or any interaction where the user's finger or pointer drives the motion directly
---

# Gestures and Springs

Duration-based CSS transitions are the right tool for state-to-state changes — see `animation-and-motion.md`.
They are the wrong tool the moment the user's own hand drives the motion.
A fixed-duration curve cannot respond to new input, cannot start from where the element currently is, and cannot inherit the speed of a flick.

The through-line for everything below: **motion should start from the current on-screen value, inherit the user's velocity, project momentum forward, and be grabbable and reversible at any instant.**

Reach for this file when the interaction is draggable, swipeable, throwable, or interruptible. Otherwise stay with transitions.

---

## Response: Kill Latency First

Everything else is built on this. The moment lag appears, the sense of directness collapses.

- **Respond on pointer-down, not on release.** A button highlights the instant it is pressed. Waiting for `click` to show feedback feels dead.
- **Audit every latency on the input path** — debounces, artificial timers, transition waits, the legacy ~300ms tap delay. Anything not essential is a regression.
- **Feedback is continuous during the interaction, not only at the end.** A drag, slider, or drawer updates 1:1 with the pointer the whole way through. Animating only on gesture completion is the single most common failure.

```css
.button {
  transition: transform 100ms var(--ease-out);
}
.button:active {
  transform: scale(0.96);
}
```

---

## Direct Manipulation: 1:1 Tracking

When the user drags something it must stay glued to the pointer, and it must respect the offset from *where they grabbed it*. Snapping the element's center to the pointer on grab breaks the illusion immediately.

```js
el.addEventListener('pointerdown', (e) => {
  // Capture so tracking survives the pointer leaving the element's bounds
  el.setPointerCapture(e.pointerId);

  // Respect where they actually grabbed it
  const grabOffset = e.clientY - el.getBoundingClientRect().top;

  // Keep a short history of {position, timestamp} — you need velocity at release
  history.length = 0;
  history.push({ y: e.clientY, t: e.timeStamp });
});
```

Track a short position/timestamp history from `pointermove`, not just the latest point. Velocity computed from a single frame is noisy.

---

## Interruptibility: The Most Important Rule

The thought and the gesture happen in parallel. A user must be able to grab a moving element mid-flight and reverse it without waiting for the animation to finish. A closing sheet the user grabs again should follow the finger, not finish closing and then reopen.

- **Never lock out input during a transition.**
- **Always animate from the presentation (live on-screen) value, never the logical target value.** On interrupt, read the element's current transform and start the new animation from there. Starting from the target causes a visible jump.
- **Do not use CSS transitions or `@keyframes` for anything gesture-driven.** They cannot be smoothly grabbed and retargeted mid-flight. Springs animate from the current value by default, which is exactly what interruption needs.
- **On reversal, blend velocity rather than hard-cutting it.** Swapping one animation for another at a reversal creates a velocity discontinuity that reads as a brick wall. Use a spring library that retargets from the current velocity.
- **Decompose 2D motion into independent X and Y springs.** A single spring over a 2D distance desyncs when the axes carry different velocities.

---

## Spring Parameters

Think in two designer-facing values, not the physics triplet:

- **Damping ratio** — controls overshoot. `1.0` is critically damped: no bounce, smooth settle. Below `1.0` overshoots and oscillates; lower means bouncier.
- **Response** — how quickly the value reaches the target, in seconds. Lower is snappier. This is **not** a duration: a spring has no fixed duration, its settle time emerges from the parameters.

**Defaults:**

- Start at **damping `1.0`** for most UI. Graceful, non-distracting, never draws attention to itself.
- Add bounce (**damping ~`0.8`**) **only when the gesture itself carried momentum** — a flick, a throw, a drag release. Overshoot on a menu that merely faded in feels wrong; overshoot on a card you threw feels right.

| Interaction | Damping | Response |
|---|---|---|
| Move / reposition | `1.0` | `0.4` |
| Rotation | `0.8` | `0.4` |
| Drawer / sheet | `0.8` | `0.3` |

**Web mapping.** Motion (formerly Framer Motion) exposes `bounce` + `duration`, which maps closely onto damping + response: `bounce: 0` is critically damped, `bounce: 0.2` is a light overshoot.

```js
import { animate } from 'motion';

// Critically damped default — no overshoot
animate(el, { y: 0 }, { type: 'spring', bounce: 0, duration: 0.4 });

// Momentum interaction — a little bounce, earned by the flick that preceded it
animate(el, { y: target }, { type: 'spring', bounce: 0.2, duration: 0.4, velocity });
```

Keep bounce in the `0.1`-`0.3` range when used at all. Anything higher belongs to toys and celebrations.

---

## Velocity Handoff

When a gesture ends, the animation must continue at the pointer's exact release velocity. Without this there is a visible seam between dragging and animating — the element stops, then starts again. This detail separates "fluid" from "fine."

Compute velocity from the position history, then pass it as the spring's initial velocity:

```js
const dt = last.t - first.t;
const velocity = (last.y - first.y) / dt * 1000;   // px/s
```

Motion takes absolute px/s directly via its `velocity` option. Some spring APIs want a *relative* velocity, normalised by the remaining distance:

```
relativeVelocity = gestureVelocity / (targetValue - currentValue)
```

Element at `y=50`, target `y=150` (100px to go), finger moving at 50px/s gives `50 / 100 = 0.5`.

---

## Momentum Projection

Do not snap to the nearest boundary measured from the release point. Use velocity to **project where the gesture was going**, exactly as scroll deceleration does, then snap to the target nearest that projected point. This is what makes a flick feel like a throw rather than a nudge.

```js
// Exponential decay — this, not the textbook v^2/(2a)
function project(initialVelocity /* px/s */, decelerationRate = 0.998) {
  return (initialVelocity / 1000) * decelerationRate / (1 - decelerationRate);
}

const projected = currentPosition + project(releaseVelocity);
const target    = nearestSnapPoint(projected);
animateSpringTo(target, { velocity: releaseVelocity });   // then hand off velocity
```

`decelerationRate` of `0.998` gives a normal scroll feel; `0.99` is snappier. This is the standard behavior behind good bottom sheets and carousels.

**Decide reverse-vs-commit on the velocity sign, not the position.** A user who drags a sheet halfway down and then flicks it back up has told you what they want, regardless of where their finger ended.

Distance thresholds alone are not enough either: dismiss on `Math.abs(distance) > THRESHOLD` **or** velocity above roughly `0.11` px/ms. A quick flick should be enough on its own.

---

## Rubber-Banding at Boundaries

At an edge, resist progressively instead of stopping dead. A hard stop reads as frozen; continuous resistance reads as responsive with nothing more to show. Real things slow before they stop.

```js
// The further past the bound, the less the element follows
function rubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

Apply the same idea to a drawer dragged past its open position, a list pulled past its top, and a slider pushed past its maximum.

---

## Gesture Feel Checklist

- **Tap** — highlight on pointer-*down* (instant), commit on pointer-*up*. Allow ~10px of hit padding, and allow cancel by dragging away and back.
- **Drag / swipe** — require a small movement threshold (~10px hysteresis) before committing to a direction, then track 1:1.
- **Detect all plausible gestures in parallel from the first move**, then cancel the losers once intent is clear. Avoid recognisers that only report a final state (`swipeleft`-style events): they throw away the continuous tracking that feedback depends on.
- **Multi-touch protection** — ignore additional touch points once a drag has begun. Without it, switching fingers mid-drag makes the element jump.
- **Minimise disambiguation delays.** Double-tap detection unavoidably delays single taps. Pay that cost only where double-tap genuinely exists.

```js
function onPress() {
  if (isDragging) return;   // second finger arrives mid-drag — ignore it
  // start drag...
}
```

---

## Spatial Consistency

- **Enter and exit along the same path.** A panel that slides in from the right dismisses to the right. In-from-right, out-the-bottom reads as two unrelated elements.
- **Anchor to the source.** A menu, popover, or sheet originates from the element that triggered it. Set `transform-origin` to the trigger so the relationship between button and content is obvious. Modals are the exception: they are not anchored to a trigger and stay centered.
- **Mirror the easing on reversible transitions** so the return path matches the outbound one.
- **Hint in the direction of travel.** Humans predict a final state from a trajectory, so the intermediate frames should point at the outcome rather than interpolating blindly toward it.

---

## Frame-Level Smoothness

Smoothness is about what is in the frames, not only the frame rate.

- Keep the per-frame positional change below the perception threshold, or fast motion strobes.
- For very fast motion, a subtle motion blur or stretch encodes speed better than a hard sharp streak.
- `requestAnimationFrame` is the display-synced clock. Animate only compositor-friendly properties (`transform`, `opacity`, `filter`) and add `will-change` only where you have observed first-frame stutter.
- Changing a CSS custom property on a parent recalculates styles for every child. In a drawer with many rows, writing `--swipe-amount` on the container is expensive; write `transform` on the element instead.

```js
// Bad — style recalc cascades to all children
container.style.setProperty('--swipe-amount', `${distance}px`);

// Good — touches one element
el.style.transform = `translateY(${distance}px)`;
```

---

## Reduced Motion

Reduced motion means gentler and non-vestibular, not absent. Gesture tracking itself is direct manipulation and stays — what goes is the projected, springy, overshooting part.

```css
@media (prefers-reduced-motion: reduce) {
  .sheet { transition: opacity 200ms ease; transform: none !important; }
}
```

- Replace projection and overshoot with a short cross-fade or a direct settle.
- Keep opacity and color changes that carry meaning.
- Avoid full-viewport moving backgrounds and slow looping oscillations near 0.2 Hz.

```jsx
const reduce = useReducedMotion();
const closedX = reduce ? 0 : '-100%';
```

---

## Quick Reference

| Need | Technique | Value |
|---|---|---|
| Default UI spring | Critically damped | damping `1.0`, response `0.3-0.4` |
| Momentum / flick spring | Slight overshoot | damping `~0.8`, response `0.3-0.4` |
| Gesture to spring | Hand off release velocity | px/s directly, or `v / (target − current)` if normalised |
| Flick landing point | Project momentum | `current + (v/1000)·d/(1−d)`, `d ≈ 0.998` |
| Interrupt cleanly | Start from the live on-screen value | read the current transform |
| Avoid reversal brick wall | Carry velocity through retarget | spring that blends velocity |
| Decide reverse vs. commit | Velocity sign, not position | at release |
| 1:1 drag | Pointer Events + `setPointerCapture` | respect the grab offset |
| Dismiss threshold | Distance **or** velocity | velocity > ~`0.11` px/ms |
| Boundary | Rubber-band | progressive resistance, constant `0.55` |
| Feedback timing | Pointer-down, continuous | never only at the end |
