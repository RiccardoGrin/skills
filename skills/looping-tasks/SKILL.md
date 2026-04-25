---
name: looping-tasks
description: Generates an autonomous implementation loop that executes tasks from a plan across Claude sessions, with periodic audit passes that inject follow-up tasks. Covers loop script, prompt design, and audit cadence. Use when setting up autonomous task execution or Ralph-style iterative workflows
---

# Looping Tasks

Install the infrastructure to run Claude Code in an autonomous implementation loop.
Each iteration starts a fresh session, picks the next task from the active plan, implements it, tests it, commits, and exits.
Fresh context per iteration is the key design principle — avoids context window degradation.

Every N worker iterations (default 5) and once at the very end, the loop runs an **audit iteration** instead of a worker iteration.
The auditor spawns parallel subagents to review recently completed work against the plan and codebase, triages the findings, and injects follow-ups into the plan as new `[ ]` tasks.
It never fixes code itself — the next worker iteration picks the audit tasks up normally — with one exception: the auditor verifies the project builds and fixes build breakage inline, since a broken build would block its own commit.

The user creates the plan (via the planning skill or manually).
The loop only implements — but the agent can update the plan when it discovers new work, bugs, or needed refactoring.

## Bundled Templates

These templates ship with the skill. Copy them into the target repo under `loop/` and gitignore that directory.
The templates are designed to be project-agnostic — most projects need zero changes, some need a tweak to the audit prompt's checklist.

| Template | Purpose |
|----------|---------|
| `scripts/loop.sh` | The loop driver. Implements mode selection (worker/audit/resume), retry-on-error, final-audit gating, and changelog generation. |
| `scripts/prompt.txt` | The worker prompt — one iteration picks a task, implements, tests, commits, updates the plan, stops. |
| `scripts/loop-worktrees.sh` | **Optional.** Thin wrapper that runs the same loop inside a git worktree on its own branch. Delegates all iteration logic to `loop.sh` — zero duplication. See the "Worktree Mode" section below. |
| `scripts/worktreeinclude.example` | Optional template for `.worktreeinclude` — globs of gitignored files to copy into new worktrees (`.env` etc.). |
| `scripts/worktreesetup.example` | Optional template for `.worktreesetup` — shell script that runs once in a new worktree to install deps. |

The audit prompt and changelog prompt are inline heredocs inside `loop.sh` — they rarely need tuning.

## Workflow Checklist

```
- [ ] Phase 1: Detect project and locate plan
- [ ] Phase 2: Install templates into loop/
- [ ] Phase 3: Verify the plan is loop-ready
- [ ] Phase 4: Customize for the project
- [ ] Phase 5: Show the user how to run it
```

## Phase 1: Detect Project and Locate Plan

