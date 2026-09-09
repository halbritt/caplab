#!/usr/bin/env python3
"""Step 1 of the review-instrument validation study (instruction 2026-09-07):
the criterion set from the striatum ledger, zero model spend.

Population: anchored-era production review runs (pass_id `review`, a
`materialized_base` input pin). Each run's verdict is read from its
review-ledger artifact (object store) and from the driver's review
gate_result; the two are reported side by side.

Strata are inspection candidates, never review-correctness judgments:

  gold          unavailable: no review-specific adjudication reader exists.
                An artifact acceptance gate cannot supply a gold label.
  silver-defect review cleared a change set AND a later integration_conflict
                names that change set as the losing pin with a conflict that
                is not "tree moved" (tree-moved is staleness of the base, a
                builder/timing event, reported separately and NOT counted),
                OR a later Principal cancellation_record on the request whose
                reason names a defect in that artifact.
  bronze-clear  review cleared a change set AND an application_record applied
                that change set AND no later acceptance fail, conflict, or
                cancellation names it.
  excluded      refused, then the same identity has an artifact admission
                after review closure and the reviewed version.

Usage: review_criterion_ledger_pass.py --ledger ledger.jsonl --out fresh-directory
Output must be fresh; existing exports are never overwritten.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import statistics
import sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from caplab.advisory import materialize as M  # noqa: E402
from caplab.advisory.review_response import response_error  # noqa: E402
from caplab.codex_events import parse_native_json  # noqa: E402

CLEAR = {"accept", "accept_with_findings"}
REFUSE = {"needs_revision", "reject"}
VERDICT_SELECTION = "latest-admitted-body-then-linked-review-gate/2"
BODY_REFERENCE_RESOLUTION = "sha256-address-or-hash-agreement/1"
DEFECT_WORDS = re.compile(r"defect|wrong|incorrect|false claim|fabricat|contradict|hollow|does not (deliver|implement|match)", re.I)
LIFECYCLE_FIELDS = {
    "pass_run_closed": ("outcome", "closure_source", "closure_reason", "deferral_reason",
                        "retry_at", "refusal_code", "detail", "failure", "capacity_observation_refs",
                        "submission_operation_key"),
    "submission_received": ("status", "attempt", "late", "operation_key", "expected_outputs",
                            "outputs", "semantic_exhaust", "evidence_objects", "submission_object"),
    "admission_decision": ("decision", "output", "submitted_state", "refusal_code", "detail",
                           "submission_operation_key"),
    "submission_refused": ("reason", "detail", "semantic_exhaust", "output_objects",
                           "evidence_objects", "submission_object"),
    "dispatch_lapse": ("dispatch_id", "basis", "observed", "sealed"),
}
NUMERIC_REFERENCE_PATHS = {
    **{kind: ("run_ref",) for kind in LIFECYCLE_FIELDS},
    "lane_binding": ("run_ref",),
    "scheduling_decision": ("run_ref",),
    "pass_run_opened": ("request_ref", "manifest.subject_pin.version_seq"),
    "artifact_admitted": ("produced_by_run",),
    "cancellation_record": ("request_ref",),
    "head_movement": ("to_version",),
    "gate_result": ("subject.version_seq",),
}


def _validate_reference_paths(payload: dict, paths: tuple[str, ...], location: str) -> None:
    """Validate borrowed reference fields without coercing or filling absence."""
    if not isinstance(payload, dict):
        raise ValueError(f"{location} must be an object")
    for path in paths:
        value = payload
        for part in path.split("."):
            if value is None:
                break
            if not isinstance(value, dict):
                raise ValueError(f"{location}.{path} requires object containers")
            value = value.get(part)
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(f"{location}.{path} must be a nonnegative integer or absent")


def T(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def artifact_class(identity: str) -> str:
    tail = identity.rsplit("/", 1)[-1]
    if tail == "change-set":
        return "change-set"
    return tail or "(unknown)"


def _artifact_version_key(pin: dict) -> tuple | None:
    if not isinstance(pin, dict):
        return None
    identity, version, content_hash = (pin.get(key) for key in ("identity", "version_seq", "content_hash"))
    if (not isinstance(identity, str) or not identity or type(version) is not int or version < 0
            or not isinstance(content_hash, str) or not content_hash):
        return None
    return identity, version, content_hash


def review_gate_attribution(event: dict, run: dict, admissions: dict) -> str:
    payload = event["payload"]
    subject = _artifact_version_key(payload.get("subject"))
    if subject is None or subject != _artifact_version_key(run):
        return "subject-mismatch-or-incomplete"
    evidence = payload.get("evidence") or []
    if not evidence or any(item != evidence[0] for item in evidence[1:]):
        return "not-one-distinct-evidence"
    item = evidence[0]
    pin = _artifact_version_key(item.get("pin"))
    if pin is None:
        return "evidence-pin-incomplete"
    admission = admissions.get(pin[1])
    if admission is None or not run["run"] < pin[1] < event["seq"]:
        return "evidence-admission-missing-or-out-of-order"
    artifact = admission["payload"]
    if (artifact.get("kind") != "review-ledger" or artifact.get("produced_by_run") != run["run"]
            or (item.get("producing_run") or {}).get("run_ref") != run["run"]
            or _artifact_version_key({**artifact, "version_seq": admission["seq"]}) != pin):
        return "evidence-admission-mismatch"
    edges = artifact.get("edges")
    claims = edges.get("evidences") if isinstance(edges, dict) else None
    claim = claims[0] if isinstance(claims, list) and claims and isinstance(claims[0], dict) else {}
    if _artifact_version_key(claim.get("subject")) != subject:
        return "admitted-subject-mismatch-or-incomplete"
    verdict = payload.get("verdict")
    if (not isinstance(verdict, str) or verdict not in CLEAR | REFUSE
            or payload.get("outcome") != ("pass" if verdict in CLEAR else "fail")
            or claim.get("claim") != "verdict:" + verdict):
        return "admitted-verdict-mismatch-or-incomplete"
    return "linked"


def review_body_reference(body: dict | None) -> tuple[str | None, str | None]:
    if body is None:
        return None, "missing-reference"
    if not isinstance(body, dict):
        return None, "invalid-reference"
    hashes = []
    if "address" in body:
        address = body["address"]
        if not isinstance(address, str) or not re.fullmatch(r"sha256/[0-9a-f]{64}", address):
            return None, "invalid-reference"
        hashes.append(address[7:])
    if "content_hash" in body:
        value = body["content_hash"]
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            return None, "invalid-reference"
        hashes.append(value)
    if not hashes:
        return None, "missing-reference"
    if len(set(hashes)) != 1:
        return None, "conflicting-reference"
    if (body.get("store", "object") != "object" or body.get("compression", "zstd") != "zstd"
            or ("size" in body and (type(body["size"]) is not int or body["size"] < 0))):
        return None, "invalid-reference"
    return hashes[0], None


def review_body_observation(event: dict, *, object_store: str = M.GRAPH_STORE) -> tuple[dict, dict | None]:
    payload = event["payload"]
    body = payload.get("body")
    ref, error = review_body_reference(body)
    observation = {"seq": event["seq"], "artifact": payload.get("identity"),
                   "body_hash": ref, "body_reference": body, "status": error or "missing-reference",
                   "verdict": None, "response_error": "body-not-read"}
    if error:
        return observation, None
    raw = M.store_object(ref, root=object_store)
    if raw is None:
        observation["status"] = "unavailable-or-unverified"
        return observation, None
    if "size" in body and len(raw) != body["size"]:
        observation["status"] = "body-size-mismatch"
        return observation, None
    try:
        doc = parse_native_json(raw.decode("utf-8"))
    except ValueError:
        observation.update(status="invalid-json", response_error="invalid-json")
        return observation, None
    observation["response_error"] = response_error(doc)
    if not isinstance(doc, dict):
        observation["status"] = "invalid-object"
        return observation, None
    observation.update(status="parsed-object", verdict=doc.get("verdict"))
    return observation, doc


def read_reviews(ledger_path: str, *, expected_prefix: dict | None = None, object_store: str | None = None):
    """Read an export without changing its records or admitting evidence."""
    by = collections.defaultdict(list)
    digest = hashlib.sha256()
    prefix_digest = hashlib.sha256()
    prefix_remaining = expected_prefix["byte_count"] if expected_prefix else 0
    snapshot = {"path": os.path.abspath(ledger_path), "events": 0,
                "last_seq": 0, "written_at": None,
                "object_store": os.path.abspath(os.path.expanduser(M.GRAPH_STORE if object_store is None else object_store))}
    needed = {"pass_run_opened", "pass_run_closed", "lane_binding",
              "scheduling_decision", "artifact_admitted", "gate_result",
              "integration_conflict", "application_record", "cancellation_record",
              "head_movement"}
    needed.update(LIFECYCLE_FIELDS)
    with open(ledger_path, "rb") as f:
        for line in f:
            digest.update(line)
            if prefix_remaining:
                prefix = line[:prefix_remaining]
                prefix_digest.update(prefix)
                prefix_remaining -= len(prefix)
            if not line.strip():
                continue
            e = parse_native_json(line.decode("utf-8"))
            if not isinstance(e, dict) or type(e.get("seq")) is not int or e["seq"] < 0:
                raise ValueError("ledger sequence must be a nonnegative integer")
            expected = snapshot["last_seq"] + 1 if snapshot["events"] else 0
            if e["seq"] != expected:
                raise ValueError(f"complete ledger required: expected sequence {expected}, got {e['seq']}")
            snapshot["events"] += 1
            snapshot["last_seq"] = e["seq"]
            snapshot["written_at"] = e["written_at"]
            if e["type"] in needed:
                payload = e.get("payload")
                location = f"event {e['seq']} payload"
                _validate_reference_paths(payload, NUMERIC_REFERENCE_PATHS.get(e["type"], ()), location)
                if e["type"] == "gate_result" and payload.get("gate_class") == "review":
                    evidence = payload.get("evidence")
                    if evidence is not None:
                        if not isinstance(evidence, list):
                            raise ValueError(f"{location}.evidence must be an array or absent")
                        for index, item in enumerate(evidence):
                            _validate_reference_paths(item, ("producing_run.run_ref", "pin.version_seq"),
                                                      f"{location}.evidence[{index}]")
                by[e["type"]].append(e)
    if not snapshot["events"]:
        raise ValueError("ledger export is empty")
    if expected_prefix and (prefix_remaining or prefix_digest.hexdigest() != expected_prefix["sha256"]):
        raise ValueError("ledger does not extend the verified baseline export")
    snapshot["sha256"] = digest.hexdigest()

    # --- population: anchored review runs
    runs = {}
    for e in by["pass_run_opened"]:
        p = e["payload"]; m = p.get("manifest") or {}
        pins = m.get("input_pins") or []
        if p.get("pass_id") != "review":
            continue
        mb = next((x["content_hash"] for x in pins if x.get("role") == "materialized_base"), None)
        if not mb:
            continue
        sp = m.get("subject_pin") or {}
        env = m.get("environment") or []
        contract = next((x["hash"] for x in env if x.get("kind") == "pass-contract"), None)
        runs[e["seq"]] = {
            "run": e["seq"], "opened": e["written_at"], "identity": sp.get("identity"),
            "content_hash": sp.get("content_hash"), "version_seq": sp.get("version_seq"),
            "class": artifact_class(sp.get("identity") or ""),
            "materialized_base": mb,
            "base_pin": next((x["content_hash"] for x in pins if x.get("role") == "base"), None),
            "contract_hash": contract, "contract_version": p.get("contract_version"),
            "prompt_assets": m.get("prompt_asset_hashes") or [],
            "request_ref": p.get("request_ref"),
        }
    closed = {e["payload"].get("run_ref"): e for e in by["pass_run_closed"]}
    lane = {e["payload"].get("run_ref"): e["payload"].get("backend_id") for e in by["lane_binding"]}
    sched = {e["payload"].get("run_ref"): e["payload"].get("backend_id") for e in by["scheduling_decision"]}
    for seq, r in runs.items():
        r["backend"] = lane.get(seq) or sched.get(seq) or "(unbound)"
        c = closed.get(seq)
        r["outcome"] = c["payload"].get("outcome") if c else None
        r["closed"] = c["written_at"] if c else None
        r["closed_seq"] = c["seq"] if c else None
        r["wall_s"] = (T(c["written_at"]) - T(r["opened"])).total_seconds() if c else None

    for kind, fields in LIFECYCLE_FIELDS.items():
        for event in by[kind]:
            payload = event["payload"]
            run = payload.get("run_ref")
            if run in runs:
                runs[run].setdefault("lifecycle_observations", []).append({
                    "seq": event["seq"], "type": kind, "at": event["written_at"],
                    "schema_version": event.get("schema_version"),
                    "detail": {key: payload[key] for key in fields if key in payload},
                })
    for r in runs.values():
        r["lifecycle_observations"] = sorted(r.get("lifecycle_observations", []), key=lambda e: e["seq"])

    # --- verdicts: review-ledger bodies and review gate results
    for e in by["artifact_admitted"]:
        p = e["payload"]
        if p.get("kind") != "review-ledger" or p.get("produced_by_run") not in runs:
            continue
        observation, doc = review_body_observation(e, object_store=snapshot["object_store"])
        r = runs[p["produced_by_run"]]
        r.setdefault("review_body_observations", []).append(observation)
        r["review_artifact"] = p.get("identity")
        r["review_body_hash"] = observation["body_hash"]
        # Last-admission selection must not attach an earlier verdict to the
        # newer body's locator when the new body cannot be read.
        for key in ("verdict", "findings", "summary"):
            r.pop(key, None)
        if doc is not None:
            r["verdict"] = doc.get("verdict") if isinstance(doc.get("verdict"), str) else None
            findings = doc.get("findings")
            r["findings"] = []
            for finding in findings if isinstance(findings, list) else []:
                if isinstance(finding, dict):
                    text = finding.get("text") or finding.get("finding") or ""
                    r["findings"].append({"anchor": finding.get("element_anchor") or finding.get("anchor"),
                                          "text": text[:300] if isinstance(text, str) else ""})
            summary = doc.get("summary")
            r["summary"] = summary[:400] if isinstance(summary, str) else ""
    admissions = {e["seq"]: e for e in by["artifact_admitted"]}
    for e in by["gate_result"]:
        p = e["payload"]
        if p.get("gate_class") != "review":
            continue
        seen = set()
        for ev in p.get("evidence") or []:
            run = (ev.get("producing_run") or {}).get("run_ref")
            if run in runs and run not in seen:
                seen.add(run)
                outcome = p.get("outcome")
                attribution = review_gate_attribution(e, runs[run], admissions)
                runs[run].setdefault("review_gate_observations", []).append(
                    {"seq": e["seq"], "schema_version": e.get("schema_version"), "outcome": outcome,
                     "verdict": p.get("verdict"), "subject": p.get("subject"), "evidence": p.get("evidence"),
                     "attribution": attribution})
                runs[run]["review_gate"] = outcome if attribution == "linked" and isinstance(outcome, str) else None
                runs[run]["review_gate_seq"] = e["seq"]
                runs[run]["review_gate_evidence_seq"] = ev["pin"]["version_seq"] if attribution == "linked" else None

    def cleared(r):
        v = r.get("verdict")
        if v in CLEAR:
            return True
        if v in REFUSE:
            return False
        return {"pass": True, "fail": False}.get(r.get("review_gate"))

    # --- Principal acceptance rulings, by artifact version
    acceptance = collections.defaultdict(list)
    for e in by["gate_result"]:
        p = e["payload"]
        if p.get("gate_class") != "acceptance":
            continue
        if (p.get("authority") or {}).get("kind") != "principal":
            continue
        subject = p.get("subject") or {}
        acceptance[_artifact_version_key(subject)].append({"seq": e["seq"], "at": e["written_at"], "outcome": p.get("outcome"),
            "detail": (p.get("detail") or "")[:600], "identity": subject.get("identity"),
            "version_seq": subject.get("version_seq"), "content_hash": subject.get("content_hash")})
    # --- integration conflicts and applications, by change-set hash
    conflicts = collections.defaultdict(list)
    for e in by["integration_conflict"]:
        p = e["payload"]
        h = (p.get("losing_change_set_pin") or {}).get("content_hash")
        d = p.get("detail") or ""
        kind = ("tree-moved" if "tree moved" in d else
                "anchored-delete-named-later-version" if "deletes over an anchored base" in d else
                "declares-vs-yields" if "declares" in d else
                "link-check" if p.get("conflict_class") == "link_check_failure" else "other")
        conflicts[h].append({"seq": e["seq"], "at": e["written_at"], "kind": kind, "detail": d[:300],
                             "conflicting_paths": p.get("conflicting_paths")})
    applied = collections.defaultdict(list)
    for e in by["application_record"]:
        p = e["payload"]
        applied[(p.get("change_set") or {}).get("content_hash")].append({"seq": e["seq"], "at": e["written_at"]})
    # --- Principal cancellations with defect wording, by request
    cancellations = collections.defaultdict(list)
    for e in by["cancellation_record"]:
        p = e["payload"]
        if (p.get("issuer") or {}).get("kind") != "principal":
            continue
        cancellations[p.get("request_ref")].append({"seq": e["seq"], "at": e["written_at"], "reason": (p.get("reason") or "")[:400],
                                                    "defect_words": bool(DEFECT_WORDS.search(p.get("reason") or ""))})
    # Version references do not establish that an artifact was admitted.
    versions = collections.defaultdict(list)
    for e in by["artifact_admitted"]:
        p = e["payload"]
        identity = p.get("identity")
        if isinstance(identity, str) and identity:
            versions[identity].append({"seq": e["seq"], "at": e["written_at"],
                                       "identity": identity, "content_hash": p.get("content_hash")})

    # --- strata
    strata = collections.defaultdict(list)
    tree_moved_after_clear = []

    def post_close(index, key, closed_seq):
        if key is None or key == "" or closed_seq is None:
            return []
        return [e for e in index.get(key, []) if e["seq"] > closed_seq]

    for seq, r in sorted(runs.items()):
        # Acceptance and revision observations follow closure in ledger order.
        # Other legacy candidate predicates below retain their original scope.
        r["post_close_events"] = {
            "applied": post_close(applied, r["content_hash"], r["closed_seq"]),
            "conflicts": [e for e in post_close(conflicts, r["content_hash"], r["closed_seq"])
                          if e["kind"] != "tree-moved"],
            "cancellations_with_defect_words": [e for e in post_close(cancellations, r["request_ref"], r["closed_seq"])
                                               if e["defect_words"]],
        }
        r["post_close_version_observations"] = [
            e for e in post_close(versions, r["identity"], r["closed_seq"])
            if r["version_seq"] is not None and e["seq"] > r["version_seq"]]
        r["post_close_acceptance_observations"] = post_close(acceptance, _artifact_version_key(r), r["closed_seq"])
        later_versions = [e["seq"] for e in r["post_close_version_observations"]]
        r["post_close_versions"] = later_versions
        c = cleared(r)
        r["cleared"] = c
        if c is None:
            strata["no-verdict"].append(r); continue
        later_acc = r["post_close_acceptance_observations"]
        acc_fail = [a for a in later_acc if a["outcome"] == "fail"]
        acc_pass = [a for a in later_acc if a["outcome"] == "pass"]
        later_conf = [x for x in conflicts.get(r["content_hash"], []) if x["at"] > r["opened"]]
        real_conf = [x for x in later_conf if x["kind"] != "tree-moved"]
        moved = [x for x in later_conf if x["kind"] == "tree-moved"]
        later_app = [x for x in applied.get(r["content_hash"], []) if x["at"] > r["opened"]]
        canc = [x for x in cancellations.get(r["request_ref"], []) if x["at"] > r["opened"] and x["defect_words"]]
        r["later"] = {"acceptance_fail": acc_fail, "acceptance_pass": acc_pass, "conflicts": real_conf,
                      "tree_moved": len(moved), "applied": later_app, "cancellations_with_defect_words": canc,
                      "later_versions": later_versions[:5]}
        if c and (real_conf or canc):
            strata["silver-defect"].append(r)
        elif c and later_app and not acc_fail and not later_conf and not canc:
            strata["bronze-clear"].append(r)
        elif (not c) and later_versions:
            strata["excluded-refused-then-revised"].append(r)
        elif c and moved and not later_app:
            strata["unlabelled-cleared-tree-moved"].append(r); tree_moved_after_clear.append(r)
        elif c:
            strata["unlabelled-cleared-no-later-event"].append(r)
        else:
            strata["unlabelled-refused-no-later-event"].append(r)

    def table(rows, key):
        return dict(collections.Counter(key(r) for r in rows).most_common())
    report = {"record": "caplab-review-criterion-candidates/2",
              "snapshot": snapshot,
              "gold_outcomes": "unavailable: no review-specific adjudication reader; artifact acceptance is not review correctness",
              "verdict_selection": VERDICT_SELECTION,
              "body_reference_resolution": BODY_REFERENCE_RESOLUTION,
              "interpretation": "Inspection candidates only; no ranking, scoring or adjudicated correctness labels.",
              "acceptance_observation_linkage": "gate-subject-pin-after-review-closure/2",
              "revision_evidence": "artifact-admission-after-review-closure/1",
              "population": len(runs), "strata": {}, "contracts": {}, "wall_clock_median_s": {}, "prompt_assets_retained": sum(1 for r in runs.values() if r["prompt_assets"]),
              "dispatch_dirs_retained": 0}
    for s, rows in strata.items():
        report["strata"][s] = {"n": len(rows),
                               "by_class": table(rows, lambda r: r["class"]),
                               "by_binding": table(rows, lambda r: r["backend"]),
                               "by_era": table(rows, lambda r: r["opened"][:7]),
                               "distinct_artifact_versions": len({(r["identity"], r["version_seq"]) for r in rows})}
    report["contracts"] = table(list(runs.values()), lambda r: f"{r['contract_hash']}@v{r['contract_version']}")
    wall = collections.defaultdict(list)
    for r in runs.values():
        if r.get("wall_s") and r.get("outcome") in ("submitted", "submitted_partial"):
            wall[r["backend"]].append(r["wall_s"])
    report["wall_clock_median_s"] = {b: {"median": round(statistics.median(v)), "n": len(v)} for b, v in sorted(wall.items()) if len(v) >= 5}
    report["verdict_sources"] = {"review_ledger_body": sum(1 for r in runs.values() if r.get("verdict")),
                                 "review_gate_only": sum(1 for r in runs.values() if not r.get("verdict") and r.get("review_gate")),
                                 "none": sum(1 for r in runs.values() if not r.get("verdict") and not r.get("review_gate"))}
    report["conflict_kinds_all"] = dict(collections.Counter(x["kind"] for v in conflicts.values() for x in v))
    report["principal_acceptance_rulings"] = {"total": sum(len(v) for v in acceptance.values()),
                                              "by_outcome": dict(collections.Counter(a["outcome"] for v in acceptance.values() for a in v)),
                                              "by_class": dict(collections.Counter(artifact_class(a["identity"] or "") for v in acceptance.values() for a in v))}
    return snapshot, report, runs, strata


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--object-store", help="Graph-store root containing objects/sha256; defaults to the local Striatum graph")
    ap.add_argument("--out", default=os.path.join(ROOT, "advisory", "criterion"), help="Fresh output directory; existing paths refuse")
    args = ap.parse_args()
    snapshot, report, runs, strata = read_reviews(args.ledger, object_store=args.object_store)
    os.makedirs(args.out, exist_ok=False)
    with open(os.path.join(args.out, "review-criterion-summary.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, sort_keys=True)
    with open(os.path.join(args.out, "review-criterion-cases.jsonl"), "w", encoding="utf-8") as f:
        for s in ("silver-defect", "bronze-clear"):
            for r in strata.get(s, []):
                f.write(json.dumps({"stratum": s, **{k: v for k, v in r.items() if k not in {"prompt_assets", "closed", "closed_seq", "post_close_versions", "post_close_version_observations", "post_close_events", "review_body_observations", "review_gate_observations", "lifecycle_observations"}}}, ensure_ascii=False, sort_keys=True) + "\n")
    with open(os.path.join(args.out, "review-acceptance-observations.jsonl"), "w", encoding="utf-8") as f:
        for r in runs.values():
            for observation in r["post_close_acceptance_observations"]:
                f.write(json.dumps({"record": "caplab-review-acceptance-observation/1",
                    "ledger_sha256": snapshot["sha256"], "review_run": r["run"],
                    "subject": {key: r[key] for key in ("identity", "version_seq", "content_hash")},
                    "acceptance": observation,
                    "interpretation": "Artifact acceptance observation, not an adjudication of this review."},
                    ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "wall_clock_median_s"}, indent=1)[:6000])
    print("wall clock", json.dumps(report["wall_clock_median_s"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
