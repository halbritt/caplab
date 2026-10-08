"""Reuse-safe Linux process observations inside the existing native supervisor.

A reaped Bubblewrap monitor is not a namespace-quiescence oracle. Only the
observed namespace init's kernel death can close that namespace. No signalling,
new process, persistent registry or account authority is provided here.
"""

from __future__ import annotations

import os
import select
import time
from pathlib import Path


class ProcessProofUnavailable(ValueError):
    pass


def boot_id() -> str:
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip()


def identity(pid: int) -> dict:
    if type(pid) is not int or pid <= 1:
        raise ProcessProofUnavailable("process_identity_invalid")
    root = Path("/proc") / str(pid)
    fields = (root / "stat").read_text().rsplit(")", 1)[1].split()
    status = dict(
        line.split(":", 1)
        for line in (root / "status").read_text().splitlines()
        if ":" in line
    )
    return {
        "boot_id": boot_id(),
        "pid": pid,
        "start_ticks": int(fields[19]),
        "parent_pid": int(status["PPid"].strip()),
        "namespace_pids": [int(p) for p in status["NSpid"].split()],
    }


class ProcessWitness:
    """A live pidfd binds one exact process, never just a numeric PID."""

    def __init__(self, descriptor: int, fact: dict):
        self.descriptor = descriptor
        self.fact = fact

    @classmethod
    def open(cls, pid: int) -> ProcessWitness:
        before = identity(pid)
        descriptor = os.pidfd_open(pid)
        try:
            after = identity(pid)
            if before != after:
                raise ProcessProofUnavailable("process_identity_changed")
        except BaseException:
            os.close(descriptor)
            raise
        return cls(descriptor, before)

    def dead(self, timeout_ms: int = 0) -> bool:
        poller = select.poll()
        poller.register(self.descriptor, select.POLLIN)
        events = poller.poll(timeout_ms)
        if any(mask & (select.POLLNVAL | select.POLLERR) for _, mask in events):
            raise ProcessProofUnavailable("process_pidfd_invalid")
        return any(mask & select.POLLIN for _, mask in events)

    def close(self) -> None:
        if self.descriptor >= 0:
            os.close(self.descriptor)
            self.descriptor = -1

    def __enter__(self) -> ProcessWitness:
        return self

    def __exit__(self, *_args) -> None:
        self.close()


def namespace_init(outer_pid: int, *, deadline: float) -> ProcessWitness | None:
    """Observe the actual direct child PID1, bounded by native remaining time.

    Missing /proc access, pidfd support, a fast exit or an unobserved initializer
    provides no quiescence proof. Never infer death from a failed inspection.
    """
    stop = min(deadline, time.monotonic() + 0.05)
    while True:
        try:
            outer = identity(outer_pid)
            children = (
                Path(f"/proc/{outer_pid}/task/{outer_pid}/children").read_text().split()
            )
            for child in children:
                witness = None
                try:
                    witness = ProcessWitness.open(int(child))
                    fact = witness.fact
                    if (
                        fact["parent_pid"] == outer_pid
                        and len(fact["namespace_pids"])
                        == len(outer["namespace_pids"]) + 1
                        and fact["namespace_pids"][-1] == 1
                    ):
                        return witness
                except (OSError, ValueError, KeyError, AttributeError):
                    pass  # unavailable observation, never a proof
                if witness is not None:
                    witness.close()
        except (OSError, ValueError, KeyError, AttributeError):
            return None
        remaining = stop - time.monotonic()
        if remaining <= 0:
            return None
        time.sleep(min(remaining, 0.005))
