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
import hashlib
import json
import os
import random
import subprocess
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import yaml

from ._tuner_vendored import REFUSING, anchor_hits, anchors_of, extract_json
from .calibrate import (CALIBRATION_PROFILES, REVIEW_PREAMBLE_VERSION,
                        profile_for_artifact, resolve_json_pointer)
from .corpus import SubstrateRegistry, sample_cases, targeted_cases
from .instrument_defects import NotApplicable
from .operators import BY_NAME, check_present

SYNTHETIC_CONTRACT_INSTRUMENT = "matched-pair defect injection (synthetic contract)"
MEASUREMENT_PROFILE = "v1"

#: The execution environment is part of claim identity (Principal ruling,
#: 2026-08-23). Isolation moved one arm's catch by ~25 points while its
#: unmounted control moved 5, so a claim measured with ambient checkout
#: access and one measured without describe different tasks — the
#: v1-changeset comparability lesson at the environment level. Bump this
#: whenever the lane's visible universe changes; runs before the field
#: existed carry no environment and are cohorted apart from all of them.
#:
#: iso-v1 (2026-08-23): bubblewrap containment, ~/git masked entirely,
#: neutral case-workspace cwd, declaration-pinned files re-exposed
#: read-only, review preamble v2. Successor work: materialize the task's
#: pinned base into the workspace (bundle-faithful affordance).
ENVIRONMENT_VERSION = "iso-v1"

#: Well below the kernel's per-argument limit, leaving room for the rest of
#: argv and the environment. A prompt larger than this cannot ride argv; its
#: body is spilled to a workspace file and referenced by path, and if even
#: the spilled prompt overflows, the arm is refused loudly. There is no
#: stdin fallback: an arg-mode CLI never reads stdin, and rerouting there
#: recorded eight unasked questions as unanswered ones in sweep 20260817.
MAX_ARG_BYTES = 100_000


def declared_lanes(declaration: dict) -> int:
    """The concurrency the declaration itself permits.

    A sweep must not exceed it. The number is part of the Binding: running
    more lanes than the declaration sanctions measures a configuration that
    striatum never dispatches, and it invites the rate limiting that turns a
    run into a row of empty lanes.
    """
    concurrency = ((declaration.get("capabilities") or {})
                   .get("concurrency") or {})
    try:
        return max(1, int(concurrency.get("max_lanes", 1)))
    except (TypeError, ValueError):
        return 1


def load_declaration(backends_root: str, backend_id: str) -> dict:
    path = os.path.join(backends_root, backend_id, "backend.yaml")
    with open(path, encoding="utf-8") as f:
        declaration = yaml.safe_load(f)
    if declaration.get("id") != backend_id:
        raise ValueError(f"{path} declares id {declaration.get('id')!r}")
    return declaration


def sandbox_available() -> bool:
    import shutil
    return shutil.which("bwrap") is not None and not os.environ.get(
        "CAPLAB_NO_SANDBOX")


def adapter_resources(command: list[str]) -> list[str]:
    """Absolute-path files the adapter command itself references.

    A declaration may pin resources by path (agy pins its --json-schema
    under the striatum-next checkout). Masking the checkouts must not break
    the declared adapter, so exactly these files are re-exposed read-only —
    files the declaration names, never directories, never anything the
    artifact names.
    """
    out = []
    for arg in command:
        if isinstance(arg, str) and arg.startswith("/") \
                and os.path.isfile(arg):
            out.append(arg)
    return out


#: Home paths a lane must never see. Plan tree-v1 rev 2 §0/§2.2 (Stage A,
#: 2026-09-06): between 2026-08-23 and this change every lane could read and
#: write the graph store, the exchange, the tuner's eval runs, the whole cache
#: and the Plane tokens, because home was bound writable beneath the ~/git
#: mask. Each is now a tmpfs; what a harness needs back is re-bound on top.
MASKED_HOME_PATHS = ("~/.local/share/striatum", "~/.local/share/striatum-tuner",
                     "~/.config/plane", "~/.cache")

#: Environment assignments in an adapter command that name the directory a
#: harness keeps its own state in. That directory — and only that one — is
#: re-bound writable inside the striatum mask.
HARNESS_STATE_VARS = ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "HOME")


