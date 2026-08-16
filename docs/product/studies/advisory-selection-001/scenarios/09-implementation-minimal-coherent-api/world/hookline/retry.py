"""Retry policy for transient delivery failures."""

from __future__ import annotations

import random
from dataclasses import dataclass

DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_BACKOFF = 0.0
DEFAULT_MULTIPLIER = 2.0
DEFAULT_CAP = 30.0


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = DEFAULT_MAX_ATTEMPTS
    backoff: float = DEFAULT_BACKOFF
    multiplier: float = DEFAULT_MULTIPLIER
    jitter: float = 0.0
    cap: float = DEFAULT_CAP

    @classmethod
    def from_options(cls, options: dict) -> "RetryPolicy":
        return cls(
            max_attempts=int(options.get("max_attempts", DEFAULT_MAX_ATTEMPTS)),
            backoff=float(options.get("retry_backoff", DEFAULT_BACKOFF)),
            multiplier=float(options.get("retry_multiplier", DEFAULT_MULTIPLIER)),
            jitter=float(options.get("retry_jitter", 0.0)),
            cap=float(options.get("retry_cap", DEFAULT_CAP)),
        )

    def delay_before(self, attempt: int) -> float:
        """Delay before the given attempt; attempt 2 is the first retry."""
        base = self.backoff * (self.multiplier ** (attempt - 2))
        capped = min(base, self.cap)
        if self.jitter:
            capped += random.uniform(0.0, self.jitter)
        return capped
