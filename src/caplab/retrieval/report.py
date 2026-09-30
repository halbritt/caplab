"""Reviewer-readable reports for the Cairn retrieval evaluation harness.

`build_report` assembles a `caplab-retrieval-report/1` document from a sealed
plan, the recorded attempts and `metrics.summarize`; `render_markdown` renders a
report or a `caplab-retrieval-comparison/1` document for a human reviewer. Both
are pure: no filesystem, network or clock access. A report is an observational
experiment artifact. It is not a `caplab-measurement/1` record, sets no pass
threshold and says nothing about downstream task completion.

Reviewer context comes first in the report and in the rendering: what was
tested, where the labels come from, how much of the plan ran, and how to read
the numbers. Metric summaries follow and always keep numerators and
denominators next to every rate.
"""
from __future__ import annotations

from typing import Any

from caplab.retrieval import contracts

REPORT_SCHEMA = "caplab-retrieval-report/1"
COMPARISON_SCHEMA = "caplab-retrieval-comparison/1"

STATUS_COMPLETE = "complete"
STATUS_WITH_FAILURES = "completed_with_failures"
STATUS_INCOMPLETE = "incomplete"

LIMITATIONS = (
    "This is an observational experiment artifact. It is not a caplab-measurement/1 record, a qualification "
    "claim or an acceptance decision, and no pass threshold applies.",
    "Scores measure whether retrieval ranked the labelled notes; they do not measure downstream task "
    "completion or agent usefulness.",
    "Seeds repeat the same case; they are not independent new cases. Case-level figures average seeds "
    "within a query first.",
    "A failed, timed-out, interrupted, not-started or missing assignment is never a successful abstention. "
    "Conditional metrics exclude such assignments; coverage and all-assignment bounds keep them visible.",
    "Rank and exposure are separate: exposure figures exist only for attempts whose adapter observed "
    "delivery, and delivery is never inferred from rank.",
    "Integrity checks detect inconsistent edits of the retained files. They do not authenticate who wrote "
    "them; pin the manifest digest elsewhere to detect wholesale replacement.",
)


def run_status(plan: dict, attempts: list[dict]) -> dict:
    """Plan accounting that never turns a missing assignment into a success."""
    recorded = {attempt["assignment_id"]: attempt for attempt in attempts}
    by_status: dict[str, int] = {}
    failures, missing = [], []
    for row in plan["roster"]:
        attempt = recorded.get(row["assignment_id"])
        if attempt is None:
            missing.append(row["assignment_id"])
            continue
        by_status[attempt["status"]] = by_status.get(attempt["status"], 0) + 1
        if attempt["status"] != "ok":
            error = attempt.get("error") or {}
            failures.append({"assignment_id": row["assignment_id"], "arm": row["arm"], "query_id": row["query_id"],
                             "seed": row["seed"], "status": attempt["status"], "error_code": error.get("code")})
    planned = len(plan["roster"])
    ok = by_status.get("ok", 0)
    if missing:
        status = STATUS_INCOMPLETE
    elif failures:
        status = STATUS_WITH_FAILURES
    else:
        status = STATUS_COMPLETE
    return {"status": status, "planned": planned, "recorded": planned - len(missing), "ok": ok,
            "failed_or_not_started": len(failures), "missing": len(missing),
            "by_status": dict(sorted(by_status.items())), "failures": failures, "missing_assignments": missing}