def harness_rebinds(argv: list[str]) -> list[str]:
    """Absolute directories the lane's own harness needs writable.

    Read off the adapter command's `env VAR=value` assignments, never
    guessed from the harness name: the declaration is the authority on where
    a harness keeps state. agy's GOCACHE lands under the masked ~/.cache and
    is re-bound too. opencode uses the real home; its two directories are not
    under any mask and need nothing here.
    """
    home = os.path.expanduser("~")
    out = []
    for arg in argv:
        if not isinstance(arg, str) or "=" not in arg:
            continue
        key, _, value = arg.partition("=")
        if key in HARNESS_STATE_VARS or key == "GOCACHE":
            path = os.path.abspath(os.path.expanduser(value))
            if path != home and path.startswith(home + os.sep) and os.path.isdir(path):
                out.append(path)
    return out


def sandbox_argv(argv: list[str], workspace: str | None,
                 extra_ro: list[str] | None = None) -> list[str]:
    """Contain a lane: the checkouts and the store do not exist inside it.

    On 2026-08-23 a replayed build case's delivery was written by an agy
    lane into the live striatum-next checkout, byte-identical to the case
    body (postmortem scheduler-overwrite-postmortem-2026-08-23); a sibling
    case 26 seconds later named a file carrying uncommitted repair work.
    The replayed prompts name live repository paths by design, and an
    agentic harness acts on what it is shown — so the escape is contained
    at the filesystem, not argued away in the prompt.

    Stage A (2026-09-06, plan tree-v1 rev 2 §2.2): home stays writable for
    the harness's benefit, but ~/git, the striatum store, the tuner's runs,
    the cache and the Plane tokens are each a tmpfs; the harness's own config
    directory (and GOCACHE, for agy) is re-bound writable on top; only the
    case workspace is otherwise re-bound writable. Stage B (the allowlisted
    synthetic home) replaces this before any model process runs.
    """
    home = os.path.expanduser("~")
    git_root = os.path.join(home, "git")
    if workspace:
        # bwrap binds and the lane cwd must be absolute: a relative
        # workspace resolved against a masked parent silently loses to the
        # tmpfs and every invocation dies with exit 1 (both isolation
        # sweeps of 2026-08-23 did exactly that).
        workspace = os.path.abspath(workspace)
    wrapped = ["bwrap", "--ro-bind", "/", "/", "--bind", home, home]
    if os.path.isdir(git_root):
        # MASKED, not merely read-only: on 2026-08-23 two reviews resolved
        # a change set's file references against the caplab tree the lane
        # was mounted in — the read-only cousin of the replay escape. The
        # visible universe is the artifact; the checkouts do not exist
        # inside a lane. (Absent git root: a CI runner keeps its checkout
        # elsewhere; binding a missing path refuses to start.)
        wrapped += ["--tmpfs", git_root]
    for masked in MASKED_HOME_PATHS:
        path = os.path.expanduser(masked)
        if os.path.isdir(path):
            wrapped += ["--tmpfs", path]
    for path in harness_rebinds(argv):
        wrapped += ["--bind", path, path]
    for path in extra_ro or []:
        wrapped += ["--ro-bind", path, path]
    wrapped += ["--bind", "/tmp", "/tmp"]
    if workspace:
        os.makedirs(workspace, exist_ok=True)
        wrapped += ["--bind", workspace, workspace]
    wrapped += ["--dev", "/dev", "--proc", "/proc", "--die-with-parent", "--"]
    return wrapped + list(argv)


