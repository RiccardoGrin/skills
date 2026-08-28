---
summary: Accessibility, ARIA, accessible names, focus and keyboard patterns, hit areas, forms, live regions, alt text, overflow, images, URL state, touch, zoom and reflow, locale, and the flag-on-sight list
read_when: building or reviewing any interactive element, custom widget, form, table, dialog, or navigation; handling user-generated or translated content; or auditing an interface for correctness rather than aesthetics
---

# Interface Quality

The rest of this skill catches work that reads as *generic*. This file catches work that reads as *amateur*: broken keyboard access, a blocked paste handler, a decorative glow eating every click, a hardcoded date format.

Most of it is free if you use the platform. Native elements ship with keyboard support, real labels announce themselves, and a visible focus ring is one CSS rule. When unsure, take the platform default over a custom rebuild, and remove ARIA rather than add it.

Two reference points worth reading directly when the details matter: Vercel's Web Interface Guidelines, and the ARIA Authoring Practices Guide for keyboard patterns.

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

None of this is optional because a component came from a library. A pulled component gets checked in the same pass that restyles it.

---

## Native Elements First

The first rule of ARIA is not to use ARIA when a native element exists. No ARIA is better than bad ARIA — a screen reader trusts the roles you declare, so a wrong one is worse than none at all.

| Element | Use for | What you get free |
|---|---|---|
| `<a href>` | Navigation, anything that changes the URL | Command/middle-click, copy link, Enter activation |
| `<button>` | Actions: submit, toggle, open, delete | Focus, Enter *and* Space activation, form semantics |
| `<div onClick>` | Nothing | No role, no focus, no keyboard. A screen reader sees plain text |

If it looks clickable it must be clickable, and if it is clickable it must be a real interactive element. A "button" that navigates is a styled link. Where a native element is genuinely impossible, the full replacement is `role="button"` plus `tabindex="0"` plus Enter and Space handlers — which is why the native element is always less code.

**The five ARIA rules:** use the native element if one exists; do not change native semantics without cause; every interactive ARIA control must be keyboard-operable, because a role is a promise of the whole keyboard model; never put `aria-hidden` or `role="presentation"` on a focusable element; every interactive element has an accessible name.

### Common ARIA mistakes

| Mistake | Why it fails |
|---|---|
| `aria-label` on a plain `<div>` or `<span>` | Most screen readers ignore names on non-interactive, role-less elements |
| `<button role="button">` | Redundant. Noise with no benefit |
| `aria-hidden="true"` on or above a focusable element | Creates stops you can Tab to that do not exist for a screen reader |
| `aria-labelledby` pointing at a missing id | Silently produces no name at all |
| `role="menu"` on site navigation | `menu` promises app-style arrow-key behavior; navigation is a `<nav>` with a list |

---

## Accessible Names

