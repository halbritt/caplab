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
retrieval relevance. `verify_task_run` re-checks every retained byte.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
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


def _json(data: bytes, label: str) -> Any:
    try:
        return json.loads(data)
    except ValueError as exc:
        raise TaskEvidenceError("MALFORMED", f"{label} is not JSON") from exc


def _load_parser(checkout: Path):
    source = checkout / PARSER_PATH
    data = _read_file(source, "Cairn trial_task_evidence.py")
    spec = importlib.util.spec_from_file_location("caplab_pinned_trial_task_evidence", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
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


def _run_key(case: Any, arm: Any, seed: Any) -> tuple:
    if not isinstance(case, str) or not isinstance(arm, str) or type(seed) is not int:
        raise TaskEvidenceError("MALFORMED", f"invalid run identity {case!r}/{arm!r}/{seed!r}")
    run_id = f"{case}.{arm}.s{seed}"
    if not _RUN_ID.fullmatch(run_id) or ".." in run_id:
        raise TaskEvidenceError("UNSAFE_PATH", f"run identity {run_id!r} is not a safe path component")
    return case, arm, seed


def _check_identity(report: dict, plan: dict, corpus_digest: str) -> dict:
    if report.get("schema") != REPORT_SCHEMA:
        raise TaskEvidenceError("UNKNOWN_SCHEMA", f"report schema must be {REPORT_SCHEMA}")
    frozen = report.get("frozen")
    if not isinstance(frozen, dict) or frozen != plan.get("frozen"):
        raise TaskEvidenceError("IDENTITY_MISMATCH", "report and plan frozen identities differ")
    if frozen.get("corpus_sha256") != corpus_digest:
        raise TaskEvidenceError("IDENTITY_MISMATCH", "corpus bytes do not match the frozen corpus hash")
    if report.get("arms") != plan.get("arms") or not isinstance(report.get("arms"), list):
        raise TaskEvidenceError("IDENTITY_MISMATCH", "report and plan arms differ")
    identity = {}
    for field in _IDENTITY_FIELDS:
        if report.get(field) != plan.get(field):
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"report and plan {field} differ")
        identity[field] = report.get(field)
    if report.get("observed_corpus") != plan.get("observed_corpus"):
        raise TaskEvidenceError("IDENTITY_MISMATCH", "report and plan observed corpus differ")
    return identity