def invoke(adapter: dict, prompt: str, timeout: int,
           workspace: str | None = None) -> dict:
    argv = list(adapter["command"])
    sandbox = "none"
    if sandbox_available():
        if workspace:
            os.makedirs(workspace, exist_ok=True)
        argv = sandbox_argv(argv, workspace,
                            extra_ro=adapter_resources(adapter["command"]))
        sandbox = "bwrap"
    # The lane's cwd is the neutral case workspace, never a repository:
    # a subject that "looks around" finds only its own spill file.
    run_cwd = (os.path.abspath(workspace)
               if workspace and os.path.isdir(workspace) else None)
    prompt_mode = adapter.get("prompt_mode", "stdin")
    encoded = prompt.encode()
    transport = prompt_mode
    stdin_data = None
    if prompt_mode == "arg":
        if len(encoded) > MAX_ARG_BYTES:
            # An arg-mode CLI never reads stdin. Rerouting an oversize prompt
            # there asks nothing and records the silence as the subject's
            # answer (every discard in sweep 20260817 was this). Refuse
            # without invoking, so an unasked question can never look like an
            # unanswered one.
            return {"doc": None, "exit_code": None, "timed_out": False,
                    "seconds": 0.0, "transport": "none",
                    "prompt_bytes": len(encoded), "raw_head": "",
                    "sandbox": sandbox,
                    "error": "prompt exceeds transport capacity"}
        argv.append(prompt)
    else:
        stdin_data = encoded

    started = time.time()
    timed_out = False
    try:
        completed = subprocess.run(argv, input=stdin_data, capture_output=True,
                                   timeout=timeout, cwd=run_cwd)
        stdout = completed.stdout.decode("utf-8", errors="replace")
        code = completed.returncode
    except subprocess.TimeoutExpired:
        stdout, code, timed_out = "", None, True
    body = stdout
    pointer = adapter.get("stdout_json_pointer")
    if pointer:
        body = resolve_json_pointer(stdout, pointer)
    doc = extract_json(body)
    return {
        "doc": doc if isinstance(doc, dict) else None,
        "exit_code": code,
        "timed_out": timed_out,
        "seconds": round(time.time() - started, 1),
        "transport": transport,
        "prompt_bytes": len(encoded),
        "raw_head": stdout[:400],
        "sandbox": sandbox,
        "error": None,
    }


def _prepare_prompt(contract: str, arm_body: str, adapter: dict,
                    workspace: str | None) -> tuple:
    """(prompt, transport label) for one arm, spilling when argv cannot carry it.

    Striatum's own renderer spills argv-mode input bodies to files and
    references them by path when the prompt overflows; an agentic subject
    reads the file itself. The label is None for a plain inline prompt, and
    (None, None) means no transport can carry the arm — the caller must
    refuse loudly, never reroute. The spill filename derives from the body's
    content, so it carries no marker of which arm it belongs to.
    """
    prompt = contract + arm_body
    if (adapter.get("prompt_mode", "stdin") != "arg"
            or len(prompt.encode()) <= MAX_ARG_BYTES):
        return prompt, None
    if workspace is None:
        workspace = tempfile.mkdtemp(prefix="caplab-spill-")
    os.makedirs(workspace, exist_ok=True)
    name = hashlib.sha256(arm_body.encode()).hexdigest()[:16] + ".txt"
    path = os.path.abspath(os.path.join(workspace, name))
    with open(path, "w", encoding="utf-8") as f:
        f.write(arm_body)
    spilled = (contract
               + "The body under review is too large to inline. Read it in "
                 "full from this file before deciding: " + path + "\n")
    if len(spilled.encode()) > MAX_ARG_BYTES:
        return None, None
    return spilled, "arg-spill"


def _majority(verdicts: list) -> tuple:
    """(majority verdict, refusing count, total). Ties resolve to refusing.

    A tie means the subject is genuinely on the fence, and the conservative
    reading of a fence-sitting reviewer is that it refused — the alternative
    silently credits the arm with a clearance it did not consistently give.
    The split is recorded either way, so no reader has to trust this choice.
    """
    real = [v for v in verdicts if v is not None]
    if not real:
        return None, 0, 0
    refusing = sum(1 for v in real if v in REFUSING)
    if refusing * 2 >= len(real):
        return next(v for v in real if v in REFUSING), refusing, len(real)
    return next(v for v in real if v not in REFUSING), refusing, len(real)


