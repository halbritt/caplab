"""Crash-durable, globally one-shot custody for live Revbench processes.

The custody root is an at-most-once launch boundary, not a workflow engine and
not proof that a request reached a provider.  A live manifest is globally
one-shot inside one durable, non-rollback root.  Every process identity is the
digest of its exact launch plan, and every effect identity excludes execution
authorization: new permission cannot turn an uncertain attempt into a retry.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import secrets
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Self

from caplab.runtime.canonical import canonical_json, sha256_hex


class LiveExecutionCustodyError(ValueError):
    """Live custody could not establish or recover a trustworthy state."""


_AUTHORIZATION_ID = re.compile(r"^revbench-execution-auth-[0-9a-f]{64}$")
_BINDING_ID = re.compile(r"^bnd-[0-9a-f]{64}$")
_HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_EFFECT_ID = re.compile(r"^live-effect-[0-9a-f]{64}$")
_PROCESS_ID = re.compile(r"^process-[0-9a-f]{64}$")
_CUSTODY_DOMAIN_ID = re.compile(r"^custody-domain-[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_TIMESTAMP = "%Y-%m-%dT%H:%M:%SZ"
_PROCESS_KINDS = {"version-probe", "native-review"}
_COMPLETED_INVOCATIONS = {"not-invoked", "invoked"}
_TERMINATIONS = {
    "exited",
    "timeout",
    "stdout-limit",
    "stderr-limit",
    "spawn-failure",
    "authorization-expired",
    "preflight-refused",
    "privacy-quarantine",
}


@dataclass(frozen=True)
class RecoveredProcessCapture:
    """A completed or uncertain process capture that cannot be launched."""

    intent: dict[str, Any]
    stdout: bytes
    stderr: bytes
    invocation_state: str
    termination: str
    completion: dict[str, Any] | None
    recovery: dict[str, Any] | None


def live_effect_id(effect_scope: Mapping[str, Any]) -> str:
    """Return the authorization-independent identity of one live effect slot."""

    scope = _validate_effect_scope(effect_scope)
    return "live-effect-" + sha256_hex(canonical_json(scope))


def live_process_id(launch_plan: Mapping[str, Any]) -> str:
    """Return the identity of the exact process launch plan."""

    plan = _validate_launch_plan(launch_plan)
    return "process-" + sha256_hex(canonical_json(plan))


class FreshProcessCapture:
    """Preopened durable stream sinks for exactly one new process intent."""

    def __init__(
        self,
        root: Path,
        intent: Mapping[str, Any],
        stdout_descriptor: int,
        stderr_descriptor: int,
    ) -> None:
        self._root = root
        self.intent = _canonical_copy(intent)
        self._stdout_descriptor = stdout_descriptor
        self._stderr_descriptor = stderr_descriptor
        self._closed = False
        self._completed = False

    def write_stdout(self, payload: bytes) -> None:
        self._write(self._stdout_descriptor, payload)

    def write_stderr(self, payload: bytes) -> None:
        self._write(self._stderr_descriptor, payload)

    def _write(self, descriptor: int, payload: bytes) -> None:
        if self._closed or self._completed:
            raise LiveExecutionCustodyError("process_capture_closed")
        if not isinstance(payload, bytes):
            raise LiveExecutionCustodyError("process_stream_payload_not_bytes")
        view = memoryview(payload)
        written = 0
        try:
            while written < len(view):
                count = os.write(descriptor, view[written:])
                if count <= 0:
                    raise OSError("short process stream write")
                written += count
            os.fdatasync(descriptor)
        except OSError as error:
            raise LiveExecutionCustodyError("process_stream_sync_failed") from error

    def complete(self, completion: Mapping[str, Any]) -> RecoveredProcessCapture:
        if self._closed or self._completed:
            raise LiveExecutionCustodyError("process_capture_closed")
        document = _validate_completion(
            completion,
            self.intent["process_id"],
            self.intent.get("intent_recorded_at"),
        )
        try:
            os.fdatasync(self._stdout_descriptor)
            os.fdatasync(self._stderr_descriptor)
            stdout = _read_regular(self._root / "stdout", "process_stdout")
            stderr = _read_regular(self._root / "stderr", "process_stderr")
        except OSError as error:
            raise LiveExecutionCustodyError("process_stream_sync_failed") from error
        sealed = {
            **document,
            "stdout_sha256": sha256_hex(stdout),
            "stdout_byte_count": len(stdout),
            "stderr_sha256": sha256_hex(stderr),
            "stderr_byte_count": len(stderr),
        }
        if document["invocation_state"] == "not-invoked" and (stdout or stderr):
            raise LiveExecutionCustodyError("process_completion_invalid")
        _write_exclusive(self._root, "completion.json", canonical_json(sealed))
        self._completed = True
        self.close()
        return RecoveredProcessCapture(
            intent=self.intent,
            stdout=stdout,
            stderr=stderr,
            invocation_state=document["invocation_state"],
            termination=document["termination"],
            completion=sealed,
            recovery=None,
        )

    def close(self) -> None:
        if self._closed:
            return
        errors: list[OSError] = []
        for descriptor in (self._stdout_descriptor, self._stderr_descriptor):
            try:
                os.fdatasync(descriptor)
            except OSError as error:
                errors.append(error)
            try:
                os.close(descriptor)
            except OSError as error:
                errors.append(error)
        self._closed = True
        if errors:
            raise LiveExecutionCustodyError("process_stream_close_failed") from errors[
                0
            ]

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        self.close()


class LiveExecutionSession:
    """Exclusive access to one authorization's globally reserved manifest."""

    def __init__(
        self,
        custody_root: Path,
        root: Path,
        intent: Mapping[str, Any],
        lock_descriptor: int,
        sealed: Mapping[str, Any] | None,
        resumed: bool,
    ) -> None:
        self._custody_root = custody_root
        self.root = root
        self.intent = _canonical_copy(intent)
        self._lock_descriptor = lock_descriptor
        self._closed = False
        self.sealed = _canonical_copy(sealed) if sealed is not None else None
        self.resumed = resumed

    def claim_process(
        self, launch_plan: Mapping[str, Any]
    ) -> FreshProcessCapture | RecoveredProcessCapture:
        if self._closed:
            raise LiveExecutionCustodyError("live_execution_session_closed")
        if self.sealed is not None:
            raise LiveExecutionCustodyError("live_execution_sealed")
        plan = _validate_launch_plan(launch_plan)
        scope = plan["effect_scope"]
        for field in ("manifest_sha256", "experiment_id", "binding_id"):
            if scope[field] != self.intent[field]:
                raise LiveExecutionCustodyError("process_execution_identity_mismatch")
        if plan["execution_deadline_at"] != self.intent["execution_deadline_at"]:
            raise LiveExecutionCustodyError("process_execution_deadline_mismatch")
        effect_id = live_effect_id(scope)
        process_id = live_process_id(plan)
        declared = {"effect_id": effect_id, "process_id": process_id}
        sequence = self.intent["process_sequence"]
        declared_sequence = [
            {"effect_id": entry["effect_id"], "process_id": entry["process_id"]}
            for entry in sequence
        ]
        try:
            sequence_index = declared_sequence.index(declared)
        except ValueError as error:
            raise LiveExecutionCustodyError("process_not_declared") from error
        claimed = self._claimed_processes()
        if sequence_index > len(claimed):
            raise LiveExecutionCustodyError("process_claim_out_of_order")
        if sequence_index < len(claimed):
            if claimed[sequence_index] != declared:
                raise LiveExecutionCustodyError("process_claim_sequence_corrupt")
            return self._recover_declared_process(plan, effect_id, process_id)
        if sequence_index > 0:
            previous = sequence[sequence_index - 1]
            previous_root = self._custody_root / "effects" / previous["effect_id"]
            try:
                previous_intent = _read_canonical_document(
                    previous_root / "intent.json"
                )
            except FileNotFoundError as error:
                raise LiveExecutionCustodyError(
                    "prior_process_not_completed"
                ) from error
            try:
                _read_canonical_document(previous_root / "completion.json")
            except FileNotFoundError:
                raise LiveExecutionCustodyError("prior_process_not_completed")
            previous_capture = _recover_process(previous_root, previous_intent)
            if previous_capture.completion is None:
                raise LiveExecutionCustodyError("prior_process_not_completed")
        claim = {
            "schema_version": "caplab-revbench-live-effect-claim/1",
            "authorization_id": self.intent["authorization_id"],
            "manifest_sha256": self.intent["manifest_sha256"],
            "effect_id": effect_id,
            "process_id": process_id,
        }
        process_intent = {
            "schema_version": "caplab-revbench-live-process-intent/2",
            "authorization_id": self.intent["authorization_id"],
            "effect_id": effect_id,
            "process_id": process_id,
            "intent_recorded_at": _timestamp(),
            "launch_plan": plan,
        }
        global_lock = _locked_file(self._custody_root / ".global.lock")
        try:
            effect_intent_path = (
                self._custody_root / "effect-intents" / f"{effect_id}.json"
            )
            effect_intent = {
                "schema_version": "caplab-revbench-live-global-effect-intent/1",
                "claim": claim,
                "process_intent": process_intent,
            }
            try:
                retained_effect_intent = _read_canonical_document(effect_intent_path)
            except FileNotFoundError:
                if self.resumed:
                    raise LiveExecutionCustodyError(
                        "live_execution_recovery_cannot_launch"
                    )
                _write_exclusive(
                    self._custody_root / "effect-intents",
                    effect_intent_path.name,
                    canonical_json(effect_intent),
                )
                fresh_effect = True
            else:
                process_intent = _validate_global_effect_intent(
                    retained_effect_intent,
                    expected_claim=claim,
                    expected_plan=plan,
                )
                fresh_effect = False
            effects = self._custody_root / "effects"
            effect_root = effects / effect_id
            if fresh_effect and _mkdir_exclusive(effect_root):
                try:
                    _write_exclusive(effect_root, "claim.json", canonical_json(claim))
                    _write_exclusive(
                        effect_root, "intent.json", canonical_json(process_intent)
                    )
                    stdout_descriptor = _open_stream_exclusive(effect_root, "stdout")
                    try:
                        stderr_descriptor = _open_stream_exclusive(
                            effect_root, "stderr"
                        )
                    except Exception:
                        os.close(stdout_descriptor)
                        raise
                    _fsync_directory(effect_root)
                    _write_exclusive(
                        effect_root,
                        "ready.json",
                        canonical_json(
                            {
                                "schema_version": "caplab-revbench-live-effect-ready/1",
                                "process_id": process_id,
                            }
                        ),
                    )
                    capture: FreshProcessCapture | RecoveredProcessCapture = (
                        FreshProcessCapture(
                            effect_root,
                            process_intent,
                            stdout_descriptor,
                            stderr_descriptor,
                        )
                    )
                except Exception as error:
                    raise LiveExecutionCustodyError(
                        "live_effect_intent_publish_failed"
                    ) from error
            else:
                capture = _recover_effect_root(
                    effect_root,
                    claim=claim,
                    process_intent=process_intent,
                )
            claims = self.root / "claims"
            try:
                _write_exclusive(
                    claims,
                    f"{sequence_index:08d}.json",
                    canonical_json(declared),
                )
            except Exception:
                if isinstance(capture, FreshProcessCapture):
                    capture.close()
                raise
        finally:
            _unlock_close(global_lock)
        return capture

    def _recover_declared_process(
        self, plan: dict[str, Any], effect_id: str, process_id: str
    ) -> RecoveredProcessCapture:
        root = self._custody_root / "effects" / effect_id
        _require_owned_directory(root, "live_effect_root")
        expected = {
            "schema_version": "caplab-revbench-live-process-intent/2",
            "authorization_id": self.intent["authorization_id"],
            "effect_id": effect_id,
            "process_id": process_id,
        }
        try:
            retained = _read_canonical_document(root / "intent.json")
        except FileNotFoundError:
            return _uncertain_capture(
                root,
                {
                    **expected,
                    "intent_recorded_at": self.intent["intent_recorded_at"],
                    "launch_plan": plan,
                },
            )
        if set(retained) != {*expected, "intent_recorded_at", "launch_plan"}:
            raise LiveExecutionCustodyError("process_intent_shape_invalid")
        for field, value in expected.items():
            if retained[field] != value:
                raise LiveExecutionCustodyError("process_intent_identity_conflict")
        if retained["launch_plan"] != plan:
            raise LiveExecutionCustodyError("process_intent_identity_conflict")
        _parse_timestamp(
            retained["intent_recorded_at"], "process_intent_timestamp_invalid"
        )
        return _recover_process(root, retained)

    def _claimed_processes(self) -> list[dict[str, str]]:
        claims = self.root / "claims"
        _require_owned_directory(claims, "live_execution_claims")
        retained: list[dict[str, str]] = []
        for index, sequence_entry in enumerate(self.intent["process_sequence"]):
            expected = {
                "effect_id": sequence_entry["effect_id"],
                "process_id": sequence_entry["process_id"],
            }
            path = claims / f"{index:08d}.json"
            try:
                document = _read_canonical_document(path)
            except FileNotFoundError:
                if any(claims.glob(f"{index + 1:08d}.json")):
                    raise LiveExecutionCustodyError("process_claim_sequence_corrupt")
                break
            if document != expected:
                raise LiveExecutionCustodyError("process_claim_sequence_corrupt")
            retained.append(document)
        allowed = {f"{index:08d}.json" for index in range(len(retained))}
        actual = {path.name for path in claims.iterdir()}
        if actual != allowed:
            raise LiveExecutionCustodyError("process_claim_sequence_corrupt")
        return retained

    def declared_launch_plans(self) -> list[dict[str, Any]]:
        """Return the exact retained sequence used for recovery-only replay."""

        if self._closed:
            raise LiveExecutionCustodyError("live_execution_session_closed")
        return [
            _canonical_copy(entry["launch_plan"])
            for entry in self.intent["process_sequence"]
        ]

    def finalization_recorded_at(self) -> str:
        """Persist one stable evidence-finalization time after claimed effects settle."""

        if self._closed:
            raise LiveExecutionCustodyError("live_execution_session_closed")
        latest = _parse_timestamp(
            self.intent["intent_recorded_at"],
            "live_execution_finalization_timestamp_invalid",
        )
        for declared in self._claimed_processes():
            effect_root = self._custody_root / "effects" / declared["effect_id"]
            try:
                completion = _read_canonical_document(effect_root / "completion.json")
            except FileNotFoundError:
                try:
                    recovery = _read_canonical_document(effect_root / "recovery.json")
                except FileNotFoundError as error:
                    raise LiveExecutionCustodyError(
                        "live_execution_finalization_requires_terminal_claims"
                    ) from error
                candidate = _parse_timestamp(
                    recovery.get("recovered_at"),
                    "live_execution_finalization_timestamp_invalid",
                )
            else:
                candidate = _parse_timestamp(
                    completion.get("completion_recorded_at"),
                    "live_execution_finalization_timestamp_invalid",
                )
            latest = max(latest, candidate)
        path = self.root / "finalization.json"
        try:
            retained = _read_canonical_document(path)
        except FileNotFoundError:
            recorded_at = max(
                latest,
                _parse_timestamp(
                    _timestamp(), "live_execution_finalization_timestamp_invalid"
                ),
            ).strftime(_TIMESTAMP)
            retained = {
                "schema_version": "caplab-revbench-live-finalization/1",
                "finalization_recorded_at": recorded_at,
            }
            _write_exclusive(self.root, path.name, canonical_json(retained))
        if (
            set(retained) != {"schema_version", "finalization_recorded_at"}
            or retained["schema_version"] != "caplab-revbench-live-finalization/1"
        ):
            raise LiveExecutionCustodyError("live_execution_finalization_invalid")
        recorded = _parse_timestamp(
            retained["finalization_recorded_at"],
            "live_execution_finalization_timestamp_invalid",
        )
        if recorded < latest:
            raise LiveExecutionCustodyError("live_execution_finalization_invalid")
        return retained["finalization_recorded_at"]

    def seal(self, reviews: Mapping[str, Any]) -> None:
        if self._closed:
            raise LiveExecutionCustodyError("live_execution_session_closed")
        document = _canonical_copy(reviews)
        path = self.root / "sealed-execution.json"
        try:
            retained = _read_canonical_document(path)
        except FileNotFoundError:
            _write_exclusive(self.root, path.name, canonical_json(document))
            self.sealed = document
            return
        if retained != document:
            raise LiveExecutionCustodyError("live_execution_seal_conflict")
        self.sealed = retained

    def close(self) -> None:
        if self._closed:
            return
        _unlock_close(self._lock_descriptor)
        self._closed = True

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        self.close()


