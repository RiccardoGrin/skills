---
name: looping-tasks
description: Generates an autonomous implementation loop that executes tasks from a plan across multiple Claude sessions. Covers loop script, prompt design, and plan maintenance. Use when setting up autonomous task execution or Ralph-style iterative workflows
---

# Looping Tasks

Generate the infrastructure to run Claude Code in an autonomous implementation loop.
Each iteration starts a fresh session, picks the highest-priority task from `IMPLEMENTATION_PLAN.md`, implements it, tests it, commits, and exits.
Fresh context per iteration is the key design principle — avoids context window degradation.

The user creates the plan (via the planning skill or manually).
The loop only implements — but the agent can update the plan when it discovers new work, bugs, or needed refactoring.

## Workflow

### Phase 1: Project Detection

1. Detect package manager from lock files or config (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`).
2. Detect test command (jest, vitest, pytest, cargo test, or `scripts.test` in `package.json`).
3. Detect linter/formatter (eslint, biome, prettier, ruff, etc.).
4. Check for an existing `IMPLEMENTATION_PLAN.md` — if missing, suggest the user create one with the planning skill first.

### Phase 2: Generate `loop.sh`

Generate this script in the project root:

```bash
#!/bin/bash
# Autonomous Claude Code implementation loop
# Usage: ./loop.sh [max_iterations]
set -euo pipefail

MAX="${1:-10}"
PLAN="IMPLEMENTATION_PLAN.md"
BRANCH=$(git branch --show-current)
i=0

[ ! -f "$PLAN" ] && echo "Missing $PLAN — create a plan first (use the planning skill or write one manually)" && exit 1

while [ $i -lt $MAX ]; do
  echo "=== Iteration $((i + 1))/$MAX ==="

  cat <<'PROMPT' | claude -p --model opus --dangerouslySkipPermissions
Study IMPLEMENTATION_PLAN.md and CLAUDE.md (if it exists).

PICKUP: Before doing anything, orient yourself:
- Check git status and recent commits (git log --oneline -5)
- Read .claude/handoff.md if it exists (then delete it)
- Understand where the project stands right now

TASK SELECTION: Choose the highest-priority open task (marked [ ]) from the plan.
Consider dependencies, urgency, and what unblocks the most work.
You are not required to go in order — use your judgment.

IMPLEMENT: Do that one task thoroughly:
- Study existing code before modifying — don't assume features are not implemented
- Write code, write tests, run tests until they pass
- Run the linter/formatter if one is configured
- Use only 1 subagent for builds and tests to avoid resource contention

PLAN MAINTENANCE: After implementation, update the plan:
- Mark the completed task [x]
- If you discovered bugs, add them as new [ ] tasks at the right priority
- If a future task needs splitting or revision, update it
- Add key decisions to the Decision Log (business/project decisions, not obvious code choices)
- Add issues found to Issues Found if relevant
- If all tasks are done, write ALL_TASKS_COMPLETE as the first line of the plan

HANDOFF: Commit all changes with a descriptive message (WHY not WHAT).
If there is context the next iteration needs, write it to .claude/handoff.md.

Stop after this one task.
PROMPT

  # Check completion
  if head -1 "$PLAN" 2>/dev/null | grep -q "ALL_TASKS_COMPLETE"; then
    echo "=== All tasks complete ==="
    break
  fi

  git push origin "$BRANCH" 2>/dev/null || git push -u origin "$BRANCH" 2>/dev/null || true
  i=$((i + 1))
  sleep 2
done

echo "=== Finished after $i iterations ==="
```

#### Design Choices

- `--dangerouslySkipPermissions` — the agent needs full tool access including code execution; this is the default for autonomous loops.
- `--model opus` — strongest model for autonomous work; change to sonnet for simpler tasks.
- Heredoc prompt (`cat <<'PROMPT'`) — easier to read and edit than a one-liner.
- "Don't assume features are not implemented" — prevents recreating existing code.
- "Only 1 subagent for builds and tests" — prevents resource contention.
- "Stop after this one task" — critical for loop discipline; without it agents try to do everything.
- `git push` after each iteration — progress is never lost even if the loop is interrupted.
- `sleep 2` — prevents API rate limiting between iterations.
- `ALL_TASKS_COMPLETE` sentinel — simple, grep-able completion signal.

### Phase 3: Generate `IMPLEMENTATION_PLAN.md` Template

If the user does not have a plan, generate this template:

```markdown
# Implementation Plan

## Goal
[One sentence: what we're building and why]

## Tasks
- [ ] Task description — `path/to/file` — brief approach notes
- [ ] Task description — `path/to/file`
- [ ] Task description

## Decision Log
<!-- Populated by Claude during implementation -->

## Issues Found
<!-- Populated by Claude during implementation -->
```

If the user has an existing rich plan (from the planning skill), offer to convert it to this checkbox format.
Each task should be completable in a single iteration — split large tasks.

### Phase 4: Customize for Project

Adjust the generated `loop.sh`:

- Set the model — opus for complex work, sonnet for straightforward tasks.
- If the user wants restricted tool access, replace `--dangerouslySkipPermissions` with `--allowedTools` and a whitelist tailored to the detected stack (e.g., `"Read,Glob,Grep,Edit,Write,Bash(git *),Bash(pnpm *),Bash(npx *),Task"`).

### Phase 5: Verification

1. Read back `loop.sh` and confirm it is correct.
2. Verify `IMPLEMENTATION_PLAN.md` exists and has at least one `[ ]` task.
3. Show the user how to run it:
   - `./loop.sh 10` — implement up to 10 tasks
   - `./loop.sh 1` — implement just one task (for testing)
4. Recommend: run `./loop.sh 1` first, review the result, then scale up.

## Anti-Patterns

| Avoid | Do Instead |
|-------|------------|
| Running without a plan | Create `IMPLEMENTATION_PLAN.md` first — the loop reads it every iteration |
| Tasks too large for one iteration | Split into smaller, independently testable tasks |
| Never reviewing loop output | Check the first few iterations, then spot-check periodically |
| Restricting tools by default | Let the agent use code execution; restrict only when specifically needed |
| Automating the planning step | Planning requires user decisions — keep it manual, let the loop implement |
