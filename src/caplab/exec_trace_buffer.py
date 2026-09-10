"""Withhold bounded strace hex output in an anonymous file until quarantine."""

from contextlib import contextmanager
import fcntl
import hashlib
import os
from pathlib import Path
import re
import stat

from caplab.capture_quarantine import check_capture_bytes, check_capture_document
from caplab.process_capture import _write_all
from caplab.task_capture_verify import _require, _read_file, _digest


_SEALS = (
    fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL
)


def _identity(info):
    return {"device": info.st_dev, "inode": info.st_ino}


def _check_trace(raw, factory):
    _require(
        raw and raw.endswith(b"\n"), "trace is empty or has an incomplete final line"
    )
    _require(raw.isascii(), "trace must use ASCII hex format")
    check_capture_bytes(factory, raw)
    position, count = 0, 0
    while True:
        start = raw.find(b'"', position)
        if start < 0:
            return count
        end = raw.find(b'"', start + 1)
        _require(end >= 0, "trace has an incomplete quoted string")
        encoded = raw[start + 1 : end]
        _require(
            re.fullmatch(rb"(?:\\x[0-9a-f]{2})*", encoded) is not None,
            "trace contains a non-hex quoted string",
        )
        _require(
            raw[end + 1 : end + 4] != b"...", "trace has an abbreviated quoted string"
        )
        decoded = bytes.fromhex(encoded.replace(b"\\x", b"").decode("ascii"))
        check_capture_bytes(factory, decoded)
        position, count = end + 1, count + 1


class ExecTraceBuffer:
    """Borrowed during buffered_exec_trace(); caller owns the bounded producer."""

    def __init__(self, descriptor, max_bytes, factory):
        self._descriptor = descriptor
        self._maximum = max_bytes
        self._factory = factory
        self._attempted = False

    @property
    def descriptor(self):
        _require(self._descriptor is not None, "trace buffer is closed")
        return self._descriptor

    @property
    def path(self):
        # The tracer opens the supervisor's descriptor; the workload inherits none.
        return Path(f"/proc/{os.getpid()}/fd/{self.descriptor}")

    @property
    def identity(self):
        info = os.fstat(self.descriptor)
        _require(
            stat.S_ISREG(info.st_mode) and info.st_nlink == 0,
            "trace buffer is not an anonymous regular file",
        )
        return _identity(info)

    def retain(self, path):
        """One publication attempt, after the caller has stopped all trace writers.

        Sealing makes the checked bytes immutable even if a stray descriptor
        survives. It does not establish successful execution or writer shutdown.
        The caller supplies a trusted stable private output parent. Refusal before
        publication writes no trace; I/O failure can leave a safe partial artifact.
        """
        _require(not self._attempted, "trace retention was already attempted")
        self._attempted = True
        path = Path(path)
        _require(
            path.is_absolute() and path.parent.resolve() == path.parent,
            "trace custody parent must be resolved",
        )
        parent = path.parent.stat()
        _require(
            parent.st_uid == os.getuid() and stat.S_IMODE(parent.st_mode) & 0o077 == 0,
            "trace custody parent must be private and owned",
        )
        check_capture_bytes(self._factory, os.fsencode(path))
        source = self.identity
        fcntl.fcntl(self.descriptor, fcntl.F_ADD_SEALS, _SEALS)
        size = os.fstat(self.descriptor).st_size
        _require(0 < size < self._maximum, "trace reached its byte limit or is empty")
        raw = os.pread(self.descriptor, size + 1, 0)
        _require(len(raw) == size, "sealed trace size differs")
        strings = _check_trace(raw, self._factory)
        receipt = {
            "schema": "caplab.exec-trace-retention/v1",
            "source_identity": source,
            "trace_sha256": hashlib.sha256(raw).hexdigest(),
            "trace_bytes": size,
            "max_trace_bytes": self._maximum,
            "decoded_strings": strings,
            "quarantine_applied": True,
            "source_seals": _SEALS,
        }
        check_capture_document(self._factory, receipt)
        fd = os.open(
            path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
            0o600,
        )
        try:
            _write_all(fd, raw)
            os.fsync(fd)
            receipt["retained_identity"] = _identity(os.fstat(fd))
        finally:
            os.close(fd)
        directory = os.open(
            path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        )
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        check_capture_document(self._factory, receipt)
        return receipt


@contextmanager
def buffered_exec_trace(*, max_bytes, quarantine_factory):
    """Own an anonymous trace descriptor; never execute a producer or read credentials.

    The caller bounds producer writes with RLIMIT_FSIZE and its process owner,
    excludes the buffer from untrusted namespaces, prevents swap/core retention,
    and stops writers before retain. Closing is not a memory-erasure guarantee.
    """
    _require(
        type(max_bytes) is int and 0 < max_bytes <= 32 * 1024**2,
        "invalid trace byte allowance",
    )
    _require(callable(quarantine_factory), "trace quarantine factory is required")
    descriptor = os.memfd_create(
        "caplab-exec-trace", os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING
    )
    buffer = ExecTraceBuffer(descriptor, max_bytes, quarantine_factory)
    try:
        yield buffer
    finally:
        os.close(descriptor)
        buffer._descriptor = None


def verify_trace_retention(receipt, path, *, expected_source_identity):
    """Verify an independently anchored retention link, not its origin or policy authority."""
    _require(
        isinstance(receipt, dict)
        and set(receipt)
        == {
            "schema",
            "source_identity",
            "retained_identity",
            "trace_sha256",
            "trace_bytes",
            "max_trace_bytes",
            "decoded_strings",
            "quarantine_applied",
            "source_seals",
        },
        "invalid trace retention fields",
    )
    _require(
        receipt["schema"] == "caplab.exec-trace-retention/v1"
        and receipt["quarantine_applied"] is True
        and type(receipt["source_seals"]) is int
        and receipt["source_seals"] == _SEALS,
        "trace retention lacks sealed quarantine",
    )
    for name in ("trace_bytes", "max_trace_bytes", "decoded_strings"):
        _require(
            type(receipt[name]) is int and receipt[name] >= 0,
            "invalid trace retention counts",
        )
    _require(
        0 < receipt["trace_bytes"] < receipt["max_trace_bytes"] <= 32 * 1024**2,
        "trace retention exceeded allowance",
    )
    for name in ("source_identity", "retained_identity"):
        identity = receipt[name]
        _require(
            isinstance(identity, dict)
            and set(identity) == {"device", "inode"}
            and type(identity["device"]) is int
            and identity["device"] >= 0
            and type(identity["inode"]) is int
            and identity["inode"] > 0,
            "invalid trace retention identity",
        )
    _require(
        receipt["source_identity"] == expected_source_identity,
        "trace retention source differs from observed tracer",
    )
    _digest(receipt["trace_sha256"])
    path = Path(path)
    _require(
        path.is_absolute() and path.parent.resolve() == path.parent,
        "retained trace parent must be resolved",
    )
    before = path.lstat()
    _require(
        stat.S_ISREG(before.st_mode)
        and _identity(before) == receipt["retained_identity"],
        "retained trace identity differs",
    )
    raw, size, digest = _read_file(None, path, receipt["max_trace_bytes"], retain=True)
    _require(
        size == receipt["trace_bytes"]
        and digest == receipt["trace_sha256"]
        and _identity(path.lstat()) == receipt["retained_identity"],
        "retained trace bytes or identity differ",
    )
    _require(
        _check_trace(raw, None) == receipt["decoded_strings"],
        "retained trace decoded-string count differs",
    )
    return dict(receipt)
