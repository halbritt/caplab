"""Probe job model.

A :class:`ProbeJob` owns everything the scheduler needs to know about one
monitored endpoint: where to probe, how often, and how the last few attempts
went.  Jobs are plain mutable objects; the runtime controller updates them
in place when an operator changes settings without a restart.
"""

from __future__ import annotations

from upmon.config import DEFAULT_RETRIES, DEFAULT_TIMEOUT, clamp_interval


class ProbeJob:
    """One monitored endpoint and its scheduling state."""

    def __init__(
        self,
        name: str,
        url: str,
        poll_interval: float = 60.0,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        enabled: bool = True,
    ) -> None:
        self.name = name
        self.url = url
        # Operators sometimes put wild values in the config file; keep the
        # interval inside the supported operating band (see INC-2081).
        self.poll_interval = clamp_interval(poll_interval)
        self.timeout = float(timeout)
        self.retries = int(retries)
        self.enabled = bool(enabled)
        self.consecutive_failures = 0

    def record_result(self, ok: bool) -> None:
        """Fold one probe attempt into the job's failure streak."""
        if ok:
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1

    def snapshot(self) -> dict:
        """Public view of the job.

        Written verbatim to the status file and returned by the control
        socket's ``status`` and ``update`` replies, so the dashboard and
        ``upmonctl`` depend on these keys.
        """
        return dict(vars(self))

    def __repr__(self) -> str:
        return (
            f"ProbeJob(name={self.name!r}, url={self.url!r}, "
            f"every={self.poll_interval}s)"
        )
