---
name: designing-frontend
description: Guides creation of high-quality frontend interfaces using proven design principles for color, typography, spacing, layout, page composition, depth, animation, gesture physics, surface craft, interface correctness, and UX. Covers both building new UIs and auditing existing ones. Use when creating web components, pages, or applications, when a design looks generic or "like every other AI app", when polishing an interface that "feels off", or when reviewing frontend code for design quality
version: 1.3.0
---

# Designing Frontend

A comprehensive design knowledge base for building polished, professional frontends.
Apply these principles when creating new interfaces or auditing existing ones.
Framework-agnostic: the principles work with any CSS approach (vanilla, Tailwind, CSS modules, etc.).

## Reference Files

| File | Read When |
|------|-----------|
| `references/color-and-theming.md` | Choosing colors, building ramps, naming color tokens, dark mode, measuring and fixing contrast, gradients |
| `references/typography-and-spacing.md` | Type scales and roles, line height, measure, wrapping, truncation, underlines, spacing systems |
| `references/layout-and-responsiveness.md` | Building layouts with flexbox/grid, making designs responsive |
| `references/depth-and-visual-hierarchy.md` | Adding shadows, depth, borders, establishing visual hierarchy |
| `references/animation-and-motion.md` | Adding transitions, animations, scroll effects, SVG animation; deciding whether to animate at all |
| `references/gestures-and-springs.md` | Drawers, sheets, carousels, sliders, swipe-to-dismiss, drag-and-drop — anything the pointer drives directly |
| `references/surface-craft.md` | Nested border radius, optical alignment, shadow-vs-border, image outlines, icon stroke/state/sizing |
| `references/page-composition.md` | Composing a whole page or screen: show-don't-tell, narrative arc, page shapes, section archetypes, heroes, section rhythm, app shells |
| `references/interface-quality.md` | Accessibility, ARIA, focus and keyboard patterns, hit areas, forms, live regions, alt text, zoom and reflow, touch, locale — the correctness layer |
| `references/interface-writing.md` | Button labels, error messages, empty states, placeholders, settings labels, capitalization, voice and tone |
| `references/ux-and-components.md` | Choosing between a modal, popover, toast, or page; designing empty, loading, and error states; onboarding; dashboard content; design personality |

## Scope

Match the scope of the design work to the scope of the request. A change to one component does not warrant project-wide changes to color systems, spacing tokens, or theme infrastructure. A small fix needs one relevant principle, not a reference file.

If the project already has a design system, follow it. Everything here applies when building from scratch, or where the project has no established pattern for what you are about to build.

## Core Principles

These cross-cutting principles apply to every frontend task.
Reference files contain the specific techniques and values.

### 1. Simple Over Clever

Good design is as little design as possible.
More design almost always results in uglier design.
Simple does not mean minimal to the point of uselessness — all essential elements must be present.
The biggest visual payoff comes from taking an average design to "good" — pushing from good to great yields diminishing returns.

### 2. Hierarchy Is Everything

Users scan, they don't read.
Emphasize what users look for first using size, weight, and color.
De-emphasizing secondary elements is often more effective than making the primary element bigger or bolder.
Always zoom out to verify scannability.

### 3. Spacing Makes or Breaks a Design

All spacing, sizing, padding, and margin values should be divisible by 4 (converted to rem by dividing by 16).
Elements need more spacing than you think — start generous, reduce until it feels right when viewed as a whole.
Use Gestalt proximity: spacing between elements signals grouping.

### 4. Limit Your Palette

A complete UI needs only: neutral background/text shades, a brand/primary color, and a few semantic state colors.
Use HSL or OKLCH (not hex/RGB) — they map directly to design decisions.
Create 3-4 shades per color by adjusting lightness in consistent increments.

### 5. Follow Conventions

Users should understand what to do instantly without thinking.
Stick to established UI patterns (nav at top, buttons look like buttons, magnifying glass = search).
Deviating from conventions forces thought. Following conventions is good design, not boring design.

