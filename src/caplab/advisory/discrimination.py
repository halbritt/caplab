"""Promotion gate for the discrimination corpus.

The pool is candidate generation; this gate decides what graduates into the
durable set of cases that reproducibly tell Bindings apart. The standing goal
(Principal, 2026-08-17) is discrimination — high between-Binding variance
with low within-Binding variance — not absolute-rate precision. One lucky
disagreement is not evidence: within-Binding variance limits the confidence
that an observed between-Binding difference is real, so a separation must
reproduce before it counts. That is a principle about confidence, not a
literal statistical bound.

A case is promoted only when, across at least `min_sweeps` distinct sweeps
(distinct seeds draw distinct injections from the same substrate, so this is
reproduction under perturbation, not replay):

- it separates the same Binding pair in the same direction every time;
- its control is adjudicated sound — on an unsound control, "separation"
  scores the detecting reviewer against the missing one backwards;
- its defect class is a declared operator of the instrument, so the
  disagreement maps to the Construct rather than to an accident.

Everything that separates but does not qualify is reported with the reason
it was withheld, because a silent gate reads as an empty pool.
"""

from __future__ import annotations

#: Prompt profiles whose measurements are quarantined from promotion. The
#: v1 change-set contract demanded verification of an absent base with no
#: lookup primitive; subjects complied by grepping the host's 361 GB store
#: (infra postmortem 2026-08-21-oom-rg-store-grep.md), so its cells measure
#: store-forensics affordance and grep survival as much as review. A cell
#: touched by a quarantined profile in ANY sweep is withheld until it
#: reproduces entirely under a clean contract. Quarantine accepted by the
#: Principal 2026-08-22.
QUARANTINED_PROFILES = {"v1-changeset"}


def promotion_candidates(contrasts: list[dict], adjudications,
                         substrate_sources: dict | None = None,
                         min_sweeps: int = 2) -> dict:
    """{promoted, withheld} over annotated contrast documents.

    Each contrast is a `paired_comparison` result annotated with the
    `sweep_seed` its runs shared. Grouping is by (substrate, defect class,
    Binding pair): the same substrate separating the same pair under
    different injections is the reproduction that matters.
    """
    from .operators import BY_NAME

    grouped: dict[tuple, dict] = {}
    for doc in contrasts:
        pair = (doc["a"], doc["b"])
        for entry in doc.get("discordant_cases") or []:
            key = (entry.get("substrate_id") or entry["dispatch_id"],
                   entry.get("defect_class"), pair)
            cell = grouped.setdefault(key, {"sweeps": [], "directions": set(),
                                            "quarantined_profiles": set()})
            cell["sweeps"].append(doc.get("sweep_seed"))
            cell["directions"].add(
                doc["a"] if entry.get("caught_by") == "a" else doc["b"])
            profile = entry.get("calibration_profile")
            if profile in QUARANTINED_PROFILES:
                cell["quarantined_profiles"].add(profile)

    promoted, withheld = [], []
    for (substrate, defect_class, pair), cell in sorted(grouped.items()):
        sweeps = sorted(set(cell["sweeps"]), key=str)
        entry = {"substrate_id": substrate, "defect_class": defect_class,
                 "pair": list(pair), "sweeps": sweeps}
        control_key = (substrate_sources or {}).get(substrate) or substrate
        disposition = adjudications.disposition(control_key)
        if cell["quarantined_profiles"]:
            profiles = ", ".join(sorted(cell["quarantined_profiles"]))
            withheld.append({**entry, "reason":
                             f"measured under quarantined contract "
                             f"({profiles}) — the cell reflects "
                             f"store-forensics affordance, not review; "
                             f"re-measure under a clean profile"})
        elif len(cell["directions"]) > 1:
            withheld.append({**entry, "reason":
                             "direction flips between sweeps — the "
                             "separation is instability, not capability"})
        elif len(sweeps) < min_sweeps:
            withheld.append({**entry, "reason":
                             f"reproduction not established: seen in "
                             f"{len(sweeps)} sweep(s), needs {min_sweeps}"})
        elif disposition != "sound":
            withheld.append({**entry, "reason":
                             f"control disposition is {disposition!r}, not "
                             f"'sound' — separation on an unexamined or "
                             f"defective control scores backwards"})
        elif defect_class not in BY_NAME:
            withheld.append({**entry, "reason":
                             f"{defect_class!r} is not a declared operator, "
                             f"so the disagreement maps to no Construct"})
        else:
            promoted.append({**entry,
                             "caught_by": next(iter(cell["directions"]))})
    return {"promoted": promoted, "withheld": withheld}
