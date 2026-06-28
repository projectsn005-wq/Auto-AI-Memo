#!/usr/bin/env python3
"""Build a copy-ready note package from an article and its cover image."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


def build(article_path: Path, cover_path: Path, destination: Path) -> None:
    text = article_path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, flags=re.DOTALL)
    if not match:
        raise RuntimeError("article has no YAML frontmatter")

    title_match = re.search(r"^title:\s*(.+?)\s*$", match.group(1), flags=re.MULTILINE)
    if not title_match:
        raise RuntimeError("frontmatter has no title")

    title = title_match.group(1).strip().strip("'\"")
    body = match.group(2).strip() + "\n"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "title.txt").write_text(title + "\n", encoding="utf-8")
    (destination / "body.md").write_text(body, encoding="utf-8")
    shutil.copyfile(cover_path, destination / "cover.png")
    (destination / "README.md").write_text(
        "# note投稿パッケージ\n\n"
        "1. `cover.png`をnoteの見出し画像へ設定します。\n"
        "2. `title.txt`の内容をタイトルへ貼り付けます。\n"
        "3. `body.md`の内容を本文へ貼り付けます。\n"
        "4. 改行・見出し・リンクを確認してから公開します。\n\n"
        "noteには一般利用者向けの公式投稿APIがないため、最終公開だけはnote画面で行います。\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("article", type=Path)
    parser.add_argument("cover", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    build(args.article, args.cover, args.destination)
    print(args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
