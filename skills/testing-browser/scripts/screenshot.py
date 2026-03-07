#!/usr/bin/env python3
"""Takes a screenshot and dumps the accessibility tree + console errors.

Full diagnostic dump: visual screenshot saved to disk, accessibility tree and
any console errors printed to stdout for the agent to read.

Usage:
    python screenshot.py URL [--output PATH] [--selector SELECTOR] [--full-page] [--timeout MS]

Examples:
    python screenshot.py http://localhost:3000 --output screenshot.png
    python screenshot.py http://localhost:3000 --full-page --output full.png
    python screenshot.py http://localhost:3000 --selector "#main-content"
"""

import argparse
import sys


def format_node(node, indent=0):
    """Format an accessibility tree node as readable indented text."""
    if not node:
        return ""

    lines = []
    role = node.get("role", "")
    name = node.get("name", "")

    if role in ("generic", "none", "") and not name:
        for child in node.get("children", []):
            child_text = format_node(child, indent)
            if child_text:
                lines.append(child_text)
        return "\n".join(lines)

    prefix = "  " * indent
    parts = [role]
    if name:
        parts.append(f'"{name}"')

    props = []
    if node.get("level"):
        props.append(f"level={node['level']}")
    if node.get("checked") is not None:
        props.append(f"checked={node['checked']}")
    if node.get("disabled"):
        props.append("disabled")
    if node.get("required"):
        props.append("required")
    if node.get("expanded") is not None:
        props.append(f"expanded={node['expanded']}")
    if node.get("selected"):
        props.append("selected")
    if node.get("valuetext"):
        props.append(f"value={node['valuetext']}")
    if node.get("invalid"):
        props.append(f"invalid={node['invalid']}")
    if node.get("focused"):
        props.append("focused")

    if props:
        parts.append(f"[{', '.join(props)}]")

    lines.append(prefix + " ".join(parts))

    for child in node.get("children", []):
        child_text = format_node(child, indent + 1)
        if child_text:
            lines.append(child_text)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Screenshot + accessibility tree + console errors")
    parser.add_argument("url", help="URL to screenshot")
    parser.add_argument("--output", "-o", default="screenshot.png", help="Output file path")
    parser.add_argument("--selector", help="CSS selector to screenshot (element only)")
    parser.add_argument("--full-page", action="store_true", help="Capture full scrollable page")
    parser.add_argument(
        "--timeout", type=int, default=10000,
        help="Navigation timeout in ms (default: 10000)",
    )
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Playwright not installed. Run: pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.on(
            "console",
            lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
        )

        try:
            page.goto(args.url, timeout=args.timeout, wait_until="load")
        except Exception as e:
            print(f"Could not navigate to {args.url}: {e}", file=sys.stderr)
            browser.close()
            sys.exit(1)

        # Take screenshot
        if args.selector:
            locator = page.locator(args.selector).first
            try:
                locator.wait_for(state="visible", timeout=5000)
            except Exception:
                print(f"Selector '{args.selector}' not found or not visible", file=sys.stderr)
                browser.close()
                sys.exit(1)
            locator.screenshot(path=args.output)
        else:
            page.screenshot(path=args.output, full_page=args.full_page)

        print(f"Screenshot saved: {args.output}")

        # Accessibility tree
        snapshot = page.accessibility.snapshot()
        if snapshot:
            print("\n--- Accessibility Tree ---\n")
            print(format_node(snapshot))

        # Console errors
        if console_errors:
            print(f"\n--- Console Errors ({len(console_errors)}) ---\n")
            for err in console_errors:
                print(f"  {err}")

        browser.close()


if __name__ == "__main__":
    main()
