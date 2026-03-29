# skills

Reusable agent skills for Claude Code, Cursor, Codex, and OpenCode.

## Quick Start

```bash
npx skills add RiccardoGrin/skills
```

## Available Skills

| Skill | What it does |
|-------|--------------|
| `creating-skills` | Guides creation of agent skills following best practices and the open format specification |
| `listing-docs` | Scans `docs/` for markdown front-matter and lists summaries and `read_when` hints |
| `planning` | Creates implementation-ready plans through discovery interviews, external research, and codebase analysis |
| `initializing-projects` | Generates a minimal, self-maintaining CLAUDE.md for projects through auto-detection and developer interview |
| `looping-tasks` | Generates autonomous loop infrastructure for executing implementation plans across multiple Claude sessions |
| `planning-loop` | Generates an autonomous game design loop that iteratively expands a game concept into a comprehensive vision and implementation plan |
| `enforcing-architecture` |  Guides setup of mechanical architecture enforcement — layer detection, dependency rules, check scripts, and hook wiring |
| `generating-game-changelogs` | Generates player-facing game changelogs from implementation plans and git history |
| `testing-browser` | Guides browser-based UI verification using Playwright — server lifecycle, accessibility snapshots, screenshots, and assertion-based verification |
| `creating-sprites` | Guides pixel-art sprite creation via OpenAI gpt-image-1.5 with automated processing |
| `designing-frontend` | Guides creation of high-quality frontend interfaces using proven design principles for color, typography, spacing, layout, depth, animation, and UX — covers both building and auditing |
| `transcribing-youtube` | Downloads YouTube audio, transcribes via OpenAI Whisper, and produces cached summaries — handles chunking, caching, and cleanup |
| `being-careful` | Activates session-scoped safety hooks that block dangerous shell commands (rm -rf, DROP TABLE, force-push, hard reset, kubectl delete) |
| `freezing-edits` | Blocks all file writes and edits outside a specified directory for the rest of the session |
| `reviewing-code` | Adversarial review loop — spawns independent reviewer and fixer subagents, iterating until only nitpicks remain |

## Contributing

Open a PR with your skill in `skills/<skill-name>/` — see the `creating-skills` skill for the format.

## License

MIT
