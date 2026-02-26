---
summary: Hook recipes for .claude/settings.json
read_when:
  - Setting up hooks in .claude/settings.json
  - Reviewing hook patterns for Claude Code
---

# Hooks Recipes

Hooks live in `.claude/settings.json` under a `hooks` key. The full structure:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "ToolName", "hooks": [{ "type": "command", "command": "..." }] }
    ],
    "PostToolUse": [
      { "matcher": "ToolName", "hooks": [{ "type": "command", "command": "..." }] }
    ],
    "Stop": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "..." }] }
    ]
  }
}
```

Each recipe below shows the hook object that goes inside the appropriate array. The `matcher` field filters by tool name (regex). An empty `matcher` matches all tools.

## Hook Environment Variables

Claude Code sets these environment variables when hooks run:

| Variable | Description |
|----------|-------------|
| `$CLAUDE_FILE_PATH` | Absolute path to the file being written/edited. Available in PostToolUse hooks for Write and Edit tools. |
| `$CLAUDE_TOOL_INPUT` | The full input passed to the tool (e.g., the bash command string). Available in PreToolUse hooks. |

Paths are absolute and properly escaped. If your hook command uses these variables, quote them to handle spaces in paths.

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
      "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE '(push\\s+.*\\s+(--force|-f\\b)|reset\\s+--hard|clean\\s+-f|checkout\\s+--\\s|branch\\s+-D)'; then echo 'BLOCKED: dangerous git operation' >&2; exit 1; fi"
    }
  ]
}
```

This catches `git push --force`, `git push -f`, `git reset --hard`, `git clean -f`, `git checkout -- .`, and `git branch -D`.
The hook writes to stderr and exits non-zero to block execution.

## Stop Hook: Self-Review

Run a quick check before Claude completes its turn.
Useful for catching lint errors or type issues before the user sees "done."

**Run linter on changed files:**
```json
{
  "matcher": "",
  "hooks": [
    { "type": "command", "command": "git diff --name-only HEAD | xargs -I {} npx eslint {} 2>/dev/null || true" }
  ]
}
```

**Run type-checker on changed files (TypeScript):**
```json
{
  "matcher": "",
  "hooks": [
    { "type": "command", "command": "npx tsc --noEmit 2>&1 | head -20 || true" }
  ]
}
```

Keep Stop hooks fast.
If they take more than a few seconds, Claude's response feels sluggish.

## Common Patterns from the Community

**Auto-commit on task completion:**
Some developers hook into Stop to auto-commit changes after each Claude turn.
This creates a granular git history that makes it easy to revert bad changes.
Tradeoff: noisy commit history.

```json
{
  "matcher": "",
  "hooks": [
    { "type": "command", "command": "git add -A && git commit -m 'auto: Claude checkpoint' 2>/dev/null || true" }
  ]
}
```

**Test-on-save:**
Run the nearest test file after every Write or Edit.
Catches regressions immediately but slows down multi-file refactors.
Best used selectively on critical paths.

```json
{
  "matcher": "Write|Edit",
  "hooks": [
    { "type": "command", "command": "npx jest --findRelatedTests \"$CLAUDE_FILE_PATH\" --passWithNoTests 2>/dev/null || true" }
  ]
}
```

**Notification hooks:**
Send a system notification when Claude finishes a long task.
Useful when running Claude in the background.
Platform-specific: `notify-send` on Linux, `osascript` on macOS, `powershell` on Windows.

Linux:
```json
{
  "matcher": "",
  "hooks": [
    { "type": "command", "command": "notify-send 'Claude Code' 'Task finished' 2>/dev/null || true" }
  ]
}
```

macOS:
```json
{
  "matcher": "",
  "hooks": [
    { "type": "command", "command": "osascript -e 'display notification \"Task finished\" with title \"Claude Code\"' 2>/dev/null || true" }
  ]
}
```
