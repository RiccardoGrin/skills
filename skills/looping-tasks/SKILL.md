---
name: looping-tasks
description: Generates an autonomous implementation loop that executes tasks from a plan across agent sessions (Claude Code or OpenAI Codex), with periodic audit passes that inject follow-up tasks. Covers loop script, prompt design, and audit cadence. Use when setting up autonomous task execution or Ralph-style iterative workflows
---

# Looping Tasks

Install the infrastructure to run a coding agent in an autonomous implementation loop.
Each iteration starts a fresh session, picks the next task from the active plan, implements it, tests it, commits, and exits.
Fresh context per iteration is the key design principle — avoids context window degradation.

The loop drives **Claude Code** (default) or **OpenAI Codex**, selected with `AGENT=claude|codex`.
Both run through one seam (`spawn_agent` / `agent_oneshot` in `loop.sh`); everything else in the script is agent-agnostic.
See *Choosing the Agent* below — the two differ in real ways (liveness signal, quota behaviour, instruction file).

Every N worker iterations (default 5) and once at the very end, the loop runs an **audit iteration** instead of a worker iteration.
The auditor spawns parallel subagents to review work against the plan and codebase, triages the findings, and injects follow-ups into the plan as new `[ ]` tasks.
The two rounds have deliberately different scope: a **periodic** pass reviews only the work since the last `audit:` commit, while a **final** pass reviews the whole plan as one body of work — it is the only pass that sees the whole, and the only one that can judge duplication and redundancy, which exist only in aggregate.
It never fixes code itself — the next worker iteration picks the audit tasks up normally — with one exception: the auditor verifies the project builds and fixes build breakage inline, since a broken build would block its own commit.
Both rounds are bounded by the **plan**, never by the log: the loop merges `main` in every iteration, so the branch history also carries parallel work the plan never asked for, and an auditor that reviews the window instead of the plan files tasks against code the loop then rewrites. Anything real but out of scope goes under `Issues Found` as a note, not as a `[ ]` task.

The user creates the plan (via the planning skill or manually).
The loop only implements — but the agent can update the plan when it discovers new work, bugs, or needed refactoring.

## Bundled Templates

These templates ship with the skill. Copy them into the target repo under `loop/` and gitignore that directory.
The templates are designed to be project-agnostic — most projects need zero changes, some need a tweak to the audit prompt's checklist.

| Template | Purpose |
|----------|---------|
| `scripts/loop.sh` | The loop driver. Implements mode selection (worker/audit/resume), retry-on-error, final-audit gating, and changelog generation. |
| `scripts/prompt.txt` | The worker prompt — one iteration picks a task, implements, tests, commits, updates the plan, stops. |
| `scripts/watchdog.sh` | Background process the loop launches at startup. Kills the active agent session if its liveness file stops growing for 20 min, so the loop's retry path can spawn a fresh session. See "Idle Watchdog" below. |
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
4. Copy `<skill-dir>/scripts/watchdog.sh` → `loop/watchdog.sh`. The loop auto-detects it at startup; absent watchdog just disables the idle timeout.
5. Ensure `loop/` is gitignored — append `loop/` to `.gitignore` if it isn't already.
   The loop directory holds runtime artifacts (`handoff.md`, `.final_audit_done`, `.current_session`) and a personal-to-the-user prompt, so it should not be checked in.
6. On macOS/Linux, `chmod +x loop/loop.sh loop/watchdog.sh`.
7. If the loop will run on Codex (`AGENT=codex`) and the repo has a `CLAUDE.md` but no `AGENTS.md`, create a thin `AGENTS.md` at the repo root pointing at `CLAUDE.md` — Codex does not read `CLAUDE.md`. Keep the rules in one file and point at it; do not duplicate them, and do not symlink (see *Choosing the Agent*). This one is committed, unlike everything else in `loop/`.

All `scripts/` paths are **relative to the skill directory** — resolve to absolute paths before copying.

## Phase 3: Verify the Plan Is Loop-Ready

1. The plan should be a flat `[ ]` checkbox list with a short preamble covering project structure and conventions.
   The worker prompt reads the preamble every iteration.
2. Confirm the plan has at least one unchecked `[ ]` task.
3. If the plan is prose-heavy or uses phased sections without checkboxes, offer to convert it to the flat checkbox format before starting the loop.

## Phase 4: Customize for the Project

Most customization is optional — defaults are sensible.

