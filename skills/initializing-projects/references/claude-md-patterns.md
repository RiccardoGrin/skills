---
summary: Examples and principles for effective minimal CLAUDE.md files
read_when:
  - Constructing a CLAUDE.md for a new project
  - Reviewing examples of effective minimal project configs
---

# CLAUDE.md Patterns

## Minimal Starter

For most projects, this is enough to start.
Let the file grow naturally as the agent discovers gotchas.

```markdown
## What This Is
[One paragraph: what it does, who it's for, why]

## Do / Don't
- Do: [specific convention that differs from the default]
- Don't: [specific thing that has caused problems]

## Known Issues
<!-- Populated by Claude — remove when fixed -->

## Decision Log
<!-- Key business/project decisions only -->
```

This works for CLI tools, libraries, APIs, and full-stack apps.
The agent reads `package.json`, config files, and directory structure on its own.

## Project with Business Context

When the project has domain-specific constraints or a non-obvious mission.

```markdown
## What This Is
Internal tool for the sales team to track customer onboarding progress.
Built so account managers can see which onboarding steps are incomplete without asking engineering.
Users are non-technical — every action must be obvious without documentation.

## Do / Don't
- Do: use server actions for mutations (not API routes) — decided in sprint 3 for simplicity
- Do: validate all form inputs with zod at the boundary, then trust internal types
- Don't: add loading spinners to instant operations — only show for >200ms delays
- Don't: soft-delete anything in the onboarding_steps table — hard delete is fine, we have audit logs

## Key Files
- `lib/onboarding-engine.ts` — state machine for onboarding flow, all transitions go through here
- `app/api/webhooks/stripe/route.ts` — handles payment events, must stay idempotent

## Known Issues
<!-- Remove when fixed -->

## Decision Log
- 2026-01-15: Chose server actions over API routes for all mutations — fewer files, less boilerplate, sales team only uses the web UI (no mobile/API clients)
- 2026-02-01: Stripe webhook handler must be idempotent — we got duplicate events in prod, added event ID dedup
```

Note: no tech stack listing, no repo structure, no development commands.
The agent reads those from config files.

## Lessons from Power Users & Research

- Start minimal, then grow through usage. Each mistake becomes a do/don't rule.
- Agents maintain the file. The file is a living document, not a static config.
- Known issues get added when found and removed when fixed. Decisions get logged when made.
- Verbose CLAUDE.md files can actually hurt agent performance.
- Agents are good at figuring things out from code.

## What to Include vs What's Noise

**Include — things Claude would get wrong or waste time on:**
- Non-obvious conventions ("we use server actions, not API routes, for mutations")
- Domain-specific rules ("the user table has soft-delete, always filter by deleted_at IS NULL")
- Business decisions that affect code ("no loading spinners for <200ms operations")
- Gotchas from real experience ("Stripe webhooks come in duplicate, handler must be idempotent")
- Key files that are non-obvious ("all onboarding transitions go through lib/onboarding-engine.ts")

**Exclude — noise that wastes context:**
- Tech stack descriptions ("Next.js 14 with TypeScript and Tailwind")
- Repo structure listings ("src/ contains source code, tests/ contains tests")
- Development commands verbatim from package.json
- Generic programming advice ("write clean code", "use meaningful names")
- Well-known framework patterns
- Aspirational conventions nobody follows
- Lengthy explanations of standard tools
