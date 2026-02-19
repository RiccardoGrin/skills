# Evaluation-Driven Development

## Table of Contents

- [Why Evaluations First](#why-evaluations-first)
- [The 5-Step Process](#the-5-step-process)
- [Evaluation Format](#evaluation-format)
- [Writing Good Evaluations](#writing-good-evaluations)
- [Iteration Cycle](#iteration-cycle)

## Why Evaluations First

The most effective skill development follows an evaluation-driven approach: define what success looks like **before** writing the skill.
This prevents the common trap of writing a skill that "feels complete" but doesn't actually improve agent behavior on real tasks.

Without evaluations, you're guessing at quality.
With evaluations, you can measure improvement objectively.

## The 5-Step Process

### 1. Identify the Gap

Complete the target task **without any skill** to establish a baseline.
Note where the agent struggles, makes mistakes, or produces suboptimal output.

```
- [ ] Run the task with a fresh agent session (no skill installed)
- [ ] Record the output quality, errors, and missed steps
- [ ] Document specific failure modes
```

### 2. Create Evaluations

Write 3–5 evaluation cases that cover:
- The **happy path** (straightforward, typical input)
- An **edge case** (unusual input, boundary condition)
- A **failure mode** you observed in the baseline

Each evaluation is a prompt + expected outcome pair.

### 3. Establish Baseline Scores

Run your evaluations against the agent **without** the skill.
Record scores using the rubric below.
This is your baseline — the skill must beat it.

### 4. Write Minimal Skill

Write the smallest possible SKILL.md that addresses the identified gaps.
Don't try to be comprehensive on the first pass.

### 5. Iterate Against Evaluations

Run evaluations after each change.
Stop when scores plateau or reach your target threshold.

## Evaluation Format

Store evaluations as JSON in a `tests/` directory (or inline in your testing notes):

```json
{
  "evaluations": [
    {
      "id": "eval-001",
      "name": "Basic skill creation",
      "prompt": "Create a new skill for reviewing Python code",
      "expected_behaviors": [
        "Chooses Rules-Based Audit pattern",
        "Creates valid frontmatter with gerund name",
        "Includes reference files table",
        "Runs validator before finishing"
      ],
      "scoring": {
        "method": "checklist",
        "pass_threshold": 3
      }
    },
    {
      "id": "eval-002",
      "name": "Edge case — ambiguous pattern",
      "prompt": "Create a skill that helps set up CI/CD pipelines",
      "expected_behaviors": [
        "Recognizes this could be Guided Workflow or Scaffolding",
        "Asks clarifying questions or picks primary pattern",
        "Explains pattern choice rationale"
      ],
      "scoring": {
        "method": "checklist",
        "pass_threshold": 2
      }
    }
  ]
}
```

## Writing Good Evaluations

**Do**:
- Test observable behaviors, not internal reasoning
- Include the exact prompt you'll use to trigger the skill
- Define pass/fail criteria before running the evaluation
- Cover different capability levels (test with Haiku and Sonnet)

**Don't**:
- Write evaluations that require subjective judgment ("output is good")
- Test only the happy path
- Create evaluations after writing the skill (confirmation bias)
- Use vague expected behaviors ("handles edge cases well")

**Scoring methods**:

| Method | Use When |
|--------|----------|
| **Checklist** | Expected behaviors are discrete, observable steps |
| **Rubric** (1–5 scale) | Output quality is on a spectrum |
| **Diff comparison** | Output should match a reference closely |

## Iteration Cycle

```
┌─────────────────────────────────────┐
│  1. Run evaluations                 │
│  2. Identify lowest-scoring areas   │
│  3. Make targeted SKILL.md edits    │
│  4. Re-run evaluations              │
│  5. Compare to previous scores      │
│  └── Improved? → Continue           │
│      Plateaued? → Ship it           │
│      Regressed? → Revert and retry  │
└─────────────────────────────────────┘
```

Track scores over iterations to see trends:

| Iteration | eval-001 | eval-002 | eval-003 | Notes |
|-----------|----------|----------|----------|-------|
| Baseline (no skill) | 1/4 | 0/3 | 1/3 | Agent misses pattern selection |
| v1 | 3/4 | 2/3 | 2/3 | Added pattern decision table |
| v2 | 4/4 | 2/3 | 3/3 | Added frontmatter examples |
| v3 | 4/4 | 3/3 | 3/3 | Added clarifying questions guidance |
