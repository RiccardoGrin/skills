---
name: testing-browser
description: Guides browser-based UI verification using Playwright. Covers server lifecycle, accessibility snapshots, screenshots, and assertion-based verification. Use when verifying UI behavior, testing web apps, or adding browser checks to loop agent VERIFY phases
---

# Testing Browser

Verify web UI behavior with Playwright — start servers, take screenshots, inspect accessibility trees, and run assertions.
Self-contained scripts, no MCP dependency.
Designed for loop agent VERIFY phases but works standalone.

## Reference Files

| File | Read When |
|------|-----------|
| `references/assertion-patterns.md` | Choosing assertions for a specific framework or UI pattern |

## Prerequisites

Playwright must be installed:

```bash
pip install playwright && python -m playwright install chromium
```

All scripts use only Playwright + Python standard library.

> **Note:** Use `python -m playwright` instead of bare `playwright` — pip user installs may not add the script to PATH.

## Scripts

| Script | Purpose | Quick Example |
|--------|---------|---------------|
| `scripts/verify.py` | Pass/fail assertions against a URL | `python verify.py URL --assert "text:Welcome"` |
| `scripts/interact.py` | Multi-step browser flows (click, fill, assert) | `python interact.py URL --fill "#email=test@test.com" --click "#submit" --assert "text:Welcome"` |
| `scripts/snapshot.py` | Accessibility tree snapshot (LLM-friendly) | `python snapshot.py URL --wait-for "h1"` |
| `scripts/screenshot.py` | Screenshot + accessibility tree + console errors | `python screenshot.py URL --wait-for "h1"` |
| `scripts/with_server.py` | Server lifecycle wrapper | `python with_server.py --cmd "npm start" --port 3000 -- CMD` |

### Common flags (all scripts except with_server.py)

| Flag | Purpose |
|------|---------|
| `--viewport WIDTHxHEIGHT` | Set viewport size (e.g., `--viewport 375x812`) |
| `--device NAME` | Use a Playwright device preset (e.g., `--device "iPhone 14"`) |
| `--dismiss-dialogs` | Silently dismiss JS dialogs (default: auto-dismiss with stderr warning) |
| `--timeout MS` | Navigation/action timeout (default: 10000) |
| `--use-chrome` | Launch real Chrome with persistent profile — sessions survive restarts (see below) |
| `--chrome-port PORT` | Connect to running Chrome via CDP (less reliable than `--use-chrome`) |
| `--console` | Print detailed console log with timestamps, source locations, and stack traces |

## Key Concept: `--wait-for` vs `--selector`

Most web apps (React, Next.js, Vue, SPA frameworks) render content with client-side JavaScript **after** the initial page load.
Without waiting, screenshots and snapshots capture a blank or partially-rendered page.

| Flag | Purpose | Affects what is captured? |
|------|---------|--------------------------|
| `--wait-for SELECTOR` | Pauses until the element is visible, confirming JS has rendered | **No** — full page is still captured |
| `--selector SELECTOR` | Scopes both the capture and accessibility tree to this element | **Yes** — only that element is captured |

**Default to including `--wait-for`** with `screenshot.py` and `snapshot.py`.
It is harmless on static sites and essential for SPAs.
Pick a stable element that only appears after the page renders (e.g., `h1`, `main`, `nav`, `[data-testid=app]`).

`verify.py` also supports `--wait-for` for cases where you need to wait before running assertions (e.g., SPAs, network-dependent content).
Its `text:` and `visible:` assertions already wait up to 5s internally, so `--wait-for` is only needed for other wait conditions like `network-idle` or waiting for a specific selector before running non-waiting assertions.

You can combine both flags: `--wait-for "h1" --selector "main"` waits for h1 to appear, then captures only the main element.

## Using Real Chrome (`--use-chrome`)

All scripts support `--use-chrome` to launch a real, visible Chrome window instead of headless Chromium.
Uses a persistent `.browser-data/` profile in the current working directory — sessions (cookies, localStorage) survive across runs.

