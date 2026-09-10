#!/usr/bin/env python3
"""Freeze a coverage sample before inspecting correctness or reviewer outcomes."""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


SEED = "reviewer-ranking-001-feasibility/v1"
PER_STRATUM = 2


def digest(document: dict) -> str:
    return hashlib.sha256(json.dumps(document, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def size_stratum(paths: list[dict]) -> str:
    code = [entry for entry in paths if entry["included_code"]]
    if any(entry["added_lines"] is None or entry["deleted_lines"] is None for entry in code):
        return "non-text"
    size = sum(entry["added_lines"] + entry["deleted_lines"] for entry in code)
    if size <= 20:
        return "0-20"
    if size <= 100:
        return "21-100"
    if size <= 500:
        return "101-500"
    return "501+"


def select(census: dict) -> dict:
    payload = {key: value for key, value in census.items() if key != "content_sha256"}
    if census.get("schema") != "caplab.reviewer-population-census/v1" or digest(payload) != census.get("content_sha256"):
        raise ValueError("census schema or content hash mismatch")
    strata = defaultdict(list)
    identities = set()
    for repository in census["repositories"]:
        for change in repository["commits"]:
            identity = (repository["name"], change["commit"])
            if identity in identities:
                raise ValueError("duplicate change identity")
            identities.add(identity)
            if not change["eligible"]:
                continue
            if not change["parents"] or not any(p["included_code"] for p in change["changed_paths"]):
                raise ValueError("eligible change lacks base or included code")
            stratum = size_stratum(change["changed_paths"])
            selection_hash = hashlib.sha256((SEED + "\0" + repository["name"] + "\0" + change["commit"]).encode()).hexdigest()
            strata[(repository["name"], stratum)].append({
                "repository": repository["name"], "source_path": repository["path"],
                "source_tip": repository["tip"], "commit": change["commit"],
                "base": change["parents"][0], "tree": change["tree"],
                "changed_paths": change["changed_paths"], "size_stratum": stratum,
                "selection_hash": selection_hash,
            })
    selected, accounting = [], []
    for (repository, stratum), candidates in sorted(strata.items()):
        ordered = sorted(candidates, key=lambda row: (row["selection_hash"], row["commit"]))
        selected.extend(ordered[:PER_STRATUM])
        accounting.append({"repository": repository, "size_stratum": stratum,
                           "eligible_count": len(ordered), "selected_count": min(PER_STRATUM, len(ordered)),
                           "not_selected_commits": [row["commit"] for row in ordered[PER_STRATUM:]]})
    report = {
        "schema": "caplab.reviewer-feasibility-sample/v1", "census_content_sha256": census["content_sha256"],
        "selection": {"seed": SEED, "per_repository_size_stratum": PER_STRATUM,
                      "method": "lowest SHA256 of seed, repository and commit, separated by NUL",
                      "size": "added plus deleted lines in included code paths; non-text retained separately",
                      "replacement": "none; retain unverifiable cases in feasibility accounting"},
        "strata": accounting, "cases": selected,
        "interpretation": "feasibility sample only; no correctness labels or evidence admission; excluded from later held-out evaluation",
    }
    report["content_sha256"] = digest(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = select(json.loads(args.census.read_text()))
    with args.out.open("x", encoding="utf-8") as output:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": str(args.out), "cases": len(report["cases"]), "content_sha256": report["content_sha256"]}))


if __name__ == "__main__":
    main()
