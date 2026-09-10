#!/usr/bin/env python3
"""Check retained behavior against pre-execution criteria, without reviewer scoring."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from reviewer_timeout_witness import COMMITS, CONDITIONS, sha, write_json


def assess(observation: dict, condition: str, criteria: dict) -> dict:
    if observation.get("schema") != "caplab.council-provider-lifetime-observation/v1" or observation.get("condition") != condition:
        raise ValueError("observation identity mismatch")
    if type(observation.get("requests")) is not int or observation["requests"] < 0:
        raise ValueError("invalid request count")
    timeline = {}
    previous = -1.0
    for event in observation["events"]:
        ms = event["ms"]
        if type(ms) not in (float, int) or not math.isfinite(ms) or ms < previous:
            raise ValueError("invalid event chronology")
        if event["event"] in timeline:
            raise ValueError("ambiguous repeated event")
        timeline[event["event"]] = ms
        previous = ms
    required = criteria[condition]["required_events"]
    if any(event not in timeline for event in required):
        raise ValueError("missing events needed to assess the requested condition")
    if any(timeline[a] > timeline[b] for a, b in zip(required, required[1:])):
        raise ValueError("condition events occurred out of order")
    if timeline["turn-returned"] < timeline["turn-invoked"]:
        raise ValueError("turn returned before invocation")
    expected = criteria[condition]
    result = observation["result"]
    mismatches = []
    if observation["requests"] != expected["requests"]:
        mismatches.append("requests")
    for field in ("status", "code", "phase", "dispatched", "reply"):
        if field in expected and (type(result.get(field)) is not type(expected[field]) or result[field] != expected[field]):
            mismatches.append(field)
    if expected.get("body_ended_before_return") is False:
        if "body-ended" in timeline and timeline["body-ended"] <= timeline["turn-returned"]:
            mismatches.append("body-ended-before-return")
    for origin, key in (("headers-flushed", "maximum_ms_from_headers_to_return"),
                        ("service-aborted", "maximum_ms_from_abort_to_return")):
        if key in expected and timeline["turn-returned"] - timeline[origin] > expected[key]:
            mismatches.append(key)
    return {"property_satisfied": not mismatches, "mismatches": mismatches,
            "turn_elapsed_ms": timeline["turn-returned"] - timeline["turn-invoked"]}


def verify(root: Path, plan_hash: str, criteria_hash: str) -> dict:
    plan_raw, criteria_raw = (root / "plan.json").read_bytes(), (root / "criteria.json").read_bytes()
    if sha(plan_raw) != plan_hash or sha(criteria_raw) != criteria_hash:
        raise ValueError("plan or criteria hash mismatch")
    plan, criteria = json.loads(plan_raw), json.loads(criteria_raw)
    if sha((root / "witness/probe.mts").read_bytes()) != plan["probe_sha256"]:
        raise ValueError("probe hash mismatch")
    completion = json.loads((root / "run-complete.json").read_text())
    if completion["launches"] != 36 or completion["plan_sha256"] != plan_hash:
        raise ValueError("run series is incomplete or bound to a different plan")
    rows = []
    for role, commit in COMMITS.items():
        snapshot = plan["snapshots"][role]
        if snapshot["commit"] != commit:
            raise ValueError("source role mismatch")
        source = next(entry for entry in snapshot["files"] if entry["path"] == "src/v3/deepseek-runtime.ts")
        for condition in CONDITIONS:
            for repetition in range(1, 4):
                slot = root / f"{role}-{condition}-{repetition}"
                exit_result = json.loads((slot / "completion.json").read_text())
                if exit_result != {"exit_code": 0, "timed_out": False}:
                    raise ValueError("diagnostic process did not complete normally")
                raw = (slot / "stdout").read_bytes()
                observation = json.loads(raw)
                if observation["source_sha256"] != source["sha256"]:
                    raise ValueError("observed source differs from pinned source")
                rows.append({"role": role, "commit": commit, "condition": condition,
                             "repetition": repetition, "stdout_sha256": sha(raw),
                             "result": observation["result"], "requests": observation["requests"],
                             **assess(observation, condition, criteria)})
    return {"schema": "caplab.council-provider-lifetime-verification/v1",
            "plan_sha256": plan_hash, "criteria_sha256": criteria_hash, "observations": rows,
            "interpretation": "Observed bounded properties of one related failure family; not whole-patch cleanliness, independent incident count or reviewer performance"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--plan-sha256", required=True)
    parser.add_argument("--criteria-sha256", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    report = verify(args.root, args.plan_sha256, args.criteria_sha256)
    write_json(args.out, report)
    print(json.dumps({"observations": len(report["observations"]), "out": str(args.out)}))


if __name__ == "__main__":
    main()
