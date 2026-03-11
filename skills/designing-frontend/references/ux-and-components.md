---
summary: UX principles, component architecture patterns, native HTML elements, and design system fundamentals
read_when: designing user interfaces, building component systems, choosing HTML elements, reducing JS dependencies, planning UX flows, creating design systems
---

# UX Principles and Component Architecture

## Don't Make Me Think

The golden rule of UX: users should understand what to do **instantly** without cognitive effort.

- Stick to established UI conventions — nav at top, logo links home, buttons look clickable, magnifying glass means search.
- Following conventions is good design, not boring design. Deviating from conventions forces users to think.
- Every element should be self-evident. If something needs a label or tooltip to be understood, the design needs work.
- Clickable things must look clickable. Interactive elements need visual affordance (color, underline, cursor change, hover state).

---

## Simple Over Complex

Simple design is harder to create than complex design. It requires discipline and knowing what to leave out.

- Simple does not mean minimal to the point of uselessness — all essential elements must be present.
- Good design = as little design as possible. Design solves problems; it is not art.
- When in doubt, remove. If removing something breaks the experience, add it back. If no one notices, it was unnecessary.
- Start with core functionality (heading, input, button) rather than layout structure. Build outward from the task.

---

## User Flow

Map the shortest path from intent to task completion.

- Count clicks/steps to complete core tasks. Every unnecessary step loses users.
- Reduce friction: pre-fill fields, use smart defaults, show progress indicators for multi-step flows.
- Group related actions together. Don't scatter related controls across the page.
- Test with real people and iterate. Your mental model of the UI is not the user's mental model.

### User Flow Documentation

Before building UI, create a `docs/user-flows.md` file in the project.
This becomes a living document that the agent maintains and checks with the user.

**Flow format:**

```
## Flow: [Name] (e.g., "New User Signup")

**Entry point:** Landing page CTA / Direct URL / Email link
**Goal:** User completes signup and sees dashboard

1. User lands on signup page
   - Sees: Email/password form, social login options, "Already have account?" link
   - Data needed: None
   - Edge cases: Returning user (redirect to login), expired invite link

2. User submits form
   - Sees: Loading state on button (gray out, show spinner)
   - Data needed: Email, password
   - Edge cases: Invalid email, weak password, email already taken, network error

3. User lands on onboarding
   - Sees: Welcome message, "Start here" prompt, empty dashboard with guidance
   - Data needed: User profile
   - Edge cases: None (first visit is always empty state)
```

**Edge cases to check at every step:**
- **Empty state:** What shows when there's no data yet?
- **Error state:** What happens when something fails?
- **Loading state:** What does the user see while waiting?
- **Unauthorized state:** What if the user lacks permission?
- **Offline state:** What if the network drops?

Present flows to the user for review before building.
Update the doc whenever requirements change.

### Interaction Pattern Decisions

Choose the right container for each interaction:

| Pattern | Use When | Behavior |
|---------|----------|----------|
| **Popover** | Simple, non-blocking context (settings toggle, filter dropdown) | User can click away to dismiss |
| **Modal / Dialog** | Complex but same-context action (create new item, confirm delete) | Blocks background; requires explicit close |
| **New page** | Large or detailed content (item details, settings page, reports) | Full navigation; needs breadcrumb or back button |
| **Toast** | Brief feedback after action (saved, deleted, error occurred) | Auto-dismisses; non-blocking; stackable |
| **Inline expansion** | Revealing related detail (accordion, expandable row) | Stays in context; no overlay |

**Destructive action pattern:**
1. User clicks delete/remove
2. Confirmation dialog appears (use native `<dialog>`)
3. Brief animation on confirm (button loading state)
4. Toast notification confirming completion
5. Provide undo option when possible

### Designing Empty States

Empty states are a user's first encounter with a feature — design them intentionally.

**Every list, table, dashboard, and data view needs an empty state.**

Good empty states include:
- A clear explanation of what will appear here
- A primary action to get started ("Create your first project")
- Optional illustration or icon (keep it simple)
- For dashboards: sample/demo data toggle so users understand the layout

