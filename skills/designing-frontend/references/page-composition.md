---
summary: Show-don't-tell, the narrative arc of a page, named page shapes, section archetypes and their variation knobs, hero discipline, section rhythm, and column balance
read_when: composing a whole page or screen rather than a single component, building a landing or marketing page, building a hero, deciding what sections a page needs and in what order, or diagnosing why a page reads as generic despite good tokens
---

# Page Composition

A page can pass every token-level check — right palette, right type scale, right spacing — and still read as machine-made, because sameness lives at the level of *page shape*, not color. Two sites with different palettes and the same skeleton are the same site twice.

This file is the antidote: what a page is made of, why each section exists, and how to keep the shape from collapsing into the default every time.

---

## The Governing Default: Show, Don't Tell

The single highest-leverage rule on this page, and the easiest to lose, because writing another paragraph is always the path of least resistance.

**Each section should be mostly something to look at, with text as its caption.** Not mostly prose with a decorative icon on top. A wall of feature cards — heading plus two sentences, repeated down the page — reads as generated even with a perfect palette.

Before writing a paragraph to explain something, ask whether a visual could carry it with a caption instead, and default to the visual.

| Instead of telling | Show it |
|---|---|
| Feature card: heading + two-sentence description | A small mockup of that feature's actual UI, one-line caption |
| "Fast, powerful, real-time analytics" | An actual chart rendered in the project's palette |
| "Simple 3-step setup" as a bulleted list | Three side-by-side visual panels, each a real screen state, numbered |
| "See the difference" prose | A literal before/after split or slider |
| A number buried in a sentence | The number at display size with a one-word label, as its own tile |
| "Works with your stack" paragraph | The logo or icon grid of actual integrations |
| "Trusted by teams" claim | The real logo strip, or one real testimonial |
| An abstract benefit (calm, focus, security) | An illustration built for that concept |

Text still does real work: a headline, a short subhead, a caption, a button label. The point is that the *primary content* of a section is something to look at.

**A chart with axis labels but no title is still unlabeled.** Every chart needs a one-line caption stating what it shows. If related numbers sit beside it, connect them explicitly rather than leaving a chart and a stat list floating next to each other with no stated relationship.

**A caption that only narrates what the visual already shows is chrome, not clarification.** If the visual labels itself, cut the caption rather than rewording it. Never write a caption that defends the visual's authenticity.

**Proof sections have a higher floor than feature cards.** A label, a one-line description, and a small icon in a bordered box is the *minimum* bar for a feature card and is not enough to carry a proof beat. Proof needs a real supporting visual doing the work: an annotated capture, a constructed diagram, a chart with actual data, a before/after. If a section has nothing to show but a claim and an icon, it needs a different treatment or a real asset, not a smaller version of the feature card.

Check visual *surface area*, not just visual presence. Three small cards in a wide viewport leave the section reading as empty background around undersized content. Either one larger visual carries the section's weight, or the section needs a shape with more natural surface area.

---

## Why Each Section Exists: The Narrative Arc

Shape and story are different questions. Work out the argument first, then pick the shape that carries it.

The default arc, six beats:

1. **Hook** — the promise. The hero.
2. **Problem or stakes** — what is actually broken or at risk. Specific to this product. "Teams struggle with X" is a placeholder for a beat, not a beat.
3. **Solution or mechanism** — how it actually solves that, *shown* per the table above, not asserted.
4. **How it works** — the concrete flow. Three to five steps, not a manual.
5. **Proof** — real evidence. Real numbers, real logos, real quotes.
6. **Close** — the ask, tied back to the hook's promise.

**Never drop below four distinct beats; five is the default.** A page that runs hook to proof to close skips the part that actually persuades. "How it works" is the one beat that can legitimately fold into "Solution" for a simple enough product, and that is a stated merge, not a section that quietly never got built.