def measure_case(case: dict, body: str, adapter: dict, timeout: int,
                 replicates: int = 1, mutant_replicates: int | None = None,
                 workspace: str | None = None) -> dict:
    """One matched pair, optionally replicated.

    Replication exists because the control arm reproduces at ~53% on identical
    inputs while the mutant arm reproduces at ~80-87% (finding of 2026-08-16).
    A single-trial false-alarm rate therefore does not describe a binding.
    Every replicate verdict is recorded, not just the majority, so reliability
    can be recomputed later without paying for the calls again.
    """
    row = {"dispatch_id": f"{case['substrate_id']}:{case['operator']}:{case['seed']}",
           "substrate_id": case["substrate_id"],
           "source_kind": case["source"]["kind"],
           "defect_class": case["operator"]}
    row.setdefault("calibration_profile", MEASUREMENT_PROFILE)
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

    profile = profile_for_artifact(body)
    row["calibration_profile"] = profile
    prompt = CALIBRATION_PROFILES[profile]
    arms = [("control", body), ("mutant", injection.body)]
    # Arm order varies per case so a subject cannot benefit from position.
    random.Random(case["seed"] ^ 0x5EED).shuffle(arms)
    per_arm = {"control": max(1, replicates),
               "mutant": max(1, replicates if mutant_replicates is None
                             else mutant_replicates)}
    results, replicate_verdicts = {}, {}
    for name, arm_body in arms:
        prompt_text, transport_label = _prepare_prompt(prompt, arm_body,
                                                       adapter, workspace)
        if prompt_text is None:
            runs = [{"doc": None, "exit_code": None, "timed_out": False,
                     "seconds": 0.0, "transport": "none",
                     "prompt_bytes": len((prompt + arm_body).encode()),
                     "raw_head": "",
                     "error": "prompt exceeds transport capacity"}]
        else:
            runs = [invoke(adapter, prompt_text, timeout,
                           workspace=workspace)
                    for _ in range(per_arm[name])]
            if transport_label:
                for r in runs:
                    r["transport"] = transport_label
        replicate_verdicts[name] = [(r["doc"] or {}).get("verdict") for r in runs]
        results[name] = runs

    def representative(name: str, majority_verdict) -> dict:
        """The retained capture must agree with the verdict the row reports.

        Keeping the first parseable replicate lost qs-9f2748c49dd3313e's
        refusal reasons in sweep 20260817: the row said refused while its
        findings came from the one accepting replicate.
        """
        runs = results[name]
        parseable = [r for r in runs if r["doc"] is not None]
        if majority_verdict is not None:
            aligned = [r for r in parseable
                       if (r["doc"].get("verdict") in REFUSING)
                       == (majority_verdict in REFUSING)]
            if aligned:
                return aligned[0]
        return parseable[0] if parseable else runs[0]

    control_majority, _, _ = _majority(replicate_verdicts["control"])
    mutant_majority, _, _ = _majority(replicate_verdicts["mutant"])
    control = representative("control", control_majority)
    mutant = representative("mutant", mutant_majority)
    dead = [name for name, rep in (("control", control), ("mutant", mutant))
            if rep["doc"] is None]
    if dead:
        # One dead arm used to leave the pair "usable": a dead mutant arm
        # scored as a miss and a dead control arm as a clean clearance —
        # answers the subject never gave. A pair is a measurement only when
        # both arms answered; the discard keeps every scrap of telemetry
        # that says which arm died and how.
        which = "either arm" if len(dead) == 2 else f"{dead[0]} arm"
        return {**row, "usable": False,
                "error": f"no parseable review on {which}",
                "control_head": control["raw_head"],
                "mutant_head": mutant["raw_head"],
                "control_verdicts": replicate_verdicts["control"],
                "mutant_verdicts": replicate_verdicts["mutant"],
                "control_exit_code": control.get("exit_code"),
                "mutant_exit_code": mutant.get("exit_code"),
                "control_timed_out": control.get("timed_out", False),
                "mutant_timed_out": mutant.get("timed_out", False),
                "control_transport": control.get("transport"),
                "mutant_transport": mutant.get("transport"),
                "control_seconds": control.get("seconds"),
                "mutant_seconds": mutant.get("seconds"),
                "control_error": control.get("error"),
                "mutant_error": mutant.get("error")}

    control_verdict, control_refusing, control_n = _majority(
        replicate_verdicts["control"])
    mutant_verdict, mutant_refusing, mutant_n = _majority(
        replicate_verdicts["mutant"])
    emitted = anchors_of((mutant["doc"] or {}).get("findings") or [])
    # Why a control was refused is the evidence that decides whether the
    # refusal was an error or a latent defect in a substrate assumed sound.
    # Storing only the boolean cost two rounds of paid calls on 2026-08-16.
    from .calibrate import _summarize_findings
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
        "control_findings_detail": _summarize_findings(control["doc"]),
        "mutant_findings_detail": _summarize_findings(mutant["doc"]),
        "replicates": per_arm["control"],
        "mutant_replicates": per_arm["mutant"],
        "control_verdicts": replicate_verdicts["control"],
        "mutant_verdicts": replicate_verdicts["mutant"],
        "control_refusing_share": (control_refusing / control_n) if control_n else None,
        "mutant_refusing_share": (mutant_refusing / mutant_n) if mutant_n else None,
        "control_unanimous": control_n > 0 and control_refusing in (0, control_n),
        "mutant_unanimous": mutant_n > 0 and mutant_refusing in (0, mutant_n),
        "control_json_valid": control["doc"] is not None,
        "mutant_json_valid": mutant["doc"] is not None,
        "control_seconds": control["seconds"], "mutant_seconds": mutant["seconds"],
        "control_transport": control["transport"], "mutant_transport": mutant["transport"],
        "sandbox": control.get("sandbox"),
        "review_preamble": REVIEW_PREAMBLE_VERSION,
        "workspace_isolation": 1,
        "estimated_input_tokens": int(mutant["prompt_bytes"] / 3.04),
        "error": None,
    }


