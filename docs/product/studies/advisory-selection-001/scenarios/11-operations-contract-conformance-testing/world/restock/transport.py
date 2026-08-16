"""Minimal HTTP transport, kept behind a small interface so tests can stub it."""

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Response:
    status: int
    headers: dict
    body: bytes

    def json(self):
        return json.loads(self.body.decode("utf-8"))


class UrllibTransport:
    """Blocking GET transport over urllib. One instance per process is fine."""

    def __init__(self, timeout_s: float = 10.0):
        self._timeout_s = timeout_s

    def get(self, url: str, params: dict | None = None, headers: dict | None = None) -> Response:
        query = urllib.parse.urlencode(params or {})
        request = urllib.request.Request(
            f"{url}?{query}" if query else url,
            headers=headers or {},
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=self._timeout_s) as raw:
            return Response(status=raw.status, headers=dict(raw.headers), body=raw.read())