### 6. Show, Don't Tell

Every section should be mostly something to look at, with text as its caption — not mostly prose with a decorative icon on top.

A wall of feature cards, each a heading and two sentences explaining a benefit, is the most common way a well-tokenized page still reads as machine-made. Replace the explanation with the thing it describes: a claim about speed becomes a real chart, a three-step setup becomes three visual panels, a feature becomes a mockup of that feature.

Before writing a paragraph to explain something, ask whether a visual could carry it with a caption instead. Default to the visual.
Load `references/page-composition.md` for the full conversion table and the higher floor that proof sections carry.

### 7. Design With Character

Every product has a personality — discover it before building.
A financial dashboard feels different from a creative portfolio, which feels different from a developer tool.
Ask: if this product were a person, how would they dress? How would they speak?
Ask: **what makes this design unforgettable?** What's the one thing someone will remember after closing the tab?

Commit to a clear aesthetic direction. Some flavors to consider: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian. These are starting points — the right direction comes from the product's purpose and audience.

Generic AI-generated frontends have tells: perfectly centered layouts, blue-to-purple gradients, identical card grids, rounded-everything, stock illustrations, polished but soulless.
The antidote is intentional character — expressed through color boldness, type choices, copy tone, spacing rhythm, and interaction style.

**Match implementation complexity to the aesthetic vision.** Maximalist designs need elaborate code with extensive animations, textures, and effects. Minimalist designs need restraint, precision, and careful attention to spacing and typography. Bold maximalism and refined minimalism both work — the key is intentionality, not intensity.

Don't limit character to color and typography. Consider spatial composition (asymmetry, overlap, diagonal flow, grid-breaking elements) and atmospheric details (noise textures, gradient meshes, grain overlays, layered transparencies, custom cursors). These are tools, not requirements — use them when they serve the vision.

Before building, identify at least one distinguishing trait: a bold color, an unusual type pairing, a distinctive interaction pattern, a specific tone of voice, or a deliberate layout choice that makes this product feel like *this* product and not a template.
Load `references/ux-and-components.md` for detailed guidance on design personality.

### 8. Motion Is a Budget, Not a Garnish

Before animating anything, ask how often a user will see it. An action performed a hundred times a day gets no animation ever; an action performed once gets room for delight. An animation on a high-frequency interaction charges its attention cost on every single trigger.

Motion is also never the only feedback channel. Every state change an animation communicates must stay visible when the animation does not run — a color, an icon, a label.

### 9. Sameness Lives in the Page Shape

Two sites with different palettes and the same skeleton are the same site twice. The generic rhythm — hero, three feature cards, testimonial, call to action, footer — is the strongest machine-made signal at the page level, and it survives a perfect palette.

Two habits break it. **Pick the page shape by name before building, and say which one and why** — an unstated decision reverts to the most common option every time. And **find the one intentional rule-break**: a design where everything sits on the grid, evenly spaced and perfectly safe, reads as generated even when every token is right. One deliberate break is the budget, not a licence to stack decorative gestures.

### 10. The Unseen Details Compound

Nobody reports that an inner radius is off by 4px or that an icon is two pixels from optical center. They report that the product feels cheap, or they say nothing and trust it less. Concentric radii, optical alignment, matched icon weights, and correct image edges are individually invisible and collectively decisive.

Load `references/surface-craft.md` when building or reviewing any component surface.

## House Values

Where sources disagree, these are the calls. Use them unless the project has already standardised on something else — an established project convention always wins over this list.