1. Detect package manager from lock files or config (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`).
2. Detect test command (jest, vitest, pytest, cargo test, or `scripts.test` in `package.json`).
3. Search for an existing implementation plan — `IMPLEMENTATION_PLAN.md` at the repo root first, then common locations (`docs/`, `docs/plans/`), then search recursively.
4. If missing, stop and tell the user to create one first (suggest the `planning` skill).

## Phase 2: Install Templates Into `loop/`

1. Create `loop/` at the repo root.
2. Copy `<skill-dir>/scripts/loop.sh` → `loop/loop.sh`.
3. Copy `<skill-dir>/scripts/prompt.txt` → `loop/prompt.txt`.
4. Ensure `loop/` is gitignored — append `loop/` to `.gitignore` if it isn't already.
   The loop directory holds runtime artifacts (`handoff.md`, `.final_audit_done`) and a personal-to-the-user prompt, so it should not be checked in.
5. On macOS/Linux, `chmod +x loop/loop.sh`.

All `scripts/` paths are **relative to the skill directory** — resolve to absolute paths before copying.

## Phase 3: Verify the Plan Is Loop-Ready

1. The plan should be a flat `[ ]` checkbox list with a short preamble covering project structure and conventions.
   The worker prompt reads the preamble every iteration.
2. Confirm the plan has at least one unchecked `[ ]` task.
3. If the plan is prose-heavy or uses phased sections without checkboxes, offer to convert it to the flat checkbox format before starting the loop.

## Phase 4: Customize for the Project

Most customization is optional — defaults are sensible.

**Audit cadence.** The loop audits every `AUDIT_EVERY` worker iterations (default 5) and once at the end.
Override per-run with an env var: `AUDIT_EVERY=3 bash loop/loop.sh 15`.
Smaller plans (< 15 tasks) may warrant lowering it so audits still fire before the final pass.

**Audit checklist.** The auditor prompt inside `loop.sh` lists five categories to check: gaps vs plan, pattern match, security, comments, and tests.
The security line is intentionally generic ("violations of rules stated in CLAUDE.md").
If the target repo's `CLAUDE.md` has specific rules worth naming explicitly (authz scoping, rate-limit tiers, webhook signature verification, etc.), edit that line to name them — a concrete auditor finds more.

**Build verification at audit time.** The audit prompt instructs the auditor to run the project's build command before committing. The auditor figures out the right command from CLAUDE.md / AGENTS.md / the package manifest — generic across stacks. This lets per-commit hooks skip the (often slow) full build and run only fast checks (unit tests + typecheck), with audit serving as the periodic full-build gate. If the project has no meaningful build step, the auditor skips this.

**Restricted tools.** By default the script uses `--dangerously-skip-permissions`.
If the user wants restricted tool access, replace it with `--allowedTools` and a whitelist tailored to the detected stack (e.g., `"Read,Glob,Grep,Edit,Write,Bash(git *),Bash(pnpm *),Bash(npx *),Task"`).
Apply the same change to every `claude` invocation in the script.

**Model choice.** The worker and auditor both use `--model opus`.
The changelog pass uses `--model sonnet`.
These are unversioned aliases — they track the current opus/sonnet and don't need manual updating as new versions release.
Only change them if the user specifically wants a different capability tier.

**Windows/PowerShell users.** `./loop.sh` won't execute directly in PowerShell — it triggers a "choose program" dialog.
Running `bash loop/loop.sh` may also fail because PowerShell resolves `bash` to `C:/Windows/System32/bash.exe` (WSL launcher), not Git Bash.
Instruct the user to either:
- Use the full Git Bash path: `& "C:/Program Files/Git/usr/bin/bash.exe" loop/loop.sh 1`
- Or open a **Git Bash** terminal and run `bash loop/loop.sh 1` from there

The bundled script already includes `export PATH="/usr/bin:/mingw64/bin:$PATH"` which ensures Git Bash utilities (`grep`, `cat`, `find`, etc.) are available even when Git Bash is invoked from PowerShell without its normal startup.
Do NOT generate a `.ps1` equivalent — PowerShell treats `-` as a unary operator and special characters (em dashes, etc.) break string parsing, making the prompt content unreliable.

## Phase 5: Show the User How to Run It

1. Get a subagent to read back `loop/loop.sh` and confirm it is correct after any edits.
2. **Do NOT attempt to run `loop/loop.sh` from within Claude Code** — nested Claude sessions are forbidden and will error.
   The script must be run from a separate terminal.
3. Usage:
   - **macOS/Linux**: `bash loop/loop.sh 10` (or `./loop/loop.sh 10` if chmod'd)
   - **Windows (Git Bash terminal)**: `bash loop/loop.sh 10`
   - **Windows (PowerShell)**: `& "C:/Program Files/Git/usr/bin/bash.exe" loop/loop.sh 10`
   - Use `1` instead of `10` for a single test iteration
   - **Resume after interrupt**: `bash loop/loop.sh 10 <session-id>` (the session ID is printed when you Ctrl+C mid-iteration)
   - **Tune audit cadence**: `AUDIT_EVERY=3 bash loop/loop.sh 10`
   - **Custom plan file**: `PLAN_FILE=docs/plans/my_plan.md bash loop/loop.sh 10`
4. Recommend: run with `1` first, review the result, then scale up.

## How the Audit Pass Works

Understanding the audit behavior helps diagnose surprises.

- The loop tracks `SINCE_AUDIT`, a counter of worker iterations since the last audit.
- When `SINCE_AUDIT >= AUDIT_EVERY`, the next iteration runs the auditor instead of the worker.
  The counter resets after an audit.
- When the worker prepends `ALL_TASKS_COMPLETE` to the plan, the loop runs one **final audit pass** before generating the changelog.
- If the final audit finds issues worth fixing, it appends them as tasks and removes `ALL_TASKS_COMPLETE`.
  Subsequent worker iterations pick the audit tasks up and eventually the worker restores the sentinel.
- The final-audit pass runs exactly **once**.
  After it runs with `ALL_TASKS_COMPLETE` still present, the script creates `loop/.final_audit_done` and goes straight to the changelog on the next loop pass — this prevents an infinite audit → fix → audit cycle.
- The flag file is cleared at script start so reruns of the whole loop get a fresh final audit.

## Worktree Mode (Optional)

`scripts/loop-worktrees.sh` runs the same loop inside a dedicated git worktree + branch, so it never touches the user's main working tree.
It is a thin wrapper — pre-flight only.
All iteration behavior (worker/audit/resume, retry, changelog) is inherited from the inner `loop.sh` that runs inside the worktree.
One command, full output visibility in the terminal.

**When to use it:**

- Running multiple plans in parallel (separate terminals, separate worktrees).
- Experimenting with risky or large changes that you want isolated on a branch before merging.
- The user wants to keep working in main while the loop runs somewhere else.

**When NOT to use it:**

- The project has shared external state (databases, queues, caches, third-party services) that parallel worktrees would race on — worktrees isolate *code*, not infrastructure.
- The plan is small (< 10 tasks) — the setup overhead isn't worth it.
- There's only one plan running — plain `loop.sh` is simpler.

**Installation.** In addition to `loop.sh` + `prompt.txt`:

1. Copy `scripts/loop-worktrees.sh` → `loop/loop-worktrees.sh` in the target repo.
2. Optionally copy `scripts/worktreeinclude.example` → `.worktreeinclude` at the repo root (for `.env` / gitignored files the worktree needs).
3. Optionally copy `scripts/worktreesetup.example` → `.worktreesetup` at the repo root and customize for the stack (deps install, etc.).
4. Both `.worktreeinclude` and `.worktreesetup` should be gitignored — they're personal to the user's setup.

**Usage.**

```
bash loop/loop-worktrees.sh <PLAN_FILE> [max_iterations]
```

The wrapper creates `loop/worktrees/<name>/` on branch `worktree/<name>` (name derived from the plan filename), copies deps + envs, syncs the loop templates, and invokes `loop.sh` inside.
The plan path is a **positional argument** to the wrapper (not an env var) — the wrapper forwards it to the inner loop as the `PLAN_FILE` env var automatically.
Other env vars (`AUDIT_EVERY`, `RESUME_ID`) pass through to the inner loop unchanged.
The inner loop's stdout streams to this terminal live — you see every iteration exactly as you would with `loop.sh` directly.

On exit (normal or Ctrl+C), the wrapper prints merge + cleanup instructions.
It never merges back to main automatically — the user reviews the branch and merges when ready.

**Footguns:**

- **Shared external state is not isolated.**
  Two worktrees running in parallel share the same database, Redis, queues, external APIs, etc.
  For code areas that touch shared infrastructure (schema migrations, queue consumers), stick to one worktree at a time.
- **Base branch is `origin/HEAD`, not local HEAD.**
  The worktree is created from the remote's default branch (matching Anthropic's worktree design).
  If the user has unpushed WIP on the current branch, the worktree will not see it — the wrapper warns when it detects this and pauses 5 seconds.
- **The plan must be reachable.**
  If the plan is committed locally but not pushed, or is untracked, the wrapper copies it into the worktree so the first worker iteration can commit it on the worktree branch.
  Still worth pushing first if you want an authoritative copy on origin.
- **`isolation: worktree` subagent failure mode.**
  Anthropic has known cases where subagents with `isolation: worktree` silently fall back to running in the main repo.
  The bundled worker prompt does not spawn parallel code-editing subagents for this reason.
  The auditor spawns parallel subagents but only for read-only review.

## Related Skills

Consider activating `/being-careful` before starting an autonomous loop to block accidental destructive commands (`rm -rf`, force-push, `DROP TABLE`, etc.).
If the loop should only touch files in a specific area, use `/freezing-edits <dir>` to prevent edits elsewhere.
After the loop completes, run `/reviewing-code` for a final adversarial review before pushing.

## Anti-Patterns

| Avoid | Do Instead |
|-------|------------|
| Running without a plan | Create the implementation plan first — the loop reads it every iteration |
| Tasks too large for one iteration | Split into smaller, independently testable tasks |
| Never reviewing loop output | Check the first few iterations, then spot-check periodically. The audit pass catches a lot, but is not a substitute for human review on anything user-facing |
| Restricting tools by default | Let the agent use code execution; restrict only when specifically needed |
| Automating the planning step | Planning requires user decisions — keep it manual, let the loop implement |
| Setting `AUDIT_EVERY` very high to "save tokens" | Audit drift compounds. The point of periodic audits is catching issues while context is small. Default 5 is already a reasonable upper bound |
| Pinning the model to a specific version (e.g., `opus-4-6`) | Use the unversioned alias (`opus`, `sonnet`) so the loop tracks current releases automatically |
| Editing `loop/loop.sh` in the skill repo for a project-specific tweak | Keep the skill's `scripts/loop.sh` generic. Tweak the copy in the target repo's `loop/` directory |
