#!/usr/bin/env python3
"""Returns an LLM-friendly accessibility tree snapshot of a web page.

Usage:
    python snapshot.py URL [--selector SELECTOR] [--timeout MS]

Output: YAML-like indented tree showing roles, names, and properties.
Structured for LLM consumption — far more token-efficient than raw HTML or screenshots.

Examples:
    python snapshot.py http://localhost:3000
    python snapshot.py http://localhost:3000 --selector "#main-content"
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Accessibility tree snapshot")
    parser.add_argument("url", help="URL to snapshot")
    parser.add_argument("--selector", help="CSS selector to scope the snapshot")
    parser.add_argument(
        "--timeout", type=int, default=10000,
        help="Navigation timeout in ms (default: 10000)",
    )
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Playwright not installed. Run: pip install playwright && python -m playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto(args.url, timeout=args.timeout, wait_until="load")
        except Exception as e:
            print(f"Could not navigate to {args.url}: {e}", file=sys.stderr)
            browser.close()
            sys.exit(1)

        if args.selector:
            locator = page.locator(args.selector).first
            try:
                locator.wait_for(timeout=5000)
            except Exception:
                print(f"Selector '{args.selector}' not found", file=sys.stderr)
                browser.close()
                sys.exit(1)
            snapshot = locator.aria_snapshot()
        else:
            snapshot = page.locator("body").aria_snapshot()

        if snapshot:
            print(snapshot)
        else:
            print("(empty accessibility tree)", file=sys.stderr)

        browser.close()


if __name__ == "__main__":
    main()
