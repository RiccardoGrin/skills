---
summary: Type scales and roles, weight floors, line height, measure, wrapping and truncation, letter spacing, underlines, rendering details, non-Latin scripts, spacing systems, grouping ratios, card padding floors, and the divisible-by-4 rule
read_when: Setting font sizes or a type scale, setting line height or letter spacing, capping line length, styling links, truncating text, typesetting a non-Latin script, building spacing systems, or applying consistent padding and margin
---

# Typography & Spacing

## Typography

### Font Family

Stick to one font family. A single well-chosen font with weight variation looks more professional than a multi-font hodgepodge. System font stacks are fast and familiar:

```css
--font-sans: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
--font-mono: 'SF Mono', 'Cascadia Code', 'Fira Code', monospace;
```

If using a custom font, load only the weights you need (typically 400, 500, 600, 700).

### Type Scale

Build a type scale as CSS variables. Use a ratio-based scale (1.25 "major third" or 1.2 "minor third" are safe defaults). Use a TypeScale generator to pick exact values.

```css
:root {
  --text-xs:   0.75rem;   /* 12px */
  --text-sm:   0.875rem;  /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg:   1.125rem;  /* 18px */
  --text-xl:   1.25rem;   /* 20px */
  --text-2xl:  1.5rem;    /* 24px */
  --text-3xl:  2rem;      /* 32px */
  --text-4xl:  2.5rem;    /* 40px */
  --text-5xl:  3rem;      /* 48px */
}
```

Every font size in your project should reference one of these variables. If you find yourself writing a one-off `font-size: 15px`, that's a smell.

### A Role-Based Scale Is One Decision Instead of Three

Pairing each role with its own line-height and weight means picking a role settles all three at once, and emphasis within a role is one weight step rather than a size change.

| Role | Size | Line-height | Weight |
|---|---|---|---|
| Display | 36px | 1.1 | 600 |
| Title | 24px | 1.2 | 600 |
| Heading | 18px | 1.3 | 600 |
| Body | 16px | 1.5 | 400 |
| Caption | 13px | 1.4 | 400 |

Naming matters more than it looks. `text-sm` tells you the size but not the use; `text-body-sm` carries both, and the usage rule survives other people.

### Weight Floors

**Below 18px, stay at weight 400 or heavier.** Thin, light, and ultralight strokes (100-300) disappear at text sizes and on low-DPI screens. They are display-only, reserved for 28px and up, and even there they need checking against the background.

Browsers **synthesize** a weight or style the active family does not provide, slanting or smearing the real face into something the designer never drew. Load the faces the design actually uses. `font-synthesis: none` turns synthesis off, but it erases emphasis rather than reporting it, so set it only after confirming every required bold and italic form stays distinct across the whole fallback stack.

### Headings

Headings should be the largest elements on the page. If a heading doesn't look like the most prominent element in its section, either increase its size or reduce the size of surrounding content.

Use font weight to reinforce the hierarchy:
- `h1`: `--text-4xl` or `--text-5xl`, weight 700-800
- `h2`: `--text-2xl` or `--text-3xl`, weight 600-700
- `h3`: `--text-xl`, weight 600
- Body: `--text-base`, weight 400

### Line Height

Line height is inversely proportional to font size. Large text needs tight leading; small text needs loose leading for readability.

```css
:root {
  --leading-tight:  1.1;   /* headings, display text */
  --leading-snug:   1.25;  /* subheadings, large text */
  --leading-normal: 1.5;   /* body text */
  --leading-loose:  1.6;   /* small text, captions */
}

h1, h2 { line-height: var(--leading-tight); }
h3, h4 { line-height: var(--leading-snug); }
p, li   { line-height: var(--leading-normal); }
small   { line-height: var(--leading-loose); }
```

Generous line height on body text doubles as built-in vertical spacing between lines. This is free breathing room you don't have to add with margin.

**Tight leading is for short text.** Anything wrapping to three or more lines needs at least 1.4, even inside a height-constrained row. A card description set at heading leading is the common version of this — it wraps to three lines and reads as cramped. A tightly leaded paragraph is harder to read than a taller row is to fit.