Read the finished page top to bottom. It should answer, in order: who is this for and what is the promise, what is wrong, how does this fix it, why should I believe it, what do I do now. A section serving none of those is a gap in the argument.

This is a separate property from visual variety. A page can have a perfectly varied shape and still read as sections that do not add up to anything.

---

## Named Page Shapes

Pick one by name before building. The reach for "the first shape that comes to mind" is always the same shape, and that shape is the generic hero, three feature cards, testimonial, CTA, footer rhythm — the strongest "a machine built this" signal at the page level, and one that survives a perfect palette.

| Shape | What it is | Reach for it when |
|---|---|---|
| **Feature Stack** | Full-width bands down the scroll, each an alternating text/visual split | 3-6 distinct capabilities that each deserve a real visual. Bands, never a 3-up card grid |
| **Bento Showcase** | Asymmetric grid of mixed-span tiles, each showing one capability as a live-looking fragment | Many small features, better at a glance than in sequence |
| **Editorial Index** | Masthead, a numbered or categorized index, generous type, hairline rules | Portfolios, agencies, publications, "who we are" |
| **Long-Scroll Narrative** | The arc told top to bottom, one full section per beat, scroll-linked reveals | A non-obvious product that needs explaining before the pitch lands |
| **Stat-Led** | One dominant real number, or a tight row of them, is the spine | The story is genuinely quantitative and the numbers are real |
| **Gallery Grid** | The work is the pitch; real imagery fills the page, chrome minimal | Commerce, photography, food, travel, physical product |
| **Product Demo** | The hero is the product in use; the page is organized around doing, not describing | Dev tools and apps where seeing it work is the argument |
| **Split Diptych** | A persistent statement column beside a scrolling content column | Studios, single-voice products, art-directed rather than stacked |
| **Conversational FAQ** | Built around the real questions the audience asks, with proof folded into the answers | Products fighting a specific objection or trust gap |
| **Manifesto** | Type-forward, few images, one strong point of view in big statements | Brand-led launches, opinionated products |
| **Catalogue** | A structured, near-tabular listing presented with editorial care | Many SKUs, pricing as a page, changelogs, spec-heavy products |
| **Poster Fold** | One full-bleed art-directed fold carries the whole first screen | The brand or a single image *is* the message |

**Match shape to argument, not to habit.** If the strongest argument is "look how much people use this," that is Stat-Led. "Look at the work" is Gallery Grid. "Let me explain why this matters" is Long-Scroll Narrative.

**On a vague brief, offer rather than default.** Three concrete choices from categorically different groups, not a survey of all twelve.

**These are for public and marketing pages.** An app shell has its own governing shape — see below.

---

## Section Archetypes and Their Knobs

The shape is the skeleton; these are the parts inside it. Two rules bind:

- **No two sections on one page use the same archetype.** Two identical feature blocks read as templated.
- **If you reuse an archetype, change at least one knob.** Two heroes both built split, left-bias, with a mockup are the same hero.

| Slot | Variants worth having | Knobs |
|---|---|---|
| **Nav** | Minimal bar, product bar with sections, floating pill, sidebar-style, none | Position, density, whether the CTA lives here |
| **Hero** | Split with visual, centered statement, full-bleed poster, product demo, stat-led, letter/manifesto | Bias (left/right/centered), visual type, headline scale |
| **Feature** | Alternating full-width bands, bento tiles, spec sheet, numbered step sequence, annotated capture, comparison | Rhythm, tile spans, visual-to-text ratio |
| **Proof** | Logo wall, pull quote, single testimonial with face, stat strip, case tile | Density, whether a visual backs it |
| **CTA** | Inline form, statement plus action, sticky bar, split with reassurance | Placement, commitment level |
| **Footer** | Masthead, minimal single row, sitemap, statement, oversized wordmark | Column count, whether it repeats the nav |
| **Section head** | Hanging in negative space, inline small-caps, sticky pinned, eyebrow stacked above heading | Alignment, whether an eyebrow appears at all |