| Decision | Value | Note |
|---|---|---|
| Press feedback | `scale(0.96)` | Below `0.95` reads exaggerated; above `0.98` is invisible |
| Default UI easing | `cubic-bezier(0.23, 1, 0.32, 1)` | Stronger than the CSS built-ins, which feel weak |
| Easing for exits | `ease-out`, shorter duration | **Never `ease-in` on UI** — it delays the frame the user is watching |
| UI animation ceiling | 300ms | Exit at roughly half the enter duration |
| Nested radius | `outer = inner + padding` | Stops applying past ~24px padding |
| Element needing an edge | `--shadow-border` ring | Elevation scale is for things that genuinely float |
| Image edge | Pure black/white at 10% | Never a tinted neutral or the brand accent |
| Spacing unit | Multiples of 4 | Group gap ≥ 2× the gap inside a group |
| Direction-dependent CSS | Logical properties | `padding-inline-start`, not `padding-left` |

Never approximate a specified curve or scale value with a similar-looking one. `cubic-bezier(0.2, 0, 0, 1)` is not `cubic-bezier(0.4, 0, 0.2, 1)`, and `0.96` is not `0.95`.

## Order of Decisions

Some decisions constrain the ones after them, so their order is not arbitrary:

1. **What the thing is** — a marketing page, an app shell, a form, a data view, an editor, a state screen. This governs density, motion, and component choice more than anything else. A marketing page can teach through scroll; a tool earns trust by getting out of the way.
2. **What the argument or task is** — for a page, the beats it needs; for a screen, the one job it does.
3. **Shape** — the page shape or shell frame that carries it, picked by name.
4. **Layout, type, color** — the token layer. Color last of the three, because it is chosen against real type and real surfaces.
5. **Spacing, depth, hierarchy** — verified by zooming out, not by reading the values.
6. **Motion** — only where it earns its place.
7. **The craft pass** — radius, optical alignment, states, keyboard access, overflow, locale, and the words themselves.

Not every piece of work touches all seven. A single component starts at step 4.

## Audit Checklist

When reviewing existing frontend code, check these areas.
Load the relevant reference file for detailed criteria on any failing item.

### Composition
- [ ] Each section is mostly something to look at, with text as caption — not prose with a decorative icon
- [ ] The page shape is a named, deliberate choice, not the reflexive hero → three cards → CTA → footer
- [ ] No two sections on the page use the same archetype
- [ ] Reading top to bottom, each section has a job in the argument; at least four distinct beats
- [ ] Section padding is weighted by role, not flattened to one value
- [ ] One section-separation mechanism used consistently at every boundary
- [ ] Two-column sections have a deliberate balance treatment, not a column trailing into empty space
- [ ] One intentional rule-break exists; the page is not uniformly safe
- [ ] No hand-built fake browser, phone, or IDE chrome
- [ ] Every metric, quote, and logo is real, or honestly marked as a placeholder

### Color & Theming
- [ ] Colors defined as CSS variables or design tokens, not hardcoded
- [ ] Using HSL or OKLCH format for easy palette manipulation
- [ ] Limited palette: primary + secondary + accent + neutrals + semantic states
- [ ] Contrast checked for every pairing the build introduced, not only body text on background
- [ ] Button label against its fill verified separately; a fill that passes as a swatch can fail as a button
- [ ] No dark panel left with dark text; lightness inversion carries to nested children
- [ ] Accent stays an accent, roughly 5% of a viewport or less
- [ ] Dark mode support (if applicable) uses proper shade inversion

### Typography & Spacing
- [ ] Consistent type scale (not arbitrary font sizes)
- [ ] Single font family (or deliberate pairing with clear roles); at most three families on a page
- [ ] Line height inversely proportional to font size, with 1.0 as the floor on display type
- [ ] No italic headings; emphasis carried by weight, color, or an underline
- [ ] Body copy is not set in a monospace face
- [ ] Long-form text capped at 60-75 characters per line
- [ ] Nothing below 18px set lighter than weight 400
- [ ] Anything wrapping to three or more lines has line-height 1.4 or more
- [ ] `text-wrap: balance` on headings, `pretty` on descriptions
- [ ] Truncated content stays reachable somewhere
- [ ] No center-aligned paragraphs (only short headings/labels)
- [ ] All spacing values divisible by 4 (in px) or clean rem values
- [ ] Gestalt proximity: related items close, unrelated items far