def select_cases(substrates: list[dict], *, sweep_seed: int,
                 per_operator: int, partition: str, max_cases: int,
                 withheld: set[str], cases_doc: dict | None) -> tuple:
    """(cases, selection label): the seeded draw, or an explicit cell list.

    A targeted-cell document exists for the promotion gate — re-measuring
    exactly the cells that separated a pair, under a fresh sweep seed. Its
    cases are in the sample *because of what they previously scored*, so the
    label is stamped on the summary where claim-grade scoring can refuse the
    run; the honest use of a targeted run is the discrimination corpus only.
    """
    if cases_doc is None:
        breadth_pool = [s for s in substrates
                        if s["substrate_id"] not in withheld]
        cases = sample_cases(breadth_pool, sweep_seed=sweep_seed,
                             per_operator=per_operator, partition=partition)
        return cases[:max_cases], "seeded-draw"
    cells = cases_doc.get("cells") or []
    if not cells:
        raise ValueError("targeted case document names no cells")
    selection = cases_doc.get("selection", "targeted-reproduction")
    if selection not in ("targeted-reproduction", "profile-remeasurement"):
        # profile-remeasurement selects cells by an exogenous property fixed
        # before any result existed (their contract version), so it stays
        # claim-eligible; targeted-reproduction selects on outcome and is
        # not. Anything else is a mistake, not a mode.
        raise ValueError(f"unknown cell selection {selection!r}")
    overlap = {c["substrate_id"] for c in cells} & withheld
    if overlap:
        # An anchor substrate is replayed every sweep as an instrument
        # control; a targeted cell on it would run one constant subset as
        # two populations at once.
        raise ValueError(f"targeted cells overlap the anchor set: "
                         f"{sorted(overlap)}")
    cases = targeted_cases(substrates, cells, sweep_seed)
    if len(cases) > max_cases:
        raise ValueError(f"{len(cases)} targeted cells exceed max_cases="
                         f"{max_cases}; a truncated reproduction set would "
                         f"silently drop named cells")
    return cases, selection


