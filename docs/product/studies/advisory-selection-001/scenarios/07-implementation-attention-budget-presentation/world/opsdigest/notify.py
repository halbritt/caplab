"""Deliver a rendered digest.

Real deployments also post to the chat webhook; everywhere else (tests,
dry runs) the digest lands in an outbox directory that a cron job ships.
"""
from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


class Outbox:
    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)

    def deliver(self, digest_text: str, now: datetime | None = None) -> Path:
        now = now or datetime.now(timezone.utc)
        self.directory.mkdir(parents=True, exist_ok=True)
        target = self.directory / f"digest-{now:%Y%m%d}.txt"
        target.write_text(digest_text, encoding="utf-8")
        webhook = os.environ.get("OPSDIGEST_WEBHOOK_URL")
        if webhook:
            post_webhook(webhook, digest_text)
        return target


def post_webhook(url: str, text: str) -> None:
    data = json.dumps({"text": text}).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(request, timeout=10)
