---
summary: Type scales, font choices, line heights, spacing systems, and the divisible-by-4 rule
read_when: Setting font sizes, choosing type scales, building spacing systems, applying consistent padding and margin
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

### Links and Lists

Use `text-underline-offset` to prevent underlines from cutting through descenders:

```css
a {
  text-decoration: underline;
  text-underline-offset: 0.2em;
  text-decoration-thickness: 1px;
}
```

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
| 96  | 6rem    | Hero sections, large separation   |

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
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-24: 6rem;     /* 96px */
}
```

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
