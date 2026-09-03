"""Pairwise plan judgment, and the calibration that decides who may judge.

Layer 1 of the ranking memo (`research-2026-09-02-planning-ranking-instrument.md`):
two work graphs for the same task, shown blinded to a judge from a family
independent of both planners, in both orders. This module carries the
prompt (versioned: the rubric is claim identity), the judge adapters, the
independence rule, the verdict parser, and the calibration summary.

Calibration comes before any ranking is read. A judge is shown
control/mutant pairs from the audited plan operators and must prefer the
control. Its per-class catch on those pairs is its reliability, measured on
this instrument, this day. The two size probes are summarized apart from
the defect classes: on `atomicity_split` the mutant is the larger graph and
on `merge_independent_packets` the smaller, so a judge whose verdicts track
size shows up as one that prefers the split mutant and rejects the merge
mutant — or the reverse — rather than as one that catches defects.

Position handling follows the literature the memo cites: every pair runs in
both orders, and a verdict that changes with the order is recorded as a tie,
never as a preference.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import random

from .planning_corpus import task_context
from .pool_runner import invoke, load_declaration

JUDGE_PROFILE = "plan-judge-v1"

PAIRWISE_SCHEMA = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "advisory", "schemas",
    "pairwise-verdict.schema.json"))

JUDGE_PROMPT_V1 = """JUDGE ONLY. You are comparing two implementation plans; \
you are not building, executing, or modifying anything. Do not create, \
modify, delete, or write any file anywhere. Do not run tools. The filesystem \
is not the task: judge only the material presented below.

You will read one engineering step's DESIGN and CONTEXT, then two candidate
WORK GRAPHS for that step, labelled A and B. Each work graph packetizes the
step into ordered packets, each with a purpose, inputs, outputs, dependencies,
a write scope, and acceptance checks.

THE QUESTION. If each graph were built packet by packet, exactly as written,
by a competent builder who does only what the packet says: which graph is
more likely to deliver everything the design promises, with each packet
independently verifiable by its own declared acceptance checks?

WHAT TO WEIGH.
- Coverage: every deliverable the design names appears as some packet's output.
- Verifiability: each packet's acceptance checks can actually establish that
  packet's outputs are correct; a packet that claims verification it does not
  check is a defect.
- Dependency honesty: depends_on names real packets, forms no cycle, and the
  index lists a packet only after everything it depends on.
- Scope discipline: write scopes denote places the step plausibly touches, and
  a packet's purpose describes work its scope can hold.
- Granularity: a graph that hands the whole step back as one packet is not a
  plan; a graph that splits one verifiable unit across dependent packets makes
  its intermediate states unverifiable. Packet COUNT by itself is evidence of
  neither quality nor defect. Do not prefer a graph for being longer or
  shorter.

ANSWER FORMAT. Reply with ONLY one JSON object, nothing else:
  {"preferred": "A" | "B" | "tie",
   "confidence": <0.0-1.0>,
   "reasons": ["<one sentence>", ...]}
Answer "tie" only when you find no difference that bears on the question.
"""


def render_judge_prompt(task: dict, graph_a: dict, graph_b: dict,
                        max_bytes: int = 180_000) -> str | None:
    """The judge prompt: rubric, the task's design and context, graphs A and B."""
    context = task_context(task, include_base=False, max_bytes=max_bytes)
    if context is None:
        return None
    return "".join([
        JUDGE_PROMPT_V1, "\nDESIGN AND CONTEXT:\n", context,
        "\n===== WORK GRAPH A =====\n",
        json.dumps(graph_a, ensure_ascii=False, indent=1, sort_keys=True),
        "\n\n===== WORK GRAPH B =====\n",
        json.dumps(graph_b, ensure_ascii=False, indent=1, sort_keys=True),
        "\n\nRespond with ONLY the verdict JSON object.\n"])


# ------------------------------------------------------------------- judges

