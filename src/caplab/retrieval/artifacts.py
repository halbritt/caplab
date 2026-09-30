"""Immutable, verifiable run evidence for the Cairn retrieval evaluation harness.

`RunArtifacts` writes one new run directory:

    plan.json       sealed plan: normalized spec, pins and the full assignment roster,
                    written before any retrieval runs
    attempts.jsonl  one validated attempt per line, appended and fsynced as it is recorded
    evidence.jsonl  hash-chained index of raw artifacts per attempt and named artifacts
    report.json     the final `caplab-retrieval-report/1` (written by `finish`)
    manifest.json   file hashes, chain head and ledger references (written last)
    ledger/         a FilesystemQualificationLedger holding exact raw bytes

Raw request, response, stdout and stderr bytes are registered byte for byte in the
ledger; nothing is re-encoded, so floats and unusual JSON inside them survive.
JSON media is stored as opaque bytes because the ledger canonicalizes JSON
documents and refuses floats. The plan and the report are also registered there.
A retrieval report is an observational experiment artifact, not a
`caplab-measurement/1` record: no Binding or basis authorization is created.

`verify_run` re-checks every retained byte and recomputes the metrics before it
returns anything. It detects inconsistent edits, not authorship; pin the
manifest digest elsewhere to detect wholesale replacement.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import threading
from pathlib import Path
from typing import Any

from caplab.qualification.ledger import FilesystemQualificationLedger, QualificationLedgerError
from caplab.retrieval import contracts, metrics
from caplab.retrieval.report import REPORT_SCHEMA, build_report, run_status

PLAN_SCHEMA = "caplab-retrieval-plan/1"
MANIFEST_SCHEMA = "caplab-retrieval-manifest/1"
EVIDENCE_SCHEMA = "caplab-retrieval-evidence/1"
RAW_LEDGER_SCHEMA = "caplab-retrieval-raw/1"
PLAN_FILE = "plan.json"
ATTEMPTS_FILE = "attempts.jsonl"
EVIDENCE_FILE = "evidence.jsonl"
REPORT_FILE = "report.json"
MANIFEST_FILE = "manifest.json"
LEDGER_DIR = "ledger"
KNOWN_FILES = {PLAN_FILE, ATTEMPTS_FILE, EVIDENCE_FILE, REPORT_FILE, MANIFEST_FILE, LEDGER_DIR}
MAX_RAW_BYTES = 256 << 20
MAX_PROVENANCE_BYTES = 1 << 20
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")  # raw roles
_ARTIFACT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,255}")  # run-level names such as arm.<arm-id>.stdout
_GENESIS = "0" * 64


class ArtifactError(ValueError):
    """An operation on a run being written was refused."""

    def __init__(self, code: str, message: str, **detail: Any) -> None:
        super().__init__(f"{code}: {message}")
        self.code, self.message, self.detail = code, message, detail


class ArtifactIntegrityError(ArtifactError):
    """Retained evidence failed verification; nothing from it may be used."""


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: Path | str) -> dict:
    """Hash an external source (binary, checkout file) for the plan's provenance."""
    resolved = Path(os.path.abspath(os.fspath(path)))
    digest, size = hashlib.sha256(), 0
    try:
        with open(resolved, "rb") as handle:
            while chunk := handle.read(1 << 20):
                digest.update(chunk)
                size += len(chunk)
    except OSError as error:
        raise ArtifactError("SOURCE_UNREADABLE", f"cannot read {resolved}: {error.strerror or error}") from error
    return {"path": str(resolved), "sha256": digest.hexdigest(), "byte_count": size}


# ---- serialization ---------------------------------------------------------------------------


