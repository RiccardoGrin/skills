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
| `initializing-projects` | Beta | Generates a tailored, self-maintaining CLAUDE.md for new projects through auto-detection and interviews |
| `looping-tasks` | Beta | Generates autonomous loop infrastructure for executing implementation plans across multiple Claude sessions |

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
