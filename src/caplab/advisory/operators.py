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

import random
import re

from .instrument_defects import (ALL_OPERATORS as _VENDORED_OPERATORS,
                                 HEADING, Injection, MAJOR, MINOR,
                                 NotApplicable, _headings,
                                 check_present as _vendored_check_present)


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


CAPLAB_OPERATORS = [broken_internal_crossref, requirement_inversion,
                    duplicated_section, truncated_tail, swapped_section_bodies]
ALL_OPERATORS = list(_VENDORED_OPERATORS) + CAPLAB_OPERATORS
BY_NAME = {op.__name__: op for op in ALL_OPERATORS}


def check_present(injection: Injection, body: str) -> bool | None:
    """Mechanical presence check covering vendored and CAPLAB classes."""
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
