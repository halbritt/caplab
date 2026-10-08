"""Reuse-safe Linux process observations inside the existing native supervisor.

A reaped Bubblewrap monitor is not a namespace-quiescence oracle. Only the
observed namespace init's kernel death can close that namespace. No signalling,
new process, persistent registry or account authority is provided here.
"""

from __future__ import annotations

import json
import os
import select
import time
from pathlib import Path


class ProcessProofUnavailable(ValueError):
    pass


class SandboxReadiness:
    """Own bwrap block/info pipes until an exact namespace-init pidfd is held.

    Info is a bounded hint from the pinned adapter, validated against /proc and
    a reuse-safe pidfd. EOF is never death evidence. Closing the block writer
    also releases bwrap: callers must terminate/reap the owned monitor before
    closing this context on any unsuccessful startup. A crash leaves uncertainty.
    """

    def __init__(self):
        self.block_reader = self.block_writer = -1
        self.info_reader = self.info_writer = -1
        self.witness = None
        self.released = False
        try:
            self.block_reader, self.block_writer = os.pipe2(os.O_CLOEXEC)
            self.info_reader, self.info_writer = os.pipe2(os.O_CLOEXEC)
            os.set_blocking(self.info_reader, False)
        except BaseException:
            self.close()
            raise

    @property
    def pass_fds(self) -> tuple[int, int]:
        return self.block_reader, self.info_writer

    def child_started(self) -> None:
        for name in ("block_reader", "info_writer"):
            descriptor = getattr(self, name)
            if descriptor >= 0:
                os.close(descriptor)
                setattr(self, name, -1)

    def observe(self, outer_pid: int, *, deadline: float) -> ProcessWitness:
        if self.witness is not None or self.released:
            raise ProcessProofUnavailable("sandbox_readiness_already_observed")
        data = bytearray()
        poller = select.poll()
        poller.register(self.info_reader, select.POLLIN | select.POLLHUP)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ProcessProofUnavailable("sandbox_readiness_deadline")
            events = poller.poll(min(50, max(1, int(remaining * 1000))))
            if not events:
                continue
            if any(mask & (select.POLLERR | select.POLLNVAL) for _, mask in events):
                raise ProcessProofUnavailable("sandbox_readiness_descriptor_invalid")
            try:
                chunk = os.read(self.info_reader, 8193 - len(data))
            except BlockingIOError:
                continue
            data.extend(chunk)
            if len(data) > 8192:
                raise ProcessProofUnavailable("sandbox_readiness_info_oversized")
            if not chunk:
                break
        try:
            info = json.loads(data)
            pid = info["child-pid"]
            outer = identity(outer_pid)
            witness = ProcessWitness.open(pid)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            raise ProcessProofUnavailable("sandbox_readiness_identity_unavailable") from error
        try:
            fact = witness.fact
            if (fact["parent_pid"] != outer_pid
                    or fact["boot_id"] != outer["boot_id"]
                    or len(fact["namespace_pids"]) != len(outer["namespace_pids"]) + 1
                    or fact["namespace_pids"][-1] != 1):
                raise ProcessProofUnavailable("sandbox_readiness_identity_mismatch")
            if time.monotonic() >= deadline:
                raise ProcessProofUnavailable("sandbox_readiness_deadline")
        except BaseException:
            witness.close()
            raise
        self.witness = witness
        return witness

    def release(self) -> None:
        if self.witness is None or self.released:
            raise ProcessProofUnavailable("sandbox_readiness_not_observed")
        os.write(self.block_writer, b"1")
        os.close(self.block_writer)
        self.block_writer = -1
        self.released = True

    def close(self) -> None:
        try:
            if self.witness is not None:
                self.witness.close()
                self.witness = None
        finally:
            for name in ("block_reader", "block_writer", "info_reader", "info_writer"):
                descriptor = getattr(self, name)
                if descriptor >= 0:
                    os.close(descriptor)
                    setattr(self, name, -1)

    def __enter__(self) -> SandboxReadiness:
        return self

    def __exit__(self, *_args) -> None:
        self.close()


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
        return any(mask & (select.POLLIN | select.POLLHUP) for _, mask in events)

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
