---
name: creating-skills
description: Guides creation of agent skills following best practices and the open format specification. Covers pattern selection, frontmatter, directory layout, reference files, validation, and iteration. Use when creating a new skill, updating SKILL.md, or asking "how to write a skill"
---

# Creating Skills

This skill walks you through creating a well-structured agent skill from scratch.
Follow the workflow below step by step. Use the reference files for detailed guidance on specific topics.

## Reference Files

| File | Read When |
|------|-----------|
| `references/format-specification.md` | Checking format rules, frontmatter constraints, or naming conventions |
| `references/skill-patterns.md` | Choosing a skill pattern or viewing skeleton templates |
| `references/workflow-and-output-patterns.md` | Designing workflows, output formats, or feedback loops |
| `references/quality-checklist.md` | Running the pre-ship quality checklist |
| `references/anti-patterns.md` | Reviewing common mistakes to avoid |

## Choose a Skill Pattern

Before writing anything, identify which pattern fits the task:

| Pattern | Best For | Example |
|---------|----------|---------|
| **Guided Workflow** | Multi-step processes with decisions | `creating-skills`, `deploying-apps` |
| **Rules-Based Audit** | Code review, linting, compliance | `reviewing-typescript`, `auditing-security` |
| **Scaffolding / Generation** | Creating files from templates | `generating-apis`, `initializing-projects` |
| **Knowledge Reference** | Lookup tables, conventions, mappings | `mapping-status-codes`, `converting-units` |

**Not sure?** Ask these questions:
1. Does the task have sequential steps? → Guided Workflow
2. Is it about checking/validating? → Rules-Based Audit
3. Does it produce files from templates? → Scaffolding / Generation
4. Is it primarily informational? → Knowledge Reference

Read `references/skill-patterns.md` for full skeleton templates and directory structures.

## Creation Workflow

Copy this checklist and work through it step by step:

```
- [ ] Step 1: Understand the skill
- [ ] Step 2: Choose a pattern
- [ ] Step 3: Initialize the skill
- [ ] Step 4: Write the SKILL.md body
- [ ] Step 5: Add reference files
- [ ] Step 6: Validate
- [ ] Step 7: Test with real usage
- [ ] Step 8: Iterate
```

### Step 1: Understand the Skill

Before writing any files, have a conversation to clarify:

- **What does this skill do?** Get a one-sentence answer.
- **Who triggers it?** What prompts or situations should activate it?
- **What's the output?** Files created, code reviewed, information provided?
- **What does the agent need to know?** Domain knowledge, project conventions, constraints?
- **What does the agent already know?** Don't include common programming knowledge.

Synthesize into a draft description using the formula:
`[Does what] for/using [domain]. [Checks/covers what]. Use when [triggers]`

### Step 2: Choose a Pattern

Use the decision table above to select a primary pattern.
Most skills combine patterns — pick the dominant one and incorporate elements from others.

For example, `creating-skills` is primarily a Guided Workflow but includes:
- Rules-Based Audit elements (validation checklist)
- Scaffolding elements (init script)

### Step 3: Initialize the Skill

Run the scaffolding script to create the directory structure:

```bash
python scripts/init_skill.py <skill-name> --path skills
```

This creates:
```
skills/<skill-name>/
├── SKILL.md          (template with TODOs)
└── references/       (empty, ready for use)
```

If not using the script, create this structure manually. The name must be kebab-case, preferably with a gerund first word (e.g., `analyzing-data`, not `data-analyzer`).

### Step 4: Write the SKILL.md Body

Open the generated `SKILL.md` and fill it in:

1. **Frontmatter**: Fill in `name` and `description`
   - Name: kebab-case, must match directory name
   - Description: third-person voice, under 300 characters, include "Use when" triggers
   - See `references/format-specification.md` for the full spec

2. **Reference Files table**: List every reference file with a "Read When" condition

3. **Main content**: Follow the skeleton for your chosen pattern
   - Target 150–300 lines for the body
   - Hard limit: 500 lines (agents lose focus beyond this)
   - Use progressive disclosure — put detailed content in reference files
   - Use ATX headings, fenced code blocks with language tags
   - One sentence per line for clean diffs

4. **Workflows**: Use copyable checklists for sequential steps
   - See `references/workflow-and-output-patterns.md` for patterns

### Step 5: Add Reference Files

Create reference files in `references/` for detailed content that would bloat the main SKILL.md.

Common reference file types:
- **Rules and specifications** — naming conventions, format constraints, allowed values
- **Examples** — input/output pairs, good/bad comparisons
- **Detailed step guides** — expanded instructions for complex steps
- **Decision matrices** — comparison tables for choosing between options

Rules for reference files:
- One level deep only (no nested directories under `references/`)
- Every file must be listed in the SKILL.md "Reference Files" table
- Files over 100 lines should include a table of contents
- Use kebab-case file names

### Step 6: Validate

Run the validator against your skill:

```bash
python scripts/validate_skill.py skills/<skill-name>
```

The validator checks:
- Frontmatter format and required fields
- Name matches directory, kebab-case format
- Description length and voice
- Body line count
- File references exist on disk
- No Windows-style paths
- No deeply nested references
- Reference files are listed in the body

**Fix all errors** (blocking). **Review all warnings** (advisory — fix or acknowledge).

If errors persist after 3 attempts, review `references/anti-patterns.md` for common mistakes.

Also run through the manual `references/quality-checklist.md` for items the automated validator cannot check (content quality, token efficiency, terminology consistency).

### Step 7: Test with Real Usage

Automated validation catches format issues but not usability problems. Test with real tasks:

1. **Install the skill**: Copy to `~/.claude/skills/` or use `npx skills add`
2. **Start a fresh session**: The agent should not have prior context about this skill
3. **Trigger naturally**: Use a prompt that would naturally activate the skill
4. **Evaluate the output**: Did the agent follow the workflow? Was the output correct?

**Multi-model testing**: Test with at least two capability levels:
- **Haiku**: Can the skill work with a smaller model? Simplify if not.
- **Sonnet/Opus**: Does the skill produce high-quality output with a capable model?

If the skill fails or produces poor output, go back to Step 4 and revise.

### Step 8: Iterate

Skills improve through real usage and feedback. Use the Claude A/B pattern:

1. **Claude A**: Use the skill as-is with a real task. Note where it struggles.
2. **Claude B**: Open a new session. Describe the problems. Ask Claude B to suggest improvements to the SKILL.md.
3. **Apply and re-test**: Incorporate the suggestions, then repeat from Step 6.

This external feedback loop catches blind spots that self-review misses.

## Anti-Patterns Quick Reference

Avoid these common mistakes (see `references/anti-patterns.md` for full details):

| Anti-Pattern | Fix |
|-------------|-----|
| Over-explaining (things Claude already knows) | Only include domain-specific or non-obvious info |
| Windows-style backslash paths | Always use forward slashes |
| Deeply nested references | Keep `references/` one level deep |
| Too many options without a default | Always recommend a default |
| "When to use" in body instead of description | Put triggers in the frontmatter `description` |
| Unlisted reference files | List every file in the Reference Files table |
| Time-sensitive claims | Use evergreen phrasing or link to sources |
| Wrong voice in description | Use third-person: "Guides..." not "Guide..." |

## Related Skills

When using this skill alongside others:

- After creating a skill, use a **reviewing** skill to audit it against project standards
- For skills that generate code, pair with a **testing** skill to validate output
- For API-related skills, consider a **documenting** skill for endpoint coverage
