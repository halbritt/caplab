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
