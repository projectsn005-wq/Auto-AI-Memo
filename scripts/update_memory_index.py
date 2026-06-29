#!/usr/bin/env python3
"""Update Obsidian-friendly memory notes and the content management ledger."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LEDGER_FIELDS = [
    "no",
    "issue_number",
    "title",
    "status",
    "category",
    "github_issue_url",
    "draft_pr_url",
    "actions_run_url",
    "article_path",
    "cover_path",
    "note_package_path",
    "note_title_path",
    "note_body_path",
    "note_cover_path",
    "note_url",
    "source_urls",
    "created_at",
    "updated_at",
    "owner",
    "next_action",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_frontmatter(article: Path) -> tuple[dict[str, str], str]:
    text = article.read_text(encoding="utf-8").lstrip("\ufeff")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, flags=re.DOTALL)
    if not match:
        raise RuntimeError(f"{article} has no YAML frontmatter")

    metadata: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("'\"")
    return metadata, match.group(2).strip()


def read_proposal(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def extract_urls(*texts: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for text in texts:
        for url in re.findall(r"https?://[^\s)>\"]+", text or ""):
            cleaned = url.rstrip(".,;。、")
            if cleaned not in seen:
                seen.add(cleaned)
                urls.append(cleaned)
    return urls


def relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def read_ledger(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_ledger(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows.sort(key=lambda row: int(row.get("no") or row.get("issue_number") or 0))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in LEDGER_FIELDS})


def write_memory_note(path: Path, row: dict[str, str], body_excerpt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    title = row["title"].replace('"', '\\"')
    source_urls = [url for url in row.get("source_urls", "").split(" ") if url]
    source_lines = "\n".join(f"- {url}" for url in source_urls) or "- 未登録"
    note_url = row.get("note_url") or "未公開"

    path.write_text(
        "---\n"
        "type: ai_memory\n"
        f"issue_number: {row['issue_number']}\n"
        f"title: \"{title}\"\n"
        f"status: {row['status']}\n"
        f"category: \"{row['category']}\"\n"
        f"github_issue_url: {row['github_issue_url']}\n"
        f"draft_pr_url: {row['draft_pr_url']}\n"
        f"actions_run_url: {row['actions_run_url']}\n"
        f"article_path: {row['article_path']}\n"
        f"note_url: {note_url}\n"
        "tags:\n"
        "  - auto-ai-memo\n"
        "  - article-memory\n"
        "---\n\n"
        f"# {row['title']}\n\n"
        "## これは何の記憶か\n\n"
        "AIが次回以降の会話や記事生成で参照しやすいように、記事化の判断・生成物・リンクを1枚にまとめた外部記憶です。"
        "Obsidianではfrontmatterのプロパティとして検索・絞り込みできます。\n\n"
        "## 生成物リンク\n\n"
        f"- GitHub Issue: {row['github_issue_url']}\n"
        f"- 草稿PR: {row['draft_pr_url'] or '未作成'}\n"
        f"- Actions実行: {row['actions_run_url']}\n"
        f"- 記事Markdown: `{row['article_path']}`\n"
        f"- 見出し画像: `{row['cover_path']}`\n"
        f"- note投稿パッケージ: `{row['note_package_path']}`\n"
        f"- note公開URL: {note_url}\n\n"
        "## ソース・参照URL\n\n"
        f"{source_lines}\n\n"
        "## 次のアクション\n\n"
        f"- {row['next_action']}\n\n"
        "## 記事本文の冒頭メモ\n\n"
        f"{body_excerpt[:1200]}\n",
        encoding="utf-8",
    )


def write_memory_readme(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Auto AI Memo Memory\n\n"
        "このフォルダはObsidianでそのまま開けるAI外部記憶です。\n\n"
        "- `articles/issue-*.md`: 記事ごとの判断・生成物・リンク\n"
        "- `../admin/content-index.csv`: スプレッドシート向け管理台帳\n\n"
        "目的は、AIチャットの圧縮や履歴消失で抜けやすい文脈を、GitHub上のMarkdownとして保持することです。"
        "この記憶は秘密情報を含めず、Issue、PR、記事、note公開URLの索引として使います。\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-number", required=True)
    parser.add_argument("--article", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--note-package", required=True, type=Path)
    parser.add_argument("--proposal-json", type=Path)
    parser.add_argument("--pr-url", default="")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--note-url", default="")
    parser.add_argument("--owner", default="Auto-AI-Memo")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    root = args.root.resolve()
    metadata, body = read_frontmatter(args.article)
    proposal = read_proposal(args.proposal_json)
    updated_at = now_iso()
    issue_number = str(args.issue_number)
    issue_url = proposal.get("url", "")
    source_urls = extract_urls(proposal.get("body", ""), body)

    ledger_path = root / "admin" / "content-index.csv"
    rows = read_ledger(ledger_path)
    existing = next((row for row in rows if row.get("issue_number") == issue_number), None)
    created_at = existing.get("created_at", updated_at) if existing else updated_at

    row = {
        "no": issue_number,
        "issue_number": issue_number,
        "title": metadata.get("title") or proposal.get("title", "").replace("[提案]", "").strip(),
        "status": "草稿PR作成済み" if args.pr_url else "noteパッケージ作成済み",
        "category": metadata.get("category", ""),
        "github_issue_url": issue_url,
        "draft_pr_url": args.pr_url,
        "actions_run_url": args.run_url,
        "article_path": relative(args.article, root),
        "cover_path": relative(args.cover, root),
        "note_package_path": relative(args.note_package, root),
        "note_title_path": f"{relative(args.note_package, root)}/title.txt",
        "note_body_path": f"{relative(args.note_package, root)}/body.md",
        "note_cover_path": f"{relative(args.note_package, root)}/cover.png",
        "note_url": args.note_url or (existing.get("note_url", "") if existing else ""),
        "source_urls": " ".join(source_urls),
        "created_at": created_at,
        "updated_at": updated_at,
        "owner": args.owner,
        "next_action": "noteへ貼り付けて公開し、公開URLを台帳へ追記する",
    }

    if existing:
        existing.update(row)
    else:
        rows.append(row)

    write_ledger(ledger_path, rows)
    write_memory_readme(root / "memory" / "README.md")
    write_memory_note(root / "memory" / "articles" / f"issue-{issue_number}.md", row, body)
    print(f"updated {ledger_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