Prefer unitless line-height values so they scale with the font size. A fixed `24px` does not.

### Cap the Measure

Long lines make it hard for the eye to find the start of the next one. **Cap long-form text at 60-75 characters per line.**

Any unit works. `65ch` measures characters directly, and a rem or pixel cap is just as good — at a 16px body size, 60-75 characters lands roughly between 560px and 680px depending on the font. What matters is that a cap exists and the line length sits in range. Recheck it if the body size changes.

Justified text stretches word spaces until both edges line up. It works in specific editorial layouts and nowhere else in an interface.

### Type Choices That Read as Machine-Made

Four habits that signal a generated interface regardless of how good the scale is:

- **Italic headings.** An all-italic display face, or an upright heading with one word italicized for emphasis, is among the most reliable tells. Headings are roman. Carry emphasis with weight, color, or a drawn underline. Italic survives only as emphasis inside running body copy.
- **Body copy in a monospace face.** It reads as a developer template. Reserve mono for code, data, timestamps, and short technical labels, even on a deliberately technical product.
- **More than three font families on a page.** Display, body, and at most one outlier used in no more than two slots. The same family at different weights counts once.
- **Display line-height below 1.0.** Tighten as size grows, but 1.0 is the floor. Below it, descenders and punctuation touch the line beneath. Verify this visually at the real weight and size — a value that is safe at 400 weight and 3rem will clip at 800 weight and 6rem.

### Letter Spacing Is Size-Specific

Tracking is not one value applied to the whole project. Letterforms read too far apart as they grow and too crowded as they shrink, so the correction runs in opposite directions at the two ends of the scale.

- **Large display text wants negative tracking.** Around `-0.02em` at heading sizes, tightening further as size increases.
- **Body text sits near `0`.**
- **Small text and uppercase labels want slightly positive tracking**, roughly `0.02em` to `0.05em`, for legibility.

A single fixed `letter-spacing` across the project is wrong somewhere by definition.

```css
:root {
  --tracking-tight:  -0.02em;   /* display and headings */
  --tracking-normal:  0;        /* body */
  --tracking-wide:    0.05em;   /* small caps, badges, overline labels */
}

.display { font-size: clamp(2rem, 5vw, 4rem); line-height: 1.05; letter-spacing: var(--tracking-tight); }
.label   { font-size: var(--text-xs); text-transform: uppercase; letter-spacing: var(--tracking-wide); }
```

Build hierarchy from **weight, size, and leading as a set**, not size alone. Weight adds presence without taking more space.

Where a variable font is available, `font-optical-sizing: auto` lets the face adjust its own shapes with size, which is the same discipline handled by the type designer.

### Respect the User's Text Size

Users can set a larger base font size at the OS or browser level. Layouts must scale *with* the text rather than break around it.

- Size spacing in `rem` or `em`, not fixed `px`, so padding grows with the type.
- Never set a fixed height on a container whose content is text.
- Test at 200% zoom. Everything must remain reachable and readable, with no horizontal page scroll.

### Text Alignment

Left-align paragraphs. Always. Center-aligned body text is hard to read because the eye has to find a new starting position on every line.

Center alignment is fine for:
- Short headings (1-2 lines max)
- Labels and badges
- Hero section taglines
- Single-line captions

```css
/* Good */
.hero-title { text-align: center; }
p, li, blockquote { text-align: left; }

/* Bad — never do this */
.article-body p { text-align: center; }
```

### Wrapping

Four declarations, four jobs:

- `text-wrap: balance` distributes text evenly across lines. **Use it on headings** so a two-line heading is not lopsided.
- `text-wrap: pretty` stops a single short word landing alone on the final line. **Use it on descriptions.**
- `overflow-wrap: break-word` where a long word, URL, or ID could escape its container.
- `white-space: nowrap` on labels and badges where a line break looks broken.

Skip `balance` and `pretty` in long-form text. Browsers ignore `balance` past a few lines anyway, and evening out a whole paragraph wastes space without helping.

### Truncation

