# Assertion Patterns by Framework

## Table of Contents

- [Custom Playwright Scripts](#custom-playwright-scripts)
- [Next.js / React](#nextjs--react)
- [Static Sites](#static-sites)
- [Form Validation](#form-validation)
- [Authentication Flows](#authentication-flows)
- [Tables and Lists](#tables-and-lists)
- [Error States](#error-states)
- [API Verification](#api-verification)
- [Console Inspection](#console-inspection)
- [Responsive / Mobile](#responsive--mobile)
- [Multi-server Setups](#multi-server-setups)

## Custom Playwright Scripts

For flows that `interact.py` can't handle, write a Playwright script directly.

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

**Canvas/WebGL verification** — checking non-DOM content via screenshot size:

```python
page.goto("http://localhost:3000/game")
page.wait_for_timeout(2000)  # let canvas render
canvas = page.locator("canvas")
assert canvas.is_visible(), "Canvas should be visible"
screenshot_bytes = canvas.screenshot()
assert len(screenshot_bytes) > 1000, "Canvas is blank (screenshot too small)"
print("PASS: Canvas rendered content")
```

## Next.js / React

### Page loads correctly

```bash
python verify.py http://localhost:3000 \
    --assert "status:200" \
    --assert "no-console-errors" \
    --assert "title:My App"
```

### Navigation works

```bash
python verify.py http://localhost:3000/about \
    --assert "text:About" \
    --assert "visible:nav" \
    --assert "url:about"
```

> **Note:** `url:` checks the URL immediately after page load.
> This works for direct navigation (the URL is already set by the request) but will miss client-side redirects.
> For redirect testing, use a custom Playwright script with `page.wait_for_url()`.

### Dynamic content rendered (not stuck loading)

```bash
python verify.py http://localhost:3000/dashboard \
    --assert "visible:[data-testid=dashboard]" \
    --assert "no-text:Loading..."
```

### Cold dev server (slow first compile)

The default navigation timeout is 10s.
For Next.js/Vite dev servers that compile on first request, use `--timeout`:

```bash
python verify.py http://localhost:3000 \
    --timeout 30000 \
    --assert "text:Welcome" \
    --assert "no-console-errors"
```

### Visual check with screenshot

```bash
# --wait-for ensures React has rendered before the screenshot is taken
python screenshot.py http://localhost:3000 --wait-for "h1" --output homepage.png
python screenshot.py http://localhost:3000/dashboard --wait-for "[data-testid=dashboard]" --full-page --output dashboard.png
```

### Accessibility tree inspection

```bash
# --wait-for ensures React has rendered before the tree is captured
python snapshot.py http://localhost:3000 --wait-for "h1"
python snapshot.py http://localhost:3000/dashboard --wait-for "[data-testid=dashboard]" --selector "main"
```

## Static Sites

```bash
python verify.py http://localhost:8080 \
    --assert "status:200" \
    --assert "title:Home" \
    --assert "visible:header" \
    --assert "visible:footer"
```

For static sites, `--wait-for` is optional since there's no client-side rendering:

```bash
python screenshot.py http://localhost:8080 --output static.png
python snapshot.py http://localhost:8080
```

## Form Validation

### Form elements present

```bash
python verify.py http://localhost:3000/signup \
    --assert "visible:input[name=email]" \
    --assert "visible:input[name=password]" \
    --assert "visible:button[type=submit]"
```

### Debugging form state

Use `snapshot.py` to inspect ARIA attributes (invalid, required, disabled):

```bash
python snapshot.py http://localhost:3000/signup --wait-for "form" --selector "form"
```

Output is YAML-like — look for `[required]`, `[invalid]`, `[disabled]` annotations:

```yaml
- textbox "Email" [required]:
  - /placeholder: you@example.com
- textbox "Password" [required]
- button "Submit" [disabled]
```

## Authentication Flows

Use `interact.py` for login flows:

```bash
python interact.py http://localhost:3000/login \
    --fill "input[name=email]=test@example.com" \
    --fill "input[name=password]=password" \
    --click "button[type=submit]" \
    --wait "text:Dashboard" \
    --assert "url:/dashboard" \
    --assert "text:Dashboard"
```

With server lifecycle:

```bash
python with_server.py --cmd "npm start" --port 3000 -- \
    python interact.py http://localhost:3000/login \
        --fill "input[name=email]=test@example.com" \
        --fill "input[name=password]=password" \
        --click "button[type=submit]" \
        --wait "text:Dashboard" \
        --assert "url:/dashboard"
```

For flows too complex for interact.py (e.g., conditional logic, loops), use a custom Playwright script:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    page.goto("http://localhost:3000/login")
    page.fill("input[name=email]", "test@example.com")
    page.fill("input[name=password]", "password")
    page.click("button[type=submit]")

    page.wait_for_url("**/dashboard", timeout=5000)
    assert page.locator("h1").text_content() == "Dashboard"
    print("PASS: Login redirects to dashboard")

    browser.close()
```

## Tables and Lists

```bash
# Table loads with data
python verify.py http://localhost:3000/admin/users \
    --assert "visible:table" \
    --assert "count:table tbody tr:5" \
    --assert "no-console-errors"

# List has expected items
python verify.py http://localhost:3000/tasks \
    --assert "visible:ul" \
    --assert "count:li.task-item:3"
```

## Error States

### 404 page

```bash
python verify.py http://localhost:3000/nonexistent \
    --assert "status:404" \
    --assert "text:Not Found"
```

### Error boundary

```bash
python verify.py http://localhost:3000/broken-page \
    --assert "text:Something went wrong" \
    --assert "hidden:.spinner"
```

### API error handling

```bash
python verify.py http://localhost:3000/dashboard \
    --assert "no-console-errors" \
    --assert "no-text:undefined" \
    --assert "no-text:NaN"
```

## API Verification

### Page makes expected API calls

```bash
python verify.py http://localhost:3000/dashboard \
    --wait-for "text:Dashboard" \
    --assert "request:GET:/api/user:200" \
    --assert "request:GET:/api/stats:200"
```

### No failed network requests

```bash
python verify.py http://localhost:3000 \
    --assert "no-failed-requests" \
    --assert "no-console-errors"
```

> **Note:** `no-failed-requests` checks ALL network responses including favicon, fonts, etc.
> Use specific `request:METHOD:PATH:STATUS` assertions for targeted API checks.

### API call after user action

```bash
python interact.py http://localhost:3000/settings \
    --fill "#name=New Name" \
    --click "button:has-text('Save')" \
    --wait "text:Saved" \
    --assert "request:POST:/api/settings:200" \
    --assert "text:Saved"
```

## Console Inspection

### Verify specific console output

```bash
python verify.py http://localhost:3000 \
    --assert "console-contains:App initialized"
```

### No warnings or errors

```bash
python verify.py http://localhost:3000 \
    --assert "no-console-errors" \
    --assert "no-console-warnings"
```

### Debug with full console log

```bash
python snapshot.py http://localhost:3000 --wait-for "h1" --console
python screenshot.py http://localhost:3000 --wait-for "h1" --console --output debug.png
```

The `--console` flag adds a `<console-log>` section with all messages (info, warn, error, log).

## Responsive / Mobile

### Mobile viewport

```bash
python screenshot.py http://localhost:3000 --viewport 375x812 --wait-for "h1" --output mobile.png
python verify.py http://localhost:3000 --viewport 375x812 --assert "visible:.mobile-nav"
```

### Device presets

```bash
python screenshot.py http://localhost:3000 --device "iPhone 14" --wait-for "h1" --output iphone.png
python screenshot.py http://localhost:3000 --device "iPad Pro 11" --wait-for "h1" --output ipad.png
```

Device presets set viewport, user agent, and device scale factor. `--viewport` overrides the preset's viewport if both are specified.

### Mobile interaction flow

```bash
python interact.py http://localhost:3000 \
    --device "iPhone 14" \
    --click "button.hamburger" \
    --wait "selector:.mobile-menu" \
    --click "a:has-text('Settings')" \
    --wait "text:Settings" \
    --assert "url:/settings"
```

## Multi-server Setups

Frontend + API backend:

```bash
python with_server.py \
    --cmd "npm run dev" --port 3000 \
    --cmd "python api/main.py" --port 8000 \
    -- python verify.py http://localhost:3000 \
        --assert "text:Welcome" \
        --assert "no-console-errors"
```

Frontend + API + database seeder:

```bash
# Seed first, then start servers
python seed_db.py && \
python with_server.py \
    --cmd "npm run dev" --port 3000 \
    --cmd "python api/main.py" --port 8000 \
    -- python verify.py http://localhost:3000/users \
        --assert "visible:table" \
        --assert "count:table tbody tr:10"
```
