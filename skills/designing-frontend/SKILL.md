---
name: designing-frontend
description: Guides creation of high-quality frontend interfaces using proven design principles for color, typography, spacing, layout, depth, animation, and UX. Covers both building new UIs and auditing existing ones. Use when creating web components, pages, or applications, or when reviewing frontend code for design quality
version: 1.0.0
---

# Designing Frontend

A comprehensive design knowledge base for building polished, professional frontends.
Apply these principles when creating new interfaces or auditing existing ones.
Framework-agnostic: the principles work with any CSS approach (vanilla, Tailwind, CSS modules, etc.).

## Reference Files

| File | Read When |
|------|-----------|
| `references/color-and-theming.md` | Choosing colors, building palettes, implementing dark/light mode |
| `references/typography-and-spacing.md` | Setting type scales, font choices, spacing systems |
| `references/layout-and-responsiveness.md` | Building layouts with flexbox/grid, making designs responsive |
| `references/depth-and-visual-hierarchy.md` | Adding shadows, depth, borders, establishing visual hierarchy |
| `references/animation-and-motion.md` | Adding transitions, animations, scroll effects, SVG animation |
| `references/ux-and-components.md` | Designing user flows, building dashboards, planning interaction states (empty/loading/error), building reusable components, onboarding patterns, choosing native HTML elements |

## Task Sizing

Before starting, classify the task to avoid over-engineering:

- **Patch** (single element change, bug fix, style tweak): Apply only the directly relevant principle. Skip phases, skip audit. Don't load reference files.
- **Component** (new button, card, form, modal): Phases 1-5 only. Load 1-2 reference files max.
- **Page/Feature** (new page, multi-component feature, dashboard): Full workflow. Load references as needed per phase.
- **Audit** (reviewing existing code): Use the audit checklist. Load references for failing items only.

Always match the scope of your design work to the scope of the user's request.
A request to modify one component does not warrant project-wide changes to color systems, spacing tokens, or theme infrastructure.
If the project has an existing design system, follow it. These guidelines apply when building from scratch or when the project has no established patterns.

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

### 6. Design Before Code

Always sketch or plan the UI before coding, even if rough.
Gather inspiration from real sites, Figma Community, Dribbble, or Mobbin.
Identify the repeated patterns — most sites use only 2-3 core component types with variations.

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

## Build Workflow

When creating new frontend interfaces, follow this sequence.
Load relevant reference files based on which phases apply to your task.

```
Phase 0: User Flows    → Map core journeys, identify edge cases, document in project
Phase 1: Structure     → Identify components, sketch layout hierarchy
Phase 2: Layout        → Build with flexbox/grid, plan responsive behavior
Phase 3: Typography    → Set type scale, font family, line heights
Phase 4: Color         → Apply palette, ensure contrast, handle dark/light mode
Phase 5: Spacing       → Apply consistent spacing system (multiples of 4)
Phase 6: Depth         → Add shadows, borders, elevation where needed
Phase 7: Hierarchy     → Verify visual hierarchy — zoom out, check scanning
Phase 8: Animation     → Add transitions and motion where they aid UX
Phase 9: Polish        → Responsive testing, native HTML elements, image optimization
```

Not every task requires all phases.
A small component may only need phases 1-5.
A full page build benefits from the complete sequence.

### Phase 0: User Flows

Before building any UI, map the user's journey through the feature or page.

1. Create or update `docs/user-flows.md` documenting each core user flow as a numbered step sequence (entry point → intermediate steps → goal achieved)
2. For each step, note: what the user sees, what actions are available, what data is needed, what happens next
3. Identify edge cases at every step: empty states, error states, loading states, unauthorized states
4. Present flows to the user for review before coding
5. After building, verify the implemented UI matches the documented flows
6. Update the doc whenever flows change

Load `references/ux-and-components.md` for detailed user flow guidance.

Skip Phase 0 for isolated component changes, targeted fixes, or tasks where the user flow is self-evident.
Only create `docs/user-flows.md` when building a new feature with multiple screens or a multi-step interaction.
For smaller tasks, describe flows in your response rather than creating files.