### Layout & Responsiveness
- [ ] Flexbox as default, Grid only for structured/uniform layouts
- [ ] Dynamic sizing (viewport units, `clamp()`, flex ratios) over hardcoded pixels
- [ ] Responsive behavior planned and tested, not just "it doesn't break"
- [ ] Hover effects wrapped in `@media (hover: hover)` for touch safety
- [ ] Images served responsively with `<picture>` or `srcset` where appropriate

### Depth & Hierarchy
- [ ] Visual hierarchy clear when zoomed out (primary > secondary > tertiary)
- [ ] Shadow system consistent (not random box-shadow values per element)
- [ ] Secondary content de-emphasized rather than primary over-emphasized
- [ ] Interactive elements have clear hover/focus/active states

### Animation
- [ ] Every animation passes the frequency gate — nothing animates on a high-frequency or keyboard-initiated action
- [ ] No `ease-in` on UI; exits are `ease-out` and shorter than enters
- [ ] No `transition: all` — exact properties named
- [ ] Nothing enters from `scale(0)`; entrances start at `0.9`-`0.95` with opacity
- [ ] Anchored surfaces (popovers, dropdowns, tooltips) scale from their trigger, not center
- [ ] Rapidly re-triggerable elements use transitions, not keyframes
- [ ] Every animated state change also has a static cue (color, icon, label)
- [ ] Motion respects `prefers-reduced-motion` media query
- [ ] Hover animations wrapped in `@media (hover: hover)`
- [ ] Theme switching does not smear (transitions suppressed for the swap)

### Surface Craft
- [ ] Nested rounded elements are concentric (`outer = inner + padding`)
- [ ] Icons optically centered, not just geometrically
- [ ] Borders used for structure, shadows for depth — not interchangeably
- [ ] Images carry a pure black/white 10% outline, never a tinted one
- [ ] Icon stroke weight matches adjacent text weight; one icon library per surface
- [ ] Icons still legible at their smallest render size

### Internationalization & Device
- [ ] Direction-dependent CSS uses logical properties, not `left`/`right`
- [ ] No fixed widths or heights on text containers (strings grow when translated)
- [ ] Edge-pinned elements account for `env(safe-area-inset-*)`
- [ ] Breakpoints chosen from where content breaks, not device presets
- [ ] Off-screen or collapsed content has a visible affordance
- [ ] Layout survives 200% zoom with no horizontal page scroll

### UX & Accessibility
- [ ] Core user flow achievable in minimum clicks
- [ ] Native HTML elements used where appropriate (`dialog`, `details`, `datalist`)
- [ ] Images optimized (WebP, appropriate sizing) with explicit dimensions
- [ ] SVGs used for icons instead of raster images
- [ ] Every interactive element reachable and operable from the keyboard, with a visible focus ring that never fades in
- [ ] Icon-only buttons and every form control carry an accessible name
- [ ] Paste is never blocked; inputs carry `autocomplete` and the right `type`
- [ ] Filters, tabs, and pagination are reflected in the URL
- [ ] Dates and numbers formatted through the platform's locale APIs, never hardcoded
- [ ] Text containers handle overflow; copy tested short, long, and translated
- [ ] Custom widgets implement their role's full keyboard model; no positive `tabindex`
- [ ] Modals trap focus, return it to the trigger on close, and close on Escape
- [ ] Decorative overlays carry `pointer-events: none` so they don't swallow clicks
- [ ] Hit areas meet the 24px floor, and extended hit areas never overlap
- [ ] Submit is never disabled until valid; the first invalid field takes focus
- [ ] Alt text chosen by purpose; a missing `alt` is worse than an empty one
- [ ] Layout reflows at 320px equivalent with vertical scrolling alone

