#!/usr/bin/env python3
"""One-line assertion runner for browser UI verification.

Usage:
    python verify.py URL [--assert ASSERTION]... [--wait-for WAIT]... [--viewport WxH] [--device NAME] [--dismiss-dialogs] [--timeout MS]

Wait-for (applied after navigation, before assertions):
    SELECTOR               Wait for CSS selector (bare selector)
    selector:SELECTOR      Wait for CSS selector (explicit prefix)
    text:TEXT              Wait for visible text to appear
    network-idle           Wait for network to be idle

Assertions:
    text:EXPECTED          Page contains visible text
    no-text:UNEXPECTED     Page does NOT contain text
    title:EXPECTED         Page title contains substring
    visible:SELECTOR       CSS selector matches a visible element
    hidden:SELECTOR        Element is hidden or absent
    count:SELECTOR:N       Exactly N elements match selector
    url:PATTERN            Current URL contains pattern
    no-console-errors      No console.error() calls during load
    no-console-warnings    No console.warn() calls during load
    console-contains:TEXT  Any console message contains text
    request:METHOD:PATH:STATUS  Network request was made matching method, path, status
    no-failed-requests     No 4xx/5xx responses in network log
    status:CODE            HTTP response status code matches

Examples:
    python verify.py http://localhost:3000 --assert "text:Welcome" --assert "no-console-errors"
    python verify.py http://localhost:3000/login --assert "visible:#email" --assert "visible:#password"
    python verify.py http://localhost:3000 --wait-for "text:Dashboard" --assert "text:Dashboard"
    python verify.py http://localhost:3000 --assert "no-failed-requests" --assert "request:GET:/api/users:200"
"""

import argparse
import sys


def check_assertion(page, assertion, ctx):
    """Check a single assertion. Returns (passed, detail).

    ctx keys: response_status, console_errors, console_messages, network_responses
    """
    if assertion == "no-console-errors":
        errors = ctx["console_errors"]
        if errors:
            msgs = "; ".join(errors[:3])
            suffix = f" (and {len(errors) - 3} more)" if len(errors) > 3 else ""
            return False, f"{len(errors)} error(s): {msgs}{suffix}"
        return True, ""

    if assertion == "no-console-warnings":
        warnings = [text for typ, text in ctx["console_messages"] if typ == "warning"]
        if warnings:
            msgs = "; ".join(warnings[:3])
            suffix = f" (and {len(warnings) - 3} more)" if len(warnings) > 3 else ""
            return False, f"{len(warnings)} warning(s): {msgs}{suffix}"
        return True, ""

    if assertion == "no-failed-requests":
        failed = [(m, u, s) for m, u, s in ctx["network_responses"] if s >= 400]
        if failed:
            examples = [f"{m} {u} -> {s}" for m, u, s in failed[:3]]
            suffix = f" (and {len(failed) - 3} more)" if len(failed) > 3 else ""
            return False, f"{len(failed)} failed request(s): {'; '.join(examples)}{suffix}"
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
        if ctx["response_status"] == expected:
            return True, ""
        return False, f"Status is {ctx['response_status']}, expected {expected}"

    elif kind == "console-contains":
        for _, text in ctx["console_messages"]:
            if value in text:
                return True, ""
        return False, f"No console message contains '{value}'"

    elif kind == "request":
        # Format: METHOD:PATH:STATUS (e.g., GET:/api/users:200)
        if value.count(":") < 2:
            return False, "request assertion needs METHOD:PATH:STATUS format"
        method, rest = value.split(":", 1)
        path, status_str = rest.rsplit(":", 1)
        try:
            expected_status = int(status_str)
        except ValueError:
            return False, f"STATUS must be an integer, got '{status_str}'"
        for req_method, req_url, req_status in ctx["network_responses"]:
            if req_method == method and path in req_url and req_status == expected_status:
                return True, ""
        return False, f"No {method} request matching '{path}' with status {expected_status}"

    else:
        return False, f"Unknown assertion type: {kind}"


def apply_wait_for(page, wait_for, timeout):
    """Apply a --wait-for condition after navigation."""
    if wait_for == "network-idle":
        page.wait_for_load_state("networkidle", timeout=timeout)
    elif wait_for.startswith("text:"):
        text = wait_for[5:]
        page.get_by_text(text, exact=False).first.wait_for(timeout=timeout)
    else:
        # Bare selector or explicit "selector:" prefix
        selector = wait_for[9:] if wait_for.startswith("selector:") else wait_for
        page.locator(selector).first.wait_for(state="visible", timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description="Browser UI assertion runner")
    parser.add_argument("url", help="URL to verify")
    parser.add_argument(
        "--assert", dest="assertions", action="append", default=[],
        help="Assertion to check (can specify multiple)",
    )
    parser.add_argument(
        "--wait-for", dest="wait_for", action="append", default=[],
        help="Wait condition after navigation (can specify multiple): "
        "CSS selector, 'text:TEXT', 'selector:SEL', or 'network-idle'",
    )
    parser.add_argument(
        "--viewport", help="Viewport size as WIDTHxHEIGHT (e.g., 375x812)",
    )
    parser.add_argument(
        "--device", help="Playwright device preset (e.g., 'iPhone 14')",
    )
    parser.add_argument(
        "--dismiss-dialogs", action="store_true",
        help="Silently dismiss dialogs (default: auto-dismiss with warning)",
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
    console_messages = []
    network_responses = []
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch()

        context_opts = {}
        if args.device:
            device = p.devices.get(args.device)
            if not device:
                print(f"Unknown device: {args.device}", file=sys.stderr)
                browser.close()
                sys.exit(1)
            context_opts.update(device)
        context = browser.new_context(**context_opts)
        page = context.new_page()

        if args.viewport:
            try:
                w, h = args.viewport.split("x")
                page.set_viewport_size({"width": int(w), "height": int(h)})
            except ValueError:
                print(f"Invalid viewport format: {args.viewport} (expected WIDTHxHEIGHT)", file=sys.stderr)
                browser.close()
                sys.exit(1)

        def on_console(msg):
            console_messages.append((msg.type, msg.text))
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", on_console)
        page.on(
            "response",
            lambda resp: network_responses.append((resp.request.method, resp.url, resp.status)),
        )

        def handle_dialog(dialog):
            if not args.dismiss_dialogs:
                print(f"Warning: auto-dismissed dialog: {dialog.message}", file=sys.stderr)
            dialog.accept()

        page.on("dialog", handle_dialog)

        try:
            response = page.goto(args.url, timeout=args.timeout, wait_until="load")
            response_status = response.status if response else None
        except Exception as e:
            print(f"FAIL: Could not navigate to {args.url}: {e}")
            browser.close()
            sys.exit(1)

        for wait_for in args.wait_for:
            try:
                apply_wait_for(page, wait_for, args.timeout)
            except Exception as e:
                print(f"FAIL: --wait-for '{wait_for}' failed: {e}")
                browser.close()
                sys.exit(1)

        ctx = {
            "response_status": response_status,
            "console_errors": console_errors,
            "console_messages": console_messages,
            "network_responses": network_responses,
        }

        for assertion in args.assertions:
            passed, detail = check_assertion(page, assertion, ctx)
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
