#!/usr/bin/env python3
"""Register a published note URL in the local ledger and memory note."""

from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-number", required=True)
    parser.add_argument("--note-url", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    if not re.match(r"^https?://", args.note_url):
        raise RuntimeError("note-url must start with http:// or https://")

    root = args.root.resolve()
    ledger_path = root / "admin" / "content-index.csv"
    if not ledger_path.exists():
        raise RuntimeError("admin/content-index.csv does not exist")

    with ledger_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)

    changed = False
    for row in rows:
        if row.get("issue_number") == str(args.issue_number):
            row["note_url"] = args.note_url
            row["status"] = "note公開済み"
            row["updated_at"] = now_iso()
            row["next_action"] = "公開後の反応・改善点を追記する"
            changed = True
            break

    if not changed:
        raise RuntimeError(f"issue {args.issue_number} was not found in ledger")

    with ledger_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    memory_path = root / "memory" / "articles" / f"issue-{args.issue_number}.md"
    if memory_path.exists():
        text = memory_path.read_text(encoding="utf-8")
        text = re.sub(r"note_url: .*", f"note_url: {args.note_url}", text, count=1)
        text = re.sub(r"status: .*", "status: note公開済み", text, count=1)
        text = re.sub(r"- note公開URL: .*", f"- note公開URL: {args.note_url}", text, count=1)
        text = text.replace(
            "- noteへ貼り付けて公開し、公開URLを台帳へ追記する",
            "- 公開後の反応・改善点を追記する",
        )
        memory_path.write_text(text, encoding="utf-8")

    print(f"registered note URL for issue {args.issue_number}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
