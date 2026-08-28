---
summary: Color formats, ramp construction, brand-color placement, two-tier tokens and naming, dark mode, contrast measurement and repair, gamut, gradients, and color meaning across cultures
read_when: building or auditing a color palette, naming color tokens, implementing dark mode, measuring or fixing contrast, building a gradient, or deciding what a color means in the interface
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

### Placing a Brand Color

A brand color arrives as one value. Two decisions come before any ramp exists.

**Which step does it occupy?** A brand color meant for buttons and links belongs on the solid-fill step, so that step renders the actual brand color rather than an approximation.

**Is it pinned or snapped?** Pin a contractually fixed brand color: it stays exact and the ramp builds outward from it, at the cost of that one step spacing slightly unevenly. Otherwise snap it onto the ramp so every step spaces evenly, which looks better almost always and nobody notices without a swatch held to the screen.

A brand color that fails contrast behind white text is still the brand color — it just is not the solid-fill step. Put it where it lands and use a darker step for interactive fills. **Never quietly darken the brand.**

### What a Correct Ramp Looks Like

Six properties, checkable against any output in any notation:

- **Steps are evenly spaced in *perceived* lightness**, not in whatever the format calls lightness. HSL's lightness is not perceptual, so evenly spaced HSL values bunch at one end.
- **Hue is constant end to end.** A wandering hue reads as two colors blended and will not sit correctly against a neutral built on a different hue.
- **Vividness peaks in the middle and falls off at both ends.** Holding full chroma into the extremes gives a lightest step that glows and a darkest one like ink spilled on the brand.
- **Steps sit denser at the light end.** Light backgrounds need finer distinctions than dark ones. If the two palest steps stop reading as two different surfaces, the spacing is wrong.
- **No two adjacent steps are indistinguishable.** If they are, the ramp has more steps than the design has decisions. Drop one.
- **Both ends stop short of pure black and white**, which cannot carry hue at all.

**Across several hues, match perceived lightness exactly but vividness only relatively.** Hues do not share a maximum chroma — a saturated yellow and a saturated blue are not equally far from gray, and no format makes them so. Set each ramp to the same *proportion* of what its own hue reaches. Copy a saturation number across hues and one ramp comes out washed out; yellows and cyans are the usual casualties, which is how a warning color ends up looking weak beside the danger one.

Use a color library rather than eyeballing this. Anything that converts notations and interpolates perceptually will do.

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

Inverting the lightness — subtracting from 1.0 — gets you the starting point:

```css
/* Light mode — inverted from dark */
--bg-base: oklch(1.00 0 0);     /* white */
--bg-raised: oklch(0.95 0 0);   /* light gray */
--bg-elevated: oklch(0.92 0 0); /* slightly darker */
--bg-overlay: oklch(0.90 0 0);  /* darker still */
```

In light mode, darker shades = elevated. The naming convention flips: what was "raised" in dark mode is still "raised" in light mode, but the lightness direction reverses.

**A dark palette is not the light one reversed.** The mirror is where you start, not where you stop. Three things need hand-tuning afterwards:

- **Vividness comes down.** A color that reads as confident on white reads as neon on near-black. The accent usually wants a step or two less chroma in dark mode.
- **The dark end needs more separation.** Steps that are clearly distinct as pale backgrounds collapse into each other as dark surfaces.
- **Contrast does not survive the mirror.** Contrast is not symmetric, so a pair that passes in light mode can fail reversed. Recheck every foreground against its real background in both appearances.

### Pick One Switching Mechanism

Mixing them is the common failure: a media query setting some tokens and a class setting others gives a half-themed interface the moment someone overrides their system preference.

- **`prefers-color-scheme` alone** is correct when there is no theme toggle. Nothing to persist, nothing to hydrate.
- **A class or data attribute** becomes necessary as soon as users can override the system setting. The media query then only sets the initial value.
- **`light-dark()`** collapses both values into one declaration and is the least code where the project also sets `color-scheme`. It reads that property rather than a class, so a class-based toggle must set `color-scheme` too.

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

In UI elements — buttons, cards, repeated components — stick to variations of a single hue. Multi-color gradients look amateurish there. Gradients spanning analogous hues, within about 30 degrees, can work for a hero or an accent surface.

```css
/* Good: single-hue gradient */
background: linear-gradient(135deg, hsl(220 80% 50%), hsl(220 80% 35%));
```

