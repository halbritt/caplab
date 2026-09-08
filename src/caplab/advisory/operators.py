"""CAPLAB-authored defect operators (Tier 3 corpus expansion).

Same contract as the vendored instrument operators: deterministic given
(body, seed), exactly one defect of a known class at a known element, and a
mechanical checker that must pass on the mutant and fail on the control or
the pair is discarded. Every operator here starts life `validation: pending`
under the case-admission protocol (docs/product/advisory/
case-pool-governance.md): a case that known-strong reference bindings
systematically miss questions the case, not the binding.
"""

from __future__ import annotations

import json
import random
import re

from . import instrument_defects as _vendored
from .instrument_defects import (ALL_OPERATORS as _VENDORED_OPERATORS,
                                 HEADING, Injection, MAJOR, MINOR,
                                 NotApplicable, _headings,
                                 check_present as _vendored_check_present)


# --------------------------------------------------- gating the ungated five
#
# Five vendored operators assert their defect by construction and ship no
# checker: `dropped_section`, `contradicted_clause`, `scope_violation`,
# `refuted_conclusion`, `overclaimed_level`. A case built on an unchecked
# injection cannot distinguish "the subject missed a defect" from "the
# mutation never made one" — and `overclaimed_level` is exactly the case two
# strong references missed on 2026-08-16.
#
# Each is decidable. These wrappers call the vendored operator unchanged,
# then record what a checker needs and mark the injection checkable. The
# vendored file stays a verbatim copy.

def _wrap_checkable(vendored_op, enrich):
    def operator(body: str, rng: random.Random) -> Injection:
        injection = vendored_op(body, rng)
        enrich(injection, body)
        injection.checkable = True
        return injection

    operator.__name__ = vendored_op.__name__
    operator.__doc__ = (vendored_op.__doc__ or "") + \
        "\n\nMechanically gated by caplab.advisory.operators."
    return operator


def _enrich_dropped_section(injection: Injection, control: str) -> None:
    """The deleted heading line, which the mutant must no longer contain."""
    text = injection.detail["section"]
    for match in HEADING.finditer(control):
        if match.group(2) == text:
            injection.detail["heading_line"] = match.group(0).strip()
            return
    raise NotApplicable("could not locate the deleted heading to gate on")


def _enrich_inserted_marker(key: str):
    """For operators that insert fixed prose: keep the exact inserted slice."""

    def enrich(injection: Injection, control: str) -> None:
        # The inserted text is whatever the mutant has that the control does
        # not, taken from the first divergence forward.
        limit = min(len(control), len(injection.body))
        start = next((i for i in range(limit)
                      if control[i] != injection.body[i]), limit)
        marker = injection.body[start:start + 160]
        if not marker or marker in control:
            raise NotApplicable(f"{key}: no distinguishing inserted text")
        injection.detail["inserted_marker"] = marker

    return enrich


def _enrich_overclaimed_level(injection: Injection, control: str) -> None:
    """Counting the downgraded token distinguishes the arms exactly."""
    was = injection.detail["was"]
    injection.detail["control_count"] = control.count(was)
    injection.detail["mutant_count"] = injection.body.count(was)
    if injection.detail["control_count"] == injection.detail["mutant_count"]:
        raise NotApplicable("overclaim did not change the claim-level count")


_GATED = {
    "dropped_section": _enrich_dropped_section,
    "contradicted_clause": _enrich_inserted_marker("contradicted_clause"),
    "scope_violation": _enrich_inserted_marker("scope_violation"),
    "refuted_conclusion": _enrich_inserted_marker("refuted_conclusion"),
    "overclaimed_level": _enrich_overclaimed_level,
}


def _anchor_before(body: str, position: int) -> str:
    anchor = None
    for m in HEADING.finditer(body[:position]):
        anchor = m.group(4) or m.group(2)
    return f"#el:{anchor}" if anchor else "document"


def broken_internal_crossref(body: str, rng: random.Random) -> Injection:
    """Repoint an internal {#el:...} cross-reference at a slug that exists
    nowhere in the document. A reference that resolves to nothing is the
    in-document form of a dangling citation."""
    slugs = {slug for _, _, slug in _headings(body) if slug}
    mentions = [m for m in re.finditer(r"\{#el:([a-z0-9-]+)\}", body)]
    # Only prose mentions that are NOT the defining heading occurrence.
    heading_spans = [(m.start(), m.end()) for m in HEADING.finditer(body)]

    def in_heading(m):
        return any(s <= m.start() < e for s, e in heading_spans)

    candidates = [m for m in mentions if not in_heading(m) and m.group(1) in slugs]
    if not candidates:
        raise NotApplicable("no resolvable in-prose {#el:} cross-reference")
    target = rng.choice(candidates)
    broken = f"{target.group(1)}-superseded"
    while broken in slugs:
        broken += "-x"
    return Injection(
        defect_class="broken_internal_crossref",
        severity=MINOR,
        element_anchor=_anchor_before(body, target.start()),
        description="repointed an internal cross-reference at a nonexistent element",
        body=body[:target.start()] + "{#el:" + broken + "}" + body[target.end():],
        checkable=True,
        detail={"was": target.group(1), "now": broken},
    )


