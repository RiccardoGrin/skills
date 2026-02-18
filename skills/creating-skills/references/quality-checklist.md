# Quality Checklist

Pre-ship validation checklist for skills. Score each item: Yes = 1, No = 0, N/A = exclude from total.

**Pass threshold**: Score ≥ 80% of applicable items.
**Automatic fail**: Any item marked with ⛔ that scores No.

## Structure & Format

| # | Check | ⛔ |
|---|-------|----|
| 1 | SKILL.md exists in the skill directory | ⛔ |
| 2 | SKILL.md starts with valid YAML frontmatter (`---` delimiters) | ⛔ |
| 3 | Frontmatter contains only spec-allowed keys (`name`, `description`, `version`, `license`, `compatibility`, `metadata`, `allowed-tools`) | ⛔ |
| 4 | `name` is kebab-case and matches directory name | ⛔ |
| 5 | `description` is under 1024 characters (recommend under 300) | ⛔ |
| 6 | `description` uses third-person voice | |
| 7 | `description` includes "Use when" triggers | |
| 8 | `description` does not end with a period | |
| 9 | `name` uses gerund form (e.g., `creating-skills`) | |
| 10 | SKILL.md body is under 500 lines | ⛔ |
| 11 | SKILL.md body is in the 150–300 line sweet spot | |
| 12 | No Windows-style backslash paths anywhere | ⛔ |

## Reference Files

| # | Check | ⛔ |
|---|-------|----|
| 13 | All reference files are in `references/` (one level deep) | ⛔ |
| 14 | Every reference file is listed in the SKILL.md body | |
| 15 | Referenced files actually exist on disk | ⛔ |
| 16 | Files over 100 lines have a table of contents | |
| 17 | No auxiliary files (README.md, CHANGELOG.md) in skill directory | |

## Content Quality

| # | Check | ⛔ |
|---|-------|----|
| 18 | Body uses progressive disclosure (details in reference files) | |
| 19 | "When to use" info is in the description, not the body | |
| 20 | Terminology is consistent throughout | |
| 21 | No time-sensitive claims ("as of 2024", specific versions) | |
| 22 | Code blocks have language tags | |
| 23 | No TODO markers remain | |
| 24 | MCP tool references use `ServerName:tool_name` format | |

## Scripts & Automation

| # | Check | ⛔ |
|---|-------|----|
| 25 | Scripts use only the standard library (no pip/npm installs) | ⛔ |
| 26 | Scripts work cross-platform (no `chmod`, no OS-specific paths) | |
| 27 | Scripts have usage instructions in docstring or `--help` | |

## Testing & Evaluation

| # | Check | ⛔ |
|---|-------|----|
| 28 | Tested with a real task (not just reading the skill) | |
| 29 | Tested with at least two model tiers (e.g., Haiku + Sonnet) | |
| 30 | Validator passes with no errors | ⛔ |
| 31 | Skill activates when triggered by natural language prompts | |
| 32 | Output quality matches expectations for the task | |

## Token Efficiency

| # | Check | ⛔ |
|---|-------|----|
| 33 | No information that Claude already knows (common language syntax, well-known APIs) | |
| 34 | Reference files are loaded conditionally, not all at once | |
| 35 | Examples are concise (2–4 per section, not exhaustive lists) | |

## Scoring

```
Applicable items = Total items - N/A items
Score = Yes items / Applicable items × 100

Pass: Score ≥ 80% AND no ⛔ items scored No
Fail: Score < 80% OR any ⛔ item scored No
```
