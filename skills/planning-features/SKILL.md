---
name: planning-features
description: Creates implementation-ready plans through discovery interviews, external research, and codebase analysis. Covers requirements, competitor research, architecture decisions, and change sequencing. Use when planning a feature, creating a spec, or when changes need discovery before coding
---

# Feature Planning

Create concrete, implementation-ready plans for features and complex changes.

DO NOT write code during planning. Only explore, research, analyse, and document.

## Reference Files

| File | Read When |
|------|-----------|
| `references/discovery-interview.md` | Starting the discovery phase or need guidance on what questions to ask |
| `references/research-strategy.md` | Planning external research or launching sub-agents for competitor/pattern research |
| `references/plan-templates.md` | Constructing the plan or reviewing plan quality — contains worked examples |

## Scope Check

Before deep planning, gauge the scope:

- **Full planning**: changes span 3+ files, cross system boundaries, have unclear requirements, or involve architectural tradeoffs
- **Light planning**: single-file changes with clear requirements — provide a brief execution outline instead of a full spec

For light planning, skip directly to a short outline: what file, what change, why.

## Workflow

### Phase 1: Discovery Interview

Conduct a thorough interview to surface requirements, constraints, and context the user may not have considered yet.

**How to interview:**

- One question at a time — wait for the user's response before moving on
- Present 2-4 concrete options with tradeoffs for each
- Always include your recommendation with clear reasoning
- Skip questions the user has already answered
- Continue until there are no more meaningful questions or the user says they're done

**What makes a good question:**

- It surfaces a genuine ambiguity or tradeoff the user needs to decide
- It cannot be answered by reading the codebase or applying common sense
- It covers territory the user may not have considered

**What makes a bad question:**

- You could answer it yourself by reading `package.json`, the codebase, or the project's AGENTS.md
- It asks for information the user already provided
- It's generic enough to apply to any project ("What framework are you using?")

If you can determine something from context, state your assumption and move on.
Don't ask — inform.

**Question domains** (not exhaustive — use judgment):

- Problem definition and success criteria
- User-facing behaviour and interaction design
- Edge cases, error states, and failure modes
- Performance, scale, and data implications
- Accessibility and internationalization concerns
- Security and privacy considerations
- Tradeoffs between approaches (with your recommendation)
- Migration and backwards-compatibility concerns

Read `references/discovery-interview.md` for detailed question categories and examples of strong vs weak questions.

### Phase 2: Research

Go beyond the codebase. Not every plan needs this — skip when the feature is purely internal, the approach is well-established, or the user has provided sufficient context.

**When to research:**

- The feature involves user-facing patterns where conventions matter (forms, navigation, onboarding, dashboards, etc.)
- There are multiple viable technical approaches and the tradeoffs aren't obvious
- The user is building something they haven't built before
- Competitor or industry patterns would inform better decisions

**What to research:**

- **Competitors and similar products** — how do others solve this? What UX patterns are established?
- **Technical approaches** — what libraries, APIs, or architectural patterns apply? What are the tradeoffs?
- **Design patterns** — for UI features, what interaction patterns are standard? What accessibility requirements apply?

**How to research:**

- Launch sub-agents in parallel with focused research questions
- Each sub-agent gets one specific question, not a broad mandate
- Synthesize findings into actionable insights, not raw dumps

Read `references/research-strategy.md` for guidance on structuring research queries and synthesizing findings.

### Phase 3: Codebase Analysis

Explore the codebase systematically. Use sub-agents for parallel exploration when the codebase is large or the feature touches multiple systems.

**What to map:**

- **Relevant files** — document paths (not line numbers — code shifts in multi-agent environments)
- **Existing patterns** — architecture, naming conventions, data flow, component structure
- **Dependencies** — what systems, files, or modules will be affected by this change
- **Similar implementations** — existing features that solve analogous problems, to maintain consistency
- **Constraints** — technical limitations, conventions from AGENTS.md or CLAUDE.md, framework constraints

**Document findings as:**

- **File**: `path/to/file.ext` — what it does, how it's relevant
- **Pattern**: existing approach used for similar features
- **Constraint**: technical limitation, convention, or requirement

### Phase 4: Plan Construction

Synthesize discovery, research, and analysis into an implementation-ready plan.

**For each change, specify:**

- File path (not line numbers)
- What function, component, class, or section to modify
- What to add, remove, or change — be specific
- Why this change serves the goal
- Dependencies — what must happen first

**Structuring the plan:**