A single line truncates with `text-overflow: ellipsis`, which needs `overflow: hidden` and `white-space: nowrap`. Several lines use `line-clamp`. A flex child needs `min-width: 0` or neither works.

Truncation hides content. **Where the missing text matters, keep the full value reachable** in a tooltip or an expanded view.

### Trim the Box, Not the Text

Fonts reserve space above and below the letters, which is why text sits slightly too low in a button or badge and why vertical centering never quite lands. `text-box` trims it:

```css
.badge   { text-box: trim-both cap alphabetic; }  /* top and bottom */
.heading { text-box: trim-start cap; }            /* top only */
```

Chromium and Safari support it, Firefox does not yet. Treat it as progressive enhancement — unsupported browsers keep the default leading, which is what you have today anyway.

### Links and Underlines

Pull underline position and thickness from the font's own metrics rather than letting the browser decide, then tune by hand if needed:

```css
a {
  text-underline-position: from-font;
  text-decoration-thickness: from-font;
  text-underline-offset: 0.2em;
  text-decoration-skip-ink: auto;   /* gaps around descenders */
}
```

`text-decoration-style: dotted` is a common convention for a word carrying extra information, such as an abbreviation or a defined term.

**Only the color of a real underline animates reliably.** If anything other than the color needs to animate, build the underline as a separate element rather than using `text-decoration`.

Use `::marker` for custom list bullet styling without extra markup:

```css
li::marker {
  color: hsl(220 60% 50%);
  font-size: 1.2em;
}
```

---

## The Divisible-by-4 Rule

ALL spacing, sizing, padding, and margin values should be divisible by 4. This creates a consistent visual rhythm and eliminates "feels off" alignment issues.

Convert to rem by dividing by 16:

| px  | rem     | Use case                          |
|-----|---------|-----------------------------------|
| 4   | 0.25rem | Tiny gaps, icon padding           |
| 8   | 0.5rem  | Tight padding, inline spacing     |
| 12  | 0.75rem | Compact component padding         |
| 16  | 1rem    | Standard padding, paragraph gaps  |
| 20  | 1.25rem | Card padding, form field spacing  |
| 24  | 1.5rem  | Section padding (small)           |
| 32  | 2rem    | Section gaps, card spacing        |
| 48  | 3rem    | Major section separation          |
| 64  | 4rem    | Page-level vertical spacing       |
| 96  | 6rem    | Section padding, large separation |
| 128 | 8rem    | Pivotal section padding           |
| 160 | 10rem   | A section meant to dominate       |
| 192 | 12rem   | The practical ceiling             |

If you catch yourself writing `margin-top: 15px` or `padding: 13px 18px`, stop — round to the nearest multiple of 4.

---

## Spacing Scale

Build a spacing scale from these multiples as CSS variables:

```css
:root {
  --space-1:  0.25rem;  /* 4px  */
  --space-2:  0.5rem;   /* 8px  */
  --space-3:  0.75rem;  /* 12px */
  --space-4:  1rem;     /* 16px */
  --space-5:  1.25rem;  /* 20px */
  --space-6:  1.5rem;   /* 24px */
  --space-8:  2rem;     /* 32px */
  --space-12: 3rem;     /* 48px  */
  --space-16: 4rem;     /* 64px  */
  --space-24: 6rem;     /* 96px  */
  --space-32: 8rem;     /* 128px */
  --space-40: 10rem;    /* 160px */
  --space-48: 12rem;    /* 192px */
}
```

The top three steps exist for section rhythm on a full page and have no business inside a component. Skip the gaps between named steps deliberately — 20px, 28px, 40px, 56px are legal but rare, reached for when a specific alignment needs it, never as a default. A project using six arbitrary values between 16 and 32 reads as unintentional the same way mixed radius values do.

The naming uses the 4px unit count (`--space-4` = 4 x 4px = 16px = 1rem). This makes mental math trivial.

---

## Spacing Principles

### More Space Than You Think

Elements need more spacing than you think. When working at 100% zoom with your face near the screen, everything looks adequately spaced. Zoom out to 75% or view on an actual device — the gaps shrink and things look cramped.

