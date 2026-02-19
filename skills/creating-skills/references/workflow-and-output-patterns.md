# Workflow and Output Patterns

## Table of Contents

- [Workflow Patterns](#workflow-patterns)
  - [Sequential Workflow](#sequential-workflow)
  - [Conditional Workflow](#conditional-workflow)
  - [Feedback Loop](#feedback-loop)
  - [Plan-Validate-Execute](#plan-validate-execute)
- [Output Patterns](#output-patterns)
  - [Template Pattern](#template-pattern)
  - [Examples Pattern](#examples-pattern)
  - [Verifiable Intermediate Outputs](#verifiable-intermediate-outputs)
- [Combining Patterns](#combining-patterns)
- [Concrete Examples](#concrete-examples)

## Workflow Patterns

### Sequential Workflow

Steps that must be completed in order. Use copyable checklists so the agent can track progress.

```markdown
## Workflow

- [ ] **Step 1: Gather requirements**
  Ask the user what they need. Clarify constraints.

- [ ] **Step 2: Analyze existing code**
  Read relevant files. Identify patterns.

- [ ] **Step 3: Implement changes**
  Write the code. Follow project conventions.

- [ ] **Step 4: Validate**
  Run tests. Check for regressions.
```

**When to use**: Most guided workflows. Steps depend on prior steps.

**Tips**:
- Bold the step name for scannability
- Add a one-line description under each step
- Keep to 5–8 steps maximum (merge or split if needed)
- Use sub-steps sparingly — prefer reference files for detail

### Conditional Workflow

Branches based on conditions. Use decision tables or if/then blocks.

```markdown
## Choose Your Approach

| Condition | Action |
|-----------|--------|
| Project uses TypeScript | Follow the TypeScript path below |
| Project uses JavaScript | Follow the JavaScript path below |
| Unsure | Check for `tsconfig.json` — if present, use TypeScript path |

### TypeScript Path
1. Step specific to TypeScript
2. Next step

### JavaScript Path
1. Step specific to JavaScript
2. Next step
```

**When to use**: The workflow branches based on project type, user preference, or detected conditions.

**Tips**:
- Put the decision table at the top so the agent can route quickly
- Provide a default/fallback for ambiguous cases
- Keep branches short — shared steps should be in a common section

### Feedback Loop

Iterative cycle: run → check → fix → repeat. Essential for validation workflows.

```markdown
## Validation Loop

1. Run the validator: `python scripts/validate_skill.py <skill-dir>`
2. Review the output:
   - **No errors**: Proceed to the next step
   - **Errors found**: Fix each error, then re-run from step 1
   - **Warnings only**: Review each warning — fix or acknowledge, then proceed
3. Maximum 3 iterations — if still failing, ask the user for guidance
```

**When to use**: Validation, linting, build processes — anything where the first pass rarely succeeds.

**Tips**:
- Set a maximum iteration count to prevent infinite loops
- Distinguish between blocking errors and advisory warnings
- Provide an escape hatch (ask user) for persistent failures

### Plan-Validate-Execute

Three-phase pattern: plan what to do, validate the plan, then execute.

```markdown
## Approach

### Phase 1: Plan
1. Read all relevant files
2. List the changes needed
3. Present the plan to the user for approval

### Phase 2: Validate
1. Check that the plan is feasible (files exist, no conflicts)
2. Identify risks or side effects
3. Get user confirmation

### Phase 3: Execute
1. Implement the changes in order
2. Run tests after each change
3. Report results
```

**When to use**: High-impact changes (refactoring, migrations, deletions) where mistakes are costly.

**Tips**:
- Always get user confirmation before the execute phase
- The plan should be specific enough to be reviewable
- Include rollback guidance if execution fails partway through

## Output Patterns

### Template Pattern

Define a strict output format that the agent must follow. Use fenced code blocks with placeholders.

**Strict template** (agent fills in placeholders):
```markdown
## Output Format

Generate the following file:

\```yaml
name: {{skill-name}}
description: {{description}}
version: {{version}}
\```

Rules:
- `{{skill-name}}` must be kebab-case
- `{{description}}` must be under 300 characters
- `{{version}}` follows semver (e.g., 1.0.0)
```

**Flexible template** (agent adapts structure):
```markdown
## Output Format

Generate a summary with these sections:
- **Overview**: 2–3 sentences describing what was done
- **Changes**: Bulleted list of files modified
- **Risks**: Any potential issues (or "None identified")
```

**When to use**: The output must conform to a specific format (config files, API responses, reports).

### Examples Pattern

Show input/output pairs so the agent learns by example.

```markdown
## Examples

**Input**: "Create a skill for reviewing pull requests"
**Output**:
- Name: `reviewing-pull-requests`
- Pattern: Rules-Based Audit
- Key rules: diff size, test coverage, naming conventions

**Input**: "Create a skill for generating API documentation"
**Output**:
- Name: `generating-api-docs`
- Pattern: Scaffolding / Generation
- Key outputs: OpenAPI spec, endpoint summary, example requests
```

**When to use**: The mapping from input to output is easier to show than to describe in rules.

**Tips**:
- Include 2–4 examples covering different cases
- Show both typical and edge cases
- Keep examples concise — they add to token count

### Verifiable Intermediate Outputs

Produce checkable artifacts at each stage, not just at the end.

```markdown
## Workflow with Checkpoints

- [ ] **Step 1: Analyze** → Output: list of files to modify (show to user)
- [ ] **Step 2: Plan** → Output: change description for each file (show to user)
- [ ] **Step 3: Implement** → Output: modified files (run tests)
- [ ] **Step 4: Verify** → Output: test results + diff summary
```

**When to use**: Complex multi-step tasks where catching errors early saves significant rework.

**Tips**:
- Each checkpoint should produce something the user or a script can verify
- Don't wait until the end to surface problems
- Pair with the feedback loop pattern for validation checkpoints

## Combining Patterns

Most real skills combine multiple patterns. Common combinations:

| Primary | Secondary | Example |
|---------|-----------|---------|
| Sequential Workflow | Feedback Loop | Build → validate → fix → retry |
| Sequential Workflow | Template Pattern | Follow steps, produce formatted output |
| Conditional Workflow | Examples Pattern | Branch based on type, show examples per branch |
| Plan-Validate-Execute | Verifiable Outputs | Plan with checkpoints at each phase |

When combining, use the primary pattern for the overall structure and embed secondary patterns within individual steps.

## Concrete Examples

### Research Synthesis (Sequential + Template)

A non-code skill that gathers information and produces a structured summary:

```markdown
## Workflow

- [ ] **Step 1: Define the research question**
  Ask the user what they want to understand. Identify 2–3 sub-questions.

- [ ] **Step 2: Gather sources**
  Search the codebase, docs, and external references. Collect key findings.

- [ ] **Step 3: Synthesize**
  Produce the summary using this format:

  ## Research Summary: {{topic}}

  ### Key Findings
  - Finding 1 (source: ...)
  - Finding 2 (source: ...)

  ### Recommendations
  1. Recommendation with rationale
  2. Recommendation with rationale

  ### Open Questions
  - What remains unclear
```

### PDF Form Filling (Conditional + Scaffolding)

A code skill that fills PDF forms from structured data:

```markdown
## Choose Your Approach

| Signal | Action |
|--------|--------|
| User provides JSON data | Map fields directly |
| User provides CSV | Convert to JSON first, then map |
| User describes fields verbally | Generate JSON schema, confirm, then fill |

## Generation Workflow

1. Read the PDF form to identify field names
2. Map input data to form fields
3. Run: `python scripts/fill_pdf.py --template assets/form.pdf --data input.json`
4. Validate: open the output PDF and verify all fields are filled
5. Report any unmapped fields as warnings
```
