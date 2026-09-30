"""Shared fixtures for the retrieval artifact, report and comparison tests.

The default spec has three queries, two seeds and four command arms that stand
for a known-good retriever, a deliberately bad one, an empty one and one that
always times out. Nothing here runs a retriever: attempts are constructed
directly so every expected number can be checked by hand.
"""
from __future__ import annotations

import copy
from pathlib import Path

from caplab.retrieval import artifacts, contracts

CORPUS = [{"id": f"n{i}", "body": f"note body {i}"} for i in range(1, 7)]

# arm -> query -> ranked ids. q1 needs n1; q2 needs n2 and n3; q3 is a control that forbids n5.
BEHAVIOR = {
    "good": {"q1": ["n1", "n4"], "q2": ["n2", "n3", "n4"], "q3": []},
    "mid": {"q1": ["n4", "n1"], "q2": ["n2", "n4", "n5"], "q3": ["n4"]},
    "bad": {"q1": ["n4", "n5"], "q2": ["n4", "n5", "n6"], "q3": ["n5", "n4"]},
    "empty": {"q1": [], "q2": [], "q3": []},
    "failing": None,
}


def make_spec(*, experiment_id="fixture", arms=("good", "bad"), seeds=(0, 1), cutoffs=(1, 3), timeout=5,
              corpus=None, queries=None):
    return {
        "schema_version": "caplab-retrieval-spec/1",
        "experiment_id": experiment_id,
        "corpus": copy.deepcopy(corpus or CORPUS),
        "queries": copy.deepcopy(queries or [
            {"id": "q1", "text": "where is one", "relevant_ids": ["n1"]},
            {"id": "q2", "text": "where are two and three", "relevant_ids": ["n2", "n3"]},
            {"id": "q3", "text": "nothing matches", "relevant_ids": [], "forbidden_ids": ["n5"], "stratum": "no_answer"},
        ]),
        "arms": [{"id": arm, "adapter": "command", "configuration": {"argv": ["retriever", arm]}} for arm in arms],
        "cutoffs": list(cutoffs),
        "seeds": list(seeds),
        "timeout_seconds": timeout,
    }


def attempt(row, *, status="ok", ranked=None, delivered=None, latency=1_000, error=None, observation=None):
    """An attempt for one roster row, with the failure conventions of the contract."""
    if status != "ok":
        ranked, delivered = [], None
        if status == "not_started":
            latency = None
        elif error is None:
            error = {"code": status}
    return {"assignment_id": row["assignment_id"], "arm": row["arm"], "query_id": row["query_id"], "seed": row["seed"],
            "status": status, "ranked_ids": list(ranked or []), "delivered_ids": delivered, "latency_ns": latency,
            "error": error, "observation": observation or {}}


def behave(row, overrides=None):
    """The default attempt for a row, honoring an override {(arm, query, seed): attempt kwargs}."""
    key = (row["arm"], row["query_id"], row["seed"])
    if overrides and key in overrides:
        return attempt(row, **overrides[key])
    plan = BEHAVIOR[row["arm"]]
    if plan is None:
        return attempt(row, status="timeout", latency=5_000_000_000)
    return attempt(row, ranked=plan[row["query_id"]])


def write_run(parent: Path, name="run", *, spec=None, overrides=None, skip=(), finish=True, raw=True,
              provenance=None):
    """Record a run under parent/name. `skip` holds assignment ids to leave unrecorded."""
    spec = spec or make_spec()
    run = artifacts.RunArtifacts(Path(parent) / name, spec, provenance=provenance)
    for row in run.pending_assignments():
        if row["assignment_id"] in skip:
            continue
        payload = None
        if raw:
            payload = {"request": b'{"query": "' + row["query_id"].encode() + b'"}',
                       "response": b'{"ranked_ids": [], "seconds": 1.50}', "stderr": b""}
        run.record_attempt(behave(row, overrides), raw=payload)
    return run, (run.finish() if finish else None)


def normalized(spec):
    return contracts.validate_spec(spec)
