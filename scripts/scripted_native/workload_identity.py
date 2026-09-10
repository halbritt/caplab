"""Trusted setup for a non-root workload beneath its network's user-namespace owner."""

import os
from pathlib import Path


def enter_parent_owned_workload():
    """Create the selected child mapping; caller must drop privileges before handoff.

    This mutates only the calling process's user namespace. The caller must own
    the fresh parent/network and hold the setup privileges needed by the kernel.
    Any error is fatal to that workload; partially configured namespaces must
    never be released or retried in place.
    """
    if os.getuid() != 0 or os.getgid() != 0:
        raise ValueError("parent-owned setup requires mapped root")
    os.unshare(os.CLONE_NEWUSER)
    Path("/proc/self/setgroups").write_text("deny\n", encoding="ascii")
    Path("/proc/self/uid_map").write_text("1000 0 1\n", encoding="ascii")
    Path("/proc/self/gid_map").write_text("1000 0 1\n", encoding="ascii")
    if os.getuid() != 1000 or os.getgid() != 1000:
        raise ValueError("parent-owned workload mapping differs")
