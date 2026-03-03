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
PROMPT_FILE=".claude/loop-prompt.txt"
CHANGELOG_PROMPT=".claude/changelog-prompt.txt"
i=0

[ ! -f "$PLAN" ] && echo "Missing $PLAN — create a plan first (use the planning skill or write one manually)" && exit 1

mkdir -p .claude

# Write prompt to file — avoids heredoc-pipe-OR parsing issues on Windows/Git Bash
cat > "$PROMPT_FILE" <<'PROMPT'
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
- Read CLAUDE.md (or equivalent project config) before creating content — follow any asset, design, or quality rules documented there
- Check your available skills and tools before deferring work — you may have capabilities for asset creation (sprites, images, icons), content generation, or other tasks that seem "human-only." If a skill exists for it, attempt it rather than leaving a placeholder
- Self-correct: if an intermediate result looks wrong (test failures, zero results, unexpected behavior), investigate the root cause and adjust your approach — don't just proceed or retry blindly
- Write code, write tests, run tests until they pass
- Run the linter/formatter if one is configured
- Use only 1 subagent for builds and tests to avoid resource contention

VERIFY: Before marking a task done, check your work:
- If you created assets (images, icons, etc.), verify they meet project quality standards (e.g., correct dimensions, true transparency, no placeholders left behind)
- Verify new content is logically consistent with the rest of the project (e.g., labels make sense, data relationships are valid, config entries match code that references them)
- If you added UI elements, verify layering/z-index doesn't obscure existing UI
- Cross-reference any data/config files against the code that loads them — list gaps as new tasks
- Run the build/test command and confirm zero errors

PLAN MAINTENANCE: After implementation, update the plan:
- Mark the completed task [x]
- If you discovered bugs, add them as new [ ] tasks at the right priority
- If a future task needs splitting or revision, update it
- Add key decisions to the Decision Log (business/project decisions, not obvious code choices)
- Add issues found to Issues Found if relevant
- If all tasks are done, prepend ALL_TASKS_COMPLETE as a new line above all existing content in the plan

CHANGELOG: Consider whether the completed work so far warrants a changelog update.
Prefer bundling related work into larger, thematic updates over frequent small ones.
For example: one new biome with its mobs is a minor addition — but three new biomes with full
enemy rosters is a cohesive major update worth a version bump. Wait for the bigger story.
Only run /generating-changelogs when the accumulated [x] items (not yet in CHANGELOG.md) form
a release that would feel meaningful to a player — not just "stuff got added."
When in doubt, skip it — the end-of-loop completion will always generate a final changelog.

HANDOFF: Commit all changes with a descriptive message (WHY not WHAT).
If there is context the next iteration needs, write it to .claude/handoff.md.

Stop after this one task.
PROMPT

cat > "$CHANGELOG_PROMPT" <<'CHANGELOG'
Run /generating-changelogs

Generate a changelog for all completed work in IMPLEMENTATION_PLAN.md.
Only include tasks marked [x] that are NOT already covered by an existing CHANGELOG.md entry.
If CHANGELOG.md already has entries, this is an incremental update — don't repeat previous content.
Commit the changelog update.
CHANGELOG

while [ $i -lt $MAX ]; do
  echo "=== Iteration $((i + 1))/$MAX ==="

  if ! claude -p --model opus --dangerously-skip-permissions < "$PROMPT_FILE"; then
    echo "Claude exited with error — stopping loop"
    exit 1
  fi

  # Check completion (grep anywhere — sentinel may not be exactly line 1)
  if grep -q "^ALL_TASKS_COMPLETE" "$PLAN" 2>/dev/null; then
    echo "=== All tasks complete after $((i + 1)) iterations ==="
    echo "=== Generating changelog ==="
    claude -p --model sonnet --dangerously-skip-permissions < "$CHANGELOG_PROMPT"
    git push origin "$BRANCH" 2>/dev/null || true
    break
  fi

  git push origin "$BRANCH" 2>/dev/null || git push -u origin "$BRANCH" 2>/dev/null || echo "Warning: git push failed — changes are committed locally but not backed up"
  i=$((i + 1))
  sleep 2  # Prevents API rate limiting; increase if hitting limits, decrease for faster iteration