**Audit cadence.** The loop audits every `AUDIT_EVERY` worker iterations (default 5), plus up to
`MAX_FINAL_AUDITS` times (default 2) once the plan reports complete.
Override per-run with env vars: `AUDIT_EVERY=3 MAX_FINAL_AUDITS=1 bash loop/loop.sh 15`.
Smaller plans (< 15 tasks) may warrant lowering `AUDIT_EVERY` so audits still fire before the final pass.
Raise `MAX_FINAL_AUDITS` only deliberately — see *How the Audit Pass Works* for why it is capped at all.

**Audit checklist.** The auditor prompt inside `loop.sh` lists six categories to check: gaps vs plan, pattern match, security, comments, tests, and — final pass only — duplication/redundancy/best practices.
The security line is intentionally generic ("violations of rules stated in CLAUDE.md"), as is the best-practices line ("the project's own stated rules").
If the target repo's `CLAUDE.md` has specific rules worth naming explicitly (authz scoping, rate-limit tiers, webhook signature verification, etc.), edit that line to name them — a concrete auditor finds more.

**Build verification at audit time.** The audit prompt instructs the auditor to run the project's build command before committing. The auditor figures out the right command from CLAUDE.md / AGENTS.md / the package manifest — generic across stacks. This lets per-commit hooks skip the (often slow) full build and run only fast checks (unit tests + typecheck), with audit serving as the periodic full-build gate. If the project has no meaningful build step, the auditor skips this.

**Restricted tools.** By default the script uses `--dangerously-skip-permissions` (claude) / `--dangerously-bypass-approvals-and-sandbox` (codex).
On claude, if the user wants restricted tool access, replace it with `--allowedTools` and a whitelist tailored to the detected stack (e.g., `"Read,Glob,Grep,Edit,Write,Bash(git *),Bash(pnpm *),Bash(npx *),Task"`) in `spawn_agent`'s claude arm and in `agent_oneshot`.
On codex there is no middle setting worth using — see *Choosing the Agent*.

**Model choice.** Claude: worker and auditor use `--model opus`, the changelog pass `sonnet` (`CLAUDE_MODEL` / `CLAUDE_FAST_MODEL`).
These are unversioned aliases — they track the current opus/sonnet and don't need manual updating as new versions release.
Codex: `CODEX_MODEL` (default `gpt-5.6-sol`, the flagship tier) and `CODEX_EFFORT` (default `high`).
Codex model names ARE versioned — there is no `latest` alias — so they need updating as releases land.
Only change tiers if the user specifically wants a different capability level, or to stretch a subscription window.

**Windows/PowerShell users.** `./loop.sh` won't execute directly in PowerShell — it triggers a "choose program" dialog.
Running `bash loop/loop.sh` may also fail because PowerShell resolves `bash` to `C:/Windows/System32/bash.exe` (WSL launcher), not Git Bash.
Instruct the user to either:
- Use the full Git Bash path: `& "C:/Program Files/Git/usr/bin/bash.exe" loop/loop.sh 1`
- Or open a **Git Bash** terminal and run `bash loop/loop.sh 1` from there

The bundled script already includes `export PATH="/usr/bin:/mingw64/bin:$PATH"` which ensures Git Bash utilities (`grep`, `cat`, `find`, etc.) are available even when Git Bash is invoked from PowerShell without its normal startup.
Do NOT generate a `.ps1` equivalent — PowerShell treats `-` as a unary operator and special characters (em dashes, etc.) break string parsing, making the prompt content unreliable.

## Choosing the Agent

`AGENT=claude` (default) or `AGENT=codex`. The seam is `spawn_agent` / `agent_oneshot` in `loop.sh` — a third CLI is a new `case` arm, not edits across the script.

**Codex prerequisites.** `npm install -g @openai/codex`, then `codex login` once (browser OAuth).
A ChatGPT Plus/Pro/Business plan includes Codex CLI usage — check `~/.codex/auth.json` shows `"auth_mode": "chatgpt"` and no API key is needed.
If the user has the Codex **desktop app**, it already wrote that file and the CLI shares it — they may already be logged in.

**The desktop app cannot run the loop.** It has no scriptable one-shot mode. `codex exec` is the headless counterpart to `claude -p`; if the user asks about the app, that is the answer.

**Flags are not interchangeable, and the docs are stale.** `codex exec` has REMOVED `-a/--ask-for-approval` and `--full-auto` (exec hardcodes approval=never; the bypass flag is what selects `danger-full-access`), and `-s workspace-write` is effectively read-only on native Windows. Blog posts and even the official CLI reference still recommend `-a never -s workspace-write`; the installed binary rejects both. Verify any flag change with `codex exec --help` before shipping it.
`codex exec resume` additionally rejects `-s -a -C --add-dir -p --color` — only `--model`, the two bypass flags, `-c`, `-o`, `--json` and the `--ignore-*` flags survive onto resume. This is why `loop.sh` keeps `CODEX_FRESH_FLAGS` separate from `CODEX_FLAGS`.

