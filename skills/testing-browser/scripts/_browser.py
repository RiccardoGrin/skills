"""Shared browser helpers for testing-browser scripts.

Provides Chrome connection (persistent profile or CDP) with fallback,
enhanced console capture with source locations and stack traces, and safe cleanup.
"""

import os
import sys
import time


def connect_or_launch(playwright, use_chrome=False, chrome_port=None, device_opts=None):
    """Launch or connect to a browser.

    Modes (tried in priority order):
    1. use_chrome: Launch real Chrome with a persistent .browser-data/ profile.
       Sessions (cookies, localStorage) survive across runs. Opens headed (visible).
    2. chrome_port: Connect to running Chrome via CDP (less reliable).
    3. Default: Launch fresh headless Chromium.

    Returns (browser, context, page, mode).
    mode is "chrome", "cdp", or "fresh".
    browser is None in "chrome" mode (persistent context manages its own browser).
    """
    context_opts = dict(device_opts) if device_opts else {}

    if use_chrome:
        if device_opts:
            print("Note: --device is ignored when using --use-chrome", file=sys.stderr)

        profile_dir = os.path.join(os.getcwd(), ".browser-data")
        first_run = not os.path.exists(profile_dir)
        try:
            context = playwright.chromium.launch_persistent_context(
                profile_dir,
                channel="chrome",
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
                ignore_default_args=["--enable-automation"],
            )
            # Reuse the initial about:blank page (avoids opening a second tab)
            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()
            if first_run:
                print("Launched Chrome with new persistent profile at .browser-data/", file=sys.stderr)
                print("If this page requires login, use interact.py --use-chrome to script the login flow first.", file=sys.stderr)
            else:
                print("Launched Chrome with persistent profile (session restored)", file=sys.stderr)
            return None, context, page, "chrome"
        except Exception as e:
            print(f"Could not launch Chrome: {e}", file=sys.stderr)
            print("Make sure all Chrome windows are closed first.", file=sys.stderr)
            print("Falling back to fresh Chromium.", file=sys.stderr)
            print("", file=sys.stderr)

    if chrome_port:
        if device_opts:
            print("Note: --device is ignored when connecting to existing Chrome", file=sys.stderr)
        try:
            browser = playwright.chromium.connect_over_cdp(f"http://localhost:{chrome_port}")
            if browser.contexts:
                context = browser.contexts[0]
            else:
                context = browser.new_context()
            page = context.new_page()
            print(f"Connected to Chrome on port {chrome_port}", file=sys.stderr)
            return browser, context, page, "cdp"
        except Exception as e:
            print(f"Could not connect to Chrome on port {chrome_port}: {e}", file=sys.stderr)
            print("Falling back to fresh Chromium.", file=sys.stderr)
            print("", file=sys.stderr)
            print("To connect via CDP:", file=sys.stderr)
            print("  1. Close ALL Chrome windows completely", file=sys.stderr)
            print("  2. Relaunch with:", file=sys.stderr)
            print(f'     chrome --remote-debugging-port={chrome_port} --profile-directory="Default" --restore-last-session', file=sys.stderr)
            print("  3. Re-run this script", file=sys.stderr)
            print("", file=sys.stderr)

    browser = playwright.chromium.launch()
    context = browser.new_context(**context_opts)
    page = context.new_page()
    return browser, context, page, "fresh"


def setup_console_capture(page):
    """Set up detailed console and page error capture.

    Always captures everything. Returns dict with both assertion-compatible
    formats and detailed formats with timestamps, locations, and stacks.
    """
    start = time.time()
    collectors = {
        "console_errors": [],
        "console_messages": [],
        "detailed_messages": [],
        "page_errors": [],
        "_start": start,
    }

    def on_console(msg):
        collectors["console_messages"].append((msg.type, msg.text))
        if msg.type == "error":
            collectors["console_errors"].append(msg.text)

        loc = msg.location
        collectors["detailed_messages"].append({
            "type": msg.type,
            "text": msg.text,
            "ts": round(time.time() - start, 3),
            "url": loc.get("url", "") if loc else "",
            "line": loc.get("lineNumber", -1) if loc else -1,
            "col": loc.get("columnNumber", -1) if loc else -1,
        })

    def on_pageerror(error):
        collectors["page_errors"].append({
            "message": getattr(error, "message", str(error)),
            "stack": getattr(error, "stack", ""),
            "ts": round(time.time() - start, 3),
        })

    page.on("console", on_console)
    page.on("pageerror", on_pageerror)
    return collectors


def format_console_detail(collectors):
    """Format detailed console output with timestamps and source locations."""
    lines = []
    msgs = collectors["detailed_messages"]
    if msgs:
        lines.append(f'<console-log count="{len(msgs)}">')
        for m in msgs:
            loc = ""
            if m["url"] and m["line"] >= 0:
                url = m["url"]
                if "://" in url:
                    url = url.split("://", 1)[1]
                loc = f" @ {url}:{m['line']}:{m['col']}"
            lines.append(f"  [{m['ts']:.3f}s] [{m['type']}] {m['text']}{loc}")
        lines.append("</console-log>")
    return lines



def format_page_errors(collectors):
    """Format uncaught page errors with stack traces."""
    lines = []
    errs = collectors["page_errors"]
    if errs:
        lines.append(f'<page-errors count="{len(errs)}">')
        for e in errs:
            lines.append(f"  [{e['ts']:.3f}s] {e['message']}")
            stack = e.get("stack", "")
            if stack and stack != e["message"]:
                for sl in stack.split("\n"):
                    stripped = sl.strip()
                    if stripped:
                        lines.append(f"    {stripped}")
        lines.append("</page-errors>")
    return lines


def cleanup_browser(browser, page, mode):
    """Clean up browser resources.

    - "chrome": closes the persistent context (which closes Chrome). Profile is saved to disk.
    - "cdp": closes only the tab we created, not the user's browser.
    - "fresh": closes the entire browser.
    """
    if mode == "chrome":
        page.context.close()
    elif mode == "cdp":
        try:
            page.close()
        except Exception:
            pass
    else:
        browser.close()
