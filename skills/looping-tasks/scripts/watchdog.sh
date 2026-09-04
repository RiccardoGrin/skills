#!/usr/bin/env bash
# Watchdog companion for loop.sh.
# Polls the sentinel file the loop writes for each agent invocation; if the
# session's liveness file stops growing for IDLE_TIMEOUT seconds, kills the
# agent process tree. The loop's existing retry-on-error path then spins up a
# fresh session on the same iteration.
#
# The liveness file depends on which agent is running (loop.sh exports AGENT):
#   claude — the session transcript JSONL under ~/.claude/projects
#   codex  — $AGENT_LOG, the loop's capture of codex's event stream (codex keeps
#            no per-session file this can stat, and streams when redirected)
#
# This script is not invoked directly — loop.sh launches it in the background
# and reaps it on EXIT.
#
# Env:
#   IDLE_TIMEOUT   seconds of transcript silence before kill (default 1200 = 20 min)
#   POLL_INTERVAL  seconds between checks (default 60)

# `set -e` deliberately omitted: a transient ps/stat/find failure inside the
# poll loop must not kill the watchdog (the loop relies on it staying alive
# for the entire run). The `|| true` / `|| continue` discipline below is
# load-bearing — preserve it on any future edit.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SENTINEL="$SCRIPT_DIR/.current_session"
IDLE_TIMEOUT="${IDLE_TIMEOUT:-1200}"
POLL_INTERVAL="${POLL_INTERVAL:-60}"
# Exported by loop.sh. Defaulted here so the watchdog still behaves if it is
# ever run standalone.
AGENT="${AGENT:-claude}"
AGENT_LOG="${AGENT_LOG:-$SCRIPT_DIR/.agent-out.log}"

# Real Windows PID for an MSYS PID. Git-for-Windows `ps` is NOT procps: it has
# no -o/--format, so `ps -o winpid=` fails outright and returns empty — which is
# how the taskkill path here silently stopped running. Parse the fixed-width
# table instead (PID PPID PGID WINPID TTY UID STIME COMMAND). On real Unix
# column 4 is not a PID, so callers must keep their digits-only guard.
winpid_of() {
  ps -p "$1" 2>/dev/null | awk -v p="$1" 'NR>1 && $1==p {print $4; exit}'
}

# Cross-platform process-tree kill. On Windows we MUST do both halves:
#  - taskkill walks the Windows process tree (claude.exe + descendants), but
#    needs a real Windows PID. The MSYS PID Bash exposes via $! is fictional
#    to the OS — taskkill silently no-ops on it, the watchdog logs success,
#    and the hung process survives. The loop pre-translates and writes the
#    WINPID into the sentinel so we have it here.
#  - kill on the MSYS PID is what releases the parent bash's `wait`. Without
#    it the loop hangs even after taskkill cleans up the OS-side process,
#    because the bash wrapper is still tracking the dead MSYS handle.
# On real Unix taskkill is absent and WINPID is "0" → the kill/pkill path
# alone does the right thing on the MSYS-PID-which-is-actually-the-OS-PID.
kill_tree() {
  local msys_pid=$1
  local win_pid=$2
  if command -v taskkill >/dev/null 2>&1 && [ -n "$win_pid" ] && [ "$win_pid" != "0" ]; then
    taskkill //T //F //PID "$win_pid" >/dev/null 2>&1 || true
  fi
  pkill -P "$msys_pid" 2>/dev/null || true
  kill "$msys_pid" 2>/dev/null || true
}

# Cross-platform mtime as epoch seconds (GNU stat vs BSD stat differ on flags).
mtime() {
  stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null
}

echo "[watchdog] started (idle timeout ${IDLE_TIMEOUT}s, poll every ${POLL_INTERVAL}s)" >&2

