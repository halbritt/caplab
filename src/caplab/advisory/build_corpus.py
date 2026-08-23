"""Harvest the build construct from striatum's own ledger.

Build is the one producer pass with a mechanical, non-circular label: its
output is a change set, and `packet-checks` (format/compile/test) passes or
does not, with no judgment in the loop. Review capability had to manufacture
ground truth (Revbench); build capability is already labelled at production
scale on the striatum ledger — thousands of backend-attributed runs.

This module defines CAPLAB's first build construct and harvests it:

  **construct** `build.packet_delivery/1`
  - `packet_checks_pass_rate` — of the mechanically-gated delivery attempts,
    the share that passed `packet-checks`.
  - `delivery_rate` — of the runs the backend was actually given (capacity
    deferrals and dispatch refusals excluded), the share closed `submitted`.

Two confounds are excluded, never scored, and always counted:

  - **tree-moved churn**: a `packet-checks` failure whose detail carries the
    `tree moved: rebase-style revision required` marker failed because an
    operator commit moved the anchored base under the in-flight build. That
    outcome describes the repository's churn, not the builder.
  - **capacity deferrals**: closures via `scheduling_deferral` or
    `dispatch_refusal` produced nothing; scoring them against the builder
    would measure the scheduler.

Custody is `striatum-production`: the evidence was executed and labelled by
striatum's own production loop; CAPLAB harvested and scored it. That is a
third custody class beside `historical-seed` and `caplab-advisory`, and
consumers weight it themselves.

The ledger read is guarded: `striatum ledger cat` can exit 0 with an empty
file under lock contention, so a harvest refuses inputs that are implausibly
small rather than reporting an empty fleet.
"""

from __future__ import annotations

import hashlib
import json

from .wilson import wilson

BUILD_CONSTRUCT = "build.packet_delivery/1"
TREE_MOVED_MARKER = "tree moved: rebase-style revision required"
EXCLUDED_CLOSURE_SOURCES = {"scheduling_deferral", "dispatch_refusal"}
MIN_LEDGER_LINES = 200_000


def harvest_build_corpus(events: list[dict]) -> dict:
    """Per-backend build outcomes from raw ledger events.

    Attribution: `lane_binding.payload.run_ref` names the run a backend was
    bound to; submissions reference the run; `gate_result` records reference
    the submission through `causes`. Gate results are followed one hop past
    the run's directly-related events, which is where admission places them.
    """
    build_runs: set[int] = set()
    for e in events:
        if (e.get("type") == "pass_run_opened"
                and e.get("payload", {}).get("pass_id") == "build"):
            build_runs.add(e["seq"])
    if not build_runs:
        return {}

    backend_of_run: dict[int, str] = {}
    run_of_seq: dict[int, int] = {}
    for e in events:
        payload = e.get("payload", {})
        run = payload.get("run_ref")
        touches = set(e.get("causes") or [])
        if run in build_runs:
            touches.add(run)
        else:
            touches &= build_runs
            run = next(iter(touches), None)
        if run is None:
            continue
        run_of_seq[e["seq"]] = run
        if e.get("type") == "lane_binding":
            backend_of_run[run] = payload.get("backend_id")

    corpus: dict[str, dict] = {}

    def cell(backend):
        return corpus.setdefault(backend, {
            "packet_checks": {"pass": 0, "fail": 0, "excluded_tree_moved": 0},
            "deliveries": {"submitted": 0, "submitted_partial": 0,
                           "submitted_late": 0, "abandoned": 0, "error": 0,
                           "excluded_deferrals": 0},
        })

    for e in events:
        payload = e.get("payload", {})
        if (e.get("type") == "gate_result"
                and payload.get("gate_id") == "packet-checks"):
            run = None
            for cause in e.get("causes") or []:
                run = run_of_seq.get(cause)
                if run is not None:
                    break
            backend = backend_of_run.get(run)
            if backend is None:
                continue
            pc = cell(backend)["packet_checks"]
            if TREE_MOVED_MARKER in json.dumps(payload):
                pc["excluded_tree_moved"] += 1
            elif payload.get("outcome") == "pass":
                pc["pass"] += 1
            else:
                pc["fail"] += 1
        elif e.get("type") == "pass_run_closed":
            run = payload.get("run_ref")
            backend = backend_of_run.get(run)
            if backend is None or run not in build_runs:
                continue
            d = cell(backend)["deliveries"]
            if payload.get("closure_source") in EXCLUDED_CLOSURE_SOURCES:
                d["excluded_deferrals"] += 1
            else:
                outcome = payload.get("outcome") or "error"
                d[outcome] = d.get(outcome, 0) + 1

    return corpus


