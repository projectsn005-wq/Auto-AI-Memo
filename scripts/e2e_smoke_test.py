#!/usr/bin/env python3
"""Run an end-to-end smoke test for the n8n proposal workflow.

The test intentionally stops before pressing the Slack approval button. That
button is the human approval gate. Everything before it should be automatic:
n8n receives the webhook, Claude creates proposals, GitHub Issues are created,
and Slack receives proposal messages.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any


REQUIRED = [
    "N8N_BASE_URL",
    "N8N_API_TOKEN",
    "SLACK_CHANNEL_ID",
    "GITHUB_TOKEN",
    "GITHUB_REPOSITORY",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


def check_required() -> None:
    missing = [name for name in REQUIRED if not os.environ.get(name, "").strip()]
    if missing:
        raise RuntimeError("Missing required secrets/env: " + ", ".join(missing))


def request_json(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    payload: Any | None = None,
    timeout: int = 60,
) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read()
            if not body:
                return {}
            content_type = res.headers.get("content-type", "")
            if "application/json" in content_type:
                return json.loads(body.decode("utf-8"))
            return {"status": res.status, "body": body.decode("utf-8", errors="replace")}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed with HTTP {exc.code}: {body}") from exc


def request_text(method: str, url: str, headers: dict[str, str] | None = None) -> str:
    req = urllib.request.Request(url, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return res.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed with HTTP {exc.code}: {body}") from exc


def slack_message(text: str) -> None:
    token = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    channel = os.environ.get("SLACK_CHANNEL_ID", "").strip()
    if not token or not channel:
        return
    response = request_json(
        "POST",
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        payload={"channel": channel, "text": text},
    )
    if response.get("ok") is not True:
        print("Slack notification failed:", json.dumps(response, ensure_ascii=False))


def github_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {required('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def list_recent_proposal_issues(since_iso: str) -> list[dict[str, Any]]:
    repo = required("GITHUB_REPOSITORY")
    query = urllib.parse.urlencode(
        {
            "state": "open",
            "since": since_iso,
            "per_page": "10",
        }
    )
    url = f"https://api.github.com/repos/{repo}/issues?{query}"
    issues = request_json("GET", url, headers=github_headers())
    proposal_prefix = "[\u63d0\u6848]"
    return [
        issue
        for issue in issues
        if "pull_request" not in issue
        and str(issue.get("title", "")).startswith(proposal_prefix)
    ]


def n8n_headers() -> dict[str, str]:
    return {
        "X-N8N-API-KEY": required("N8N_API_TOKEN"),
        "Accept": "application/json",
    }


def n8n_api(path: str) -> Any:
    base = required("N8N_BASE_URL").rstrip("/")
    return request_json("GET", base + path, headers=n8n_headers())


def find_workflow_id(name_prefix: str) -> str | None:
    try:
        workflows = n8n_api("/api/v1/workflows?limit=250").get("data", [])
    except Exception as exc:  # noqa: BLE001
        print(f"Could not list n8n workflows: {exc}")
        return None
    for workflow in workflows:
        if str(workflow.get("name", "")).startswith(name_prefix):
            return str(workflow.get("id"))
    return None


def latest_n8n_execution(workflow_id: str | None) -> tuple[dict[str, Any] | None, str]:
    if not workflow_id:
        return None, "n8n workflow id was not found."
    query = urllib.parse.urlencode({"workflowId": workflow_id, "limit": "5"})
    try:
        executions = n8n_api(f"/api/v1/executions?{query}").get("data", [])
    except Exception as exc:  # noqa: BLE001
        return None, f"Could not read n8n executions via Public API: {exc}"
    if not executions:
        return None, f"No n8n executions found for workflow id {workflow_id}."

    latest = executions[0]
    execution_id = latest.get("id")
    summary = {
        "id": execution_id,
        "workflowId": latest.get("workflowId"),
        "status": latest.get("status") or latest.get("finished"),
        "mode": latest.get("mode"),
        "startedAt": latest.get("startedAt"),
        "stoppedAt": latest.get("stoppedAt"),
    }
    detail = ""
    if execution_id:
        try:
            full = n8n_api(f"/api/v1/executions/{execution_id}?includeData=true")
            detail = json.dumps(full.get("data", full), ensure_ascii=False)[:4000]
        except Exception as exc:  # noqa: BLE001
            detail = f"Could not fetch execution detail: {exc}"
    return latest, "Latest n8n execution:\n" + json.dumps(summary, ensure_ascii=False, indent=2) + "\n" + detail


def latest_n8n_execution_diagnostic(workflow_id: str | None) -> str:
    return latest_n8n_execution(workflow_id)[1]


def execution_looks_failed(execution: dict[str, Any] | None) -> bool:
    if not execution:
        return False
    status = str(execution.get("status") or "").lower()
    if status in {"error", "failed", "crashed"}:
        return True
    if execution.get("finished") is False and execution.get("stoppedAt"):
        return True
    return False


def trigger_n8n() -> None:
    base = required("N8N_BASE_URL").rstrip("/")
    response = request_text("GET", base + "/webhook/auto-ai-memo-proposals")
    print("n8n webhook response:", response)


def run(wait_seconds: int, poll_interval: int) -> int:
    check_required()
    started = now_iso()
    workflow_id = find_workflow_id("01 週次記事提案")
    print(f"Started smoke test at {started}")
    print(f"n8n proposal workflow id: {workflow_id or 'not found'}")
    trigger_n8n()

    deadline = time.time() + wait_seconds
    issues: list[dict[str, Any]] = []
    while time.time() < deadline:
        issues = list_recent_proposal_issues(started)
        if issues:
            break
        time.sleep(poll_interval)

    if issues:
        latest_execution, diagnostic = latest_n8n_execution(workflow_id)
        if execution_looks_failed(latest_execution):
            message = (
                "E2E smoke test failed after GitHub Issue creation.\n"
                "GitHub Issue was created, but n8n latest execution reports failure. "
                "Likely failing area: Slack notification or a downstream n8n node.\n\n"
                f"{diagnostic}"
            )
            print(message)
            slack_message(message[:3500])
            return 1
        lines = [
            "E2E smoke test passed: proposal Issues were created and n8n did not report a failed execution.",
            *[f"- #{issue['number']} {issue['title']} {issue['html_url']}" for issue in issues[:3]],
            "Next human step: press the Slack approval button for one proposal.",
        ]
        message = "\n".join(lines)
        print(message)
        slack_message(message)
        return 0

    diagnostic = latest_n8n_execution_diagnostic(workflow_id)
    message = (
        "E2E smoke test failed before GitHub Issue creation.\n"
        "Likely failing area: n8n internal workflow, Claude credential, GitHub credential, or Slack setup.\n\n"
        f"{diagnostic}"
    )
    print(message)
    slack_message(message[:3500])
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait-seconds", type=int, default=180)
    parser.add_argument("--poll-interval", type=int, default=10)
    args = parser.parse_args()
    return run(args.wait_seconds, args.poll_interval)


if __name__ == "__main__":
    raise SystemExit(main())