### Phase 1: Structure

Before writing HTML, create a mental model of the component tree.
Every element is a box — responsive design is dynamically moving boxes into rows and columns.
Identify repeated patterns and build them as reusable components.
Most well-designed sites use surprisingly few unique component types — often just 2-3 core patterns with different props.

### Phase 2-9: Reference Files

Load only the reference files relevant to your current phase:

| Phase | Reference File |
|-------|---------------|
| 2. Layout | `references/layout-and-responsiveness.md` |
| 3. Typography | `references/typography-and-spacing.md` |
| 4. Color | `references/color-and-theming.md` |
| 5. Spacing | `references/typography-and-spacing.md` |
| 6. Depth | `references/depth-and-visual-hierarchy.md` |
| 7. Hierarchy | `references/depth-and-visual-hierarchy.md` |
| 8. Animation | `references/animation-and-motion.md` |
| 9. Polish | `references/layout-and-responsiveness.md` + `references/ux-and-components.md` |

## Audit Checklist

When reviewing existing frontend code, check these areas.
Load the relevant reference file for detailed criteria on any failing item.

### Color & Theming
- [ ] Colors defined as CSS variables or design tokens, not hardcoded
- [ ] Using HSL or OKLCH format for easy palette manipulation
- [ ] Limited palette: primary + secondary + accent + neutrals + semantic states
- [ ] Contrast ratios meet WCAG AA: 4.5:1 for normal text, 3:1 for large text (18px+ bold or 24px+)
- [ ] Dark mode support (if applicable) uses proper shade inversion

### Typography & Spacing
- [ ] Consistent type scale (not arbitrary font sizes)
- [ ] Single font family (or deliberate pairing with clear roles)
- [ ] Line height inversely proportional to font size
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
- [ ] Transitions use appropriate timing functions (not all `linear`)
- [ ] Animations serve UX purpose (feedback, orientation, delight) not just decoration
- [ ] Motion respects `prefers-reduced-motion` media query
- [ ] Hover animations wrapped in `@media (hover: hover)`

### UX & Accessibility
- [ ] Core user flow achievable in minimum clicks
- [ ] Native HTML elements used where appropriate (`dialog`, `details`, `datalist`)
- [ ] Images optimized (WebP, appropriate sizing)
- [ ] SVGs used for icons instead of raster images

### Interaction States
- [ ] Empty states designed (not blank screens) with clear next-action guidance
- [ ] Loading states use skeleton screens or spinners, not blank areas
- [ ] Error states are informative and offer recovery actions
- [ ] Destructive actions have confirmation dialogs
- [ ] Post-action feedback provided (toasts, button state changes, completion indicators)
- [ ] Interaction pattern choices appropriate (popover vs modal vs new page)
- [ ] Icon library consistent (one set, with labels/tooltips for non-obvious icons)
- [ ] Action terminology consistent across all screens

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
| Over-designing | The simplest solution that works is the best solution |
| Designing only the happy path | Map user flows first; design for empty, error, loading, and unauthorized states |
| Inconsistent terminology ("Delete" vs "Remove") | Standardize action labels and button names project-wide |
| Mixing icon styles (fill + outline + varying weights) | Use one icon library consistently (Lucide, Phosphor, etc.) |
| Stacking multiple effects (gradient + shadow + glow) | Pick one subtle effect or none; less is almost always better |
| No feedback after user actions | Gray out buttons on click, show loading indicators, use toasts for confirmation |
| Over-designed charts (rounded bars, missing axes) | Simple charts with clear axes, labels, and hover states showing values |
| No empty state design | Design intentional empty states with guidance on what to do next |
| Using Lorem Ipsum in prototypes | Use real or realistic content to catch layout and flow issues early |

## Related Skills

For frontend code architecture decisions (rendering strategies, state management, component file organization, MVC/MVVM patterns), see the `architecting-frontend` skill (if available).
This skill focuses on visual design and UX — how the interface looks, feels, and behaves.
