# Skill Patterns

## Table of Contents

- [Pattern Overview](#pattern-overview)
- [Pattern 1: Guided Workflow](#pattern-1-guided-workflow)
- [Pattern 2: Rules-Based Audit](#pattern-2-rules-based-audit)
- [Pattern 3: Scaffolding / Generation](#pattern-3-scaffolding--generation)
- [Pattern 4: Knowledge Reference](#pattern-4-knowledge-reference)
- [Choosing a Pattern](#choosing-a-pattern)

## Pattern Overview

| Pattern | Lines | Best For | Example |
|---------|-------|----------|---------|
| Guided Workflow | 200–300 | Multi-step processes with decisions | `creating-skills`, `deploying-apps` |
| Rules-Based Audit | 100–200 | Code review, linting, compliance | `reviewing-typescript`, `auditing-security` |
| Scaffolding / Generation | 150–250 | Creating files from templates | `generating-apis`, `initializing-projects` |
| Knowledge Reference | 80–150 | Lookup tables, conventions, mappings | `mapping-status-codes`, `converting-units` |

## Pattern 1: Guided Workflow

For multi-step processes where the agent makes decisions at each stage.

**When to use**: The task has sequential steps, conditional branches, or requires user interaction.

**Directory structure**:
```
skills/<skill-name>/
├── SKILL.md
├── references/
│   ├── detailed-steps.md
│   └── examples.md
└── scripts/
    └── helper.py
```

**SKILL.md skeleton**:
```markdown
---
name: doing-something
description: Guides [process] for [domain]. Covers [what]. Use when [triggers]
---

# Doing Something

## Reference Files

| File | Read When |
|------|-----------|
| `references/detailed-steps.md` | Need detailed guidance for a specific step |
| `references/examples.md` | Need real-world examples |

## Workflow

- [ ] **Step 1: Understand the goal**
  Ask the user what they want to achieve. Clarify scope and constraints.

- [ ] **Step 2: Gather inputs**
  Identify required information. Read relevant files.

- [ ] **Step 3: Execute**
  Perform the main task. Use scripts if available.

- [ ] **Step 4: Validate**
  Check the output against requirements.

- [ ] **Step 5: Iterate**
  Refine based on feedback.

## Quick Reference

Key decision points and common options.
```

**Real-world examples**: `creating-skills`, `deploying-to-production`, `migrating-databases`

## Pattern 2: Rules-Based Audit

For checking code or content against a set of rules.

**When to use**: The task is about reviewing, validating, or enforcing standards.

**Directory structure**:
```
skills/<skill-name>/
├── SKILL.md
└── references/
    ├── rules.md
    └── examples.md
```

**SKILL.md skeleton**:
```markdown
---
name: reviewing-something
description: Enforces [standard] across [scope]. Checks [what]. Use when [triggers]
---

# Reviewing Something

## Reference Files

| File | Read When |
|------|-----------|
| `references/rules.md` | Need the full rule set with rationale |
| `references/examples.md` | Need good/bad examples for a specific rule |

## Rules Summary

### Category A
1. **Rule name** — One-line description
2. **Rule name** — One-line description

### Category B
1. **Rule name** — One-line description

## Review Workflow

1. Read the target files
2. Check each rule category
3. Report findings with severity (error/warning/info)
4. Suggest fixes for each finding

## Output Format

| File | Line | Severity | Rule | Finding |
|------|------|----------|------|---------|
```

**Real-world examples**: `reviewing-typescript`, `auditing-accessibility`, `checking-api-contracts`

## Pattern 3: Scaffolding / Generation

For creating files, projects, or code from templates.

**When to use**: The task produces one or more files from a template or specification.

**Directory structure**:
```
skills/<skill-name>/
├── SKILL.md
├── references/
│   └── templates.md
└── scripts/
    └── scaffold.py
```

**SKILL.md skeleton**:
```markdown
---
name: generating-something
description: Generates [output] from [input/spec]. Covers [what]. Use when [triggers]
---

# Generating Something

## Reference Files

| File | Read When |
|------|-----------|
| `references/templates.md` | Need template examples or customization options |

## What Gets Generated

| File | Purpose |
|------|---------|
| `output/file.ext` | Description |

## Generation Workflow

1. Gather requirements from user
2. Select appropriate template
3. Run scaffold script: `python scripts/scaffold.py <args>`
4. Customize generated files
5. Validate output

## Customization Options

| Option | Default | Description |
|--------|---------|-------------|
```

**Real-world examples**: `generating-apis`, `initializing-projects`, `creating-components`

## Pattern 4: Knowledge Reference

For lookup tables, mappings, and encyclopedic content.

**When to use**: The task is primarily about providing information, not performing actions.

**Directory structure**:
```
skills/<skill-name>/
├── SKILL.md
└── references/
    └── detailed-tables.md
```

**SKILL.md skeleton**:
```markdown
---
name: mapping-something
description: Provides [mapping/reference] for [domain]. Covers [what]. Use when [triggers]
---

# Mapping Something

## Reference Files

| File | Read When |
|------|-----------|
| `references/detailed-tables.md` | Need the full reference with all entries |

## Quick Reference

| Input | Output | Notes |
|-------|--------|-------|
| Common case 1 | Result | |
| Common case 2 | Result | |

## Usage

How to apply this reference in practice.
```

**Real-world examples**: `mapping-status-codes`, `converting-units`, `translating-error-codes`

## Choosing a Pattern

Ask these questions:

1. **Does the task have sequential steps?** → Guided Workflow
2. **Is the task about checking/validating?** → Rules-Based Audit
3. **Does it produce files from templates?** → Scaffolding / Generation
4. **Is it primarily informational?** → Knowledge Reference

If the task spans multiple patterns, use the **primary** pattern and incorporate elements from others.
For example, a `creating-skills` skill uses Guided Workflow as the primary pattern but includes Rules-Based Audit elements (validation checklist) and Scaffolding elements (init script).
