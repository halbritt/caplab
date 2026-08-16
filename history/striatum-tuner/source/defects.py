"""Defect injection for the reviewer-quality eval.

Each operator takes a sound artifact body and returns exactly one defect of a
known class at a known element, plus a label saying what was done and where.
That label is the ground truth the eval rests on, and it is independent of every
reviewer's opinion because we placed it.

Where an operator's defect is decidable by computation, it ships a `check`:
given a body, the checker says whether the defect is present. Those checkers run
on both arms before scoring — mutant must fail, control must pass — so a
mutation that did not actually break anything is discarded rather than counted
as a defect the reviewer missed. See docs/design/REVIEWER_QUALITY_EVAL_2026-08-07.md
sections 5 and 7.

Operators are deterministic given (body, seed): the eval must be replayable.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from dataclasses import dataclass, field

MAJOR, MINOR = "major", "minor"


@dataclass
class Injection:
    """One injected defect: what, where, and how severe it should read."""

    defect_class: str
    severity: str
    element_anchor: str          # the element a correct finding should name
    description: str             # what was done, for the run record
    body: str                    # the mutated artifact
    checkable: bool = False      # a mechanical checker can confirm it
    detail: dict = field(default_factory=dict)


class NotApplicable(Exception):
    """This operator has nothing to bite on in this artifact."""


# ---------------------------------------------------------------- markdown IRs

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*(\{#el:([a-z0-9-]+)\})?\s*$", re.MULTILINE)


def _headings(body: str) -> list[tuple[str, str, str | None]]:
    """(level, text, anchor slug) for every heading."""
    return [(m.group(1), m.group(2), m.group(4)) for m in HEADING.finditer(body)]


def _anchor_for(body: str, heading_text: str) -> str:
    for level, text, slug in _headings(body):
        if text == heading_text:
            return f"#el:{slug}" if slug else text
    return heading_text


def dropped_section(body: str, rng: random.Random) -> Injection:
    """Delete a section the pass contract requires.

    A design without its Consequences section is incomplete for its stage —
    the reviewer's job is to notice the stage contract is unmet.
    """
    required = ("Consequences", "Constrains", "Decision", "Non-goals",
                "Constraints", "Motivation", "Acceptance", "Verification")
    candidates = [(lvl, text, slug) for lvl, text, slug in _headings(body)
                  if any(text.lower().startswith(r.lower()) for r in required)]
    if not candidates:
        raise NotApplicable("no required section present to drop")
    level, text, slug = rng.choice(candidates)

    # Cut from this heading to the next heading of the same or higher level.
    start = body.index(f"{level} {text}")
    rest = body[start + len(level) + 1 + len(text):]
    nxt = re.search(rf"^#{{1,{len(level)}}}\s+", rest, re.MULTILINE)
    end = start + len(level) + 1 + len(text) + (nxt.start() if nxt else len(rest))
    return Injection(
        defect_class="dropped_section",
        severity=MAJOR,
        element_anchor=f"#el:{slug}" if slug else text,
        description=f"deleted the required section {text!r}",
        body=body[:start] + body[end:],
        detail={"section": text},
    )


def contradicted_clause(body: str, rng: random.Random) -> Injection:
    """Add a clause that negates one already stated.

    Decision clauses are the binding semantic state; two of them asserting
    opposite things is incoherence a reviewer must refuse.
    """
    bullets = [m for m in re.finditer(r"^\s*[-*]\s+\*\*(C\d+[^*]*)\*\*:?\s*(.+)$",
                                      body, re.MULTILINE)]
    if not bullets:
        bullets = [m for m in re.finditer(r"^\s*[-*]\s+(.{40,200})$", body, re.MULTILINE)]
    if not bullets:
        raise NotApplicable("no clause bullets to contradict")
    target = rng.choice(bullets)
    original = target.group(0)
    claim = (target.group(2) if target.lastindex and target.lastindex >= 2
             else target.group(1)).strip()
    # Negate by asserting the opposite disposition of the same subject.
    negated = f"{original}\n- **Exception**: the preceding requirement does not apply; " \
              f"the opposite disposition is permitted and no gate enforces it."
    anchor = None
    for m in HEADING.finditer(body[:target.start()]):
        anchor = m.group(4) or m.group(2)
    return Injection(
        defect_class="contradicted_clause",
        severity=MAJOR,
        element_anchor=f"#el:{anchor}" if anchor else "document",
        description="added a clause negating an adjacent binding clause",
        body=body[:target.start()] + negated + body[target.end():],
        detail={"contradicted": claim[:120]},
    )


def dangling_reference(body: str, rng: random.Random) -> Injection:
    """Repoint a cited path at something that does not exist.

    Real instance: backends/kimi-k3 cited eval-runs/probe-k3-* directories that
    were never created. Evidence that cannot be reached is not evidence.
    """
    paths = [m for m in re.finditer(r"`([a-zA-Z0-9_./-]+/[a-zA-Z0-9_./-]+)`", body)]
    if not paths:
        raise NotApplicable("no cited paths to break")
    target = rng.choice(paths)
    original = target.group(1)
    broken = f"docs/evidence/{hashlib.sha256(original.encode()).hexdigest()[:12]}-report.md"
    anchor = None
    for m in HEADING.finditer(body[:target.start()]):
        anchor = m.group(4) or m.group(2)
    return Injection(
        defect_class="dangling_reference",
        severity=MINOR,
        element_anchor=f"#el:{anchor}" if anchor else "document",
        description=f"repointed a cited path to a nonexistent file",
        body=body[:target.start()] + f"`{broken}`" + body[target.end():],
        checkable=True,
        detail={"was": original, "now": broken},
    )


def overclaimed_level(body: str, rng: random.Random) -> Injection:
    """Assert a claim level the artifact's own bindings do not support.

    Claims are computed from evidence, never declared. A body that writes itself
    up to Verified is asserting authority it does not hold.
    """
    spots = [m for m in re.finditer(r"\b(Asserted|Designed)\b", body)]
    if not spots:
        raise NotApplicable("no claim level to overclaim")
    target = rng.choice(spots)
    anchor = None
    for m in HEADING.finditer(body[:target.start()]):
        anchor = m.group(4) or m.group(2)
    return Injection(
        defect_class="overclaimed_level",
        severity=MAJOR,
        element_anchor=f"#el:{anchor}" if anchor else "document",
        description=f"raised a claim from {target.group(1)} to Verified without bindings",
        body=body[:target.start()] + "Verified" + body[target.end():],
        detail={"was": target.group(1)},
    )


def scope_violation(body: str, rng: random.Random) -> Injection:
    """Put a later-stage commitment into an earlier-stage artifact.

    A proposal states the problem; interface definitions and sequencing belong
    to design and planning. The IR ladder is the contract being broken.
    """
    headings = [h for h in _headings(body) if h[0] == "##"]
    if not headings:
        raise NotApplicable("no section to append a commitment to")
    level, text, slug = headings[-1]
    commitment = (
        "\n\n## Interface commitments {#el:interface-commitments}\n\n"
        "The implementation MUST expose `func ReviewGate(ctx context.Context, "
        "candidate ArtifactRef) (Verdict, error)` in `internal/gate/review.go`, "
        "sequenced as: (1) land the interface, (2) migrate callers, (3) delete "
        "the legacy entrypoint in the following release.\n"
    )
    return Injection(
        defect_class="scope_violation",
        severity=MAJOR,
        element_anchor="#el:interface-commitments",
        description="added interface definitions and sequencing to an early-stage IR",
        body=body.rstrip() + commitment,
        detail={"after_section": text},
    )


def refuted_conclusion(body: str, rng: random.Random) -> Injection:
    """State a conclusion the artifact's own text contradicts.

    Real instance: kimi-k3's declaration concluded "the budget is the fix" while
    recording probes that finished naturally with budget to spare.
    """
    headings = [h for h in _headings(body) if h[0] in ("##", "###")]
    if not headings:
        raise NotApplicable("no section to attach a conclusion to")
    level, text, slug = rng.choice(headings)
    marker = f"{level} {text}"
    at = body.index(marker) + len(marker)
    inserted = (
        "\n\nThe measurements above therefore establish the opposite of what they "
        "record: because every probe terminated normally and well inside its "
        "budget, the budget is confirmed as the binding constraint and raising it "
        "is the fix.\n"
    )
    return Injection(
        defect_class="refuted_conclusion",
        severity=MAJOR,
        element_anchor=f"#el:{slug}" if slug else text,
        description="stated a conclusion the surrounding evidence refutes",
        body=body[:at] + inserted + body[at:],
        detail={"section": text},
    )


# ------------------------------------------------------------------ JSON IRs

def _load_json(body: str):
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        raise NotApplicable(f"not a JSON artifact: {e}")


def hollow_delivery(body: str, rng: random.Random) -> Injection:
    """Drop most of a change set's files while its claims stay put.

    This is the hollow-Verified incident: a two-file stub standing in for a
    seventeen-item plan, passing because whole-tree checks pass trivially on
    additive dead code.
    """
    doc = _load_json(body)
    files = doc.get("files")
    if not isinstance(files, dict) or len(files) < 4:
        raise NotApplicable("not a multi-file change set")
    keep = sorted(files)[:1]
    dropped = [k for k in files if k not in keep]
    doc["files"] = {k: files[k] for k in keep}
    return Injection(
        defect_class="hollow_delivery",
        severity=MAJOR,
        element_anchor=dropped[0],
        description=f"dropped {len(dropped)} of {len(files)} delivered files",
        body=json.dumps(doc, indent=2),
        checkable=True,
        detail={"kept": keep, "dropped_count": len(dropped)},
    )


def hash_mismatch(body: str, rng: random.Random) -> Injection:
    """Perturb a declared hash so it no longer equals what it names."""
    doc = _load_json(body)
    hits: list[tuple[dict, str, str]] = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v):
                    hits.append((node, k, v))
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(doc)
    if not hits:
        raise NotApplicable("no sha256 field to perturb")
    node, key, value = rng.choice(hits)
    flipped = ("0" if value[0] != "0" else "1") + value[1:]
    node[key] = flipped
    return Injection(
        defect_class="hash_mismatch",
        severity=MAJOR,
        element_anchor=key,
        description=f"altered the declared {key} so it no longer matches its content",
        body=json.dumps(doc, indent=2),
        checkable=True,
        detail={"field": key, "was": value, "now": flipped},
    )


def decorative_check(body: str, rng: random.Random) -> Injection:
    """Point an acceptance check at a name nothing resolves.

    An unregistered check name is silently never run, so the packet claims a
    gate it does not have — the mechanism behind the hollow-Verified close.
    """
    doc = _load_json(body)
    holders: list[tuple[dict, list]] = []

    def walk(node):
        if isinstance(node, dict):
            checks = node.get("acceptance_checks")
            if isinstance(checks, list) and checks:
                holders.append((node, checks))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(doc)
    if not holders:
        raise NotApplicable("no acceptance_checks to hollow out")
    node, checks = rng.choice(holders)
    was = checks[0]
    node["acceptance_checks"] = ["repository-coherence-full"] + list(checks[1:])
    return Injection(
        defect_class="decorative_check",
        severity=MAJOR,
        element_anchor="acceptance_checks",
        description="replaced an acceptance check with an unregistered name",
        body=json.dumps(doc, indent=2),
        checkable=True,
        detail={"was": was, "now": "repository-coherence-full"},
    )


def base_dropped(body: str, rng: random.Random) -> Injection:
    """Remove the base composition from an anchored change set."""
    doc = _load_json(body)
    if "base" not in doc and "base_composition" not in doc:
        raise NotApplicable("no anchored base to drop")
    key = "base" if "base" in doc else "base_composition"
    was = doc.pop(key)
    return Injection(
        defect_class="base_dropped",
        severity=MAJOR,
        element_anchor=key,
        description=f"removed the anchored {key}, making the delivery a standalone tree",
        body=json.dumps(doc, indent=2),
        checkable=True,
        detail={"removed": key, "was": str(was)[:160]},
    )


# ------------------------------------------------------------------ registry

MARKDOWN_OPERATORS = [
    dropped_section, contradicted_clause, dangling_reference,
    overclaimed_level, scope_violation, refuted_conclusion,
]
JSON_OPERATORS = [hollow_delivery, hash_mismatch, decorative_check, base_dropped]
ALL_OPERATORS = MARKDOWN_OPERATORS + JSON_OPERATORS
BY_NAME = {op.__name__: op for op in ALL_OPERATORS}


def inject(body: str, seed: int, only: list[str] | None = None) -> Injection:
    """Apply one applicable operator, chosen deterministically from the seed."""
    rng = random.Random(seed)
    pool = [BY_NAME[n] for n in only] if only else list(ALL_OPERATORS)
    rng.shuffle(pool)
    failures = []
    for operator in pool:
        try:
            return operator(body, rng)
        except NotApplicable as e:
            failures.append(f"{operator.__name__}: {e}")
    raise NotApplicable("no operator applied; " + "; ".join(failures))


# ------------------------------------------------- mechanical defect checkers

def check_present(injection: Injection, body: str) -> bool | None:
    """Is this defect present in `body`? None when not mechanically decidable.

    Run on both arms before scoring: the mutant must answer True and the control
    False, or the pair is discarded. This is what keeps a no-op mutation from
    being recorded as a defect the reviewer failed to catch.
    """
    cls = injection.defect_class
    if cls == "dangling_reference":
        return injection.detail["now"] in body
    if cls == "hash_mismatch":
        return injection.detail["now"] in body
    if cls == "decorative_check":
        return '"repository-coherence-full"' in body
    if cls == "hollow_delivery":
        try:
            doc = json.loads(body)
        except json.JSONDecodeError:
            return None
        return isinstance(doc.get("files"), dict) and len(doc["files"]) == 1
    if cls == "base_dropped":
        try:
            doc = json.loads(body)
        except json.JSONDecodeError:
            return None
        return "base" not in doc and "base_composition" not in doc
    return None


def anchor_resolves(anchor: str, body: str) -> bool:
    """Does a finding's element_anchor name something that exists?

    Fabrication check, and it needs no ground truth: a reviewer citing an
    element the artifact does not contain has invented it.
    """
    if not anchor:
        return False
    tail = anchor.rsplit("#", 1)[-1]
    if tail.startswith("el:"):
        return f"{{#{tail}}}" in body
    return tail in body or anchor in body
