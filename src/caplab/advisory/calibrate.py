"""Case calibration against reference reviewers (Tier 3 admission protocol).

Principle (Principal guidance, 2026-08-15): when a new case or operator is
tested, reference bindings that *should* pass are run against it first — and
if they don't, the test is questioned before any binding is scored with it.
A sample across a capability spread then estimates per-case difficulty and
finds the floor below which nothing passes; cases under the floor are
flagged, never silently averaged into scores.

This module implements the mechanical part: generate the (control, mutant)
pair for a sampled case, put both arms blindly to a reference reviewer, and
record what happened. The v0 reference is the local llama.cpp endpoint
(free, always available) as the WEAK end of the spread:

- a case the weak reference catches is at or below the easy floor;
- a case it misses stays `pending-strong-reference` until a strong binding
  (claude/codex class, supervised session) has seen it — a weak miss alone
  neither validates nor condemns a case.

Calibration is case QA, not binding measurement: results here never become
scored claims about any binding.
"""

from __future__ import annotations

import json
import os
import random
import urllib.request

from .instrument_defects import NotApplicable
from .operators import BY_NAME, check_present
from ._tuner_vendored import REFUSING, anchors_of, anchor_hits, extract_json

LOCAL_ENDPOINT = "http://localhost:8081/v1/chat/completions"
MAX_SUBSTRATE_BYTES = 60_000  # keep well inside the local slot's context

REVIEW_PROMPT = """You are a strict artifact reviewer. Review the artifact \
below for defects: incoherence, missing required content, contradictions, \
broken references, structural damage, or claims the text itself does not \
support. Respond with ONLY a JSON object:
{"verdict": "accept" | "accept_with_findings" | "needs_revision" | "reject",
 "findings": [{"element_anchor": "<anchor or heading>", "text": "<what is wrong>"}]}
Use needs_revision or reject only for defects that genuinely block acceptance.

ARTIFACT:
"""


