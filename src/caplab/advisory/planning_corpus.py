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
import re
import shutil
import subprocess

from ._tuner_vendored import extract_json
from . import cas

#: The prompt contract is claim identity (scar tissue: the v1-changeset
#: quarantine cost a cohort its comparability). plan-v1 demanded acceptance
#: checks "from the checks registry provided in the context" and never
#: supplied one, so its resolvability verdict measured guessing; plan-v2
#: carries a verified index of resolvable check-set ids. Numbers from the two
#: contracts describe different tasks and must never share a cohort.
PLANNING_PROFILE = "plan-v2"
PLANNING_INSTRUMENT = "production-task planning qualification (synthetic contract)"
ORACLE = "striatum-plan-oracle"

PLANNING_PROMPT_V2 = """PLAN ONLY. You are producing an implementation plan; \
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
      "acceptance_checks": ["<a CHECK SETS id, listed below>"]}
   ]}
- Its DEPENDENCIES ARE LEGAL: `depends_on` must be acyclic and every named
  dependency must exist.
- Its CHECKS ARE REAL: every `acceptance_checks` entry must name one of the
  check-set ids listed under CHECK SETS below, exactly as spelled there. That
  list is the whole registry available to you; a named check that resolves to
  nothing is a gate the plan does not have.
- Its WRITE SCOPES ARE REAL: every packet's `write_scope` must name paths
  that exist in or extend the base tree the design describes.
- It IS FINISHABLE: prefer shallow, narrow dependency structure; never split
  one whole-tree-checked unit (a single lint-checked file) across dependent
  packets; every deliverable the design promises must appear in some packet.
"""

CHECK_SETS_HEADER = """
CHECK SETS. These are the only acceptance-check names that resolve. Use these
ids verbatim; anything else is an unresolvable gate.

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


def registry_index(check_sets: list[str]) -> str:
    """The CHECK SETS block: the only acceptance-check names a subject may use.

    Only set ids appear. The registry's 82 checks are identified by content
    hash, so a planner cannot name one meaningfully; its 46 sets carry
    human ids and are the whole nameable surface.
    """
    return CHECK_SETS_HEADER + "".join(f"- {name}\n" for name in check_sets)


def resolvable_check_sets(registry_path: str) -> list[str]:
    """The set ids that the oracle actually resolves today.

    A set may be listed in the registry and still fail to resolve —
    `cli-guards` does, though all five of its member checks are defined —
    so membership is verified against the oracle rather than read off the
    file. Offering a subject a name that cannot resolve would score the
    registry's drift as the planner's defect.
    """
    with open(registry_path, encoding="utf-8") as f:
        listed = sorted(json.load(f).get("sets") or {})
    resolvable = []
    for name in listed:
        probe = {"schema_version": 2,
                 "plan": {"identity": "probe", "version_seq": 1,
                          "content_hash": "0" * 64},
                 "index": ["p1"],
                 "packets": [{"id": "p1", "purpose": "probe",
                              "derived_from": "el:probe",
                              "inputs": ["probe.txt"],
                              "outputs": ["probe.txt"], "depends_on": [],
                              "write_scope": ["probe.txt"],
                              "acceptance_checks": [name]}]}
        verdict = score_graph(probe, registry_path=registry_path)
        checked = verdict.get("resolvability") or {}
        if checked.get("status") == "checked" and not checked.get("unresolvable"):
            resolvable.append(name)
    return resolvable


#: Inputs whose basename starts with this are the full base tree — 98% of the
#: corpus's 2,893 MB. The design-only environment excludes them; the base pin
#: (`00-base-pin`) and the review diagnostics the lane saw are kept.
BASE_INPUT_PREFIX = "01-base"


def render_task_prompt(task: dict, check_sets: list[str],
                       include_base: bool = False,
                       max_bytes: int = 180_000) -> str | None:
    """The planning contract over the task's retained inputs.

    Inputs are concatenated in bundle order under named headers; a task
    whose inputs exceed the budget returns None (refused loudly, not
    truncated silently — a truncated design measures truncation). An empty
    `check_sets` raises: the contract promises a registry, and rendering one
    without it is the plan-v1 defect that made resolvability measure
    guessing.
    """
    if not check_sets:
        raise ValueError("plan-v2 requires a non-empty check-set index; "
                         "rendering without one measures guessing")
    parts = [PLANNING_PROMPT_V2, registry_index(check_sets), "\nCONTEXT:\n"]
    closing = "\nRespond with ONLY the work-graph JSON object.\n"
    total = 0
    for entry in task.get("inputs", []):
        name = (entry.get("path") or "").rsplit("/", 1)[-1]
        if not include_base and name.startswith(BASE_INPUT_PREFIX):
            parts.append(f"\n===== {entry['path']} ===== "
                         f"(base tree withheld in this environment)\n")
            continue
        body = cas.load(entry["sha256"])
        if body is None:
            return None
        total += len(body.encode())
        parts.append(f"\n===== {entry['path']} =====\n{body}\n")
    if total > max_bytes:
        return None
    parts.append(closing)
    return "".join(parts)


#: A step's trailing attempt: the ledger seq, optionally retried.
_ATTEMPT = re.compile(r"\d+(-r\d+)?")


def step_pass(task: dict) -> str:
    """The pass a task belongs to.

    Several tasks share one pass and therefore one accepted design — the
    corpus's 348 tasks span only 117 passes, one of them carrying 29. A
    draw that treats them as independent inflates n, so the pass is the
    sampling unit. `revise` steps carry a trailing attempt number.
    """
    step = task.get("step_id") or "?"
    head, _, tail = step.rpartition("/")
    return head if head and _ATTEMPT.fullmatch(tail) else step


def sample_planning_tasks(tasks: list[dict], *, seed: int, n: int,
                          eligible=None) -> list[dict]:
    """A seeded, pass-disjoint draw balanced on step kind.

    One task per pass, so oracle verdicts are independent rather than
    correlated through a shared design. `produce` and `revise` are drawn in
    equal halves where both are available, so the sample's kind mix is a
    property of the design and not of a shuffle. Selection never reads
    production outcome: filtering on it would select cases by what they
    previously scored.
    """
    import random
    pool = [t for t in tasks if eligible is None or eligible(t)]
    by_kind: dict[str, dict[str, list[dict]]] = {}
    for task in pool:
        kind = (task.get("step_id") or "?").split("/")[0]
        by_kind.setdefault(kind, {}).setdefault(step_pass(task), []).append(task)
    picked: list[dict] = []
    for kind in sorted(by_kind):
        rng = random.Random(f"{seed}:{kind}")
        passes = sorted(by_kind[kind])
        rng.shuffle(passes)
        quota = n // max(1, len(by_kind))
        for name in passes[:quota]:
            # Within a pass the attempt is chosen by the same seed, so a
            # rerun draws the same task and not merely the same pass.
            group = sorted(by_kind[kind][name], key=lambda t: t["task_id"])
            picked.append(group[rng.randrange(len(group))])
    return picked


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
