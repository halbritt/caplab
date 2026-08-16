"""Measure a binding on Tier 3 pool cases, under the synthetic-contract profile.

The pinned instrument selects its own cases by seeded shuffle over exchange
dispatches, so the Tier 3 pool's partitioning, class balancing and per-sweep
seeds governed nothing that actually got scored. This runner closes that gap
without touching the instrument: CAPLAB draws the cases, renders its own
prompt carrying the review contract, and invokes the subject through the
exact adapter command its declaration pins.

What is gained: the whole pool becomes measurable, including the 300-odd
repo-doc substrates that carry no dispatch bundle, and every knob the pool
provides (sealed/open, class balance, per-sweep seed variation) now applies
to real measurement.

What is given up, and must be named on every claim: this is a
contract-bearing review task, not striatum's exact dispatch. The instrument
renders a specific posture, pins, and expected outputs that this profile
does not reproduce. Numbers from the two profiles describe different tasks
and are written to separate run roots so they cannot merge by accident.

Blinding is preserved: the two arms are separate invocations in a workspace
that carries no marker of which is which, and the arm order per case is
derived from the case seed rather than fixed.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import random
import subprocess
import time

import yaml

from ._tuner_vendored import REFUSING, anchor_hits, anchors_of, extract_json
from .calibrate import CALIBRATION_PROFILES, resolve_json_pointer
from .corpus import SubstrateRegistry, sample_cases
from .instrument_defects import NotApplicable
from .operators import BY_NAME, check_present

SYNTHETIC_CONTRACT_INSTRUMENT = "matched-pair defect injection (synthetic contract)"
MEASUREMENT_PROFILE = "v1"

#: Well below the kernel's per-argument limit, leaving room for the rest of
#: argv and the environment. A body larger than this is delivered on stdin
#: and the row records that the transport differed — the audit harness hit
#: exactly this ceiling on 2026-08-16 and died rather than adapting.
MAX_ARG_BYTES = 100_000


def load_declaration(backends_root: str, backend_id: str) -> dict:
    path = os.path.join(backends_root, backend_id, "backend.yaml")
    with open(path, encoding="utf-8") as f:
        declaration = yaml.safe_load(f)
    if declaration.get("id") != backend_id:
        raise ValueError(f"{path} declares id {declaration.get('id')!r}")
    return declaration


def invoke(adapter: dict, prompt: str, timeout: int) -> dict:
    argv = list(adapter["command"])
    prompt_mode = adapter.get("prompt_mode", "stdin")
    encoded = prompt.encode()
    transport = prompt_mode
    stdin_data = None
    if prompt_mode == "arg" and len(encoded) <= MAX_ARG_BYTES:
        argv.append(prompt)
    else:
        if prompt_mode == "arg":
            transport = "stdin-oversize-fallback"
        stdin_data = encoded

    started = time.time()
    try:
        completed = subprocess.run(argv, input=stdin_data, capture_output=True,
                                   timeout=timeout)
        stdout = completed.stdout.decode("utf-8", errors="replace")
        code = completed.returncode
    except subprocess.TimeoutExpired:
        stdout, code = "", -1
    body = stdout
    pointer = adapter.get("stdout_json_pointer")
    if pointer:
        body = resolve_json_pointer(stdout, pointer)
    doc = extract_json(body)
    return {
        "doc": doc if isinstance(doc, dict) else None,
        "exit_code": code,
        "seconds": round(time.time() - started, 1),
        "transport": transport,
        "prompt_bytes": len(encoded),
        "raw_head": stdout[:400],
    }


def measure_case(case: dict, body: str, adapter: dict, timeout: int) -> dict:
    """One matched pair. Returns a row in the instrument's own shape."""
    row = {"dispatch_id": f"{case['substrate_id']}:{case['operator']}:{case['seed']}",
           "substrate_id": case["substrate_id"],
           "source_kind": case["source"]["kind"],
           "defect_class": case["operator"],
           "calibration_profile": MEASUREMENT_PROFILE}
    operator = BY_NAME.get(case["operator"])
    if operator is None:
        return {**row, "usable": False, "error": "unknown operator"}
    try:
        injection = operator(body, random.Random(case["seed"]))
    except NotApplicable as e:
        return {**row, "usable": False, "error": f"not applicable: {e}"}

    # Mechanical gate, before any model sees the pair.
    if check_present(injection, injection.body) is False:
        return {**row, "usable": False, "error": "injection failed its own check"}
    if check_present(injection, body) is True:
        return {**row, "usable": False, "error": "control already carries the defect"}

    prompt = CALIBRATION_PROFILES[MEASUREMENT_PROFILE]
    arms = [("control", body), ("mutant", injection.body)]
    # Arm order varies per case so a subject cannot benefit from position.
    random.Random(case["seed"] ^ 0x5EED).shuffle(arms)
    results = {}
    for name, arm_body in arms:
        results[name] = invoke(adapter, prompt + arm_body, timeout)

    control, mutant = results["control"], results["mutant"]
    if control["doc"] is None and mutant["doc"] is None:
        return {**row, "usable": False,
                "error": "no parseable review on either arm",
                "control_head": control["raw_head"],
                "mutant_head": mutant["raw_head"]}

    control_verdict = (control["doc"] or {}).get("verdict")
    mutant_verdict = (mutant["doc"] or {}).get("verdict")
    emitted = anchors_of((mutant["doc"] or {}).get("findings") or [])
    return {
        **row,
        "usable": True,
        "defect_anchor": injection.element_anchor,
        "defect_severity": injection.severity,
        "defect_checkable": injection.checkable,
        "control_verdict": control_verdict,
        "mutant_verdict": mutant_verdict,
        "caught": mutant_verdict in REFUSING,
        "false_alarm": control_verdict in REFUSING,
        "anchor_hit": bool(anchor_hits(injection.element_anchor, emitted)),
        "anchors_emitted": emitted[:8],
        "mutant_findings": len((mutant["doc"] or {}).get("findings") or []),
        "control_json_valid": control["doc"] is not None,
        "mutant_json_valid": mutant["doc"] is not None,
        "control_seconds": control["seconds"], "mutant_seconds": mutant["seconds"],
        "control_transport": control["transport"], "mutant_transport": mutant["transport"],
        "estimated_input_tokens": int(mutant["prompt_bytes"] / 3.04),
        "error": None,
    }