while :; do
  sleep "$POLL_INTERVAL"

  # Sentinel empty means "no session active" — between iterations, or loop just started.
  [ -s "$SENTINEL" ] || continue

  # Sentinel format: "<msys_pid> <win_pid> <session_id>" on a single line.
  # WINPID is "0" on real Unix where the column doesn't exist (see loop.sh).
  read -r PID WINPID SID < "$SENTINEL" || continue
  [ -n "${PID:-}" ] && [ -n "${SID:-}" ] || continue

  # If claude already exited (cleanly or otherwise), nothing to police.
  kill -0 "$PID" 2>/dev/null || continue

  if [ "$AGENT" = "codex" ]; then
    LIVENESS="$AGENT_LOG"
  else
    # Transcript path varies by OS encoding of the project cwd. Globbing by session
    # ID is platform-agnostic and session IDs are UUIDs (collision-free).
    LIVENESS=$(find "$HOME/.claude/projects" -maxdepth 2 -name "${SID}.jsonl" 2>/dev/null | head -1)
  fi

  if [ -n "${LIVENESS:-}" ] && [ -s "$LIVENESS" ]; then
    LAST=$(mtime "$LIVENESS")
  else
    # Nothing written yet — fall back to sentinel write time so we still bound
    # startup hangs (the agent wedged before producing any output).
    LAST=$(mtime "$SENTINEL")
  fi
  [ -n "${LAST:-}" ] || continue

  NOW=$(date +%s)
  IDLE=$((NOW - LAST))
  if [ "$IDLE" -ge "$IDLE_TIMEOUT" ]; then
    # Re-read sentinel right before kill — defends the narrow window where the
    # agent exited cleanly, the OS recycled its PID to an unrelated process,
    # and the loop hasn't yet cleared the sentinel. If PID/SID changed or the
    # sentinel was cleared, abort the kill.
    CHECK_PID=""; CHECK_WINPID=""; CHECK_SID=""
    read -r CHECK_PID CHECK_WINPID CHECK_SID < "$SENTINEL" 2>/dev/null || true
    if [ "$CHECK_PID" != "$PID" ] || [ "$CHECK_SID" != "$SID" ]; then
      continue
    fi
    # Kill the Windows PID the MSYS PID maps to RIGHT NOW, not the one the loop
    # recorded at spawn: the two legitimately differ, so comparing them (which
    # this used to do, aborting on any difference) vetoed every kill on Windows
    # and let a wedged agent hang the loop forever.
    #
    # Measured, because it is not obvious: `codex` on PATH is an npm POSIX-shell
    # shim that `exec`s node. Under MSYS an exec keeps the MSYS PID but puts a
    # NEW Windows process behind it, so the mapping moves within the first
    # second of launch — 25308 at t=0, 6840 at t=1 in a direct test of that
    # shape, and 9244 -> 24160 in a real killed iteration. A directly-launched
    # native exe does NOT move, which is why this looks wrong until you try it
    # through the shim.
    #
    # Dropping the comparison costs nothing here: PID-recycling is already
    # covered by the sentinel re-read above (same MSYS PID, same session), and
    # that check is now the only thing standing between us and killing a
    # recycled PID — keep it. If the lookup yields nothing usable, fall back to
    # the recorded value — "0" on Unix, where taskkill is skipped anyway.
    CURRENT_WINPID=$(winpid_of "$PID" | tr -d '[:space:]') || true
    [[ "$CURRENT_WINPID" =~ ^[0-9]+$ ]] || CURRENT_WINPID="$WINPID"
    echo "[watchdog] PID $PID (winpid $CURRENT_WINPID, session $SID) idle ${IDLE}s ≥ ${IDLE_TIMEOUT}s — killing process tree" >&2
    # Marker the loop reads on retry so the recovery banner labels the cause as
    # "watchdog timeout" instead of a generic non-zero exit. Loop deletes it
    # immediately after consuming.
    #
    # BEFORE the kill, not after: the kill releases the loop's `wait`, which
    # reads this flag immediately — touching it afterwards loses that race and
    # every watchdog kill gets reported as an ordinary agent crash. A flag left
    # behind by a kill that then failed only mislabels one banner; the loop
    # clears it on read either way.
    touch "$SCRIPT_DIR/.watchdog_killed"
    kill_tree "$PID" "$CURRENT_WINPID"
    # Clear sentinel so we don't double-kill the corpse on the next tick.
    : > "$SENTINEL"
    echo "[watchdog] kill issued — loop will sleep 60s and retry the iteration" >&2
  fi
done
