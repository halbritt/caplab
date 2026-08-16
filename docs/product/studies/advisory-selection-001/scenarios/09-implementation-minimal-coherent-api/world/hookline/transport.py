"""HTTP transport used by DeliveryService.

Anything with a matching ``post`` method can stand in for it in tests.
"""

from __future__ import annotations

import urllib.error
import urllib.request


class TransportError(Exception):
    """The request could not be completed at all (DNS failure, refused, timed out)."""


class Response:
    def __init__(self, status: int, body: bytes = b""):
        self.status = status
        self.body = body


class HttpTransport:
    def post(self, url: str, body: bytes, headers: dict[str, str], timeout: float) -> Response:
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as raw:
                return Response(raw.status, raw.read())
        except urllib.error.HTTPError as err:
            return Response(err.code, err.read())
        except urllib.error.URLError as err:
            raise TransportError(str(err.reason)) from err
