#!/usr/bin/env python3
"""Multi-step browser interaction script.

Executes actions in the order they appear on the command line, then runs assertions.

Usage:
    python interact.py URL [options] [actions...]

Global options:
    --timeout MS            Navigation/action timeout in ms (default: 10000)
    --viewport WIDTHxHEIGHT Viewport size (e.g., 375x812)
    --device NAME           Playwright device preset (e.g., "iPhone 14")
    --dismiss-dialogs       Silently dismiss dialogs (default: auto-dismiss with warning)
    --screenshot PATH       Take screenshot after all actions

Ordered actions (executed in order):
    --click SELECTOR        Click an element
    --fill "SEL=VALUE"      Clear and fill an input field
    --select "SEL=VALUE"    Select a dropdown option
    --type "SEL=VALUE"      Type text key-by-key (for autocomplete etc.)
    --wait CONDITION        Wait: "text:TEXT", "selector:SEL", or "network-idle"
    --assert ASSERTION      Same assertions as verify.py

Examples:
    python interact.py http://localhost:3000 --fill "#email=test@test.com" --click "#submit" --assert "text:Welcome"
    python interact.py http://localhost:3000 --viewport 375x812 --click "nav button" --wait "text:Menu" --screenshot mobile.png
"""

import sys


GLOBAL_VALUE_FLAGS = {"--timeout", "--viewport", "--device", "--screenshot"}
GLOBAL_BOOL_FLAGS = {"--dismiss-dialogs"}
ACTION_FLAGS = {"--click", "--fill", "--select", "--type", "--wait", "--assert"}


def parse_args(argv):
    """Parse args manually to preserve action ordering."""
    url = None
    config = {
        "timeout": 10000,
        "viewport": None,
        "device": None,
        "dismiss_dialogs": False,
        "screenshot": None,
    }
    actions = []  # list of (action_type, value)

    i = 1  # skip script name
    while i < len(argv):
        arg = argv[i]
        if arg in GLOBAL_BOOL_FLAGS:
            key = arg.lstrip("-").replace("-", "_")
            config[key] = True
            i += 1
        elif arg in GLOBAL_VALUE_FLAGS:
            if i + 1 >= len(argv):
                print(f"{arg} requires a value", file=sys.stderr)
                sys.exit(1)
            key = arg.lstrip("-").replace("-", "_")
            config[key] = argv[i + 1]
            i += 2
        elif arg in ACTION_FLAGS:
            if i + 1 >= len(argv):
                print(f"{arg} requires a value", file=sys.stderr)
                sys.exit(1)
            action_type = arg.lstrip("-")
            actions.append((action_type, argv[i + 1]))
            i += 2
        elif arg.startswith("-"):
            print(f"Unknown flag: {arg}", file=sys.stderr)
            sys.exit(1)
        else:
            if url is None:
                url = arg
                i += 1
            else:
                print(f"Unexpected positional argument: {arg}", file=sys.stderr)
                sys.exit(1)

    if url is None:
        print("URL is required", file=sys.stderr)
        print("Usage: python interact.py URL [options] [actions...]", file=sys.stderr)
        sys.exit(1)

    config["timeout"] = int(config["timeout"])
    return url, config, actions


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


def apply_wait(page, condition, timeout):
    """Apply a wait condition."""
    if condition == "network-idle":
        page.wait_for_load_state("networkidle", timeout=timeout)
    elif condition.startswith("text:"):
        text = condition[5:]
        page.get_by_text(text, exact=False).first.wait_for(timeout=timeout)
    else:
        # Bare selector or explicit "selector:" prefix
        selector = condition[9:] if condition.startswith("selector:") else condition
        page.locator(selector).first.wait_for(state="visible", timeout=timeout)


