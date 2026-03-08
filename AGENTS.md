# AGENTS.md

> CLAUDE.md is a symlink to this file. Edit AGENTS.md only — CLAUDE.md will stay in sync automatically.

## Overview

Content-only repository of reusable agent skills.
Skills installed via `npx skills add <username>/skills` or manual copy to `~/.claude/skills/`.
The CLI scans for SKILL.md files inside `skills/` directories.

## Do / Don't

- Do: use gerund-form kebab-case for skill names (`creating-skills`, not `skill-creator`)
- Do: use `/creating-skills` when authoring or modifying a skill — it covers the full workflow, format spec, and validation
- Do: one sentence per line in markdown body text (for clean diffs)
- Do: one skill per PR; include a real-usage test result in the PR description
- Do: update the Available Skills table in README.md when adding or removing a skill
- Don't: add external Python dependencies unless declared in SKILL.md with a `requirements.txt` in `scripts/`
- Don't: use backslash paths — always forward slashes

## Gotchas

- Frontmatter (`name`, `description`) is required — skills without it won't be indexed
- Reference files must be linked from SKILL.md body or they won't be discovered
- When renaming folders or reference files, grep all SKILL.md files for stale paths