```html
<!-- Empty state example -->
<div class="empty-state">
  <svg><!-- simple illustration --></svg>
  <h3>No projects yet</h3>
  <p>Create your first project to get started.</p>
  <button class="btn-primary">Create Project</button>
</div>
```

### Loading States

Never show blank areas while content loads.

**Skeleton screens** (gray placeholder shapes matching the layout) are preferred over spinners for content areas.
Spinners are appropriate for buttons and small inline actions.

Use skeleton screens for content loading areas. See `references/animation-and-motion.md` for the skeleton shimmer CSS implementation.

**Button loading states:** On click, gray out the button, disable it, and show a spinner or "..." to indicate the action was registered.

### Onboarding Patterns

Avoid forced linear tutorials. Use progressive onboarding:

- **Contextual tooltips:** Appear when the user first encounters a feature
- **"Start here" buttons:** Visually emphasized entry points on empty screens
- **Empty states as onboarding:** Each empty view explains what it does and how to get started
- **Feature discovery:** Subtle indicators (dots, badges) on unexplored features
- **Mini-onboarding:** Treat every new feature encounter as a brief introduction, not just the first login

### Dashboard & SaaS Patterns

Dashboards have different design constraints than marketing pages.

**Layout structure:**
- **Sidebar:** The product's navigation spine. Contains: logo, nav links, search, profile, collapse toggle. Always visible or one-click accessible.
- **Top bar:** Reserved for page-level actions (filters, dropdowns, primary action button). Not for global navigation.
- **Content area:** Most important data at top. Use a grid of cards, lists/tables, and charts.

**Dashboard typography:** Use smaller, tighter type than landing pages. Data-dense UIs need compact but readable sizing.

**Core dashboard components:**
1. **Lists/Tables** — For structured data. Add sorting, filtering, and search. Design for 0, 1, and many items.
2. **Cards** — For summarized metrics or grouped content. Keep consistent sizing.
3. **Forms/Inputs** — For user actions. Group related fields. Validate inline.
4. **Charts** — Keep simple. Clear axes and labels. Hover states show exact values. Dim non-hovered elements. Avoid decorative chart effects (rounded bar tops, 3D, excessive gradients).
5. **Tabs** — For switching between related views without navigation.

**Chart design rules:**
- Always include axis labels and values
- Hover state: highlight the element, dim others, show tooltip with exact value
- Avoid rounded bar tops (they obscure exact values)
- Simple > beautiful for data visualization

**SaaS-specific considerations:**
- Design for the "job to be done" — focus UI on the single task the user hired the product for
- Speed is an aesthetic: a 1-second delay cuts conversions by 7%. Optimize perceived performance with skeleton screens.
- Show ROI: embed metrics showing time saved or value delivered when appropriate
- Brand through personality (copy, error messages, micro-interactions), not just colors

### Icon Consistency

- Use ONE icon library throughout the project (Lucide, Phosphor, Heroicons, Feather, etc.)
- Download as SVGs for styling flexibility and dark mode support
- Always add text labels or tooltips for non-obvious icons
- Different icon styles (fill vs outline) are acceptable only if they serve different purposes in visually separate areas (e.g., filled = active tab, outline = inactive)
- Match icon stroke width to your typography weight

### Language Consistency

Visual consistency is not enough — terminology must be consistent too.

- If one screen says "Delete" and another says "Remove," users feel friction they can't articulate
- Standardize: action labels (Save/Submit/Confirm), status labels (Active/Enabled/On), navigation labels
- Create a terminology guide if the project has many screens
- Button labels should describe the action outcome: "Create Project" not "Submit"

---

## Component Architecture

Most well-designed sites use surprisingly few unique component patterns — often 2-3 core components with variations.

### Identify Repeated Patterns

A typical marketing page might use only:
- A **section** component (two-column with text + media)
- A **card grid** component
- A **header/footer**

These three patterns, with prop variations, build entire pages.

### Build Reusable Components

