#!/usr/bin/env python3
"""Validate a skill directory against the format specification.

Usage:
    python validate_skill.py <skill-directory>

Returns errors (blocking) and warnings (advisory) separately.
Uses only the Python standard library — no external dependencies.
"""

import re
import sys
from pathlib import Path


def parse_frontmatter(content: str):
    """Parse YAML frontmatter from SKILL.md content using regex (no PyYAML dependency).

    Handles multi-line values using YAML folding (>) and block (|) indicators,
    as well as continuation lines (indented lines after a key).
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None, content
    raw = match.group(1)
    body = content[match.end():]
    data = {}
    current_key = None
    for line in raw.strip().splitlines():
        if line and not line[0].isspace():
            # New key:value pair
            kv = line.split(":", 1)
            if len(kv) == 2:
                current_key = kv[0].strip()
                value = kv[1].strip().strip('"').strip("'")
                # Skip YAML folding indicators
                if value in (">", "|", ">-", "|-"):
                    data[current_key] = ""
                else:
                    data[current_key] = value
        elif current_key and line.strip():
            # Continuation line for multi-line value
            separator = " " if data[current_key] else ""
            data[current_key] = data[current_key] + separator + line.strip()
    return data, body


def validate(skill_dir: str):
    """Run all validation checks. Returns (errors, warnings) lists."""
    errors = []
    warnings = []
    skill_path = Path(skill_dir)

    # --- Structural checks ---

    if not skill_path.is_dir():
        errors.append(f"Skill directory not found: {skill_dir}")
        return errors, warnings

    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        errors.append("SKILL.md not found in skill directory")
        return errors, warnings

    try:
        content = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        errors.append("SKILL.md is not valid UTF-8 text")
        return errors, warnings
    except OSError as e:
        errors.append(f"Could not read SKILL.md: {e}")
        return errors, warnings

    # --- Frontmatter checks ---

    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return errors, warnings

    frontmatter, body = parse_frontmatter(content)
    if frontmatter is None:
        errors.append("Could not parse frontmatter — ensure opening and closing --- on their own lines")
        return errors, warnings

    allowed_keys = {"name", "description", "version", "license", "compatibility", "metadata", "allowed-tools"}
    for key in frontmatter:
        if key not in allowed_keys:
            errors.append(f"Unknown frontmatter key: '{key}' (allowed: {', '.join(sorted(allowed_keys))})")

    # Name checks
    name = frontmatter.get("name", "")
    if not name:
        errors.append("Frontmatter 'name' is required and must not be empty")
    else:
        if not re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", name):
            errors.append(f"Name '{name}' is not valid kebab-case (e.g., 'creating-skills', 'analyzing-data')")

        dir_name = skill_path.name
        if name != dir_name:
            errors.append(f"Name '{name}' does not match directory name '{dir_name}'")

        reserved = ["anthropic", "claude", "openai", "cursor"]
        for word in reserved:
            if word in name.lower():
                warnings.append(f"Name contains reserved word '{word}' — consider renaming")

        # Gerund naming suggestion
        first_word = name.split("-")[0]
        if not first_word.endswith("ing"):
            warnings.append(f"Consider a gerund name (e.g., 'creating-skills' instead of 'skill-creator') — current first word: '{first_word}'")

    # Description checks
    description = frontmatter.get("description", "")
    if not description:
        errors.append("Frontmatter 'description' is required and must not be empty")
    else:
        if len(description) > 1024:
            errors.append(f"Description is {len(description)} characters (spec max 1024)")
        elif len(description) > 300:
            warnings.append(f"Description is {len(description)} characters; recommend under 300 for readability")

        if description.endswith("."):
            warnings.append("Description should not end with a period")

        # Third-person heuristic: should not start with imperative verbs
        imperative_starts = ["create ", "guide ", "help ", "build ", "run ", "make ", "use "]
        lower_desc = description.lower()
        for verb in imperative_starts:
            if lower_desc.startswith(verb):
                warnings.append(f"Description appears to use imperative voice (starts with '{verb.strip()}'). Prefer third-person: 'Guides...' not 'Guide...'")
                break

        if "use when" not in lower_desc and "use for" not in lower_desc:
            warnings.append("Description should include 'Use when' triggers to help agents match the skill")

    # --- Body checks ---

    body_lines = body.strip().splitlines()
    body_line_count = len(body_lines)

    if body_line_count > 500:
        errors.append(f"SKILL.md body is {body_line_count} lines (max 500)")
    elif body_line_count > 300:
        warnings.append(f"SKILL.md body is {body_line_count} lines (target: 150–300)")

    # Windows-style paths
    # Look for backslash paths but exclude markdown escape sequences and common false positives
    win_path_pattern = re.compile(r"[A-Za-z]:\\|\\[A-Za-z]+\\")
    for i, line in enumerate(body_lines, 1):
        if win_path_pattern.search(line):
            errors.append(f"Line {i}: Contains Windows-style backslash path — use forward slashes")
            break  # Report only first occurrence

    # File references check — find references to files and verify they exist
    ref_pattern = re.compile(r"(?:references|scripts)/[\w.-]+(?:\.(?:md|py|sh|txt))")
    referenced_files = set(ref_pattern.findall(body))
    for ref in referenced_files:
        ref_path = skill_path / ref
        if not ref_path.is_file():
            errors.append(f"Referenced file '{ref}' does not exist in skill directory")

    # Check for deeply nested reference directories
    refs_dir = skill_path / "references"
    if refs_dir.is_dir():
        for item in refs_dir.rglob("*"):
            if item.is_dir():
                relative = item.relative_to(refs_dir)
                if len(relative.parts) > 1:
                    errors.append(f"Deeply nested reference directory: {relative} (max 1 level deep)")

    # Reference files over 100 lines should have a TOC
    if refs_dir.is_dir():
        for ref_file in refs_dir.glob("*.md"):
            try:
                ref_content = ref_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError) as e:
                errors.append(f"Could not read reference file '{ref_file.name}': {e}")
                continue
            ref_lines = ref_content.strip().splitlines()
            if len(ref_lines) > 100:
                has_toc = any(
                    "table of contents" in line.lower() or "## contents" in line.lower()
                    for line in ref_lines[:20]
                )
                if not has_toc:
                    warnings.append(f"{ref_file.name} is {len(ref_lines)} lines — consider adding a table of contents")

    # Check that all reference files are listed in the body
    if refs_dir.is_dir():
        for ref_file in refs_dir.glob("*.md"):
            if ref_file.name not in body:
                warnings.append(f"Reference file '{ref_file.name}' is not mentioned in SKILL.md body")

    # TODO markers
    todo_count = body.lower().count("todo")
    if todo_count > 0:
        warnings.append(f"Found {todo_count} TODO marker(s) — resolve before shipping")

    # Check for auxiliary docs that shouldn't be in skill directory
    aux_files = ["README.md", "CHANGELOG.md", "CONTRIBUTING.md"]
    for aux in aux_files:
        if (skill_path / aux).is_file():
            warnings.append(f"Auxiliary file '{aux}' found in skill directory — not recommended")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_skill.py <skill-directory>")
        print("Example: python validate_skill.py skills/creating-skills")
        sys.exit(2)

    skill_dir = sys.argv[1]
    errors, warnings = validate(skill_dir)

    print(f"\nValidating: {skill_dir}")
    print("=" * 50)

    if warnings:
        print(f"\n[!] Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n[X] Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        print(f"\nResult: FAIL ({len(errors)} error(s), {len(warnings)} warning(s))")
        sys.exit(1)
    else:
        print(f"\nResult: PASS ({len(warnings)} warning(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()
