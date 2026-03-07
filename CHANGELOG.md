**Skills — v1.0.0 "Harness Engineering"**

_Agent skills grow teeth. Mechanical enforcement replaces documentation-only rules — architecture checks run automatically, loop agents verify their own work, and browser testing joins the toolkit._

### ✨ New Skills
Three new skills bring enforcement and verification capabilities to the ecosystem.

- **Enforcing Architecture** — Guided workflow that detects project structure, interviews for layer boundaries and dependency rules, then generates check scripts and hooks that run automatically on every edit
- **Testing Browser** — Playwright-based UI verification with accessibility snapshots, screenshots, assertion helpers, and server lifecycle management. Designed for loop agent VERIFY phases
- **Generating Changelogs** — Produces player-facing changelogs from implementation plans and git history with thematic intros and system-grouped sections

### 🔄 Skill Improvements
Existing skills gain enforcement-first upgrades inspired by OpenAI's harness engineering findings.

- **Planning** — Each change spec now includes a Verify field so loop agents know HOW to verify beyond "does it build"
- **Looping Tasks** — VERIFY phase runs `/simplify` on files with substantial changes, catching quality issues automatically
- **Initializing Projects** — Detects linter configs and `ARCHITECTURE.md`, suggests PostToolUse lint hooks when a linter exists but no hook is wired, and recommends `/enforcing-architecture` for complex projects

### 🔧 Fixes & Improvements
- README now lists all nine available skills
- Fixed `creating-sprites` description (was "Gemini", now correctly says "gpt-image-1.5")
- Removed leftover `skills/skills/` empty directory