def requirement_inversion(body: str, rng: random.Random) -> Injection:
    """Invert one binding requirement: 'must not'/'never' becomes 'may'.

    The sentence keeps reading fluently; only its normative force flips, so
    catching it requires reading the constraint, not the grammar."""
    patterns = [
        (re.compile(r"\bmust not\b"), "may"),
        (re.compile(r"\bnever\b"), "may freely"),
        (re.compile(r"\bMUST NOT\b"), "MAY"),
    ]
    hits = [(m, replacement) for pattern, replacement in patterns
            for m in pattern.finditer(body)]
    if not hits:
        raise NotApplicable("no prohibitive requirement to invert")
    target, replacement = hits[rng.randrange(len(hits))]
    marker = body[max(0, target.start() - 40):target.start()] + replacement
    return Injection(
        defect_class="requirement_inversion",
        severity=MAJOR,
        element_anchor=_anchor_before(body, target.start()),
        description=f"inverted a prohibition ({target.group(0)!r} -> {replacement!r})",
        body=body[:target.start()] + replacement + body[target.end():],
        checkable=True,
        detail={"was": target.group(0), "now": replacement,
                "context_marker": marker[-60:]},
    )


def duplicated_section(body: str, rng: random.Random) -> Injection:
    """Append a verbatim duplicate of an existing section at the end.

    Structural incoherence: the same section asserted twice reads as an
    unresolved merge, and a reviewer signing it off did not read the tail."""
    sections = [(lvl, text, slug) for lvl, text, slug in _headings(body)
                if lvl in ("##", "###")]
    if not sections:
        raise NotApplicable("no section to duplicate")
    level, text, slug = rng.choice(sections)
    start = body.index(f"{level} {text}")
    rest = body[start + len(level) + 1 + len(text):]
    nxt = re.search(rf"^#{{1,{len(level)}}}\s+", rest, re.MULTILINE)
    end = start + len(level) + 1 + len(text) + (nxt.start() if nxt else len(rest))
    section = body[start:end].rstrip()
    if len(section) < 80:
        raise NotApplicable("candidate section too small to read as a defect")
    return Injection(
        defect_class="duplicated_section",
        severity=MINOR,
        element_anchor=f"#el:{slug}" if slug else text,
        description=f"appended a verbatim duplicate of section {text!r}",
        body=body.rstrip() + "\n\n" + section + "\n",
        checkable=True,
        detail={"section": text, "duplicate": section},
    )


