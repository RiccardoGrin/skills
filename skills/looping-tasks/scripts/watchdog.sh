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

# `set -e` deliberately omitted: a transient ps/stat/find failure inside the
# poll loop must not kill the watchdog (the loop relies on it staying alive
# for the entire run). The `|| true` / `|| continue` discipline below is
# load-bearing — preserve it on any future edit.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SENTINEL="$SCRIPT_DIR/.current_session"
IDLE_TIMEOUT="${IDLE_TIMEOUT:-1200}"
POLL_INTERVAL="${POLL_INTERVAL:-60}"

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
    CHECK_PID=""; CHECK_WINPID=""; CHECK_SID=""
    read -r CHECK_PID CHECK_WINPID CHECK_SID < "$SENTINEL" 2>/dev/null || true
    if [ "$CHECK_PID" != "$PID" ] || [ "$CHECK_SID" != "$SID" ]; then
      continue
    fi
    # WINPID-recycle defense: if the MSYS process is still alive but its
    # mapped Windows PID changed since sentinel write (MSYS reaped + spawned
    # a fresh claude reusing the bash slot, or the OS recycled the WINPID to
    # an unrelated process), the WINPID we have is stale. Re-derive from the
    # still-live MSYS PID and abort the kill if the mapping moved — better a
    # missed kill than `taskkill` shooting the user's IDE.
    CURRENT_WINPID=$(ps -p "$PID" -o winpid= 2>/dev/null | tr -d '[:space:]')
    if [ -n "$CURRENT_WINPID" ] && [ "$WINPID" != "0" ] && [ "$CURRENT_WINPID" != "$WINPID" ]; then
      echo "[watchdog] PID $PID winpid changed ($WINPID → $CURRENT_WINPID) — aborting kill" >&2
      continue
    fi
    echo "[watchdog] PID $PID (winpid $WINPID, session $SID) idle ${IDLE}s ≥ ${IDLE_TIMEOUT}s — killing process tree" >&2
    kill_tree "$PID" "$WINPID"
    # Clear sentinel so we don't double-kill the corpse on the next tick.
    : > "$SENTINEL"
    # Marker the loop reads on retry so the recovery banner labels the cause as
    # "watchdog timeout" instead of a generic non-zero exit. Loop deletes it
    # immediately after consuming.
    touch "$SCRIPT_DIR/.watchdog_killed"
    echo "[watchdog] kill issued — loop will sleep 60s and retry the iteration" >&2
  fi
done
