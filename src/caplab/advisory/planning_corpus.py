"""Arm 1 of the planning constructs: corpus harvest and oracle scoring.

Per the capability card (`planning-constructs-v1.md`): a fixed corpus of
planning tasks from real campaigns. Every `implementation-planning`
dispatch bundle on the exchange is a task — the accepted design, the base
pin, and the packet context the production lane received. CAPLAB renders
its own planning contract over those inputs (the synthetic-contract
precedent: striatum's rendered dispatch prompt is not reproduced, and
every claim names the profile), the subject produces a work-graph
lowering, and `striatum-plan-oracle` scores it mechanically. The oracle
binary's sha256 rides every scored document.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess

from ._tuner_vendored import extract_json
from . import cas

PLANNING_PROFILE = "plan-v1"
PLANNING_INSTRUMENT = "production-task planning qualification (synthetic contract)"
ORACLE = "striatum-plan-oracle"

PLANNING_PROMPT_V1 = """PLAN ONLY. You are producing an implementation plan; \
you are not building, executing, or modifying anything. Do not create, \
modify, delete, or write any file anywhere. The filesystem is not the task: \
judge and reference only the material presented below.

You are the implementation planner for one engineering step. From the design
and context below, produce the step's WORK GRAPH: the packetization of the
work into ordered, verifiable packets.

THE CONTRACT. A work graph is acceptable only when all of the following hold:
- It PARSES: emit exactly one JSON object matching EXACTLY this skeleton —
  no additional fields anywhere (the parser rejects unknown fields):

  {"schema_version": 2,
   "plan": {"identity": "<step identity>", "version_seq": 1,
            "content_hash": "<leave as 64 zeros>"},
   "index": ["p1"],
   "packets": [
     {"id": "p1", "purpose": "<one sentence>",
      "derived_from": "<design element anchor, a single string>",
      "inputs": ["<path>"], "outputs": ["<deliverable path>"],
      "depends_on": [],
      "write_scope": ["<path prefix>"],
      "acceptance_checks": ["<check or set name from the registry>"]}
   ]}
- Its DEPENDENCIES ARE LEGAL: `depends_on` must be acyclic and every named
  dependency must exist.
- Its CHECKS ARE REAL: every `acceptance_checks` entry must name a check or
  set from the checks registry provided in the context; a named check that
  resolves to nothing is a gate the plan does not have.
- Its WRITE SCOPES ARE REAL: every packet's `write_scope` must name paths
  that exist in or extend the base tree the design describes.
- It IS FINISHABLE: prefer shallow, narrow dependency structure; never split
  one whole-tree-checked unit (a single lint-checked file) across dependent
  packets; every deliverable the design promises must appear in some packet.

Respond with ONLY the work-graph JSON object.

CONTEXT:
"""


def harvest_planning_tasks(events: list[dict]) -> list[dict]:
    """Task records for every bound implementation-planning run."""
    runs = {e["seq"]: e for e in events
            if e.get("type") == "pass_run_opened"
            and e.get("payload", {}).get("pass_id") == "implementation-planning"}
    closed = {e["payload"].get("run_ref"): e["payload"].get("outcome")
              for e in events if e.get("type") == "pass_run_closed"}
    tasks = []
    for e in events:
        if e.get("type") != "lane_binding":
            continue
        run = e["payload"].get("run_ref")
        if run not in runs:
            continue
        manifest = runs[run].get("payload", {}).get("manifest", {})
        tasks.append({
            "record": "caplab-planning-task/1",
            "task_id": "pt-" + e["payload"]["dispatch_id"][:16],
            "dispatch_id": e["payload"]["dispatch_id"],
            "run_ref": run,
            "step_id": manifest.get("step_id"),
            "production_backend": e["payload"].get("backend_id"),
            "production_outcome": closed.get(run),
        })
    return tasks


def retain_task_inputs(task: dict, exchange_root: str) -> dict | None:
    """Copy the bundle's inputs into the advisory CAS; return the task with
    input hashes pinned, or None if the bundle is gone."""
    bundle = os.path.join(exchange_root, "dispatch", task["dispatch_id"])
    manifest_path = os.path.join(bundle, "manifest.json")
    if not os.path.isfile(manifest_path):
        return None
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    inputs = []
    for entry in manifest.get("inputs", []):
        path = os.path.join(bundle, entry.get("path", ""))
        if not os.path.isfile(path):
            continue
        body = open(path, encoding="utf-8", errors="replace").read()
        inputs.append({"path": entry.get("path"),
                       "sha256": cas.retain(body),
                       "bytes": len(body.encode())})
    out = dict(task)
    out["inputs"] = inputs
    out["manifest_sha256"] = cas.retain(
        json.dumps(manifest, sort_keys=True, ensure_ascii=False))
    return out


def render_task_prompt(task: dict, max_bytes: int = 180_000) -> str | None:
    """The planning contract over the task's retained inputs.

    Inputs are concatenated in bundle order under named headers; a task
    whose inputs exceed the budget returns None (refused loudly, not
    truncated silently — a truncated design measures truncation).
    """
    parts = [PLANNING_PROMPT_V1]
    total = 0
    for entry in task.get("inputs", []):
        body = cas.load(entry["sha256"])
        if body is None:
            return None
        total += len(body.encode())
        parts.append(f"\n===== {entry['path']} =====\n{body}\n")
    if total > max_bytes:
        return None
    return "".join(parts)


def normalize_graph(graph: dict, task: dict) -> dict:
    """Fill the plan pin the way the production driver would.

    The plan block's identity/version_seq/content_hash are store
    bookkeeping the driver stamps at admission; a measured subject cannot
    know them and inventing them measures nothing. The subject's actual
    work — index and packets — is passed through untouched, and the
    normalization is recorded on every scored document.
    """
    out = dict(graph)
    out["plan"] = {"identity": (task.get("step_id") or "measured-task"),
                   "version_seq": 1,
                   "content_hash": hashlib.sha256(json.dumps(
                       graph.get("packets", []), sort_keys=True).encode()
                   ).hexdigest()}
    out.setdefault("index", [p.get("id") for p in graph.get("packets", [])])
    out.setdefault("schema_version", 2)
    return out


def extract_work_graph(output: str) -> dict | None:
    doc = extract_json(output or "")
    if isinstance(doc, dict) and ("packets" in doc or "plan" in doc):
        return doc
    return None


def oracle_identity() -> dict:
    path = shutil.which(ORACLE)
    if path is None:
        raise FileNotFoundError(f"{ORACLE} is not installed")
    version = subprocess.run([path, "-version"], capture_output=True,
                             text=True).stdout.strip()
    return {"path": path, "version": version,
            "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest()}


def score_graph(graph: dict, registry_path: str | None = None,
                tree_path: str | None = None) -> dict:
    """One oracle verdict document for one produced graph."""
    ident = oracle_identity()
    argv = [ident["path"]]
    if registry_path:
        argv += ["-registry", registry_path]
    if tree_path:
        argv += ["-tree", tree_path]
    result = subprocess.run(argv, input=json.dumps(graph).encode(),
                            capture_output=True, timeout=120)
    if result.returncode != 0:
        return {"oracle_failed": result.stderr.decode()[:400],
                "oracle": ident}
    verdict = json.loads(result.stdout)
    verdict["oracle"] = ident
    return verdict