def run_pool(*, backend: str, backends_root: str, registry_path: str,
             out_dir: str, sweep_seed: int, per_operator: int,
             partition: str = "open", timeout: int = 1800,
             max_cases: int = 40, abort_after_empty: int = 8) -> dict:
    """Measure one binding over a sampled slice of the pool."""
    declaration = load_declaration(backends_root, backend)
    adapter = declaration["adapter"]
    substrates = SubstrateRegistry(registry_path).read()
    cases = sample_cases(substrates, sweep_seed=sweep_seed,
                         per_operator=per_operator, partition=partition)
    if len(cases) > max_cases:
        cases = cases[:max_cases]

    os.makedirs(out_dir, exist_ok=True)
    results_path = os.path.join(out_dir, "results.jsonl")
    done = set()
    if os.path.isfile(results_path):
        with open(results_path, encoding="utf-8") as f:
            done = {json.loads(line)["dispatch_id"] for line in f if line.strip()}

    from .calibrate import load_substrate_body

    exchange = os.path.expanduser(
        "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
    repos = {"caplab": os.path.expanduser("~/git/caplab"),
             "striatum-next": os.path.expanduser("~/git/striatum-next")}

    empty_streak = 0
    aborted = None
    started_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
    with open(results_path, "a", encoding="utf-8") as out:
        for index, case in enumerate(cases, 1):
            case_id = f"{case['substrate_id']}:{case['operator']}:{case['seed']}"
            if case_id in done:
                continue
            body = load_substrate_body(case, exchange, repos)
            if body is None:
                row = {"dispatch_id": case_id, "usable": False,
                       "error": "substrate unreachable",
                       "defect_class": case["operator"]}
            else:
                row = measure_case(case, body, adapter, timeout)
            row["backend_measured"] = backend
            out.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            out.flush()
            os.fsync(out.fileno())
            print(f"[{index}/{len(cases)}] {case['operator']:28} "
                  f"{'usable' if row.get('usable') else row.get('error','')}"
                  f"{' CAUGHT' if row.get('caught') else ''}"
                  f"{' FALSE-ALARM' if row.get('false_alarm') else ''}", flush=True)

            if row.get("error") == "no parseable review on either arm":
                empty_streak += 1
                if abort_after_empty and empty_streak >= abort_after_empty:
                    aborted = f"{empty_streak} consecutive empty lanes"
                    break
            elif row.get("usable"):
                empty_streak = 0

    with open(results_path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    usable = [r for r in rows if r.get("usable")]
    summary = {
        "backend": backend,
        "instrument": SYNTHETIC_CONTRACT_INSTRUMENT,
        "calibration_profile": MEASUREMENT_PROFILE,
        "sweep_seed": sweep_seed,
        "partition": partition,
        "pairs_usable": len(usable),
        "pairs_discarded": len(rows) - len(usable),
        "catch_rate": (sum(1 for r in usable if r["caught"]) / len(usable)
                       if usable else None),
        "false_alarm_rate": (sum(1 for r in usable if r["false_alarm"]) / len(usable)
                             if usable else None),
        "started_at": started_at,
        "finished_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "aborted": aborted,
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    return summary
