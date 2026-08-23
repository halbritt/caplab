"""Advisory substrate CAS: bodies retained at registration, forever.

Hashes without bodies cannot be audited: on 2026-08-23, 7 of 25
deepseek-refused control bodies were unreachable at audit time because
their exchange dispatch bundles had been reaped. The registry pins every
substrate's sha256; this store keeps the bytes those hashes name, keyed by
the hash, verified on every read. Write-through happens at harvest and on
any successful body load; the store lives outside git (it is bulk
evidence, not source) at ~/.local/share/caplab/cas.
"""

from __future__ import annotations

import hashlib
import os

DEFAULT_ROOT = os.path.expanduser("~/.local/share/caplab/cas")


def _path(sha256: str, root: str) -> str:
    return os.path.join(root, sha256[:2], sha256)


def retain(body: str, root: str | None = None) -> str:
    root = root or DEFAULT_ROOT
    data = body.encode()
    sha = hashlib.sha256(data).hexdigest()
    path = _path(sha, root)
    if not os.path.isfile(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    return sha


def load(sha256: str, root: str | None = None) -> str | None:
    root = root or DEFAULT_ROOT
    path = _path(sha256, root)
    if not os.path.isfile(path):
        return None
    data = open(path, "rb").read()
    if hashlib.sha256(data).hexdigest() != sha256:
        raise ValueError(f"CAS object {sha256[:16]}… fails its own hash — "
                         f"refusing to return tampered bytes")
    return data.decode()
