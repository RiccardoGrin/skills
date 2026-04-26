#!/usr/bin/env bash
# Watchdog companion for loop.sh.
# Polls the sentinel file the loop writes for each claude invocation; if the
# session's transcript JSONL stops growing for IDLE_TIMEOUT seconds, kills the
# claude process tree. The loop's existing retry-on-error path then spins up a
# fresh session on the same iteration.
#
# This script is not invoked directly — loop.sh launches it in the background
# and reaps it on EXIT.
#
# Env:
#   IDLE_TIMEOUT   seconds of transcript silence before kill (default 1200 = 20 min)
#   POLL_INTERVAL  seconds between checks (default 60)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SENTINEL="$SCRIPT_DIR/.current_session"
IDLE_TIMEOUT="${IDLE_TIMEOUT:-1200}"
POLL_INTERVAL="${POLL_INTERVAL:-60}"

# Cross-platform process-tree kill. Critical: on Windows, killing claude alone
# leaves descendant Bash processes alive (observed: a stuck `until grep ...; do
# sleep 2; done` polling loop survived its parent claude's death). taskkill /T
# walks the tree; Unix uses pkill -P then kill.
kill_tree() {
  local pid=$1
  if command -v taskkill >/dev/null 2>&1; then
    taskkill //T //F //PID "$pid" >/dev/null 2>&1 || true
  else
    pkill -P "$pid" 2>/dev/null || true
    kill "$pid" 2>/dev/null || true
  fi
}

# Cross-platform mtime as epoch seconds (GNU stat vs BSD stat differ on flags).
mtime() {
  stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null
}

while :; do
  sleep "$POLL_INTERVAL"

  # Sentinel empty means "no session active" — between iterations, or loop just started.
  [ -s "$SENTINEL" ] || continue

  # Sentinel format: "<pid> <session_id>" on a single line.
  read -r PID SID < "$SENTINEL" || continue
  [ -n "${PID:-}" ] && [ -n "${SID:-}" ] || continue

  # If claude already exited (cleanly or otherwise), nothing to police.
  kill -0 "$PID" 2>/dev/null || continue

  # Transcript path varies by OS encoding of the project cwd. Globbing by session
  # ID is platform-agnostic and session IDs are UUIDs (collision-free).
  TRANSCRIPT=$(find "$HOME/.claude/projects" -maxdepth 2 -name "${SID}.jsonl" 2>/dev/null | head -1)

  if [ -n "${TRANSCRIPT:-}" ] && [ -f "$TRANSCRIPT" ]; then
    LAST=$(mtime "$TRANSCRIPT")
  else
    # Transcript not yet created — fall back to sentinel write time so we still
    # bound startup hangs (claude wedged before producing any output).
    LAST=$(mtime "$SENTINEL")
  fi
  [ -n "${LAST:-}" ] || continue

  NOW=$(date +%s)
  IDLE=$((NOW - LAST))
  if [ "$IDLE" -ge "$IDLE_TIMEOUT" ]; then
    # Re-read sentinel right before kill — defends the narrow window where
    # claude exited cleanly, the OS recycled its PID to an unrelated process,
    # and the loop hasn't yet cleared the sentinel. If PID/SID changed or the
    # sentinel was cleared, abort the kill.
    CHECK_PID=""; CHECK_SID=""
    read -r CHECK_PID CHECK_SID < "$SENTINEL" 2>/dev/null || true
    if [ "$CHECK_PID" != "$PID" ] || [ "$CHECK_SID" != "$SID" ]; then
      continue
    fi
    echo "[watchdog] PID $PID (session $SID) idle ${IDLE}s ≥ ${IDLE_TIMEOUT}s — killing process tree" >&2
    kill_tree "$PID"
    # Clear sentinel so we don't double-kill the corpse on the next tick.
    : > "$SENTINEL"
  fi
done
