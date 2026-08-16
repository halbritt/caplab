"""Control-plane client.

All device-to-control-plane traffic goes through
:class:`ControlPlaneClient`. Transient failures (timeouts, 5xx,
connection resets) are retried a bounded number of times before the
sync attempt is abandoned; the agent will simply try again at its next
scheduled check-in.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Mapping

MAX_ATTEMPTS = 6
RETRY_DELAY_SECONDS = 5.0
REQUEST_TIMEOUT_SECONDS = 10.0


class TransientError(RuntimeError):
    """A failure worth retrying (timeout, 5xx, connection reset)."""


class SyncError(RuntimeError):
    """A check-in that failed after every attempt."""


def http_send(url: str, body: Mapping[str, Any]) -> dict[str, Any]:
    """Perform one HTTP exchange with the control plane."""
    data = json.dumps(dict(body)).encode()
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(
            request, timeout=REQUEST_TIMEOUT_SECONDS
        ) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code >= 500:
            raise TransientError(f"control plane returned {exc.code}") from exc
        raise
    except (urllib.error.URLError, TimeoutError) as exc:
        raise TransientError(str(exc)) from exc


class ControlPlaneClient:
    """Thin client for the check-in endpoint, with bounded retries."""

    def __init__(
        self,
        base_url: str,
        send: Callable[[str, Mapping[str, Any]], dict[str, Any]] | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._url = base_url.rstrip("/") + "/v1/checkin"
        self._send = send if send is not None else http_send
        self._sleep = sleep

    def check_in(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """POST one check-in, retrying transient failures.

        Returns the control plane's response document, which may carry
        updated config for the device.
        """
        last_error: TransientError | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return self._send(self._url, payload)
            except TransientError as exc:
                last_error = exc
                if attempt == MAX_ATTEMPTS:
                    break
                self._sleep(RETRY_DELAY_SECONDS)
        raise SyncError(
            f"check-in failed after {MAX_ATTEMPTS} attempts: {last_error}"
        ) from last_error
