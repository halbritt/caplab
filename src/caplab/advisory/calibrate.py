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

#: Calibration profile v0 — no stage contract. Retained only to reproduce the
#: 2026-08-16 finding; it cannot admit or quarantine a case, because a
#: reviewer given no contract cannot refuse a contract-relative defect.
REVIEW_PROMPT_V0 = """You are a strict artifact reviewer. Review the artifact \
below for defects: incoherence, missing required content, contradictions, \
broken references, structural damage, or claims the text itself does not \
support. Respond with ONLY a JSON object:
{"verdict": "accept" | "accept_with_findings" | "needs_revision" | "reject",
 "findings": [{"element_anchor": "<anchor or heading>", "text": "<what is wrong>"}]}
Use needs_revision or reject only for defects that genuinely block acceptance.

ARTIFACT:
"""

#: Calibration profile v1 — carries the review contract the measurement
#: prompt supplies. It states general reviewer obligations, the way a review
#: posture does; it deliberately does NOT enumerate defect classes, which
#: would telegraph the injection. The matched-pair design is the check on
#: whether it leads: a leading prompt refuses controls too, and a
#: control-arm refusal is recorded as a false alarm.
REVIEW_PROMPT_V1 = """You are reviewing one artifact produced at a defined \
stage of an engineering pipeline, under a review contract.

THE CONTRACT. An artifact clears review only when all of the following hold:

- It is COMPLETE for its stage. An artifact that states decisions must also
  carry the sections its stage requires (such as the consequences of those
  decisions, the constraints they impose, and what they bind). A required
  part that is absent means the stage contract is unmet, even when what
  remains reads well.
- It is INTERNALLY CONSISTENT. No statement may contradict another, and no
  conclusion may assert what the artifact's own content refutes or fails to
  establish.
- Its REFERENCES RESOLVE. Every cited path, element, or document it points
  at must be reachable and must name something that exists.
- Its DECLARED METADATA MATCHES ITS CONTENT. Any hash, count, level, base,
  or identity the artifact declares about itself must actually equal what it
  describes. A declared value that does not match is a defect regardless of
  how minor the discrepancy looks.
- Its CLAIMS ARE EARNED. An asserted status, level, or completion must be
  supported by what the artifact contains, not merely stated.
- Its SCOPE IS ITS OWN STAGE. It must not carry commitments belonging to a
  later stage.

YOUR JOB. Decide whether this artifact meets the contract. Refuse
(`needs_revision` or `reject`) when it does not, and name the element at
fault. Clear it (`accept` or `accept_with_findings`) when it does — a sound
artifact must be accepted, and inventing a blocker is as much a failure as
missing one.

Respond with ONLY a JSON object:
{"verdict": "accept" | "accept_with_findings" | "needs_revision" | "reject",
 "findings": [{"element_anchor": "<anchor or heading>", "text": "<what is wrong>"}]}

ARTIFACT:
"""

REVIEW_PROMPT = REVIEW_PROMPT_V1
CALIBRATION_PROFILES = {"v0": REVIEW_PROMPT_V0, "v1": REVIEW_PROMPT_V1}


def local_review(body: str, endpoint: str = LOCAL_ENDPOINT,
                 timeout: int = 300, profile: str = "v1") -> dict | None:
    payload = {
        "model": "qwen3.6-35b-a3b",
        "messages": [{"role": "user",
                      "content": CALIBRATION_PROFILES[profile] + body}],
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


def resolve_json_pointer(body: str, pointer: str) -> str:
    """The sub-document an RFC 6901 pointer names, or "" if unresolvable.

    Mirrors bench.resolve_json_pointer / the supervisor's own resolution: a
    lane whose runtime wraps the completion in an envelope is read at the
    payload the driver would admit."""
    doc = extract_json(body)
    if doc is None or not pointer.startswith("/"):
        return ""
    for raw in pointer.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if not isinstance(doc, dict) or token not in doc:
            return ""
        doc = doc[token]
    return doc if isinstance(doc, str) else json.dumps(doc)


def adapter_review(adapter_command: list[str], prompt_mode: str, body: str,
                   timeout: int = 1800, stdout_json_pointer: str = "",
                   profile: str = "v1") -> dict | None:
    """Review one document through a declared adapter command.

    Used for strong-reference case validation: the reference binding sees the
    same compact review prompt the weak reference sees, so weak and strong
    calibrations disagree only about the case, never about the task.

    `stdout_json_pointer` must be honored when the declaration names one.
    The agy family wraps its completion in an envelope and points at
    `/structured_output`; reading raw stdout there finds no `verdict` and
    would score every case a strong miss — falsely quarantining sound cases,
    which is the failure this validation exists to prevent."""
    import subprocess

    prompt = CALIBRATION_PROFILES[profile] + body
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
    stdout = completed.stdout.decode("utf-8", errors="replace")
    if stdout_json_pointer:
        stdout = resolve_json_pointer(stdout, stdout_json_pointer)
    doc = extract_json(stdout)
    return doc if isinstance(doc, dict) else None


def strong_reviewer_from_declaration(backends_root: str, backend_id: str,
                                     timeout: int = 1800, profile: str = "v1"):
    import yaml

    path = os.path.join(backends_root, backend_id, "backend.yaml")
    with open(path, encoding="utf-8") as f:
        declaration = yaml.safe_load(f)
    adapter = declaration["adapter"]

    def reviewer(body: str) -> dict | None:
        return adapter_review(adapter["command"],
                              adapter.get("prompt_mode", "stdin"),
                              body, timeout=timeout,
                              stdout_json_pointer=adapter.get(
                                  "stdout_json_pointer") or "",
                              profile=profile)

    reviewer.reference_name = f"{backend_id}/strong"
    reviewer.profile = profile
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
               "reference": getattr(reviewer, "reference_name", "strong"),
               "calibration_profile": getattr(reviewer, "profile", "v1")}
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
