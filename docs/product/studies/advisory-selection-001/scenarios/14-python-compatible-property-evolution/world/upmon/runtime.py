"""Runtime control: applies operator updates to live jobs without a restart.

The control socket hands us ``{"cmd": "update", "job": name, "set": {...}}``
payloads.  Updates are applied directly to the running :class:`ProbeJob`
objects, so they take effect on the scheduler's next pass.
"""

from __future__ import annotations

from upmon.probe import ProbeJob

#: Fields an operator may change at runtime.
MUTABLE_FIELDS = frozenset({"url", "poll_interval", "timeout", "retries", "enabled"})


class UnknownJobError(KeyError):
    """The update names a job we are not running."""


class UnknownFieldError(KeyError):
    """The update names a field that cannot be changed at runtime."""


class RuntimeController:
    """Owns the live job table on behalf of the control socket."""

    def __init__(self, jobs) -> None:
        self._jobs: dict[str, ProbeJob] = {job.name: job for job in jobs}

    def apply_update(self, name: str, changes: dict) -> dict:
        """Apply operator changes to one job and return its new snapshot."""
        try:
            job = self._jobs[name]
        except KeyError:
            raise UnknownJobError(name) from None
        unknown = set(changes) - MUTABLE_FIELDS
        if unknown:
            raise UnknownFieldError(", ".join(sorted(unknown)))
        for field, value in changes.items():
            setattr(job, field, value)
        return job.snapshot()

    def status(self) -> list[dict]:
        """Snapshots of every job, in registration order."""
        return [job.snapshot() for job in self._jobs.values()]