done

if grep -q "^ALL_TASKS_COMPLETE" "$PLAN" 2>/dev/null; then
  echo "=== All tasks complete — changelog generated ==="
else
  echo "=== Reached max iterations ($MAX) — open tasks may remain ==="
fi
```

#### Design Choices

- `--dangerously-skip-permissions` — the agent needs full tool access including code execution; this is the default for autonomous loops.
- `--model opus` — strongest model for autonomous work; change to sonnet for simpler tasks.
- Prompt written to temp file, then fed via `< "$PROMPT_FILE"` — the previous `cat <<'PROMPT' | claude ... || { ... }` pattern caused syntax errors on Windows/Git Bash because the heredoc-pipe-OR-brace combination doesn't parse reliably across shells. Writing to a file first is portable and equally readable.
- "Don't assume features are not implemented" — prevents recreating existing code.
- "Only 1 subagent for builds and tests" — prevents resource contention.
- "Stop after this one task" — critical for loop discipline; without it agents try to do everything.
- `git push` after each iteration — progress is never lost even if the loop is interrupted.
- `sleep 2` — prevents API rate limiting between iterations.
- `ALL_TASKS_COMPLETE` sentinel — simple, grep-able completion signal. Prepended above all content so it's detectable regardless of plan format.
- Changelog generation via `/generating-changelogs` — runs as a separate sonnet session on completion (fresh context, focused on synthesis). Mid-loop, the agent can also invoke the skill inline when enough work has accumulated.

### Phase 3: Verify `IMPLEMENTATION_PLAN.md`

The plan should already exist — the user creates it before running the loop (via the planning skill or manually).

1. Check for `IMPLEMENTATION_PLAN.md` in the project root.
2. If it exists, verify it has at least one `[ ]` task and the format is loop-compatible (flat checkbox list).
3. If it exists but uses a rich format (prose, phased sections without checkboxes), offer to convert it to the flat checkbox format.
4. If it does not exist, stop and tell the user to create one first — suggest using the planning skill with the loop-ready output option (Phase 4b).

### Phase 4: Customize for Project

Adjust the generated `loop.sh`:

- Set the model — opus for complex work, sonnet for straightforward tasks.
- If the user wants restricted tool access, replace `--dangerously-skip-permissions` with `--allowedTools` and a whitelist tailored to the detected stack (e.g., `"Read,Glob,Grep,Edit,Write,Bash(git *),Bash(pnpm *),Bash(npx *),Task"`).
- **Windows/PowerShell users**: `./loop.sh` won't execute directly in PowerShell — it triggers a "choose program" dialog. Instruct the user to run `bash ./loop.sh` instead (requires Git Bash on PATH, which is standard with Git for Windows). Do NOT generate a `.ps1` equivalent — PowerShell treats `-` as a unary operator and special characters (em dashes, etc.) break string parsing, making the prompt content unreliable.

### Phase 5: Verification

1. Read back `loop.sh` and confirm it is correct.
2. Verify `IMPLEMENTATION_PLAN.md` exists and has at least one `[ ]` task.
3. **Do NOT attempt to run `loop.sh` from within Claude Code** — nested Claude sessions are forbidden and will error. The script must be run from a separate terminal.
4. Show the user how to run it:
   - `./loop.sh 10` — implement up to 10 tasks
   - `./loop.sh 1` — implement just one task (for testing)
5. Recommend: run `./loop.sh 1` first, review the result, then scale up.

## Anti-Patterns

| Avoid | Do Instead |
|-------|------------|
| Running without a plan | Create `IMPLEMENTATION_PLAN.md` first — the loop reads it every iteration |
| Tasks too large for one iteration | Split into smaller, independently testable tasks |
| Never reviewing loop output | Check the first few iterations, then spot-check periodically |
| Restricting tools by default | Let the agent use code execution; restrict only when specifically needed |
| Automating the planning step | Planning requires user decisions — keep it manual, let the loop implement |