### Gradient Interpolation

When a gradient *is* wanted, the interpolation space is a look, not a correctness setting. The difference shows up in the middle.

```css
/* sRGB, the default: the midpoint darkens and mutes */
background: linear-gradient(#3b82f6, #ec4899);

/* oklab: even brightness across the transition. The best default */
background: linear-gradient(in oklab, #3b82f6, #ec4899);

/* oklch: travels around the hue wheel, staying vivid throughout */
background: linear-gradient(in oklch, #3b82f6, #ec4899);
```

`oklab` and sRGB are **rectangular** — they interpolate in a straight line through the color space. `oklch` is **polar** — it interpolates the hue angle, arcing around the wheel through every hue between the stops. That is why it stays saturated, and also why it can produce hues nobody asked for: blue to pink routes through purple, which is either the look or a surprise.

**The gray dead zone in the middle of a two-hue gradient is a rectangular-space problem.** Two hues on opposite sides of the wheel sit either side of the neutral axis, and a straight line between them passes near gray. Either switch to a polar space, which routes around the axis, or add a third stop and keep the space you have.

Two more traps. **Banding** shows on large areas when two stops sit close in contrast — widen the contrast, shrink the area, or overlay subtle noise. And **keep text off gradients** where you can: contrast varies continuously across one, so a single measurement does not describe it. Where text must sit on a gradient, measure the worst region or put a scrim behind it.

---

## Two Token Tiers

**Primitives** name a value: `--blue-500`, `--neutral-200`. A primitive describes what a color *is*, so it never changes meaning between themes, and it is never applied directly in a component.

**Semantics** name a job: `--color-text-secondary`, `--color-border-subtle`. They point at a primitive, and they are the only tier components reference.

That seam is what makes theming possible. Dark mode, a white-label theme, and an increased-contrast variant all repoint the semantic tier and leave every component untouched. A codebase applying `--blue-500` directly in components has no theming seam at all, and adding one later means auditing every usage to work out which meant "the accent" and which just wanted blue.

Add a third component-level tier only where a component genuinely diverges from the system. One such token is a documented exception; twenty mean the semantic tier is missing roles.

### The Role Inventory

A system is complete when every role below has a token. Build against this list rather than adding tokens as components demand them, or the palette ends up shaped like whichever screen was built first.

| Group | Roles |
|---|---|
| Surfaces | page background, surface, raised (menus, popovers), sunken (inputs, wells), overlay scrim |
| Text | primary, secondary, disabled, inverse, on-accent |
| Borders | subtle, default, strong, focus ring, separator |
| Accent | subtle background, border, solid, solid hover, text |
| Status | per status shipped: subtle background, border, solid, text |

Separator and border are separate roles even when they share a value today. A separator divides content; a border encloses a control. They diverge the first time someone restyles inputs.

### Naming Grammar

One shape, never deviated from: `--color-{role}-{variant}-{state}`. Pick one word per concept and use only that word — a reader who has seen `--color-text-primary` must be able to guess `--color-text-disabled` without looking.

| Concept | Pick one | Never mix in |
|---|---|---|
| Foreground | `text` | `fg`, `foreground`, `content`, `ink` |
| Background | `bg` | `background`, `fill` |
| Edge | `border` | `stroke`, `outline`, `line` |
| Brand color | `accent` | `primary`, `brand`, `theme` used interchangeably |

**Reserve `primary` for exactly one meaning.** `--color-text-primary` for body text sitting beside `--color-primary` for the brand is the most common naming collision there is, and it makes every `primary` token ambiguous until you open its definition. Use `accent` for the brand and let `primary` mean "the most prominent of its group".

| Bad name | Problem |
|---|---|
| `--color-blue-button` | Appearance at the semantic tier; lies the moment the brand changes |
| `--color-sidebar-gray` | Named for where it was used first; the second usage makes it nonsense |
| `--color-light-gray` | Lies in dark mode, where it is the dark one |
| `--color-text-2` | Numbered semantics carry no meaning; nobody can guess what 3 would be |
| `--blue-500` in a component | Skips the semantic tier and removes the theming seam |

### Use a Token Only in Its Role

Never borrow a token because its value happens to be right today. A separator used as a text color works until borders get lighter, and then the text goes with them. If a role has no token, add the token.

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

## Measuring Contrast

**Measure the foreground against the background it actually renders on**, which is the nearest ancestor that paints one. Measuring against the page background when the element sits on a card gives the wrong answer.

