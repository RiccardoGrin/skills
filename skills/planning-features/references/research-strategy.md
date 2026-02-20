# Research Strategy

## Table of Contents

- [When to Research](#when-to-research)
- [Research Types](#research-types)
- [Using Sub-Agents](#using-sub-agents)
- [Synthesizing Findings](#synthesizing-findings)
- [Research Anti-Patterns](#research-anti-patterns)

## When to Research

Research adds value when the planning agent lacks information that would materially change the plan.

**Research when:**

- Building a user-facing feature where UX conventions matter (how do other products handle this?)
- Choosing between technical approaches with non-obvious tradeoffs
- The user is entering unfamiliar territory (new domain, new pattern)
- Industry standards or accessibility requirements apply
- The feature involves integration with external services or APIs

**Skip research when:**

- The feature is purely internal (refactoring, infrastructure, CI/CD)
- The approach is well-established and the team has done it before
- The user has already provided thorough context and requirements
- Time is the primary constraint and the user wants to move fast
- The change is small enough that research would take longer than implementation

## Research Types

### Competitor & Product Research

Understand how other products solve the same problem.

**What to look for:**

- Common UX patterns (how do most apps handle this interaction?)
- Standard information architecture (where do users expect to find this?)
- Onboarding and progressive disclosure approaches
- Error handling and edge case patterns
- Mobile vs desktop differences in approach

**Good research prompts for sub-agents:**

- "How do [competitor A], [competitor B], and [competitor C] handle [feature]? Focus on the user flow, not the visual design."
- "What are the established UX patterns for [interaction type]? Look for articles from Nielsen Norman Group, Baymard Institute, or similar sources."
- "What accessibility requirements apply to [component type]? Check WCAG guidelines and common implementations."

### Technical Research

Evaluate approaches, libraries, and architectural patterns.

**What to look for:**

- Library comparison for the specific use case (not generic "top 10 libraries" lists)
- Performance characteristics and bundle size implications
- Maintenance status and community adoption
- API design patterns for the type of feature being built
- Known pitfalls or gotchas for the chosen approach

**Good research prompts for sub-agents:**

- "Compare [library A] vs [library B] for [specific use case]. Focus on API ergonomics, bundle size, and how well each works with [framework]."
- "What are the common pitfalls when implementing [pattern] in [framework]? Look for blog posts and GitHub issues describing real problems."
- "What's the recommended approach for [technical challenge] in [framework version]? Check the official docs and recent community discussions."

### Design Pattern Research

For UI/UX features, understand established interaction patterns.

**What to look for:**

- Standard interaction patterns (drag-and-drop, inline editing, multi-select, etc.)
- Animation and transition conventions for the type of interaction
- Responsive behaviour expectations
- Keyboard navigation and screen reader patterns

## Using Sub-Agents

Sub-agents enable parallel research without blocking the planning workflow.

### Structuring Sub-Agent Tasks

Each sub-agent should have:

1. **A single, focused question** — not "research everything about auth", but "compare JWT vs session-based auth for a multi-tenant SaaS with these specific requirements"
2. **Clear output expectations** — "return a comparison table with: approach, pros, cons, and your recommendation"
3. **Scope boundaries** — "focus on [specific aspect], don't cover [out-of-scope thing]"

### Parallelization Strategy

Launch research sub-agents in parallel when the questions are independent:

```
Sub-agent 1: "How do Notion, Linear, and Asana handle keyboard shortcuts in their editors?"
Sub-agent 2: "Compare ProseMirror vs TipTap vs Slate for rich text editing in React"
Sub-agent 3: "What WCAG requirements apply to rich text editors? Focus on keyboard nav and screen reader support"
```

Don't parallelize when one question's answer depends on another:

```
Step 1: "What auth approach should we use?" (JWT vs sessions)
Step 2: "Given [chosen approach], what library best supports it in Next.js?"
```

### What Sub-Agents Should Return

- **Concise, actionable findings** — not raw search results
- **Specific recommendations** with reasoning
- **Relevant links** for further reading (when the team might want to dig deeper)
- **Caveats or limitations** of the research (outdated sources, conflicting information)

## Synthesizing Findings

Raw research is not useful in a plan.
Synthesize findings into decisions and recommendations.

### From Research to Plan

1. **Distill patterns**: What do most implementations have in common?
2. **Identify the recommendation**: Given this project's constraints, which approach fits best?
3. **Note alternatives**: What was considered and why it was rejected?
4. **Flag uncertainties**: Where is the research inconclusive?

### Research Insights Format

In the plan, present research insights as:

```
## Research Insights

**UX Pattern**: Most competing products (Notion, Linear, Figma) handle this with
an inline popover rather than a full modal. Users expect to stay in context.
Recommendation: Use a popover attached to the trigger element.

**Technical Approach**: TipTap (built on ProseMirror) is the strongest fit — it supports
collaborative editing, has React bindings, and the existing editor in `components/editor/`
already uses ProseMirror primitives, so migration is incremental rather than a rewrite.

**Accessibility**: WCAG 2.1 requires keyboard-navigable toolbar, focus management on
popover open/close, and aria-labels for all formatting actions. The current implementation
is missing focus trapping — this should be addressed as part of this feature.
```

### What Not to Include

- Raw search result summaries
- Tangential findings that don't affect the plan
- Obvious information ("React is a JavaScript library")
- Research that contradicts what the codebase already uses without actionable suggestions

## Research Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Researching everything before asking the user anything | Discovery first, research second — user context narrows what to research |
| One sub-agent with a broad mandate | Multiple focused sub-agents with specific questions |
| Including raw search results in the plan | Synthesize into recommendations with reasoning |
| Researching well-known patterns | Only research when there's genuine uncertainty |
| Spending time on research when the user wants speed | Ask: "Should I research how others handle this, or move straight to planning?" |
| Ignoring research findings that conflict with initial assumptions | Update the plan — that's why you researched |
