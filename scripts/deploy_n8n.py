#!/usr/bin/env python3
"""Create or update the repository's workflows through the n8n Public API."""

from __future__ import annotations

import json
import os
import ssl
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / "operations" / "n8n").glob("*.json"))


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


def replace(value: Any, substitutions: dict[str, str]) -> Any:
    if isinstance(value, str):
        for old, new in substitutions.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace(item, substitutions) for item in value]
    if isinstance(value, dict):
        return {key: replace(item, substitutions) for key, item in value.items()}
    return value


class N8nClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.context = ssl.create_default_context()

    def request(self, method: str, path: str, payload: Any | None = None) -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            headers={
                "X-N8N-API-KEY": self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            method=method,
        )
        with urllib.request.urlopen(request, timeout=60, context=self.context) as response:
            content = response.read()
            return json.loads(content) if content else {}


def main() -> int:
    base_url = required("N8N_BASE_URL")
    client = N8nClient(base_url, required("N8N_API_TOKEN"))
    substitutions = {
        "SET_ANTHROPIC_CREDENTIAL_ID": required("N8N_ANTHROPIC_CREDENTIAL_ID"),
        "SET_GITHUB_CREDENTIAL_ID": required("N8N_GITHUB_CREDENTIAL_ID"),
        "SET_SLACK_CREDENTIAL_ID": required("N8N_SLACK_CREDENTIAL_ID"),
        "SET_SLACK_CHANNEL_ID": required("SLACK_CHANNEL_ID"),
        "SET_SLACK_APPROVER_IDS": required("SLACK_APPROVER_IDS"),
        "SET_SLACK_INTERACTION_SECRET": required("SLACK_INTERACTION_SECRET"),
    }

    existing = client.request("GET", "/api/v1/workflows?limit=250").get("data", [])
    by_name = {workflow["name"]: workflow for workflow in existing}

    for workflow_path in WORKFLOWS:
        workflow = replace(json.loads(workflow_path.read_text(encoding="utf-8")), substitutions)
        payload = {
            key: workflow[key]
            for key in ("name", "nodes", "connections", "settings")
            if key in workflow
        }
        current = by_name.get(workflow["name"])
        if current:
            workflow_id = current["id"]
            client.request("PUT", f"/api/v1/workflows/{urllib.parse.quote(str(workflow_id))}", payload)
            action = "updated"
        else:
            created = client.request("POST", "/api/v1/workflows", payload)
            workflow_id = created["id"]
            action = "created"
        client.request("POST", f"/api/v1/workflows/{urllib.parse.quote(str(workflow_id))}/activate")
        print(f"{action} and activated: {workflow['name']} ({workflow_id})")

    secret = substitutions["SET_SLACK_INTERACTION_SECRET"]
    print(f"Slack Interactivity URL: {base_url}/webhook/auto-ai-memo-approve-{secret}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