```jsx
// One component, many variations via props
function FeatureSection({ heading, details, icon, image, direction = "left" }) {
  return (
    <section className={`feature-section ${direction}`}>
      <div className="feature-content">
        {icon && <span className="feature-icon">{icon}</span>}
        <h2>{heading}</h2>
        <p>{details}</p>
      </div>
      {image && (
        <div className="feature-media">
          <img src={image} alt={heading} />
        </div>
      )}
    </section>
  );
}

// Compose pages from components
function LandingPage() {
  return (
    <>
      <Header />
      <FeatureSection heading="Fast" details="..." image="/speed.png" direction="left" />
      <FeatureSection heading="Secure" details="..." icon="🔒" direction="right" />
      <CardGrid items={features} />
      <Footer />
    </>
  );
}
```

### Props Over New Components

Before creating a new component, ask: can an existing component handle this with a new prop? Variants like `size`, `variant`, `direction`, or `layout` prevent component sprawl.

---

## Design Systems

A design system is a collection of reusable UI components, global CSS variables, and utility classes that enforce consistency.

### Define Tokens First

Set spacing, fonts, and colors as CSS variables before building any components:

```css
:root {
  /* Spacing scale (4px unit count: --space-N = N × 4px) */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-4: 1rem;      /* 16px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */

  /* Typography */
  --font-body: system-ui, sans-serif;
  --font-heading: "Inter", sans-serif;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.25rem;
  --text-xl: 1.5rem;

  /* Colors */
  --color-primary: oklch(0.55 0.18 250);
  --color-surface: oklch(0.98 0 0);
  --color-text: oklch(0.2 0 0);
  --color-border: oklch(0.85 0 0);
}
```

### Utility Classes

Create layout helpers to avoid repeating the same CSS:

```css
.container { max-width: 72rem; margin-inline: auto; padding-inline: var(--space-4); }
.flex { display: flex; gap: var(--space-4); }
.flex-col { display: flex; flex-direction: column; gap: var(--space-4); }
.grid-auto { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-8); }
```

---

## Native HTML Elements That Replace JavaScript

Use built-in elements before reaching for libraries. Less JS = faster, more accessible, fewer bugs.

### Modal Dialogs

`<dialog>` with `showModal()` and `close()` replaces custom modal components. Handles backdrop, focus trapping, and Escape-to-close natively.

```html
<dialog id="confirm-dialog">
  <h2>Are you sure?</h2>
  <p>This action cannot be undone.</p>
  <form method="dialog">
    <button value="cancel">Cancel</button>
    <button value="confirm">Confirm</button>
  </form>
</dialog>

<button onclick="document.getElementById('confirm-dialog').showModal()">
  Delete Item
</button>
```

### Collapsible Sections

`<details>` + `<summary>` creates accordion/collapsible content with zero JS:

```html
<details>
  <summary>View shipping details</summary>
  <p>Ships within 3-5 business days. Free shipping on orders over $50.</p>
</details>
```

### Autocomplete Dropdowns

`<datalist>` adds a searchable dropdown to any input — no component library needed:

```html
<input list="frameworks" placeholder="Choose a framework" />
<datalist id="frameworks">
  <option value="React" />
  <option value="Svelte" />
  <option value="Vue" />
  <option value="Astro" />
</datalist>
```

### Progress and Meter Bars

```html
<!-- Progress: task completion (determinate or indeterminate) -->
<progress value="70" max="100">70%</progress>

<!-- Meter: scalar measurement within a known range -->
<meter min="0" max="100" low="25" high="75" optimum="80" value="62">62%</meter>
```

### Other Useful Attributes

```html
<!-- Correct mobile keyboard without JS -->
<input type="text" inputmode="numeric" placeholder="ZIP code" />
<input type="text" inputmode="email" placeholder="Email" />

<!-- Preserve whitespace and line breaks -->
<pre>Line 1
Line 2
  Indented line</pre>

<!-- Make any element editable -->
<div contenteditable="true">Click to edit this text</div>

<!-- Make elements visible but non-interactive (useful during loading) -->
<form inert>
  <input placeholder="Loading..." />
  <button>Submit</button>
</form>
```

