---
name: freezing-edits
description: Blocks all file writes and edits outside a specified directory for the rest of the session. Use when debugging, investigating, or doing exploratory work where you want to prevent accidental modifications to unrelated code. Pass the allowed directory as an argument, e.g. /freezing-edits src/components
argument-hint: <allowed-directory>
hooks:
  PreToolUse:
    - matcher: Write|Edit
      hooks:
        - type: command
          command: |
            payload=$(cat)
            file_path=$(echo "$payload" | jq -r '.tool_input.file_path // empty')
            if [ -z "$file_path" ]; then exit 0; fi
            freeze_config="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/data/freezing-edits}/freeze-config.json"
            if [ ! -f "$freeze_config" ]; then
              echo "BLOCKED: freeze is active but no allowed directory configured. Run /freezing-edits <directory> first." >&2; exit 2
            fi
            allowed_dir=$(jq -r '.allowed_dir' "$freeze_config")
            if [ -z "$allowed_dir" ]; then exit 0; fi
            case "$file_path" in
              "$allowed_dir"*) exit 0 ;;
              *) echo "BLOCKED: edit frozen. Only files under $allowed_dir are allowed. File: $file_path" >&2; exit 2 ;;
            esac
---

# Freezing Edits

Locks down file modifications to a single directory for the rest of the session.
Everything outside that directory becomes read-only to Claude.

## Usage

```
/freezing-edits src/components
```

This allows edits only to files under `src/components/` and blocks Write/Edit to anything else.

## Setup

When invoked, save the allowed directory to a config file so the hook can read it:

1. Resolve the argument to an absolute path relative to the current working directory
2. Create the config directory if needed: `${CLAUDE_PLUGIN_DATA:-$HOME/.claude/data/freezing-edits}/`
3. Write the config: `{"allowed_dir": "/absolute/path/to/directory"}`

The config file path is: `${CLAUDE_PLUGIN_DATA:-$HOME/.claude/data/freezing-edits}/freeze-config.json`

If no argument is provided, ask the user which directory to allow.

## How It Works

The skill registers a PreToolUse hook on Write and Edit tools.
Before any file modification, the hook checks whether the target file path starts with the allowed directory.
If it doesn't, the edit is blocked (exit code 2) and Claude sees which directory is allowed.

The hooks are **session-scoped** — they last until the session ends.

## Unfreezing

To remove the freeze within the same session, delete the config file:

```bash
rm "${CLAUDE_PLUGIN_DATA:-$HOME/.claude/data/freezing-edits}/freeze-config.json"
```

Or simply end the session — hooks don't persist.

## Gotchas

- The path comparison is a prefix match on absolute paths. `src/components` will also match `src/components-old/` if such a directory exists. Use trailing slashes in the config if precision matters.
- New file creation (Write) is also blocked outside the allowed directory, not just edits.
- The hook does not block Bash commands that write files (e.g., `echo > file`). It only covers Claude's Write and Edit tools. For full protection, combine with `/being-careful`.
- If you need to allow multiple directories, edit the config file to use an array and update the hook logic accordingly.
