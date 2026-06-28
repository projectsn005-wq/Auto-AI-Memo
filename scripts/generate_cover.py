#!/usr/bin/env python3
"""Generate a landscape note cover through the OpenAI Image API."""

from __future__ import annotations

import argparse
import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


ENDPOINT = "https://api.openai.com/v1/images/generations"


def generate(prompt_path: Path, output_path: Path) -> None:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    prompt = prompt_path.read_text(encoding="utf-8").strip()
    if not prompt:
        raise RuntimeError("cover prompt is empty")

    payload = json.dumps(
        {
            "model": "gpt-image-2",
            "prompt": prompt,
            "size": "1536x1024",
            "quality": "medium",
            "output_format": "png",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"OpenAI Image API failed ({exc.code}): {detail}") from exc

    image_data = result.get("data", [{}])[0].get("b64_json")
    if not image_data:
        raise RuntimeError("OpenAI Image API response did not contain b64_json")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(image_data, validate=True))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    generate(args.prompt, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