### Copy
- [ ] Button labels start with a verb and name the outcome
- [ ] Confirmation buttons repeat the consequence, so the dialog is answerable without reading the body
- [ ] Link text makes sense out of context; no bare "Learn more" appearing twice
- [ ] One capitalization policy per element type
- [ ] Errors state the fix, sit beside the field that failed, and carry no blame
- [ ] Empty states say what goes here and offer one next action
- [ ] Placeholders are examples, never the only label
- [ ] Toggles are labeled for their on state
- [ ] No sentence assembled by concatenating fragments around a variable

### Interaction States
- [ ] Empty states designed (not blank screens) with clear next-action guidance
- [ ] Loading states use skeleton screens or spinners, not blank areas
- [ ] Error states are informative and offer recovery actions
- [ ] Destructive actions have confirmation dialogs
- [ ] Post-action feedback provided (toasts, button state changes, completion indicators)
- [ ] Interaction pattern choices appropriate (popover vs modal vs new page)
- [ ] Icon library consistent (one set, with labels/tooltips for non-obvious icons)
- [ ] Action terminology consistent across all screens

## Before You Finish

Score the work 1-5 on each of six axes before handing it back. Anything below 3 gets a revision pass — catching a weakness here is far cheaper than catching it in a full review. Two passes is normal. A third usually means the brief is underspecified, not the design.

| Axis | What you are scoring |
|---|---|
| **Show-don't-tell** | Is each section mostly something to look at, or mostly prose with a decorative icon? Score this first. |
| **Philosophy** | Is there a clear reason it looks like *this*, or is it just a competent layout? |
| **Hierarchy** | Can someone tell in two seconds what is primary, secondary, tertiary? |
| **Specificity** | Does this look like *this* product, or like a generic page in different colors? |
| **Restraint** | Has everything that is not earning its place been removed? |
| **Variety** | Does this share a structural fingerprint with the last thing built? A palette swap is not variety. |

## Audit Output

An audit is not a list of ticked boxes. It ends with a verdict and an honest statement of what was not checked.

**Severity.** `HIGH` breaks an interaction, blocks content or an action at a supported viewport, or leaves a state change visible only while an animation runs. `MEDIUM` is a visible inconsistency in layout, surfaces, or motion, or harms hierarchy and reading order. `LOW` is isolated polish.

**Verification.** Say what you actually checked. Without a browser, that means: every state the component defines (hover, focus, active, disabled, loading, empty), plus durations, easings, and logical-property usage read from the code. With a browser: walk each state, check every supported width, 200% zoom, and the RTL mirror, and replay motion at 10% speed. **Report anything you could not run as `Not verified`.**

**Format.** Group findings under the principle each violates, ordered by severity, one row per root cause listing every location it appears in.

| Severity | Location | Before | After | Why |
|---|---|---|---|---|

`Location` is `path/to/file:line`. `Why` names the principle and the user impact, not just the rule.

End with **Block** when any `HIGH` remains, **Approve** otherwise, leaving the rest in the table as work to do. Never approve coverage you did not inspect. With nothing to report, say so explicitly and still report what was verified.

## Anti-Patterns

