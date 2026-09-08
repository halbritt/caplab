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
- across sweeps it describes changes in recorded anchor outcomes. Sampling
  variation, the Binding, the instrument, or runtime conditions may contribute;
  outcome disagreement alone does not identify a cause.

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

    def pairwise(field):
        """Replicate pairwise agreement on refuse/clear, chance-corrected.

        Unanimity, within-sweep pairwise agreement, and cross-sweep
        agreement are three different statistics; conflating them overstated
        the 2026-08-17 reliability block. This one names itself: verdicts
        binarized to refuse/clear, pairs involving a null (unparseable)
        replicate excluded from the denominator and their count reported.
        Kappa corrects for the base rate — an arm that nearly always refuses
        agrees with itself by chance alone, and raw agreement hides that.
        """
        from itertools import combinations

        from ._tuner_vendored import REFUSING
        agree = valid = nulls = 0
        parsed: list[bool] = []
        for r in anchor:
            verdicts = r.get(field) or []
            binarized = [None if v is None else (v in REFUSING)
                         for v in verdicts]
            nulls += sum(1 for b in binarized if b is None)
            parsed += [b for b in binarized if b is not None]
            for x, y in combinations(binarized, 2):
                if x is None or y is None:
                    continue
                valid += 1
                agree += (x == y)
        if not valid or not parsed:
            return None
        observed = agree / valid
        refuse_rate = sum(parsed) / len(parsed)
        chance = refuse_rate ** 2 + (1 - refuse_rate) ** 2
        return {
            "agreement": observed,
            "agreeing_pairs": agree,
            "valid_pairs": valid,
            "null_replicates": nulls,
            "base_refuse_rate": refuse_rate,
            "chance_agreement": chance,
            "kappa": ((observed - chance) / (1 - chance)) if chance < 1 else None,
            "handling": ("verdicts binarized to refuse/clear; "
                         "null replicates excluded pairwise"),
        }

    return {
        "anchor_cases": len(anchor),
        "control_unanimous_share": share("control_unanimous"),
        "mutant_unanimous_share": share("mutant_unanimous"),
        "control_pairwise": pairwise("control_verdicts"),
        "mutant_pairwise": pairwise("mutant_verdicts"),
        "control_catch_rate": sum(1 for r in anchor if r["caught"]) / len(anchor),
        "control_false_alarm_rate": (
            sum(1 for r in anchor if r["false_alarm"]) / len(anchor)),
    }


def drift(current: list[dict], previous: list[dict]) -> dict:
    """Describe catch and false-alarm agreement, with recorded-case coverage.

    Dispatch labels join rows; this does not verify experiment comparability
    or account for cases absent from both inputs. Ambiguous identities fail.
    Unusable rows and non-Boolean outcomes remain visible as unavailable.
    """
    def index(rows: list[dict], label: str) -> tuple[dict, dict]:
        indexed, unavailable = {}, {}
        for row in rows:
            if not row.get("anchor"):
                continue
            identity = row.get("dispatch_id")
            if not isinstance(identity, str) or not identity.strip():
                raise ValueError(f"{label} anchor lacks a valid dispatch_id")
            if identity in indexed:
                raise ValueError(f"duplicate {label} anchor dispatch_id: {identity}")
            indexed[identity] = row
            if row.get("usable") is not True:
                unavailable[identity] = "row-not-usable"
            elif any(type(row.get(field)) is not bool
                     for field in ("caught", "false_alarm")):
                unavailable[identity] = "missing-or-invalid-outcomes"
        return indexed, dict(sorted(unavailable.items()))

    now, unavailable_now = index(current, "current")
    before, unavailable_before = index(previous, "previous")
    shared_recorded = set(now) & set(before)
    shared = sorted(shared_recorded - unavailable_now.keys()
                    - unavailable_before.keys())
    agree = {field: sum(1 for k in shared if now[k][field] == before[k][field])
             for field in ("caught", "false_alarm")}
    complete = len(shared) == len(now) == len(before)
    if not shared:
        status = "unavailable"
        reading = "no shared usable anchor cases with complete Boolean outcomes"
    elif any(count != len(shared) for count in agree.values()):
        status = "observed-change"
        reading = (
            "anchor outcomes differ on shared usable cases; sampling variation, "
            "the Binding, the instrument, or runtime conditions may contribute; "
            "this comparison does not say which")
    elif not complete:
        status = "agreement-on-subset"
        reading = (
            "both outcomes agree on the shared usable subset; unmatched or "
            "unavailable recorded anchors prevent a full recorded-set comparison")
    else:
        status = "observed-agreement"
        reading = (
            "both outcomes agree on all recorded anchor cases; this observation "
            "does not establish instrument stability or future agreement")
    return {
        "schema_version": "caplab-anchor-drift/2",
        "status": status,
        "shared_anchor_cases": len(shared),
        "caught_agreement": agree["caught"] / len(shared) if shared else None,
        "false_alarm_agreement": (
            agree["false_alarm"] / len(shared) if shared else None),
        "coverage": {
            "current_anchor_cases": len(now),
            "previous_anchor_cases": len(before),
            "shared_recorded_cases": len(shared_recorded),
            "current_only_ids": sorted(set(now) - set(before)),
            "previous_only_ids": sorted(set(before) - set(now)),
            "current_unavailable": unavailable_now,
            "previous_unavailable": unavailable_before,
        },
        "comparison_basis": (
            "dispatch-id join of reported outcomes; input bytes, condition "
            "comparability, native Binding identity, and planned population "
            "completeness are not verified"),
        "reading": reading,
    }