Name precedence, highest first: `aria-labelledby`, then `aria-label`, then the native label (a `<label>`, the element's text, `alt`), then `title`.

- Prefer visible text or `aria-labelledby` over `aria-label`. An `aria-label` is invisible, drifts out of sync with the UI, and is handled inconsistently by translation tools.
- Icon-only buttons always need a name, with the icon itself `aria-hidden="true"`.
- **Label in name:** the visible text must appear in the accessible name. A button reading "Send" with `aria-label="Submit message"` breaks voice control, because the user says "click Send" and nothing matches.
- Mark brand names, code tokens, and identifiers `translate="no"` so auto-translation does not garble them.

---

## Focus

- Style `:focus-visible`, never bare `:focus`. Keyboard users get a ring; mouse users do not.
- **Prefer the browser's own indicator.** It adapts to platform and forced-color settings without you predicting every background. Adding only `outline-offset: 2px` keeps it and gives it room.
- A custom ring needs an explicit, verified color. `outline: 2px solid` with no color renders `currentColor`, which is not automatically accessible — the outline crosses colors the text never sits on. Inspect the whole perimeter against every adjacent color: component fills, page surfaces, images, hover and selected states.
- Never `outline: none` without a verified replacement.
- The ring appears instantly and never fades or transitions in.
- In forced-colors mode, keep the default color adjustment or name a system color.
- Use `:focus-within` when a wrapper should light up while an inner input has focus.

### tabindex

`tabindex="0"` joins the natural tab order and is only for custom interactive elements that are not natively focusable. `tabindex="-1"` is focusable by script only — for headings you move focus to, modal containers, and roving-tabindex members. **Positive values, never.** They hijack the tab order for the whole page; fix the DOM order instead.

**Roving tabindex** is how a composite widget occupies one Tab stop. Tabs, menus, toolbars, and radio groups give the active item `tabindex="0"` and every other item `-1`, and arrow keys move both focus and the zero.

### Trapping and restoring focus

Prefer a native `<dialog>` opened as a modal: it gives you the trap, the inert background, and Escape handling for free. Otherwise set `inert` on the background content, which removes it from the tab order and from assistive technology in one move.

- On open, move focus inside. For a destructive confirmation, focus the *least* destructive action.
- On close, return focus to the trigger, or to the nearest logical container if the trigger is gone.
- Add `overscroll-behavior: contain` so scrolling the dialog never scrolls the page behind it.

### Keyboard patterns

Native elements come with these. Custom widgets must implement them, because a role is a promise.

| Widget | Keys |
|---|---|
| Dialog | Tab and Shift+Tab cycle inside and wrap; Escape closes |
| Tabs | Arrows move between tabs and wrap; Tab exits to the panel; Home and End jump to the ends |
| Menu button | Enter, Space, or Down opens and focuses the first item; Up opens at the last; Escape closes and refocuses the button |
| Disclosure / accordion | The header is a `<button aria-expanded>`; Enter and Space toggle |
| Combobox | Down opens and moves into the list; Enter accepts; Escape closes and returns to the input; typing filters |
| Listbox / radio group | Arrows move selection; one Tab stop for the whole group |

Universal rules: Escape dismisses whatever opened last, in order — tooltip, then menu, then dialog. Arrows move *within* a composite widget while Tab moves *between* widgets. Enter submits from a focused input; in a textarea, Enter inserts a newline and Command or Control plus Enter submits.

Tabs pick an activation mode: automatic, where the panel switches as arrows move focus, when panels render instantly; manual, requiring Enter or Space, when switching is expensive.

### Client-side navigation

A route change in a single-page app resets nothing and announces nothing. On navigation, update the document title to match the new context, move focus to the new view's heading (given `tabindex="-1"`) or to `<main>`, scroll to top going forward, and restore scroll position going back.

---

## Hit Areas

| Standard | Minimum |
|---|---|
| WCAG 2.5.8 (AA) | 24×24px — the hard floor |
| WCAG 2.5.5 (AAA) | 44×44px |
| Apple HIG | 44×44pt |
| Material | 48×48dp |

Aim for 44px on touch and 40px on desktop where density permits. Smaller controls are not automatic failures — the spacing exception passes an undersized target when a 24px circle centered on it intersects no other target. In practice, 20px targets need a 4px gap.

**The visible element can stay small; the hit area is what must be big.** Anything that looks clickable must be clickable across its whole visual extent, with no dead zones, and a checkbox shares one hit target with its label.

Extend a small control with a pseudo-element on the wrapping `<label>` or `<button>`, never on the `<input>` — replaced elements do not render `::before` and `::after` reliably. Where the element can afford real box size, give it `min-width` and `min-height` instead and let the browser have real geometry.

**Extended hit areas never overlap.** Where two would collide, shrink one to the largest size that does not.

### Decorative layers eat clicks

A gradient scrim, a glow, a blurred sheen, a full-bleed `::after` painted over interactive content absorbs every pointer event its box covers. The control underneath looks live and does nothing, and no amount of hit-area sizing fixes it. Give every decorative layer `pointer-events: none` and `aria-hidden="true"`.

Keep pointer events on any layer the user is meant to hit — a modal scrim that dismisses on click is a control, not decoration.

---

## Forms

### Labels

Every control needs a programmatic label: a `<label for>` pointing at the input's id, or a wrapping `<label>`. **A placeholder is never a label** — it disappears the moment the user types and usually fails contrast. A placeholder used *alongside* a label shows the expected format.

Label and control share one hit target with no dead zone between them. Mark required fields natively plus a visible indicator explained once per form.

### Errors

- `aria-invalid="true"` on the failing field, removed once fixed.
- `aria-describedby` links the field to its inline error so it is announced with the field.
- Errors render inline beside their field, with text or an icon. **Never a red border alone** — that is a color-only cue.
- On submit, focus the first invalid field. That focus move is itself the announcement.
- **Never disable submit until the form is valid.** Keep it enabled, allow the incomplete submission, and let validation surface.
- Accept free text and validate after. Never block typing or filter characters as the user types. Trim before validating, because autofill and text expansion add trailing spaces.

### Autocomplete and input types

`autocomplete` with a meaningful `name` fills a form in one tap and is a WCAG requirement for fields about the user.

| Field | Token |
|---|---|
| Name | `name`, or `given-name` / `family-name` |
| Email, phone | `email`, `tel` |
| Address | `street-address`, `address-line1`, `postal-code`, `country` |
| Card | `cc-number`, `cc-exp`, `cc-csc`, `cc-name` |
| Login | `username`, `current-password` |
| Signup or reset | `new-password` |
| Two-factor code | `one-time-code` |

Prefix with a section where relevant, as in `shipping street-address`.

The right `type` and `inputmode` summon the right mobile keyboard. A one-time code, PIN, or card number is `type="text"` with `inputmode="numeric"` — it keeps text semantics and loses the spinner. Money and decimals use `inputmode="decimal"`. Reserve `type="number"` for a genuine numeric quantity.

Turn spellcheck off on emails, codes, and usernames. Stay compatible with password managers and two-factor autofill: a real `<form>`, correct autocomplete, no fake inputs. **Never block paste.**

### Submit behavior

Keep submit enabled until the request starts, then disable it and show a spinner *beside the original label*, not replacing it — the label is what tells assistive technology which button is busy. Warn before navigating away from unsaved changes, and never lose typed input to a re-render.

### Disabled states

Native `disabled` supplies the platform's complete behavior: out of the tab order, activation suppressed, excluded from submission. `aria-disabled="true"` only *announces* the state and changes neither focusability nor behavior nor styling.

- A natively disabled control suppresses pointer events and leaves the tab order, so **a tooltip on it never opens** for keyboard or touch users. Put the reason in visible text beside it, or switch to `aria-disabled` so it stays focusable.
- With `aria-disabled`, block activation in the handler yourself and style the state explicitly.
- Never set both on the same element.
- Signal disabled on three channels — reduced opacity, `cursor: not-allowed`, and the real attribute. Opacity alone is not a disabled state.
- Disabled controls are exempt from contrast minimums. Keep them legible anyway.

---

## Announcing Change

Work down this list and stop at the first match:

1. **Focus already moves there** — an opened dialog, the first invalid field. The focus move is the announcement. Nothing else needed.
2. **Tied to a specific control** — a field error, a character count. Use `aria-describedby` on that control.
3. **Not urgent, not tied to a control** — a toast, "Saved", a result count, a loading state. Use a polite live region, `role="status"`.
4. **Urgent and not tied to a control** — a form-level failure, a session expiry. Use `role="alert"`, and nothing else.

Rules that make announcements actually fire:

- For repeated polite updates, keep a **stable empty region in the DOM** and change its text. Inserting a new region together with its content is announced inconsistently.
- Default to polite. Overusing assertive is the most common live-region mistake, because it interrupts whatever the user was reading.
- Keep messages short and self-contained; the whole region is re-read on change.
- **Never move focus to a toast.** Announce it and leave focus where the user is working.
- Never put the only path to an action inside an auto-dismissing element.

### Visually hidden content

The `.sr-only` pattern hides content visually while keeping it in the accessibility tree. Use 1px boxes rather than zero, because some screen readers skip zero-sized elements, and add `white-space: nowrap` so words are not read as one run-together string. Never `display: none` or `visibility: hidden`, which remove the content entirely.

Use it for context sighted users get visually: "opens in new tab", a table caption, an icon-only control's label where `aria-label` is not an option.

---

## Images, Alt Text, and SVG

Choose alt text by purpose, not by what the image looks like.

| Purpose | Alt |
|---|---|
| Decorative, or redundant with adjacent text | `alt=""` — empty, but present |
| Informative | The meaning it adds, not its appearance |
| Functional (the image is the control) | The action: a search icon is "Search", not "magnifying glass" |
| Image of text | The exact text. Better: use real text |
| Complex (chart, diagram) | A short summary, with the full data as a table or text nearby |

**A missing `alt` is worse than an empty one**, because screen readers fall back to reading the file name.

For SVG: decorative gets `aria-hidden="true"` and `focusable="false"`; a meaningful inline SVG gets `role="img"` with a label. An `<img>` with real alt text is the most reliable delivery for simple cases.

Give every image explicit `width` and `height` to prevent layout shift, `loading="lazy"` below the fold, and high fetch priority on the one critical above-fold image.

> A trap worth remembering: setting HTML `width`/`height` attributes *and* a CSS `aspect-ratio` without `height: auto` makes the browser use the literal attribute height, which silently breaks the layout.

Prerecorded video needs captions and audio needs a transcript. Never autoplay with sound, and always render controls.

---

## Motion, Autoplay, and Timed UI

Make motion **opt-in** by wrapping it in `@media (prefers-reduced-motion: no-preference)`, rather than chasing every animation with an override afterwards. Where an existing codebase makes that impractical, the global kill switch is the fallback — and it sets durations to `0.01ms` rather than `none` specifically so `animationend` and `transitionend` still fire and any JavaScript waiting on them does not hang.

Reduced motion means reduced, not eliminated. It targets vestibular triggers, not feedback.

| Disable entirely | Replace | Keep |
|---|---|---|
| Parallax | Slide, scale, zoom → opacity crossfade | Loading and progress indicators |
| Autoplaying video, looping decoration | Smooth scrolling → instant jump | Instant state changes: hover color, focus ring |
| Large-scale movement across the screen | Auto-rotating carousels → start paused | Brief functional feedback, a button press |

**Anything moving, blinking, or updating on its own for more than five seconds needs a visible pause control**, muted hero videos included.

Prefer explicit dismissal over timers. A toast carrying an action, an error, or information the user may need stays until dismissed. Where one must time out, five seconds is the floor, and hovering or focusing it pauses the timer. **Never put critical information only in a timed element** — a vanished toast holding the only undo link is data loss on a schedule.

---

## Zoom, Reflow, and Units

- **200% zoom.** All content and functionality survives text scaled to 200%, and the viewport meta never caps how far the reader can zoom.
- **Reflow at 320px.** At 400% zoom on a 1280px viewport the page must work with vertical scrolling alone. Genuinely two-dimensional content is the exception: tables, maps, and code blocks scroll inside their own container.
- **Fixed heights are what break.** Use `min-height` on anything containing text and let containers grow.

Respect how the codebase is set up rather than introducing mixed units into someone else's system. Where you do have the choice:

| Use `rem` | Use `px` |
|---|---|
| `font-size` | Borders and hairlines |
| `max-width` on text containers | Focus outline width and offset |
| Media-query breakpoints | Shadow details |
| Spacing that should scale with text | Fixed-size decorations |

Breakpoints are where it matters most. At a larger base font size a `rem` query switches to the mobile layout when the *text* needs it; a `px` query never does.

---

## Content Handling

- Every text container handles overflow — truncate, clamp, or break words. Real user content is not one tidy line.
- A flex child needs `min-width: 0` for truncation to work at all.
- Truncation hides content. Where the missing text matters, keep the full value reachable in a tooltip or an expanded view.
- Test copy short, long, and translated.
- Design the empty state rather than rendering broken UI for an empty array.

## Navigation and State

- **The URL reflects state.** Filters, tabs, pagination, and expanded panels belong in query params so a view can be shared and restored.
- Navigation uses real links so command-click and middle-click work.
- Destructive actions get a confirmation or an undo window, never immediate execution. Where the action is genuinely reversible, an optimistic update plus undo beats a confirmation dialog.

## Structure

- One `<h1>`, with levels nested beneath it and headings that describe their sections. Style a heading level with CSS; never pick the tag for its default size.
- One visible `<main>` landmark. Where repeated navigation precedes it, a "Skip to content" link is the first focusable element.
- Multiple landmarks of the same type need distinguishing labels.
- The document title matches the current context, most specific first.
- Anchored headings need `scroll-margin-top` or they land under a sticky header.

## Touch

- `touch-action: manipulation` removes the double-tap zoom delay. `touch-action: none` belongs only on a surface implementing its own gestures, scoped to that surface — at page level it kills scrolling.
- Set the tap highlight color deliberately rather than inheriting the default gray flash.
- Put hover styling behind `@media (hover: hover)`. On touch, `:hover` latches after a tap and holds until the user taps elsewhere, reading as a stuck selected state.
- Autofocus sparingly: desktop only, one primary input, never on mobile where it forces the keyboard open.
- Prefer generous targets over finicky interactions — tiny drag handles and precise hover zones.

## Performance

- Lists beyond roughly 50 items get virtualized, or `content-visibility: auto`.
- Do not read layout during render. Batch reads and writes; never interleave them.
- Preconnect to asset domains; preload critical fonts.

## Theming and Locale

- `color-scheme` on the root so native scrollbars and form controls follow the theme, and a theme-color meta matching the page background.
- A native `<select>` needs an explicit background and text color or it renders unreadable in some dark modes.
- Use the platform's date and number formatting. Never hardcode a date or currency format.
- Detect language from the browser's language preferences, not from IP.

## Adjacent References

Interface copy — button labels, error messages, empty states, capitalization — is in `interface-writing.md`. Text rendering, wrapping, truncation, measure, and smart punctuation are in `typography-and-spacing.md`. Contrast measurement and repair are in `color-and-theming.md`.

---

## Flag These on Sight

Disabled zoom (`user-scalable=no`, `maximum-scale=1`) · a paste handler calling `preventDefault` · `transition: all` · `outline: none` with no verified replacement · a `<div>` or `<span>` carrying a click handler · a decorative overlay without `pointer-events: none` · images with no dimensions · a large list with no virtualization · inputs without labels · icon buttons without an accessible name · submit disabled until valid · a tooltip on a natively disabled control · `aria-hidden` on a focusable element · positive `tabindex` · a red border as the only error cue · hardcoded date or number formats · unjustified autofocus · a non-clickable badge shaped exactly like the buttons beside it