**Two chrome patterns to avoid by default.** The wordmark-left, inline-links, button-right nav is a template signature unless the page genuinely has two or fewer destinations. The four-column Product / Company / Resources / Legal footer with a social row is the same, unless it is a real docs root.

**The eyebrow-left, heading-right two-column section head is the most reliable templated-editorial tell.** Stack the eyebrow above the heading in one column, and cap eyebrows at one or two per page. Most sections do not need one at all — the identical pill eyebrow repeated above every section is a signature.

**A section headline is not a hero headline.** Cap it at roughly 50-65% of the hero's full display size, and it should read in one or two lines regardless of word count. One deliberate large mid-page statement is a legitimate moment in a Manifesto or Long-Scroll Narrative. Repeated at every section head, it is a mistake.

**No hand-built fake chrome.** Never draw a fake browser bar with a URL pill and traffic-light dots, a fake phone frame, or a fake IDE window. Use a real screenshot in a plain frame, or omit the chrome. Redrawn chrome is a strong tell — it invents UI the real environment already supplies.

---

## Hero Discipline

Before writing any markup, complete this sentence in plain language:

> This product helps [specific user] achieve [valuable outcome] by [distinct mechanism].

The valuable outcome becomes the headline. The subhead clarifies the mechanism. If the hero needs a workflow diagram, four metrics, and a paragraph to explain the product, the message is not sharp enough yet.

### The attention budget

A starting limit, not a quota to fill:

- One optional eyebrow, only when it adds context the headline cannot
- One headline: one promise, usually 6-12 words
- One subhead: one sentence, 16-28 words, at most two lines on desktop
- One primary action, plus at most one secondary that serves a genuinely lower-commitment path
- One focused visual that proves the outcome

Do not add trust rows, feature chips, workflow rails, metric sidebars, floating badges, decorative orbits, or a second mockup merely because there is room. Move them into the next section where they can become real proof instead of hero clutter.

### Headline size and word count move together

| Words | Display size |
|---|---|
| 3-5 | The same full display size the 6-8 band uses — **never larger** |
| 6-8 | Full display size |
| 9-12 | One tier down, roughly 15-20% smaller across the whole range |

The instinct to size inversely with word count is the failure to watch for: a four-word headline rendering one word per line at near-viewport scale. Short headlines at real premium products run at the same top-tier size, not a scaled-up outlier. Punchiness comes from word choice and whitespace, not from exceeding the scale's own ceiling.

A headline under six words should read on one or two lines. If it breaks into three or more, the type is too large for its container at that word count. Step it down.

### The subtraction pass

List every distinct group in the hero and ask what user question it answers. Keep only groups answering one of:

1. What is this?
2. Why should I care?
3. What should I do next?
4. What does a good result look like?

Move everything else below the fold. If two groups answer the same question, keep the stronger one.

### Composition

- Give the headline and the visual clear, separate territories with generous negative space.
- Let one side dominate slightly. Equal-weight columns read as mechanically templated.
- Do not stack the eyebrow, headline, subhead, and action all on one centered vertical axis. Center at most two and break alignment for the rest.
- Keep the hero palette quieter than the sections below it. The accent identifies the key phrase, the action, or a detail in the visual — not all three at once.
- Show the desirable result, not the machinery. For a dashboard, crop to the one decision users care about rather than reproducing the whole app shell.
- At most one outer frame around the visual. Never a dashboard inside a dashboard.

---

## Section Rhythm

### Padding weighted by role

Flattening every section to one value is what makes a page read as cramped with nothing getting its own moment, even when each individual number is on the scale. Weight the tier by what the section is doing.

| Section role | Padding per side (desktop) |
|---|---|
| Connective (logo strip, trust bar, transition band) | 48-64px |
| Standard content (a feature explanation, a testimonial block) | 64-96px |
| Pivotal (the hero, the primary proof or demo) | 128-192px |