def judge_adapter(backends_root: str, judge_id: str,
                  schema_path: str = PAIRWISE_SCHEMA) -> dict:
    """The declared adapter, reshaped only where its output contract forbids
    a verdict.

    The agy declarations pin `--json-schema review-ledger.schema.json`, which
    cannot carry a pairwise verdict; that one argument is swapped for the
    verdict schema and the payload pointer is kept. Every other adapter is
    used exactly as declared and its text is parsed for the JSON object. The
    judge is instrument, not subject — but its exact command is still
    recorded on every row, because the judge configuration is claim identity.
    """
    declaration = load_declaration(backends_root, judge_id)
    adapter = copy.deepcopy(declaration["adapter"])
    command = list(adapter["command"])
    if "--json-schema" in command:
        command[command.index("--json-schema") + 1] = os.path.abspath(schema_path)
    adapter["command"] = command
    adapter["judge_id"] = judge_id
    adapter["aliasing_class"] = (declaration.get("aliasing") or {}).get("aliasing_class")
    adapter["command_sha256"] = hashlib.sha256(
        json.dumps(command).encode()).hexdigest()
    return adapter


def planner_class(backends_root: str, planner_id: str) -> str | None:
    declaration = load_declaration(backends_root, planner_id)
    return (declaration.get("aliasing") or {}).get("aliasing_class")


def eligible_judges(judges: list[dict], *planner_classes: str | None,
                    want: int = 2) -> list[dict]:
    """Judges whose family excludes every planner's family, in jury order.

    A judge with no declared aliasing class is never eligible: independence
    that cannot be shown is not assumed."""
    out = []
    for judge in judges:
        cls = judge.get("aliasing_class")
        if cls and all(cls != pc for pc in planner_classes):
            out.append(judge)
    return out[:want]


def parse_verdict(doc) -> str | None:
    """'A', 'B' or 'tie' from a judge's document; None when unusable."""
    if not isinstance(doc, dict):
        return None
    preferred = doc.get("preferred")
    if isinstance(preferred, str) and preferred.strip().upper() in ("A", "B"):
        return preferred.strip().upper()
    if isinstance(preferred, str) and preferred.strip().lower() == "tie":
        return "tie"
    return None


def judge_pair(adapter: dict, task: dict, graph_a: dict, graph_b: dict,
               timeout: int, workspace: str) -> dict:
    """One judge call on one ordered pair, through the sandboxed adapter."""
    prompt = render_judge_prompt(task, graph_a, graph_b)
    if prompt is None:
        return {"preferred": None, "error": "prompt refused (missing body or over budget)",
                "prompt_bytes": None, "seconds": 0.0, "exit_code": None,
                "timed_out": False, "sandbox": None, "raw_head": None}
    result = invoke(adapter, prompt, timeout, workspace=workspace)
    return {
        "preferred": parse_verdict(result["doc"]),
        "confidence": (result["doc"] or {}).get("confidence") if isinstance(result["doc"], dict) else None,
        "reasons": ((result["doc"] or {}).get("reasons") or [])[:6] if isinstance(result["doc"], dict) else [],
        "error": result["error"] if result["error"] else (
            None if parse_verdict(result["doc"]) else "no parseable verdict"),
        "prompt_bytes": result["prompt_bytes"], "seconds": result["seconds"],
        "exit_code": result["exit_code"], "timed_out": result["timed_out"],
        "sandbox": result["sandbox"], "raw_head": None if parse_verdict(result["doc"])
        else result["raw_head"],
    }


# --------------------------------------------------------------- resolution

def resolve_orders(first: str | None, second: str | None) -> str | None:
    """One verdict from the two orderings of a pair.

    `first` is the verdict with the control shown as A; `second` with the
    control shown as B. Returns 'control', 'mutant', 'tie', or None when
    either call was unusable. Order-dependent verdicts are ties: the memo's
    rule, from the position-bias literature."""
    if first is None or second is None:
        return None
    a = {"A": "control", "B": "mutant", "tie": "tie"}[first]
    b = {"A": "mutant", "B": "control", "tie": "tie"}[second]
    if a == b:
        return a
    if "tie" in (a, b):
        return "tie"
    return "tie"                       # flipped with the order: no preference


def position_flipped(first: str | None, second: str | None) -> bool | None:
    """Did the judge pick the same LABEL in both orders (a position habit)?"""
    if first in (None, "tie") or second in (None, "tie"):
        return None
    return first == second


# ------------------------------------------------------------------ sampling