def build_report(plan: dict, attempts: list[dict], summary: dict, *, finished: bool,
                 references: dict | None = None) -> dict:
    """Assemble the report. `references` names retained files and raw artifacts."""
    spec = plan["spec"]
    run = run_status(plan, attempts)
    run["finished"] = finished
    queries = spec["queries"]
    strata: dict[str, int] = {}
    for query in queries:
        strata[query["stratum"]] = strata.get(query["stratum"], 0) + 1
    answerable = sum(1 for query in queries if query["relevant_ids"])
    return {
        "schema_version": REPORT_SCHEMA,
        "reviewer_context": {
            "purpose": "Measure how well each configured retrieval arm ranks frozen, labelled notes for each "
                       "labelled query. The result is retrieval quality against these labels only.",
            "what_was_tested": {
                "experiment_id": spec["experiment_id"],
                "arms": [{"id": arm["id"], "adapter": arm["adapter"], "configuration": arm["configuration"]}
                         for arm in spec["arms"]],
                "corpus_notes": len(spec["corpus"]),
                "queries": {"total": len(queries), "answerable": answerable, "controls": len(queries) - answerable,
                            "by_stratum": dict(sorted(strata.items()))},
                "seeds": spec["seeds"],
                "cutoffs": spec["cutoffs"],
                "timeout_seconds": spec["timeout_seconds"],
                "planned_assignments": run["planned"],
            },
            "labelled_truth": {
                "source": "relevant_ids and forbidden_ids in the spec, frozen in plan.json before any retrieval "
                          "ran; gold labels are never passed to a retrieval adapter",
                "spec_sha256": plan["pins"]["spec_sha256"],
                "corpus_sha256": plan["pins"]["corpus_sha256"],
                "cases_sha256": plan["pins"]["cases_sha256"],
                "roster_sha256": plan["pins"]["roster_sha256"],
            },
            "run_status": {key: run[key] for key in ("status", "finished", "planned", "recorded", "ok",
                                                      "failed_or_not_started", "missing")},
            "how_to_read": [
                "Read the run status and the denominators first: a score over few scorable assignments says little.",
                "Every rate is shown as numerator/denominator. Conditional metrics cover successful attempts only; "
                "all-assignment bounds show the effect of failures and missing work.",
                "Answerable queries have relevant notes; empty-gold controls report false positives and "
                "forbidden hits instead of precision or recall.",
                "Precision@k always divides by k, even when fewer than k notes were returned.",
            ],
        },
        "run": run,
        "denominators": {arm: arm_summary["coverage"] for arm, arm_summary in summary["arms"].items()},
        "limitations": list(LIMITATIONS) + _dynamic_limitations(run),
        "provenance": plan.get("provenance", {}),
        "references": references or {},
        "summary": summary,
    }


def _dynamic_limitations(run: dict) -> list[str]:
    notes = []
    if not run["finished"]:
        notes.append("The run was not finished; this report is computed from the recorded attempts only.")
    if run["missing"]:
        notes.append(f"{run['missing']} planned assignment(s) have no recorded attempt and are counted as missing.")
    if run["failed_or_not_started"]:
        notes.append(f"{run['failed_or_not_started']} recorded attempt(s) failed, timed out, were interrupted or "
                     "never started; none is a successful abstention.")
    return notes


def _rate(value: Any) -> str:
    if isinstance(value, dict) and "numerator" in value and "denominator" in value:
        shown = value.get("value")
        if value["numerator"] is None:  # float-only figure such as nDCG
            return "n/a" if shown is None else f"{shown:.4f}"
        suffix = "" if shown is None else f" ({shown:.4f})"
        return f"{value['numerator']}/{value['denominator']}{suffix}"
    return "n/a" if value is None else str(value)


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    if not rows:
        return ["_none_", ""]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |" for row in rows]
    return lines + [""]


def render_markdown(document: dict) -> str:
    """Render a report or comparison for a reviewer. Reviewer context comes first."""
    schema = document.get("schema_version") if isinstance(document, dict) else None
    if schema == REPORT_SCHEMA:
        return _render_report(document)
    if schema == COMPARISON_SCHEMA:
        return _render_comparison(document)
    raise contracts.ContractError("UNKNOWN_SCHEMA", "/schema_version", f"cannot render {schema!r}")