def local_review(body: str, endpoint: str = LOCAL_ENDPOINT,
                 timeout: int = 300) -> dict | None:
    payload = {
        "model": "qwen3.6-35b-a3b",
        "messages": [{"role": "user", "content": REVIEW_PROMPT + body}],
        "max_tokens": 2048,
        "temperature": 0.0,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    request = urllib.request.Request(
        endpoint, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content = json.load(response)["choices"][0]["message"]["content"]
    doc = extract_json(content)
    return doc if isinstance(doc, dict) else None


def adapter_review(adapter_command: list[str], prompt_mode: str, body: str,
                   timeout: int = 1800) -> dict | None:
    """Review one document through a declared adapter command.

    Used for strong-reference case validation: the reference binding sees the
    same compact review prompt the weak reference sees, so weak and strong
    calibrations disagree only about the case, never about the task."""
    import subprocess

    prompt = REVIEW_PROMPT + body
    argv = list(adapter_command)
    stdin_data = None
    if prompt_mode == "arg":
        argv.append(prompt)
    else:
        stdin_data = prompt.encode()
    try:
        completed = subprocess.run(argv, input=stdin_data, capture_output=True,
                                   timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    doc = extract_json(completed.stdout.decode("utf-8", errors="replace"))
    return doc if isinstance(doc, dict) else None


def strong_reviewer_from_declaration(backends_root: str, backend_id: str,
                                     timeout: int = 1800):
    import yaml

    path = os.path.join(backends_root, backend_id, "backend.yaml")
    with open(path, encoding="utf-8") as f:
        declaration = yaml.safe_load(f)
    adapter = declaration["adapter"]

    def reviewer(body: str) -> dict | None:
        return adapter_review(adapter["command"],
                              adapter.get("prompt_mode", "stdin"),
                              body, timeout=timeout)

    reviewer.reference_name = f"{backend_id}/strong"
    return reviewer


def validate_pending(calibration_path: str, reviewer, load_body) -> list[dict]:
    """Run pending-strong-reference cases against a strong reference.

    Per the admission protocol: a strong catch validates the case as
    genuinely-hard-but-detectable; a strong miss marks it a quarantine
    CANDIDATE (`strong-miss`) — full quarantine wants 2-3 references and a
    human decision, so one miss never silently drops a case."""
    rows = []
    with open(calibration_path, encoding="utf-8") as f:
        pending = [json.loads(line) for line in f if line.strip()]
    pending = [r for r in pending
               if r.get("difficulty_flag") == "pending-strong-reference"]
    for record in pending:
        case = record["case"]
        row = {"case": case,
               "reference": getattr(reviewer, "reference_name", "strong")}
        body = load_body(case)
        if body is None:
            row["status"] = "substrate-unreachable"
            rows.append(row)
            continue
        materialized = materialize_case(case, body)
        if materialized is None:
            row["status"] = "injection-failed-gate"
            rows.append(row)
            continue
        control, mutant, injection = materialized
        control_doc = reviewer(control)
        mutant_doc = reviewer(mutant)
        if control_doc is None and mutant_doc is None:
            row["status"] = "reference-unparseable"
            rows.append(row)
            continue
        caught = (mutant_doc or {}).get("verdict") in REFUSING
        false_alarm = (control_doc or {}).get("verdict") in REFUSING
        row.update({
            "status": "calibrated",
            "defect_class": injection.defect_class,
            "strong_reference_caught": caught,
            "strong_reference_false_alarm": false_alarm,
            "strong_reference_anchored": bool(caught and anchor_hits(
                injection.element_anchor,
                anchors_of((mutant_doc or {}).get("findings") or []))),
            "difficulty_flag": (
                "validated-hard" if caught and not false_alarm
                else "strong-reference-noisy" if false_alarm
                else "strong-miss-quarantine-candidate"),
        })
        rows.append(row)
    return rows


def materialize_case(case: dict, body: str) -> tuple[str, str, object] | None:
    """(control, mutant, injection) for a sampled case, or None if the
    injection fails its own mechanical gate on this substrate."""
    operator = BY_NAME[case["operator"]]
    try:
        injection = operator(body, random.Random(case["seed"]))
    except NotApplicable:
        return None
    if check_present(injection, injection.body) is False:
        return None
    if check_present(injection, body) is True:
        return None
    return body, injection.body, injection


def calibrate_case(case: dict, body: str, reviewer=local_review) -> dict:
    row = {"case": case, "reference": "local-qwen3.6-35b-a3b/weak"}
    materialized = materialize_case(case, body)
    if materialized is None:
        row.update({"status": "injection-failed-gate"})
        return row
    control, mutant, injection = materialized
    if len(mutant.encode()) > MAX_SUBSTRATE_BYTES:
        row.update({"status": "over-calibration-context"})
        return row
    control_doc = reviewer(control)
    mutant_doc = reviewer(mutant)
    if control_doc is None and mutant_doc is None:
        row.update({"status": "reference-unparseable"})
        return row
    caught = (mutant_doc or {}).get("verdict") in REFUSING
    false_alarm = (control_doc or {}).get("verdict") in REFUSING
    anchored = bool(caught and anchor_hits(
        injection.element_anchor, anchors_of((mutant_doc or {}).get("findings") or [])))
    row.update({
        "status": "calibrated",
        "defect_class": injection.defect_class,
        "defect_anchor": injection.element_anchor,
        "weak_reference_caught": caught,
        "weak_reference_false_alarm": false_alarm,
        "weak_reference_anchored": anchored,
        "difficulty_flag": (
            "at-or-below-easy-floor" if caught and not false_alarm
            else "weak-reference-noisy" if false_alarm
            else "pending-strong-reference"),
    })
    return row


def load_substrate_body(case: dict, exchange_root: str | None,
                        repos: dict[str, str]) -> str | None:
    source = case["source"]
    if source["kind"] == "striatum-exchange" and exchange_root:
        path = os.path.join(exchange_root, "dispatch", source["dispatch_id"],
                            source["input_path"])
    elif source["kind"] == "repo-doc" and source.get("repo") in repos:
        path = os.path.join(repos[source["repo"]], source["path"])
    else:
        return None
    if not os.path.isfile(path):
        return None
    with open(path, errors="replace", encoding="utf-8") as f:
        return f.read()