- **Flat list** (default): Use for plans with ~4 or fewer changes concentrated in one area
- **Phased grouping**: Use when the plan has 5+ changes or spans multiple systems (data model, API, UI, etc.)
  - Each phase groups related changes that can be implemented and verified together
  - Phases are ordered by dependency — later phases build on earlier ones
  - Each phase should be safely re-runnable — if interrupted, the implementer can restart the current phase without corrupting previous work
  - Each phase ends with a brief validation checkpoint

**Plan output format (flat list):**

```
## Goal
[One sentence: what we're building and why]

## Research Insights
[Key findings from external research that informed the plan]
[Skip this section if no external research was done]

## Changes

### 1. [Description]
- **File**: `path/to/file.ext`
- **Target**: `functionName()` / `ComponentName` / relevant section
- **Action**: What specifically to add, modify, or remove
- **Reasoning**: Why this change is needed
- **Depends on**: What must happen first, or "Nothing"

### 2. [Description]
...

## Edge Cases & Risks
- [Specific scenario and how the plan addresses it]
- [Risk and mitigation strategy]

## Validation
- [ ] Specific, testable acceptance criterion
- [ ] Another criterion
- [ ] Edge case X is handled
```

**Plan output format (phased grouping):**

```
## Goal
[One sentence: what we're building and why]

## Research Insights
[Key findings from external research that informed the plan]
[Skip this section if no external research was done]

## Phase 1: [Phase Name, e.g. "Data Model"]

### 1. [Description]
- **File**: `path/to/file.ext`
- **Target**: `functionName()` / `ComponentName` / relevant section
- **Action**: What specifically to add, modify, or remove
- **Reasoning**: Why this change is needed
- **Depends on**: What must happen first, or "Nothing"

### 2. [Description]
...

**Checkpoint**: [How to verify this phase works before moving on]

## Phase 2: [Phase Name, e.g. "API Layer"]

### 3. [Description]
...

**Checkpoint**: [How to verify this phase works before moving on]

## Phase 3: [Phase Name, e.g. "UI"]

### 4. [Description]
...

**Checkpoint**: [How to verify this phase works before moving on]

## Edge Cases & Risks
- [Specific scenario and how the plan addresses it]
- [Risk and mitigation strategy]

## Validation
- [ ] Specific, testable acceptance criterion
- [ ] Another criterion
- [ ] Edge case X is handled
```

For complex features, include test descriptions in the Validation section: what test file, what test case name, and what it asserts.

**For multi-session features**, optionally add these sections to the plan:

- **Progress**: Checklist of phases/changes, marked as they're completed
- **Decision Log**: Implementation-time decisions that deviated from the original plan, with reasoning
- **Open Questions**: Anything discovered during implementation that needs revisiting

Keep the plan file updated as implementation proceeds — it becomes the source of truth.

### Persist the Plan

Write the completed plan to a markdown file so it survives beyond this session.

- If the platform provides a designated plan location, use it
- Otherwise, write to the project directory (e.g., `docs/plans/<feature-name>.md`)
- The plan must be a standalone document — readable and actionable in a future session without conversation history

- A subagent review turns up no issues
### Phase 5: Plan Review

Before delivering the plan, verify:

- [ ] Someone could implement this without asking further questions
- [ ] Plan is self-contained — all context needed for implementation is in the plan, not just in conversation history
- [ ] Plan respects project conventions (from CLAUDE.md, AGENTS.md, or equivalent project config)
- [ ] File paths reference real files in the codebase
- [ ] Steps are ordered with clear dependency chains
- [ ] Acceptance criteria are specific and testable
- [ ] Every decision includes reasoning (the "why")
- [ ] No vague language — "update", "improve", "fix" always paired with specifics
- [ ] Research insights are incorporated where relevant
- [ ] Edge cases and risks are addressed

## Anti-Patterns

| Avoid | Do Instead |
|-------|------------|
| "Update the authentication system" | "Modify `auth/middleware.ts` — add `validateSession()` that checks token expiry" |
| "Add error handling" | "Wrap the API call in `auth/api.ts` with try/catch, show toast on error" |
| "Use the standard pattern" | "Follow the existing pattern from `user/dao.ts` (class-based with explicit types)" |
| "Make sure it works" | "Verify: (1) form submits on Enter, (2) inline errors display, (3) submit disabled during request" |
| Asking "What framework do you use?" | Read `package.json` and state: "I see you're using Next.js with App Router" |
| Specifying line numbers | Reference file path + function/component name |
| Skipping research for novel features | Launch sub-agents to research competitor patterns and technical approaches |
| Asking one question then moving on | Continue the interview until all meaningful questions are covered |
