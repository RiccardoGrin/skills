# Anti-Patterns

Common mistakes when authoring skills. Avoid these.

## Table of Contents

- [Over-Explaining](#over-explaining)
- [Windows-Style Paths](#windows-style-paths)
- [Deeply Nested References](#deeply-nested-references)
- [Too Many Options Without a Default](#too-many-options-without-a-default)
- [Time-Sensitive Information](#time-sensitive-information)
- [Inconsistent Terminology](#inconsistent-terminology)
- [Wrong Voice in Description](#wrong-voice-in-description)
- ["When to Use" in Body](#when-to-use-in-body)
- [Auxiliary Docs in Skill Directory](#auxiliary-docs-in-skill-directory)
- [Unlisted Reference Files](#unlisted-reference-files)
- [Over-Engineering](#over-engineering)
- [Under-Specifying Critical Operations](#under-specifying-critical-operations)

## Over-Explaining

**Problem**: Adding information that Claude already knows — common language syntax, well-known API behavior, basic programming concepts.

**Fix**: Only include domain-specific knowledge, project conventions, or non-obvious constraints. If it's in Claude's training data, don't repeat it.

```markdown
<!-- Bad: Claude knows how to write Python -->
## How to Write Python Functions
Use `def` to define a function. Use `return` to return a value.

<!-- Good: Project-specific convention Claude wouldn't know -->
## Function Naming
All handler functions must be prefixed with `handle_` and accept `ctx` as the first argument.
```

## Windows-Style Paths

**Problem**: Using backslash paths (`references\format.md`) that break on Unix systems and confuse agents.

**Fix**: Always use forward slashes: `references/format.md`.

## Deeply Nested References

**Problem**: Reference directories more than one level deep (`references/patterns/advanced/templates.md`).

**Fix**: Keep references flat — one level under `references/`. Use longer file names if needed: `references/advanced-template-patterns.md`.

## Too Many Options Without a Default

**Problem**: Presenting multiple choices without recommending one, forcing the agent to guess.

**Fix**: Always indicate a default or recommended option.

```markdown
<!-- Bad -->
Choose a database: PostgreSQL, MySQL, SQLite, MongoDB

<!-- Good -->
Choose a database:
- **PostgreSQL** (recommended for most projects)
- MySQL — if the team already uses it
- SQLite — for local development or small projects
```

## Time-Sensitive Information

**Problem**: Including version numbers, dates, or claims that will age ("as of 2024", "the latest version is 3.2").

**Fix**: Use evergreen phrasing or link to authoritative sources.

```markdown
<!-- Bad -->
As of January 2025, the recommended Node.js version is 20.x.

<!-- Good -->
Use the current LTS version of Node.js (check nodejs.org for the latest).
```

## Inconsistent Terminology

**Problem**: Using different words for the same concept ("skill" vs "plugin" vs "extension" vs "rule").

**Fix**: Pick one term in the frontmatter and use it consistently throughout.

## Wrong Voice in Description

**Problem**: Using imperative voice ("Create skills") or second-person ("Helps you create") in the frontmatter description.

**Fix**: Use third-person declarative: "Guides creation of..." or "Enforces naming conventions across...".

```markdown
<!-- Bad -->
description: Create agent skills following best practices
description: Help you build and validate skills

<!-- Good -->
description: Guides creation of agent skills following best practices
description: Enforces naming conventions across TypeScript codebases
```

## "When to Use" in Body

**Problem**: Putting trigger/activation context in the SKILL.md body instead of the description.

**Fix**: The description's "Use when" clause is what agents match against. Body content is only read after activation.

## Auxiliary Docs in Skill Directory

**Problem**: Adding `README.md`, `CHANGELOG.md`, or `CONTRIBUTING.md` inside the skill directory.

**Fix**: The SKILL.md is the only documentation needed. Repository-level docs go in the repo root.

## Unlisted Reference Files

**Problem**: Having reference files in `references/` that aren't mentioned in the SKILL.md body.

**Fix**: Every reference file must be listed in the "Reference Files" table with a "Read When" condition. If a file isn't worth listing, it shouldn't exist.

## Over-Engineering

**Problem**: Adding unnecessary complexity — magic numbers, premature abstractions, feature flags, excessive configuration.

**Fix**: Keep it minimal. Three similar lines of code are better than a premature abstraction. Only add complexity when the current task demands it.

```markdown
<!-- Bad: Premature abstraction -->
Configure the validation threshold in `config/thresholds.yaml`
Override per-environment in `config/thresholds.{env}.yaml`
Set feature flags in `config/features.json`

<!-- Good: Direct and simple -->
The validator fails if the body exceeds 500 lines.
```

## Under-Specifying Critical Operations

**Problem**: Being vague about operations that have significant consequences (file deletion, API calls, database changes).

**Fix**: Be explicit about what happens, what gets modified, and what the rollback path is.

```markdown
<!-- Bad -->
Clean up the old files.

<!-- Good -->
Delete files matching `*.tmp` in the `build/` directory. This does not affect source files.
```