def main():
    url, config, actions = parse_args(sys.argv)

    if not actions:
        print("No actions specified. Use --click, --fill, --wait, --assert, etc.", file=sys.stderr)
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
    assertion_results = []

    with sync_playwright() as p:
        # Browser context setup (viewport/device)
        context_opts = {}
        if config["device"]:
            device = p.devices.get(config["device"])
            if not device:
                print(f"Unknown device: {config['device']}", file=sys.stderr)
                sys.exit(1)
            context_opts.update(device)

        browser = p.chromium.launch()
        context = browser.new_context(**context_opts)
        page = context.new_page()

        if config["viewport"]:
            try:
                w, h = config["viewport"].split("x")
                page.set_viewport_size({"width": int(w), "height": int(h)})
            except ValueError:
                print(f"Invalid viewport format: {config['viewport']} (expected WIDTHxHEIGHT)", file=sys.stderr)
                browser.close()
                sys.exit(1)

        # Console and network collection
        def on_console(msg):
            console_messages.append((msg.type, msg.text))
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", on_console)
        page.on(
            "response",
            lambda resp: network_responses.append((resp.request.method, resp.url, resp.status)),
        )

        # Dialog handling
        def handle_dialog(dialog):
            if not config["dismiss_dialogs"]:
                print(f"Warning: auto-dismissed dialog: {dialog.message}", file=sys.stderr)
            dialog.accept()

        page.on("dialog", handle_dialog)

        # Navigate
        try:
            response = page.goto(url, timeout=config["timeout"], wait_until="load")
            response_status = response.status if response else None
        except Exception as e:
            print(f"FAIL: Could not navigate to {url}: {e}")
            browser.close()
            sys.exit(1)

        # Execute actions in order
        ctx = {
            "response_status": response_status,
            "console_errors": console_errors,
            "console_messages": console_messages,
            "network_responses": network_responses,
        }

        for action_type, value in actions:
            try:
                if action_type == "click":
                    print(f"  ACTION: click {value}")
                    page.locator(value).click(timeout=config["timeout"])

                elif action_type == "fill":
                    if "=" not in value:
                        raise ValueError("--fill requires SELECTOR=VALUE format")
                    selector, fill_value = value.split("=", 1)
                    print(f"  ACTION: fill {selector}")
                    page.locator(selector).fill(fill_value, timeout=config["timeout"])

                elif action_type == "select":
                    if "=" not in value:
                        raise ValueError("--select requires SELECTOR=VALUE format")
                    selector, select_value = value.split("=", 1)
                    print(f"  ACTION: select {selector}")
                    page.locator(selector).select_option(select_value, timeout=config["timeout"])

                elif action_type == "type":
                    if "=" not in value:
                        raise ValueError("--type requires SELECTOR=VALUE format")
                    selector, type_value = value.split("=", 1)
                    print(f"  ACTION: type {selector}")
                    page.locator(selector).press_sequentially(type_value, timeout=config["timeout"])

                elif action_type == "wait":
                    print(f"  ACTION: wait {value}")
                    apply_wait(page, value, config["timeout"])

                elif action_type == "assert":
                    passed, detail = check_assertion(page, value, ctx)
                    assertion_results.append((value, passed, detail))

            except Exception as e:
                if action_type == "assert":
                    assertion_results.append((value, False, str(e)))
                else:
                    print(f"  FAIL: {action_type} {value} -- {e}")
                    browser.close()
                    sys.exit(1)

        # Screenshot at end if requested
        if config["screenshot"]:
            page.screenshot(path=config["screenshot"])
            print(f"  Screenshot saved: {config['screenshot']}")

        browser.close()

    # Print assertion results
    if assertion_results:
        for assertion, passed, detail in assertion_results:
            status = "PASS" if passed else "FAIL"
            line = f"  {status}: {assertion}"
            if detail:
                line += f" -- {detail}"
            print(line)

        failed_count = sum(1 for _, passed, _ in assertion_results if not passed)
        print()
        if failed_count == 0:
            print(f"All {len(assertion_results)} assertion(s) passed")
        else:
            print(f"{failed_count} of {len(assertion_results)} assertion(s) failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
