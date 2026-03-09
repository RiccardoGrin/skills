#!/usr/bin/env python3
"""One-line assertion runner for browser UI verification.

Usage:
    python verify.py URL [--assert ASSERTION]... [--timeout MS]

Assertions:
    text:EXPECTED          Page contains visible text
    no-text:UNEXPECTED     Page does NOT contain text
    title:EXPECTED         Page title contains substring
    visible:SELECTOR       CSS selector matches a visible element
    hidden:SELECTOR        Element is hidden or absent
    count:SELECTOR:N       Exactly N elements match selector
    url:PATTERN            Current URL contains pattern
    no-console-errors      No console.error() calls during load
    status:CODE            HTTP response status code matches

Examples:
    python verify.py http://localhost:3000 --assert "text:Welcome" --assert "no-console-errors"
    python verify.py http://localhost:3000/login --assert "visible:#email" --assert "visible:#password"
"""

import argparse
import sys


def check_assertion(page, assertion, response_status, console_errors):
    """Check a single assertion. Returns (passed, detail)."""
    if assertion == "no-console-errors":
        if console_errors:
            msgs = "; ".join(console_errors[:3])
            suffix = f" (and {len(console_errors) - 3} more)" if len(console_errors) > 3 else ""
            return False, f"{len(console_errors)} error(s): {msgs}{suffix}"
        return True, ""

    if ":" not in assertion:
        return False, f"Invalid assertion format: {assertion}"

    kind, value = assertion.split(":", 1)

    if kind == "text":
        try:
            page.get_by_text(value, exact=False).first.wait_for(timeout=5000)
            return True, ""
        except Exception:
            return False, f"Text '{value}' not found on page"

    elif kind == "no-text":
        count = page.get_by_text(value, exact=False).count()
        if count > 0:
            return False, f"Text '{value}' found {count} time(s)"
        return True, ""

    elif kind == "title":
        title = page.title()
        if value.lower() in title.lower():
            return True, ""
        return False, f"Title is '{title}', expected to contain '{value}'"

    elif kind == "visible":
        try:
            page.locator(value).first.wait_for(state="visible", timeout=5000)
            return True, ""
        except Exception:
            return False, f"Element '{value}' not visible"

    elif kind == "hidden":
        count = page.locator(value).count()
        if count == 0:
            return True, ""
        if not page.locator(value).first.is_visible():
            return True, ""
        return False, f"Element '{value}' is visible"

    elif kind == "count":
        parts = value.rsplit(":", 1)
        if len(parts) != 2:
            return False, "count assertion needs SELECTOR:N format"
        selector, n_str = parts
        try:
            expected = int(n_str)
        except ValueError:
            return False, f"N must be an integer, got '{n_str}'"
        actual = page.locator(selector).count()
        if actual == expected:
            return True, ""
        return False, f"Expected {expected} elements matching '{selector}', found {actual}"

    elif kind == "url":
        current = page.url
        if value in current:
            return True, ""
        return False, f"URL is '{current}', expected to contain '{value}'"

    elif kind == "status":
        try:
            expected = int(value)
        except ValueError:
            return False, f"CODE must be an integer, got '{value}'"
        if response_status == expected:
            return True, ""
        return False, f"Status is {response_status}, expected {expected}"

    else:
        return False, f"Unknown assertion type: {kind}"


def main():
    parser = argparse.ArgumentParser(description="Browser UI assertion runner")
    parser.add_argument("url", help="URL to verify")
    parser.add_argument(
        "--assert", dest="assertions", action="append", default=[],
        help="Assertion to check (can specify multiple)",
    )
    parser.add_argument(
        "--timeout", type=int, default=10000,
        help="Navigation timeout in ms (default: 10000)",
    )
    args = parser.parse_args()

    if not args.assertions:
        print("No assertions specified. Use --assert to add checks.", file=sys.stderr)
        sys.exit(1)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Playwright not installed. Run: pip install playwright && python -m playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    console_errors = []
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.on(
            "console",
            lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
        )

        try:
            response = page.goto(args.url, timeout=args.timeout, wait_until="load")
            response_status = response.status if response else None
        except Exception as e:
            print(f"FAIL: Could not navigate to {args.url}: {e}")
            browser.close()
            sys.exit(1)

        for assertion in args.assertions:
            passed, detail = check_assertion(page, assertion, response_status, console_errors)
            results.append((assertion, passed, detail))

        browser.close()

    for assertion, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        line = f"  {status}: {assertion}"
        if detail:
            line += f" -- {detail}"
        print(line)

    failed_count = sum(1 for _, passed, _ in results if not passed)
    print()
    if failed_count == 0:
        print(f"All {len(results)} assertion(s) passed")
    else:
        print(f"{failed_count} of {len(results)} assertion(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