Rule of thumb: if the spacing looks "about right" up close, it's probably too tight. Start generous and reduce.

### Gestalt Proximity

Spacing signals grouping. Related items should be close together; unrelated items should be far apart. The ratio matters more than the absolute values.

```css
/* A card with a title, description, and action button */
.card {
  padding: var(--space-6);          /* 24px internal padding */
}
.card-title {
  margin-bottom: var(--space-2);   /* 8px — title tightly coupled to description */
}
.card-description {
  margin-bottom: var(--space-6);   /* 24px — larger gap before the action */
}
```

The 8px gap between title and description says "these belong together." The 24px gap before the button says "this is a separate concern."

**The ratio rule: the gap between groups is at least 2× the gap within one.** At 8px inside a group, groups need 16px or more between them. Below 2×, the eye cannot find the boundary and the grouping reads as noise rather than structure.

### Group With Space, Not Lines

Three tools create grouping, in strict order of preference:

1. **Negative space** — the default, and usually sufficient on its own.
2. **Background shapes** — a card or filled container, where a group must read as one object: a selectable row, a draggable card.
3. **Separator lines** — a last resort for dense data where space costs too much: tables, long settings lists.

```css
/* Good — spacing alone communicates the grouping */
.field-group { display: flex; flex-direction: column; gap: 8px; }
.form        { display: flex; flex-direction: column; gap: 24px; }

/* Bad — uniform spacing, then lines to compensate for it */
.form > * { margin-bottom: 12px; border-bottom: 1px solid var(--border); }
```

Where a separator is genuinely needed, keep it quiet: hairline width, low contrast, and never combined with a large gap that already did the job.

### Align to Shared Edges

Pick a small set of alignment edges and put everything on them — the eye tracks straight edges to scan. Every stray edge reads as noise even when nobody can name it: an icon 2px off the text edge, a card padded unlike its neighbor.

Use one spacing step to express each level of subordination (`16px` is a useful default), and repeat that same step for deeper nesting.

```css
/* Good — one shared leading edge, one indent step */
.section        { padding-inline: 24px; }
.section .child { margin-inline-start: 16px; }

/* Bad — three unrelated leading edges in one column */
.header    { padding-inline-start: 20px; }
.list-item { padding-inline-start: 14px; }
.footer    { padding-inline-start: 24px; }
```

Numbers in tables align to the trailing edge; text aligns to the leading edge.

### Internal Never Exceeds External

The rule that decides which token applies: **the space around a group is equal to or greater than the space within it.** If a card's padding is larger than the gap to its neighbor, the eye cannot find the boundary between them, and the layout reads as cramped inside and empty outside at the same time.

Three cards with 24px between them need at least 24px of internal padding each, not less. A section with 64px of outer padding keeps the gaps between its internal groups smaller than that.

### Card Padding Floors by Type

Generic "add padding" advice is how cards end up inconsistent. Use a floor per card type instead.

