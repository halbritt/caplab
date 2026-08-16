"""The actual HTTP probe."""

from __future__ import annotations

import urllib.error
import urllib.request


def http_probe(job) -> bool:
    """Blocking GET against the job's URL.

    True when the endpoint answers with a non-error status within the job's
    timeout, allowing ``retries`` extra attempts.
    """
    for _ in range(job.retries + 1):
        try:
            with urllib.request.urlopen(job.url, timeout=job.timeout) as resp:
                if 200 <= resp.status < 400:
                    return True
        except (urllib.error.URLError, OSError, TimeoutError):
            continue
    return False