def _render_report(report: dict) -> str:
    context, run = report["reviewer_context"], report["run"]
    tested = context["what_was_tested"]
    lines = [f"# Retrieval evaluation report: {tested['experiment_id']}", "", "## What was tested", "",
             context["purpose"], ""]
    lines += _table(["arm", "adapter", "configuration"],
                    [[arm["id"], arm["adapter"], f"`{_compact(arm['configuration'])}`"] for arm in tested["arms"]])
    queries = tested["queries"]
    lines += [f"- Corpus: {tested['corpus_notes']} notes. Queries: {queries['total']} "
              f"({queries['answerable']} answerable, {queries['controls']} controls; strata "
              f"{_compact(queries['by_stratum'])}).",
              f"- Seeds: {_compact(tested['seeds'])} (repetitions of each case). Cutoffs: {_compact(tested['cutoffs'])}. "
              f"Timeout: {tested['timeout_seconds']} s per assignment.", "",
              "## Labelled truth and provenance", "",
              f"- Labels: {context['labelled_truth']['source']}.",
              f"- spec `{context['labelled_truth']['spec_sha256']}`; corpus `{context['labelled_truth']['corpus_sha256']}`; "
              f"cases `{context['labelled_truth']['cases_sha256']}`.",
              f"- Provenance: `{_compact(report.get('provenance', {}))}`", "",
              "## Run status and denominators", "",
              f"**{run['status']}**{'' if run['finished'] else ' (run not finished)'}: {run['recorded']}/{run['planned']} "
              f"planned assignments recorded, {run['ok']} ok, {run['failed_or_not_started']} failed or not started, "
              f"{run['missing']} missing.", ""]
    rows = []
    for arm, coverage in report["denominators"].items():
        rows.append([arm, coverage["planned"], coverage["attempted"], coverage["scorable"], coverage["failures"],
                     coverage["not_started"], coverage["missing"], _rate(coverage["scorable_rate"])])
    lines += _table(["arm", "planned", "attempted", "scorable", "failures", "not started", "missing", "scorable rate"],
                    [[str(cell) for cell in row] for row in rows])
    if run["failures"]:
        lines += ["### Failed or not-started assignments", ""]
        lines += _table(["assignment", "status", "error code"],
                        [[f["assignment_id"], f["status"], f["error_code"] or ""] for f in run["failures"][:200]])
        if len(run["failures"]) > 200:
            lines += [f"_{len(run['failures']) - 200} more not shown; see report.json._", ""]
    if run["missing_assignments"]:
        shown = run["missing_assignments"][:50]
        lines += ["### Missing assignments", "", ", ".join(f"`{a}`" for a in shown) +
                  (f" (+{len(run['missing_assignments']) - 50} more)" if len(run["missing_assignments"]) > 50 else ""), ""]
    lines += ["## How to read this report", ""] + [f"- {item}" for item in context["how_to_read"]] + [""]
    lines += ["## Limitations", ""] + [f"- {item}" for item in report["limitations"]] + [""]
    lines += ["## Metrics", ""]
    for arm, arm_summary in report["summary"]["arms"].items():
        lines += _render_arm_metrics(arm, arm_summary)
    refs = report.get("references", {})
    if refs:
        lines += ["## Retained evidence", ""] + [f"- `{name}`: {_compact(value)}" for name, value in refs.items()
                                                  if name != "raw_artifacts"]
        raw = refs.get("raw_artifacts")
        if raw is not None:
            lines.append(f"- raw artifacts: {len(raw)} exact-byte object(s) in the ledger")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_arm_metrics(arm: str, summary: dict) -> list[str]:
    lines = [f"### Arm `{arm}`", ""]
    planned = summary["planned_by_kind"]
    lines += [f"Planned: {planned['answerable']} answerable, {planned['controls']} control, "
              f"{planned['with_forbidden']} with forbidden labels (assignments).", ""]
    for cutoff, block in summary["cutoffs"].items():
        answer = block["answerable"]
        lines += [f"**Cutoff k={cutoff}**", ""]
        conditional = answer["conditional"]
        rows = [[name, _rate(conditional[name])] for name in ("precision", "recall", "mrr", "success") if name in conditional]
        if "ndcg" in conditional:
            value = conditional["ndcg"]
            rows.append(["ndcg (float)", "n/a" if value["value"] is None else f"{value['value']:.4f} (n={value['count']})"])
        lines += ["Answerable, successful attempts only (conditional):", ""] + _table(["metric", "value"], rows)
        bounds = answer.get("all_assignments", {})
        if bounds:
            lines += ["Answerable, all planned assignments (bounds, not observed quality):", ""]
            lines += _table(["bound", "value"], [[name, _rate(value)] for name, value in bounds.items()])
        case = answer.get("case_level", {})
        if case:
            lines += ["Case level (seeds averaged within a query):", ""]
            lines += _table(["metric", "value"], [[name, _rate(value)] for name, value in case.items()])
        controls, forbidden = block["controls"], block["forbidden"]
        lines += _table(["controls and forbidden labels", "value"],
                        [["control false-positive rate", _rate(controls["false_positive_rate"])],
                         ["controls clean (all assignments)", _rate(controls["clean_all_assignments"])],
                         ["forbidden-hit rate", _rate(forbidden["hit_rate"])],
                         ["forbidden clean (all assignments)", _rate(forbidden["clean_all_assignments"])]])
    exposure = summary["exposure"]
    lines += ["Exposure (only where the adapter observed delivery):", ""]
    lines += _table(["measure", "value"], [[name, _rate(value)] for name, value in exposure.items()])
    latency = summary["latency_ok"]
    lines += [f"Latency of ok attempts: n={latency['count']}, median {latency['median_ns']} ns, "
              f"p95 {latency['p95_ns']} ns, max {latency['max_ns']} ns.", ""]
    return lines