| Avoid | Do Instead |
|-------|------------|
| Hardcoded hex colors scattered throughout | Define color tokens as CSS variables |
| Random spacing values (13px, 17px, 22px) | Use multiples of 4: 12px, 16px, 24px |
| Multiple font families without clear purpose | One family, vary weight and size |
| Pure white (#fff) text on dark backgrounds | Slightly off-white (95-97% lightness) |
| Center-aligned body text | Left-align paragraphs, center only short headings |
| `position: absolute` for layout | Flexbox or Grid for layout, absolute only for overlays |
| Uniform shadows on every element | 3 shadow levels (sm, md, lg) applied by context |
| Animations on everything | Animate only what aids comprehension or feedback |
| Custom JS for modals, accordions, tooltips | Native `<dialog>`, `<details>`, `<datalist>` first |
| Serving full-size images to mobile | `<picture>` + `<source>` with media queries |
| Ignoring touch devices | `@media (hover: hover)` for hover-dependent interactions |
| `transition: all` | Name the exact properties that change |
| Same radius on a container and its nested child | `outer = inner + padding` |
| Animating a keyboard shortcut or other 100×/day action | No animation at all |
| `ease-in` on an entering or exiting element | `ease-out`; exits also get a shorter duration |
| Entering from `scale(0)` | `scale(0.95)` with opacity — nothing appears from nothing |
| Popover scaling from its own center | `transform-origin` at the trigger (modals stay centered) |
| `margin-left` / `padding-right` in a localizable layout | `margin-inline-start` / `padding-inline-end` |
| Fixed-width button sized to its English label | `padding-inline` and let the label define the width |
| Content hidden with no cue that it exists | Peek the next item 16-32px, or add a labeled disclosure control |
| Motion as the only signal a state changed | Pair it with a color, icon, or label change |
| A section explaining a benefit in two sentences under a heading | Show the benefit: a mockup, a chart, a comparison, a numbered visual flow |
| Hero → three feature cards → testimonial → CTA → footer | Pick a page shape by name and say which one and why |
| A hero carrying feature chips, metric rails, and floating badges | One promise, one subhead, one action, one visual; the rest goes below the fold |
| Every section padded to the same value | Weight the padding by the section's role in the page |
| An italic heading, or emphasis by italicizing one word in it | Emphasis by weight, color, or an underline |
| A hand-drawn fake browser bar or phone frame | A real screenshot in a plain frame, or no chrome |
| Invented metrics or testimonials filling a proof section | Real evidence, an honest placeholder, or a shape that doesn't need them |
| Contrast checked once, on body text over background | Check every pairing the build introduces, button labels especially |
| A `<div>` with a click handler | A real `<button>` or link, keyboard-operable, with an accessible name |
| Filter and tab state held only in component state | Reflect it in the URL so the view can be shared and restored |
| A decorative glow or scrim over interactive content | `pointer-events: none` on every decorative layer |
| Submit disabled until the form validates | Keep it enabled; validate on submit and focus the first error |
| A tooltip on a natively disabled control | Visible text beside it, or `aria-disabled` so it stays focusable |
| A red border as the only error signal | Inline text beside the field, plus `aria-invalid` |
| `--color-text-primary` beside `--color-primary` | Reserve `accent` for the brand; `primary` means most prominent of its group |
| A raw ramp value like `--blue-500` used in a component | Point a semantic token at it |
| Dark mode built by mechanically inverting the light palette | Invert as a start, then cut chroma, widen the dark end, recheck every pair |
| A gradient that goes gray in the middle | Interpolate in a polar space, or add a third stop |
| "OK" or "Yes" on a consequential action | Name the consequence: "Delete project" |
| Guidance that only exists in the empty state | Put it where it survives content existing |
| Over-designing | The simplest solution that works is the best solution |
| Designing only the happy path | Map user flows first; design for empty, error, loading, and unauthorized states |
| Inconsistent terminology ("Delete" vs "Remove") | Standardize action labels and button names project-wide |
| Mixing icon styles (fill + outline + varying weights) | Use one icon library consistently (Lucide, Phosphor, etc.) |
| Stacking multiple effects (gradient + shadow + glow) | Pick one subtle effect or none; less is almost always better |
| No feedback after user actions | Gray out buttons on click, show loading indicators, use toasts for confirmation |
| Over-designed charts (rounded bars, missing axes) | Simple charts with clear axes, labels, and hover states showing values |
| No empty state design | Design intentional empty states with guidance on what to do next |
| Using Lorem Ipsum in prototypes | Use real or realistic content to catch layout and flow issues early |

## Scope of This Skill

This is a knowledge base about finished interfaces: what they should look like, how they should behave, and why. It is deliberately not a process.

It does not cover how to run a design project, how to produce mockups or variant pickers, how to organize component files, which framework to pick, or what to write into project documentation. For frontend code architecture — rendering strategies, state management, file organization — see the `architecting-frontend` skill if available.