**`--ignore-user-config` is deliberate.** On a machine that also has the Codex desktop app, `~/.codex/config.toml` is written BY that app — plugins, MCP servers, and a turn-ended notify hook, all of which would spawn every iteration of an unattended loop. Auth resolves from `CODEX_HOME`, not that file, so the subscription login is unaffected; AGENTS.md discovery is likewise unaffected.

**`CODEX_EFFORT` is validated by the script, because codex will not validate it.** The config enum has a catch-all string variant, so `-c model_reasoning_effort=hgih` is accepted and forwarded — the run then reasons at some other level for the whole loop with no error. Note `gpt-5.6-sol`'s own default is `low`, so this knob does real work. `ultra` is excluded on purpose: it delegates to subagents.

**Subscription quota is a hard stop, not a flake.** Codex classes usage-limit as non-retryable and exits 1. The loop detects the message and stops cleanly with the rerun command rather than burning its retry on a window that resets in hours. Roughly: a ~100-iteration run on the flagship tier at `high` effort will exhaust a Plus window. `CODEX_MODEL=gpt-5.6-terra` or `CODEX_EFFORT=low` goes considerably further.

**Instruction file.** Claude Code reads `CLAUDE.md`; Codex reads `AGENTS.md` (merged from git root down to cwd, 32 KiB cap). If the repo has only `CLAUDE.md`, add a thin real `AGENTS.md` pointing at it.
Do **NOT** symlink `AGENTS.md → CLAUDE.md`: Codex does follow real symlinks, but Git Bash `ln -s` silently creates a *copy* unless `MSYS=winsymlinks:nativestrict` is set, and `core.symlinks` is false in most Windows clones. It looks correct on day one and drifts forever after.

**Two known Codex behaviours the loop absorbs rather than fixes:**
- `codex exec` can exit **0** when a nested command failed (open upstream bug). Harmless here — the next iteration re-reads the plan and picks up whatever is still unchecked — but it means exit code alone is not proof an iteration worked.
- `~/.codex/sessions` grows without bound (one report reached ~165 GiB). Prune it occasionally. `--ephemeral` would prevent it but breaks resume.

**Codex always runs PowerShell on Windows**, regardless of the shell that launched it, and this is not configurable. Prompt/plan instructions written in bash idiom will fight the runtime.

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
   - **Run on Codex instead of Claude**: `AGENT=codex bash loop/loop.sh 10`
     (PowerShell: `$env:AGENT="codex"; & "C:/Program Files/Git/usr/bin/bash.exe" loop/loop.sh 10`)
4. Recommend: run with `1` first, review the result, then scale up.

## How the Audit Pass Works

Understanding the audit behavior helps diagnose surprises.

- The loop tracks `SINCE_AUDIT`, a counter of worker iterations since the last audit.
- When `SINCE_AUDIT >= AUDIT_EVERY`, the next iteration runs the auditor instead of the worker.
  The counter resets after an audit.
- When the worker prepends `ALL_TASKS_COMPLETE` to the plan, the loop runs a **final audit pass** before generating the changelog.
- If that audit files tasks, it removes `ALL_TASKS_COMPLETE`. Workers pick the tasks up, the sentinel eventually comes back, and that triggers **another** final audit.
- `loop/.final_audit_done` is written only when a final audit leaves `ALL_TASKS_COMPLETE` **in place**. The next pass then goes straight to the changelog.
  It is therefore not a cap: an audit that files tasks never sets it, so the audit → fix → audit path runs around it. It ends a *clean* run; it does not end a productive one.
- `MAX_FINAL_AUDITS` (default 2) is the actual cap. Once that many final audits have run in one invocation, the loop stops and an agent writes a hand-back message instead of opening another round.
  It counts only `ALL_TASKS_COMPLETE`-triggered audits; periodic ones can't re-arm a completed plan, so they're uncapped.
  It is **not persisted** — rerunning grants a fresh allowance. The thing that actually breaks the cycle is a human choosing to rerun.
- The flag file is cleared at script start so reruns of the whole loop get a fresh final audit.

