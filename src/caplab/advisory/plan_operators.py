"""Defect operators over work graphs (Arm 2 of the planning constructs).

The artifact is a schema-version-2 work graph as JSON text — the shape
`plan-v2` asks a planner for and `striatum-plan-oracle` scores. Same
contract as the review operators: deterministic given (body, seed), exactly
one defect of a known class at a known packet, and a mechanical checker that
passes on the mutant and fails on the control or the pair is discarded.

Two things are specific to plans and are recorded on every injection:

- **Which oracle verdict, if any, the defect flips.** Three classes are
  visible to the oracle without a tree (`dangling_dependency` fails
  legality, `circular_depends_on` fails the application index,
  `unresolvable_acceptance_check` fails resolvability). The rest are
  oracle-silent by construction — a dropped deliverable or a swapped
  purpose parses, orders and resolves exactly as the control did — and
  that is the point: they are the defects a mechanical gate cannot see and
  a plan reviewer must. `ORACLE_EXPECTATION` says which is which so the
  control audit can demand the flip where one is owed.
- **Whether the operator changes packet count.** `atomicity_split` (+1)
  and `merge_independent_packets` (-1) are the size probes the ranking
  memo asks for: a judge that prefers the larger graph on a split pair and
  the smaller on a merge pair is scoring packet count, not planning.

Defect classes follow the capability card (`planning-constructs-v1.md`,
Arm 2). The card's "overclaimed level" is a prose-plan defect (a claim level
asserted above the evidence); its work-graph analogue here is
`overclaimed_verification`: a packet's purpose asserts full verification
while its acceptance checks are cut to one.
"""

from __future__ import annotations

import copy
import json
import random

from .instrument_defects import MAJOR, MINOR, Injection, NotApplicable

#: The oracle verdict a mutant must flip relative to its control, or None
#: when the defect is oracle-silent and only the checker can see it.
ORACLE_EXPECTATION: dict[str, str | None] = {
    "dangling_dependency": "legality",
    "circular_depends_on": "application_index",
    "unresolvable_acceptance_check": "resolvability",
    "write_scope_outside_tree": None,   # needs -tree; silent in design-only
    "atomicity_split": None,
    "dropped_deliverable": None,
    "purpose_scope_contradiction": None,
    "overclaimed_verification": None,
    "merge_independent_packets": None,
}

#: Packet-count change per class; the size probes are the non-zero ones.
SIZE_DELTA: dict[str, int] = {
    "atomicity_split": +1,
    "merge_independent_packets": -1,
}

_VERIFICATION_OVERCLAIM = (" On completion this packet leaves its whole "
                           "surface fully verified; no further checks are needed.")


# ------------------------------------------------------------------ helpers

def _load(body: str) -> dict:
    try:
        graph = json.loads(body)
    except json.JSONDecodeError as e:
        raise NotApplicable(f"body is not JSON: {e}")
    packets = graph.get("packets") if isinstance(graph, dict) else None
    if not isinstance(packets, list) or not packets:
        raise NotApplicable("no packets")
    if any(not isinstance(p, dict) or "id" not in p for p in packets):
        raise NotApplicable("a packet lacks an id")
    return graph


def _dump(graph: dict) -> str:
    return json.dumps(graph, ensure_ascii=False, indent=1, sort_keys=True)


def _by_id(graph: dict) -> dict[str, dict]:
    return {p["id"]: p for p in graph["packets"]}


def _deps(packet: dict) -> list[str]:
    deps = packet.get("depends_on")
    return list(deps) if isinstance(deps, list) else []


def _descendants(graph: dict, root: str) -> set[str]:
    """Every packet that transitively depends on `root`."""
    children: dict[str, list[str]] = {}
    for p in graph["packets"]:
        for d in _deps(p):
            children.setdefault(d, []).append(p["id"])
    seen, stack = set(), list(children.get(root, []))
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        stack.extend(children.get(pid, []))
    return seen


def _ancestors(graph: dict, pid: str) -> set[str]:
    by = _by_id(graph)
    seen, stack = set(), list(_deps(by[pid]))
    while stack:
        cur = stack.pop()
        if cur in seen or cur not in by:
            continue
        seen.add(cur)
        stack.extend(_deps(by[cur]))
    return seen


