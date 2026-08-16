"""The invariant replay set: a fixed control for instrument reliability.

Breadth and reliability want opposite things from a budget. Breadth wants
many distinct planted defects measured once. Reliability wants few cases
measured many times. Trading one against the other inside a single sample
leaves both weak, and it leaves reliability unmeasured until somebody
re-runs identical cases by accident — which is how the control arm's 53%
test-retest agreement was found on 2026-08-16.

The anchor set separates them. It is a small, pinned set of cases that every
sweep replays with replication on **both** arms, while the rest of the
budget buys distinct defects at asymmetric replication. Because the set
never changes, its numbers are comparable across sweeps and across Bindings:

- within one sweep it measures how often the instrument agrees with itself;
- across sweeps it measures drift — if the same cases move, either the
  Binding changed or the instrument did, and the Scored claims of that
  period must be read with that in mind.

Three properties make the set an instrument control rather than more
evidence:

1. **Invariant.** The set does not depend on the sweep seed. It is built
   once, written to a file, and pinned. A pool that grows does not change
   it.
2. **Disjoint from breadth.** Anchor substrates are withheld from the
   breadth draw. A case that is replayed every sweep must not also count
   toward a claim's distinct-defect coverage, or the headline becomes partly
   a function of one constant subset.
3. **Trusted.** A substrate whose control soundness is in question cannot
   anchor anything, so substrates with a `defective` control adjudication
   are excluded at build time.
"""

from __future__ import annotations

import hashlib
import json
import os

from .corpus import measurement_ready

ANCHOR_RECORD = "caplab-anchor-set/1"
DEFAULT_SIZE = 12


def _case_seed(substrate_sha: str, operator: str) -> int:
    """Anchor seeds are fixed by content, never by a sweep seed."""
    return int(hashlib.sha256(
        f"anchor:{substrate_sha}:{operator}".encode()).hexdigest()[:8], 16)


def build_anchor_set(substrates: list[dict], size: int = DEFAULT_SIZE,
                     adjudications=None, partition: str = "open") -> dict:
    """Choose the invariant set: one case per operator, both classes covered.

    Selection is deterministic given the substrate registry: operators are
    taken in a fixed order and each contributes its lowest-hash eligible
    substrate. No sweep seed and no shuffle takes part, so two builds of the
    same registry agree.
    """
    from .adjudication import Adjudications
    from .operators import ALL_OPERATORS

    if adjudications is None:
        adjudications = Adjudications([])

    def trusted(substrate: dict) -> bool:
        dispatch = (substrate.get("source") or {}).get("dispatch_id")
        return not (dispatch and adjudications.is_defective(dispatch))

    eligible = [s for s in substrates
                if s["partition"] == partition
                and measurement_ready(s)
                and trusted(s)]

    by_operator: dict[str, list[dict]] = {}
    for substrate in eligible:
        for name in substrate["applicable_operators"]:
            by_operator.setdefault(name, []).append(substrate)

    used_substrates: set[str] = set()
    cases: list[dict] = []
    # One pass per operator in declared order, so the set spans the defect
    # space before it deepens anywhere. Operators with no eligible substrate
    # are recorded as uncovered rather than silently absent.
    uncovered = []
    for operator in [op.__name__ for op in ALL_OPERATORS]:
        if len(cases) >= size:
            break
        candidates = sorted(by_operator.get(operator, []),
                            key=lambda s: s["sha256"])
        candidates = [s for s in candidates
                      if s["substrate_id"] not in used_substrates]
        if not candidates:
            uncovered.append(operator)
            continue
        substrate = candidates[0]
        used_substrates.add(substrate["substrate_id"])
        cases.append({
            "substrate_id": substrate["substrate_id"],
            "sha256": substrate["sha256"],
            "operator": operator,
            "seed": _case_seed(substrate["sha256"], operator),
            "source": substrate["source"],
        })

    return {
        "record": ANCHOR_RECORD,
        "size": len(cases),
        "requested_size": size,
        "partition": partition,
        "uncovered_operators": uncovered,
        "cases": cases,
        "notes": [
            "Invariant: this set does not depend on a sweep seed and does "
            "not change when the pool grows.",
            "Anchor substrates are withheld from breadth sampling, so a "
            "replayed case never inflates a claim's distinct-defect count.",
            "Both arms are replicated on every sweep. The set measures the "
            "instrument, not the corpus.",
        ],
    }


def save(anchor_set: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(anchor_set, f, indent=2, sort_keys=True)
        f.write("\n")


def load(path: str) -> dict | None:
    if not path or not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def anchor_substrate_ids(anchor_set: dict | None) -> set[str]:
    if not anchor_set:
        return set()
    return {c["substrate_id"] for c in anchor_set["cases"]}


def reliability(rows: list[dict]) -> dict:
    """Within-sweep agreement of the instrument with itself, on anchor rows.

    Unanimity across replicates of one arm is the direct reading: an arm that
    answers the same way every time is reproducible, and one that splits is
    not. Reported per arm because the two differ sharply — a planted defect
    is a clear signal, while a sound artifact always holds arguable
    imperfections.
    """
    anchor = [r for r in rows if r.get("anchor") and r.get("usable")]
    if not anchor:
        return {"anchor_cases": 0}

    def share(field):
        seen = [r for r in anchor if r.get(field) is not None]
        return (sum(1 for r in seen if r[field]) / len(seen)) if seen else None

    return {
        "anchor_cases": len(anchor),
        "control_unanimous_share": share("control_unanimous"),
        "mutant_unanimous_share": share("mutant_unanimous"),
        "control_catch_rate": sum(1 for r in anchor if r["caught"]) / len(anchor),
        "control_false_alarm_rate": (
            sum(1 for r in anchor if r["false_alarm"]) / len(anchor)),
    }


def drift(current: list[dict], previous: list[dict]) -> dict:
    """Agreement between two sweeps on the same anchor cases.

    A moved anchor means the Binding changed or the instrument did. It does
    not say which, and this function does not guess.
    """
    now = {r["dispatch_id"]: r for r in current
           if r.get("anchor") and r.get("usable")}
    before = {r["dispatch_id"]: r for r in previous
              if r.get("anchor") and r.get("usable")}
    shared = sorted(set(now) & set(before))
    if not shared:
        return {"shared_anchor_cases": 0}
    agree = {field: sum(1 for k in shared if now[k][field] == before[k][field])
             for field in ("caught", "false_alarm")}
    return {
        "shared_anchor_cases": len(shared),
        "caught_agreement": agree["caught"] / len(shared),
        "false_alarm_agreement": agree["false_alarm"] / len(shared),
        "reading": ("anchor stable" if agree["caught"] == len(shared)
                    else "anchor moved: the Binding or the instrument changed, "
                         "and this measurement does not say which"),
    }
