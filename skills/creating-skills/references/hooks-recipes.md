---
summary: Hook recipes and reference for .claude/settings.json
read_when:
  - Setting up hooks in skills or understanding hook patterns
  - Reviewing hook patterns for Claude Code
---

# Hooks Recipes

Hooks live under a `hooks` key in settings files or skill frontmatter. The full structure:

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

## Hook Locations

Hooks can be defined in multiple locations. All matching hooks from all locations run in parallel and are deduplicated.

| Location | Scope | Committable? |
|----------|-------|-------------|
| `~/.claude/settings.json` | All projects (global) | No, machine-local |
| `.claude/settings.json` | Single project | Yes, commit to git |
| `.claude/settings.local.json` | Single project | No, gitignored |
| Skill/agent frontmatter | While skill is active | Yes, in the skill file |

## Hook Environment Variables

Claude Code provides context to hooks in two ways:

**JSON on stdin:** Every hook receives a JSON object on stdin with full context including `tool_name`, `tool_input`, `session_id`, `cwd`, and more. For complex hooks, read this with `jq` or your language's JSON parser.

**Convenience environment variables** for simple one-liners:

| Variable | Description |
|----------|-------------|
| `$CLAUDE_FILE_PATH` | Absolute path to the file being written/edited. Available in PostToolUse hooks for Write and Edit tools. |
| `$CLAUDE_TOOL_INPUT` | The full input passed to the tool (e.g., the bash command string). Available in PreToolUse hooks. |

Paths are absolute and properly escaped. If your hook command uses these variables, quote them to handle spaces in paths.

**Exit codes:**
- **Exit 0** = allow (tool proceeds normally)
- **Exit 2** = block (tool call prevented, stderr shown to Claude as feedback)
- **Other non-zero** = non-blocking error (logged silently, tool still runs)

## Table of Contents

- [PostToolUse: Auto-Format](#posttooluse-auto-format)
- [PreToolUse: Git Safety](#pretooluse-git-safety)
- [Stop Hook: Self-Review](#stop-hook-self-review)
- [Common Patterns from the Community](#common-patterns-from-the-community)
- [Other Hook Events](#other-hook-events)

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
      "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE '(push\\s+.*\\s+(--force|-f\\b)|reset\\s+--hard|clean\\s+-f|checkout\\s+--\\s|branch\\s+-D)'; then echo 'BLOCKED: dangerous git operation' >&2; exit 2; fi"
    }
  ]
}
```

This catches `git push --force`, `git push -f`, `git reset --hard`, `git clean -f`, `git checkout -- .`, and `git branch -D`.
The hook writes to stderr and exits with code 2 to block execution. Exit 2 is the blocking exit code — exit 1 would only log a warning without preventing the command.

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

**Auto-commit (not recommended):** Some developers use a Stop hook to auto-commit after each Claude turn. This creates rollback points but produces meaningless commit messages and `git add -A` is indiscriminate. For autonomous loops, the loop prompt already commits with descriptive messages — prefer that approach. If you need crash recovery, use branch checkpoints or `git stash` instead.

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

## Other Hook Events

The recipes above cover the most common hooks. Claude Code supports 17 hook events total. For the full reference, see https://code.claude.com/docs/en/hooks

| Event | When it fires |
|-------|--------------|
| `SessionStart` | Claude Code session begins |
| `SessionEnd` | Session ends |
| `UserPromptSubmit` | User submits a prompt (can modify/reject it) |
| `PreToolUse` | Before a tool call executes |
| `PostToolUse` | After a tool call completes successfully |
| `PostToolUseFailure` | After a tool call fails |
| `PermissionRequest` | When a permission prompt is shown |
| `Notification` | When Claude sends a notification |
| `SubagentStart` | When a subagent (Task tool) starts |
| `SubagentStop` | When a subagent stops |
| `Stop` | When Claude finishes its turn |
| `TeammateIdle` | When a teammate agent goes idle |
| `TaskCompleted` | When a task in the task list is completed |
| `ConfigChange` | When settings or config change |
| `WorktreeCreate` | When a git worktree is created |
| `WorktreeRemove` | When a git worktree is removed |
| `PreCompact` | Before conversation context is compacted |