def _has_cycle(graph: dict) -> bool:
    by = _by_id(graph)
    state: dict[str, int] = {}

    def visit(pid: str) -> bool:
        if state.get(pid) == 1:
            return True
        if state.get(pid) == 2:
            return False
        state[pid] = 1
        for d in _deps(by.get(pid, {})):
            if d in by and visit(d):
                return True
        state[pid] = 2
        return False

    return any(visit(p["id"]) for p in graph["packets"])


def _topological_index(graph: dict) -> list[str]:
    """A total topological order, ties broken by the authored index."""
    authored = {pid: i for i, pid in enumerate(graph.get("index") or [])}
    by = _by_id(graph)
    order_key = lambda pid: (authored.get(pid, len(authored)), pid)  # noqa: E731
    remaining = set(by)
    placed: list[str] = []
    while remaining:
        ready = sorted((pid for pid in remaining
                        if all(d not in remaining for d in _deps(by[pid]))),
                       key=order_key)
        if not ready:
            raise NotApplicable("dependency cycle; no topological index exists")
        placed.append(ready[0])
        remaining.discard(ready[0])
    return placed


def _all_paths(graph: dict) -> set[str]:
    paths: set[str] = set()
    for p in graph["packets"]:
        for key in ("inputs", "outputs", "write_scope"):
            for v in p.get(key) or []:
                if isinstance(v, str):
                    paths.add(v)
    return paths


def _fresh_id(graph: dict, base: str) -> str:
    ids = {p["id"] for p in graph["packets"]}
    candidate, n = base, 2
    while candidate in ids:
        candidate, n = f"{base}{n}", n + 1
    return candidate


def _choose(rng: random.Random, items: list, what: str):
    if not items:
        raise NotApplicable(f"no {what}")
    return rng.choice(sorted(items, key=str))


# ---------------------------------------------------------------- operators

def dangling_dependency(body: str, rng: random.Random) -> Injection:
    """One packet depends on an id no packet carries. Oracle: legality."""
    graph = _load(body)
    packet = _choose(rng, graph["packets"], "packets")
    missing = _fresh_id(graph, "p-missing")
    mutant = copy.deepcopy(graph)
    _by_id(mutant)[packet["id"]]["depends_on"] = _deps(packet) + [missing]
    return Injection(
        defect_class="dangling_dependency", severity=MAJOR,
        element_anchor=packet["id"],
        description=f"packet {packet['id']} now depends on absent {missing}",
        body=_dump(mutant), checkable=True,
        detail={"packet": packet["id"], "missing": missing})


def circular_depends_on(body: str, rng: random.Random) -> Injection:
    """A packet depends on one of its own descendants. Oracle: index."""
    graph = _load(body)
    if _has_cycle(graph):
        raise NotApplicable("control already carries a cycle")
    candidates = [(p["id"], sorted(_descendants(graph, p["id"])))
                  for p in graph["packets"] if _descendants(graph, p["id"])]
    if not candidates:
        raise NotApplicable("no dependency edge to close into a cycle")
    root, descendants = _choose(rng, candidates, "descendant edges")
    target = _choose(rng, descendants, "descendants")
    mutant = copy.deepcopy(graph)
    packet = _by_id(mutant)[root]
    packet["depends_on"] = _deps(packet) + [target]
    return Injection(
        defect_class="circular_depends_on", severity=MAJOR,
        element_anchor=root,
        description=f"packet {root} now depends on its descendant {target}",
        body=_dump(mutant), checkable=True,
        detail={"packet": root, "target": target})


def unresolvable_acceptance_check(body: str, rng: random.Random) -> Injection:
    """One acceptance check names a set no registry holds. Oracle: resolvability."""
    graph = _load(body)
    candidates = [p for p in graph["packets"]
                  if isinstance(p.get("acceptance_checks"), list)
                  and p["acceptance_checks"]]
    packet = _choose(rng, candidates, "packets with acceptance checks")
    checks = list(packet["acceptance_checks"])
    slot = rng.randrange(len(checks))
    bogus = f"{checks[slot]}-full-suite"
    checks[slot] = bogus
    mutant = copy.deepcopy(graph)
    _by_id(mutant)[packet["id"]]["acceptance_checks"] = checks
    return Injection(
        defect_class="unresolvable_acceptance_check", severity=MAJOR,
        element_anchor=packet["id"],
        description=f"packet {packet['id']} names unregistered check set {bogus}",
        body=_dump(mutant), checkable=True,
        detail={"packet": packet["id"], "bogus": bogus, "was": packet["acceptance_checks"][slot]})