def build_claims(corpus: dict, as_of: str, ledger_lines: int,
                 ledger_sha256: str | None = None) -> list[dict]:
    """quartermaster-scored-claim/1 records for the build construct."""
    if ledger_lines < MIN_LEDGER_LINES:
        raise ValueError(
            f"ledger dump holds {ledger_lines} lines, below the "
            f"{MIN_LEDGER_LINES} floor — `ledger cat` can return empty under "
            f"lock contention, and an empty read must not become claims")
    claims = []
    for backend, data in sorted(corpus.items()):
        pc = data["packet_checks"]
        gated = pc["pass"] + pc["fail"]
        deliveries = data["deliveries"]
        given = sum(v for k, v in deliveries.items()
                    if k != "excluded_deferrals")
        delivered = (deliveries["submitted"] + deliveries["submitted_late"])
        metrics = {}
        if gated:
            lo, hi = wilson(pc["pass"], gated)
            metrics["packet_checks_pass_rate"] = {
                "value": pc["pass"] / gated, "denominator": gated,
                "ci95": [lo, hi]}
        if given:
            lo, hi = wilson(delivered, given)
            metrics["delivery_rate"] = {
                "value": delivered / given, "denominator": given,
                "ci95": [lo, hi]}
        if not metrics:
            continue
        # The projection's sample floor reads the n_pairs metric; the gated
        # attempt count is this construct's sample size.
        metrics["n_pairs"] = {"value": gated}
        body = {
            "record": "quartermaster-scored-claim/1",
            "construct": BUILD_CONSTRUCT,
            "subject": {"source_id": backend, "match": "declared-name"},
            "custody": "striatum-production",
            "as_of": as_of,
            "metrics": metrics,
            "evidence": [{
                "kind": "striatum-ledger-harvest",
                "ledger_lines": ledger_lines,
                "ledger_sha256": ledger_sha256,
                "pass_id": "build",
                "gate_id": "packet-checks",
            }],
            "notes": [
                "striatum-production custody: executed and labelled by "
                "striatum's production loop; harvested and scored by CAPLAB "
                "(caplab.advisory.build_corpus).",
                f"packet-checks failures carrying the '{TREE_MOVED_MARKER}' "
                f"marker are excluded as base churn, not builder failures "
                f"({pc['excluded_tree_moved']} excluded for this subject).",
                f"capacity deferrals and dispatch refusals leave the "
                f"delivery denominator "
                f"({deliveries['excluded_deferrals']} excluded).",
                "The mechanical label is packet-checks (format/compile/test) "
                "plus admission; no model judgment is in the labelling loop.",
            ],
        }
        payload = json.dumps(body, sort_keys=True, ensure_ascii=False)
        body["claim_id"] = "qc-" + hashlib.sha256(
            payload.encode()).hexdigest()[:16]
        claims.append(body)
    return claims


# --------------------------------------------------------------- Tier A
# Tier A of the capability-measurement program (Principal, 2026-08-23):
# every label here is mechanical or a closure outcome — no model judgment
# in the loop. Tier B (independent-family review/acceptance verdicts) is a
# different label class and is handled separately.

PASS_CONSTRUCTS = {
    "build": BUILD_CONSTRUCT,           # richer claim via harvest_build_corpus
    "implementation-planning": "planning.delivery/1",
    "design-convergence": "design.delivery/1",
    "proposal-generation": "proposal.delivery/1",
    "packetization": "packetization.delivery/1",
    "integration": "integration.delivery/1",
    "verification": "verification.delivery/1",
    "review": "review_pass.delivery/1",
    "intent-capture": "intent.delivery/1",
}
RECEIPT_CONSTRUCT = "harness.receipt_compliance/1"
DELIVERED_OUTCOMES = ("submitted", "submitted_late")


def _attribution(events: list[dict], pass_ids: set[str] | None = None):
    """(runs, backend_of_run, run_of_seq) for the selected pass runs."""
    runs = {}
    for e in events:
        if e.get("type") == "pass_run_opened":
            pid = e.get("payload", {}).get("pass_id")
            if pass_ids is None or pid in pass_ids:
                runs[e["seq"]] = pid
    backend_of_run: dict[int, str] = {}
    run_of_seq: dict[int, int] = {}
    for e in events:
        payload = e.get("payload", {})
        run = payload.get("run_ref")
        touches = set(e.get("causes") or [])
        if run in runs:
            touches.add(run)
        else:
            touches &= set(runs)
            run = next(iter(touches), None)
        if run is None:
            continue
        run_of_seq[e["seq"]] = run
        if e.get("type") == "lane_binding":
            backend_of_run[run] = payload.get("backend_id")
    return runs, backend_of_run, run_of_seq


def harvest_deliveries(events: list[dict]) -> dict:
    """{pass_id: {backend: delivery counters}} for every pass type."""
    runs, backend_of_run, _ = _attribution(events)
    out: dict = {}
    for e in events:
        if e.get("type") != "pass_run_closed":
            continue
        payload = e.get("payload", {})
        run = payload.get("run_ref")
        pid = runs.get(run)
        backend = backend_of_run.get(run)
        if pid is None or backend is None:
            continue
        cell = out.setdefault(pid, {}).setdefault(
            backend, {"excluded_deferrals": 0})
        if payload.get("closure_source") in EXCLUDED_CLOSURE_SOURCES:
            cell["excluded_deferrals"] += 1
        else:
            outcome = payload.get("outcome") or "error"
            cell[outcome] = cell.get(outcome, 0) + 1
    return out


