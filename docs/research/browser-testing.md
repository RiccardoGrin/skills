---
summary: 'Research on browser testing approaches for agent-driven UI verification'
read_when:
  - 'Creating or updating the testing-browser skill'
  - 'Adding browser testing capabilities to agent workflows'
---

# Browser Testing Research for Agent-Driven UI Verification

## Problem Statement

Loop agents executing implementation plans need to verify UI behavior — not just "does it build" but "does the signup form work, does the modal close, does the error message appear." We need a self-contained skill (no MCP dependency) that enables agents to start dev servers, navigate pages, take screenshots, inspect DOM, capture console logs, and verify UI behavior.

## Approaches Evaluated

### 1. Anthropic's webapp-testing Skill

**What it is:** Official Anthropic skill providing Python Playwright scripts for testing local web apps.

**Architecture:** Write-and-run pattern — agent writes a Python script using `sync_playwright()`, runs it, reads output. Includes `scripts/with_server.py` for server lifecycle management and a decision tree (static HTML vs dynamic webapp).

**Strengths:**
- Simple mental model: write script, run script, read output
- Server lifecycle helper handles multi-server setups (backend + frontend)
- Reconnaissance-then-action pattern (screenshot/DOM inspect before acting)
- No external dependencies beyond Playwright

**Limitations:**
- No state persistence between script runs — each script launches a fresh browser
- No accessibility tree snapshots — relies on raw DOM or screenshots
- Limited to headless Chromium
- Context-heavy: scripts are "very large" per its own docs and SKILL.md warns against reading source
- No structured data extraction — agent must parse raw HTML/screenshots
- No integration with loop agent VERIFY phases
- Generic — doesn't encode testing-specific patterns (assertions, test reporting)

### 2. Playwright MCP Server (@playwright/mcp)

**What it is:** Microsoft's official MCP server exposing 25+ browser tools via Model Context Protocol.

**Architecture:** Accessibility-tree-first — returns 2-5KB structured snapshots instead of screenshots. Agent sends tool calls, MCP server executes in browser, returns structured results.

**Strengths:**
- Accessibility tree snapshots are 10-100x more token-efficient than screenshots
- Deterministic element references (no brittle selectors)
- Official Microsoft support, actively maintained
- Cross-browser (Chromium, Firefox, WebKit)
- Persistent browser state across tool calls

**Limitations:**
- Requires MCP infrastructure — adds external dependency
- Each tool call is a round-trip (slower for multi-step flows)
- Verbose tool schemas consume tokens
- Not self-contained — depends on MCP client support in the agent runtime

**Verdict:** Excellent technology but MCP dependency violates our self-contained skill requirement.

### 3. Playwright Agents (v1.56+, October 2025)

**What it is:** Built-in AI agents in Playwright: Planner (explores app, writes test specs), Generator (converts specs to tests), Healer (auto-fixes failing tests).

**Architecture:** Agentic loop with three specialized agents. Planner creates markdown specs, Generator produces Playwright test files, Healer repairs failures.

**Strengths:**
- Native Playwright integration — no additional dependencies
- Planner creates human-readable test plans
- Generator verifies selectors live during generation
- Healer provides self-healing test maintenance
- Integrates with VS Code, Claude Code, OpenCode

**Limitations:**
- Designed for test generation workflows, not ad-hoc UI verification during development
- Heavy — initializes entire agent infrastructure for each use
- Requires VS Code 1.105+ for full agentic experience
- Overkill for "verify this one thing works" during loop agent VERIFY phase

**Verdict:** Great for dedicated QA workflows but too heavy for inline verification during implementation loops.

### 4. Stagehand (by Browserbase)

**What it is:** TypeScript SDK adding AI primitives (`act()`, `extract()`, `observe()`) on top of Playwright.

**Architecture:** Hybrid — deterministic Playwright for known steps + AI for dynamic elements. v3 is "AI-native from the ground up." Has `agent()` method for autonomous multi-step tasks.

