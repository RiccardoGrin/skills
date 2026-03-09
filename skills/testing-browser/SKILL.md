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
| `scripts/snapshot.py` | Accessibility tree snapshot (LLM-friendly) | `python snapshot.py URL` |
| `scripts/screenshot.py` | Screenshot + accessibility tree + console errors | `python screenshot.py URL` |
| `scripts/with_server.py` | Server lifecycle wrapper | `python with_server.py --cmd "npm start" --port 3000 -- CMD` |

## Workflow

```
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
| Debugging layout/content | `snapshot.py` | Investigating what the page contains |
| Visual verification, bug reports | `screenshot.py` | Need to see the page, full diagnostic dump |
| Multi-step flows (login, forms) | Custom Playwright script | Agent writes directly |

For loop agent VERIFY phases, `verify.py` is the primary tool — clear pass/fail with details.

### Phase 4: Write and Run Verification

#### verify.py (most common)

```bash
# Server already running
python verify.py http://localhost:3000 --assert "text:Welcome" --assert "no-console-errors"

# With server lifecycle
python with_server.py --cmd "npm start" --port 3000 -- \
    python verify.py http://localhost:3000 --assert "text:Welcome" --assert "no-console-errors"
```

**Available assertions:**

| Assertion | Checks |
|-----------|--------|
| `text:EXPECTED` | Page contains visible text |
| `no-text:UNEXPECTED` | Page does NOT contain text |
| `title:EXPECTED` | Page title contains substring |
| `visible:SELECTOR` | CSS selector matches a visible element |
| `hidden:SELECTOR` | Element is hidden or absent |
| `count:SELECTOR:N` | Exactly N elements match selector |
| `url:PATTERN` | Current URL contains pattern |
| `no-console-errors` | No console.error() calls during load |
| `status:CODE` | HTTP response status code matches |

Read `references/assertion-patterns.md` for framework-specific recipes.

#### snapshot.py (debugging)

```bash
python snapshot.py http://localhost:3000
python snapshot.py http://localhost:3000 --selector "#main-content"
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
python screenshot.py http://localhost:3000 --output screenshot.png
python screenshot.py http://localhost:3000 --full-page --output full.png
python screenshot.py http://localhost:3000 --selector "#main-content" --output main.png
```

Saves the screenshot and prints the accessibility tree + any console errors to stdout.
When `--selector` is provided, both the visual screenshot and the accessibility tree are scoped to that element.

#### SPA / Client-Rendered Apps

All scripts use `wait_until="load"` which fires after initial HTML and resources load, but potentially before client-side JavaScript finishes rendering or performing redirects.
For React, Next.js, and other SPA frameworks:

- **`text:` and `visible:` assertions in `verify.py` handle this** — they internally wait up to 5s for elements to appear
- **`url:` assertions check immediately** — they will miss client-side redirects. For redirect testing, use a custom script with `page.wait_for_url("**/path", timeout=10000)`
- **`screenshot.py` visual captures may be blank** for pages that redirect or render client-side — use `--selector` to wait for a specific element, or use a custom script for redirect pages
- **`snapshot.py`** captures the accessibility tree at page load. For async content, add a `--selector` that only appears after loading completes, which forces the script to wait

#### Custom Playwright Scripts

For complex flows, write a Playwright script directly. Focus on patterns the built-in scripts can't handle:

**Waiting for async state** — assert after dynamic content settles:

```python
page.goto("http://localhost:3000/dashboard")
page.locator(".loading-spinner").wait_for(state="hidden", timeout=10000)
assert page.locator("[data-testid=metrics]").count() > 0
print("PASS: Dashboard loaded with metrics")
```

**Testing across navigations** — multi-page flows where state carries over:

```python
page.goto("http://localhost:3000/cart")
page.click("button:has-text('Checkout')")
page.wait_for_url("**/checkout")
page.fill("#address", "123 Main St")
page.click("button:has-text('Place Order')")
page.wait_for_url("**/confirmation")
assert page.locator(".order-number").is_visible()
print("PASS: Checkout flow completes end-to-end")
```

**Canvas/WebGL verification** — checking non-DOM content via pixel sampling:

```python
page.goto("http://localhost:3000/game")
page.wait_for_timeout(2000)  # let canvas render
screenshot = page.locator("canvas").screenshot()
from PIL import Image; import io
img = Image.open(io.BytesIO(screenshot))
center = img.getpixel((img.width // 2, img.height // 2))
assert center != (0, 0, 0, 0), "Canvas is not blank"
print("PASS: Canvas rendered content")
```

See `references/assertion-patterns.md` for login flows and other common patterns.

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
| Screenshots for every verification | Use `verify.py` for pass/fail; screenshots only for visual debugging |
| Exact text assertions for dynamic content | Use `visible:SELECTOR` for elements, `text:` for stable labels |
| Full test suites in VERIFY | VERIFY is for quick smoke checks; full suites belong in CI |
| Hardcoding ports | Read port from project config or use framework defaults |
| Persistent browser state between runs | Fresh browser per verification is simpler and more correct |
