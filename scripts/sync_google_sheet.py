#!/usr/bin/env python3
"""Sync the content ledger CSV to a Google Sheet."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
DEFAULT_TAB = "Content Index"
PATH_COLUMNS = {
    "article_path",
    "cover_path",
    "note_package_path",
    "note_title_path",
    "note_body_path",
    "note_cover_path",
}


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


def service() -> Any:
    account_info = json.loads(required("GOOGLE_SERVICE_ACCOUNT_JSON"))
    credentials = service_account.Credentials.from_service_account_info(
        account_info,
        scopes=SCOPES,
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        rows = list(reader)
    if not headers:
        raise RuntimeError(f"{path} has no header row")
    return headers, rows


def github_url(repo: str, branch: str, path: str) -> str:
    path = path.strip().strip("/")
    if not path:
        return ""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    kind = "tree" if path.startswith("note-package/") else "blob"
    return f"https://github.com/{repo}/{kind}/{branch}/{path}"


def values_for_sheet(headers: list[str], rows: list[dict[str, str]]) -> list[list[str]]:
    repo = os.environ.get("GITHUB_REPOSITORY", "projectsn005-wq/Auto-AI-Memo")
    branch = os.environ.get("SHEET_GITHUB_BRANCH", "main")
    values = [headers]
    for row in rows:
        line: list[str] = []
        for header in headers:
            value = row.get(header, "")
            if header in PATH_COLUMNS:
                value = github_url(repo, branch, value)
            line.append(value)
        values.append(line)
    return values


def get_or_create_sheet_id(sheets: Any, spreadsheet_id: str, tab_name: str) -> int:
    metadata = sheets.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    for sheet in metadata.get("sheets", []):
        properties = sheet.get("properties", {})
        if properties.get("title") == tab_name:
            return int(properties["sheetId"])

    response = sheets.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [{"addSheet": {"properties": {"title": tab_name}}}]},
    ).execute()
    return int(response["replies"][0]["addSheet"]["properties"]["sheetId"])


def sync() -> None:
    spreadsheet_id = required("GOOGLE_SHEET_ID")
    tab_name = os.environ.get("GOOGLE_SHEET_TAB", DEFAULT_TAB).strip() or DEFAULT_TAB
    ledger_path = Path(os.environ.get("CONTENT_LEDGER_PATH", "admin/content-index.csv"))
    headers, rows = read_rows(ledger_path)
    values = values_for_sheet(headers, rows)
    sheets = service()
    sheet_id = get_or_create_sheet_id(sheets, spreadsheet_id, tab_name)

    sheets.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f"'{tab_name}'!A:Z",
        body={},
    ).execute()
    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"'{tab_name}'!A1",
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()

    request_count = len(headers)
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": request_count,
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 0.12,
                                    "green": 0.47,
                                    "blue": 0.71,
                                },
                                "textFormat": {
                                    "bold": True,
                                    "foregroundColor": {
                                        "red": 1,
                                        "green": 1,
                                        "blue": 1,
                                    },
                                },
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat)",
                    }
                },
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "gridProperties": {"frozenRowCount": 1},
                        },
                        "fields": "gridProperties.frozenRowCount",
                    }
                },
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": request_count,
                        }
                    }
                },
            ]
        },
    ).execute()
    print(f"Synced {len(rows)} rows to Google Sheet tab: {tab_name}")


def main() -> int:
    sync()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
