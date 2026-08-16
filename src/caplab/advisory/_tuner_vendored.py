"""Scoring helpers vendored from striatum-tuner, post-correction.

Source: ~/git/striatum-tuner at commit 4d2115a (2026-08-09), files eval.py,
bench.py, defects.py. These are the CORRECTED anchor-path functions delivered
by tuner commits bbd70e3 ("Read the anchor a review actually wrote, wherever
it wrote it") and 0334716; the pre-correction reading of anchored detection
as 0.000 for every claude/codex tuple was a parser defect, and any scoring
done here must use these corrected forms. Vendored rather than imported so
CAPLAB's scoring semantics cannot drift when the tuner repo changes.
"""

from __future__ import annotations

import json
import re

VERDICTS = {"accept", "accept_with_findings", "needs_revision", "reject"}
ACCEPTING = {"accept", "accept_with_findings"}
REFUSING = {"needs_revision", "reject"}


def extract_json(content: str):
    """Supervisor-bridge-style extraction: fenced block first, then the first
    parseable JSON value in the text."""
    for m in re.finditer(r"```(?:json)?\s*\n(.*?)```", content, re.DOTALL):
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
    dec = json.JSONDecoder()
    for i, ch in enumerate(content):
        if ch in "{[":
            try:
                doc, _ = dec.raw_decode(content[i:])
                return doc
            except json.JSONDecodeError:
                continue
    return None


ANCHOR_IN_TEXT = re.compile(
    r"(?:\{#(el:[A-Za-z0-9_.\-/:]+)\}"           # {#el:slug}, the emitted form
    r"|element[ _]anchor[:=]\s*([^|\n,;]+)"       # "element anchor: <x>", prose
    r"|(?<![\w#])(#?el:[A-Za-z0-9_.\-/:]+))",     # a bare el:slug mention
    re.IGNORECASE)


def normalize_anchor(anchor: str) -> str:
    """An anchor reduced to the identity two lanes can be compared on."""
    text = anchor.strip().strip("`'\"").strip()
    text = text.removeprefix("{").removesuffix("}")
    text = text.removeprefix("#")
    text = text.removeprefix("el:")
    return text.strip().lower()


def anchors_of(findings: list) -> list[str]:
    """Every element anchor a review names, whatever shape it names it in."""
    found: list[str] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        declared = finding.get("element_anchor")
        if isinstance(declared, str) and declared.strip():
            found.append(declared)
            continue
        for value in finding.values():
            if not isinstance(value, str):
                continue
            for groups in ANCHOR_IN_TEXT.findall(value):
                found.extend(g for g in groups if g and g.strip())
    return found


def anchor_hits(injected: str, emitted: list[str]) -> bool:
    """Whether any emitted anchor names the element the injection broke."""
    target = normalize_anchor(injected)
    if not target:
        return False
    for anchor in emitted:
        candidate = normalize_anchor(anchor)
        if candidate and (candidate in target or target in candidate):
            return True
    return False
