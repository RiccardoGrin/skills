---
name: being-careful
description: Activates safety hooks that block dangerous shell commands for the rest of the session — rm -rf, DROP TABLE, force-push, hard reset, kubectl delete, and other destructive operations. Use when touching production, working with sensitive data, or doing risky operations where an accidental destructive command could cause harm
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qEi '(rm\\s+-(r|f|rf|fr)\\b|rm\\s+--force|rmdir\\s+/)'; then echo 'BLOCKED: destructive file deletion. Use trash or targeted rm instead.' >&2; exit 2; fi && if echo \"$CLAUDE_TOOL_INPUT\" | grep -qEi '(DROP\\s+(TABLE|DATABASE|SCHEMA|INDEX)|TRUNCATE\\s+TABLE|DELETE\\s+FROM\\s+\\S+\\s*(;|$))'; then echo 'BLOCKED: destructive SQL operation. Review and run manually.' >&2; exit 2; fi && if echo \"$CLAUDE_TOOL_INPUT\" | grep -qEi '(push\\s+.*(\\s+--force\\b|\\s+-f\\b)|push\\s+-f\\b)'; then echo 'BLOCKED: force-push. Use --force-with-lease.' >&2; exit 2; fi && if echo \"$CLAUDE_TOOL_INPUT\" | grep -qEi '(reset\\s+--hard|clean\\s+-f|checkout\\s+--\\s+\\.)'; then echo 'BLOCKED: destructive git operation. Stash or commit first.' >&2; exit 2; fi && if echo \"$CLAUDE_TOOL_INPUT\" | grep -qEi '(branch\\s+-D\\b)'; then echo 'BLOCKED: force branch deletion. Use -d for safe delete.' >&2; exit 2; fi && if echo \"$CLAUDE_TOOL_INPUT\" | grep -qEi '(kubectl\\s+delete|kubectl\\s+.*--force)'; then echo 'BLOCKED: kubectl delete/force. Review and run manually.' >&2; exit 2; fi && if echo \"$CLAUDE_TOOL_INPUT\" | grep -qEi '(docker\\s+(system|volume|container)\\s+prune)'; then echo 'BLOCKED: docker prune. Run manually if intended.' >&2; exit 2; fi"
---

# Being Careful

Activates session-scoped safety hooks that block dangerous shell commands.
Use this when working near production systems, sensitive data, or doing anything where a misfire could cause real damage.

## What Gets Blocked

| Pattern | Why | Safe Alternative |
|---------|-----|-----------------|
| `rm -rf`, `rm -f`, `rm --force` | Irreversible file deletion | `trash`, targeted `rm` on specific files |
| `DROP TABLE`, `TRUNCATE`, bulk `DELETE FROM` | Destructive SQL | Review and run manually |
| `git push --force`, `git push -f` | Overwrites remote history | `git push --force-with-lease` |
| `git reset --hard` | Discards uncommitted work | `git stash` then reset |
| `git clean -f` | Deletes untracked files | `git stash -u` |
| `git checkout -- .` | Discards all working changes | Stash or commit first |
| `git branch -D` | Force-deletes branch | `git branch -d` (safe delete) |
| `kubectl delete`, `kubectl --force` | Destroys cluster resources | Review and run manually |
| `docker system/volume/container prune` | Removes all stopped containers/volumes | Run manually with filters |

## How It Works

The skill registers a PreToolUse hook on Bash that inspects each command before execution.
If a dangerous pattern is matched, the command is blocked (exit code 2) and Claude sees the reason in stderr.
Claude can then suggest a safer alternative.

The hooks are **session-scoped** — they activate when you invoke `/being-careful` and last until the session ends.
They do not affect other sessions or persist between sessions.

## Gotchas

- The patterns use regex matching, so they may occasionally match in string literals or comments within commands. If a legitimate command is blocked, you can run it manually outside Claude.
- `git push --force-with-lease` is intentionally allowed — it's the safe alternative to force-push.
- The hook does not block `rm` without `-rf`/`-f` flags — targeted file removal is still permitted.
- SQL patterns match case-insensitively, so `drop table` and `DROP TABLE` are both caught.