def harvest_receipt_compliance(events: list[dict]) -> dict:
    """{backend: {pass, fail}} over every receipt-checks gate result.

    Receipts are emitted for runs of every pass type; their shape check is
    the mechanical label for harness protocol fidelity.
    """
    _, backend_of_run, run_of_seq = _attribution(events)
    out: dict = {}
    for e in events:
        payload = e.get("payload", {})
        if (e.get("type") != "gate_result"
                or payload.get("gate_id") != "receipt-checks"):
            continue
        run = None
        for cause in e.get("causes") or []:
            run = run_of_seq.get(cause)
            if run is not None:
                break
        backend = backend_of_run.get(run)
        if backend is None:
            continue
        cell = out.setdefault(backend, {"pass": 0, "fail": 0})
        cell["pass" if payload.get("outcome") == "pass" else "fail"] += 1
    return out


def harvest_gate(events: list[dict], pass_id: str, gate_id: str) -> dict:
    """{backend: {pass, fail}} for one gate on one pass type."""
    runs, backend_of_run, run_of_seq = _attribution(events, {pass_id})
    out: dict = {}
    for e in events:
        payload = e.get("payload", {})
        if (e.get("type") != "gate_result"
                or payload.get("gate_id") != gate_id):
            continue
        run = None
        for cause in e.get("causes") or []:
            run = run_of_seq.get(cause)
            if run is not None:
                break
        backend = backend_of_run.get(run)
        if backend is None:
            continue
        cell = out.setdefault(backend, {"pass": 0, "fail": 0})
        cell["pass" if payload.get("outcome") == "pass" else "fail"] += 1
    return out


def _rate_claim(construct: str, backend: str, metric: str, k: int, n: int,
                as_of: str, ledger_lines: int, ledger_sha256, notes):
    lo, hi = wilson(k, n)
    body = {
        "record": "quartermaster-scored-claim/1",
        "construct": construct,
        "subject": {"source_id": backend, "match": "declared-name"},
        "custody": "striatum-production",
        "as_of": as_of,
        "metrics": {metric: {"value": k / n, "denominator": n,
                             "ci95": [lo, hi]},
                    "n_pairs": {"value": n}},
        "evidence": [{"kind": "striatum-ledger-harvest",
                      "ledger_lines": ledger_lines,
                      "ledger_sha256": ledger_sha256}],
        "notes": list(notes),
    }
    payload = json.dumps(body, sort_keys=True, ensure_ascii=False)
    body["claim_id"] = "qc-" + hashlib.sha256(
        payload.encode()).hexdigest()[:16]
    return body


def tier_a_claims(events: list[dict], as_of: str, ledger_lines: int,
                  ledger_sha256: str | None = None) -> list[dict]:
    """All Tier A claims: per-pass delivery, receipt compliance, and the
    mechanical per-pass gates (packetization legality, integration checks).
    Build's richer packet-checks claim stays with `build_claims`."""
    if ledger_lines < MIN_LEDGER_LINES:
        raise ValueError(
            f"ledger dump holds {ledger_lines} lines, below the "
            f"{MIN_LEDGER_LINES} floor")
    claims: list[dict] = []
    base_notes = [
        "striatum-production custody: executed and labelled by striatum's "
        "production loop; harvested and scored by CAPLAB "
        "(caplab.advisory.build_corpus, Tier A).",
        "Mechanical/closure labels only — no model judgment in the loop. "
        "Assignment is scheduler-routed, not random; rates describe the "
        "work each Binding was actually given.",
    ]
    for pid, backends in sorted(harvest_deliveries(events).items()):
        construct = PASS_CONSTRUCTS.get(pid)
        if construct is None or pid == "build":
            continue
        for backend, cell in sorted(backends.items()):
            given = sum(v for k, v in cell.items()
                        if k != "excluded_deferrals")
            if not given:
                continue
            delivered = sum(cell.get(o, 0) for o in DELIVERED_OUTCOMES)
            claims.append(_rate_claim(
                construct, backend, "delivery_rate", delivered, given,
                as_of, ledger_lines, ledger_sha256, base_notes + [
                    f"capacity deferrals excluded "
                    f"({cell['excluded_deferrals']}).",
                ]))
    for backend, cell in sorted(harvest_receipt_compliance(events).items()):
        n = cell["pass"] + cell["fail"]
        if not n:
            continue
        claims.append(_rate_claim(
            RECEIPT_CONSTRUCT, backend, "receipt_pass_rate", cell["pass"], n,
            as_of, ledger_lines, ledger_sha256, base_notes + [
                "receipt-checks shape validation across all pass types: "
                "harness protocol fidelity, not model capability.",
            ]))
    for pid, gate_id, construct, metric in (
            ("packetization", "work-graph-legality",
             "packetization.legality/1", "legality_pass_rate"),
            ("integration", "integration-checks",
             "integration.checks/1", "checks_pass_rate")):
        for backend, cell in sorted(
                harvest_gate(events, pid, gate_id).items()):
            n = cell["pass"] + cell["fail"]
            if not n:
                continue
            claims.append(_rate_claim(
                construct, backend, metric, cell["pass"], n,
                as_of, ledger_lines, ledger_sha256, base_notes))
    return claims
