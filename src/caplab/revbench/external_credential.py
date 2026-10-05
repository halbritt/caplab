"""Private Revbench adapter around the external-token credential lease.

``caplab.codex_external_credential`` already owns the file read, identity checks,
sealed projection and exact-byte stream guards.  This module composes it with the
Revbench live runtime for the explicitly selected external-token profile:

* the expected source/account/subject hashes come from the separately supplied
  private anchors, never from the file being validated;
* the required access lifetime is derived from the retained execution deadline;
* the lease exposes only the descriptor and fresh stream guards that
  ``run_codex_process`` needs, and its descriptor stops being readable when the
  owning context closes.

The delivery API is imported when a lease is opened, not at module import:
that module imports ``caplab.revbench.codex`` at top level, so a reverse
top-level import here would create an initialization cycle.  Every refusal is a
fixed code; no source path, anchor, claim or exception text reaches a message.
"""

from __future__ import annotations

import contextlib
import math
import os
import re
import stat
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from .codex import (
    CODEX_EXTERNAL_CREDENTIAL_PROFILE_SCHEMA,
    CodexAdapterError,
    ExactSecretStreamQuarantine,
    validate_credential_profile,
)
from .custody import FilesystemLiveExecutionRuntime, LiveExecutionCustodyError

MAXIMUM_REQUIRED_LIFETIME_SECONDS = 86400
_TIMESTAMP = "%Y-%m-%dT%H:%M:%SZ"
_API_CODE = re.compile(r"credential_[a-z][a-z_]{0,63}")
_CUSTODY_CODE = re.compile(r"[a-z][a-z0-9_]{0,95}")


def required_access_lifetime_seconds(execution_deadline_at: str, now: datetime) -> int:
    """Whole seconds the access token must still cover, rounded up.

    The requirement runs from ``now`` to the retained execution deadline, which
    already bounds version probes and every native process.  Only a positive
    requirement below one second is raised to the delivery API's minimum of one;
    a deadline that has passed, or one the API's 86400-second maximum cannot
    cover, is refused rather than truncated.
    """

    try:
        deadline = datetime.strptime(execution_deadline_at, _TIMESTAMP).replace(
            tzinfo=UTC
        )
    except (TypeError, ValueError):
        raise CodexAdapterError("external_credential_deadline_invalid") from None
    if now.tzinfo is None:
        raise CodexAdapterError("external_credential_clock_invalid")
    remaining = (deadline - now).total_seconds()
    if remaining <= 0:
        raise CodexAdapterError("external_credential_deadline_elapsed")
    required = max(1, math.ceil(remaining))
    if required > MAXIMUM_REQUIRED_LIFETIME_SECONDS:
        raise CodexAdapterError("external_credential_lifetime_exceeds_maximum")
    return required


class ExternalRevbenchCredential:
    """One lease as ``run_codex_process`` sees it: descriptor plus fresh guards."""

    def __init__(self, lease: Any) -> None:
        self._lease = lease
        self._open = True

    @property
    def descriptor(self) -> int:
        if not self._open:
            raise CodexAdapterError("external_credential_lease_closed")
        return self._lease.descriptor

    def stream_quarantine(self) -> ExactSecretStreamQuarantine:
        """A fresh exact-byte gate; each durable stream needs its own."""

        if not self._open:
            raise CodexAdapterError("external_credential_lease_closed")
        return self._lease.quarantine_factory()

    def assert_streams_safe(self, stdout: bytes, stderr: bytes) -> None:
        """Refuse a retained stream that still contains guarded material."""

        if not isinstance(stdout, bytes) or not isinstance(stderr, bytes):
            raise CodexAdapterError("credential_quarantine_stream_not_bytes")
        for stream in (stdout, stderr):
            gate = self.stream_quarantine()
            gate.feed(stream)
            gate.finish()
            if gate.quarantined:
                raise CodexAdapterError("credential_secret_quarantine")

    def _close(self) -> None:
        self._open = False


def _api_refusal(error: Exception) -> CodexAdapterError:
    """Carry the delivery API's fixed code, and nothing else, across the boundary."""

    code = str(error)
    if _API_CODE.fullmatch(code):
        return CodexAdapterError(f"external_{code}")
    return CodexAdapterError("external_credential_input_invalid")


def _require_owned_root(root: Path, source: Path) -> int:
    """Open the credential root as the direct parent of the source; return its descriptor."""

    if not root.is_absolute() or not source.is_absolute() or source.parent != root:
        raise CodexAdapterError("credential_source_outside_configured_root")
    if source.name in {"", ".", ".."}:
        raise CodexAdapterError("credential_source_outside_configured_root")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        descriptor = os.open(root, flags)
    except OSError:
        raise CodexAdapterError("credential_root_open_failed") from None
    metadata = os.fstat(descriptor)
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or metadata.st_uid != os.geteuid()
        or stat.S_IMODE(metadata.st_mode) != 0o700
    ):
        os.close(descriptor)
        raise CodexAdapterError("credential_root_owner_or_mode_invalid")
    return descriptor


@contextlib.contextmanager
def open_external_revbench_credential(
    *,
    runtime: FilesystemLiveExecutionRuntime,
    profile: Mapping[str, Any],
    execution_deadline_at: str,
) -> Iterator[ExternalRevbenchCredential]:
    """Lease the sealed external-token projection for one fresh live slot.

    Call only after the overall one-shot intent is durable and before any
    version or provider-capable subprocess.  A refusal raises
    ``CodexAdapterError`` with a fixed code; the caller seals the same slot.
    """

    owned = validate_credential_profile(profile)
    if owned["schema_version"] != CODEX_EXTERNAL_CREDENTIAL_PROFILE_SCHEMA:
        raise CodexAdapterError("credential_profile_method_mismatch")
    # Imported here on purpose (see the module docstring).
    from caplab.codex_external_credential import (
        ExternalCredentialError,
        open_codex_external_credential,
    )

    try:
        anchors = runtime.credential_anchors(owned["profile_id"])
        source = Path(runtime.credential_source(owned["profile_id"]))
    except LiveExecutionCustodyError as error:
        code = str(error)
        raise CodexAdapterError(
            code if _CUSTODY_CODE.fullmatch(code) else "credential_runtime_refused"
        ) from None
    if runtime.credential_root is None:
        raise CodexAdapterError("credential_root_required")
    lifetime = required_access_lifetime_seconds(
        execution_deadline_at, datetime.now(UTC)
    )
    root_descriptor = _require_owned_root(Path(runtime.credential_root), source)
    try:
        with contextlib.ExitStack() as stack:
            try:
                lease = stack.enter_context(
                    open_codex_external_credential(
                        source,
                        expected_source_sha256=anchors["source_sha256"],
                        expected_account_sha256=anchors["account_sha256"],
                        expected_subject_sha256=anchors["subject_sha256"],
                        minimum_access_lifetime_seconds=lifetime,
                        quarantine_profile=owned["quarantine_profile"],
                    )
                )
            except ExternalCredentialError as error:
                raise _api_refusal(error) from None
            view = ExternalRevbenchCredential(lease)
            try:
                yield view
            finally:
                view._close()
    finally:
        os.close(root_descriptor)
