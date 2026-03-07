<!-- When all tasks are done, the loop agent prepends ALL_TASKS_COMPLETE above this line -->

# Skills Improvements (Harness Engineering)

## Goal

Improve the agent skill ecosystem based on lessons from OpenAI's "Harness Engineering" article. Core principle: **mechanical enforcement (linters, hooks, structural tests) beats documentation-only rules**. We add skills that SET UP enforcement, not skills that duplicate what linters do.

## Context for Implementing Agents

This plan was derived from OpenAI's "Harness Engineering" article (https://openai.com/index/harness-engineering/). An earlier version of this plan misapplied the article's lessons by creating documentation-only skills (review checklists, cleanup skills, testing strategy guides) — exactly the approach the article says doesn't work. The article's core finding:

**OpenAI tried manual quality processes (20% of each week on cleanup). It didn't scale. What worked: encoding rules as automated linters, hooks, and structural tests that run without agent action.**

Apply this when implementing every task below:

- **Skills should SET UP mechanical enforcement** (generate lint rules, hooks, check scripts) — not BE the enforcement (don't write skills that are checklists agents must remember to follow)
- **If a linter can catch it, don't put it in a skill.** Unused imports, debug statements, naming conventions — these are linter rules, not skill content
- **Keep skills lean.** Don't pad with reference files full of generic content Claude already knows. One reference file is fine if it contains genuinely non-obvious, domain-specific patterns
- **Hooks > instructions.** A PostToolUse hook runs on every file edit automatically. A skill instruction like "remember to check for X" relies on the agent's discipline — that's the documentation-only pattern
- **Don't re-introduce what was cut.** The Decision Log below explains what was removed from the previous plan and why. Don't sneak those concepts back in as subsections or reference files of the skills you're building
- **Only modify skills in this repo** (`skills/skills/`). Don't edit installed copies, skills in other repos, or global config files

## Important Notes

- **All new skills MUST be created using the `/creating-skills` skill** — follow its 9-step workflow, use `python skills/creating-skills/scripts/validate_skill.py` to validate
- **Only update skills within this repo** (`skills/skills/`) — never modify installed copies or skills we don't own
- **Skill patterns reference**: `skills/creating-skills/references/skill-patterns.md`
- **Format spec**: `skills/creating-skills/references/format-specification.md`

---

## Tasks

### Phase 1: Architecture Enforcement (highest value)

- [x] **Create `enforcing-architecture` skill** — `skills/skills/enforcing-architecture/` — Guided Workflow pattern. Helps users set up mechanical architecture enforcement for their projects. Workflow: detect existing architecture signals (layer structure, dependency patterns, existing lint configs) → interview user for layer boundaries, dependency direction, naming conventions → generate `ARCHITECTURE.md` (layer diagram, dependency rules, structural requirements) → generate enforcement (custom lint rules or a lightweight check script) with educational error messages that tell agents HOW to fix violations → wire enforcement into hooks (PostToolUse or pre-commit). Keep it lean — one reference file max for common layer patterns by stack. Use `/creating-skills` workflow. Run validator after.

### Phase 2: Strengthen Existing Skills

- [x] **Update `initializing-projects`** — `skills/skills/initializing-projects/SKILL.md` — Phase 1 (Auto-Detection): add detection of `ARCHITECTURE.md`, `docs/` directory, and linter config (not just formatter). Phase 4 (Hooks): extend hook generation beyond formatters — if a linter is detected but no lint hook exists, suggest a PostToolUse lint hook (e.g., `npx eslint --fix $CLAUDE_FILE_PATH`, `npx biome check --fix $CLAUDE_FILE_PATH`). If no linter is detected and the project has 10+ source files, suggest adding one appropriate for the stack. For complex projects, mention `/enforcing-architecture`. This is the mechanical enforcement path — hooks that run automatically, not instructions agents may skip.

- [x] **Update `planning` skill** — `skills/skills/planning/SKILL.md` — Phase 4 (Plan Construction): add "verification approach" field to each change spec, so loop agents know HOW to verify beyond "does it build." Example: "Verify: form submits on Enter, inline errors display, submit disabled during request." Keep it as a single added field in the existing change spec template, not a new section.

- [x] **Update `looping-tasks` VERIFY phase** — `skills/skills/looping-tasks/SKILL.md` — In the VERIFY section, add one line: "Run /simplify on files with substantial changes." That's it — don't duplicate what linters catch.

### Phase 3: Browser Testing

- [ ] **Research browser testing approaches** — Before creating the skill, research what is actually working well for agent-driven browser testing and how they are implemented. Investigate: Playwright-based approaches (how teams wire Playwright into agent workflows), Stagehand (browser automation for AI agents), browser-use, what the OpenAI article describes (Chrome DevTools Protocol, DOM snapshots, screenshots, navigation), how other agent frameworks handle browser interaction, and any open-source tools purpose-built for agent-driven UI verification. Focus on what's production-grade vs. toy/demo quality. Examine Anthropic's existing webapp-testing skill to understand its limitations. Write findings to `docs/research/browser-testing.md` in the skills repo with front-matter. Update this plan with the chosen approach before proceeding to the next task.

- [ ] **Create `testing-browser` skill** — `skills/skills/testing-browser/` — (Approach TBD after research. Should be production-grade, not generic. Must enable agents to: start dev server, navigate pages, take screenshots, inspect DOM, capture console logs, verify UI behavior. Integrate with the looping-tasks VERIFY phase. Use `/creating-skills` workflow.)

### Phase 4: Housekeeping

- [ ] **Update skills repo README.md** — `skills/README.md` — Add new skills to the Available Skills table. Fix existing issues: `generating-changelogs` is missing from the table; `creating-sprites` description says "Gemini" but SKILL.md says "gpt-image-1.5" — update to match SKILL.md.

## Decision Log

| Decision | Reasoning |
|----------|-----------|
| No `reviewing-work` skill | Linters + hooks provide mechanical enforcement; a review skill is documentation-only enforcement, which the article explicitly says doesn't scale |
| No `testing-strategy` skill | Agents already handle test decisions well; project-specific testing needs belong in CLAUDE.md, not a generic skill |
| No `cleaning-up` skill | Article's solution was encoding cleanup as automated linter rules, not periodic manual scans. The manual Friday cleanup approach is what they moved away from |
| No `golden-principles.md` | Project-specific quality standards belong in each project's CLAUDE.md, not in a skill |
| Linter hooks over review checklists | The article's core insight: mechanical enforcement beats documentation-only rules. Hooks run automatically on every edit; skills rely on the agent remembering to invoke them |
| Browser testing as custom skill | Existing marketplace options (including Anthropic's) are too generic for production use. No MCP dependency — we want a self-contained, production-grade skill |
| Global CLAUDE.md changes out of scope | Lives in a different repo (dotfiles); useful additions noted but not tracked here |

## Issues Found

<!-- Bugs or problems discovered during implementation -->
- `generating-changelogs` missing from README.md Available Skills table
- README says `creating-sprites` uses "Gemini" but SKILL.md says "gpt-image-1.5"
