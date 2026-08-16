"""Matched comparison between two bindings measured on the same cases.

When two subjects were measured under the same sweep seed, they saw the same
substrates with the same injections. That permits a *paired* comparison,
which is both more sensitive and more honest than comparing two independent
rates: it conditions on the cases, so a difference in case difficulty cannot
masquerade as a difference in capability.

The test is the exact binomial (sign) test over discordant pairs — McNemar's
test without the chi-square approximation, which small samples do not earn.
Concordant pairs (both caught, both missed) carry no information about which
subject is better and are excluded from the test by construction, though
they are reported so the reader can see how much of the sample was
uninformative.
"""

from __future__ import annotations

import json
import math
import os

from .scoring import completed


def _rows(run_dir: str) -> dict[str, dict]:
    path = os.path.join(run_dir, "results.jsonl")
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if not row.get("usable"):
                continue
            if not (row.get("mutant_json_valid") or row.get("control_json_valid")):
                continue
            out[row["dispatch_id"]] = row
    return out


def _binom_two_sided(k: int, n: int, p: float = 0.5) -> float:
    """Exact two-sided binomial p-value (equal-tail doubling for p=0.5)."""
    if n == 0:
        return 1.0

    def pmf(i):
        return math.comb(n, i) * p ** i * (1 - p) ** (n - i)

    tail = sum(pmf(i) for i in range(0, k + 1)) if k <= n / 2 else \
        sum(pmf(i) for i in range(k, n + 1))
    return min(1.0, 2 * tail)


def paired_comparison(run_a: str, run_b: str, label_a: str = "",
                      label_b: str = "") -> dict:
    """Compare two completed runs on the cases they both measured."""
    for run in (run_a, run_b):
        if not completed(run):
            raise ValueError(f"{run}: not a completed run; refusing to compare")
    a, b = _rows(run_a), _rows(run_b)
    shared = sorted(set(a) & set(b))

    a_only_caught = b_only_caught = both = neither = 0
    a_alarms = b_alarms = 0
    a_only_alarm = b_only_alarm = 0
    per_class: dict[str, dict] = {}
    for dispatch in shared:
        ra, rb = a[dispatch], b[dispatch]
        ca, cb = bool(ra.get("caught")), bool(rb.get("caught"))
        if ca and cb:
            both += 1
        elif ca:
            a_only_caught += 1
        elif cb:
            b_only_caught += 1
        else:
            neither += 1
        fa, fb = bool(ra.get("false_alarm")), bool(rb.get("false_alarm"))
        a_alarms += fa
        b_alarms += fb
        # A false alarm is a refusal of a control arm the other subject
        # cleared. Discrimination is catch minus false alarm, so a subject
        # that catches well while refusing sound work is not the better
        # reviewer -- and a catch-rate test alone cannot see that.
        if fa and not fb:
            a_only_alarm += 1
        elif fb and not fa:
            b_only_alarm += 1
        cell = per_class.setdefault(ra.get("defect_class") or "(unknown)",
                                    {"n": 0, "a": 0, "b": 0})
        cell["n"] += 1
        cell["a"] += int(ca)
        cell["b"] += int(cb)

    discordant = a_only_caught + b_only_caught
    p_value = _binom_two_sided(min(a_only_caught, b_only_caught), discordant)
    alarm_discordant = a_only_alarm + b_only_alarm
    alarm_p = _binom_two_sided(min(a_only_alarm, b_only_alarm), alarm_discordant)
    n = len(shared)
    return {
        "a": label_a or os.path.basename(run_a),
        "b": label_b or os.path.basename(run_b),
        "shared_cases": n,
        "a_only_caught": a_only_caught,
        "b_only_caught": b_only_caught,
        "both_caught": both,
        "neither_caught": neither,
        "discordant_pairs": discordant,
        "uninformative_pairs": both + neither,
        "a_catch_rate": (both + a_only_caught) / n if n else None,
        "b_catch_rate": (both + b_only_caught) / n if n else None,
        "a_false_alarms": a_alarms,
        "b_false_alarms": b_alarms,
        "sign_test_p": p_value,
        "significant_at_05": p_value < 0.05,
        "a_only_false_alarm": a_only_alarm,
        "b_only_false_alarm": b_only_alarm,
        "false_alarm_discordant_pairs": alarm_discordant,
        "false_alarm_sign_test_p": alarm_p,
        "false_alarm_significant_at_05": alarm_p < 0.05,
        "a_discrimination": ((both + a_only_caught) - a_alarms) / n if n else None,
        "b_discrimination": ((both + b_only_caught) - b_alarms) / n if n else None,
        "by_defect_class": {k: dict(v) for k, v in sorted(per_class.items())},
        "reading": (
            "no shared cases; not a matched comparison" if not n else
            f"catch: {discordant} of {n} shared cases discriminate, exact "
            f"sign test p={p_value:.3f}"
            + ("" if p_value < 0.05 else " (not established)")
            + f"; false alarms: {alarm_discordant} discordant, p="
            f"{alarm_p:.3f}"
            + ("" if alarm_p < 0.05 else " (not established)")),
    }
