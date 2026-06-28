#!/usr/bin/env python3
"""Validate generated article files before publishing a draft branch."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED = {"id", "title", "category", "version", "review_status", "public", "post_to"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    if path.is_symlink() or path.suffix != ".md" or path.parent.name != "articles":
        return ["article must be a regular Markdown file directly under articles/"]

    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        return ["missing YAML frontmatter"]

    fields = {
        line.split(":", 1)[0].strip()
        for line in match.group(1).splitlines()
        if ":" in line and not line.startswith((" ", "\t"))
    }
    missing = sorted(REQUIRED - fields)
    if missing:
        errors.append("missing frontmatter fields: " + ", ".join(missing))

    body = text[match.end() :].strip()
    if not body.startswith("# "):
        errors.append("article body must start with an H1 heading")
    if len(body) < 800:
        errors.append("article body is shorter than 800 characters")
    if "```" in match.group(1):
        errors.append("frontmatter must not contain code fences")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_article.py <article.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    errors = validate(path)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