> **Why the cap exists.** With only the flag, the exit condition was "an audit that finds nothing." The audit's review scope is the commits since the last `audit:` commit — i.e. the previous audit's own output — and comment prose is an unbounded surface, so passes fed on each other. One real run hit 26 rounds and ~100 injected tasks on a 5-task plan. The auditor prompt now fixes prose itself without filing a task (so it can't re-arm the loop), and `MAX_FINAL_AUDITS` backstops whatever that misses.

## Idle Watchdog

An agent session can wedge mid-iteration in ways that don't return an error — most commonly a Bash polling loop with an `until` predicate that never matches (e.g., `until grep -qE "loaded|error|^[A-Za-z]" ...; do sleep 2; done` against output that starts with a non-ASCII character). The session burns CPU forever, never exits, and the loop never advances. Codex has its own version of this: a documented failure where the run stalls with its socket in CLOSE_WAIT and its internal idle timeout never fires.

`watchdog.sh` covers this. At startup, `loop.sh` spawns it in the background and reaps it via an `EXIT` trap. Before each agent invocation the loop writes the PID and session ID to `loop/.current_session`; the watchdog reads that file every 60s and stats the session's **liveness file**, killing the process tree if it hasn't grown for `IDLE_TIMEOUT` seconds (default 1200 = 20 min). The loop's retry-on-error path then spawns a fresh session on the same iteration.

The liveness file differs by agent, which is the one place the watchdog is not agent-agnostic:
- **claude** — the session transcript at `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`.
- **codex** — `loop/.agent-out.log`, the loop's tee of codex's stdout. Codex writes no per-session file that can be stat'd, but it does stream to a pipe incrementally, so the tee's mtime tracks progress. This is load-bearing: if a future codex version block-buffers to a non-TTY, every iteration would be killed at `IDLE_TIMEOUT` and retried forever. Re-verify it if codex behaviour changes.

Idle-based (not wall-clock) is deliberate: a legitimately long iteration is not killed, only a silent one. Do not "simplify" this to wrapping the agent in `timeout`.

**Tunables** (env vars, set on the same line as `bash loop/loop.sh`):

- `IDLE_TIMEOUT=1800` — seconds of transcript silence before kill. Default 1200. Drop to 600 for very interactive plans, raise to 1800–2400 if iterations frequently include long single LLM turns.
- `POLL_INTERVAL=30` — how often the watchdog checks. Default 60. Rarely worth changing.

**Behavior notes:**

- Tree kill is mandatory, not a defense-in-depth nicety. Killing the agent PID alone leaves descendant Bash subprocesses alive on Windows (observed: a stuck `until grep ...; do sleep 2; done` survived its parent's death). The watchdog uses `taskkill //T //F //PID` on Windows and `pkill -P` + `kill` on Unix.
- **Windows PID translation is subtle and was silently broken for a long time.** `taskkill` needs the real Windows PID, not the MSYS PID bash reports. Two traps, both fixed in the current script, both worth knowing before editing it: (1) Git-for-Windows `ps` is NOT procps — it has no `-o/--format`, so the natural `ps -p PID -o winpid=` fails outright and yields an empty string, skipping `taskkill` entirely; parse the fixed-width table's 4th column instead. (2) The MSYS→Windows mapping legitimately MOVES within the first second, because the agent's launcher is a shell shim that `exec`s (measured: 25308 at t=0, 6840 at t=1) — so the watchdog must re-derive the winpid at kill time rather than comparing it against the recorded one and aborting on a difference. With both bugs present the kill never ran at all, so a wedged agent just hung the loop.
- **A kill can land mid-`git commit`.** Now that tree-kill actually works, the retry path clears a leftover `.git/index.lock` — without it every subsequent git operation in the run fails.
- Deterministic hangs burn the retry. If the worker keeps tripping the same trap, watchdog kills first → 60s wait → fresh session hits the same trap → watchdog kills again → loop exits 1. That's the intended behavior — repeated identical hangs are a bug, not a flake.
- Between iterations the sentinel is cleared, so the watchdog idles silently during the 10s pause and the 60s retry sleep.
- If `watchdog.sh` is absent (e.g., the user only copied `loop.sh`), `start_watchdog` no-ops. Loop runs exactly as before, just without the safety net.

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
Other env vars (`AUDIT_EVERY`, `MAX_FINAL_AUDITS`, `HANDOFF_TIMEOUT`, `RESUME_ID`) pass through to the inner loop unchanged.
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
| Pinning the model to a specific version (e.g., `opus-4-6`) | On claude, use the unversioned alias (`opus`, `sonnet`) so the loop tracks current releases automatically. Codex has no such alias — its model names are versioned, so check them against `codex exec --help` / the model list when a release lands |
| Copying a `codex exec` flag set from a blog post or the official CLI reference | Verify against the installed binary — both are stale on the flags that matter (`-a`, `--full-auto`), and `codex exec resume` accepts a different set than `codex exec` |
| Editing `loop/loop.sh` in the skill repo for a project-specific tweak | Keep the skill's `scripts/loop.sh` generic. Tweak the copy in the target repo's `loop/` directory |