Never report a contrast value you did not measure, and never estimate a color you could compute. Color is one of the few interface concerns with an exact answer.

### Check Every Pairing the Build Introduces

Body text on background is the pairing everyone remembers to check, and checking only that is how illegible interfaces ship. A palette is a contract about which colors may touch, not a set of hexes that passed once. Every pairing the build actually introduces — a badge fill with its label, a disabled state, a hover, a border that carries state — needs to clear its floor: 4.5:1 for text, 3:1 for a UI affordance. A purely decorative hairline is exempt; a border that is the only thing conveying state is not.

**The three failures that actually ship:**

1. **Button label against button fill.** This is a downstream consequence of the palette rather than a value in it, which is why it gets missed. A color that looks fine as a swatch routinely lands at 2.5-3.5:1 with white label text. When a label and its fill sit within about 5% lightness of each other, that is the black-on-black bug — the on-fill color was never chosen.
2. **A dark panel left with dark text.** Any surface below about 50% lightness must swap its text color in the same rule, and nested children must inherit it. Sections inverted for emphasis are where this hides.
3. **An accent used as a text-bearing fill with no verified on-accent color.** The accent's normal job is links, highlights, and small emphasis, checked only at the 3:1 UI floor. The moment it becomes a solid fill carrying a label, it needs the full text check.

Do not assume the brand color's own text color works as a button label. It usually does not — white is the safe default on a saturated primary far more often than the palette's own ink is.

### Thresholds

WCAG 2 has the legal standing and is the gate for any formal conformance claim.

| Content | AA | AAA |
|---|---|---|
| Normal text (under 24px, or 18.5px bold) | 4.5:1 | 7:1 |
| Large text (24px+, or 18.5px+ bold) | 3:1 | 4.5:1 |
| UI components and graphical objects | 3:1 | — |

APCA models *perceived* contrast more accurately and is the better guide for design decisions above that gate. Its Lc values are signed — positive is dark-on-light, negative is light-on-dark — so compare the absolute value.

| Content | Minimum | Preferred |
|---|---|---|
| Body text | Lc 75 | Lc 90 |
| Non-body text (labels, headlines) | Lc 60 | Lc 75 |
| Large text (36px+) | Lc 45 | Lc 60 |
| UI components | Lc 30 | — |

### Fixing a Failing Pair

**Change lightness, not hue.** Lightness is the channel contrast responds to; hue and saturation move the measured value far less, so fixing contrast by changing hue is wasted effort. Holding hue fixed is also what stops a contrast fix becoming a palette change.

Two constraints:

- **A mid-lightness background caps what is achievable.** On a background near 75% perceived lightness, even pure black text reaches only about Lc 60. Body text needs a background near one extreme, so the *background* is the thing that has to change.
- **Pushing lightness can push a color out of gamut.** Reduce chroma as needed to keep it renderable.

**Work in this order rather than re-running the same value:**

1. Reuse a pairing already known legal for that purpose.
2. Nudge lightness within the same hue family.
3. If nudging would break the color's intended role, fall back to a neutral already in the palette for that one pairing.
4. If a hard external constraint makes it impossible — a fixed brand hex that cannot satisfy the floor for its intended use — surface the conflict rather than shipping the failure or silently substituting something else.

Always remeasure after changing a value. Never assume a fix landed.

**Rough guide for a first pass, then verify by measuring.** The crossover between dark and light text sits around 73% perceived background lightness — higher than intuition suggests. Between roughly 60% and 73% the background already looks light, yet white text still measures meaningfully better than black.

### What Always Needs Checking

- **Every pair, in both appearances.** The palettes are not mirror images, and contrast is polarity-aware, so a pair passing in light mode can fail in dark.
- **Translucent surfaces.** A color on a blurred header shifts with whatever scrolls behind it. Test against the lightest and darkest content it can sit over, or make the surface opaque enough that the shift cannot break the pair.
- **Computed colors.** `color-mix()`, relative color syntax, and opacity modifiers all resolve at render time. A token carrying alpha cannot be contrast-checked against a static background at all, because what it renders depends on what sits behind it. Use solid tokens for anything with text on it.
- **Text over images.** There is no single background color. Measure the worst region, or guarantee one with a scrim.

### Increased Contrast