### How it works

```bash
# First run: fresh profile, opens visible Chrome
python verify.py http://localhost:3000 --use-chrome --assert "text:Welcome"

# Subsequent runs: session restored (cookies, login state preserved)
python verify.py http://localhost:3000 --use-chrome --assert "text:Dashboard"
```

- The script launches Chrome, navigates to the URL, runs assertions, and closes Chrome
- Profile data is saved to `.browser-data/` in the current working directory
- Add `.browser-data/` to your `.gitignore`

### Authenticated pages

On first run, the profile is fresh (not logged in). To establish a session:

```bash
# Script the login flow — session is saved for future runs
python interact.py http://localhost:3000/login --use-chrome \
    --fill "input[name=email]=test@test.com" \
    --fill "input[name=password]=password" \
    --click "button[type=submit]" \
    --wait "text:Dashboard" \
    --assert "text:Welcome"

# Now all future --use-chrome runs have the session
python verify.py http://localhost:3000/dashboard --use-chrome --assert "text:Dashboard"
```

### Limitations

- `--device` is ignored (can't change device emulation on real Chrome)
- `--viewport` still works
- Uses a **separate** profile from your daily Chrome — your bookmarks/extensions/accounts are not shared
- Does not require closing your regular Chrome first

### CDP alternative (`--chrome-port`)

`--chrome-port PORT` connects to an already-running Chrome via CDP. This is less reliable (requires Chrome to be started with `--remote-debugging-port`, background processes often interfere). Prefer `--use-chrome` unless you have a specific reason to use CDP. Both flags fall back to fresh Chromium on failure.

## Enhanced Console Output (`--console`)

All scripts capture console messages and uncaught page errors. The `--console` flag enables detailed output:

```
<console-log count="5">
  [0.123s] [log] App initialized @ localhost:3000/main.js:42:10
  [0.456s] [warn] Deprecated API used @ localhost:3000/api.js:15:3
  [0.789s] [error] Failed to fetch user data @ localhost:3000/store.js:88:5
</console-log>

<page-errors count="1">
  [1.234s] TypeError: Cannot read properties of undefined (reading 'name')
    at UserProfile (localhost:3000/components/UserProfile.js:23:15)
    at renderWithHooks (localhost:3000/node_modules/react-dom/...)
</page-errors>
```

**Without `--console`**: only console errors and uncaught page errors are shown.

**With `--console`**: all messages (log, warn, error, info, debug) are shown with:
- **Timestamps** relative to page load (e.g., `[0.123s]`)
- **Source locations** (file:line:col)
- **Uncaught exceptions** with full stack traces (always shown, even without `--console`)

Use `--console` when debugging issues -- the timestamps help correlate events and the source locations point directly to problematic code.

## Workflow

```text
- [ ] Phase 1: Detect what to test
- [ ] Phase 2: Ensure Playwright is available
- [ ] Phase 3: Choose verification approach
- [ ] Phase 4: Write and run verification
- [ ] Phase 5: Integrate with loops (optional)
```

### Phase 1: Detect What to Test

Scan the project for:
- Web framework and dev server command (`package.json` scripts, `manage.py runserver`, etc.)
- Port the dev server uses (read from config or framework defaults)
- Key pages to verify (routes, entry points)
- Existing test infrastructure (Playwright already configured? Cypress? Vitest browser mode?)

**If Playwright is already configured:** use the existing setup. Don't duplicate or conflict.

### Phase 2: Ensure Playwright is Available

Check and install if needed:

```bash
python -c "from playwright.sync_api import sync_playwright; print('OK')" 2>/dev/null || \
    (pip install playwright && python -m playwright install chromium)
```

### Phase 3: Choose Verification Approach

| Scenario | Script | When |
|----------|--------|------|
| Quick pass/fail check | `verify.py` | VERIFY phases, smoke tests |
| Multi-step flows (login, forms, navigation) | `interact.py` | Click, fill, assert in sequence |
| Debugging layout/content | `snapshot.py` | Investigating what the page contains |
| Visual verification, bug reports | `screenshot.py` | Need to see the page, full diagnostic dump |
| Complex/custom flows | Custom Playwright script | When interact.py actions aren't enough |

For loop agent VERIFY phases, `verify.py` (single page) or `interact.py` (multi-step) are the primary tools.

### Phase 4: Write and Run Verification

#### verify.py (most common)

```bash
# Server already running
python verify.py http://localhost:3000 --assert "text:Welcome" --assert "no-console-errors"

# With server lifecycle
python with_server.py --cmd "npm start" --port 3000 -- \
    python verify.py http://localhost:3000 --assert "text:Welcome" --assert "no-console-errors"
```

**Available assertions** (used by both `verify.py` and `interact.py`):

| Assertion | Checks |
|-----------|--------|
| `text:EXPECTED` | Page contains visible text (waits up to 5s) |
| `no-text:UNEXPECTED` | Page does NOT contain text |
| `title:EXPECTED` | Page title contains substring |
| `visible:SELECTOR` | CSS selector matches a visible element (waits up to 5s) |
| `hidden:SELECTOR` | Element is hidden or absent |
| `count:SELECTOR:N` | Exactly N elements match selector |
| `url:PATTERN` | Current URL contains pattern |
| `no-console-errors` | No console.error() calls during load |
| `no-console-warnings` | No console.warn() calls during load |
| `console-contains:TEXT` | Any console message contains text |
| `request:METHOD:PATH:STATUS` | Network request was made (e.g., `request:GET:/api/users:200`) |
| `no-failed-requests` | No 4xx/5xx responses in network log |
| `status:CODE` | HTTP response status code matches |

**Wait-for conditions** (verify.py `--wait-for`, interact.py `--wait`):

| Condition | Waits for |
|-----------|-----------|
| `SELECTOR` | CSS selector to be visible (bare selector) |
| `selector:SELECTOR` | CSS selector to be visible (explicit prefix) |
| `text:TEXT` | Visible text to appear on page |
| `network-idle` | Network to be idle (no pending requests) |

> **`url:` checks immediately** — correct for direct navigation.
> For client-side redirects, use `interact.py` with `--wait "text:Dashboard"` before `--assert "url:/dashboard"`.

Read `references/assertion-patterns.md` for framework-specific recipes.

#### interact.py (multi-step flows)

For login flows, form submissions, and multi-page navigation:

```bash
# Login flow
python interact.py http://localhost:3000/login \
    --fill "input[name=email]=test@test.com" \
    --fill "input[name=password]=password" \
    --click "button[type=submit]" \
    --wait "text:Dashboard" \
    --assert "url:/dashboard" \
    --assert "text:Welcome"

# Form with screenshot
python interact.py http://localhost:3000/settings \
    --fill "#name=New Name" \
    --select "#role=admin" \
    --click "button:has-text('Save')" \
    --wait "text:Saved" \
    --assert "text:Saved" \
    --screenshot result.png

# Mobile viewport
python interact.py http://localhost:3000 \
    --viewport 375x812 \
    --click "nav button" \
    --wait "text:Menu" \
    --assert "visible:.mobile-menu" \
    --screenshot mobile.png
```

**Ordered actions** (executed in the order they appear):

| Action | Purpose |
|--------|---------|
| `--click SELECTOR` | Click an element |
| `--fill "SEL=VALUE"` | Clear and fill an input field |
| `--select "SEL=VALUE"` | Select a dropdown option |
| `--type "SEL=VALUE"` | Type text key-by-key (for autocomplete, etc.) |
| `--wait CONDITION` | Wait for a condition (see wait-for table above) |
| `--assert ASSERTION` | Check an assertion (see assertions table above) |
| `--screenshot PATH` | Take screenshot after all actions complete |

Actions fail fast on errors (except assertions, which are collected and reported at the end).

#### snapshot.py (debugging)

```bash
# Always include --wait-for to ensure JS has rendered
python snapshot.py http://localhost:3000 --wait-for "h1"
python snapshot.py http://localhost:3000 --wait-for "nav" --selector "main"
python snapshot.py http://localhost:3000 --wait-for "h1" --console
```

Returns a YAML-like tree:

```yaml
- heading "Welcome to My App" [level=1]
- navigation "Main":
  - link "Home"
  - link "About"
- main:
  - heading "Dashboard" [level=2]
  - list:
    - listitem "Task 1"
    - listitem "Task 2"
```

#### screenshot.py (visual + diagnostic)

```bash
# Always include --wait-for to ensure JS has rendered
python screenshot.py http://localhost:3000 --wait-for "h1" --output screenshot.png
python screenshot.py http://localhost:3000 --wait-for "h1" --full-page --output full.png
python screenshot.py http://localhost:3000 --wait-for "h1" --selector "main" --output main.png
```

Saves the screenshot and prints the accessibility tree + any console errors to stdout.

- `--wait-for` waits for the element to appear, then captures the full page (or `--selector` scope).
- `--selector` scopes both the screenshot and accessibility tree to that element.
- `--full-page` captures the entire scrollable page (ignored when `--selector` is used).
- `--console` prints ALL console messages (not just errors) in a `<console-log>` section.

#### Static sites

For sites with no client-side rendering (plain HTML, Hugo, Jekyll), `--wait-for` is harmless but unnecessary.
You can omit it:

```bash
python screenshot.py http://localhost:8080 --output static.png
python snapshot.py http://localhost:8080
```

#### Custom Playwright Scripts

For flows that `interact.py` can't handle, write a Playwright script directly.
See `references/assertion-patterns.md` for custom script patterns (async state, multi-page navigation, canvas/WebGL).

> **Windows note:** Avoid non-ASCII characters (arrows, emojis) in `print()` statements in custom scripts.
> Windows consoles may fail with `'charmap' codec can't encode character`.
> Stick to ASCII or set `PYTHONIOENCODING=utf-8`.

### Phase 5: Integrate with Loops (Optional)

For loop agent VERIFY phases, add browser verification to the plan's Verify field:

```markdown
- [ ] **Add signup page** — ...
  Verify: `python with_server.py --cmd "npm start" --port 3000 -- python verify.py http://localhost:3000/signup --assert "visible:#email" --assert "visible:#password" --assert "text:Sign Up"`
```

The agent copies the Verify command, runs it, and confirms pass/fail before marking the task done.

## Anti-Patterns

| Avoid | Do Instead |
|-------|------------|
| `screenshot.py` / `snapshot.py` without `--wait-for` on SPA apps | Always include `--wait-for` — it's harmless on static sites and essential for SPAs |
| Screenshots for every verification | Use `verify.py` for pass/fail; screenshots only for visual debugging |
| Custom Playwright scripts for simple login/form flows | Use `interact.py` — it handles click, fill, wait, assert sequences |
| Exact text assertions for dynamic content | Use `visible:SELECTOR` for elements, `text:` for stable labels |
| Full test suites in VERIFY | VERIFY is for quick smoke checks; full suites belong in CI |
| Hardcoding ports | Read port from project config or use framework defaults |
| Using `--use-chrome` in automated loops | `--use-chrome` is for manual debugging; loops should use fresh headless Chromium for reproducibility |
| `--wait-for "network-idle"` on pages with WebSocket/SSE | Use `--wait-for "text:..."` or `--wait-for "selector:..."` — network-idle hangs on persistent connections |
| Retrying `--chrome-port` after repeated failures | If Chrome connection fails 2-3 times, drop `--chrome-port` and use fresh Chromium with `interact.py` for auth flows |
| Ignoring `<page-errors>` in output | Uncaught exceptions are critical — always investigate stack traces before moving on |
