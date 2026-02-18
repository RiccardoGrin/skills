# AGENTS.md

> This file and CLAUDE.md should be kept in sync. If you edit one, update the other.

## Project Overview

This is a **content-only** repository of reusable agent skills. No package.json — skills are installed via `npx skills add <username>/skills`. The CLI scans for `SKILL.md` files inside `skills/` directories.

## Project Structure

```
skills/                          ← repo root
├── AGENTS.md                    ← you are here
├── CLAUDE.md                    ← copy of AGENTS.md (keep in sync)
├── README.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md             ← required entry point
        ├── references/          ← supporting docs loaded on demand
        └── scripts/             ← helper scripts (optional)
```

## Coding Style & Naming Conventions

- **Skill names**: kebab-case, prefer gerund form (`creating-skills`, `analyzing-data`, not `skill-creator`, `data-analyzer`)
- **File names**: kebab-case for markdown, snake_case for Python scripts
- **Markdown**: ATX headings (`#`), one sentence per line in body text, fenced code blocks with language tag
- **Python**: Standard library only — no external dependencies. Compatible with Python 3.8+.
- **Paths**: Always use forward slashes, even in examples. Never use backslash paths.

## Skill Authoring Rules

### Frontmatter (required)

- Must be the first thing in SKILL.md
- Allowed keys: `name` (required), `description` (required), `version` (optional), `license` (optional), `compatibility` (optional), `metadata` (optional), `allowed-tools` (optional)
- `name`: kebab-case, must match directory name
- `description`: Third-person voice, no period at end. Formula: `[Does what] for/using [domain]. [Checks/covers what]. Use when [triggers]`
- Recommend description under 300 characters for readability (spec maximum: 1024)

### Body Rules

- Target 150–300 lines for the main SKILL.md body
- Hard limit: 500 lines (agents lose focus beyond this)
- Use progressive disclosure: put details in reference files, link from body
- Every referenced file must be listed in a "Reference Files" table
- No "when to use" info in body — that belongs in the description
- No auxiliary docs (README, CHANGELOG) inside skill directories

### Reference Files

- Place in `references/` subdirectory (one level deep only)
- Files over 100 lines should include a table of contents
- Every reference file must be listed in the SKILL.md body
- Use conditional loading: "Read when [condition]"

## Testing Approach

- **Smoke test**: Install via `npx skills add` or manual copy to `~/.claude/skills/`
- **Validation**: Run `python skills/<skill-name>/scripts/validate_skill.py skills/<skill-name>` if a validator exists
- **Real usage test**: Start a new agent session and trigger the skill with a natural prompt
- **Multi-model**: Test with at least Haiku and Sonnet to verify the skill works across capability levels

## Gotchas

- Frontmatter is **required** — skills without it won't be indexed
- Reference files must be linked from the SKILL.md body or they won't be discovered
- The `npx skills` CLI reads from `skills/` directories specifically
- No package.json needed — this is a pure content repository
- Python scripts must use only the standard library (no pip installs)

## Commit & PR Guidelines

- Commit messages: imperative mood, ≤72 chars first line
- One skill per PR when adding new skills
- Run the validator before opening a PR
- PR description should include a real-usage test result

## Maintenance

- Periodically review skills against the latest best practices docs
- Keep reference files up to date when the format specification changes
- Archive deprecated skills by moving them to an `_archived/` directory
