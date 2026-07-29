"""Cooperative scheduler that drives probes.

Single-threaded on purpose: probes are cheap blocking HTTP calls and the
whole point of upmon is to be simple enough to audit in an afternoon.
"""

from __future__ import annotations

import time


class Scheduler:
    """Runs each enabled job whenever its interval has elapsed."""

    def __init__(self, jobs, prober, *, clock=time.monotonic, sleep=time.sleep):
        self._jobs = list(jobs)
        self._prober = prober
        self._clock = clock
        self._sleep = sleep
        # Everything is due immediately on startup.
        self._next_due = {job.name: 0.0 for job in self._jobs}

    def run_pending(self) -> list[str]:
        """Run every enabled, due job once.  Returns the names that ran."""
        now = self._clock()
        ran = []
        for job in self._jobs:
            if not job.enabled:
                continue
            if now < self._next_due[job.name]:
                continue
            ok = self._prober(job)
            job.record_result(ok)
            self._next_due[job.name] = now + job.poll_interval
            ran.append(job.name)
        return ran

    def run_forever(self) -> None:  # pragma: no cover - exercised manually
        while True:
            self.run_pending()
            self._sleep(1.0)