class FilesystemLiveExecutionRuntime:
    """Filesystem capability for live custody and out-of-evidence credentials."""

    def __init__(
        self,
        ledger_root: Path,
        *,
        credential_root: Path | None = None,
        credential_sources: Mapping[str, str | Path] | None = None,
    ) -> None:
        parent = Path(ledger_root)
        if not parent.is_absolute():
            raise LiveExecutionCustodyError("live_custody_root_must_be_absolute")
        _require_secure_parent_directory(parent, "live_custody_parent")
        custody_location = parent.resolve(strict=True)
        package_location = Path(__file__).resolve().parents[1]
        protected_locations = [package_location]
        repository_location = next(
            (
                candidate
                for candidate in Path(__file__).resolve().parents
                if (candidate / ".git").exists()
            ),
            None,
        )
        if repository_location is not None:
            protected_locations.append(repository_location)
        if any(
            _paths_overlap(custody_location, protected)
            for protected in protected_locations
        ):
            raise LiveExecutionCustodyError(
                "live_custody_root_must_be_disjoint_from_package"
            )
        self.root = _ensure_owned_directory(parent, "revbench-live-effects")
        for name in ("authorizations", "effect-intents", "effects", "manifests"):
            _ensure_owned_directory(self.root, name)
        descriptor = _open_lock(self.root / ".global.lock")
        os.close(descriptor)
        global_lock = _locked_file(self.root / ".global.lock")
        try:
            self._custody_domain_id = _load_or_create_custody_domain(self.root)
        finally:
            _unlock_close(global_lock)
        sources = credential_sources or {}
        if sources and credential_root is None:
            raise LiveExecutionCustodyError("credential_root_required")
        self.credential_root = (
            None if credential_root is None else Path(credential_root)
        )
        if self.credential_root is not None:
            if not self.credential_root.is_absolute():
                raise LiveExecutionCustodyError("credential_root_must_be_absolute")
            _require_owned_directory(self.credential_root, "credential_root")
            credential_location = self.credential_root.resolve(strict=True)
            custody_location = self.root.resolve(strict=True)
            evidence_location = parent.resolve(strict=True)
            package_location = Path(__file__).resolve().parents[1]
            protected_locations = [
                custody_location,
                evidence_location,
                package_location,
            ]
            repository_location = next(
                (
                    candidate
                    for candidate in Path(__file__).resolve().parents
                    if (candidate / ".git").exists()
                ),
                None,
            )
            if repository_location is not None:
                protected_locations.append(repository_location)
            if any(
                _paths_overlap(credential_location, protected)
                for protected in protected_locations
            ):
                raise LiveExecutionCustodyError(
                    "credential_root_must_be_disjoint_from_evidence_and_package"
                )
        retained_sources: dict[str, str] = {}
        for profile, source in sources.items():
            if not isinstance(profile, str) or _IDENTIFIER.fullmatch(profile) is None:
                raise LiveExecutionCustodyError("credential_profile_id_invalid")
            source_name = os.fspath(source)
            candidate = Path(source_name)
            if (
                not source_name
                or candidate.is_absolute()
                or candidate.parent != Path(".")
                or candidate.name in {"", ".", ".."}
            ):
                raise LiveExecutionCustodyError("credential_source_name_invalid")
            retained_sources[profile] = candidate.name
        self._credential_sources = retained_sources

    @property
    def custody_domain_id(self) -> str:
        """Return the durable nonsecret identity of this non-rollback root."""

        retained = _read_custody_domain(self.root)
        if retained["custody_domain_id"] != self._custody_domain_id:
            raise LiveExecutionCustodyError("live_custody_domain_changed")
        return self._custody_domain_id

    def credential_source(self, profile_id: str) -> Path:
        """Return a caller-provisioned source path without registering it."""

        if not isinstance(profile_id, str) or _IDENTIFIER.fullmatch(profile_id) is None:
            raise LiveExecutionCustodyError("credential_profile_id_invalid")
        try:
            source_name = self._credential_sources[profile_id]
        except KeyError as error:
            raise LiveExecutionCustodyError(
                "credential_profile_not_provisioned"
            ) from error
        if self.credential_root is None:
            raise LiveExecutionCustodyError("credential_root_required")
        return self.credential_root / source_name

    def claim_execution(self, intent: Mapping[str, Any]) -> LiveExecutionSession:
        """Compatibility wrapper for a fresh claim or exact retained resume."""

        owned = _validate_execution_intent(intent)
        if owned["custody_domain_id"] != self.custody_domain_id:
            raise LiveExecutionCustodyError("live_custody_domain_mismatch")
        identity = {
            "schema_version": "caplab-revbench-live-execution-identity/1",
            **{
                field: owned[field]
                for field in (
                    "authorization_id",
                    "manifest_sha256",
                    "experiment_id",
                    "binding_id",
                    "custody_domain_id",
                )
            },
        }
        return self.claim_or_resume_execution(identity, fresh_intent=owned)

    def retained_execution_intent(
        self, identity: Mapping[str, Any]
    ) -> dict[str, Any] | None:
        """Return a retained intent without arming or recovering any process."""

        owned_identity = _validate_execution_identity(identity)
        if owned_identity["custody_domain_id"] != self.custody_domain_id:
            raise LiveExecutionCustodyError("live_custody_domain_mismatch")
        global_lock = _locked_file(self.root / ".global.lock")
        try:
            manifest_path = (
                self.root / "manifests" / f"{owned_identity['manifest_sha256']}.json"
            )
            try:
                retained_claim = _read_canonical_document(manifest_path)
            except FileNotFoundError:
                return None
            retained = _validate_manifest_claim(retained_claim)
            for field in (
                "authorization_id",
                "manifest_sha256",
                "experiment_id",
                "binding_id",
                "custody_domain_id",
            ):
                if retained[field] != owned_identity[field]:
                    if field == "authorization_id":
                        raise LiveExecutionCustodyError("manifest_already_claimed")
                    raise LiveExecutionCustodyError("live_execution_identity_mismatch")
            _recover_execution_root(self.root, retained)
            return retained
        finally:
            _unlock_close(global_lock)

    def claim_or_resume_execution(
        self,
        identity: Mapping[str, Any],
        *,
        fresh_intent: Mapping[str, Any] | None = None,
    ) -> LiveExecutionSession:
        """Claim once, or resume using retained times and process sequence."""

        owned_identity = _validate_execution_identity(identity)
        if owned_identity["custody_domain_id"] != self.custody_domain_id:
            raise LiveExecutionCustodyError("live_custody_domain_mismatch")
        authorization_id = owned_identity["authorization_id"]
        global_lock = _locked_file(self.root / ".global.lock")
        try:
            manifest_path = (
                self.root / "manifests" / f"{owned_identity['manifest_sha256']}.json"
            )
            try:
                retained_claim = _read_canonical_document(manifest_path)
            except FileNotFoundError:
                if fresh_intent is None:
                    raise LiveExecutionCustodyError(
                        "live_execution_fresh_intent_required"
                    )
                owned = _validate_execution_intent(fresh_intent)
                for field in (
                    "authorization_id",
                    "manifest_sha256",
                    "experiment_id",
                    "binding_id",
                    "custody_domain_id",
                ):
                    if owned[field] != owned_identity[field]:
                        if field == "authorization_id":
                            raise LiveExecutionCustodyError("manifest_already_claimed")
                        raise LiveExecutionCustodyError(
                            "live_execution_identity_mismatch"
                        )
                execution_digest = sha256_hex(canonical_json(owned))
                manifest_claim = {
                    "schema_version": "caplab-revbench-live-manifest-claim/1",
                    "manifest_sha256": owned["manifest_sha256"],
                    "authorization_id": authorization_id,
                    "execution_intent_sha256": execution_digest,
                    "execution_intent": owned,
                }
                _write_exclusive(
                    self.root / "manifests",
                    manifest_path.name,
                    canonical_json(manifest_claim),
                )
                execution_root = _recover_execution_root(self.root, owned)
                created = True
            else:
                owned = _validate_manifest_claim(retained_claim)
                for field in (
                    "authorization_id",
                    "manifest_sha256",
                    "experiment_id",
                    "binding_id",
                    "custody_domain_id",
                ):
                    if owned[field] != owned_identity[field]:
                        if field == "authorization_id":
                            raise LiveExecutionCustodyError("manifest_already_claimed")
                        raise LiveExecutionCustodyError(
                            "live_execution_identity_mismatch"
                        )
                execution_root = _recover_execution_root(self.root, owned)
                created = False
        finally:
            _unlock_close(global_lock)

        lock_descriptor = _open_lock(execution_root / ".lock")
        try:
            fcntl.flock(lock_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            os.close(lock_descriptor)
            raise LiveExecutionCustodyError("live_execution_in_progress") from error
        try:
            try:
                sealed = _read_canonical_document(
                    execution_root / "sealed-execution.json"
                )
            except FileNotFoundError:
                sealed = None
            return LiveExecutionSession(
                self.root,
                execution_root,
                owned,
                lock_descriptor,
                sealed,
                resumed=not created,
            )
        except Exception:
            _unlock_close(lock_descriptor)
            raise

    def sealed_execution(self, authorization_id: str) -> dict[str, Any] | None:
        if (
            not isinstance(authorization_id, str)
            or _AUTHORIZATION_ID.fullmatch(authorization_id) is None
        ):
            raise LiveExecutionCustodyError("live_execution_authorization_id_invalid")
        path = self.root / "authorizations" / authorization_id / "sealed-execution.json"
        try:
            return _read_canonical_document(path)
        except FileNotFoundError:
            return None


def _validate_effect_scope(scope: Mapping[str, Any]) -> dict[str, Any]:
    owned = _canonical_copy(scope)
    expected = {
        "schema_version",
        "manifest_sha256",
        "experiment_id",
        "binding_id",
        "case_id",
        "arm",
        "assignment_index",
        "process_kind",
    }
    if set(owned) != expected:
        raise LiveExecutionCustodyError("live_effect_scope_shape_invalid")
    if owned["schema_version"] != "caplab-revbench-live-effect-scope/1":
        raise LiveExecutionCustodyError("live_effect_scope_schema_invalid")
    _digest(owned["manifest_sha256"], "live_effect_manifest_digest_invalid")
    _identifier(owned["experiment_id"], "live_effect_experiment_id_invalid")
    if (
        not isinstance(owned["binding_id"], str)
        or _BINDING_ID.fullmatch(owned["binding_id"]) is None
    ):
        raise LiveExecutionCustodyError("live_effect_binding_id_invalid")
    _identifier(owned["case_id"], "live_effect_case_id_invalid")
    if owned["arm"] not in {"control", "mutant"}:
        raise LiveExecutionCustodyError("live_effect_arm_invalid")
    if (
        isinstance(owned["assignment_index"], bool)
        or not isinstance(owned["assignment_index"], int)
        or owned["assignment_index"] < 0
    ):
        raise LiveExecutionCustodyError("live_effect_assignment_index_invalid")
    if owned["process_kind"] not in _PROCESS_KINDS:
        raise LiveExecutionCustodyError("live_effect_process_kind_invalid")
    return owned


def _validate_launch_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    owned = _canonical_copy(plan)
    expected = {
        "schema_version",
        "effect_scope",
        "argv_sha256",
        "containment_argv_sha256",
        "stdin_sha256",
        "environment_sha256",
        "runtime_bundle_sha256",
        "apparatus_sha256",
        "command_sha256",
        "credential_profile_id",
        "credential_profile_sha256",
        "timeout_seconds",
        "execution_deadline_at",
        "stdout_limit",
        "stderr_limit",
    }
    if set(owned) != expected:
        raise LiveExecutionCustodyError("launch_plan_shape_invalid")
    if owned["schema_version"] != "caplab-revbench-live-launch-plan/1":
        raise LiveExecutionCustodyError("launch_plan_schema_invalid")
    owned["effect_scope"] = _validate_effect_scope(owned["effect_scope"])
    for field in (
        "argv_sha256",
        "containment_argv_sha256",
        "stdin_sha256",
        "environment_sha256",
        "runtime_bundle_sha256",
        "apparatus_sha256",
        "command_sha256",
        "credential_profile_sha256",
    ):
        _digest(owned[field], f"launch_plan_{field}_invalid")
    _identifier(
        owned["credential_profile_id"], "launch_plan_credential_profile_invalid"
    )
    for field in ("timeout_seconds", "stdout_limit", "stderr_limit"):
        if (
            isinstance(owned[field], bool)
            or not isinstance(owned[field], int)
            or owned[field] <= 0
        ):
            raise LiveExecutionCustodyError(f"launch_plan_{field}_invalid")
    _parse_timestamp(
        owned["execution_deadline_at"], "launch_plan_execution_deadline_invalid"
    )
    return owned


def _validate_execution_intent(intent: Mapping[str, Any]) -> dict[str, Any]:
    owned = _canonical_copy(intent)
    if set(owned) != {
        "schema_version",
        "authorization_id",
        "manifest_sha256",
        "experiment_id",
        "binding_id",
        "custody_domain_id",
        "apparatus_ref",
        "intent_recorded_at",
        "execution_deadline_at",
        "process_sequence",
    }:
        raise LiveExecutionCustodyError("live_execution_intent_shape_invalid")
    if owned["schema_version"] != "caplab-revbench-live-execution-intent/1":
        raise LiveExecutionCustodyError("live_execution_intent_schema_invalid")
    authorization_id = owned["authorization_id"]
    if (
        not isinstance(authorization_id, str)
        or _AUTHORIZATION_ID.fullmatch(authorization_id) is None
    ):
        raise LiveExecutionCustodyError("live_execution_authorization_id_invalid")
    _digest(owned["manifest_sha256"], "live_execution_manifest_digest_invalid")
    _identifier(owned["experiment_id"], "live_execution_experiment_id_invalid")
    if (
        not isinstance(owned["binding_id"], str)
        or _BINDING_ID.fullmatch(owned["binding_id"]) is None
    ):
        raise LiveExecutionCustodyError("live_execution_binding_id_invalid")
    if (
        not isinstance(owned["custody_domain_id"], str)
        or _CUSTODY_DOMAIN_ID.fullmatch(owned["custody_domain_id"]) is None
    ):
        raise LiveExecutionCustodyError("live_custody_domain_id_invalid")
    owned["apparatus_ref"] = _validate_apparatus_ref(owned["apparatus_ref"])
    recorded_at = _parse_timestamp(
        owned["intent_recorded_at"], "live_execution_intent_timestamp_invalid"
    )
    deadline_at = _parse_timestamp(
        owned["execution_deadline_at"], "live_execution_deadline_invalid"
    )
    if deadline_at <= recorded_at:
        raise LiveExecutionCustodyError("live_execution_deadline_invalid")
    sequence = owned["process_sequence"]
    if not isinstance(sequence, list) or not sequence:
        raise LiveExecutionCustodyError("live_execution_process_sequence_invalid")
    retained: list[dict[str, Any]] = []
    for entry in sequence:
        if not isinstance(entry, dict) or set(entry) != {
            "effect_id",
            "process_id",
            "launch_plan",
        }:
            raise LiveExecutionCustodyError("live_execution_process_sequence_invalid")
        if (
            not isinstance(entry["effect_id"], str)
            or _EFFECT_ID.fullmatch(entry["effect_id"]) is None
        ):
            raise LiveExecutionCustodyError("live_execution_effect_id_invalid")
        if (
            not isinstance(entry["process_id"], str)
            or _PROCESS_ID.fullmatch(entry["process_id"]) is None
        ):
            raise LiveExecutionCustodyError("live_execution_process_id_invalid")
        plan = _validate_launch_plan(entry["launch_plan"])
        if live_effect_id(plan["effect_scope"]) != entry["effect_id"]:
            raise LiveExecutionCustodyError("live_execution_effect_id_invalid")
        if live_process_id(plan) != entry["process_id"]:
            raise LiveExecutionCustodyError("live_execution_process_id_invalid")
        retained.append({**dict(entry), "launch_plan": plan})
    if len({entry["effect_id"] for entry in retained}) != len(retained):
        raise LiveExecutionCustodyError("live_execution_process_sequence_duplicate")
    return owned


def _validate_manifest_claim(claim: Mapping[str, Any]) -> dict[str, Any]:
    owned = _canonical_copy(claim)
    if (
        set(owned)
        != {
            "schema_version",
            "manifest_sha256",
            "authorization_id",
            "execution_intent_sha256",
            "execution_intent",
        }
        or owned["schema_version"] != "caplab-revbench-live-manifest-claim/1"
    ):
        raise LiveExecutionCustodyError("manifest_already_claimed")
    intent = _validate_execution_intent(owned["execution_intent"])
    if (
        owned["manifest_sha256"] != intent["manifest_sha256"]
        or owned["authorization_id"] != intent["authorization_id"]
        or owned["execution_intent_sha256"] != sha256_hex(canonical_json(intent))
    ):
        raise LiveExecutionCustodyError("live_execution_intent_digest_mismatch")
    return intent


def _recover_execution_root(custody_root: Path, intent: Mapping[str, Any]) -> Path:
    """Materialize idempotent session state from the durable manifest claim."""

    owned = _validate_execution_intent(intent)
    execution_root = custody_root / "authorizations" / owned["authorization_id"]
    if not _mkdir_exclusive(execution_root):
        _require_owned_directory(execution_root, "live_execution_authorization")
    try:
        retained = _validate_execution_intent(
            _read_canonical_document(execution_root / "intent.json")
        )
    except FileNotFoundError:
        _write_exclusive(execution_root, "intent.json", canonical_json(owned))
    else:
        if canonical_json(retained) != canonical_json(owned):
            raise LiveExecutionCustodyError(
                "live_execution_authorization_reuse_conflict"
            )
    _ensure_owned_directory(execution_root, "claims")
    return execution_root


def _validate_global_effect_intent(
    value: Mapping[str, Any],
    *,
    expected_claim: Mapping[str, Any],
    expected_plan: Mapping[str, Any],
) -> dict[str, Any]:
    owned = _canonical_copy(value)
    if (
        set(owned) != {"schema_version", "claim", "process_intent"}
        or owned["schema_version"] != "caplab-revbench-live-global-effect-intent/1"
    ):
        raise LiveExecutionCustodyError("live_effect_intent_invalid")
    if canonical_json(owned["claim"]) != canonical_json(expected_claim):
        raise LiveExecutionCustodyError("live_effect_already_claimed")
    process_intent = owned["process_intent"]
    if not isinstance(process_intent, dict) or set(process_intent) != {
        "schema_version",
        "authorization_id",
        "effect_id",
        "process_id",
        "intent_recorded_at",
        "launch_plan",
    }:
        raise LiveExecutionCustodyError("live_effect_intent_invalid")
    if (
        process_intent["schema_version"] != "caplab-revbench-live-process-intent/2"
        or process_intent["authorization_id"] != expected_claim["authorization_id"]
        or process_intent["effect_id"] != expected_claim["effect_id"]
        or process_intent["process_id"] != expected_claim["process_id"]
        or canonical_json(process_intent["launch_plan"])
        != canonical_json(expected_plan)
    ):
        raise LiveExecutionCustodyError("live_effect_intent_invalid")
    _parse_timestamp(
        process_intent["intent_recorded_at"], "process_intent_timestamp_invalid"
    )
    return process_intent


def _recover_effect_root(
    effect_root: Path,
    *,
    claim: Mapping[str, Any],
    process_intent: Mapping[str, Any],
) -> RecoveredProcessCapture:
    """Repair prelaunch publication gaps, then seal the effect uncertain."""

    created = _mkdir_exclusive(effect_root)
    if not created:
        _require_owned_directory(effect_root, "live_effect_root")
    ready_path = effect_root / "ready.json"
    try:
        ready = _read_canonical_document(ready_path)
    except FileNotFoundError:
        ready = None
    expected_ready = {
        "schema_version": "caplab-revbench-live-effect-ready/1",
        "process_id": process_intent["process_id"],
    }
    if ready is not None and canonical_json(ready) != canonical_json(expected_ready):
        raise LiveExecutionCustodyError("live_effect_ready_invalid")
    for name, document in (
        ("claim.json", claim),
        ("intent.json", process_intent),
    ):
        try:
            retained = _read_canonical_document(effect_root / name)
        except FileNotFoundError:
            if ready is not None:
                raise LiveExecutionCustodyError("live_effect_custody_incomplete")
            _write_exclusive(effect_root, name, canonical_json(document))
        else:
            if canonical_json(retained) != canonical_json(document):
                raise LiveExecutionCustodyError("live_effect_already_claimed")
    for name in ("stdout", "stderr"):
        path = effect_root / name
        try:
            _read_regular(path, "live_process_stream")
        except FileNotFoundError:
            if ready is not None:
                raise LiveExecutionCustodyError("live_effect_custody_incomplete")
            descriptor = _open_stream_exclusive(effect_root, name)
            os.close(descriptor)
    _fsync_directory(effect_root)
    if ready is None:
        _write_exclusive(effect_root, "ready.json", canonical_json(expected_ready))
    return _recover_process(effect_root, dict(process_intent))


def _validate_execution_identity(identity: Mapping[str, Any]) -> dict[str, Any]:
    owned = _canonical_copy(identity)
    if set(owned) != {
        "schema_version",
        "authorization_id",
        "manifest_sha256",
        "experiment_id",
        "binding_id",
        "custody_domain_id",
    }:
        raise LiveExecutionCustodyError("live_execution_identity_shape_invalid")
    if owned["schema_version"] != "caplab-revbench-live-execution-identity/1":
        raise LiveExecutionCustodyError("live_execution_identity_schema_invalid")
    if (
        not isinstance(owned["authorization_id"], str)
        or _AUTHORIZATION_ID.fullmatch(owned["authorization_id"]) is None
    ):
        raise LiveExecutionCustodyError("live_execution_authorization_id_invalid")
    _digest(owned["manifest_sha256"], "live_execution_manifest_digest_invalid")
    _identifier(owned["experiment_id"], "live_execution_experiment_id_invalid")
    if (
        not isinstance(owned["binding_id"], str)
        or _BINDING_ID.fullmatch(owned["binding_id"]) is None
    ):
        raise LiveExecutionCustodyError("live_execution_binding_id_invalid")
    if (
        not isinstance(owned["custody_domain_id"], str)
        or _CUSTODY_DOMAIN_ID.fullmatch(owned["custody_domain_id"]) is None
    ):
        raise LiveExecutionCustodyError("live_custody_domain_id_invalid")
    return owned


def _load_or_create_custody_domain(root: Path) -> str:
    """Create one durable root capability identity, or validate the retained one."""

    try:
        return _read_custody_domain(root)["custody_domain_id"]
    except FileNotFoundError:
        identity = {
            "schema_version": "caplab-revbench-live-custody-domain/1",
            "nonce": secrets.token_hex(32),
        }
        document = {
            **identity,
            "custody_domain_id": "custody-domain-"
            + sha256_hex(canonical_json(identity)),
        }
        try:
            _write_exclusive(root, "custody-domain.json", canonical_json(document))
        except LiveExecutionCustodyError as error:
            if "record_exists" not in str(error):
                raise
        return _read_custody_domain(root)["custody_domain_id"]


def _read_custody_domain(root: Path) -> dict[str, str]:
    document = _read_canonical_document(root / "custody-domain.json")
    if (
        not isinstance(document, dict)
        or set(document) != {"schema_version", "nonce", "custody_domain_id"}
        or document["schema_version"] != "caplab-revbench-live-custody-domain/1"
        or not isinstance(document["nonce"], str)
        or _HEX_DIGEST.fullmatch(document["nonce"]) is None
        or not isinstance(document["custody_domain_id"], str)
        or _CUSTODY_DOMAIN_ID.fullmatch(document["custody_domain_id"]) is None
    ):
        raise LiveExecutionCustodyError("live_custody_domain_invalid")
    identity = {
        "schema_version": document["schema_version"],
        "nonce": document["nonce"],
    }
    expected = "custody-domain-" + sha256_hex(canonical_json(identity))
    if document["custody_domain_id"] != expected:
        raise LiveExecutionCustodyError("live_custody_domain_invalid")
    return document


def _validate_apparatus_ref(value: Mapping[str, Any]) -> dict[str, Any]:
    owned = _canonical_copy(value)
    if set(owned) != {
        "kind",
        "schema",
        "media_type",
        "sha256",
        "byte_count",
        "locator",
        "registration_ref",
        "custody",
    }:
        raise LiveExecutionCustodyError("live_execution_apparatus_ref_invalid")
    if (
        owned["kind"] != "execution-apparatus-receipt"
        or owned["schema"] != "caplab-revbench-execution-apparatus/1"
        or owned["media_type"] != "application/json"
        or owned["custody"] is not None
    ):
        raise LiveExecutionCustodyError("live_execution_apparatus_ref_invalid")
    _digest(owned["sha256"], "live_execution_apparatus_ref_invalid")
    if (
        isinstance(owned["byte_count"], bool)
        or not isinstance(owned["byte_count"], int)
        or owned["byte_count"] <= 0
        or owned["locator"] != f"objects/sha256/{owned['sha256'][:2]}/{owned['sha256']}"
        or not isinstance(owned["registration_ref"], str)
        or not owned["registration_ref"]
    ):
        raise LiveExecutionCustodyError("live_execution_apparatus_ref_invalid")
    return owned


def _validate_completion(
    completion: Mapping[str, Any],
    process_id: str,
    intent_recorded_at: str | None = None,
) -> dict[str, Any]:
    document = _canonical_copy(completion)
    required = {
        "schema_version",
        "process_id",
        "launch_attempted_at",
        "process_started_at",
        "process_completed_at",
        "completion_recorded_at",
        "stdout_complete",
        "stderr_complete",
        "exit_code",
        "termination",
        "invocation_state",
    }
    if set(document) != required:
        raise LiveExecutionCustodyError("process_completion_shape_invalid")
    if document["schema_version"] != "caplab-revbench-live-process-completion/1":
        raise LiveExecutionCustodyError("process_completion_schema_invalid")
    if document["process_id"] != process_id:
        raise LiveExecutionCustodyError("process_completion_identity_mismatch")
    recorded = _parse_timestamp(
        document["completion_recorded_at"], "process_completion_invalid"
    )
    intent_time = (
        _parse_timestamp(intent_recorded_at, "process_completion_invalid")
        if intent_recorded_at is not None
        else None
    )
    temporal: dict[str, datetime | None] = {}
    for field in ("launch_attempted_at", "process_started_at", "process_completed_at"):
        value = document[field]
        temporal[field] = (
            None
            if value is None
            else _parse_timestamp(value, "process_completion_invalid")
        )
    launch = temporal["launch_attempted_at"]
    started = temporal["process_started_at"]
    completed = temporal["process_completed_at"]
    if not isinstance(document["stdout_complete"], bool) or not isinstance(
        document["stderr_complete"], bool
    ):
        raise LiveExecutionCustodyError("process_completion_invalid")
    exit_code = document["exit_code"]
    if exit_code is not None and (
        isinstance(exit_code, bool) or not isinstance(exit_code, int)
    ):
        raise LiveExecutionCustodyError("process_completion_invalid")
    if document["termination"] not in _TERMINATIONS:
        raise LiveExecutionCustodyError("process_completion_invalid")
    if document["invocation_state"] not in _COMPLETED_INVOCATIONS:
        raise LiveExecutionCustodyError("process_completion_invalid")
    if document["invocation_state"] == "not-invoked" and document[
        "termination"
    ] not in {"spawn-failure", "preflight-refused", "authorization-expired"}:
        raise LiveExecutionCustodyError("process_completion_invalid")
    if document["invocation_state"] == "not-invoked" and (
        exit_code is not None
        or not document["stdout_complete"]
        or not document["stderr_complete"]
    ):
        raise LiveExecutionCustodyError("process_completion_invalid")
    if document["invocation_state"] == "not-invoked":
        if started is not None or completed is not None:
            raise LiveExecutionCustodyError("process_completion_invalid")
        if document["termination"] == "spawn-failure" and launch is None:
            raise LiveExecutionCustodyError("process_completion_invalid")
        if document["termination"] != "spawn-failure" and launch is not None:
            raise LiveExecutionCustodyError("process_completion_invalid")
        if launch is not None and not ((intent_time or launch) <= launch <= recorded):
            raise LiveExecutionCustodyError("process_completion_invalid")
    if document["invocation_state"] == "invoked" and document["termination"] in {
        "spawn-failure",
        "preflight-refused",
    }:
        raise LiveExecutionCustodyError("process_completion_invalid")
    if document["invocation_state"] == "invoked":
        if launch is None or started is None or completed is None:
            raise LiveExecutionCustodyError("process_completion_invalid")
        if not (launch <= started <= completed <= recorded):
            raise LiveExecutionCustodyError("process_completion_invalid")
    elif recorded < (intent_time or recorded):
        raise LiveExecutionCustodyError("process_completion_invalid")
    if intent_time is not None and launch is not None and launch < intent_time:
        raise LiveExecutionCustodyError("process_completion_invalid")
    if document["termination"] == "stdout-limit" and document["stdout_complete"]:
        raise LiveExecutionCustodyError("process_completion_invalid")
    if document["termination"] == "stderr-limit" and document["stderr_complete"]:
        raise LiveExecutionCustodyError("process_completion_invalid")
    return document


def _recover_process(root: Path, intent: dict[str, Any]) -> RecoveredProcessCapture:
    try:
        completion = _read_canonical_document(root / "completion.json")
    except FileNotFoundError:
        return _recover_uncertain(root, intent)
    try:
        _read_canonical_document(root / "recovery.json")
    except FileNotFoundError:
        pass
    else:
        raise LiveExecutionCustodyError("process_completion_recovery_conflict")
    # A completion can make empty streams trustworthy only when both actual
    # stream files still exist.  Missing files are custody loss, not empty data.
    stdout = _read_regular(root / "stdout", "process_stdout")
    stderr = _read_regular(root / "stderr", "process_stderr")
    expected = {
        "schema_version",
        "process_id",
        "launch_attempted_at",
        "process_started_at",
        "process_completed_at",
        "completion_recorded_at",
        "stdout_complete",
        "stderr_complete",
        "exit_code",
        "termination",
        "invocation_state",
        "stdout_sha256",
        "stdout_byte_count",
        "stderr_sha256",
        "stderr_byte_count",
    }
    if set(completion) != expected:
        raise LiveExecutionCustodyError("process_completion_shape_invalid")
    base = {
        key: completion[key]
        for key in expected
        if key
        not in {
            "stdout_sha256",
            "stdout_byte_count",
            "stderr_sha256",
            "stderr_byte_count",
        }
    }
    _validate_completion(base, intent["process_id"], intent.get("intent_recorded_at"))
    if (
        completion["stdout_sha256"] != sha256_hex(stdout)
        or completion["stdout_byte_count"] != len(stdout)
        or completion["stderr_sha256"] != sha256_hex(stderr)
        or completion["stderr_byte_count"] != len(stderr)
    ):
        raise LiveExecutionCustodyError("process_completion_stream_mismatch")
    return RecoveredProcessCapture(
        intent=intent,
        stdout=stdout,
        stderr=stderr,
        invocation_state=completion["invocation_state"],
        termination=completion["termination"],
        completion=completion,
        recovery=None,
    )


def _uncertain_capture(root: Path, intent: dict[str, Any]) -> RecoveredProcessCapture:
    return _recover_uncertain(root, intent)


def _recover_uncertain(root: Path, intent: dict[str, Any]) -> RecoveredProcessCapture:
    stdout = _read_optional_regular(root / "stdout", "process_stdout", synchronize=True)
    stderr = _read_optional_regular(root / "stderr", "process_stderr", synchronize=True)
    identity = {
        "schema_version": "caplab-revbench-live-process-recovery/1",
        "process_id": intent["process_id"],
        "intent_recorded_at": intent.get("intent_recorded_at"),
        "process_started_at": None,
        "process_completed_at": None,
        "invocation_state": "uncertain",
        "termination": "executor-interrupted",
        "stdout_sha256": sha256_hex(stdout),
        "stdout_byte_count": len(stdout),
        "stderr_sha256": sha256_hex(stderr),
        "stderr_byte_count": len(stderr),
    }
    recovery_path = root / "recovery.json"
    try:
        recovery = _read_canonical_document(recovery_path)
    except FileNotFoundError:
        recovery = {**identity, "recovered_at": _timestamp()}
        _write_exclusive(root, recovery_path.name, canonical_json(recovery))
    else:
        if set(recovery) != {*identity, "recovered_at"}:
            raise LiveExecutionCustodyError("process_recovery_shape_invalid")
        for field, expected in identity.items():
            if recovery[field] != expected:
                raise LiveExecutionCustodyError("process_recovery_identity_mismatch")
        _parse_timestamp(recovery["recovered_at"], "process_recovery_timestamp_invalid")
    return RecoveredProcessCapture(
        intent=intent,
        stdout=stdout,
        stderr=stderr,
        invocation_state="uncertain",
        termination="executor-interrupted",
        completion=None,
        recovery=recovery,
    )


def _canonical_copy(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise LiveExecutionCustodyError("live_custody_document_not_object")
    try:
        copied = json.loads(canonical_json(value))
    except (TypeError, ValueError) as error:
        raise LiveExecutionCustodyError("live_custody_document_invalid") from error
    if not isinstance(copied, dict):
        raise LiveExecutionCustodyError("live_custody_document_not_object")
    return copied


def _digest(value: Any, error: str) -> None:
    if not isinstance(value, str) or _HEX_DIGEST.fullmatch(value) is None:
        raise LiveExecutionCustodyError(error)


def _identifier(value: Any, error: str) -> None:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise LiveExecutionCustodyError(error)


def _timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).strftime(_TIMESTAMP)


def _parse_timestamp(value: Any, error: str) -> datetime:
    if not isinstance(value, str):
        raise LiveExecutionCustodyError(error)
    try:
        return datetime.strptime(value, _TIMESTAMP).replace(tzinfo=UTC)
    except ValueError as cause:
        raise LiveExecutionCustodyError(error) from cause


def _require_directory(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise LiveExecutionCustodyError(f"{label}_unavailable") from error
    if not stat.S_ISDIR(metadata.st_mode):
        raise LiveExecutionCustodyError(f"{label}_not_real_directory")


def _require_secure_parent_directory(path: Path, label: str) -> None:
    _require_directory(path, label)
    metadata = path.lstat()
    if metadata.st_uid != os.geteuid() or stat.S_IMODE(metadata.st_mode) & 0o022:
        raise LiveExecutionCustodyError(f"{label}_ownership_or_mode_invalid")


def _paths_overlap(left: Path, right: Path) -> bool:
    left = left.resolve(strict=True)
    right = right.resolve(strict=True)
    return left == right or left in right.parents or right in left.parents


def _require_owned_directory(path: Path, label: str) -> None:
    _require_directory(path, label)
    metadata = path.lstat()
    if metadata.st_uid != os.geteuid() or stat.S_IMODE(metadata.st_mode) != 0o700:
        raise LiveExecutionCustodyError(f"{label}_ownership_or_mode_invalid")


def _ensure_owned_directory(parent: Path, name: str) -> Path:
    _require_secure_parent_directory(parent, "live_custody_parent")
    child = parent / name
    try:
        child.mkdir(mode=0o700)
    except FileExistsError:
        pass
    except OSError as error:
        raise LiveExecutionCustodyError(
            f"live_custody_directory_create_failed:{name}"
        ) from error
    _require_owned_directory(child, "live_custody_directory")
    _fsync_directory(child)
    _fsync_directory(parent)
    return child


def _mkdir_exclusive(path: Path) -> bool:
    try:
        path.mkdir(mode=0o700)
        _fsync_directory(path)
        _fsync_directory(path.parent)
        return True
    except FileExistsError:
        _require_owned_directory(path, "live_custody_directory")
        # An earlier creator may have observed its mkdir before the parent
        # directory fsync failed.  Re-establish durability before trusting the
        # tombstone as an at-most-once boundary.
        _fsync_directory(path)
        _fsync_directory(path.parent)
        return False
    except OSError as error:
        raise LiveExecutionCustodyError(
            "live_custody_directory_create_failed"
        ) from error


def _directory_descriptor(path: Path) -> int:
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    return os.open(path, flags)


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = _directory_descriptor(path)
    except OSError as error:
        raise LiveExecutionCustodyError("live_custody_directory_sync_failed") from error
    try:
        try:
            os.fsync(descriptor)
        except OSError as error:
            raise LiveExecutionCustodyError(
                "live_custody_directory_sync_failed"
            ) from error
    finally:
        os.close(descriptor)


def _open_lock(path: Path) -> int:
    flags = os.O_CREAT | os.O_RDWR | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o600)
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_uid != os.geteuid()
            or stat.S_IMODE(metadata.st_mode) != 0o600
        ):
            raise LiveExecutionCustodyError("live_execution_lock_invalid")
        os.fsync(descriptor)
        _fsync_directory(path.parent)
        return descriptor
    except OSError as error:
        raise LiveExecutionCustodyError("live_execution_lock_open_failed") from error