def write_scope_outside_tree(body: str, rng: random.Random) -> Injection:
    """A packet writes under a prefix nothing in the plan denotes.

    Oracle-silent without `-tree`; the checker asserts the prefix is
    disjoint from every path the control names."""
    graph = _load(body)
    candidates = [p for p in graph["packets"]
                  if isinstance(p.get("write_scope"), list) and p["write_scope"]]
    packet = _choose(rng, candidates, "packets with a write scope")
    known = _all_paths(graph)
    outside = "third_party/vendored-tools/"
    n = 2
    while any(k.startswith(outside) or outside.startswith(k) for k in known):
        outside, n = f"third_party/vendored-tools-{n}/", n + 1
    mutant = copy.deepcopy(graph)
    _by_id(mutant)[packet["id"]]["write_scope"] = [outside]
    return Injection(
        defect_class="write_scope_outside_tree", severity=MAJOR,
        element_anchor=packet["id"],
        description=f"packet {packet['id']} write scope moved to {outside}",
        body=_dump(mutant), checkable=True,
        detail={"packet": packet["id"], "outside": outside,
                "was": list(packet["write_scope"])})


def atomicity_split(body: str, rng: random.Random) -> Injection:
    """One packet's outputs split across two dependent packets sharing a scope.

    The second packet depends on the first and writes into the same scope,
    so the oracle sees no overlap — but the check unit that covered the
    original packet now straddles a dependency edge, and the first packet's
    intermediate state is unverifiable on its own. Size probe: +1."""
    graph = _load(body)
    candidates = [p for p in graph["packets"]
                  if isinstance(p.get("outputs"), list) and len(p["outputs"]) >= 2
                  and isinstance(p.get("write_scope"), list) and p["write_scope"]]
    packet = _choose(rng, candidates, "packets with two or more outputs")
    outputs = list(packet["outputs"])
    cut = rng.randrange(1, len(outputs))
    first, second = outputs[:cut], outputs[cut:]
    new_id = _fresh_id(graph, f"{packet['id']}-b")
    mutant = copy.deepcopy(graph)
    original = _by_id(mutant)[packet["id"]]
    original["outputs"] = first
    tail = copy.deepcopy(original)
    inputs = list(original.get("inputs") or [])
    inputs += [o for o in first if o not in inputs]     # the parser rejects repeats
    tail.update({
        "id": new_id,
        "outputs": second,
        "depends_on": [packet["id"]],
        "inputs": inputs,
        "purpose": f"Complete {packet['id']}: " + str(original.get("purpose", "")),
    })
    # Whatever waited on the whole packet now waits on its tail. Without this
    # the tail is parallel to the original's dependents, and a dependent that
    # legally shared the original's scope now overlaps the tail's — the
    # oracle would fail a mutant this class promises to keep legal.
    for p in mutant["packets"]:
        if packet["id"] in _deps(p):
            p["depends_on"] = [new_id if d == packet["id"] else d for d in _deps(p)]
    mutant["packets"].append(tail)
    index = list(mutant.get("index") or [])
    if packet["id"] in index:
        index.insert(index.index(packet["id"]) + 1, new_id)
    else:
        index.append(new_id)
    mutant["index"] = index
    return Injection(
        defect_class="atomicity_split", severity=MINOR,
        element_anchor=packet["id"],
        description=f"packet {packet['id']} split; {new_id} depends on it in the same scope",
        body=_dump(mutant), checkable=True,
        detail={"packet": packet["id"], "tail": new_id, "first": first,
                "second": second, "size_delta": SIZE_DELTA["atomicity_split"]})


def dropped_deliverable(body: str, rng: random.Random) -> Injection:
    """One declared output vanishes, and so does every reference to it.

    Removing the path from downstream inputs too is what makes this a
    planning defect rather than a typo: the graph stays internally
    consistent and only the design's promise goes unmet."""
    graph = _load(body)
    candidates = [p for p in graph["packets"]
                  if isinstance(p.get("outputs"), list) and len(p["outputs"]) >= 2]
    packet = _choose(rng, candidates, "packets with two or more outputs")
    victim = _choose(rng, list(packet["outputs"]), "outputs")
    mutant = copy.deepcopy(graph)
    for p in mutant["packets"]:
        for key in ("outputs", "inputs"):
            if isinstance(p.get(key), list):
                p[key] = [v for v in p[key] if v != victim]
    if any(victim in (p.get("outputs") or []) for p in mutant["packets"]):
        raise NotApplicable("deliverable produced by more than one packet")
    return Injection(
        defect_class="dropped_deliverable", severity=MAJOR,
        element_anchor=packet["id"],
        description=f"deliverable {victim} dropped from packet {packet['id']}",
        body=_dump(mutant), checkable=True,
        detail={"packet": packet["id"], "deliverable": victim})


