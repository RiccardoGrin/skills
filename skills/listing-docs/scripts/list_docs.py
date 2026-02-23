#!/usr/bin/env python3
"""List documentation files with their front-matter summaries and read_when hints.

Usage:
    python list_docs.py [docs-path]

Defaults to docs/ relative to CWD. Outputs compact line-based format to stdout.
Uses only the Python standard library — no external dependencies.
"""

import sys
from pathlib import Path


def parse_frontmatter(filepath: Path):
    """Read a file's YAML front-matter without loading the entire file.

    Returns (summary, read_when, issue) where issue is a string if something
    is wrong, or None on success.
    """
    try:
        with filepath.open("r", encoding="utf-8") as f:
            first_line = f.readline().rstrip("\n")
            if first_line != "---":
                return None, None, "missing front matter"

            lines = []
            for line in f:
                stripped = line.rstrip("\n")
                if stripped == "---":
                    break
                lines.append(stripped)
            else:
                # Hit EOF without closing ---
                return None, None, "unterminated front matter"
    except (OSError, UnicodeDecodeError) as e:
        return None, None, f"read error: {e}"

    # Simple key-value parsing (matches validate_skill.py patterns)
    # Tracks both scalar values and YAML list items per key
    data = {}
    list_data = {}
    current_key = None
    for line in lines:
        if line and not line[0].isspace():
            kv = line.split(":", 1)
            if len(kv) == 2:
                current_key = kv[0].strip()
                value = kv[1].strip().strip('"').strip("'")
                if value in (">", "|", ">-", "|-", ""):
                    data[current_key] = ""
                else:
                    data[current_key] = value
        elif current_key and line.strip():
            content = line.strip()
            # YAML list item (- 'value' or - value)
            if content.startswith("- "):
                item = content[2:].strip().strip("'\"")
                list_data.setdefault(current_key, []).append(item)
            else:
                # Continuation line for scalar value
                separator = " " if data.get(current_key) else ""
                data[current_key] = data.get(current_key, "") + separator + content

    summary = data.get("summary")

    # read_when: prefer list items, fall back to scalar parsed by separator
    read_when = None
    if "read_when" in list_data:
        read_when = list_data["read_when"]
    elif data.get("read_when"):
        raw = data["read_when"]
        # Try semicolons first, then commas
        for sep in (";", ","):
            if sep in raw:
                items = [i.strip().strip("'\"") for i in raw.split(sep) if i.strip()]
                if items:
                    read_when = items
                    break
        if not read_when:
            read_when = [raw]

    issue = None
    if not summary:
        issue = "summary missing"

    return summary, read_when, issue


def main():
    docs_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")

    if not docs_path.is_dir():
        print(f"No docs directory found at: {docs_path}")
        sys.exit(0)

    md_files = sorted(docs_path.rglob("*.md"))
    if not md_files:
        print(f"No markdown files found in: {docs_path}")
        sys.exit(0)

    cwd = Path.cwd()
    for filepath in md_files:
        try:
            rel = filepath.relative_to(cwd)
        except ValueError:
            rel = filepath
        # Always use forward slashes
        display_path = str(rel).replace("\\", "/")

        summary, read_when, issue = parse_frontmatter(filepath)

        if issue and not summary:
            print(f"{display_path} - [{issue}]")
        elif issue:
            print(f"{display_path} - {summary} [{issue}]")
        else:
            print(f"{display_path} - {summary}")

        if read_when:
            print(f"  Read when: {'; '.join(read_when)}")


if __name__ == "__main__":
    main()