def run_pool(*, backend: str, backends_root: str, registry_path: str,
             out_dir: str, sweep_seed: int, per_operator: int,
             partition: str = "open", timeout: int = 1800,
             max_cases: int = 40, abort_after_empty: int = 8,
             replicates: int = 1, mutant_replicates: int | None = None,
             anchor_path: str | None = None, workers: int = 1,
             cases_path: str | None = None) -> dict:
    """Measure one binding over a sampled slice of the pool.

    Two populations run in one sweep and are kept apart:

    - **anchor cases** replay a pinned, invariant set with replication on
      both arms. They measure the instrument, not the corpus, and are
      excluded from the breadth estimand.
    - **breadth cases** are the stratified draw. They carry replication only
      where it is needed: the control arm reproduces at ~53% and the mutant
      arm at ~80-87%, so spending equally on both buys reliability that the
      mutant arm already has, at the cost of distinct planted defects.
    """
    declaration = load_declaration(backends_root, backend)
    adapter = declaration["adapter"]
    from .anchor import anchor_substrate_ids, load as load_anchor

    substrates = SubstrateRegistry(registry_path).read()
    anchor_set = load_anchor(anchor_path) if anchor_path else None
    # A case replayed every sweep must not also count toward a claim's
    # distinct-defect coverage.
    withheld = anchor_substrate_ids(anchor_set)
    cases_doc = None
    if cases_path:
        with open(cases_path, encoding="utf-8") as f:
            cases_doc = json.load(f)
    cases, case_selection = select_cases(
        substrates, sweep_seed=sweep_seed, per_operator=per_operator,
        partition=partition, max_cases=max_cases, withheld=withheld,
        cases_doc=cases_doc)
    anchor_cases = list(anchor_set["cases"]) if anchor_set else []
    plan = [(c, True) for c in anchor_cases] + [(c, False) for c in cases]

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
    lanes = min(max(1, workers), declared_lanes(declaration))
    write_lock = threading.Lock()
    with open(results_path, "a", encoding="utf-8") as out:
        def run_one(indexed):
            index, (case, is_anchor) = indexed
            case_id = f"{case['substrate_id']}:{case['operator']}:{case['seed']}"
            if case_id in done:
                return None
            arm_replicates = (3 if is_anchor else replicates)
            arm_mutant_replicates = (
                3 if is_anchor
                else (replicates if mutant_replicates is None
                      else mutant_replicates))
            body = load_substrate_body(case, exchange, repos)
            if body is None:
                row = {"dispatch_id": case_id, "usable": False,
                       "error": "substrate unreachable",
                       "defect_class": case["operator"]}
            else:
                row = measure_case(case, body, adapter, timeout,
                                   replicates=arm_replicates,
                                   mutant_replicates=arm_mutant_replicates,
                                   workspace=os.path.join(out_dir, "workspace"))
            row["backend_measured"] = backend
            row["anchor"] = is_anchor
            with write_lock:
                out.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                out.flush()
                os.fsync(out.fileno())
                print(f"[{index}/{len(plan)}] {'ANCHOR ' if is_anchor else ''}"
                      f"{case['operator']:28} "
                      f"{'usable' if row.get('usable') else row.get('error','')}"
                      f"{' CAUGHT' if row.get('caught') else ''}"
                      f"{' FALSE-ALARM' if row.get('false_alarm') else ''}",
                      flush=True)
            return row

        # Lanes are bounded by the declaration. Each call is a subprocess to a
        # remote endpoint, so the work is IO-bound and threads carry it.
        empty_streak_state = {"streak": 0, "aborted": None}

        def guarded(indexed):
            if empty_streak_state["aborted"]:
                return None
            row = run_one(indexed)
            if not row:
                return None
            with write_lock:
                if (row.get("error") or "").startswith("no parseable review"):
                    empty_streak_state["streak"] += 1
                    if (abort_after_empty
                            and empty_streak_state["streak"] >= abort_after_empty):
                        empty_streak_state["aborted"] = (
                            f"{empty_streak_state['streak']} consecutive empty lanes")
                elif row.get("usable"):
                    empty_streak_state["streak"] = 0
            return row

        if lanes > 1:
            print(f"lanes: {lanes} (declaration permits "
                  f"{declared_lanes(declaration)})", flush=True)
            with ThreadPoolExecutor(max_workers=lanes) as pool:
                list(pool.map(guarded, enumerate(plan, 1)))
        else:
            for indexed in enumerate(plan, 1):
                guarded(indexed)
        aborted = empty_streak_state["aborted"]

    with open(results_path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    usable = [r for r in rows if r.get("usable")]
    summary = {
        "backend": backend,
        "instrument": SYNTHETIC_CONTRACT_INSTRUMENT,
        "calibration_profile": MEASUREMENT_PROFILE,
        "sweep_seed": sweep_seed,
        "partition": partition,
        "case_selection": case_selection,
        "environment": ENVIRONMENT_VERSION,
        "replicates": replicates,
        "control_unanimous_share": (
            sum(1 for r in usable if r.get("control_unanimous")) / len(usable)
            if usable and replicates > 1 else None),
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
    if cases_path:
        summary["cases_path"] = os.path.basename(cases_path)
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    return summary