| Card type | Minimum internal padding |
|---|---|
| Compact (stat tile, nav row, list item in a dense tool) | 12-16px |
| Content (feature card, pricing tier, testimonial — anything with a heading plus body) | 24px |
| Showcase (a highlighted tier, a hero's visual frame) | 32px+ |

The card meant to carry the most visual weight in a layout should have the most internal room, not the same padding as everything around it.

Section-level padding is a different scale with its own rules — see `page-composition.md`.

### Breathing Room Between Controls

Controls placed too close get mis-tapped and read as a single unit. Where the project has no density scale, start here:

| Between | Starting point |
|---|---|
| Adjacent bordered or filled controls (buttons, inputs) | `12px` |
| Around borderless controls (text buttons, icon buttons) | `24px` |
| Unrelated control groups | `24px`+ (2× the intra-group gap) |

Borderless controls need more clearance precisely because nothing marks where one target ends and the next begins — the space *is* the boundary. Compact professional tools may use less, provided hit areas stay distinct and never overlap. Preserve an established, usable density rather than inflating it to match these numbers.

### Consistent Rhythm

Apply spacing consistently across similar elements. If cards in a grid have 24px gaps, all grids with similar content should use 24px gaps. Inconsistent spacing makes a design feel unfinished.

```css
/* Consistent vertical rhythm for content sections */
.section {
  padding-block: var(--space-16);     /* 64px top and bottom */
}
.section + .section {
  border-top: 1px solid var(--border);
}
.section > * + * {
  margin-top: var(--space-6);         /* 24px between child elements */
}
```

---

## Putting It Together

A complete type and spacing system in one block:

```css
:root {
  /* Type scale */
  --text-xs:   0.75rem;
  --text-sm:   0.875rem;
  --text-base: 1rem;
  --text-lg:   1.125rem;
  --text-xl:   1.25rem;
  --text-2xl:  1.5rem;
  --text-3xl:  2rem;
  --text-4xl:  2.5rem;

  /* Line heights */
  --leading-tight:  1.1;
  --leading-snug:   1.25;
  --leading-normal: 1.5;
  --leading-loose:  1.6;

  /* Spacing scale */
  --space-1:  0.25rem;
  --space-2:  0.5rem;
  --space-3:  0.75rem;
  --space-4:  1rem;
  --space-5:  1.25rem;
  --space-6:  1.5rem;
  --space-8:  2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --space-24: 6rem;

  /* Font */
  --font-sans: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}

/* Base application */
body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
}

h1 {
  font-size: var(--text-4xl);
  line-height: var(--leading-tight);
  font-weight: 700;
  margin-bottom: var(--space-6);
}

h2 {
  font-size: var(--text-2xl);
  line-height: var(--leading-tight);
  font-weight: 600;
  margin-bottom: var(--space-4);
}

h3 {
  font-size: var(--text-xl);
  line-height: var(--leading-snug);
  font-weight: 600;
  margin-bottom: var(--space-3);
}

p + p {
  margin-top: var(--space-4);
}
```

### Usage in Components

```css
/* Card component using the system */
.card {
  padding: var(--space-6);
  border-radius: var(--space-3);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  line-height: var(--leading-snug);
  margin-bottom: var(--space-2);
}

.card-body {
  font-size: var(--text-base);
  line-height: var(--leading-normal);
}

/* Stacked card list */
.card + .card {
  margin-top: var(--space-4);
}

/* Card grid */
.card-grid {
  display: grid;
  gap: var(--space-6);
}
```

### Tailwind Equivalent

If using Tailwind, these principles map directly to its default scale:

- `text-xs` through `text-5xl` for type
- `p-1` through `p-16` for spacing (each unit = 4px = 0.25rem)
- `leading-tight`, `leading-snug`, `leading-normal`, `leading-relaxed` for line height
- `space-y-*` and `gap-*` for consistent element spacing

The divisible-by-4 rule is baked into Tailwind's defaults, so stick to the scale and avoid arbitrary values like `p-[13px]`.

---

## Rendering Details

### Reach for the property, not the raw tag

Where a CSS property exists for a font feature, use it: `font-weight: 650` rather than `font-variation-settings: "wght" 650`, `font-optical-sizing: auto` rather than `"opsz"`, `font-variant-numeric: tabular-nums` rather than `font-feature-settings: "tnum" 1`.

Properties keep working when a non-variable fallback renders. A raw variation setting silently does nothing there. Reserve raw tags for custom axes and niche features that have no property of their own — a font's own numbered stylistic sets and character variants, where what each slot does differs font to font.

Useful features worth knowing exist: tabular numbers for anything that changes, slashed zero to tell `0` from `O`, and real small caps and superscripts through `font-variant-caps` and `font-variant-position` rather than faking them with a smaller font size.

### Tabular numbers on changing values

Digits have different widths by default, so a timer, counter, price, or any value that updates in place shifts the layout every time it changes. Apply `font-variant-numeric: tabular-nums` to it, and to any column of numbers meant to be compared down the page.

### Font smoothing on the root only

On macOS, text renders heavier than intended. Apply the antialiasing correction once on the root element, never per component.

```css
html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### iOS input zoom

Safari zooms the whole page when an input's text is smaller than 16px. This is deliberate — 16px is the web default and Safari treats smaller as too hard to read while typing. Two fixes, and they look different, so the choice is a design decision rather than a technical one:

- **Size the input up on mobile** (`text-base sm:text-sm`). Nothing to compensate for, but the mobile input no longer matches the desktop one.
- **Keep `font-size: 16px` and scale the text down** with a transform, dividing width and line-height by the same factor. Identical at every viewport, more code to maintain. The transform shrinks the whole box, so let a wrapper draw the field's surface and keep the input itself transparent, or the background and border shrink with the text.

### Write copy naturally, style the case with CSS

Store text in natural case and control presentation with `text-transform`, so a redesign never means rewriting copy.

Use the real characters in rendered text: curly quotes in prose and straight ones in code, an en dash for ranges, the single ellipsis character rather than three periods, a non-breaking space to hold a value and its unit together across a line break, and a soft hyphen to say where a long word may break.

### Keep text selectable

Keep text selectable by default, and let `::selection` carry a little brand as long as the selected combination stays legible. `user-select: none` belongs on a draggable or gesture-driven surface where accidental selection interferes — never across the interface, and never because a button label can be highlighted.

### Choosing a typeface

| Category | Use for |
|---|---|
| Serif | Long passages, editorial reading |
| Sans-serif | The default for most interfaces |
| Monospace | Code, tables, tabular data |
| Display | Marketing headlines, hero text |

"Display" in a font's name does not make it a display font. Families that ship both a Display and a Text cut mean it literally: use the cut that matches the size being set. Text cuts are sturdier and more spaced for reading; display cuts are finer for large sizes.

Pair for contrast, not similarity. A serif headline over a sans body reads as a deliberate split between display and reading type; two near-identical sans-serifs read as a mistake.

Two fonts at the same `font-size` often look like different sizes, because x-height — the height of a lowercase `x` — differs between families. A large x-height looks bigger. Compare rendered text, not declared values.

### Bidirectional text

Set `lang` so browsers and assistive technology pick the right pronunciation, quotes, and hyphenation, and set `dir` wherever direction changes.

A short snippet follows the surrounding interface's direction, but **a paragraph of three or more lines aligns to its own script** — an English paragraph stays start-aligned left-to-right even inside a right-to-left interface. `text-align: start` with the correct `lang` and `dir` handles it.

**Digit order never reverses.** A phone number reads identically in both directions. Browsers handle this through the Unicode bidi algorithm; never fight it with manual reordering. Wrap a mixed-direction value in `<bdi>` where adjacent text disturbs it.

---

## Non-Latin Scripts

Everything above is a Latin typography model, and it does not transfer to CJK by swapping in a font with the right glyphs. The model itself is wrong.

- **One family across a weight scale, not two families.** Latin design pairs a display face with a body face. Hangul and CJK generally run one well-built family, with heading, body, and UI chrome distinguished by weight (semibold, regular, medium). A second family's different stroke contrast clashes far more visibly than a Latin pairing ever does, because the glyphs are denser and more structurally rigid.
- **Do not carry the "tighten the tracking" instinct across.** A Hangul syllable block is already a tightly composed unit; negative tracking compresses the gaps between whole blocks rather than between letterforms, and legibility degrades fast. Default to zero and adjust only visually.
- **Line-height runs looser, not tighter.** CJK glyphs are denser and roughly square, so even a tightened display heading generally wants more room than the Latin floor of 1.0 allows.
- **Break at word boundaries for UI text.** `word-break: keep-all` stops Korean headings, buttons, and labels breaking mid-word at arbitrary character boundaries, which is the default and reads as broken. Long-form article text is the exception where unrestricted breaking is traditional.
- **Latin inside CJK copy reads smaller** at the same nominal size. Product names and numerals in otherwise-Korean copy commonly need slightly different optical sizing. Check it in the rendered UI rather than guessing.

For Korean specifically, Pretendard is the established starting point: a system-ui-style variable font under the SIL Open Font License covering nine weights. It is not on Google Fonts, so it loads from its own CDN — verify the current embed path renders Hangul before shipping. Japanese and Chinese need their own research rather than an assumption that Korean choices carry over.