**Strengths:**
- "Playwright with an AI brain" — familiar API with AI augmentation
- Structured data extraction via Zod schemas
- 500K+ weekly downloads, production-proven
- Low maintenance (<5% breakage/month vs Playwright's 15-25%)

**Limitations:**
- TypeScript/JavaScript only
- LLM API costs scale with volume ($20-200/1000 tasks)
- Requires Browserbase cloud for full features
- External dependency we don't control

**Verdict:** Strong for production browser automation but adds LLM API dependency and cloud coupling. Not suitable for a self-contained skill.

### 5. Browser-Use (Python)

**What it is:** Open-source Python library for fully autonomous browser agents.

**Architecture:** Full agent loop — LLM receives task + page state (DOM + screenshot), decides actions, Playwright executes, observes results, loops until complete.

**Strengths:**
- Natural language task descriptions
- Multi-tab, multi-page workflows
- 3-5x faster task completion than generic approaches

**Limitations:**
- 70-85% success rate on novel tasks — too unreliable for CI/verification
- 15-30 seconds per complex task
- $200-300 per 1000 tasks in LLM costs
- Python-only

**Verdict:** Designed for web scraping/automation agents, not verification. Too slow and unreliable for testing.

### 6. Dev-Browser Skill (by Sawyer Hood)

**What it is:** Claude Code skill providing persistent browser state with adaptive script execution.

**Architecture:** Stateful server model — maintains browser state across multiple script executions. Hybrid between MCP's per-tool-call approach and write-a-full-script approach.

**Strengths:**
- Persistent pages — navigate once, interact across multiple scripts
- LLM-friendly DOM snapshots
- Outperforms both Playwright MCP (faster, cheaper) and Playwright Skill (higher success rate)
- 100% success rate in benchmarks, $0.88/run
- MIT licensed, 1.9K stars

**Limitations:**
- External dependency (not in our control)
- Architecture couples to Claude Code's skill system
- Relatively new (21 commits)

**Verdict:** Best-in-class design for agent-driven browser interaction. Key architectural insight: persistent state + adaptive scripts beats both per-call tools and fire-and-forget scripts.

### 7. Vercel agent-browser

**What it is:** Headless browser automation CLI designed for AI agents. Fast Rust CLI with Node.js fallback.

**Architecture:** CLI-first — each command is a shell invocation. Accessibility-tree-first with ref-based element targeting. Supports visual diffing, network interception, state management.

**Strengths:**
- Sub-millisecond parsing overhead (Rust)
- Accessibility tree with refs — optimized for AI consumption
- Visual diffing (pixel comparison) built in
- Network interception and mocking
- No MCP dependency — plain CLI

**Limitations:**
- External npm dependency
- Relatively new project
- CLI-per-action model can be token-heavy for complex flows

**Verdict:** Strong CLI-first design but still an external dependency.

### 8. OpenAI's CDP Approach (Harness Engineering Article)

**What it is:** OpenAI wired Chrome DevTools Protocol directly into their agent runtime for DOM snapshots, screenshots, and navigation. Used to build a 1M-line product from an empty repo.

**Architecture:** Direct CDP integration into agent environment. Compare pre/post-task snapshots, observe runtime events, apply fixes in a loop.

**Strengths:**
- No external dependencies — CDP is built into Chromium
- Snapshot comparison enables automated regression detection
- Tight integration with agent workflow

**Limitations:**
- Requires custom CDP integration code
- Low-level — agents must reason about raw protocol messages
- Not a reusable library/tool

**Verdict:** The principle (direct CDP, snapshot comparison) is sound. The implementation is custom infrastructure, not a packaged tool.

## Synthesis: What Works for Our Use Case

### Requirements
1. Self-contained skill (no MCP dependency)
2. Works in loop agent VERIFY phases
3. Can: start dev server, navigate, screenshot, inspect DOM, capture console, verify behavior
4. Production-grade reliability
5. Minimal token overhead

### Key Insights from Research

1. **Accessibility trees beat screenshots for agents.** Playwright MCP, Vercel agent-browser, and Dev-Browser all converge on this. Structured snapshots are 10-100x more token-efficient and enable deterministic element targeting.

2. **Persistent browser state matters.** Dev-Browser's key insight: navigate once, interact many times. The write-a-fresh-script-each-time pattern (webapp-testing) wastes time on repeated navigation and setup.

3. **The hybrid approach wins.** Production teams use deterministic Playwright for predictable steps + AI for dynamic parts. Our skill should produce deterministic Playwright scripts, not rely on AI-driven element discovery.

4. **Server lifecycle management is solved.** Anthropic's `with_server.py` pattern is good — wait for port, manage process lifecycle, support multiple servers.

5. **CLI tools are more token-efficient than MCP for coding agents.** Playwright MCP's own docs note this. A skill that generates and runs scripts is more efficient than per-tool-call interaction.

## Recommended Approach

**Build a Playwright-based skill using the write-and-run pattern with these improvements over webapp-testing:**

1. **Accessibility tree snapshots** — Include a helper script that returns structured accessibility trees (using Playwright's `page.accessibility.snapshot()`) instead of forcing agents to parse raw HTML or screenshots. This is the single biggest improvement.

2. **Assertion helpers** — Provide a small script that takes a URL + assertions (element visible, text matches, console has no errors) and returns pass/fail with details. This enables one-line verification in VERIFY phases.

3. **Server lifecycle** — Reuse the `with_server.py` pattern (port waiting, multi-server support).

4. **Console log capture** — Built-in capture of console errors/warnings during navigation (agents need this for debugging).

5. **Screenshot with annotation** — Screenshot helper that also dumps the accessibility tree alongside the image, so the agent gets both visual and structured data.

6. **Loop integration** — Document the single-line VERIFY pattern: `python scripts/verify.py --url http://localhost:3000 --assert "text:Welcome" --assert "no-console-errors"`.

**Do NOT include:**
- MCP server/client code
- AI-driven element discovery (Stagehand/Browser-Use approach)
- Full test generation (Playwright Agents approach)
- Persistent browser daemon (adds complexity; fresh browser per verification is fine for correctness)

**Pattern:** Guided Workflow (same as enforcing-architecture). The skill helps agents write verification scripts, not just provides generic helpers.
