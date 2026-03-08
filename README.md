# skills

Reusable agent skills for Claude Code, Cursor, Codex, and OpenCode.

## Quick Start

```bash
npx skills add RiccardoGrin/skills
```

## Available Skills

| Skill | Maturity | What it does |
|-------|----------|--------------|
| `creating-skills` | Stable | Guides creation of agent skills following best practices and the open format specification |
| `listing-docs` | Stable | Scans `docs/` for markdown front-matter and lists summaries and `read_when` hints |
| `planning` | Beta | Creates implementation-ready plans through discovery interviews, external research, and codebase analysis |
| `initializing-projects` | Beta | Generates a minimal, self-maintaining CLAUDE.md for projects through auto-detection and developer interview |
| `looping-tasks` | Beta | Generates autonomous loop infrastructure for executing implementation plans across multiple Claude sessions |
| `enforcing-architecture` | Beta | Guides setup of mechanical architecture enforcement — layer detection, dependency rules, check scripts, and hook wiring |
| `generating-game-changelogs` | Beta | Generates player-facing game changelogs from implementation plans and git history |
| `testing-browser` | Beta | Guides browser-based UI verification using Playwright — server lifecycle, accessibility snapshots, screenshots, and assertion-based verification |
| `creating-sprites` | Beta | Guides pixel-art sprite creation via OpenAI gpt-image-1.5 with automated processing |

> **Maturity** indicates development status: *Draft* (in progress), *Beta* (usable, feedback welcome), *Stable* (production-ready).

## Supported Agents

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Cursor](https://www.cursor.com/)
- [Codex](https://github.com/openai/codex)
- [OpenCode](https://opencode.ai/)

## Contributing

Open a PR with your skill in `skills/<skill-name>/` — see the `creating-skills` skill for the format.

## License

MIT