def _locked_file(path: Path) -> int:
    descriptor = _open_lock(path)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
    except OSError:
        os.close(descriptor)
        raise
    return descriptor


def _unlock_close(descriptor: int) -> None:
    try:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def _open_stream_exclusive(root: Path, name: str) -> int:
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_APPEND | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(root / name, flags, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        metadata = os.fstat(descriptor)
        if metadata.st_uid != os.geteuid() or stat.S_IMODE(metadata.st_mode) != 0o600:
            raise LiveExecutionCustodyError("process_stream_mode_invalid")
        os.fsync(descriptor)
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _write_exclusive(root: Path, name: str, payload: bytes) -> None:
    temporary = f".{name}.{secrets.token_hex(16)}"
    directory = _directory_descriptor(root)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(temporary, flags, 0o600, dir_fd=directory)
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(
            temporary,
            name,
            src_dir_fd=directory,
            dst_dir_fd=directory,
            follow_symlinks=False,
        )
        os.fsync(directory)
    except FileExistsError as error:
        raise LiveExecutionCustodyError(f"live_custody_record_exists:{name}") from error
    except OSError as error:
        raise LiveExecutionCustodyError(
            f"live_custody_record_publish_failed:{name}"
        ) from error
    finally:
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass
        except OSError as error:
            raise LiveExecutionCustodyError(
                f"live_custody_record_cleanup_failed:{name}"
            ) from error
        finally:
            try:
                os.fsync(directory)
            except OSError as error:
                raise LiveExecutionCustodyError(
                    f"live_custody_record_cleanup_sync_failed:{name}"
                ) from error
            finally:
                os.close(directory)


def _read_optional_regular(
    path: Path, label: str, *, synchronize: bool = False
) -> bytes:
    try:
        return _read_regular(path, label, synchronize=synchronize)
    except FileNotFoundError:
        return b""


def _read_regular(path: Path, label: str, *, synchronize: bool = False) -> bytes:
    flags = (os.O_RDWR if synchronize else os.O_RDONLY) | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        raise
    except OSError as error:
        raise LiveExecutionCustodyError(f"{label}_open_failed") from error
    with os.fdopen(descriptor, "rb", closefd=True) as stream:
        metadata = os.fstat(stream.fileno())
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_uid != os.geteuid()
            or stat.S_IMODE(metadata.st_mode) != 0o600
        ):
            raise LiveExecutionCustodyError(f"{label}_ownership_or_mode_invalid")
        if synchronize:
            try:
                os.fdatasync(stream.fileno())
            except OSError as error:
                raise LiveExecutionCustodyError("process_stream_sync_failed") from error
        return stream.read()


def _read_canonical_document(path: Path) -> dict[str, Any]:
    payload = _read_regular(path, "live_custody_record")
    try:
        document = json.loads(payload)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise LiveExecutionCustodyError("live_custody_record_invalid_json") from error
    if not isinstance(document, dict) or canonical_json(document) != payload:
        raise LiveExecutionCustodyError("live_custody_record_not_canonical")
    # A previous publication may have linked the final name and then failed its
    # directory fsync.  Retry/recovery must sync the visible entry before it can
    # authorize recovery or a subsequent process launch.
    _fsync_directory(path.parent)
    return document
