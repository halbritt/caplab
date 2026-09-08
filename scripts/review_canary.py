#!/usr/bin/env python3
"""Report production review observations without scores or placement decisions."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
import statistics

from review_criterion_ledger_pass import CLEAR, REFUSE, T, read_reviews


def load_baseline(path: Path) -> tuple[dict, dict, int]:
    """Bind a follow-up to the retained export and fixed window of a report."""
    raw = Path(path).read_bytes()
    report = json.loads(raw)
    if not isinstance(report, dict) or report.get("record") != "caplab-review-canary/1":
        raise ValueError("baseline must be a production review report")
    snapshot = report.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("baseline has no source snapshot")
    for key in ("events", "last_seq"):
        if type(snapshot.get(key)) is not int or snapshot[key] < 0:
            raise ValueError(f"invalid baseline snapshot {key}")
    after_run = report.get("after_run")
    if type(after_run) is not int or not 0 <= after_run <= snapshot["last_seq"]:
        raise ValueError("invalid baseline population cutoff")
    mode = report.get("mode")
    if (not isinstance(mode, str) or mode not in {"since-cutoff", "retrospective-baseline"}
            or (mode == "retrospective-baseline" and after_run != 0)):
        raise ValueError("baseline mode contradicts its population cutoff")
    source = snapshot.get("path")
    if not isinstance(source, str) or not Path(source).is_absolute():
        raise ValueError("baseline must name its retained export by absolute path")
    digest = hashlib.sha256()
    events = size = 0
    last = None
    with Path(source).open("rb") as export:
        for line in export:
            digest.update(line)
            size += len(line)
            if line.strip():
                events += 1
                last = line
    if not last or digest.hexdigest() != snapshot.get("sha256"):
        raise ValueError("baseline export no longer matches its recorded SHA-256")
    last_event = json.loads(last)
    if (events != snapshot["events"] or not isinstance(last_event, dict)
            or last_event.get("seq") != snapshot["last_seq"]):
        raise ValueError("baseline snapshot counts do not match its retained export")
    prefix = {"byte_count": size, "sha256": digest.hexdigest()}
    reference = {"path": str(Path(path).resolve()), "report_sha256": hashlib.sha256(raw).hexdigest(),
                 "ledger_sha256": prefix["sha256"], "last_seq": snapshot["last_seq"],
                 "prefix_bytes": size}
    return reference, prefix, after_run if mode == "since-cutoff" else snapshot["last_seq"]


def observe_run(run: dict) -> dict:
    observed = {key: run.get(key) for key in (
        "run", "opened", "closed", "backend", "identity", "version_seq",
        "content_hash", "class", "materialized_base", "contract_hash",
        "request_ref", "review_artifact", "review_body_hash", "verdict",
        "review_gate", "review_gate_seq", "outcome", "wall_s")}
    observed["decision"] = {True: "cleared", False: "refused", None: "unknown"}[run["cleared"]]
    observed["verdict_source"] = ("body" if run.get("verdict") in CLEAR | REFUSE else
                                  "gate-only" if run.get("review_gate") in {"pass", "fail"} else "missing")
    later = run.get("later", {})
    # Downstream joins nominate cases. They do not identify a wrong verdict.
    closed = T(run["closed"]) if run.get("closed") else None
    observed["applications"] = [e for e in later.get("applied", [])
                                if closed is not None and T(e["at"]) > closed]
    observed["conflicts"] = [e for e in later.get("conflicts", [])
                             if closed is not None and T(e["at"]) > closed]
    observed["request_cancellations"] = [e for e in later.get("cancellations_with_defect_words", [])
                                         if closed is not None and T(e["at"]) > closed]
    observed["later_versions"] = run.get("post_close_versions", [])
    return observed


def summarize(snapshot: dict, runs: dict, after_run: int) -> dict:
    if after_run < 0 or after_run > snapshot["last_seq"]:
        raise ValueError("--after-run must be between zero and the snapshot's last sequence")
    selected = [observe_run(r) for seq, r in sorted(runs.items())
                if seq > after_run and r["class"] in {"change-set", "repo-doc"}]
    grouped = collections.defaultdict(list)
    for row in selected:
        grouped[row["backend"]].append(row)
    reviewers = []
    for backend, rows in sorted(grouped.items()):
        durations = [r["wall_s"] for r in rows if r["wall_s"] is not None and r["wall_s"] >= 0]
        clear = [r for r in rows if r["decision"] == "cleared"]
        reviewers.append({
            "reviewer": backend, "runs": len(rows),
            "artifact_identities": len({r["identity"] for r in rows}),
            "decisions": dict(collections.Counter(r["decision"] for r in rows)),
            "verdict_sources": dict(collections.Counter(r["verdict_source"] for r in rows)),
            "run_outcomes": dict(collections.Counter(r["outcome"] or "open" for r in rows)),
            "median_closed_wall_s": statistics.median(durations) if durations else None,
            "closed_wall_n": len(durations),
            "clearances_with_application": sum(bool(r["applications"]) for r in clear),
            "clearances_with_conflict": sum(bool(r["conflicts"]) for r in clear),
            "clearances_with_request_cancellation": sum(bool(r["request_cancellations"]) for r in clear),
            "distinct_cancellation_records": sorted({e["seq"] for r in clear for e in r["request_cancellations"]}),
            "refusals_with_later_version": sum(r["decision"] == "refused" and bool(r["later_versions"]) for r in rows),
        })
    return {"record": "caplab-review-canary/1", "snapshot": snapshot,
            "after_run": after_run, "mode": "since-cutoff" if after_run else "retrospective-baseline",
            "population": len(selected), "reviewers": reviewers, "reviews": selected,
            "placement": "frozen", "gold_outcomes": "unavailable: no review-specific re-ruling event reader",
            "interpretation": "Report only. Downstream events are inspection candidates, not correctness labels."}


def render(report: dict) -> str:
    snapshot = report["snapshot"]
    unknown = [r for r in report["reviews"] if r["decision"] == "unknown"]
    unknown_outcomes = collections.Counter(r["outcome"] or "open" for r in unknown)
    lines = ["# CAPLAB production review report", "",
             "Use this report to find reviews to inspect and gaps in retained evidence.",
             "It cannot tell you which reviewer is more accurate. Placement remains frozen.", "",
             f"Snapshot through ledger event {snapshot['last_seq']} ({snapshot['written_at']}).",
             f"Mode: {report['mode']}. Review runs opened after event {report['after_run']}.",
             f"Population: {report['population']} anchored change-set or repo-doc review runs.",
             "All later events in this snapshot are considered. Open runs remain in the denominator.", "",
             f"Reviews without a retained verdict: {len(unknown)}. Run outcomes: " +
             (", ".join(f"{k} {v}" for k, v in sorted(unknown_outcomes.items())) or "none") + ".",
             "A missing verdict can follow cancellation, a partial submission, or an error. It is not a wrong answer.", "",
             "Reviewer names are ledger backend labels, not verified exact CAPLAB Bindings.",
             "Rows use alphabetical order. Durations include all closed outcomes and exclude open runs.", "",
             "| Reviewer | Runs | Cleared | Refused | Unknown | Missing body | Median closed seconds (n) |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for row in report["reviewers"]:
        d = row["decisions"]
        missing = row["runs"] - row["verdict_sources"].get("body", 0)
        duration = row["median_closed_wall_s"]
        timing = f"{duration:.0f} ({row['closed_wall_n']})" if duration is not None else "unavailable (0)"
        lines.append(f"| {escape(row['reviewer'])} | {row['runs']} | {d.get('cleared', 0)} | "
                     f"{d.get('refused', 0)} | {d.get('unknown', 0)} | {missing} | {timing} |")
    lines.extend(["", "Downstream events identify work to inspect:", "",
                  "| Reviewer | Clears then applied | Clears then conflict | Clears with request cancellation | Distinct cancellations | Refusals then revised |",
                  "|---|---:|---:|---:|---:|---:|"])
    for row in report["reviewers"]:
        lines.append(f"| {escape(row['reviewer'])} | {row['clearances_with_application']} | "
                     f"{row['clearances_with_conflict']} | {row['clearances_with_request_cancellation']} | "
                     f"{len(row['distinct_cancellation_records'])} | {row['refusals_with_later_version']} |")
    lines.extend(["", "Applications and conflicts join by content hash. Cancellations join by request and defect wording.",
                  "One cancellation can affect many reviews. These columns overlap and do not count independent defects.",
                  "An application does not prove correctness. A later revision does not prove a refusal was correct.",
                  "Unknown outcomes and short follow-up can hide later problems. No adjudicated outcome score is computed.", "",
                  "Inspection candidates, grouped by downstream event (all linked runs are in report.json):", ""])
    candidates = [r for r in report["reviews"] if r["decision"] == "cleared"
                  and (r["conflicts"] or r["request_cancellations"])]
    incidents = {}
    for row in candidates:
        for kind, events in (("conflict", row["conflicts"]), ("request cancellation", row["request_cancellations"])):
            for event in events:
                incident = incidents.setdefault(event["seq"], {"kind": kind, "runs": set(), "identities": set()})
                incident["runs"].add(row["run"])
                incident["identities"].add(row["identity"])
    for seq, incident in sorted(incidents.items()):
        lines.append(f"- Event {seq} ({incident['kind']}): {len(incident['runs'])} linked cleared reviews, "
                     f"{len(incident['identities'])} artifact identities. Example review: {min(incident['runs'])}.")
    if not candidates:
        lines.append("No matching candidates in this window. This does not establish that reviews were correct.")
    lines.extend(["", f"Input SHA-256: `{snapshot['sha256']}`.",
                  "The JSON report retains every selected run, including missing verdicts and open runs.", ""])
    if report.get("baseline"):
        baseline = report["baseline"]
        lines.extend([f"Verified baseline ledger prefix through event {baseline['last_seq']}.",
                      f"Baseline report SHA-256: `{baseline['report_sha256']}`.", ""])
    return "\n".join(lines)


def escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, help="complete Striatum JSONL ledger export")
    window = parser.add_mutually_exclusive_group()
    window.add_argument("--after-run", type=int, default=0, help="exclusive run-opening sequence cutoff; keep fixed for follow-up")
    window.add_argument("--baseline-report", type=Path, help="prior report.json; verify its retained export and preserve its population cutoff")
    parser.add_argument("--out", required=True, help="new output directory; existing reports are never overwritten")
    args = parser.parse_args()
    target = Path(args.out)
    if target.exists():
        parser.error("--out already exists; choose a new report directory")
    baseline, prefix, after_run = None, None, args.after_run
    try:
        if args.baseline_report:
            baseline, prefix, after_run = load_baseline(args.baseline_report)
        snapshot, _, runs, _ = read_reviews(args.ledger, expected_prefix=prefix)
        report = summarize(snapshot, runs, after_run)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    if baseline:
        report["baseline"] = baseline
        report["mode"] = "since-cutoff"
    target.mkdir(parents=True, exist_ok=False)
    (target / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (target / "report.md").write_text(render(report), encoding="utf-8")
    print(f"{target / 'report.md'}: {report['population']} review runs; report only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