### Favicon

Browsers auto-request `favicon.ico` from the site root. Place it in your `public/` folder to avoid 404 errors in the console.

---

## Framework Considerations

- **Svelte and Astro** compile to vanilla HTML/CSS with minimal JS — better for static or mostly-static sites.
- **Tailwind CSS** trades custom class naming for utility classes. Both approaches (utility-first and semantic CSS) are valid; pick one and be consistent.
- **Native Web Components** (Custom Elements + Shadow DOM) work without frameworks but have SEO drawbacks and require JS to render content.

---

## Design Personality & Character

Generic frontends happen when every design decision defaults to the safe middle.
Distinctive frontends happen when at least a few decisions are intentionally pushed in a specific direction.

### Discovering the Product's Personality

Before building, ask the user (or infer from context):
- **Who is this for?** A developer tool can be dense and technical. A consumer app needs to be warm and approachable. A luxury brand should feel restrained and precise.
- **What's the emotional tone?** Playful? Serious? Bold? Calm? Technical? Friendly?
- **What existing brands feel similar?** This anchors the aesthetic quickly. "Like Linear" means different things than "like Mailchimp."

### How Personality Manifests

Character doesn't require wild design — it shows up in small, consistent choices:

| Personality Lever | Safe/Generic | Distinctive |
|---|---|---|
| **Color** | Blue primary, gray neutrals | A bold or unexpected primary (coral, deep green, warm yellow) |
| **Typography** | Inter/system font at standard sizes | A characterful font for headings (serif, geometric, monospace), or unusually large/small sizing |
| **Spacing** | Even, predictable rhythm | Generous whitespace for calm, or tight/dense for intensity |
| **Border radius** | 8px on everything | Sharp corners for precision, pill shapes for friendliness, mixed for character |
| **Copy/microcopy** | "Submit", "Error occurred" | "Let's go", "Hmm, that didn't work — try again?" |
| **Illustrations/icons** | Generic line icons, stock illustrations | A consistent custom style, or deliberately no illustrations (typography-driven) |
| **Interactions** | Fade in, slide up | Snappy and immediate for tools, playful bounces for consumer apps, smooth and slow for luxury |
| **Layout** | Centered hero → 3-col features → testimonials → CTA | Structure that serves the content, not a template |

### Avoiding the "AI Look"

AI-generated frontends converge on the same patterns because they're statistically common in training data. Watch for these tells and deliberately vary them:

- **The gradient hero:** A full-width section with centered H1, subtitle, and CTA over a blue-to-purple gradient. Instead: consider a split layout, an image-led hero, a text-only hero with bold typography, or skip the hero entirely.
- **The 3-column feature grid:** Three cards with icons, headings, and descriptions in a perfect row. Instead: use a 2-column layout with larger cards, a single-column with alternating image/text, or a bento grid with varied card sizes.
- **Uniform card grids:** Every card identical size and shape. Instead: vary card sizes based on content importance, or use a masonry-like layout.
- **The safe color palette:** Blue primary, light gray background, dark gray text. Instead: start from the product's personality — a cooking app might use warm terracotta, a finance tool might use deep navy with gold accents.
- **Rounded-everything:** 8px border-radius on every element. Instead: pick a radius strategy that matches the personality. Sharp = precise/technical. Large rounds = playful. Mixed = intentional hierarchy.
- **Symmetry by default:** Everything perfectly centered and evenly spaced. Real designs use alignment and spacing to create visual flow and direct attention.

### Character Is Consistency

The goal is not to make every element unusual — it's to make a few deliberate choices and apply them consistently.
A product with one distinctive trait applied everywhere (e.g., a bold accent color, or unusually generous whitespace, or a characterful heading font) will feel more designed than one with many generic elements.

Pick 1-3 personality levers from the table above and commit to them throughout the project.
Everything else can follow standard best practices from this skill.