def _compact(value: Any) -> str:
    import json
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _render_comparison(comparison: dict) -> str:
    context = comparison["reviewer_context"]
    lines = ["# Retrieval run comparison", "", "## What was compared", "", context["summary"], ""]
    lines += ["## Compatibility checks", ""]
    lines += _table(["pin", "left", "right", "equal"],
                    [[name, f"`{pin['left']}`", f"`{pin['right']}`", "yes" if pin["equal"] else "NO"]
                     for name, pin in comparison["compatibility"]["pins"].items()])
    for run in comparison["runs"]:
        lines.append(f"- {run['side']}: manifest `{run['manifest_sha256']}`, status {run['status']}, "
                     f"experiment `{run['experiment_id']}`")
    lines.append("")
    for item in comparison["comparisons"]:
        lines += _render_pair(item)
    lines += ["## Limitations", ""] + [f"- {text}" for text in comparison["limitations"]] + [""]
    return "\n".join(lines).rstrip() + "\n"


def _render_pair(item: dict) -> list[str]:
    arms = item["arms"]
    pairing = item["pairing"]
    lines = [f"## Left arm `{arms['left']}` vs right arm `{arms['right']}`", "",
             "Deltas are right minus left; a positive delta favors the right arm. Cases are queries; seeds "
             "are averaged within a case first.", "", "### Pairing and denominators", ""]
    lines += _table(["class", "assignments"], [[name, str(count)] for name, count in pairing["counts"].items()])
    if pairing["unpaired"]:
        lines += ["Unpaired (kept visible, never dropped):", ""]
        lines += _table(["query", "seed", "left", "right"],
                        [[u["query_id"], str(u["seed"]), u["left"], u["right"]] for u in pairing["unpaired"]])
        if pairing["unpaired_truncated"]:
            lines += [f"_List truncated; {pairing['counts']['not_both_scorable']} assignments in total._", ""]
    for cutoff, block in item["cutoffs"].items():
        lines += [f"### Cutoff k={cutoff}", ""]
        rows = []
        for name, stats in block["answerable"]["metrics"].items():
            rows.append([name, stats["cases"], _rate(stats["left_mean"]), _rate(stats["right_mean"]),
                         _rate(stats["delta"]),
                         f"{stats['right_wins']}/{stats['left_wins']}/{stats['ties']}",
                         "n/a" if stats["sign_test_p"] is None else f"{stats['sign_test_p']:.4f}",
                         stats["interval_note"] if stats["interval"] is None else
                         f"[{stats['interval'][0]:.4f}, {stats['interval'][1]:.4f}]"])
        lines += _table(["metric", "cases", "left mean", "right mean", "delta", "right wins / left wins / ties",
                         "sign-test p", "95% interval (t, cases)"], [[str(cell) for cell in row] for row in rows])
        discordant = block["answerable"]["discordant_hits"]
        lines += [f"Discordant hit pairs (assignment level): right hit and left miss {discordant['right_hit_left_miss']['count']}, "
                  f"left hit and right miss {discordant['left_hit_right_miss']['count']}, "
                  f"both hit {discordant['both_hit']}, both miss {discordant['both_miss']}.", ""]
        controls = block["controls"]
        lines += _table(["controls / forbidden (assignment level)", "counts"],
                        [["controls: both clean / left FP only / right FP only / both FP", _compact(controls["false_positive"])],
                         ["forbidden: both clean / left hit only / right hit only / both hit", _compact(controls["forbidden_hit"])]])
        sensitivity = block["answerable"]["all_roster_sensitivity"]
        lines += ["Sensitivity over every planned answerable assignment (recall; unscorable assignments imputed "
                  "0 for the lower bound and 1 for the upper bound; not observed quality):", ""]
        if sensitivity["planned_assignments"]:
            lines += _table(["quantity", "lower", "upper"],
                            [["left mean recall", _rate(sensitivity["left"]["lower"]), _rate(sensitivity["left"]["upper"])],
                             ["right mean recall", _rate(sensitivity["right"]["lower"]), _rate(sensitivity["right"]["upper"])],
                             ["delta bounds (right - left)", _rate(sensitivity["delta_bounds"]["lower"]),
                              _rate(sensitivity["delta_bounds"]["upper"])]])
            lines += [f"Unscorable assignments: left {sensitivity['unscorable']['left']}, right "
                      f"{sensitivity['unscorable']['right']} of {sensitivity['planned_assignments']}. "
                      f"The zero-imputed scenario delta is {_rate(sensitivity['zero_imputed_scenario_delta'])}; it is "
                      "one scenario, not a bound.", ""]
        else:
            lines += ["_no answerable assignments planned_", ""]
    return lines