def _pretty(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _line(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + sha256_hex(contracts.canonical_json(value))


def _fsync_dir(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_new(path: Path, data: bytes, mode: int = 0o640) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC | os.O_NOFOLLOW, mode)
    try:
        view = memoryview(data)
        while view:
            view = view[os.write(descriptor, view):]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    _fsync_dir(path.parent)


def _append(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        view = memoryview(data)
        while view:
            view = view[os.write(descriptor, view):]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _pins(spec: dict) -> dict:
    return {
        "spec_sha256": contracts.spec_digest(spec),
        "corpus_sha256": _digest(spec["corpus"]),
        "cases_sha256": _digest(spec["queries"]),
        "arms": {arm["id"]: _digest(arm) for arm in spec["arms"]},
        "roster_sha256": _digest(contracts.assignments(spec)),
        "design": {"cutoffs": spec["cutoffs"], "seeds": spec["seeds"], "timeout_seconds": spec["timeout_seconds"]},
    }


def build_plan(spec: dict, provenance: dict | None = None) -> dict:
    """The sealed plan: normalized spec, every pin and the full roster."""
    spec = contracts.validate_spec(spec)
    return {"schema_version": PLAN_SCHEMA, "experiment_id": spec["experiment_id"], "spec": spec, "pins": _pins(spec),
            "roster": contracts.assignments(spec), "provenance": _owned_provenance(provenance)}


def _owned_provenance(provenance: dict | None) -> dict:
    if provenance is None:
        return {}
    if not isinstance(provenance, dict):
        raise ArtifactError("PROVENANCE_INVALID", "provenance must be an object")
    try:
        data = json.dumps(provenance, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ArtifactError("PROVENANCE_INVALID", f"provenance is not finite JSON: {error}") from error
    if len(data.encode("utf-8")) > MAX_PROVENANCE_BYTES:
        raise ArtifactError("PROVENANCE_INVALID", "provenance is too large")
    return json.loads(data)


def _entry(previous: str, sequence: int, kind: str, body: dict) -> tuple[dict, bytes]:
    entry = {"schema_version": EVIDENCE_SCHEMA, "sequence": sequence, "kind": kind, **body, "prev": previous}
    entry["entry_sha256"] = sha256_hex(_line(entry))
    return entry, _line(entry) + b"\n"


# ---- writing ---------------------------------------------------------------------------------


class RunArtifacts:
    """Write one new run directory. Safe for concurrent `record_attempt` calls."""

    def __init__(self, output: Path | str, spec: dict, *, provenance: dict | None = None) -> None:
        self.spec = contracts.validate_spec(spec)
        self.plan = build_plan(self.spec, provenance)
        self.output = Path(os.path.abspath(os.fspath(output)))
        if not self.output.parent.is_dir():
            raise ArtifactError("OUTPUT_PARENT_MISSING", f"{self.output.parent} is not a directory")
        try:
            self.output.mkdir(mode=0o750)
        except FileExistsError as error:
            raise ArtifactError("OUTPUT_EXISTS", f"{self.output} already exists; a run needs a new directory") from error
        self._lock = threading.Lock()
        self._closed = False
        self._recorded: dict[str, str] = {}
        self._artifacts: dict[str, str] = {}
        self._sequence, self._head = 0, _GENESIS
        self.ledger = self._open_ledger()
        plan_bytes = _pretty(self.plan)
        _write_new(self.output / PLAN_FILE, plan_bytes)
        _write_new(self.output / ATTEMPTS_FILE, b"")
        _write_new(self.output / EVIDENCE_FILE, b"")
        self._plan_ref = self._register_ledger(plan_bytes, "retrieval-plan")

    def _open_ledger(self) -> FilesystemQualificationLedger:
        try:
            return FilesystemQualificationLedger(self.output / LEDGER_DIR)
        except QualificationLedgerError as error:
            raise ArtifactError("LEDGER_REFUSED", str(error)) from error

    def _register_ledger(self, payload: bytes, kind: str, media_type: str = "application/octet-stream") -> dict:
        if media_type == "application/json":
            media_type = "application/octet-stream"  # exact bytes; the ledger canonicalizes JSON documents
        try:
            return self.ledger.register_bytes(payload, kind=kind, schema=RAW_LEDGER_SCHEMA, media_type=media_type)
        except QualificationLedgerError as error:
            raise ArtifactError("LEDGER_REFUSED", str(error)) from error

    def _require_open(self) -> None:
        if self._closed:
            raise ArtifactError("RUN_FINISHED", "the run is finished or closed; no further evidence can be added")

    def _append_entry(self, kind: str, body: dict) -> dict:
        entry, data = _entry(self._head, self._sequence, kind, body)
        _append(self.output / EVIDENCE_FILE, data)
        self._sequence, self._head = self._sequence + 1, entry["entry_sha256"]
        return entry

    def pending_assignments(self) -> list[dict]:
        """Roster rows with no recorded attempt, in roster order."""
        with self._lock:
            return [row for row in self.plan["roster"] if row["assignment_id"] not in self._recorded]

    def register_bytes(self, name: str, payload: bytes, *, media_type: str = "application/octet-stream") -> dict:
        """Register a named exact-byte artifact (binary identity, corpus export, worker log)."""
        if not isinstance(name, str) or not _ARTIFACT_NAME.fullmatch(name):
            raise ArtifactError("NAME_INVALID", "artifact names are slugs of [A-Za-z0-9._-], at most 256 characters")
        self._check_payload(payload)
        if not isinstance(media_type, str) or not media_type or len(media_type) > 128:
            raise ArtifactError("MEDIA_TYPE_INVALID", "media_type must be a short nonempty string")
        with self._lock:
            self._require_open()
            digest = sha256_hex(payload)
            if name in self._artifacts:
                if self._artifacts[name] != digest:
                    raise ArtifactError("ARTIFACT_NAME_CONFLICT", f"{name!r} is already registered with other bytes")
                return {"name": name, "declared_media_type": media_type, "sha256": digest, "byte_count": len(payload)}
            ref = self._register_ledger(payload, "retrieval-artifact", media_type)
            self._append_entry("artifact", {"name": name, "declared_media_type": media_type, "ref": ref})
            self._artifacts[name] = digest
        return {"name": name, "declared_media_type": media_type, "sha256": digest, "byte_count": len(payload)}

    @staticmethod
    def _check_payload(payload: Any) -> None:
        if not isinstance(payload, bytes):
            raise ArtifactError("PAYLOAD_NOT_BYTES", "raw evidence must be bytes; it is never re-encoded")
        if len(payload) > MAX_RAW_BYTES:
            raise ArtifactError("PAYLOAD_TOO_LARGE", f"raw evidence exceeds {MAX_RAW_BYTES} bytes")

    def record_attempt(self, attempt: dict, *, raw: dict[str, bytes] | None = None) -> dict:
        """Validate and durably record one attempt and its raw artifacts.

        Returns the normalized attempt with exactly the attempt contract fields.
        Raw references go to evidence.jsonl and the manifest. A second attempt
        for the same assignment is refused, never overwritten.
        """
        raw = dict(raw or {})
        for role, payload in raw.items():
            if not isinstance(role, str) or not _NAME.fullmatch(role):
                raise ArtifactError("NAME_INVALID", "raw roles are slugs such as request, response, stdout, stderr")
            self._check_payload(payload)
        normalized = contracts.validate_attempt(attempt, self.spec)
        with self._lock:
            self._require_open()
            assignment = normalized["assignment_id"]
            if assignment in self._recorded:
                raise ArtifactError("DUPLICATE_ATTEMPT", f"{assignment!r} already has a recorded attempt")
            refs = {role: self._register_ledger(payload, "retrieval-raw") for role, payload in sorted(raw.items())}
            line = _line(normalized)
            digest = sha256_hex(line)
            # Evidence first: an interrupted write leaves orphan evidence, never an unexplained attempt.
            self._append_entry("attempt", {"assignment_id": assignment, "attempt_sha256": digest, "raw": refs})
            _append(self.output / ATTEMPTS_FILE, line + b"\n")
            self._recorded[assignment] = digest
        return json.loads(line)

    def finish(self) -> dict:
        """Write the report and manifest. Incomplete coverage is reported, never hidden."""
        with self._lock:
            self._require_open()
            self._closed = True
            loaded = _load_run_files(self.output)
            report_bytes, references, status = _report_bytes(loaded)
            _write_new(self.output / REPORT_FILE, report_bytes, 0o440)
            report_ref = self._register_ledger(report_bytes, "retrieval-report")
            manifest = _build_manifest(loaded, report_bytes, report_ref, self._plan_ref, status)
            manifest_bytes = _pretty(manifest)
            _write_new(self.output / MANIFEST_FILE, manifest_bytes, 0o440)
            for name in (PLAN_FILE, ATTEMPTS_FILE, EVIDENCE_FILE):
                os.chmod(self.output / name, 0o440)
            report = json.loads(report_bytes)
        return {"status": status["status"], "complete": status["status"] == "complete", "run": report["run"],
                "report": report, "manifest_sha256": sha256_hex(manifest_bytes), "output": str(self.output),
                "report_path": str(self.output / REPORT_FILE)}


# ---- reading and verification ----------------------------------------------------------------


def _fail(code: str, message: str, **detail: Any) -> None:
    raise ArtifactIntegrityError(code, message, **detail)


def _read(path: Path, what: str) -> bytes:
    try:
        if path.is_symlink() or not path.is_file():
            _fail("FILE_MISSING", f"{what} ({path.name}) is missing or not a regular file")
        return path.read_bytes()
    except OSError as error:
        _fail("FILE_UNREADABLE", f"cannot read {what}: {error.strerror or error}")
    raise AssertionError  # pragma: no cover


def _parse(data: bytes, what: str) -> Any:
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        _fail("FILE_MALFORMED", f"{what} is not valid JSON: {error}")
    raise AssertionError  # pragma: no cover


def _same(left: Any, right: Any) -> bool:
    """Structural equality; floats match to display precision so a platform's last bit cannot fail a check."""
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, float) or isinstance(right, float):
        return (isinstance(left, (int, float)) and isinstance(right, (int, float))
                and math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-12))
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(_same(left[key], right[key]) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right))
    return type(left) is type(right) and left == right


class _Loaded:
    """Verified, in-memory view of the retained files of one run."""

    def __init__(self) -> None:
        self.output: Path
        self.plan_bytes = self.attempts_bytes = self.evidence_bytes = b""
        self.plan: dict = {}
        self.spec: dict = {}
        self.attempts: list[dict] = []
        self.entries: list[dict] = []
        self.ledger: FilesystemQualificationLedger
        self.raw_count = 0
        self.orphans = 0


def _load_run_files(output: Path) -> _Loaded:
    try:
        return _load_run_files_unchecked(output)
    except (KeyError, TypeError, AttributeError, IndexError) as error:  # malformed content that passed a hash
        _fail("RUN_MALFORMED", f"retained content has an unexpected shape: {type(error).__name__}: {error}")
    raise AssertionError  # pragma: no cover


def _load_run_files_unchecked(output: Path) -> _Loaded:
    loaded = _Loaded()
    loaded.output = output
    if not output.is_dir():
        _fail("RUN_MISSING", f"{output} is not a run directory")
    loaded.plan_bytes = _read(output / PLAN_FILE, "plan")
    plan = _parse(loaded.plan_bytes, "plan")
    if not isinstance(plan, dict) or plan.get("schema_version") != PLAN_SCHEMA:
        _fail("PLAN_INVALID", f"plan.json is not {PLAN_SCHEMA}")
    try:
        spec = contracts.validate_spec(plan.get("spec"))
    except contracts.ContractError as error:
        _fail("SPEC_INVALID", f"the retained spec is invalid: {error}")
    if spec != plan["spec"]:
        _fail("SPEC_NOT_NORMALIZED", "the retained spec is not in normalized form")
    expected_plan = {"schema_version": PLAN_SCHEMA, "experiment_id": spec["experiment_id"], "spec": spec,
                     "pins": _pins(spec), "roster": contracts.assignments(spec), "provenance": plan.get("provenance")}
    if not _same(plan, expected_plan) or not isinstance(plan.get("provenance"), dict):
        _fail("PLAN_MISMATCH", "the retained plan pins or roster do not match its spec")
    loaded.plan, loaded.spec = plan, spec

    loaded.evidence_bytes = _read(output / EVIDENCE_FILE, "evidence index")
    loaded.attempts_bytes = _read(output / ATTEMPTS_FILE, "attempts")
    loaded.entries = _verify_chain(loaded.evidence_bytes)
    _load_attempts(loaded)
    ledger_path = output / LEDGER_DIR
    if not ledger_path.is_dir() or ledger_path.is_symlink():
        _fail("LEDGER_MISSING", "the ledger directory is missing")
    try:
        loaded.ledger = FilesystemQualificationLedger(ledger_path)
        for entry in loaded.entries:
            refs = entry["raw"].values() if entry["kind"] == "attempt" else [entry["ref"]]
            for ref in refs:
                payload = loaded.ledger.resolve(ref)
                if len(payload) != ref["byte_count"] or sha256_hex(payload) != ref["sha256"]:
                    _fail("RAW_ARTIFACT_TAMPERED", "raw bytes do not match their retained reference")
                loaded.raw_count += 1
    except QualificationLedgerError as error:
        _fail("RAW_ARTIFACT_TAMPERED", f"a retained raw artifact failed ledger verification: {error}")
    return loaded


def _verify_chain(data: bytes) -> list[dict]:
    entries, previous = [], _GENESIS
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    elif lines:
        _fail("EVIDENCE_CHAIN_BROKEN", "the evidence index ends in a partial line")
    for index, raw_line in enumerate(lines):
        entry = _parse(raw_line, f"evidence entry {index}")
        if (not isinstance(entry, dict) or entry.get("schema_version") != EVIDENCE_SCHEMA
                or entry.get("sequence") != index or entry.get("prev") != previous
                or entry.get("kind") not in ("attempt", "artifact")):
            _fail("EVIDENCE_CHAIN_BROKEN", f"evidence entry {index} is out of sequence or malformed")
        body = {key: value for key, value in entry.items() if key != "entry_sha256"}
        if _line(entry) != raw_line:
            _fail("EVIDENCE_CHAIN_BROKEN", f"evidence entry {index} is not in its canonical form")
        if entry.get("entry_sha256") != sha256_hex(_line(body)):
            _fail("EVIDENCE_CHAIN_BROKEN", f"evidence entry {index} fails its hash")
        if entry["kind"] == "attempt" and not (
                isinstance(entry.get("raw"), dict) and all(isinstance(ref, dict) for ref in entry["raw"].values())
                and isinstance(entry.get("attempt_sha256"), str) and isinstance(entry.get("assignment_id"), str)):
            _fail("EVIDENCE_CHAIN_BROKEN", f"evidence entry {index} lacks attempt fields")
        if entry["kind"] == "artifact" and not (
                isinstance(entry.get("ref"), dict) and isinstance(entry.get("name"), str)
                and isinstance(entry.get("declared_media_type"), str)):
            _fail("EVIDENCE_CHAIN_BROKEN", f"evidence entry {index} lacks artifact fields")
        previous = entry["entry_sha256"]
        entries.append(entry)
    return entries


def _load_attempts(loaded: _Loaded) -> None:
    lines = loaded.attempts_bytes.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    elif lines:
        _fail("ATTEMPTS_TRUNCATED", "attempts.jsonl ends in a partial line")
    by_hash: dict[str, list[dict]] = {}
    for entry in loaded.entries:
        if entry["kind"] == "attempt":
            by_hash.setdefault(entry["attempt_sha256"], []).append(entry)
    seen: set[str] = set()
    for index, raw_line in enumerate(lines):
        parsed = _parse(raw_line, f"attempt {index}")
        try:
            attempt = contracts.validate_attempt(parsed, loaded.spec)
        except contracts.ContractError as error:
            _fail("ATTEMPT_INVALID", f"attempt {index} is invalid: {error}", line=index)
        if _line(attempt) != raw_line:
            _fail("ATTEMPT_NOT_NORMALIZED", f"attempt {index} is not stored in its normalized form", line=index)
        if attempt["assignment_id"] in seen:
            _fail("ATTEMPT_DUPLICATE", f"{attempt['assignment_id']!r} has more than one attempt", line=index)
        seen.add(attempt["assignment_id"])
        candidates = by_hash.get(sha256_hex(raw_line), [])
        if not candidates or candidates[0]["assignment_id"] != attempt["assignment_id"]:
            _fail("ATTEMPT_WITHOUT_EVIDENCE", f"attempt {index} has no matching evidence entry", line=index)
        candidates.pop(0)
        loaded.attempts.append(attempt)
    loaded.orphans = sum(len(rest) for rest in by_hash.values())


def _references(loaded: _Loaded) -> dict:
    raw_artifacts = []
    for entry in loaded.entries:
        if entry["kind"] == "attempt":
            for role, ref in entry["raw"].items():
                raw_artifacts.append({"assignment_id": entry["assignment_id"], "role": role, "sha256": ref["sha256"],
                                      "byte_count": ref["byte_count"]})
        else:
            ref = entry["ref"]
            raw_artifacts.append({"name": entry["name"], "declared_media_type": entry["declared_media_type"],
                                  "sha256": ref["sha256"], "byte_count": ref["byte_count"]})
    return {
        "plan": {"file": PLAN_FILE, "sha256": sha256_hex(loaded.plan_bytes), "byte_count": len(loaded.plan_bytes)},
        "attempts": {"file": ATTEMPTS_FILE, "sha256": sha256_hex(loaded.attempts_bytes),
                     "count": len(loaded.attempts)},
        "evidence": {"file": EVIDENCE_FILE, "entries": len(loaded.entries),
                     "chain_head": loaded.entries[-1]["entry_sha256"] if loaded.entries else _GENESIS,
                     "orphan_attempt_entries": loaded.orphans},
        "raw_artifacts": raw_artifacts,
    }


def _report_bytes(loaded: _Loaded) -> tuple[bytes, dict, dict]:
    summary = metrics.summarize(loaded.spec, loaded.attempts)
    references = _references(loaded)
    report = build_report(loaded.plan, loaded.attempts, summary, finished=True, references=references)
    return _pretty(report), references, run_status(loaded.plan, loaded.attempts)


def _build_manifest(loaded: _Loaded, report_bytes: bytes, report_ref: dict, plan_ref: dict, status: dict) -> dict:
    references = _references(loaded)
    return {
        "schema_version": MANIFEST_SCHEMA,
        "experiment_id": loaded.plan["experiment_id"],
        "pins": loaded.plan["pins"],
        "finished": True,
        "status": status["status"],
        "files": {
            PLAN_FILE: {"sha256": sha256_hex(loaded.plan_bytes), "byte_count": len(loaded.plan_bytes), "ledger": plan_ref},
            ATTEMPTS_FILE: {"sha256": sha256_hex(loaded.attempts_bytes), "byte_count": len(loaded.attempts_bytes),
                            "count": len(loaded.attempts)},
            EVIDENCE_FILE: {"sha256": sha256_hex(loaded.evidence_bytes), "byte_count": len(loaded.evidence_bytes),
                            "entries": len(loaded.entries), "chain_head": references["evidence"]["chain_head"]},
            REPORT_FILE: {"sha256": sha256_hex(report_bytes), "byte_count": len(report_bytes), "ledger": report_ref},
        },
        "raw_artifacts": references["raw_artifacts"],
    }


def verify_run(output: Path | str, *, allow_unfinished: bool = False) -> dict:
    """Verify a run directory and return its retained content.

    Re-hashes every retained file and ledger object, re-validates the spec and
    every attempt, checks the evidence chain and the full roster accounting, and
    recomputes the report from the attempts. Any inconsistency raises
    `ArtifactIntegrityError` with a stable code. An unfinished run (no manifest,
    for example after an interruption) raises `RUN_NOT_FINISHED` unless
    `allow_unfinished` is set, in which case the report is computed in memory
    with `run.finished` false and nothing about the missing work is hidden.
    """
    output = Path(os.path.realpath(os.fspath(output)))  # a symlinked run root is followed; member files never are
    loaded = _load_run_files(output)
    manifest_path, report_path = output / MANIFEST_FILE, output / REPORT_FILE
    verification = {"unexpected_files": sorted(child.name for child in output.iterdir() if child.name not in KNOWN_FILES),
                    "raw_artifacts_verified": loaded.raw_count, "orphan_attempt_entries": loaded.orphans}
    if not manifest_path.exists():
        if not allow_unfinished:
            _fail("RUN_NOT_FINISHED", "the run has no manifest; it was interrupted or is still running",
                  recorded=len(loaded.attempts))
        if report_path.exists():
            _fail("REPORT_WITHOUT_MANIFEST", "report.json exists but the run has no manifest")
        summary = metrics.summarize(loaded.spec, loaded.attempts)
        report = build_report(loaded.plan, loaded.attempts, summary, finished=False, references=_references(loaded))
        return {"output": str(output), "finished": False, "spec": loaded.spec, "plan": loaded.plan,
                "attempts": loaded.attempts, "report": report, "manifest": None, "manifest_sha256": None,
                "verification": verification}
    manifest_bytes = _read(manifest_path, "manifest")
    manifest = _parse(manifest_bytes, "manifest")
    report_bytes = _read(report_path, "report")
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if (not isinstance(files, dict) or manifest.get("schema_version") != MANIFEST_SCHEMA
            or not all(isinstance(files.get(name), dict) for name in (PLAN_FILE, REPORT_FILE))):
        _fail("MANIFEST_MISMATCH", "the manifest is malformed")
    expected_bytes, _, status = _report_bytes(loaded)
    expected_manifest = _build_manifest(loaded, report_bytes, files[REPORT_FILE].get("ledger"),
                                        files[PLAN_FILE].get("ledger"), status)
    if not _same(manifest, expected_manifest):
        _fail("MANIFEST_MISMATCH", "the manifest does not match the retained files")
    try:
        for name, retained in ((PLAN_FILE, loaded.plan_bytes), (REPORT_FILE, report_bytes)):
            if loaded.ledger.resolve(files[name]["ledger"]) != retained:
                _fail("MANIFEST_MISMATCH", f"{name} differs from its ledger registration")
    except (QualificationLedgerError, KeyError, TypeError) as error:
        _fail("MANIFEST_MISMATCH", f"a manifest ledger reference failed verification: {error}")
    report = _parse(report_bytes, "report")
    if not isinstance(report, dict) or report.get("schema_version") != REPORT_SCHEMA:
        _fail("REPORT_INVALID", f"report.json is not {REPORT_SCHEMA}")
    if not _same(report, json.loads(expected_bytes)):
        _fail("REPORT_MISMATCH", "the report differs from the metrics recomputed from the retained attempts")
    return {"output": str(output), "finished": True, "spec": loaded.spec, "plan": loaded.plan,
            "attempts": loaded.attempts, "report": report, "manifest": manifest,
            "manifest_sha256": sha256_hex(manifest_bytes), "verification": verification}