The **perceived gap** between two adjacent sections is one section's bottom padding plus the next one's top padding, and it commonly lands at 120-250px on desktop. That gap is what a visitor experiences as the pause before the next idea starts.

These are desktop values. Drop one to two tiers at mobile widths — the relative weighting holds, the absolute numbers compress. And none of it applies to an app shell, which stays dense.

### One separation mechanism, project-wide

Pick one and apply it at every section boundary. A page that alternates tint on some boundaries and adds dividers on others reads as unplanned.

- **Alternating surface tint** — solid default for a content-dense page with many stacked sections.
- **Hairline divider** — fits a project already using hairline borders instead of shadows.
- **Generous padding alone, no tint or divider** — what most well-separated pages actually use, and it only works if the padding is genuinely in the range above. Fixed padding at a cramped value does not separate anything.

### Column balance

Two-column sections rarely have naturally equal columns. Left alone, the shorter one stops short and the section reads as a cluster of content with unclaimed space beneath it. This is a layout decision, not a padding problem. Pick one deliberately:

1. **Vertically center the shorter column** against the taller one.
2. **Add a real element that uses the remaining height** — a stat callout, a short quote, a guarantee note. Prefer a visual over another paragraph.
3. **Cap the taller column** — tighten the headline, shorten the prose, cap the max-width.

The concrete failure this catches: a pricing section with a tall headline column beside three cards clustered at the top and dead space below them.

---

## App Shells Are a Different Animal

A dashboard or internal tool is not a page someone scrolls once. It is a frame they work inside for hours. There is no hero, and the shell *is* the first impression on every session.

- **Sidebar** carries primary navigation and persists across every screen. Group it once there are more than about seven destinations. Collapse it to icon-only on narrow viewports rather than hiding it — people live in this thing.
- **Topbar** is contextual, not navigational: breadcrumb or section label, search, account. It should never repeat what the sidebar already says.
- **Content area** has exactly one job per screen. Lead with the one number or status the user opened the app to check.
- **Active nav item** is the one place the brand color earns a dedicated treatment outside a button. Pick one treatment and use it everywhere. The hover state on inactive items must never carry the same visual weight, or people lose track of where they are.
- **Breadcrumbs** are wayfinding, not calls to action. Muted for everything but the current segment.

**Density is correct here, not a mistake to fix.** A shell should be denser than the same product's marketing page: more rows visible, tighter row height, smaller default type in data-heavy areas. That is not a contradiction of the project's character; it is what that character looks like applied to a tool instead of a pitch. Do not inherit marketing section padding into a shell.

Group related metrics rather than scattering unrelated ones across a uniform grid because a grid was easy to build. And build the whole action path: what the user checks, what they can change, what happens after, and how they recover from a mistake.

---

## Two Habits That Break the Default

**State the pick out loud before building.** Which shape, which archetypes, which beats, and how they differ from the obvious choice. Picking on the page rather than in your head is what actually breaks the pull toward the default — an unstated decision reverts to the most common option every time.

**Find the one intentional rule-break.** A design where everything sits on the grid, evenly spaced and perfectly safe, reads as generated even when every token is right. Human-authored work almost always has one deliberate break: an element bleeding past its column, an oversized number, an asymmetric moment, a bit of tension the system did not require. If there is no such moment, the page is probably too safe. One is the budget — stacked decorative gestures are the opposite failure.

---

## Honesty

Never invent a metric to fill a shape. "10× faster," "trusted by 50,000+ teams," "+47% conversion" — any quantitative claim not supplied by the user and made up to fill a stat-led layout is a fabrication the moment it is invented, and it is the fastest way a proof-led page loses trust. The same holds for testimonials, logos, and case-study counts.

If real figures are not available, pick a shape that does not demand them, or leave the slot honestly empty with a labeled placeholder. Do not stage a comparison so one side looks worse than it is.