def import_task_run(report_path: Path, *, plan_path: Path, corpus_path: Path, cairn_checkout: Path,
                    output: Path) -> dict:
    report_path, plan_path, corpus_path = Path(report_path), Path(plan_path), Path(corpus_path)
    cairn_checkout, output = Path(cairn_checkout).resolve(), Path(output).absolute()
    if output.exists():
        raise TaskEvidenceError("OUTPUT_EXISTS", f"output must be new: {output}")
    report_bytes = _read_file(report_path, "report")
    plan_bytes = _read_file(plan_path, "plan")
    corpus_bytes = _read_file(corpus_path, "corpus")
    report, plan = _json(report_bytes, "report"), _json(plan_bytes, "plan")
    if not isinstance(report, dict) or not isinstance(plan, dict):
        raise TaskEvidenceError("MALFORMED", "report and plan must be JSON objects")
    identity = _check_identity(report, plan, _sha256(corpus_bytes))

    planned, order = {}, []
    for entry in plan.get("runs") or []:
        if not isinstance(entry, list) or len(entry) != 4:
            raise TaskEvidenceError("MALFORMED", "plan runs must be [case, arm, seed, position]")
        key = _run_key(*entry[:3])
        if key in planned:
            raise TaskEvidenceError("DUPLICATE_RUN", f"plan repeats {key}")
        if key[1] not in plan["arms"]:
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"plan run uses unknown arm {key[1]!r}")
        planned[key] = entry[3]
        order.append(key)
    if not planned:
        raise TaskEvidenceError("MALFORMED", "plan has no runs")

    recorded = {}
    for record in report.get("records") or []:
        if not isinstance(record, dict):
            raise TaskEvidenceError("MALFORMED", "report records must be objects")
        key = _run_key(record.get("case"), record.get("arm"), record.get("seed"))
        if record.get("run_id") != "{}.{}.s{}".format(*key):
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"run_id {record.get('run_id')!r} does not match its identity")
        if key not in planned:
            raise TaskEvidenceError("UNPLANNED_RUN", f"report records unplanned run {record['run_id']}")
        if key in recorded:
            raise TaskEvidenceError("DUPLICATE_RUN", f"report repeats {record['run_id']}")
        for field in ("model", "harness"):
            if field in record and record[field] != identity[field]:
                raise TaskEvidenceError("IDENTITY_MISMATCH", f"{record['run_id']} {field} differs from the report")
        recorded[key] = record
    not_started = set()
    for row in (report.get("admission") or {}).get("not_started") or []:
        key = _run_key(row.get("case"), row.get("arm"), row.get("seed"))
        if key not in planned or key in recorded or key in not_started:
            raise TaskEvidenceError("IDENTITY_MISMATCH", f"not_started row {key} is unplanned, recorded or repeated")
        not_started.add(key)

    parser, parser_bytes, parser_pin = _load_parser(cairn_checkout)
    try:
        analysis = parser.analyze_report(report_path, corpus_path)
    except (ValueError, KeyError, TypeError) as exc:
        raise TaskEvidenceError("PARSER_REFUSED", f"pinned Cairn parser refused the evidence: {exc}") from exc
    rows = {r["run_id"]: r for r in analysis["records"]}

    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    ledger = FilesystemQualificationLedger(output / "ledger")

    def keep(data: bytes, kind: str, schema: str, source: str) -> dict:
        return {"source": source, "sha256": _sha256(data), "byte_count": len(data),
                "ref": ledger.register_bytes(data, kind=kind, schema=schema)}

    sources = {"report": keep(report_bytes, "cairn-task-eval-report", REPORT_SCHEMA + "+exact-bytes", str(report_path.resolve())),
               "plan": keep(plan_bytes, "cairn-task-eval-plan", "cairn.task-eval.plan+exact-bytes", str(plan_path.resolve())),
               "corpus": keep(corpus_bytes, "cairn-task-eval-corpus", "cairn.task-eval.corpus+exact-bytes", str(corpus_path.resolve())),
               "parser": dict(keep(parser_bytes, "cairn-trial-task-evidence-parser", "text/x-python+exact-bytes",
                                   str(cairn_checkout / PARSER_PATH)), pin=parser_pin)}
    observed = report.get("observed_corpus")
    if observed is not None:
        observed_bytes = _read_file(report_path.parent / observed["path"], "observed corpus")
        sources["observed_corpus"] = keep(observed_bytes, "cairn-task-eval-observed-corpus",
                                          "cairn.task-eval.corpus+exact-bytes", str((report_path.parent / observed["path"]).resolve()))

    assignments, counts = [], {"planned": len(order), "recorded": 0, "not_started": 0, "missing": 0,
                               "streams_retained": 0, "streams_missing": 0}
    outcomes, strata = {}, {}
    for key in order:
        run_id = "{}.{}.s{}".format(*key)
        row = {"run_id": run_id, "case": key[0], "arm": key[1], "seed": key[2], "order": planned[key]}
        record = recorded.get(key)
        if record is None:
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
        outcomes[str(record.get("outcome"))] = outcomes.get(str(record.get("outcome")), 0) + 1
        bucket = strata.setdefault(stratum, {})
        bucket[str(record.get("outcome"))] = bucket.get(str(record.get("outcome")), 0) + 1
        evidence = rows.get(run_id)
        if evidence is None or evidence.get("missing_stream"):
            counts["streams_missing"] += 1
            row["delivery"] = {"observed": False, "reason": "missing_stream"}
        else:
            stream = _read_file(report_path.parent / "runs" / run_id / "stream.jsonl", f"stream {run_id}")
            if _sha256(stream) != evidence["source_sha256"]:
                raise TaskEvidenceError("IDENTITY_MISMATCH", f"stream {run_id} changed while importing")
            counts["streams_retained"] += 1
            row["stream"] = keep(stream, "cairn-task-eval-stream", "cairn.native-stream+exact-bytes", str((report_path.parent / "runs" / run_id / "stream.jsonl").resolve()))
            row["delivery"] = {"observed": True, **{k: evidence[k] for k in ("preview_notes", "body_notes", "body_bytes",
                                                                              "unmapped_deliveries", "response_text_bytes")},
                               "calls": [{k: c[k] for k in ("tool", "status", "response_text_bytes", "unparsed_blocks",
                                                            "unrecognized_payloads")} for c in evidence["calls"]]}
        row["original_memory"] = record.get("memory") or None  # evaluator hook observations, as reported
        assignments.append(row)

    document = {
        "schema_version": SCHEMA,
        "sources": sources,
        "identity": {"reported": identity, "arms": report["arms"], "frozen": report["frozen"],
                     "binding": None, "configuration_identity": "incomplete: reported fields only; no CAPLAB Binding"},
        "admission": {k: (report.get("admission") or {}).get(k) for k in ("state", "stop", "planned", "admitted")},
        "counts": counts,
        "outcomes": outcomes,
        "strata": strata,
        "parser_analysis": {k: analysis[k] for k in ("report_sha256", "corpus_sha256", "observed_corpus_sha256", "analyzer_sha256")},
        "assignments": assignments,
        "limits": LIMITS,
    }
    if analysis["report_sha256"] != sources["report"]["sha256"] or analysis["analyzer_sha256"] != parser_pin["sha256"]:
        raise TaskEvidenceError("IDENTITY_MISMATCH", "parser analysed different bytes than were retained")
    # Native reports carry floats (seconds, memory timings) that CAPLAB canonical
    # JSON rightly refuses for identities. Keep them untouched: register the
    # evidence as exact sorted JSON bytes; only the float-free manifest is canonical.
    evidence_bytes = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                                allow_nan=False).encode("utf-8")
    ref = ledger.register_bytes(evidence_bytes, kind="retrieval-task-evidence", schema=SCHEMA,
                                media_type=EVIDENCE_MEDIA_TYPE)
    (output / "evidence.json").write_bytes(evidence_bytes)
    (output / "manifest.json").write_bytes(canonical_json({"schema_version": SCHEMA + "+manifest", "evidence": ref}))
    return document