def truncated_tail(body: str, rng: random.Random) -> Injection:
    """Cut the document mid-sentence inside its final section.

    An artifact that stops mid-thought is incomplete for its stage; the
    reviewer's job is to notice the contract's tail is missing."""
    sections = _headings(body)
    if len(sections) < 3:
        raise NotApplicable("too few sections to truncate meaningfully")
    level, text, slug = sections[-1]
    start = body.index(f"{level} {text}")
    tail = body[start:]
    words = tail.split()
    if len(words) < 30:
        raise NotApplicable("final section too small to truncate mid-sentence")
    cut_at = start + len(" ".join(words[: len(words) // 2]))
    truncated = body[:cut_at].rstrip()
    if truncated.endswith((".", "!", "?", ":", "`")):
        truncated = truncated[:-1]
    dropped_suffix = body[len(truncated):][-120:]
    return Injection(
        defect_class="truncated_tail",
        severity=MAJOR,
        element_anchor=f"#el:{slug}" if slug else text,
        description=f"truncated the document mid-sentence inside {text!r}",
        body=truncated,
        checkable=True,
        detail={"dropped_suffix": dropped_suffix, "final_section": text},
    )


def swapped_section_bodies(body: str, rng: random.Random) -> Injection:
    """Swap the bodies under two same-level headings, keeping the headings.

    Content filed under the wrong contract heading: each half may read fine
    alone, and only checking heading-against-content finds it."""
    headings = [(m.start(), m.group(1), m.group(2), m.group(4))
                for m in HEADING.finditer(body)]
    same_level = [h for h in headings if h[1] == "##"]
    if len(same_level) < 3:
        raise NotApplicable("need at least three ## sections to swap two")
    i = rng.randrange(len(same_level) - 2)
    first, second = same_level[i], same_level[i + 1]
    after_second = (same_level[i + 2][0] if i + 2 < len(same_level) else len(body))

    def split(entry, end):
        start = entry[0]
        header_end = body.index("\n", start) + 1 if "\n" in body[start:end] else end
        return body[start:header_end], body[header_end:end]

    first_head, first_body = split(first, second[0])
    second_head, second_body = split(second, after_second)
    if len(first_body.strip()) < 60 or len(second_body.strip()) < 60:
        raise NotApplicable("section bodies too small to read as misfiled")
    mutated = (body[:first[0]] + first_head + second_body
               + second_head + first_body + body[after_second:])
    # The exact juxtaposition the swap creates: heading immediately followed
    # by the other section's body bytes. Present in the mutant by
    # construction, absent from the control unless the bodies already alias.
    marker = first_head + second_body[:120]
    if marker in body:
        raise NotApplicable("swapped bodies would be indistinguishable here")
    return Injection(
        defect_class="swapped_section_bodies",
        severity=MAJOR,
        element_anchor=f"#el:{first[3]}" if first[3] else first[2],
        description=f"swapped the bodies of sections {first[2]!r} and {second[2]!r}",
        body=mutated,
        checkable=True,
        detail={"first": first[2], "second": second[2], "marker": marker},
    )


# --------------------------------------------------- claim-vs-behavior

def refuted_conclusion(body: str, rng: random.Random) -> Injection:
    """Insert the conclusion after a complete heading, preserving its anchor.

    The historical operator inserts after the heading title, detaching the
    element identifier. Keep it vendored for provenance; prospective calls
    use the exact heading occurrence selected here, including duplicate titles.
    """
    headings = [m for m in HEADING.finditer(body) if m.group(1) in ("##", "###")]
    if not headings:
        raise NotApplicable("no section to attach a conclusion to")
    target = rng.choice(headings)
    inserted = (
        "\n\nThe measurements above therefore establish the opposite of what they "
        "record: because every probe terminated normally and well inside its "
        "budget, the budget is confirmed as the binding constraint and raising it "
        "is the fix.\n")
    text, slug = target.group(2), target.group(4)
    injection = Injection(
        defect_class="refuted_conclusion", severity=MAJOR,
        element_anchor=f"#el:{slug}" if slug else text,
        description="stated a conclusion the surrounding evidence refutes",
        body=body[:target.end()] + inserted + body[target.end():], checkable=True,
        detail={"section": text, "inserted_text": inserted})
    _enrich_inserted_marker("refuted_conclusion")(injection, body)
    return injection

_VERIFICATION_CLAIM = (
    "Validates every emitted record against the shipped JSON Schema "
    "(draft 2020-12) before assertion")

_SCHEMA_EVIDENCE = re.compile(
    r"\.schema\.json|jsonschema|santhosh|xeipuuv|Draft202012|validate_schema",
    re.IGNORECASE)


def unearned_verification_claim(body: str, rng: random.Random) -> Injection:
    """Make documentation assert a verification its named test never performs.

    This is the shape of both defects found in an accepted striatum change
    set on 2026-08-16: a README stating `schema_validation_test.go`
    "Validates JSON outputs against draft 2020-12 schemas" beside a test that
    loads no schema and only round-trips through Marshal/Unmarshal. Whole-tree
    checks pass, because the test compiles and passes — it simply tests
    something else. The claim is the defect.

    Applies to change sets: a documentation file that names a test file which
    is present in the same change set and demonstrably performs no schema
    validation. The injection adds the claim to the doc; the test is left
    untouched, so the artifact now asserts a guarantee its own files refute.
    """
    doc = _vendored._load_json(body)
    files = doc.get("files")
    if not isinstance(files, dict):
        raise NotApplicable("not a change set with files")

    tests = {name: content for name, content in files.items()
             if isinstance(content, str)
             and re.search(r"(_test\.(go|py)|test_[a-z_]+\.py)$", name)
             and not _SCHEMA_EVIDENCE.search(content)}
    if not tests:
        raise NotApplicable("no test file that lacks schema validation")

    docs = [name for name, content in files.items()
            if isinstance(content, str) and name.endswith(".md")]
    if not docs:
        raise NotApplicable("no documentation file to carry the claim")

    test_name = rng.choice(sorted(tests))
    doc_name = rng.choice(sorted(docs))
    leaf = test_name.rsplit("/", 1)[-1]
    claim = f"\n- `{leaf}`: {_VERIFICATION_CLAIM}.\n"
    if claim in files[doc_name]:
        raise NotApplicable("claim already present")
    files[doc_name] = files[doc_name].rstrip() + "\n" + claim

    return Injection(
        defect_class="unearned_verification_claim",
        severity=MAJOR,
        element_anchor=doc_name,
        description=(f"{doc_name} now claims {leaf} validates records against "
                     f"the shipped schema; that test performs no validation"),
        body=json.dumps(doc, indent=2),
        checkable=True,
        detail={"doc": doc_name, "test": test_name, "claim": claim.strip()},
    )


#: Fields no environment makes checkable: a packet's element hash and the
#: work-graph version hash name objects that live in striatum's graph store,
#: which a lane never sees (tree-v1 §2.8).
UNCHECKABLE_HASH_FIELDS = ("packet_element_hash", "work_graph_version_hash",
                           "work_graph_hash")
#: Operators whose planted defect can only be found with the base in hand.
#: A `lost` pair with one of these is unscorable (tree-v1 §2.3 amendment).
BASE_DEPENDENT_OPERATORS = ("base_dropped", "hash_mismatch")


def hash_mismatch_v3_for(base_source: str):
    """hash_mismatch v3: flips a declared hash the tree-v1 environment makes
    checkable for this case, records the flipped field's checkability class.

    - `base`: base hashes (`base.content_hash`, `resulting_base_hash`,
      `observed_product.content_hash`) — checkable against `base/` when a
      whole or partial tree is mounted;
    - `result`: `result_tree_hash` — checkable against the applied result
      when a whole tree is mounted (the partial product tree is not the tree
      the change set was applied to, so the result cannot be re-derived);
    - `in-set`: any other sha256 field the change set declares about content
      it carries.
    Fields in UNCHECKABLE_HASH_FIELDS are never flipped.
    """
    def classify(path_keys: tuple, key: str) -> str | None:
        if key in UNCHECKABLE_HASH_FIELDS:
            return None
        if key == "result_tree_hash":
            return "result" if base_source == "whole-tree" else None
        if any(k in ("base", "base_composition") for k in path_keys) or key == "resulting_base_hash":
            return "base" if base_source in ("whole-tree", "partial-product-tree") else None
        return "in-set"

    def operator(body: str, rng: random.Random) -> Injection:
        from .instrument_defects import MAJOR, _load_json
        doc = _load_json(body)
        hits: list[tuple[dict, str, str, str]] = []

        def walk(node, path_keys=()):
            if isinstance(node, dict):
                for k, v in node.items():
                    if isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v):
                        cls = classify(path_keys, k)
                        if cls is not None:
                            hits.append((node, k, v, cls))
                    elif k != "files":
                        walk(v, path_keys + (k,))
            elif isinstance(node, list):
                for v in node:
                    walk(v, path_keys)

        walk(doc)
        if not hits:
            raise NotApplicable(
                f"no sha256 field checkable under base_source={base_source}")
        node, key, value, cls = rng.choice(sorted(hits, key=lambda h: (h[1], h[2])))
        flipped = ("0" if value[0] != "0" else "1") + value[1:]
        node[key] = flipped
        return Injection(
            defect_class="hash_mismatch",
            severity=MAJOR,
            element_anchor=key,
            description=f"altered the declared {key} ({cls}-checkable) so it no longer matches",
            body=json.dumps(doc, indent=2),
            checkable=True,
            detail={"field": key, "was": value, "now": flipped,
                    "checkability": cls, "operator_version": "v3",
                    "base_source": base_source},
        )

    operator.__name__ = "hash_mismatch"
    operator.__doc__ = hash_mismatch_v3_for.__doc__
    return operator


def operators_for(environment: str, base_source: str | None = None) -> dict:
    """Operator table for an environment: BY_NAME, with hash_mismatch v3
    substituted under tree-v1. Every other operator is unchanged in
    behaviour and carries the environment's operator label on the row."""
    table = dict(BY_NAME)
    if environment == "tree-v1":
        table["hash_mismatch"] = hash_mismatch_v3_for(base_source or "lost")
    return table


#: Standing order 2026-09-07 (instruction-2026-09-07-review-validation-study
#: §0.3): only operators with a natural analog among the 26 audited real
#: defects count toward a qualification claim. The analog for each kept
#: operator is a control the adjudication ledger proved defective:
#:   unearned_verification_claim  qs-40583720 (receipts assert executions that
#:                                never ran), 71ac079a / 1c9196ec ('proves' by
#:                                grepping comments), qs-415d0b93, b9919beb
#:   contradicted_clause          e57c4ab7 (README vs test), 425bccdb,
#:                                qs-5ea16d21 (13 vs 22), a17d0d0b, qs-f3d9c1ad
#:   refuted_conclusion           qs-42ac7af2 (capacity rationale vs its own
#:                                figures), f42f9365, b755eb26, qs-71a0c8dd
#:   decorative_check             qs-415d0b93 (registered argv silently
#:                                substituted), qs-ccfd2a5f, qs-907a07da, 614cac36
#:   broken_internal_crossref     qs-922bffcd (one anchor id for two documents)
#: The remaining operators are a regression sentinel: measured, reported
#: under `sentinel_by_defect_class`, never in catch or false alarm.
QUALIFICATION_OPERATORS = ("unearned_verification_claim", "contradicted_clause",
                           "refuted_conclusion", "decorative_check",
                           "broken_internal_crossref")
SENTINEL_ONLY_OPERATORS = ("base_dropped", "dangling_reference", "dropped_section",
                           "duplicated_section", "hash_mismatch", "hollow_delivery",
                           "overclaimed_level", "requirement_inversion", "scope_violation",
                           "swapped_section_bodies", "truncated_tail")


CAPLAB_OPERATORS = [broken_internal_crossref, requirement_inversion,
                    duplicated_section, truncated_tail, swapped_section_bodies,
                    unearned_verification_claim]

#: Vendored operators, with the previously ungated five now mechanically
#: gated. Order is preserved so sampling is unaffected.
GATED_VENDORED_OPERATORS = [
    refuted_conclusion if op.__name__ == "refuted_conclusion" else
    _wrap_checkable(op, _GATED[op.__name__]) if op.__name__ in _GATED else op
    for op in _VENDORED_OPERATORS
]

ALL_OPERATORS = GATED_VENDORED_OPERATORS + CAPLAB_OPERATORS
BY_NAME = {op.__name__: op for op in ALL_OPERATORS}

PAIR_VALIDATION_VERSION = "paired-presence/1"


def pair_gate_error(injection: Injection, control: str) -> str | None:
    """Require explicit opposing checker results before prospective attempts.

    This establishes the declared mechanical contrast only, not global
    control soundness or the correctness of a reviewer's eventual finding.
    Historical marker checkers remain available for characterization.
    """
    if injection.defect_class == "unearned_verification_claim":
        return ("oracle unverified: absent schema-related words do not prove "
                "absent validation; independent behavioral evidence is required")
    if injection.checkable is not True:
        return "oracle unverified: injection declares no mechanical checker"
    mutant_result = check_present(injection, injection.body)
    control_result = check_present(injection, control)
    if mutant_result is not True:
        return ("injection failed its own check" if mutant_result is False else
                "oracle unverified: mutant presence is unknown")
    if control_result is not False:
        return ("control already carries the defect" if control_result is True else
                "oracle unverified: control absence is unknown")
    return None


def check_present(injection: Injection, body: str) -> bool | None:
    """Historical presence heuristics, insufficient alone for a pair gate.

    Prospective execution uses pair_gate_error, which refuses unsupported
    semantic claims and unknown results instead of inventing ground truth.
    """
    cls = injection.defect_class
    if cls == "broken_internal_crossref":
        return "{#el:" + injection.detail["now"] + "}" in body
    if cls == "requirement_inversion":
        return injection.detail["context_marker"] in body
    if cls == "duplicated_section":
        return body.count(injection.detail["duplicate"]) >= 2
    if cls == "truncated_tail":
        return injection.detail["dropped_suffix"] not in body
    if cls == "swapped_section_bodies":
        return injection.detail["marker"] in body
    if cls == "dropped_section" and "heading_line" in injection.detail:
        return injection.detail["heading_line"] not in body
    if cls in ("contradicted_clause", "scope_violation", "refuted_conclusion") \
            and "inserted_marker" in injection.detail:
        return injection.detail["inserted_marker"] in body
    if cls == "unearned_verification_claim":
        doc = _vendored._load_json(body)
        files = doc.get("files") or {}
        documentation = files.get(injection.detail["doc"], "")
        test = files.get(injection.detail["test"], "")
        # Preserve the historical heuristic. A helper can validate without
        # these words appearing in the test, so pair_gate_error refuses this
        # class until independent behavioral evidence can establish the claim.
        return (injection.detail["claim"] in documentation
                and not _SCHEMA_EVIDENCE.search(test))
    if cls == "overclaimed_level" and "mutant_count" in injection.detail:
        return body.count(injection.detail["was"]) == injection.detail["mutant_count"]
    return _vendored_check_present(injection, body)


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
