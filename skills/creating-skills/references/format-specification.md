# Format Specification

## Table of Contents

- [Directory Structure](#directory-structure)
- [SKILL.md Format](#skillmd-format)
- [Frontmatter](#frontmatter)
- [Body](#body)
- [Reference Files](#reference-files)
- [Naming Conventions](#naming-conventions)
- [Scripts](#scripts)
- [Content Guidelines](#content-guidelines)
- [License](#license)

## Directory Structure

Every skill lives in its own directory under `skills/`:

```
skills/<skill-name>/
├── SKILL.md              ← required entry point
├── references/           ← supporting docs (optional)
│   ├── format-spec.md
│   └── patterns.md
├── scripts/              ← helper scripts (optional)
│   └── validate.py
└── assets/               ← files used in output (optional)
    ├── template.html
    └── icon.png
```

- `SKILL.md` is the only required file
- `references/` must be one level deep only (no nesting)
- `assets/` holds files used in output (templates, images, icons) — these are NOT loaded into context automatically, only referenced when needed by scripts or the agent
- No auxiliary files (`README.md`, `CHANGELOG.md`) inside the skill directory

## SKILL.md Format

### Frontmatter

Frontmatter is **required** and must be the first thing in the file:

```yaml
---
name: creating-skills
description: Guides creation of agent skills following best practices and the open format specification. Covers pattern selection, frontmatter, directory structure, reference files, validation, and iteration. Use when creating a new skill, updating SKILL.md, or asking "how to write a skill"
version: 1.0.0
---
```

**Allowed keys**: `name` (required), `description` (required), `version` (optional), `license` (optional), `compatibility` (optional), `metadata` (optional), `allowed-tools` (optional)

**Name rules**:
- kebab-case only: `[a-z][a-z0-9]*(-[a-z0-9]+)*`
- Maximum 64 characters
- Must match the directory name exactly
- Prefer gerund form for the first word
- Must not contain XML angle brackets (`<`, `>`)
- Must not contain reserved words: `anthropic`, `claude`, `openai`, `cursor`

| Good | Avoid |
|------|-------|
| `creating-skills` | `skill-creator` |
| `analyzing-data` | `data-analyzer` |
| `processing-pdfs` | `pdf-processor` |
| `reviewing-code` | `code-review` |

**Description rules**:
- Third-person voice ("Guides..." not "Guide...")
- No trailing period
- Must not contain XML angle brackets (`<`, `>`)
- Recommended under 300 characters for readability. Spec maximum: 1024
- Formula: `[Does what] for/using [domain]. [Checks/covers what]. Use when [triggers]`

**Description examples**:

```
Guides creation of agent skills following best practices and the open format specification. Covers pattern selection, frontmatter, directory structure, reference files, validation, and iteration. Use when creating a new skill, updating SKILL.md, or asking "how to write a skill"
```

```
Enforces TypeScript naming conventions and import ordering across a codebase. Checks barrel exports, type-only imports, and path aliases. Use when reviewing TypeScript, setting up linting rules, or fixing import errors
```

```
Generates and validates OpenAPI specifications from existing route handlers. Covers path parameters, request bodies, and response schemas. Use when documenting an API, generating client SDKs, or validating endpoint contracts
```

### Body

- Target: **150–300 lines**
- Hard limit: **500 lines** (agents lose focus beyond this)
- Use ATX headings (`#`, `##`, `###`)
- One sentence per line for clean diffs
- Fenced code blocks with language tags
- No "when to use" info in the body — that belongs in the description

### MCP Tool References

When referencing MCP tools, use the format: `ServerName:tool_name`

```
Run `GitHub:create_pull_request` to open the PR.
```

## Reference Files

Skills use a three-level progressive disclosure model:

1. **Metadata** (~100 words: name + description) — always loaded by the agent for matching
2. **SKILL.md body** (150–300 lines) — loaded when the skill is triggered
3. **Reference files** (unlimited) — loaded on demand when specific conditions are met

This layered design keeps context window usage minimal while making detailed guidance available when needed.

- Place in `references/` subdirectory
- One level deep only — no nested directories
- Every reference file must be listed in the SKILL.md body
- Use a "Reference Files" table with conditional loading:

```markdown
| File | Read When |
|------|-----------|
| `references/format-specification.md` | Checking format rules or frontmatter constraints |
| `references/skill-patterns.md` | Choosing a skill pattern or viewing skeleton templates |
```

- Files over 100 lines should include a table of contents at the top

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Skill name | kebab-case, gerund preferred | `creating-skills` |
| Skill directory | matches name exactly | `skills/creating-skills/` |
| Markdown files | kebab-case | `format-specification.md` |
| Python scripts | snake_case | `validate_skill.py` |
| Paths in content | forward slashes only | `references/patterns.md` |

## Scripts

- Scripts live in the `scripts/` subdirectory
- Must use only the language's standard library (no external dependencies)
- Scripts can be **executed without being loaded into context**, saving tokens — prefer scripts for validation, scaffolding, and other automatable tasks
- Must work cross-platform (no `chmod`, no OS-specific paths)
- Include usage instructions via docstring or `--help`

## Content Guidelines

- **No time-sensitive information**: Avoid "as of 2024" or version-specific claims that will age
- **Consistent terminology**: Pick one term and stick with it (e.g., "skill" not "plugin/extension/rule")
- **Forward slashes only**: Never use backslash paths, even in Windows examples
- **No external dependencies**: Scripts must use only the language's standard library
- **Content freshness**: Prefer linking to authoritative sources over duplicating information that changes

## License

If your skill has specific licensing requirements, include a `LICENSE.txt` in the skill directory and reference it in the frontmatter:

```yaml
---
name: my-skill
description: ...
license: MIT
---
```

For most skills in a shared repository, the repository-level LICENSE applies and no per-skill license file is needed.