def purpose_scope_contradiction(body: str, rng: random.Random) -> Injection:
    """Two packets with different write scopes swap purposes.

    Each packet now describes work its scope cannot hold."""
    graph = _load(body)
    packets = [p for p in graph["packets"]
               if isinstance(p.get("purpose"), str) and p["purpose"].strip()
               and isinstance(p.get("write_scope"), list) and p["write_scope"]]
    pairs = [(a["id"], b["id"]) for i, a in enumerate(packets)
             for b in packets[i + 1:]
             if set(a["write_scope"]).isdisjoint(b["write_scope"])
             and a["purpose"] != b["purpose"]]
    a_id, b_id = _choose(rng, pairs, "packet pairs with distinct scopes and purposes")
    mutant = copy.deepcopy(graph)
    by = _by_id(mutant)
    by[a_id]["purpose"], by[b_id]["purpose"] = by[b_id]["purpose"], by[a_id]["purpose"]
    return Injection(
        defect_class="purpose_scope_contradiction", severity=MAJOR,
        element_anchor=a_id,
        description=f"purposes of {a_id} and {b_id} swapped",
        body=_dump(mutant), checkable=True,
        detail={"packet": a_id, "other": b_id,
                "a_purpose_now": by[a_id]["purpose"]})


def overclaimed_verification(body: str, rng: random.Random) -> Injection:
    """A packet claims full verification while its checks are cut to one.

    Work-graph analogue of the card's overclaimed level."""
    graph = _load(body)
    candidates = [p for p in graph["packets"]
                  if isinstance(p.get("acceptance_checks"), list)
                  and len(p["acceptance_checks"]) >= 2
                  and isinstance(p.get("purpose"), str)]
    packet = _choose(rng, candidates, "packets with two or more acceptance checks")
    mutant = copy.deepcopy(graph)
    target = _by_id(mutant)[packet["id"]]
    target["acceptance_checks"] = [packet["acceptance_checks"][0]]
    target["purpose"] = packet["purpose"].rstrip() + _VERIFICATION_OVERCLAIM
    return Injection(
        defect_class="overclaimed_verification", severity=MAJOR,
        element_anchor=packet["id"],
        description=f"packet {packet['id']} asserts full verification on one check",
        body=_dump(mutant), checkable=True,
        detail={"packet": packet["id"], "marker": _VERIFICATION_OVERCLAIM.strip(),
                "was_checks": list(packet["acceptance_checks"])})


def merge_independent_packets(body: str, rng: random.Random) -> Injection:
    """Two packets with no path between them collapse into one.

    Union of inputs, outputs, scopes and checks; dependents rewired. Still
    legal to the oracle. Size probe: -1."""
    graph = _load(body)
    ids = [p["id"] for p in graph["packets"]]
    if len(ids) < 3:
        raise NotApplicable("fewer than three packets; a merge would leave a near-trivial graph")
    pairs = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if b not in _descendants(graph, a) and a not in _descendants(graph, b):
                pairs.append((a, b))
    a_id, b_id = _choose(rng, pairs, "independent packet pairs")
    mutant = copy.deepcopy(graph)
    by = _by_id(mutant)
    a, b = by[a_id], by[b_id]
    for key in ("inputs", "outputs", "write_scope", "acceptance_checks", "depends_on"):
        merged = list(a.get(key) or [])
        for v in b.get(key) or []:
            if v not in merged and v != a_id:
                merged.append(v)
        a[key] = [v for v in merged if v != b_id]
    a["purpose"] = f"{a.get('purpose', '')} Also: {b.get('purpose', '')}".strip()
    mutant["packets"] = [p for p in mutant["packets"] if p["id"] != b_id]
    for p in mutant["packets"]:
        deps = [a_id if d == b_id else d for d in _deps(p)]
        p["depends_on"] = [d for i, d in enumerate(deps)
                           if d not in deps[:i] and d != p["id"]]
    if _has_cycle(mutant):
        raise NotApplicable("merging would close a cycle")
    # The survivor inherits the absorbed packet's dependencies, which may sit
    # after it in the authored index; re-derive a topological order that
    # keeps the authored order wherever the dependencies allow.
    mutant["index"] = _topological_index(mutant)
    return Injection(
        defect_class="merge_independent_packets", severity=MINOR,
        element_anchor=a_id,
        description=f"packets {a_id} and {b_id} merged into {a_id}",
        body=_dump(mutant), checkable=True,
        detail={"packet": a_id, "absorbed": b_id,
                "size_delta": SIZE_DELTA["merge_independent_packets"]})


