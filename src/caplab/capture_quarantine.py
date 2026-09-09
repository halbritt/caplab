"""Synchronous raw-byte checking through a trusted caller-owned stream policy."""

from contextlib import ExitStack, contextmanager
import hashlib
import json
from typing import Callable, Protocol


class StreamQuarantine(Protocol):
    """Trusted, bounded, per-stream policy supplied by the credential owner."""

    quarantined: bool

    def feed(self, payload: bytes) -> bytes: ...
    def finish(self) -> bytes: ...
    def abandon(self) -> None: ...


class CaptureQuarantineError(RuntimeError):
    """Guarded custody cannot publish a complete raw artifact."""


class _RawStream:
    def __init__(self, gate: StreamQuarantine):
        self.gate = gate
        self.received = self.emitted = 0
        self.input_digest = hashlib.sha256()
        self.output_digest = hashlib.sha256()

    def _emission(self, raw: bytes) -> bytes:
        if self.gate.quarantined is not False:
            raise CaptureQuarantineError("capture output quarantined")
        if not isinstance(raw, bytes) or len(raw) > self.received - self.emitted:
            raise CaptureQuarantineError("quarantine changed raw stream")
        self.emitted += len(raw)
        self.output_digest.update(raw)
        return raw

    def feed(self, raw: bytes) -> bytes:
        self.received += len(raw)
        self.input_digest.update(raw)
        return self._emission(self.gate.feed(raw))

    def finish(self) -> bytes:
        tail = self._emission(self.gate.finish())
        if (self.received != self.emitted
                or self.input_digest.digest() != self.output_digest.digest()):
            raise CaptureQuarantineError("quarantine changed raw stream")
        return tail


@contextmanager
def quarantine_stream(factory: Callable[[], StreamQuarantine] | None):
    """Own one fresh gate through cleanup; None preserves unguarded copying.

    Only the source owner may call finish, after observing EOF. Every exit
    abandons withheld bytes. Factory allocation failures remain factory-owned.
    """
    if factory is None:
        yield None
        return
    if not callable(factory):
        raise ValueError("quarantine_factory must be callable")
    with ExitStack() as cleanup:
        gate = factory()
        abandon = getattr(gate, "abandon", None)
        if callable(abandon):
            cleanup.callback(abandon)
        if (any(not callable(getattr(gate, method, None))
                for method in ("feed", "finish", "abandon"))
                or getattr(gate, "quarantined", None) is not False):
            raise ValueError("quarantine_factory must create a fresh stream gate")
        yield _RawStream(gate)


def check_capture_bytes(factory: Callable[[], StreamQuarantine] | None, raw: bytes) -> None:
    """Check already-bounded metadata without altering or retaining its bytes."""
    if factory is None:
        return
    with quarantine_stream(factory) as gate:
        for offset in range(0, len(raw), 65536):
            gate.feed(raw[offset:offset + 65536])
        gate.finish()


def check_capture_document(factory: Callable[[], StreamQuarantine] | None,
                           document: dict, raw: bytes | None = None) -> None:
    """Check JSON strings before escaping, then the exact serialized receipt."""
    if factory is None:
        return

    def strings(value):
        if isinstance(value, str):
            check_capture_bytes(factory, value.encode("utf-8", errors="surrogatepass"))
        elif isinstance(value, dict):
            for key, child in value.items():
                strings(key)
                strings(child)
        elif isinstance(value, list):
            for child in value:
                strings(child)

    strings(document)
    if raw is None:
        raw = (json.dumps(document, sort_keys=True) + "\n").encode("utf-8")
    check_capture_bytes(factory, raw)
