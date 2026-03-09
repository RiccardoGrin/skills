# Assertion Patterns by Framework

## Table of Contents

- [Next.js / React](#nextjs--react)
- [Static Sites](#static-sites)
- [Form Validation](#form-validation)
- [Authentication Flows](#authentication-flows)
- [Tables and Lists](#tables-and-lists)
- [Error States](#error-states)
- [Multi-server Setups](#multi-server-setups)

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

> **Note:** `url:` checks the URL immediately after page load. This works for direct navigation (the URL is already set by the request) but will miss client-side redirects. For redirect testing, use a custom Playwright script with `page.wait_for_url()`.

### Dynamic content rendered (not stuck loading)

```bash
python verify.py http://localhost:3000/dashboard \
    --assert "visible:[data-testid=dashboard]" \
    --assert "no-text:Loading..."
```

### Cold dev server (slow first compile)

The default navigation timeout is 10s. For Next.js/Vite dev servers that compile on first request, use `--timeout`:

```bash
python verify.py http://localhost:3000 \
    --timeout 30000 \
    --assert "text:Welcome" \
    --assert "no-console-errors"
```

## Static Sites

```bash
python verify.py http://localhost:8080 \
    --assert "status:200" \
    --assert "title:Home" \
    --assert "visible:header" \
    --assert "visible:footer"
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
python snapshot.py http://localhost:3000/signup --selector "form"
```

Output is YAML-like — look for `[required]`, `[invalid]`, `[disabled]` annotations:

```yaml
- textbox "Email" [required]:
  - /placeholder: you@example.com
- textbox "Password" [required]
- button "Submit" [disabled]
```

## Authentication Flows

Multi-step flows need a custom Playwright script (assertions are single-page):

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # Login
    page.goto("http://localhost:3000/login")
    page.fill("input[name=email]", "test@example.com")
    page.fill("input[name=password]", "password")
    page.click("button[type=submit]")

    # Verify redirect
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
