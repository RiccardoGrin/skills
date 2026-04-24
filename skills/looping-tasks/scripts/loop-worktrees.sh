#!/usr/bin/env bash
# Worktree wrapper for the autonomous implementation loop.
# Creates a git worktree + branch, syncs deps/envs, then invokes loop/loop.sh
# inside the worktree. The inner loop's output streams to this terminal —
# same UX as running loop.sh directly, just isolated on its own branch.
#
# Usage:
#   bash loop/loop-worktrees.sh <PLAN_FILE> [max_iterations]
#
# Examples:
#   bash loop/loop-worktrees.sh IMPLEMENTATION_PLAN.md
#   bash loop/loop-worktrees.sh TIME_SEARCH_IMPLEMENTATION_PLAN.md 15
#
# Parallel runs (separate terminals, different plans):
#   Terminal 1: bash loop/loop-worktrees.sh TIME_SEARCH_IMPLEMENTATION_PLAN.md
#   Terminal 2: bash loop/loop-worktrees.sh EMBEDDING_IMPLEMENTATION_PLAN.md
#
# Positional arguments:
#   $1  PLAN_FILE        Path to the plan (required). Forwarded to the inner loop as
#                        the PLAN_FILE env var — do NOT also export it.
#   $2  max_iterations   Max loop iterations (default 10).
#
# Environment variables (all pass through to the inner loop):
#   AUDIT_EVERY     Audit cadence for the inner loop; default 5
#   RESUME_ID       Resume an interrupted Claude session on the first iteration
#   WORKTREE_SETUP  Shell command to run once in new worktrees (overrides .worktreesetup)
#
# Optional files (in repo root):
#   .worktreeinclude  Glob patterns for gitignored files to copy into new worktrees
#   .worktreesetup    Shell script to run once in new worktrees (deps install, etc.)
#
# Design: this wrapper handles pre-flight (worktree create, env copy, deps install,
# template sync) then delegates the entire iteration loop to loop/loop.sh inside
# the worktree. Audit cadence, retry, final-audit gating, and changelog generation
# are all inherited — this script only owns what the inner loop can't.
set -euo pipefail

export PATH="/usr/bin:/mingw64/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

PLAN_FILE="${1:-}"
MAX="${2:-10}"

if [ -z "$PLAN_FILE" ] || [ ! -f "$PLAN_FILE" ]; then
  echo "Usage: bash loop/loop-worktrees.sh <PLAN_FILE> [max_iterations]"
  echo "  PLAN_FILE must exist in the current working tree."
  exit 1
fi

# Verify the inner loop templates exist
if [ ! -f "$SCRIPT_DIR/loop.sh" ] || [ ! -f "$SCRIPT_DIR/prompt.txt" ]; then
  echo "ERROR: loop/loop.sh and loop/prompt.txt must both exist alongside this script."
  exit 1
fi

# Derive worktree name + branch from plan filename
# TIME_SEARCH_IMPLEMENTATION_PLAN.md → time-search
# IMPLEMENTATION_PLAN.md             → implementation-plan
PLAN_BASENAME=$(basename "$PLAN_FILE" .md)
WORKTREE_NAME=$(echo "$PLAN_BASENAME" | sed 's/_IMPLEMENTATION_PLAN$//' | tr '[:upper:]_' '[:lower:]-')
[ -z "$WORKTREE_NAME" ] && WORKTREE_NAME="main-plan"

BRANCH="worktree/${WORKTREE_NAME}"
WORKTREE_DIR="${REPO_ROOT}/loop/worktrees/${WORKTREE_NAME}"

# Warn if local HEAD is ahead of origin — the worktree is created from origin/HEAD
# (Anthropic's default for worktree subagents), so unpushed WIP won't be present.
git fetch origin 2>/dev/null || true
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ -n "$CURRENT_BRANCH" ] && git show-ref --verify --quiet "refs/remotes/origin/${CURRENT_BRANCH}" 2>/dev/null; then
  AHEAD=$(git rev-list --count "origin/${CURRENT_BRANCH}..HEAD" 2>/dev/null || echo 0)
  if [ "$AHEAD" -gt 0 ]; then
    echo "WARNING: local ${CURRENT_BRANCH} is ${AHEAD} commit(s) ahead of origin/${CURRENT_BRANCH}."
    echo "         The worktree is created from origin/HEAD and will NOT contain that WIP."
    echo "         Push first if the worktree needs those commits. Continuing in 5s..."
    sleep 5
  fi
fi

echo "╔══════════════════════════════════════════════╗"
echo "║  Worktree Loop                               ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  Plan:      $PLAN_FILE"
echo "║  Branch:    $BRANCH"
echo "║  Worktree:  loop/worktrees/$WORKTREE_NAME/"
echo "║  Max iters: $MAX"
echo "╚══════════════════════════════════════════════╝"
echo ""

# --- Create worktree if missing ---
if [ -d "$WORKTREE_DIR" ]; then
  if ! git -C "$WORKTREE_DIR" rev-parse --git-dir &>/dev/null; then
    echo "ERROR: $WORKTREE_DIR exists but is not a valid git worktree."
    echo "Fix:   git worktree remove '$WORKTREE_DIR' && rerun"
    exit 1
  fi
  echo "Worktree exists — resuming from previous state"