PLAN_OPERATORS = [dangling_dependency, circular_depends_on,
                  unresolvable_acceptance_check, write_scope_outside_tree,
                  atomicity_split, dropped_deliverable,
                  purpose_scope_contradiction, overclaimed_verification,
                  merge_independent_packets]
BY_NAME = {op.__name__: op for op in PLAN_OPERATORS}


# ------------------------------------------------------------------ checking

def check_present(injection: Injection, body: str) -> bool | None:
    """Is the injected defect present in `body`? None when undecidable."""
    try:
        graph = _load(body)
    except NotApplicable:
        return None
    by = _by_id(graph)
    d = injection.detail
    cls = injection.defect_class
    packet = by.get(d.get("packet"))
    if cls == "dangling_dependency":
        return packet is not None and d["missing"] in _deps(packet) \
            and d["missing"] not in by
    if cls == "circular_depends_on":
        return packet is not None and d["target"] in _deps(packet) and _has_cycle(graph)
    if cls == "unresolvable_acceptance_check":
        return packet is not None and d["bogus"] in (packet.get("acceptance_checks") or [])
    if cls == "write_scope_outside_tree":
        if packet is None:
            return False
        scope = packet.get("write_scope") or []
        others = _all_paths(graph) - set(scope)
        return d["outside"] in scope and not any(
            k.startswith(d["outside"]) or d["outside"].startswith(k) for k in others)
    if cls == "atomicity_split":
        tail = by.get(d["tail"])
        return (packet is not None and tail is not None
                and d["packet"] in _deps(tail)
                and set(tail.get("write_scope") or []) == set(packet.get("write_scope") or [])
                and list(packet.get("outputs") or []) == d["first"]
                and list(tail.get("outputs") or []) == d["second"])
    if cls == "dropped_deliverable":
        return all(d["deliverable"] not in (p.get(k) or [])
                   for p in graph["packets"] for k in ("outputs", "inputs"))
    if cls == "purpose_scope_contradiction":
        return packet is not None and packet.get("purpose") == d["a_purpose_now"]
    if cls == "overclaimed_verification":
        return (packet is not None and d["marker"] in str(packet.get("purpose", ""))
                and len(packet.get("acceptance_checks") or []) == 1)
    if cls == "merge_independent_packets":
        return d["absorbed"] not in by and packet is not None \
            and d["absorbed"] not in graph.get("index", [])
    return None


def inject(body: str, seed: int, only: list[str] | None = None) -> Injection:
    """Apply one applicable operator, chosen deterministically from the seed."""
    rng = random.Random(seed)
    pool = [BY_NAME[n] for n in only] if only else list(PLAN_OPERATORS)
    rng.shuffle(pool)
    failures = []
    for operator in pool:
        try:
            return operator(body, rng)
        except NotApplicable as e:
            failures.append(f"{operator.__name__}: {e}")
    raise NotApplicable("no operator applied; " + "; ".join(failures))


def oracle_flip(control_verdict: dict, mutant_verdict: dict,
                defect_class: str) -> bool | None:
    """Did the mutant flip the oracle verdict the class owes?

    True/False for the three oracle-visible classes; None for the
    oracle-silent ones, whose control audit is the control's own soundness
    and whose defect presence is `check_present`."""
    field = ORACLE_EXPECTATION.get(defect_class)
    if field is None:
        return None

    def ok(verdict: dict) -> bool:
        section = verdict.get(field) or {}
        if field == "resolvability":
            return section.get("status") == "checked" and not section.get("unresolvable")
        return bool(section.get("ok"))

    return ok(control_verdict) and not ok(mutant_verdict)
