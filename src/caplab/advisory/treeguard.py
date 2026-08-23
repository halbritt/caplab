"""Notice a live-tree write; do not find it by luck.

On 2026-08-23 a replayed build case escaped an agentic lane and overwrote
three files in the live striatum-next checkout. It was found ~40 minutes
later by an operator reading `git status` before a commit — the postmortem
names "any mechanism that notices a live-tree write" as the thing that did
not exist. This is that mechanism for CAPLAB sweeps: a snapshot of tracked
modifications in the protected checkouts before a run, compared after.
Untracked files do not count — sweeps create run directories legitimately.
"""

from __future__ import annotations

import os
import subprocess

PROTECTED_REPOS = [os.path.expanduser("~/git/striatum-next"),
                   os.path.expanduser("~/git/caplab")]


def snapshot(repos: list[str] | None = None) -> dict[str, str]:
    out = {}
    for repo in repos or PROTECTED_REPOS:
        if not os.path.isdir(os.path.join(repo, ".git")):
            continue
        status = subprocess.run(
            ["git", "-C", repo, "status", "--porcelain",
             "--untracked-files=no"],
            capture_output=True, text=True)
        out[repo] = status.stdout if status.returncode == 0 else "?"
    return out


def changed(before: dict[str, str], after: dict[str, str]) -> bool:
    return any(after.get(repo) != state for repo, state in before.items())


def diff(before: dict[str, str], after: dict[str, str]) -> dict[str, str]:
    return {repo: after.get(repo, "") for repo, state in before.items()
            if after.get(repo) != state}
