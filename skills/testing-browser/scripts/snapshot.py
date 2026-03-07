#!/usr/bin/env python3
"""Returns an LLM-friendly accessibility tree snapshot of a web page.

Usage:
    python snapshot.py URL [--selector SELECTOR] [--timeout MS]

Output: Indented text tree showing roles, names, and properties.
Structured for LLM consumption — far more token-efficient than raw HTML or screenshots.

Examples:
    python snapshot.py http://localhost:3000
    python snapshot.py http://localhost:3000 --selector "#main-content"
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

    # Skip generic containers with no semantic info — still process children
    if role in ("generic", "none", "") and not name:
        for child in node.get("children", []):
            child_text = format_node(child, indent)
            if child_text:
                lines.append(child_text)
        return "\n".join(lines)

    # Build node description
    prefix = "  " * indent
    parts = [role]
    if name:
        parts.append(f'"{name}"')

    # Key properties
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
            "Playwright not installed. Run: pip install playwright && playwright install chromium",
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
            root = page.accessibility.snapshot(root=locator.element_handle())
        else:
            root = page.accessibility.snapshot()

        if root:
            print(format_node(root))
        else:
            print("(empty accessibility tree)", file=sys.stderr)

        browser.close()


if __name__ == "__main__":
    main()