Users who enable it expect visibly stronger differentiation, not the default palette. Widen the foreground-to-background gap by at least 15 points of perceived lightness, then remeasure — widening without remeasuring is not fixing it.

```css
@media (prefers-contrast: more) {
  :root { --primary: oklch(0.42 0.20 250); }
}
```

---

## Gamut

Every sRGB color exists in Display P3, but not the reverse. P3 covers roughly 50% more colors, which only matters at the most saturated values — at 60% of maximum vividness the two look identical.

A color more vivid than the display can render gets **clipped, and clipping is not graceful**: it flattens neighbouring ramp steps into one rendered color, so the top of a ramp can lose its distinctions on an sRGB screen. Maximum vividness varies by hue, so a clipping ramp clips at some steps and not others.

Generate ramps against sRGB unless the product is display-restricted, and add P3 as an enhancement. Order matters — the sRGB value comes first so every display gets something.

```css
.accent { background: #3b82f6; }

@media (color-gamut: p3) {
  .accent { background: oklch(0.62 0.24 259); }
}
```

A P3 color with no sRGB fallback does not degrade. It fails.

---

## One Color, One Meaning

Use a color for one purpose across the whole interface, treating anything within about 15 degrees of hue as the same color — people read a near-miss as a slightly different shade, not as a different color.

The rule runs both ways. If the accent means interactive, that hue on static text tells people to click something that is not clickable, and an interactive element rendered neutral misleads just as badly.

### Accent Discipline

An accent covering more than roughly 5% of a viewport by area has stopped being an accent. Large accent headings, full-bleed accent bands, and solid accent panels all count. Emphasis works by scarcity.

**Tint neutrals toward the anchor hue** rather than using pure zero-chroma grey, which reads as flat and disconnected from the palette. The exception is a deliberately monochrome or technical product, where zero-chroma neutrals are the point.

**Keep every status hue distinct from the accent.** If the brand is red, the danger ramp cannot also be red, or the destructive and primary actions are the same button.

**One filled action per view.** When filled color encodes primary emphasis, one action gets it and its peers stay neutral. Put the color on the *background*, not the label: a filled button reads as primary across the room, while accent-colored text on a neutral button reads as a link. Several colored backgrounds are fine when they encode distinct states or categories rather than competing as peers.

Selected states may carry the accent on the glyph and label. An active tab is state, not emphasis.

Color is never the only carrier of meaning. Pair it with an icon, a label, or a shape.

### Color Across Cultures

Where a color is load-bearing in finance, status, or alerts, verify the meaning holds in every locale shipped to.

| Color | Common Western reading | Elsewhere |
|---|---|---|
| Red | Danger, loss | Luck and prosperity; **gains** in Chinese financial interfaces |
| Green | Success, gains | **Losses** in Chinese financial interfaces |
| White | Purity, cleanliness | Mourning in parts of East Asia |

Stock tickers are the classic case, showing gains in green for English locales and red for Chinese ones. Where the product ships to those markets, make gain and loss per-locale tokens rather than hardcoded values.

---

## Auditing an Existing Palette

Most codebases hold several times more colors than the design has decisions. Before restructuring anything, inventory it: collect every literal (including SVG fills, chart configs, and email templates, where colors hide), sort by perceived lightness within each hue family so duplicates surface as near-identical neighbors, collapse anything closer than about one ramp step — keeping the most-used and retiring the rest, never averaging them — and assign each survivor a role. A color matching no role is either a missing token or a mistake.

Report the inventory before changing anything. Consolidating a palette changes rendered output on screens nobody asked you to touch.

---

## Quick Reference

| Decision | Technique |
|---|---|
| Pick a color format | OKLCH for Tailwind v4+; HSL otherwise |
| Generate shades | Increment lightness by 0.1 (OKLCH) or 10% (HSL), keep chroma/saturation fixed |
| Add accent colors | Shift hue +/- 60 degrees from primary |
| Dark mode backgrounds | 0%, 5%, 10% lightness, zero chroma |
| Light mode from dark | Invert lightness as a STARTING point, then retune chroma and recheck |
| Avoid eye strain | Cap text at 90% lightness (dark mode), 15% (light mode) |
| Remove unnecessary borders | If surfaces differ by >= 0.05 lightness, border is optional |
| Name variables | Two tiers: primitives by hue, semantics by role. Components use semantics only |
| Fix a failing pair | Change lightness, not hue; then remeasure |
| Accent footprint | ~5% of a viewport or less |
