"""Durable, append-only custody for qualification records."""

from __future__ import annotations

import fcntl
import json
import os
import re
import secrets
import stat
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from threading import local
from typing import Any

from caplab.runtime.canonical import canonical_json, sha256_hex

_CONTENT_REF_KEYS = {
    "kind",
    "schema",
    "media_type",
    "sha256",
    "byte_count",
    "locator",
    "registration_ref",
    "custody",
}
_REGISTRATION_KEYS = _CONTENT_REF_KEYS | {"schema_version"}
_HEX = frozenset("0123456789abcdef")
_CUSTODY_KEYS = {"repository", "commit", "path", "source_sha256"}
_CUSTODY_PATH = re.compile(r"^[A-Za-z0-9._/-]+$")


class QualificationLedgerError(ValueError):
    """The qualification ledger refused unsafe or inconsistent state."""


class FilesystemQualificationLedger:
    """Own one content-addressed object namespace and append-only record streams."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        if not self.root.is_absolute():
            raise QualificationLedgerError("ledger_root_must_be_absolute")
        self._lock_state = local()
        self._prepare_root()

    def _prepare_root(self) -> None:
        if not self.root.parent.is_dir() or self.root.parent.is_symlink():
            raise QualificationLedgerError("ledger_parent_must_be_real_directory")
        try:
            self.root.mkdir(mode=0o750)
            _fsync_directory(self.root.parent)
        except FileExistsError:
            pass
        except OSError as error:
            raise QualificationLedgerError("ledger_root_create_failed") from error
        _require_real_directory(self.root, "ledger_root")

    @contextmanager
    def _locked(self, *, exclusive: bool) -> Iterator[None]:
        depth = getattr(self._lock_state, "depth", 0)
        if depth:
            if exclusive and not self._lock_state.exclusive:
                raise QualificationLedgerError("ledger_lock_upgrade_refused")
            self._lock_state.depth = depth + 1
            try:
                yield
            finally:
                self._lock_state.depth -= 1
            return
        _require_real_directory(self.root, "ledger_root")
        path = self.root / ".qualification.lock"
        created = not path.exists()
        flags = os.O_CREAT | os.O_RDWR | os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(path, flags, 0o600)
        except OSError as error:
            raise QualificationLedgerError("ledger_lock_open_failed") from error
        try:
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode):
                raise QualificationLedgerError("ledger_lock_not_regular")
            if created:
                os.fsync(descriptor)
                _fsync_directory(self.root)
            fcntl.flock(
                descriptor,
                fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH,
            )
            self._lock_state.depth = 1
            self._lock_state.exclusive = exclusive
            try:
                yield
            finally:
                self._lock_state.depth = 0
                self._lock_state.exclusive = False
        finally:
            os.close(descriptor)

    def register_document(
        self,
        document: Mapping[str, Any],
        *,
        kind: str,
        schema: str,
        media_type: str = "application/json",
        custody: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not isinstance(document, Mapping):
            raise QualificationLedgerError("registration_document_not_object")
        if media_type != "application/json":
            raise QualificationLedgerError(
                "document_media_type_must_be_application_json"
            )
        payload = canonical_json(document)
        return self._register_bytes(
            payload,
            kind=kind,
            schema=schema,
            media_type=media_type,
            custody=custody,
        )

    def register_bytes(
        self,
        payload: bytes,
        *,
        kind: str,
        schema: str,
        media_type: str = "application/octet-stream",
        custody: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Register exact non-JSON evidence bytes without an encoding rewrite."""

        if not isinstance(payload, bytes):
            raise QualificationLedgerError("registration_payload_not_bytes")
        if media_type == "application/json":
            raise QualificationLedgerError("json_bytes_must_use_register_document")
        return self._register_bytes(
            payload,
            kind=kind,
            schema=schema,
            media_type=media_type,
            custody=custody,
        )

    def _register_bytes(
        self,
        payload: bytes,
        *,
        kind: str,
        schema: str,
        media_type: str,
        custody: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        if not all(
            isinstance(field, str) and field for field in (kind, schema, media_type)
        ):
            raise QualificationLedgerError("registration_metadata_invalid")
        _validate_custody(custody)
        if custody is not None:
            raise QualificationLedgerError(
                "historical_custody_registration_requires_admission_path"
            )
        digest = sha256_hex(payload)
        locator = f"objects/sha256/{digest[:2]}/{digest}"
        body: dict[str, Any] = {
            "schema_version": "caplab-qualification-registration/1",
            "kind": kind,
            "schema": schema,
            "media_type": media_type,
            "sha256": digest,
            "byte_count": len(payload),
            "locator": locator,
            "custody": custody,
        }
        registration_ref = f"registration:{sha256_hex(canonical_json(body))}"
        registration = {**body, "registration_ref": registration_ref}
        public_ref = {key: registration[key] for key in _CONTENT_REF_KEYS}
        with self._locked(exclusive=True):
            registrations = self._load_registrations_locked()
            existing = registrations.get(registration_ref)
            if existing is not None:
                if canonical_json(existing) != canonical_json(registration):
                    raise QualificationLedgerError("registration_identity_conflict")
                self._verify_object_locked(public_ref)
                return json.loads(canonical_json(public_ref))
            self._write_object_locked(locator, payload)
            self._append_line_locked("registrations.jsonl", registration)
            self._verify_object_locked(public_ref)
        return json.loads(canonical_json(public_ref))

    def resolve(self, ref: Mapping[str, Any]) -> bytes:
        owned_ref = json.loads(canonical_json(ref))
        _validate_content_ref(owned_ref)
        with self._locked(exclusive=False):
            registration = self._load_registrations_locked().get(
                owned_ref["registration_ref"]
            )
            if registration is None:
                raise QualificationLedgerError("registration_missing")
            retained_ref = {key: registration[key] for key in _CONTENT_REF_KEYS}
            if canonical_json(retained_ref) != canonical_json(owned_ref):
                raise QualificationLedgerError("registration_reference_mismatch")
            return self._verify_object_locked(owned_ref)

    def append_measurement(
        self,
        measurement: Mapping[str, Any],
        *,
        validator: Callable[[Mapping[str, Any], Any], dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if validator is None:
            from .core import validate_measurement

            validator = validate_measurement
        return self._append_record(
            "measurements.jsonl",
            "measurement_id",
            "measurement",
            measurement,
            validator,
        )

    def append_policy(
        self,
        policy: Mapping[str, Any],
        *,
        validator: Callable[[Mapping[str, Any], Any], dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if validator is None:
            from .core import validate_policy

            validator = validate_policy
        return self._append_record(
            "policies.jsonl",
            "policy_id",
            "policy",
            policy,
            validator,
            series_validator=_validate_policy_series,
        )

    def append_claim(
        self,
        claim: Mapping[str, Any],
        *,
        validator: Callable[[Mapping[str, Any], Any], dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if validator is None:
            from .core import validate_claim

            validator = validate_claim
        validated = validator(claim, self)
        if not isinstance(validated, dict):
            raise QualificationLedgerError("claim_validator_not_object")
        claim_id = validated.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            raise QualificationLedgerError("claim_id_invalid")
        with self._locked(exclusive=True):
            claims = self._load_validated_records_locked(
                "claims.jsonl",
                "claim_id",
                "claim",
                validator,
            )
            _validate_claim_graph(claims)
            existing = claims.get(claim_id)
            if existing is not None:
                if canonical_json(existing) != canonical_json(validated):
                    existing_basis = {
                        key: value
                        for key, value in existing.items()
                        if key != "generated_at"
                    }
                    replay_basis = {
                        key: value
                        for key, value in validated.items()
                        if key != "generated_at"
                    }
                    if canonical_json(existing_basis) != canonical_json(replay_basis):
                        raise QualificationLedgerError(
                            f"claim_identity_conflict:{claim_id}"
                        )
                return json.loads(canonical_json(existing))
            _validate_new_claim_edges(validated, claims)
            combined = {**claims, claim_id: validated}
            _validate_claim_graph(combined)
            self._append_line_locked("claims.jsonl", validated)
        return json.loads(canonical_json(validated))

    def history(
        self,
        binding_id: str,
        capability: Mapping[str, Any],
        *,
        validator: Callable[[Mapping[str, Any], Any], dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if validator is None:
            from .core import validate_claim

            validator = validate_claim
        owned_capability = json.loads(canonical_json(capability))
        if not isinstance(binding_id, str) or not binding_id:
            raise QualificationLedgerError("history_binding_id_invalid")
        if not isinstance(owned_capability, dict):
            raise QualificationLedgerError("history_capability_invalid")
        with self._locked(exclusive=False):
            claims_by_id = self._load_validated_records_locked(
                "claims.jsonl",
                "claim_id",
                "claim",
                validator,
            )
            _validate_claim_graph(claims_by_id)
        selected = [
            claim
            for claim in claims_by_id.values()
            if _claim_binding_id(claim) == binding_id
            and canonical_json(_claim_capability(claim))
            == canonical_json(owned_capability)
        ]
        selected.sort(key=lambda claim: claim["claim_id"])
        superseded = {
            prior_id for claim in selected for prior_id in claim["supersedes"]
        }
        heads = sorted(
            claim["claim_id"]
            for claim in selected
            if claim["claim_id"] not in superseded
        )
        return {
            "schema_version": "caplab-qualification-history/1",
            "binding_id": binding_id,
            "capability": owned_capability,
            "claims": json.loads(canonical_json(selected)),
            "head_claim_ids": heads,
            "ambiguous": len(heads) > 1,
        }

    def resolve_capability(
        self,
        binding_id: str,
        name: str,
        version: str,
        *,
        validator: Callable[[Mapping[str, Any], Any], dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Resolve CLI shorthand only when it names one exact capability."""
        if validator is None:
            from .core import validate_claim

            validator = validate_claim
        if not all(
            isinstance(value, str) and value for value in (binding_id, name, version)
        ):
            raise QualificationLedgerError("capability_selector_invalid")
        with self._locked(exclusive=False):
            claims_by_id = self._load_validated_records_locked(
                "claims.jsonl",
                "claim_id",
                "claim",
                validator,
            )
            _validate_claim_graph(claims_by_id)
        candidates: dict[bytes, dict[str, Any]] = {}
        for claim in claims_by_id.values():
            capability = _claim_capability(claim)
            if (
                _claim_binding_id(claim) == binding_id
                and capability.get("name") == name
                and capability.get("version") == version
            ):
                encoded = canonical_json(capability)
                candidates[encoded] = json.loads(encoded)
        if not candidates:
            raise QualificationLedgerError("capability_series_not_found")
        if len(candidates) != 1:
            raise QualificationLedgerError("capability_selector_ambiguous")
        return next(iter(candidates.values()))

    def _append_record(
        self,
        filename: str,
        id_field: str,
        record_kind: str,
        document: Mapping[str, Any],
        validator: Callable[[Mapping[str, Any], Any], dict[str, Any]],
        series_validator: Callable[
            [Mapping[str, Any], Mapping[str, Mapping[str, Any]]], None
        ]
        | None = None,
    ) -> dict[str, Any]:
        validated = validator(document, self)
        if not isinstance(validated, dict):
            raise QualificationLedgerError(f"{record_kind}_validator_not_object")
        record_id = validated.get(id_field)
        if not isinstance(record_id, str) or not record_id:
            raise QualificationLedgerError(f"{record_kind}_id_invalid")
        with self._locked(exclusive=True):
            existing_records = self._load_validated_records_locked(
                filename,
                id_field,
                record_kind,
                validator,
            )
            if series_validator is not None:
                series_validator(validated, existing_records)
            existing = existing_records.get(record_id)
            if existing is not None:
                if canonical_json(existing) != canonical_json(validated):
                    raise QualificationLedgerError(
                        f"{record_kind}_identity_conflict:{record_id}"
                    )
                return json.loads(canonical_json(existing))
            self._append_line_locked(filename, validated)
        return json.loads(canonical_json(validated))

    def _load_validated_records_locked(
        self,
        filename: str,
        id_field: str,
        record_kind: str,
        validator: Callable[[Mapping[str, Any], Any], dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        retained: dict[str, dict[str, Any]] = {}
        for line_number, record in enumerate(
            self._read_stream_locked(filename), start=1
        ):
            validated = validator(record, self)
            if not isinstance(validated, dict):
                raise QualificationLedgerError(
                    f"{record_kind}_validator_not_object:{line_number}"
                )
            if canonical_json(validated) != canonical_json(record):
                raise QualificationLedgerError(
                    f"{record_kind}_retained_form_invalid:{line_number}"
                )
            record_id = record.get(id_field)
            if not isinstance(record_id, str) or not record_id:
                raise QualificationLedgerError(
                    f"{record_kind}_id_invalid:{line_number}"
                )
            if record_id in retained:
                raise QualificationLedgerError(
                    f"duplicate_{record_kind}_id:{line_number}:{record_id}"
                )
            retained[record_id] = record
        return retained

    def _load_registrations_locked(self) -> dict[str, dict[str, Any]]:
        records = self._read_stream_locked("registrations.jsonl")
        registrations: dict[str, dict[str, Any]] = {}
        for line_number, record in enumerate(records, start=1):
            _validate_registration(record, line_number)
            registration_ref = record["registration_ref"]
            if registration_ref in registrations:
                raise QualificationLedgerError(
                    f"duplicate_registration_ref:{line_number}:{registration_ref}"
                )
            public_ref = {key: record[key] for key in _CONTENT_REF_KEYS}
            self._verify_object_locked(public_ref)
            registrations[registration_ref] = record
        return registrations

    def _read_stream_locked(self, filename: str) -> list[dict[str, Any]]:
        path = self.root / filename
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            return []
        if not stat.S_ISREG(metadata.st_mode):
            raise QualificationLedgerError(f"ledger_stream_not_regular:{filename}")
        flags = os.O_RDONLY | os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(path, flags)
        except OSError as error:
            raise QualificationLedgerError(
                f"ledger_stream_open_failed:{filename}"
            ) from error
        with os.fdopen(descriptor, "rb", closefd=True) as stream:
            payload = stream.read()
        if payload and not payload.endswith(b"\n"):
            raise QualificationLedgerError(f"ledger_stream_truncated:{filename}")
        records: list[dict[str, Any]] = []
        for line_number, line in enumerate(payload.splitlines(), start=1):
            if not line.strip():
                raise QualificationLedgerError(
                    f"blank_ledger_line:{filename}:{line_number}"
                )
            try:
                record = json.loads(line)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise QualificationLedgerError(
                    f"invalid_ledger_json:{filename}:{line_number}"
                ) from error
            if not isinstance(record, dict):
                raise QualificationLedgerError(
                    f"ledger_record_not_object:{filename}:{line_number}"
                )
            if canonical_json(record) != line:
                raise QualificationLedgerError(
                    f"noncanonical_ledger_record:{filename}:{line_number}"
                )
            records.append(record)
        return records

    def _append_line_locked(self, filename: str, document: Mapping[str, Any]) -> None:
        path = self.root / filename
        created = not path.exists()
        flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY | os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(path, flags, 0o600)
        except OSError as error:
            raise QualificationLedgerError(
                f"ledger_stream_append_failed:{filename}"
            ) from error
        with os.fdopen(descriptor, "ab", closefd=True) as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise QualificationLedgerError(f"ledger_stream_not_regular:{filename}")
            stream.write(canonical_json(document) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
        if created:
            _fsync_directory(self.root)

    def _write_object_locked(self, locator: str, payload: bytes) -> None:
        parts = locator.split("/")
        parent = self.root
        for component in parts[:-1]:
            parent = _ensure_child_directory(parent, component)
        path = parent / parts[-1]
        if path.exists() or path.is_symlink():
            if _read_regular_file(path, "registered_object") != payload:
                raise QualificationLedgerError("registered_object_conflict")
            return
        temporary = parent / f".qualification-{secrets.token_hex(16)}"
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_CLOEXEC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            descriptor = os.open(temporary, flags, 0o440)
            with os.fdopen(descriptor, "wb", closefd=True) as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, path, follow_symlinks=False)
            except FileExistsError:
                if _read_regular_file(path, "registered_object") != payload:
                    raise QualificationLedgerError("registered_object_conflict")
            _fsync_directory(parent)
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass

    def _verify_object_locked(self, ref: Mapping[str, Any]) -> bytes:
        expected_locator = f"objects/sha256/{ref['sha256'][:2]}/{ref['sha256']}"
        if ref["locator"] != expected_locator:
            raise QualificationLedgerError("content_locator_mismatch")
        parts = expected_locator.split("/")
        parent = self.root
        for component in parts[:-1]:
            parent = parent / component
            _require_real_directory(parent, "object_directory")
        path = parent / parts[-1]
        payload = _read_regular_file(path, "registered_object")
        if len(payload) != ref["byte_count"]:
            raise QualificationLedgerError("content_byte_count_mismatch")
        if sha256_hex(payload) != ref["sha256"]:
            raise QualificationLedgerError("content_sha256_mismatch")
        return payload


def _validate_content_ref(ref: Any) -> None:
    if not isinstance(ref, dict) or set(ref) != _CONTENT_REF_KEYS:
        raise QualificationLedgerError("content_ref_shape_invalid")
    digest = ref.get("sha256")
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in _HEX for character in digest)
    ):
        raise QualificationLedgerError("content_ref_sha256_invalid")
    if (
        not isinstance(ref.get("byte_count"), int)
        or isinstance(ref["byte_count"], bool)
        or ref["byte_count"] < 0
    ):
        raise QualificationLedgerError("content_ref_byte_count_invalid")
    for field in ("kind", "schema", "media_type", "locator", "registration_ref"):
        if not isinstance(ref.get(field), str) or not ref[field]:
            raise QualificationLedgerError(f"content_ref_{field}_invalid")
    _validate_custody(ref.get("custody"))


def _validate_custody(custody: Any) -> None:
    if custody is None:
        return
    if not isinstance(custody, Mapping) or set(custody) != _CUSTODY_KEYS:
        raise QualificationLedgerError("content_ref_custody_invalid")
    repository = custody.get("repository")
    commit = custody.get("commit")
    path = custody.get("path")
    source_sha256 = custody.get("source_sha256")
    if not isinstance(repository, str) or not repository:
        raise QualificationLedgerError("content_ref_custody_invalid")
    if (
        not isinstance(commit, str)
        or len(commit) not in {40, 64}
        or any(character not in _HEX for character in commit)
    ):
        raise QualificationLedgerError("content_ref_custody_invalid")
    if (
        not isinstance(path, str)
        or not path
        or path.startswith("/")
        or not _CUSTODY_PATH.fullmatch(path)
        or any(component in {".", ".."} for component in path.split("/"))
    ):
        raise QualificationLedgerError("content_ref_custody_invalid")
    if (
        not isinstance(source_sha256, str)
        or len(source_sha256) != 64
        or any(character not in _HEX for character in source_sha256)
    ):
        raise QualificationLedgerError("content_ref_custody_invalid")


def _validate_registration(record: dict[str, Any], line_number: int) -> None:
    if set(record) != _REGISTRATION_KEYS:
        raise QualificationLedgerError(f"registration_shape_invalid:{line_number}")
    if record.get("schema_version") != "caplab-qualification-registration/1":
        raise QualificationLedgerError(f"registration_schema_invalid:{line_number}")
    ref = {key: record[key] for key in _CONTENT_REF_KEYS}
    _validate_content_ref(ref)
    body = {key: value for key, value in record.items() if key != "registration_ref"}
    expected = f"registration:{sha256_hex(canonical_json(body))}"
    if record["registration_ref"] != expected:
        raise QualificationLedgerError(f"registration_identity_invalid:{line_number}")


def _policy_semantic_key(policy: Mapping[str, Any]) -> bytes:
    semantic_fields = {
        "schema_version",
        "name",
        "version",
        "capability",
        "applies_to",
        "requirements",
        "criteria",
        "outcomes",
    }
    if semantic_fields.issubset(policy):
        body = {field: policy[field] for field in semantic_fields}
    else:
        body = {
            key: value
            for key, value in policy.items()
            if key not in {"policy_id", "authority", "provenance"}
        }
    return canonical_json(body)


def _validate_policy_series(
    policy: Mapping[str, Any],
    existing: Mapping[str, Mapping[str, Any]],
) -> None:
    name = policy.get("name")
    version = policy.get("version")
    if (
        not isinstance(name, str)
        or not name
        or not isinstance(version, str)
        or not version
    ):
        raise QualificationLedgerError("policy_name_version_invalid")
    semantic_key = _policy_semantic_key(policy)
    for retained in existing.values():
        if retained.get("name") != name or retained.get("version") != version:
            continue
        if _policy_semantic_key(retained) != semantic_key:
            raise QualificationLedgerError(
                f"policy_name_version_conflict:{name}:{version}"
            )


def _claim_binding_id(claim: Mapping[str, Any]) -> str:
    binding = claim.get("binding")
    if not isinstance(binding, Mapping):
        raise QualificationLedgerError("claim_binding_invalid")
    binding_id = binding.get("binding_id")
    if not isinstance(binding_id, str) or not binding_id:
        raise QualificationLedgerError("claim_binding_id_invalid")
    return binding_id


def _claim_capability(claim: Mapping[str, Any]) -> Mapping[str, Any]:
    capability = claim.get("capability")
    if not isinstance(capability, Mapping):
        raise QualificationLedgerError("claim_capability_invalid")
    return capability


def _claim_scope(claim: Mapping[str, Any]) -> tuple[str, bytes]:
    return _claim_binding_id(claim), canonical_json(_claim_capability(claim))


def _claim_supersedes(claim: Mapping[str, Any]) -> list[str]:
    supersedes = claim.get("supersedes")
    if (
        not isinstance(supersedes, list)
        or any(not isinstance(claim_id, str) or not claim_id for claim_id in supersedes)
        or len(set(supersedes)) != len(supersedes)
    ):
        raise QualificationLedgerError("claim_supersedes_invalid")
    return supersedes


def _validate_new_claim_edges(
    claim: Mapping[str, Any],
    existing: Mapping[str, Mapping[str, Any]],
) -> None:
    claim_id = claim["claim_id"]
    scope = _claim_scope(claim)
    for prior_id in _claim_supersedes(claim):
        if prior_id == claim_id:
            raise QualificationLedgerError(f"claim_self_supersession:{claim_id}")
        prior = existing.get(prior_id)
        if prior is None:
            raise QualificationLedgerError(f"claim_dangling_supersession:{prior_id}")
        if _claim_scope(prior) != scope:
            raise QualificationLedgerError(f"claim_cross_scope_supersession:{prior_id}")


def _validate_claim_graph(claims: Mapping[str, Mapping[str, Any]]) -> None:
    for claim_id, claim in claims.items():
        if claim.get("claim_id") != claim_id:
            raise QualificationLedgerError(f"claim_index_identity_mismatch:{claim_id}")
        _validate_new_claim_edges(claim, claims)
    active: set[str] = set()
    complete: set[str] = set()

    def visit(claim_id: str) -> None:
        if claim_id in complete:
            return
        if claim_id in active:
            raise QualificationLedgerError(f"claim_supersession_cycle:{claim_id}")
        active.add(claim_id)
        for prior_id in _claim_supersedes(claims[claim_id]):
            visit(prior_id)
        active.remove(claim_id)
        complete.add(claim_id)

    for claim_id in claims:
        visit(claim_id)


def _ensure_child_directory(parent: Path, name: str) -> Path:
    child = parent / name
    try:
        child.mkdir(mode=0o750)
        _fsync_directory(child)
        _fsync_directory(parent)
    except FileExistsError:
        pass
    except OSError as error:
        raise QualificationLedgerError(
            f"object_directory_create_failed:{name}"
        ) from error
    _require_real_directory(child, "object_directory")
    return child


def _require_real_directory(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise QualificationLedgerError(f"{label}_unreadable") from error
    if not stat.S_ISDIR(metadata.st_mode):
        raise QualificationLedgerError(f"{label}_not_real_directory")


def _read_regular_file(path: Path, label: str) -> bytes:
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise QualificationLedgerError(f"{label}_open_failed") from error
    with os.fdopen(descriptor, "rb", closefd=True) as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise QualificationLedgerError(f"{label}_not_regular")
        return stream.read()


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as error:
        raise QualificationLedgerError(f"directory_fsync_failed:{path}") from error
