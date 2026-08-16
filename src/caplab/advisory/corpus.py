"""Substrate harvest for the expanded matched-pair case pool (Tier 3).

A **substrate** is one known-sound artifact a defect operator can act on. Two
sources, both mechanical:

- **exchange**: striatum dispatch bundles whose review reached `fate ==
  final` — the same known-sound filter the instrument already trusts. This
  is the exhaust-as-cases miner v0: production review subjects, harvested
  with lineage, never with their operational verdicts as labels.
- **docs**: structured markdown from owned repositories (RFCs, ADRs,
  designs) at a pinned commit. These widen topic diversity beyond striatum's
  exchange.

Each substrate records lineage (source, locator, sha256), a deterministic
sealed/open partition (hash-based, so re-harvesting never migrates a
substrate across the split), and the vector of operators that mechanically
apply. A case is (substrate, operator, seed); per-sweep sampling draws from
the open partition and never re-uses a (binding, case) pair before the pool
is exhausted.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import random

from .instrument_defects import NotApplicable
from .operators import ALL_OPERATORS

SUBSTRATE_RECORD = "caplab-substrate/1"
SEALED_FRACTION = 0.25  # of substrates, by identity hash — never sampled for
                        # open sweeps; reserved for later qualification-grade
                        # evaluation so advisory exposure cannot leak into it.


def _partition(digest: str) -> str:
    return "sealed" if int(digest[:8], 16) / 0xFFFFFFFF < SEALED_FRACTION else "open"


def _applicability(body: str) -> dict[str, bool]:
    vector = {}
    for operator in ALL_OPERATORS:
        try:
            operator(body, random.Random(0))
            vector[operator.__name__] = True
        except NotApplicable:
            vector[operator.__name__] = False
        except Exception:
            # An operator crashing on a wild substrate is an operator bug,
            # but the harvest must not die on it; record it as inapplicable.
            vector[operator.__name__] = False
    return vector


def _substrate(body: bytes, source: dict) -> dict:
    digest = hashlib.sha256(body).hexdigest()
    text = body.decode("utf-8", errors="replace")
    applicability = _applicability(text)
    return {
        "record": SUBSTRATE_RECORD,
        "substrate_id": "qs-" + digest[:16],
        "sha256": digest,
        "bytes": len(body),
        "partition": _partition(digest),
        "source": source,
        "applicable_operators": sorted(
            name for name, ok in applicability.items() if ok),
    }


def harvest_exchange(exchange_root: str, analysis_path: str,
                     limit: int | None = None) -> list[dict]:
    """Fate-final dispatch inputs as substrates, with dispatch lineage."""
    with open(analysis_path, encoding="utf-8") as f:
        reviews = json.load(f)["reviews"]
    substrates = []
    for review in reviews:
        if review.get("fate") != "final":
            continue
        dispatch_id = review["dispatch_id"]
        bundle = os.path.join(exchange_root, "dispatch", dispatch_id)
        manifest_path = os.path.join(bundle, "manifest.json")
        if not os.path.isfile(manifest_path):
            continue
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        inputs = manifest.get("inputs") or []
        if not inputs:
            continue
        path = os.path.join(bundle, inputs[0]["path"])
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as f:
            body = f.read()
        substrates.append(_substrate(body, {
            "kind": "striatum-exchange",
            "dispatch_id": dispatch_id,
            "input_path": inputs[0]["path"],
            "fate": "final",
        }))
        if limit and len(substrates) >= limit:
            break
    return substrates


def harvest_docs(repo: str, patterns: list[str], commit: str,
                 min_bytes: int = 2000) -> list[dict]:
    """Structured markdown documents from an owned repository."""
    substrates = []
    for pattern in patterns:
        for path in sorted(glob.glob(os.path.join(repo, pattern),
                                     recursive=True)):
            if not os.path.isfile(path):
                continue
            with open(path, "rb") as f:
                body = f.read()
            if len(body) < min_bytes:
                continue
            substrates.append(_substrate(body, {
                "kind": "repo-doc",
                "repo": os.path.basename(os.path.normpath(repo)),
                "commit": commit,
                "path": os.path.relpath(path, repo),
            }))
    return substrates


class SubstrateRegistry:
    def __init__(self, path: str):
        self.path = path

    def read(self) -> list[dict]:
        if not os.path.isfile(self.path):
            return []
        with open(self.path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def append(self, substrates: list[dict]) -> dict:
        existing = {s["sha256"] for s in self.read()}
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        added = skipped = 0
        with open(self.path, "a", encoding="utf-8") as f:
            for substrate in substrates:
                if substrate["sha256"] in existing:
                    skipped += 1
                    continue
                f.write(json.dumps(substrate, ensure_ascii=False,
                                   sort_keys=True) + "\n")
                existing.add(substrate["sha256"])
                added += 1
        return {"added": added, "skipped_duplicates": skipped}


#: Source kinds whose substrates can be measured through the instrument's own
#: prompt path. An exchange substrate carries its dispatch bundle, so the real
#: posture, stage contract, and manifest render around it. A repo-doc has no
#: bundle and therefore no contract, and the 2026-08-16 finding showed that
#: scoring a contract-relative defect without a contract measures whether a
#: reviewer infers an unstated rule — a different construct. Repo-docs stay in
#: the registry (they are sound substrates) but are withheld from scored
#: sampling until synthetic manifests give them a stage contract.
MEASUREMENT_READY_SOURCES = {"striatum-exchange"}


def measurement_ready(substrate: dict) -> bool:
    return substrate["source"]["kind"] in MEASUREMENT_READY_SOURCES


def sample_cases(substrates: list[dict], sweep_seed: int,
                 per_operator: int, partition: str = "open",
                 require_measurement_ready: bool = True) -> list[dict]:
    """Deterministic per-sweep case sample, balanced across operator classes.

    Balancing is the corrective for the historical skew (base_dropped was 29%
    of all pairs). Every case is (substrate, operator, seed); the seed
    derives from the sweep seed and the substrate hash, so two sweeps with
    different seeds draw different injections from the same substrate.
    """
    pool = [s for s in substrates if s["partition"] == partition]
    if require_measurement_ready:
        pool = [s for s in pool if measurement_ready(s)]
    by_operator: dict[str, list[dict]] = {}
    for substrate in pool:
        for name in substrate["applicable_operators"]:
            by_operator.setdefault(name, []).append(substrate)
    cases = []
    for name in sorted(by_operator):
        rng = random.Random(f"{sweep_seed}:{name}")
        candidates = sorted(by_operator[name], key=lambda s: s["sha256"])
        rng.shuffle(candidates)
        for substrate in candidates[:per_operator]:
            cases.append({
                "substrate_id": substrate["substrate_id"],
                "sha256": substrate["sha256"],
                "operator": name,
                "seed": int(hashlib.sha256(
                    f"{sweep_seed}:{substrate['sha256']}:{name}".encode()
                ).hexdigest()[:8], 16),
                "source": substrate["source"],
            })
    return cases
