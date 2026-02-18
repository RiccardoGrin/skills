#!/usr/bin/env python3
"""Scaffold a new skill directory with SKILL.md template and references/ folder.

Usage:
    python init_skill.py <skill-name> [--path <parent-directory>]

Examples:
    python init_skill.py analyzing-data
    python init_skill.py analyzing-data --path skills

Naming convention:
    Use kebab-case with a gerund (verb ending in -ing) as the first word.
    Good: analyzing-data, creating-skills, processing-pdfs
    Avoid: data-analyzer, skill-creator, pdf-processor
"""

import argparse
import re
import sys
from pathlib import Path

SKILL_TEMPLATE = '''---
name: {name}
description: TODO — Describe what this skill does in third-person voice. Formula: [Does what] for/using [domain]. [Checks/covers what]. Use when [triggers]
---

# {title}

<!-- Target: 150–300 lines. Hard limit: 500 lines. -->
<!-- Use reference files in references/ for detailed content. -->

## Reference Files

| File | Read When |
|------|-----------|
| <!-- Add reference files here --> | <!-- Condition --> |

## Workflow

- [ ] Step 1: TODO
- [ ] Step 2: TODO
- [ ] Step 3: TODO
'''


def validate_name(name: str) -> str:
    """Validate skill name format before creating anything."""
    if not re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", name):
        raise argparse.ArgumentTypeError(
            f"'{name}' is not valid kebab-case.\n"
            f"  Good: analyzing-data, creating-skills, processing-pdfs\n"
            f"  Bad:  AnalyzeData, skill_creator, My-Skill"
        )
    return name


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new skill directory.",
        epilog="Tip: Use a gerund name like 'analyzing-data' or 'creating-skills'.",
    )
    parser.add_argument(
        "name",
        type=validate_name,
        help="Skill name in kebab-case (e.g., analyzing-data)",
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Parent directory for the skill (default: current directory)",
    )
    args = parser.parse_args()

    # Check gerund naming (advisory, not blocking)
    first_word = args.name.split("-")[0]
    if not first_word.endswith("ing"):
        print(f"Tip: Consider a gerund name (e.g., 'analyzing-data' instead of 'data-analyzer')")

    parent = Path(args.path)
    if not parent.is_dir():
        print(f"Error: Parent directory '{args.path}' does not exist.")
        sys.exit(1)

    skill_dir = parent / args.name
    if skill_dir.exists():
        print(f"Error: Directory '{skill_dir}' already exists.")
        sys.exit(1)

    # Create directory structure
    skill_dir.mkdir(parents=True)
    (skill_dir / "references").mkdir()

    # Generate title from name
    title = args.name.replace("-", " ").title()

    # Write SKILL.md
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        SKILL_TEMPLATE.format(name=args.name, title=title),
        encoding="utf-8",
    )

    print("Created skill scaffold:")
    print(f"  {skill_dir}/")
    print(f"    SKILL.md")
    print(f"    references/")
    print(f"\nNext steps:")
    print(f"  1. Edit {skill_dir}/SKILL.md -- fill in the description and body")
    print(f"  2. Add reference files to {skill_dir}/references/")
    print(f"  3. Run: python validate_skill.py {skill_dir}")


if __name__ == "__main__":
    main()
