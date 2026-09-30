"""Import a Cairn native task-evaluation run as retained CAPLAB evidence.

`import_task_run` preserves the exact bytes of a `cairn.task-eval.agent/1`
report, its original plan, its frozen corpus, any observed corpus and every
available run stream in a fresh FilesystemQualificationLedger. It runs the
explicitly selected Cairn checkout's own `scripts/trial_task_evidence.py`
parser, pinned by source hash and commit, and records the original task grades
beside the parser's delivery observations.

It never calls a model or service, never regrades, never fills a missing
stream, and never invents a native Binding: configuration identity is carried
as reported and marked incomplete. Task completion is kept separate from
retrieval relevance.

Trust boundary: the selected checkout's parser is Python code and runs in this
process at import. Select only a checkout you trust; its exact hashed bytes are
executed and retained.

`verify_task_run` re-checks every retained byte and re-derives, from the
retained report, plan and corpus bytes, every evidence field that does not come
from the parser: identities, order, statuses, original grades and memory,
strata, counts, outcomes, admission and reported identity. Parser-derived
delivery observations are bound by hash to the retained parser, report,
corpus and stream bytes but are not re-executed, unless the caller passes an
explicitly trusted checkout whose parser bytes match the retained parser.
Verification establishes consistency with immutable retained sources, not
cryptographic authorship.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import types
from typing import Any

from caplab.qualification.ledger import FilesystemQualificationLedger, QualificationLedgerError
from caplab.runtime.canonical import canonical_json

SCHEMA = "caplab-retrieval-task-evidence/1"
REPORT_SCHEMA = "cairn.task-eval.agent/1"
PARSER_PATH = "scripts/trial_task_evidence.py"
_RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,255}")
_ORIGINAL_FIELDS = ("outcome", "stratum", "correct", "mistake", "check_outcome", "execution_failure", "error",
                    "reviewed", "category", "primary", "provenance", "exit", "seconds")
# Only strata known to mean scope preservation, a no-change control or stopping
# at a blocker count as boundary/abstention. Every other value, including other
# labelled strata (decision, component, excluded) and absent strata, is unknown.
STRATUM_CLASSES = {"completion": "completion", "scope": "boundary_or_abstention",
                   "control": "boundary_or_abstention", "blocker": "boundary_or_abstention"}
EVIDENCE_MEDIA_TYPE = "application/vnd.caplab.retrieval-task-evidence+json"
_IDENTITY_FIELDS = ("model", "harness", "reasoning_effort", "wording", "harness_version", "evaluator_sha256")
LIMITS = [
    "Original task grades and check outcomes are retained source observations; this import does not certify "
    "the original instrument, oracle or labels.",
    "Task completion is a downstream measure, separate from retrieval relevance; it is not recomputed here.",
    "Delivery observations come from the pinned Cairn parser over retained MCP streams; a missing stream is "
    "unknown evidence, not zero delivery. Hook-delivered context is recorded by the original evaluator only.",
    "Configuration identity is copied as reported and is incomplete: no CAPLAB Binding, basis or Measurement "
    "record is created or implied.",
    "No model, provider or Cairn service was called while importing.",
    "The selected checkout's parser code ran in-process at import; verification re-derives all non-parser fields "
    "and binds parser output by hash, re-executing it only with an explicitly trusted matching checkout.",
]


class TaskEvidenceError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_file(path: Path, label: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise TaskEvidenceError("UNSAFE_PATH", f"{label} must be a regular file: {path}")
    return path.read_bytes()


def _reject_constant(value: str):
    raise ValueError(f"non-finite JSON number {value}")


def _json(data: bytes, label: str) -> Any:
    """Strict JSON: NaN/Infinity and pathological nesting are MALFORMED, not crashes."""
    try:
        return json.loads(data, parse_constant=_reject_constant)
    except (ValueError, RecursionError) as exc:
        raise TaskEvidenceError("MALFORMED", f"{label} is not finite JSON: {type(exc).__name__}") from exc


def _evidence_bytes(document: dict) -> bytes:
    return json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def _load_parser(checkout: Path):
    """Execute exactly the bytes that are hashed and retained (no second read)."""
    source = checkout / PARSER_PATH
    data = _read_file(source, "Cairn trial_task_evidence.py")
    module = types.ModuleType("caplab_pinned_trial_task_evidence")
    module.__file__ = str(source)
    try:
        exec(compile(data, str(source), "exec"), module.__dict__)
    except Exception as exc:  # the checkout's code failed to load; never fall back to another parser
        raise TaskEvidenceError("PARSER_CONTRACT", f"selected parser failed to load: {type(exc).__name__}") from exc
    for name in ("analyze_report", "analyze_stream"):
        if not callable(getattr(module, name, None)):
            raise TaskEvidenceError("PARSER_CONTRACT", f"pinned parser lacks {name}")
    commit = dirty = None
    try:
        commit = subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"], capture_output=True, text=True,
                                timeout=10, check=True).stdout.strip() or None
        status = subprocess.run(["git", "-C", str(checkout), "status", "--porcelain", "--", PARSER_PATH],
                                capture_output=True, text=True, timeout=10, check=True).stdout
        dirty = bool(status.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return module, data, {"path": PARSER_PATH, "checkout": str(checkout), "sha256": _sha256(data), "commit": commit,
                          "parser_file_modified": dirty}


def _run_id(key: tuple) -> str:
    return "{}.{}.s{}".format(*key)


def _run_key(case: Any, arm: Any, seed: Any) -> tuple:
    if not isinstance(case, str) or not isinstance(arm, str) or type(seed) is not int:
        raise TaskEvidenceError("MALFORMED", f"invalid run identity {case!r}/{arm!r}/{seed!r}")
    run_id = _run_id((case, arm, seed))
    if not _RUN_ID.fullmatch(run_id) or ".." in run_id:
        raise TaskEvidenceError("UNSAFE_PATH", f"run identity {run_id!r} is not a safe path component")
    return case, arm, seed


def _observed_relative(report: dict) -> str | None:
    """The observed corpus path, which must stay inside the report directory."""
    observed = report.get("observed_corpus")
    if observed is None:
        return None
    path = observed.get("path") if isinstance(observed, dict) else None
    if (not isinstance(path, str) or not path or Path(path).is_absolute()
            or any(part in ("", ".", "..") for part in Path(path).parts) or not isinstance(observed.get("sha256"), str)):
        raise TaskEvidenceError("UNSAFE_PATH", f"observed corpus path {path!r} must be a relative path inside the report directory")
    return path


def _check_inputs(report: Any, plan: Any, corpus_digest: str) -> dict:
    """Every identity check that depends only on report, plan and corpus bytes."""
    if not isinstance(report, dict) or not isinstance(plan, dict):
        raise TaskEvidenceError("MALFORMED", "report and plan must be JSON objects")
    if report.get("schema") != REPORT_SCHEMA:
        raise TaskEvidenceError("UNKNOWN_SCHEMA", f"report schema must be {REPORT_SCHEMA}")
    frozen = report.get("frozen")
    if not isinstance(frozen, dict) or frozen != plan.get("frozen"):
        raise TaskEvidenceError("IDENTITY_MISMATCH", "report and plan frozen identities differ")
    if frozen.get("corpus_sha256") != corpus_digest:
        raise TaskEvidenceError("IDENTITY_MISMATCH", "corpus bytes do not match the frozen corpus hash")
    if not isinstance(report.get("arms"), list) or report.get("arms") != plan.get("arms"):
        raise TaskEvidenceError("IDENTITY_MISMATCH", "report and plan arms differ")
    identity = {}
    for field in _IDENTITY_FIELDS:
        if report.get(field) != plan.get(field):
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"report and plan {field} differ")
        identity[field] = report.get(field)
    if report.get("observed_corpus") != plan.get("observed_corpus"):
        raise TaskEvidenceError("IDENTITY_MISMATCH", "report and plan observed corpus differ")
    _observed_relative(report)

    # Native contract (trial_task_eval.py): position is the arm's slot in the
    # shuffled arm order for one (case, seed), so 0 <= position < len(arms) and
    # positions are distinct within that (case, seed). Derived run IDs name
    # stream directories, so two identities may never derive the same run ID.
    planned, order, slots, run_ids = {}, [], {}, set()
    runs = plan.get("runs")
    if not isinstance(runs, list) or not runs:
        raise TaskEvidenceError("MALFORMED", "plan has no runs")
    for entry in runs:
        if not isinstance(entry, list) or len(entry) != 4:
            raise TaskEvidenceError("MALFORMED", "plan runs must be [case, arm, seed, position]")
        key = _run_key(*entry[:3])
        if key in planned:
            raise TaskEvidenceError("DUPLICATE_RUN", f"plan repeats {key}")
        if _run_id(key) in run_ids:
            raise TaskEvidenceError("DUPLICATE_RUN", f"plan identities collide on run_id {_run_id(key)!r}")
        run_ids.add(_run_id(key))
        if key[1] not in plan["arms"]:
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"plan run uses unknown arm {key[1]!r}")
        position = entry[3]
        if type(position) is not int or not 0 <= position < len(plan["arms"]):
            raise TaskEvidenceError("MALFORMED", f"plan position {position!r} for {key} is not an arm slot")
        taken = slots.setdefault((key[0], key[2]), set())
        if position in taken:
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"plan position {position} repeats within {key[0]} seed {key[2]}")
        taken.add(position)
        planned[key] = position
        order.append(key)

    recorded, recorded_ids = {}, set()
    records = report.get("records")
    if records is not None and not isinstance(records, list):
        raise TaskEvidenceError("MALFORMED", "report records must be a list")
    for record in records or []:
        if not isinstance(record, dict):
            raise TaskEvidenceError("MALFORMED", "report records must be objects")
        key = _run_key(record.get("case"), record.get("arm"), record.get("seed"))
        if record.get("run_id") != _run_id(key):
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"run_id {record.get('run_id')!r} does not match its identity")
        if key not in planned:
            raise TaskEvidenceError("UNPLANNED_RUN", f"report records unplanned run {record['run_id']}")
        if key in recorded or record["run_id"] in recorded_ids:
            raise TaskEvidenceError("DUPLICATE_RUN", f"report repeats {record['run_id']}")
        for field in ("model", "harness"):
            if field in record and record[field] != identity[field]:
                raise TaskEvidenceError("IDENTITY_MISMATCH", f"{record['run_id']} {field} differs from the report")
        # Older reports may omit order; a present order must match the plan.
        if "order" in record and (type(record["order"]) is not int or record["order"] != planned[key]):
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"{record['run_id']} order {record['order']!r} differs from its plan position")
        recorded[key] = record
        recorded_ids.add(record["run_id"])
    admission = report.get("admission")
    if admission is not None and not isinstance(admission, dict):
        raise TaskEvidenceError("MALFORMED", "report admission must be an object")
    not_started = set()
    rows = (admission or {}).get("not_started")
    if rows is not None and not isinstance(rows, list):
        raise TaskEvidenceError("MALFORMED", "not_started must be a list")
    for row in rows or []:
        if not isinstance(row, dict):
            raise TaskEvidenceError("MALFORMED", "not_started rows must be objects")
        key = _run_key(row.get("case"), row.get("arm"), row.get("seed"))
        if "run_id" in row and row["run_id"] != _run_id(key):
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"not_started run_id {row['run_id']!r} does not match its identity")
        if key in planned and "order" in row and (type(row["order"]) is not int or row["order"] != planned[key]):
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"not_started order {row['order']!r} differs from its plan position")
        if key not in planned or key in recorded or key in not_started:
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"not_started row {key} is unplanned, recorded or repeated")
        not_started.add(key)
    return {"identity": identity, "planned": planned, "order": order, "recorded": recorded, "not_started": not_started}


def _delivery(evidence: dict) -> dict:
    return {"observed": True, **{k: evidence[k] for k in ("preview_notes", "body_notes", "body_bytes",
                                                           "unmapped_deliveries", "response_text_bytes")},
            "calls": [{k: c[k] for k in ("tool", "status", "response_text_bytes", "unparsed_blocks",
                                         "unrecognized_payloads")} for c in evidence["calls"]]}


def _assemble(report: dict, checked: dict, sources: dict, parser_analysis: dict, streams: dict,
              deliveries: dict) -> dict:
    """Build the evidence document. Pure: import and verify share it exactly.

    `streams` maps run_id to its retained stream entry and `deliveries` maps the
    same run IDs to parser-derived delivery observations; a recorded run without
    a stream is unknown delivery, never zero.
    """
    if set(streams) != set(deliveries) or any(d.get("observed") is not True for d in deliveries.values()):
        raise TaskEvidenceError("INTEGRITY", "retained streams and delivery observations do not correspond")
    planned, recorded, not_started = checked["planned"], checked["recorded"], checked["not_started"]
    assignments, counts = [], {"planned": len(checked["order"]), "recorded": 0, "not_started": 0, "missing": 0,
                               "streams_retained": 0, "streams_missing": 0}
    outcomes, strata = {}, {}
    for key in checked["order"]:
        run_id = _run_id(key)
        row = {"run_id": run_id, "case": key[0], "arm": key[1], "seed": key[2], "order": planned[key]}
        record = recorded.get(key)
        if record is None:
            if run_id in streams:
                raise TaskEvidenceError("INTEGRITY", f"stream retained for unrecorded run {run_id}")
            row["status"] = "not_started" if key in not_started else "missing"
            counts[row["status"]] += 1
            assignments.append(row)
            continue
        counts["recorded"] += 1
        row["status"] = "recorded"
        original = {f: record[f] for f in _ORIGINAL_FIELDS if f in record}
        original.setdefault("stratum", None)  # absent in older reports: unknown, never assumed completion
        row["original"] = original
        stratum = original["stratum"] if isinstance(original["stratum"], str) and original["stratum"] else "unknown"
        row["stratum_class"] = STRATUM_CLASSES.get(stratum, "unknown")
        outcome = str(record.get("outcome"))
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
        bucket = strata.setdefault(stratum, {})
        bucket[outcome] = bucket.get(outcome, 0) + 1
        if run_id in streams:
            counts["streams_retained"] += 1
            row["stream"] = streams[run_id]
            row["delivery"] = deliveries[run_id]
        else:
            counts["streams_missing"] += 1
            row["delivery"] = {"observed": False, "reason": "missing_stream"}
        row["original_memory"] = record.get("memory") or None  # evaluator hook observations, as reported
        assignments.append(row)
    return {
        "schema_version": SCHEMA,
        "sources": sources,
        "identity": {"reported": checked["identity"], "arms": report["arms"], "frozen": report["frozen"],
                     "binding": None, "configuration_identity": "incomplete: reported fields only; no CAPLAB Binding"},
        "admission": {k: (report.get("admission") or {}).get(k) for k in ("state", "stop", "planned", "admitted")},
        "counts": counts,
        "outcomes": outcomes,
        "strata": strata,
        "parser_analysis": parser_analysis,
        "assignments": assignments,
        "limits": LIMITS,
    }


def _check_parser_analysis(analysis: dict, *, report_sha: str, corpus_sha: str, observed_sha: str | None,
                           parser_sha: str) -> None:
    """Parser output must describe exactly the retained bytes."""
    expected = {"report_sha256": report_sha, "corpus_sha256": corpus_sha, "observed_corpus_sha256": observed_sha,
                "analyzer_sha256": parser_sha}
    for key, value in expected.items():
        if analysis.get(key) != value:
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"parser {key} does not match the retained bytes")


def _analyze(parser, report_path: Path, corpus_path: Path) -> dict:
    try:
        analysis = parser.analyze_report(report_path, corpus_path)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise TaskEvidenceError("PARSER_REFUSED", f"pinned Cairn parser refused the evidence: {exc}") from exc
    if not isinstance(analysis, dict) or not isinstance(analysis.get("records"), list):
        raise TaskEvidenceError("PARSER_CONTRACT", "parser returned no records list")
    return analysis


def _deliveries_from(analysis: dict, checked: dict) -> dict:
    rows = {}
    for row in analysis["records"]:
        if row["run_id"] in rows:
            raise TaskEvidenceError("DUPLICATE_RUN", f"parser returned {row['run_id']} twice")
        rows[row["run_id"]] = row
    return {_run_id(key): rows[_run_id(key)] for key in checked["recorded"]
            if _run_id(key) in rows and not rows[_run_id(key)].get("missing_stream")}


def _write_new(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o440)
    try:
        os.write(descriptor, data)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def import_task_run(report_path: Path, *, plan_path: Path, corpus_path: Path, cairn_checkout: Path,
                    output: Path) -> dict:
    report_path, plan_path, corpus_path = Path(report_path), Path(plan_path), Path(corpus_path)
    cairn_checkout, output = Path(cairn_checkout).resolve(), Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise TaskEvidenceError("OUTPUT_EXISTS", f"output must be new: {output}")
    report_bytes = _read_file(report_path, "report")
    plan_bytes = _read_file(plan_path, "plan")
    corpus_bytes = _read_file(corpus_path, "corpus")
    report, plan = _json(report_bytes, "report"), _json(plan_bytes, "plan")
    checked = _check_inputs(report, plan, _sha256(corpus_bytes))
    observed_rel = _observed_relative(report)
    observed_bytes = None
    if observed_rel is not None:
        observed_path = report_path.parent / observed_rel
        if not observed_path.resolve().is_relative_to(report_path.parent.resolve()):
            raise TaskEvidenceError("UNSAFE_PATH", "observed corpus resolves outside the report directory")
        observed_bytes = _read_file(observed_path, "observed corpus")
        if _sha256(observed_bytes) != report["observed_corpus"]["sha256"]:
            raise TaskEvidenceError("IDENTITY_MISMATCH", "observed corpus bytes do not match the report's hash")

    parser, parser_bytes, parser_pin = _load_parser(cairn_checkout)
    analysis = _analyze(parser, report_path, corpus_path)
    _check_parser_analysis(analysis, report_sha=_sha256(report_bytes), corpus_sha=_sha256(corpus_bytes),
                           observed_sha=None if observed_bytes is None else _sha256(observed_bytes),
                           parser_sha=parser_pin["sha256"])
    evidence_rows = _deliveries_from(analysis, checked)
    stream_bytes = {}
    for run_id, evidence in evidence_rows.items():
        path = report_path.parent / "runs" / run_id / "stream.jsonl"
        data = _read_file(path, f"stream {run_id}")
        if _sha256(data) != evidence["source_sha256"]:
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"stream {run_id} changed while importing")
        stream_bytes[run_id] = (data, str(path.resolve()))
    deliveries = {run_id: _delivery(evidence) for run_id, evidence in evidence_rows.items()}
    parser_analysis = {k: analysis[k] for k in ("report_sha256", "corpus_sha256", "observed_corpus_sha256", "analyzer_sha256")}
    # Everything that can fail on input content has been checked; only I/O remains.
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.mkdir()
    except FileExistsError as exc:
        raise TaskEvidenceError("OUTPUT_EXISTS", f"output must be new: {output}") from exc
    except OSError as exc:
        raise TaskEvidenceError("UNSAFE_PATH", f"cannot create output {output}: {exc.strerror}") from exc
    ledger = FilesystemQualificationLedger(output / "ledger")

    def keep(data: bytes, kind: str, schema: str, source: str) -> dict:
        return {"source": source, "sha256": _sha256(data), "byte_count": len(data),
                "ref": ledger.register_bytes(data, kind=kind, schema=schema)}

    sources = {"report": keep(report_bytes, "cairn-task-eval-report", REPORT_SCHEMA + "+exact-bytes", str(report_path.resolve())),
               "plan": keep(plan_bytes, "cairn-task-eval-plan", "cairn.task-eval.plan+exact-bytes", str(plan_path.resolve())),
               "corpus": keep(corpus_bytes, "cairn-task-eval-corpus", "cairn.task-eval.corpus+exact-bytes", str(corpus_path.resolve())),
               "parser": dict(keep(parser_bytes, "cairn-trial-task-evidence-parser", "text/x-python+exact-bytes",
                                   str(cairn_checkout / PARSER_PATH)), pin=parser_pin)}
    if observed_bytes is not None:
        sources["observed_corpus"] = keep(observed_bytes, "cairn-task-eval-observed-corpus",
                                          "cairn.task-eval.corpus+exact-bytes", str((report_path.parent / observed_rel).resolve()))
    streams = {run_id: keep(data, "cairn-task-eval-stream", "cairn.native-stream+exact-bytes", source)
               for run_id, (data, source) in stream_bytes.items()}
    document = _assemble(report, checked, sources, parser_analysis, streams, deliveries)
    # Native reports carry floats (seconds, memory timings) that CAPLAB canonical
    # JSON rightly refuses for identities. Keep them untouched: register the
    # evidence as exact sorted JSON bytes; only the float-free manifest is canonical.
    evidence_bytes = _evidence_bytes(document)
    ref = ledger.register_bytes(evidence_bytes, kind="retrieval-task-evidence", schema=SCHEMA,
                                media_type=EVIDENCE_MEDIA_TYPE)
    _write_new(output / "evidence.json", evidence_bytes)
    _write_new(output / "manifest.json", canonical_json({"schema_version": SCHEMA + "+manifest", "evidence": ref}))
    return document


def _resolve_source(ledger, item: Any, label: str) -> bytes:
    if not isinstance(item, dict) or not isinstance(item.get("ref"), dict):
        raise TaskEvidenceError("INTEGRITY", f"retained {label} reference is malformed")
    try:
        data = ledger.resolve(item["ref"])
    except QualificationLedgerError as exc:
        raise TaskEvidenceError("INTEGRITY", f"retained {label} failed verification: {exc}") from exc
    if _sha256(data) != item.get("sha256") or len(data) != item.get("byte_count"):
        raise TaskEvidenceError("INTEGRITY", f"retained {label} does not match its recorded hash")
    return data


def verify_task_run(output: Path, *, trusted_parser_checkout: Path | None = None) -> dict:
    """Verify retained bytes and re-derive the evidence document from them.

    Every non-parser field is recomputed from the retained report, plan and
    corpus and must reproduce evidence.json byte for byte. Parser-derived
    delivery observations are hash-bound to retained parser, report, corpus and
    stream bytes; they are re-executed only when `trusted_parser_checkout` is
    given and its parser bytes equal the retained parser. Retained code is never
    executed. Raises TaskEvidenceError on any mismatch.
    """
    output = Path(output).absolute()
    try:
        manifest = _json(_read_file(output / "manifest.json", "manifest"), "manifest")
        ledger = FilesystemQualificationLedger(output / "ledger")
        registered = ledger.resolve(manifest["evidence"])
    except (QualificationLedgerError, KeyError, TypeError) as exc:
        raise TaskEvidenceError("INTEGRITY", f"evidence manifest or ledger failed verification: {exc}") from exc
    if _read_file(output / "evidence.json", "evidence") != registered:
        raise TaskEvidenceError("INTEGRITY", "evidence.json differs from the registered document")
    document = _json(registered, "evidence")
    if not isinstance(document, dict) or document.get("schema_version") != SCHEMA:
        raise TaskEvidenceError("UNKNOWN_SCHEMA", f"expected {SCHEMA}")
    sources, assignments = document.get("sources"), document.get("assignments")
    if not isinstance(sources, dict) or not isinstance(assignments, list):
        raise TaskEvidenceError("INTEGRITY", "evidence document lacks sources or assignments")
    data = {name: _resolve_source(ledger, sources.get(name), name) for name in ("report", "plan", "corpus", "parser")}
    report, plan = _json(data["report"], "retained report"), _json(data["plan"], "retained plan")
    checked = _check_inputs(report, plan, _sha256(data["corpus"]))
    observed_rel = _observed_relative(report)
    if (observed_rel is None) != ("observed_corpus" not in sources):
        raise TaskEvidenceError("INTEGRITY", "retained observed corpus does not match the report")
    observed = None if observed_rel is None else _resolve_source(ledger, sources["observed_corpus"], "observed corpus")
    if observed is not None and _sha256(observed) != report["observed_corpus"]["sha256"]:
        raise TaskEvidenceError("INTEGRITY", "retained observed corpus does not match the report's hash")
    pin = sources["parser"].get("pin")
    if not isinstance(pin, dict) or pin.get("sha256") != _sha256(data["parser"]):
        raise TaskEvidenceError("INTEGRITY", "parser pin does not match the retained parser bytes")
    parser_analysis = document.get("parser_analysis")
    if not isinstance(parser_analysis, dict):
        raise TaskEvidenceError("INTEGRITY", "evidence lacks parser analysis hashes")
    _check_parser_analysis(parser_analysis, report_sha=_sha256(data["report"]), corpus_sha=_sha256(data["corpus"]),
                           observed_sha=None if observed is None else _sha256(observed), parser_sha=_sha256(data["parser"]))
    streams, deliveries, stream_data = {}, {}, {}
    for row in assignments:
        if not isinstance(row, dict) or not isinstance(row.get("run_id"), str):
            raise TaskEvidenceError("INTEGRITY", "evidence assignment is malformed")
        if "stream" in row:
            stream_data[row["run_id"]] = _resolve_source(ledger, row["stream"], f"stream {row['run_id']}")
            streams[row["run_id"]] = row["stream"]
            deliveries[row["run_id"]] = row.get("delivery")
            if not isinstance(deliveries[row["run_id"]], dict):
                raise TaskEvidenceError("INTEGRITY", f"delivery for {row['run_id']} is malformed")
    parser_mode = "hash-bound; not re-executed"
    if trusted_parser_checkout is not None:
        parser, trusted_bytes, _ = _load_parser(Path(trusted_parser_checkout).resolve())
        if trusted_bytes != data["parser"]:
            raise TaskEvidenceError("PARSER_CONTRACT", "trusted checkout's parser differs from the retained parser")
        with tempfile.TemporaryDirectory(prefix="caplab-task-verify-") as scratch:
            root = Path(scratch)
            (root / "agent.json").write_bytes(data["report"])
            (root / "corpus.json").write_bytes(data["corpus"])
            if observed is not None:
                (root / observed_rel).parent.mkdir(parents=True, exist_ok=True)
                (root / observed_rel).write_bytes(observed)
            for run_id, stream in stream_data.items():
                (root / "runs" / run_id).mkdir(parents=True)
                (root / "runs" / run_id / "stream.jsonl").write_bytes(stream)
            analysis = _analyze(parser, root / "agent.json", root / "corpus.json")
        fresh = {run_id: _delivery(row) for run_id, row in _deliveries_from(analysis, checked).items()}
        if fresh != deliveries:
            raise TaskEvidenceError("INTEGRITY", "re-executed parser observations differ from the retained evidence")
        parser_mode = "re-executed with trusted checkout; matched"
    rebuilt = _assemble(report, checked, sources, parser_analysis, streams, deliveries)
    if _evidence_bytes(rebuilt) != registered:
        raise TaskEvidenceError("INTEGRITY", "evidence does not re-derive from the retained report, plan and corpus")
    retained = 5 + (observed is not None) + len(stream_data)  # sources incl. evidence, plus streams
    return {"schema_version": SCHEMA, "verified": True, "objects": retained, "counts": document["counts"],
            "evidence": document,
            "verification": {"bytes": "every retained object resolved and hashed",
                             "rederived": "all non-parser fields reproduce evidence.json byte for byte",
                             "parser_derived": parser_mode,
                             "authorship": "not authenticated; consistency with retained sources only"}}
