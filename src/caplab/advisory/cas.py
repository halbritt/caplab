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
import secrets

DEFAULT_ROOT = os.path.expanduser("~/.local/share/caplab/cas")


def _path(sha256: str, root: str) -> str:
    return os.path.join(root, sha256[:2], sha256)


def retain(body: str, root: str | None = None) -> str:
    root = root or DEFAULT_ROOT
    data = body.encode()
    sha = hashlib.sha256(data).hexdigest()
    path = _path(sha, root)
    if load(sha, root=root) == body:
        return sha
    parent = os.path.dirname(path)
    os.makedirs(parent, exist_ok=True)
    temporary = os.path.join(parent, f".{sha}-{secrets.token_hex(16)}")
    stream = open(temporary, "xb")
    try:
        with stream as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            pass  # A concurrent publisher must pass the same readback below.
        if load(sha, root=root) != body:
            raise ValueError("CAS retention readback differs from the supplied body")
        directory = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(temporary)
    return sha


def load(sha256: str, root: str | None = None) -> str | None:
    root = root or DEFAULT_ROOT
    path = _path(sha256, root)
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as stream:
        data = stream.read()
    if hashlib.sha256(data).hexdigest() != sha256:
        raise ValueError(f"CAS object {sha256[:16]}… fails its own hash — "
                         f"refusing to return tampered bytes")
    return data.decode()