def verify_task_run(output: Path) -> dict:
    """Re-verify every retained byte; raises TaskEvidenceError on any mismatch."""
    output = Path(output).absolute()
    try:
        manifest = _json(_read_file(output / "manifest.json", "manifest"), "manifest")
        ledger = FilesystemQualificationLedger(output / "ledger")
        registered = ledger.resolve(manifest["evidence"])
    except (QualificationLedgerError, KeyError, TypeError) as exc:
        raise TaskEvidenceError("INTEGRITY", f"evidence manifest or ledger failed verification: {exc}") from exc
    if _read_file(output / "evidence.json", "evidence") != registered:
        raise TaskEvidenceError("INTEGRITY", "evidence.json differs from the registered document")
    document = json.loads(registered)
    if document.get("schema_version") != SCHEMA:
        raise TaskEvidenceError("UNKNOWN_SCHEMA", f"expected {SCHEMA}")
    retained = list(document["sources"].values()) + [a["stream"] for a in document["assignments"] if "stream" in a]
    for item in retained:
        try:
            data = ledger.resolve(item["ref"])
        except QualificationLedgerError as exc:
            raise TaskEvidenceError("INTEGRITY", f"retained {item['source']} failed verification: {exc}") from exc
        if _sha256(data) != item["sha256"] or len(data) != item["byte_count"]:
            raise TaskEvidenceError("INTEGRITY", f"retained {item['source']} does not match its recorded hash")
    return {"schema_version": SCHEMA, "verified": True, "objects": len(retained) + 1, "counts": document["counts"]}