def sample_pairs(audit_rows: list[dict], per_class: int, seed: int,
                 size_probes: tuple[str, ...] = ("atomicity_split",
                                                 "merge_independent_packets")) -> list[dict]:
    """A seeded, planner-balanced draw of admissible mutants per operator.

    Round-robin over planners so no family dominates a class; the size
    probes are drawn like any other class and only summarized apart."""
    rng = random.Random(seed)
    by_class: dict[str, dict[str, list[dict]]] = {}
    for row in audit_rows:
        if not row.get("applied") or not row.get("admissible"):
            continue
        planner = row.get("planner") or row["identity"].split("/", 1)[0]
        by_class.setdefault(row["operator"], {}).setdefault(planner, []).append(row)
    out = []
    for operator in sorted(by_class):
        buckets = {p: sorted(rows, key=lambda r: r["identity"])
                   for p, rows in by_class[operator].items()}
        for rows in buckets.values():
            rng.shuffle(rows)
        planners = sorted(buckets)
        rng.shuffle(planners)
        drawn = []
        while len(drawn) < per_class and any(buckets.values()):
            for planner in planners:
                if buckets[planner] and len(drawn) < per_class:
                    drawn.append(buckets[planner].pop())
        for row in drawn:
            out.append({"pair_id": hashlib.sha256(
                            f"{row['identity']}|{operator}".encode()).hexdigest()[:16],
                        "identity": row["identity"], "operator": operator,
                        "planner": row.get("planner") or row["identity"].split("/", 1)[0],
                        "size_probe": operator in size_probes})
    return out


# ------------------------------------------------------------------- summary

def summarize(rows: list[dict]) -> dict:
    """Per judge and class: catch, defect-preferred, ties, position flips.

    `rows` are resolved pairs: one per (pair, judge) carrying `resolved`
    ('control' | 'mutant' | 'tie' | None), `first`, `second`, `operator`,
    `size_probe`, `judge`."""
    from .wilson import wilson
    out: dict = {}
    for judge in sorted({r["judge"] for r in rows}):
        jrows = [r for r in rows if r["judge"] == judge]
        usable = [r for r in jrows if r.get("resolved") is not None]
        flips = [position_flipped(r.get("first"), r.get("second")) for r in usable]
        decided = [f for f in flips if f is not None]
        entry = {
            "pairs": len(jrows), "usable": len(usable),
            "position_flip_rate": (sum(decided) / len(decided)) if decided else None,
            "position_flip_n": len(decided),
            "by_class": {}, "size_probes": {},
        }
        for operator in sorted({r["operator"] for r in usable}):
            orows = [r for r in usable if r["operator"] == operator]
            n = len(orows)
            control = sum(1 for r in orows if r["resolved"] == "control")
            mutant = sum(1 for r in orows if r["resolved"] == "mutant")
            tie = n - control - mutant
            cell = {"n": n, "prefers_control": control, "prefers_mutant": mutant,
                    "tie": tie, "catch": control / n if n else None,
                    "catch_ci95": list(wilson(control, n)) if n else None}
            if orows[0].get("size_probe"):
                # Direction, not correctness: the split mutant is larger, the
                # merge mutant smaller. Preferring the mutant on split and
                # rejecting it on merge is a preference for size.
                cell["mutant_is"] = ("larger" if operator == "atomicity_split"
                                     else "smaller")
                entry["size_probes"][operator] = cell
            else:
                entry["by_class"][operator] = cell
        defect_rows = [r for r in usable if not r.get("size_probe")]
        n = len(defect_rows)
        caught = sum(1 for r in defect_rows if r["resolved"] == "control")
        wrong = sum(1 for r in defect_rows if r["resolved"] == "mutant")
        entry["defect_classes_pooled"] = {
            "n": n, "catch": caught / n if n else None,
            "catch_ci95": list(wilson(caught, n)) if n else None,
            "prefers_defect": wrong / n if n else None}
        larger = [r for r in usable if r["operator"] == "atomicity_split"]
        smaller = [r for r in usable if r["operator"] == "merge_independent_packets"]
        prefers_larger = (sum(1 for r in larger if r["resolved"] == "mutant")
                          + sum(1 for r in smaller if r["resolved"] == "control"))
        entry["size_preference"] = {
            "n": len(larger) + len(smaller),
            "prefers_larger_share": (prefers_larger / (len(larger) + len(smaller)))
            if (larger or smaller) else None}
        out[judge] = entry
    return out
