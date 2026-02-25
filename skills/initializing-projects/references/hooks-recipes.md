---
summary: Hook recipes for .claude/settings.json
read_when:
  - Setting up hooks in .claude/settings.json
  - Reviewing hook patterns for Claude Code
---

# Hooks Recipes

## Table of Contents

- [PostToolUse: Auto-Format](#posttooluse-auto-format)
- [PreToolUse: Git Safety](#pretooluse-git-safety)
- [Stop Hook: Self-Review](#stop-hook-self-review)
- [Common Patterns from the Community](#common-patterns-from-the-community)

## PostToolUse: Auto-Format

Automatically format files after Claude writes or edits them.
The `2>/dev/null || true` suffix prevents hook failures from blocking Claude.

**Prettier (JS/TS):**
```json
{
  "matcher": "Write|Edit",
  "hooks": [
    { "type": "command", "command": "npx prettier --write $CLAUDE_FILE_PATH 2>/dev/null || true" }
  ]
}
```

**Biome (JS/TS):**
```json
{
  "matcher": "Write|Edit",
  "hooks": [
    { "type": "command", "command": "npx @biomejs/biome format --write $CLAUDE_FILE_PATH 2>/dev/null || true" }
  ]
}
```

**Ruff (Python):**
```json
{
  "matcher": "Write|Edit",
  "hooks": [
    { "type": "command", "command": "ruff format $CLAUDE_FILE_PATH 2>/dev/null || true" }
  ]
}
```

**Black (Python):**
```json
{
  "matcher": "Write|Edit",
  "hooks": [
    { "type": "command", "command": "black $CLAUDE_FILE_PATH 2>/dev/null || true" }
  ]
}
```

**gofmt (Go):**
```json
{
  "matcher": "Write|Edit",
  "hooks": [
    { "type": "command", "command": "gofmt -w $CLAUDE_FILE_PATH 2>/dev/null || true" }
  ]
}
```

**rustfmt (Rust):**
```json
{
  "matcher": "Write|Edit",
  "hooks": [
    { "type": "command", "command": "rustfmt $CLAUDE_FILE_PATH 2>/dev/null || true" }
  ]
}
```

## PreToolUse: Git Safety

Prevent dangerous git operations before they execute.
These hooks inspect the Bash command and block destructive patterns.

**Block force-push and hard reset:**
```json
{
  "matcher": "Bash",
  "hooks": [
    {
      "type": "command",
      "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE '(push.*--force|push.*-f|reset --hard|clean -f)'; then echo 'BLOCKED: dangerous git operation' >&2; exit 1; fi"
    }
  ]
}
```

This catches `git push --force`, `git push -f`, `git reset --hard`, and `git clean -f`.
The hook writes to stderr and exits non-zero to block execution.

## Stop Hook: Self-Review

Run a quick check before Claude completes its turn.
Useful for catching lint errors or type issues before the user sees "done."

**Run linter on changed files:**
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "git diff --name-only HEAD | xargs -I {} npx eslint {} 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

**Run type-checker on changed files (TypeScript):**
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "npx tsc --noEmit 2>&1 | head -20 || true"
          }
        ]
      }
    ]
  }
}
```

Keep Stop hooks fast.
If they take more than a few seconds, Claude's response feels sluggish.

## Common Patterns from the Community

**Auto-commit on task completion:**
Some developers hook into Stop to auto-commit changes after each Claude turn.
This creates a granular git history that makes it easy to revert bad changes.
Tradeoff: noisy commit history.

**Test-on-save:**
Run the nearest test file after every Write or Edit.
Catches regressions immediately but slows down multi-file refactors.
Best used selectively on critical paths.

**Notification hooks:**
Send a system notification when Claude finishes a long task.
Useful when running Claude in the background.
Platform-specific: `notify-send` on Linux, `osascript` on macOS, `powershell` on Windows.