else
  echo "Creating worktree..."

  # Resolve base branch (origin/HEAD → origin/main → origin/master)
  BASE=""
  if git symbolic-ref refs/remotes/origin/HEAD &>/dev/null; then
    BASE=$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@refs/remotes/@@')
  elif git show-ref --verify --quiet refs/remotes/origin/main 2>/dev/null; then
    BASE="origin/main"
  elif git show-ref --verify --quiet refs/remotes/origin/master 2>/dev/null; then
    BASE="origin/master"
  else
    echo "ERROR: Cannot determine base branch. Run: git remote set-head origin -a"
    exit 1
  fi
  echo "  Base: $BASE"

  mkdir -p "$(dirname "$WORKTREE_DIR")"

  # Reuse branch if it exists from a prior run, otherwise create fresh
  if git show-ref --verify --quiet "refs/heads/${BRANCH}" 2>/dev/null; then
    echo "  Branch $BRANCH already exists — reusing"
    git worktree add "$WORKTREE_DIR" "$BRANCH"
  else
    git worktree add -b "$BRANCH" "$WORKTREE_DIR" "$BASE"
  fi

  # Copy gitignored files listed in .worktreeinclude (e.g., .env, .env.local)
  if [ -f "${REPO_ROOT}/.worktreeinclude" ]; then
    echo "  Copying files from .worktreeinclude..."
    while IFS= read -r pattern || [ -n "$pattern" ]; do
      [[ "$pattern" =~ ^[[:space:]]*# ]] && continue
      [[ -z "${pattern// /}" ]] && continue
      for f in $(cd "$REPO_ROOT" && ls -d $pattern 2>/dev/null); do
        if [ -f "${REPO_ROOT}/$f" ] && git -C "$REPO_ROOT" check-ignore -q "$f" 2>/dev/null; then
          mkdir -p "$(dirname "${WORKTREE_DIR}/$f")"
          cp "${REPO_ROOT}/$f" "${WORKTREE_DIR}/$f"
          echo "    Copied: $f"
        fi
      done
    done < "${REPO_ROOT}/.worktreeinclude"
  fi

  # Run one-time setup (dependency installation, etc.)
  if [ -n "${WORKTREE_SETUP:-}" ]; then
    echo "  Running WORKTREE_SETUP..."
    (cd "$WORKTREE_DIR" && eval "$WORKTREE_SETUP")
  elif [ -f "${REPO_ROOT}/.worktreesetup" ]; then
    echo "  Running .worktreesetup..."
    (cd "$WORKTREE_DIR" && bash "${REPO_ROOT}/.worktreesetup")
  fi

  echo "  Worktree ready"
fi

# --- Ensure the plan exists inside the worktree ---
# If the plan isn't present in the branch being checked out (e.g., locally
# committed but not yet pushed, or simply untracked in the working tree), copy
# it in. The worker's first iteration will naturally commit it on the worktree
# branch as part of marking a task [x].
if [ ! -f "${WORKTREE_DIR}/${PLAN_FILE}" ]; then
  mkdir -p "$(dirname "${WORKTREE_DIR}/${PLAN_FILE}")"
  cp "${REPO_ROOT}/${PLAN_FILE}" "${WORKTREE_DIR}/${PLAN_FILE}"
  echo "  Copied $PLAN_FILE into worktree (not present in the branch checkout)"
fi

# --- Sync the loop templates into the worktree on every run ---
# loop/ is gitignored so the worktree's loop/ dir starts empty. Re-copying each
# run means edits to the canonical loop.sh / prompt.txt propagate immediately.
mkdir -p "${WORKTREE_DIR}/loop"
cp "${SCRIPT_DIR}/loop.sh" "${WORKTREE_DIR}/loop/loop.sh"
cp "${SCRIPT_DIR}/prompt.txt" "${WORKTREE_DIR}/loop/prompt.txt"

# --- Print follow-up instructions on any exit path ---
print_followup() {
  echo ""
  echo "─── Next steps for $BRANCH ───"
  echo "  Merge:    git merge $BRANCH"
  echo "  Cleanup:  git worktree remove loop/worktrees/$WORKTREE_NAME"
  echo "  Resume:   bash loop/loop-worktrees.sh $PLAN_FILE [remaining_iters]"
}
trap print_followup EXIT

# --- Invoke the inner loop inside the worktree ---
# Its stdout/stderr inherit this terminal — every iteration prints live.
# PLAN_FILE, AUDIT_EVERY, and RESUME_ID pass through as env vars / args.
# The inner loop's git push uses `git branch --show-current`, which in the
# worktree is the worktree's branch — so pushes go to $BRANCH automatically.
INNER_EXIT=0
(
  cd "$WORKTREE_DIR"
  export PLAN_FILE
  [ -n "${AUDIT_EVERY:-}" ] && export AUDIT_EVERY
  if [ -n "${RESUME_ID:-}" ]; then
    bash "loop/loop.sh" "$MAX" "$RESUME_ID"
  else
    bash "loop/loop.sh" "$MAX"
  fi
) || INNER_EXIT=$?

exit $INNER_EXIT
