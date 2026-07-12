#!/usr/bin/env python3
"""Model-judged screening of claim-to-source entailment for doctrine concepts.

For every ``source_support`` entry in ``doctrine/concepts/*.yaml`` this harness
resolves the cited locator to its chapter section, asks a local
OpenAI-compatible model whether the section supports the entry's claimed
contribution, and appends a provenance-carrying record to a JSONL results file.

Epistemic framing (see ubiquitous_language.md): each verdict is an
**observation** of model output that supports an **inference** about
entailment. It is screening evidence only — never verification, never
acceptance — and it must not modify doctrine sources.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import datetime
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
import urllib.error
import urllib.request

import yaml

_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from validate_doctrine import parse_heading_selector, plain_heading  # noqa: E402

SCHEMA_VERSION = "entailment-eval/2"
PROMPT_VERSION = "entailment-prompt/5"
DEFAULT_ENDPOINT = "http://localhost:8081/v1"
MODEL_ALIAS = "qwen3.6-35b-a3b"
SECTION_CHAR_BUDGET = 60000
RAW_CONTENT_BUDGET = 4000
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TIMEOUT_SECONDS = 300.0

MODEL_VERDICTS = ("supported", "partially_supported", "not_supported", "contradicted")
HARNESS_VERDICTS = (
    "insufficient_context",
    "resolution_failed",
    "unparseable",
    "transport_error",
    "quote_not_found",
)
FLAGGED_VERDICTS = (
    "not_supported",
    "contradicted",
    "insufficient_context",
    "unparseable",
    "quote_not_found",
)

RELATIONSHIP_MEANINGS = {
    "direct_support": (
        "the section is cited as directly supporting the claimed contribution"
    ),
    "corroboration": (
        "the section is cited as additional support reinforcing the contribution "
        "without materially changing it; source independence is evaluated separately"
    ),
    "refinement": (
        "the section is cited as adding conditions, scope, or nuance captured "
        "by the contribution"
    ),
    "tension": (
        "the section is cited as pushing against or qualifying the concept; "
        "the contribution describes that disagreement, not endorsement"
    ),
    "terminology_variant": (
        "the section is cited as expressing the contribution's idea under "
        "different vocabulary"
    ),
    "historical_precursor": (
        "the section is cited as an earlier form of the idea the contribution describes"
    ),
}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

DEFAULT_DOCTRINE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPOSITORY = DEFAULT_DOCTRINE_DIR.parent

TRANSPORT_ERRORS = (OSError, ValueError, http.client.HTTPException)


@dataclass
class Resolution:
    """Outcome of resolving one locator against the repository."""

    relative_path: str | None
    heading: str | None
    chapter_sha256: str | None
    section_sha256: str | None
    section_text: str | None
    error: str | None


def extract_section(
    chapter_text: str,
    expected_heading: str,
    section_roles: dict[int, tuple[str, int]] | None = None,
) -> str | None:
    """Return the uniquely selected text under ``expected_heading``.

    The section runs from the line after the matched heading until the next
    heading of the same or a higher level. When ``section_roles`` (a 1-based
    line-number → ``(role, logical depth)`` mapping from the tracked section
    maps) is supplied, headings whose role is ``embedded`` — conversion-
    flattened callouts, captions, and box titles — do not terminate the
    section, and neither does a ``section``-role heading whose logical depth
    is below the cited heading's (a genuine nested subsection flattened to
    its parent's markdown level). Headings absent from the mapping
    conservatively count as boundaries at their markdown level. Heading comparison reuses
    ``validate_doctrine.plain_heading`` so locators resolve exactly as the
    doctrine validator checks them. Returns ``None`` when no heading matches.
    """
    heading, selectors = parse_heading_selector(expected_heading)
    if "invalid" in selectors or set(selectors) - {"level", "occurrence", "sha256"}:
        return None
    normalized = plain_heading(heading)
    lines = chapter_text.splitlines()
    matches: list[tuple[int, int, str, str]] = []
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if not match or plain_heading(match.group(2)) != normalized:
            continue
        level = len(match.group(1))
        cited_entry = section_roles.get(index + 1) if section_roles else None
        cited_depth = cited_entry[1] if cited_entry else level
        body: list[str] = []
        end = len(lines)
        for candidate_index in range(index + 1, len(lines)):
            candidate = HEADING_RE.match(lines[candidate_index])
            if candidate and len(candidate.group(1)) <= level:
                if section_roles is not None:
                    entry = section_roles.get(candidate_index + 1)
                    role = entry[0] if entry else "section"
                    depth = entry[1] if entry else len(candidate.group(1))
                    # Embedded headings never terminate; a nested subsection
                    # (logical depth below the cited heading's) does not
                    # terminate its flattened parent even at an equal
                    # markdown level.
                    if role == "embedded" or depth > cited_depth:
                        body.append(lines[candidate_index])
                        continue
                end = candidate_index
                break
            body.append(lines[candidate_index])
        section_text = "\n".join(body).strip("\n")
        bounded_section = "\n".join(lines[index:end]).rstrip() + "\n"
        matches.append(
            (
                level,
                index + 1,
                hashlib.sha256(bounded_section.encode("utf-8")).hexdigest(),
                section_text,
            )
        )
    if "level" in selectors:
        try:
            selected_level = int(selectors["level"])
        except ValueError:
            return None
        matches = [match for match in matches if match[0] == selected_level]
    if "sha256" in selectors:
        matches = [match for match in matches if match[2] == selectors["sha256"]]
    if "occurrence" in selectors:
        try:
            occurrence = int(selectors["occurrence"])
        except ValueError:
            return None
        if occurrence < 1 or occurrence > len(matches):
            return None
        matches = [matches[occurrence - 1]]
    if len(matches) != 1:
        return None
    return matches[0][3]


_SECTION_MAP_CACHE: dict[Path, dict[str, tuple[str, dict[int, tuple[str, int]]]]] = {}


def load_section_roles(
    repo_root: Path, relative_path: str, chapter_sha256: str
) -> dict[int, tuple[str, int]] | None:
    """Heading roles for one chapter from the tracked section maps.

    Returns a 1-based line-number → ``(role, logical depth)`` mapping (depth
    defaults to the heading's markdown level; a map entry's optional ``depth``
    field overrides it for nested subsections flattened to their parent's
    level), or ``None`` when no map covers the chapter or the map's chapter
    hash is stale (the extractor then falls back to plain level-based
    boundaries; ``build_section_map.py --check`` reports the staleness).
    """
    root = repo_root.resolve()
    maps = _SECTION_MAP_CACHE.get(root)
    if maps is None:
        maps = {}
        map_dir = root / "doctrine" / "section-maps"
        if map_dir.is_dir():
            for map_path in sorted(map_dir.glob("*.yaml")):
                document = yaml.safe_load(map_path.read_text(encoding="utf-8")) or {}
                for chapter in document.get("chapters", []):
                    roles = {
                        int(entry["line"]): (
                            str(entry["role"]),
                            int(entry.get("depth", entry.get("level", 6))),
                        )
                        for entry in chapter.get("headings", [])
                    }
                    maps[str(chapter.get("path"))] = (
                        str(chapter.get("chapter_sha256")),
                        roles,
                    )
        _SECTION_MAP_CACHE[root] = maps
    entry = maps.get(relative_path)
    if entry is None or entry[0] != chapter_sha256:
        return None
    return entry[1]


def resolve_locator(repo_root: Path, locator: str) -> Resolution:
    """Resolve ``relative/path.md :: Exact Heading`` to section text."""
    if " :: " not in locator:
        return Resolution(None, None, None, None, None, "malformed_locator")
    relative_path, heading = locator.split(" :: ", 1)
    path = repo_root / relative_path
    if not path.is_file():
        return Resolution(relative_path, heading, None, None, None, "file_missing")
    data = path.read_bytes()
    chapter_sha256 = hashlib.sha256(data).hexdigest()
    section_roles = load_section_roles(repo_root, relative_path, chapter_sha256)
    section = extract_section(data.decode("utf-8"), heading, section_roles)
    if section is None:
        return Resolution(
            relative_path, heading, chapter_sha256, None, None, "heading_not_found"
        )
    section_sha256 = hashlib.sha256(section.encode("utf-8")).hexdigest()
    return Resolution(
        relative_path, heading, chapter_sha256, section_sha256, section, None
    )


def record_key(
    *,
    concept_id: str,
    locator: str,
    claim: str,
    contribution: str,
    relationship: str,
    chapter_sha256: str | None,
    section_sha256: str | None,
    prompt_version: str,
    model_alias: str,
    served_model_id: str,
    endpoint: str,
    max_tokens: int,
    sampler_overrides: dict[str, object],
) -> str:
    """Content identity for one complete judgment target and judge configuration."""
    target = {
        "chapter_sha256": chapter_sha256,
        "claim": claim,
        "concept_id": concept_id,
        "contribution": contribution,
        "endpoint": endpoint.rstrip("/"),
        "locator": locator,
        "max_tokens": max_tokens,
        "model_alias": model_alias,
        "served_model_id": served_model_id,
        "prompt_version": prompt_version,
        "relationship": relationship,
        "sampler_overrides": sampler_overrides,
        "section_sha256": section_sha256,
    }
    material = json.dumps(target, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def enumerate_pairs(concepts_dir: Path) -> list[dict[str, str]]:
    """All (concept, claim, source_support) pairs in deterministic order."""
    pairs: list[dict[str, str]] = []
    for path in sorted(concepts_dir.glob("*.yaml")):
        with path.open(encoding="utf-8") as stream:
            document = yaml.safe_load(stream) or {}
        for concept in document.get("concepts", []):
            for support in concept.get("source_support", []):
                pairs.append(
                    {
                        "concept_id": concept.get("id", ""),
                        "claim": concept.get("claim", ""),
                        "source_id": support.get("source_id", ""),
                        "locator": support.get("locator", ""),
                        "contribution": support.get("contribution", ""),
                        "relationship": support.get("relationship", ""),
                    }
                )
    return pairs


def build_prompt(
    section_text: str,
    heading: str,
    claim: str,
    contribution: str,
    relationship: str,
) -> tuple[str, bool, int]:
    """Return (prompt, truncated, section_chars_used)."""
    truncated = len(section_text) > SECTION_CHAR_BUDGET
    used = section_text[:SECTION_CHAR_BUDGET]
    relationship_meaning = RELATIONSHIP_MEANINGS.get(
        relationship,
        "an unregistered relationship type; judge whether the section supports the contribution",
    )
    truncation_note = (
        f" (truncated at {SECTION_CHAR_BUDGET} characters)" if truncated else ""
    )
    prompt = f"""You are screening a citation in an engineering-doctrine library. A doctrine concept cites a book section as contributing something specific to its claim. Judge whether the section text actually supports the claimed contribution.

Doctrine concept claim (paraphrased doctrine, not a quote):
{claim}

Claimed contribution of the cited section:
{contribution}

Citation relationship type: {relationship} — {relationship_meaning}.

Cited section heading: {heading}
Cited section text{truncation_note}:
---BEGIN SECTION---
{used}
---END SECTION---

Judge only whether the section text supports the claimed contribution, read in the sense of the relationship type. For a "tension" relationship, "supported" means the section genuinely exhibits the described disagreement.

Respond with exactly one JSON object and nothing else:
{{"verdict": "supported" | "partially_supported" | "not_supported" | "contradicted", "evidence_quote": "<short quote from the section, or empty string>", "rationale": "<1-3 sentences>"}}

Verdict meanings:
- supported: the section clearly supports the contribution as characterized.
- partially_supported: the section supports only part of the contribution, or supports it weakly or indirectly.
- not_supported: the section does not contain support for the contribution.
- contradicted: the section asserts the opposite of the contribution."""
    return prompt, truncated, len(used)


def extract_json_object(content: str) -> dict[str, Any] | None:
    """Extract the first parseable JSON object embedded in ``content``."""
    start: int | None = None
    depth = 0
    in_string = False
    escaped = False
    for index, character in enumerate(content):
        if start is None:
            if character == "{":
                start = index
                depth = 1
                in_string = False
                escaped = False
            continue
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                candidate = content[start : index + 1]
                start = None
                try:
                    value = json.loads(candidate)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    return value
    return None


class OpenAIClient:
    """Minimal stdlib client for an OpenAI-compatible chat endpoint."""

    def __init__(
        self,
        endpoint: str,
        timeout: float,
        max_tokens: int,
        model: str = MODEL_ALIAS,
        api_key: str | None = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.model = model
        self.api_key = api_key

    def _request(
        self, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = self.endpoint + path
        headers: dict[str, str] = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if payload is None:
            request = urllib.request.Request(url, headers=headers)
        else:
            headers["Content-Type"] = "application/json"
            request = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
            )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def model_id(self) -> str | None:
        document = self._request("/models")
        data = document.get("data") or []
        served = [entry.get("id") for entry in data if isinstance(entry, dict)]
        # Multi-model servers (ollama) route by the requested name; record it
        # when served. Single-model servers (llama.cpp) ignore the request
        # model field, so fall back to the one model actually loaded.
        if self.model in served:
            return self.model
        return served[0] if served else None

    def chat(self, prompt: str) -> tuple[str, str | None, float]:
        """Return (content, finish_reason, latency_seconds).

        Reads the final answer from ``message.content`` only; the server's
        ``reasoning_content`` (thinking) is intentionally ignored.
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
        }
        started = time.monotonic()
        document = self._request("/chat/completions", payload)
        latency = time.monotonic() - started
        choices = document.get("choices") or [{}]
        choice = choices[0] if isinstance(choices[0], dict) else {}
        message = choice.get("message") or {}
        content = message.get("content") or ""
        return content, choice.get("finish_reason"), latency


def judge(client: OpenAIClient, prompt: str) -> dict[str, Any]:
    """Ask the model for a verdict; retry once on transport or parse failure."""
    last_content = ""
    last_finish: str | None = None
    last_latency: float | None = None
    for _parse_attempt in range(2):
        content = None
        transport_error: str | None = None
        for _transport_attempt in range(2):
            try:
                content, finish_reason, latency = client.chat(prompt)
                break
            except TRANSPORT_ERRORS as error:
                transport_error = f"{type(error).__name__}: {error}"
        if content is None:
            return {
                "verdict": "transport_error",
                "evidence_quote": "",
                "rationale": "",
                "error": transport_error,
                "finish_reason": None,
                "latency_seconds": None,
            }
        last_content, last_finish, last_latency = content, finish_reason, latency
        parsed = extract_json_object(content)
        if parsed is not None and parsed.get("verdict") in MODEL_VERDICTS:
            return {
                "verdict": parsed["verdict"],
                "evidence_quote": str(parsed.get("evidence_quote", "")),
                "rationale": str(parsed.get("rationale", "")),
                "error": None,
                "finish_reason": finish_reason,
                "latency_seconds": latency,
            }
    return {
        "verdict": "unparseable",
        "evidence_quote": "",
        "rationale": "",
        "error": "no_valid_json_verdict_in_content",
        "raw_content": last_content[:RAW_CONTENT_BUDGET],
        "finish_reason": last_finish,
        "latency_seconds": last_latency,
    }


def normalize_for_quote_match(text: str) -> str:
    """Squash text to a lowercase alphanumeric stream for quote containment.

    Models quote the *rendered* text while sections carry raw conversion
    artifacts — line-break hyphenation, mid-word small-caps markup
    (``A***GGREGATE***``), heading markers, span anchors, escapes, and
    typography variants. Comparing lowercase alphanumeric streams on both
    sides is robust to all of these; link targets and image references are
    dropped first so their URLs cannot create false matches.
    """
    text = re.sub(r"<span[^>]*>|</span>", "", text)
    text = re.sub(r"!\[\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[^a-z0-9]+", "", text.casefold())


def verify_evidence_quote(outcome: dict[str, Any], section_text: str) -> dict[str, Any]:
    """Require a non-empty model quote to be present in the complete section.

    An ellipsis in the quote ("...", "…", "[...]", "[…]") is treated as an
    elision: each fragment must be present independently. Fragments are
    split before squashing (squashing removes the ellipsis characters), and
    fragments shorter than 10 alphanumeric characters are ignored to avoid
    trivial matches; if none remain, the whole squashed quote must match.
    """
    quote = outcome.get("evidence_quote")
    if not isinstance(quote, str) or not quote.strip():
        return outcome
    normalized_section = normalize_for_quote_match(section_text)
    fragments = [
        normalize_for_quote_match(fragment)
        for fragment in re.split(r"\[\.\.\.\]|\[…\]|\.\.\.|…", quote)
    ]
    fragments = [fragment for fragment in fragments if len(fragment) >= 10]
    if not fragments:
        fragments = [normalize_for_quote_match(quote)]
    if fragments[0] and all(
        fragment in normalized_section for fragment in fragments
    ):
        return outcome
    invalid = dict(outcome)
    invalid["model_verdict"] = outcome.get("verdict")
    invalid["verdict"] = "quote_not_found"
    invalid["error"] = "evidence_quote_not_found_in_section"
    return invalid


def existing_keys(results_path: Path) -> set[str]:
    keys: set[str] = set()
    if not results_path.is_file():
        return keys
    for line in results_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and "key" in record:
            keys.add(record["key"])
    return keys


def load_records(results_path: Path) -> tuple[list[dict[str, Any]], int]:
    """Latest record per key (last line wins), plus the raw line count."""
    records: dict[str, dict[str, Any]] = {}
    lines = 0
    if not results_path.is_file():
        return [], 0
    for line in results_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        lines += 1
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and "key" in record:
            records[record["key"]] = record
    ordered = sorted(
        records.values(),
        key=lambda item: (item.get("concept_id", ""), item.get("locator", "")),
    )
    return ordered, lines


def summarize(results_path: Path, summary_path: Path) -> int:
    records, line_count = load_records(results_path)
    verdict_counts = Counter(record.get("verdict", "missing") for record in records)
    source_counts: dict[str, Counter] = {}
    for record in records:
        source_counts.setdefault(record.get("source_id", "unknown"), Counter())[
            record.get("verdict", "missing")
        ] += 1
    latencies = [
        record["latency_seconds"]
        for record in records
        if isinstance(record.get("latency_seconds"), (int, float))
    ]
    flagged = [
        record for record in records if record.get("verdict") in FLAGGED_VERDICTS
    ]
    failures = [
        record for record in records if record.get("verdict") == "resolution_failed"
    ]

    verdict_order = list(MODEL_VERDICTS) + list(HARNESS_VERDICTS)
    lines = [
        "# Claim-to-source entailment screening summary",
        "",
        "Generated deterministically from `results.jsonl` by",
        "`doctrine/tools/entailment_eval.py --summarize`. Do not edit by hand.",
        "",
        "Each verdict is an observation of model output supporting an inference",
        "about entailment. It is screening evidence, not verification and not",
        "acceptance; it does not modify doctrine.",
        "",
        f"Records: {len(records)} unique judgment keys ({line_count} result lines).",
        "",
        "## Verdict counts",
        "",
        "| verdict | count |",
        "|---|---|",
    ]
    for verdict in verdict_order:
        if verdict_counts.get(verdict):
            lines.append(f"| {verdict} | {verdict_counts[verdict]} |")
    for verdict in sorted(set(verdict_counts) - set(verdict_order)):
        lines.append(f"| {verdict} | {verdict_counts[verdict]} |")
    lines += [
        "",
        "## Verdicts by source",
        "",
        "| source | " + " | ".join(verdict_order) + " | total |",
        "|---|" + "---|" * (len(verdict_order) + 1),
    ]
    for source_id in sorted(source_counts):
        counts = source_counts[source_id]
        row = [str(counts.get(verdict, 0)) for verdict in verdict_order]
        lines.append(
            f"| {source_id} | " + " | ".join(row) + f" | {sum(counts.values())} |"
        )
    lines += [
        "",
        "## Flagged entries (negative, incomplete, or invalid screening evidence)",
        "",
    ]
    if flagged:
        for record in flagged:
            lines.append(
                f"- `{record.get('verdict')}` — concept `{record.get('concept_id')}` — "
                f"`{record.get('locator')}`"
            )
    else:
        lines.append("None.")
    lines += ["", "## Locator-resolution failures", ""]
    if failures:
        for record in failures:
            lines.append(
                f"- `{record.get('resolution_error')}` — concept `{record.get('concept_id')}` — "
                f"`{record.get('locator')}`"
            )
    else:
        lines.append("None.")
    lines += ["", "## Latency", ""]
    if latencies:
        lines.append(
            f"Mean latency over {len(latencies)} model-judged records: "
            f"{sum(latencies) / len(latencies):.2f}s."
        )
    else:
        lines.append("No model-judged records with recorded latency.")
    lines.append("")
    text = "\n".join(lines)
    print(text)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(text, encoding="utf-8")
    print(f"wrote {summary_path}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limit", type=int, default=None, help="stop after N new records"
    )
    parser.add_argument(
        "--concept",
        action="append",
        default=None,
        help="filter by concept ID (repeatable)",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=None,
        help="filter by source ID (repeatable)",
    )
    parser.add_argument(
        "--redo", action="store_true", help="re-judge records whose key already exists"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="enumerate, resolve, and build prompts without model calls",
    )
    parser.add_argument("--results", type=Path, default=None, help="results JSONL path")
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="summarize results.jsonl and write summary.md; no judging",
    )
    parser.add_argument(
        "--endpoint", default=DEFAULT_ENDPOINT, help="OpenAI-compatible base URL"
    )
    parser.add_argument(
        "--model",
        default=MODEL_ALIAS,
        help="model name sent in requests (llama.cpp ignores it; ollama routes by it)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="repository root override (mainly for tests)",
    )
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument(
        "--api-key-env",
        default=None,
        help=(
            "name of an environment variable holding a bearer API key for the "
            "endpoint (e.g. OPENROUTER_API_KEY); only the variable NAME is "
            "recorded in provenance, never the key"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="per-request timeout in seconds",
    )
    args = parser.parse_args(argv)

    repo_root = (args.repo_root or DEFAULT_REPOSITORY).resolve()
    results_path = (
        args.results
        or repo_root / "doctrine" / "evaluations" / "entailment" / "results.jsonl"
    )
    if args.summarize:
        return summarize(results_path, results_path.parent / "summary.md")

    pairs = enumerate_pairs(repo_root / "doctrine" / "concepts")
    if args.concept:
        pairs = [pair for pair in pairs if pair["concept_id"] in set(args.concept)]
    if args.source:
        pairs = [pair for pair in pairs if pair["source_id"] in set(args.source)]

    known_keys = existing_keys(results_path)
    api_key = None
    if args.api_key_env:
        api_key = os.environ.get(args.api_key_env)
        if not api_key:
            print(
                f"error: environment variable {args.api_key_env} is not set",
                file=sys.stderr,
            )
            return 2
    client = OpenAIClient(
        args.endpoint,
        args.timeout,
        args.max_tokens,
        model=args.model,
        api_key=api_key,
    )
    model_id: str | None = None
    if not args.dry_run:
        try:
            model_id = client.model_id()
        except TRANSPORT_ERRORS as error:
            print(f"warning: /models unavailable: {error}", file=sys.stderr)
    served_model_id = model_id or client.model
    processed = 0
    skipped = 0
    verdict_counts: Counter = Counter()
    results_handle = None
    try:
        for pair in pairs:
            resolution = resolve_locator(repo_root, pair["locator"])
            sampler_overrides: dict[str, object] = {}
            key = record_key(
                concept_id=pair["concept_id"],
                locator=pair["locator"],
                claim=pair["claim"],
                contribution=pair["contribution"],
                relationship=pair["relationship"],
                chapter_sha256=resolution.chapter_sha256,
                section_sha256=resolution.section_sha256,
                prompt_version=PROMPT_VERSION,
                model_alias=client.model,
                served_model_id=served_model_id,
                endpoint=client.endpoint,
                max_tokens=args.max_tokens,
                sampler_overrides=sampler_overrides,
            )
            if key in known_keys and not args.redo:
                skipped += 1
                continue
            if args.limit is not None and processed >= args.limit:
                break
            processed += 1

            truncated = False
            section_chars = 0
            prompt = None
            if resolution.error is None:
                prompt, truncated, section_chars = build_prompt(
                    resolution.section_text or "",
                    resolution.heading or "",
                    pair["claim"],
                    pair["contribution"],
                    pair["relationship"],
                )
            if args.dry_run:
                status = resolution.error or "resolved"
                print(
                    f"DRY {status} concept={pair['concept_id']} source={pair['source_id']} "
                    f"truncated={truncated} prompt_chars={len(prompt) if prompt else 0} "
                    f"locator={pair['locator']}"
                )
                continue

            record: dict[str, Any] = {
                "schema_version": SCHEMA_VERSION,
                "key": key,
                "concept_id": pair["concept_id"],
                "source_id": pair["source_id"],
                "locator": pair["locator"],
                "relationship": pair["relationship"],
                "contribution": pair["contribution"],
                "claim": pair["claim"],
                "chapter_sha256": resolution.chapter_sha256,
                "section_sha256": resolution.section_sha256,
                "resolution_error": resolution.error,
                "truncated": truncated,
                "section_chars": section_chars,
                "section_char_budget": SECTION_CHAR_BUDGET,
                "endpoint": client.endpoint,
                "prompt_version": PROMPT_VERSION,
                "request_params": {
                    "model_alias": client.model,
                    "api_key_env": args.api_key_env,
                    "served_model_id": served_model_id,
                    "max_tokens": args.max_tokens,
                    "sampler_overrides": sampler_overrides,
                },
                "judged_at": datetime.datetime.now(datetime.timezone.utc).isoformat(
                    timespec="seconds"
                ),
            }
            if resolution.error is not None:
                record.update(
                    {
                        "verdict": "resolution_failed",
                        "evidence_quote": "",
                        "rationale": "",
                        "error": resolution.error,
                        "finish_reason": None,
                        "latency_seconds": None,
                        "model": None,
                    }
                )
            elif truncated:
                record.update(
                    {
                        "verdict": "insufficient_context",
                        "evidence_quote": "",
                        "rationale": (
                            "The complete cited section exceeds the configured "
                            "context budget; no entailment judgment was requested."
                        ),
                        "error": "section_exceeds_context_budget",
                        "finish_reason": None,
                        "latency_seconds": None,
                        "model": None,
                    }
                )
            else:
                outcome = verify_evidence_quote(
                    judge(client, prompt or ""), resolution.section_text or ""
                )
                record["model"] = model_id
                record.update(outcome)
            if results_handle is None:
                results_path.parent.mkdir(parents=True, exist_ok=True)
                results_handle = results_path.open("a", encoding="utf-8")
            results_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            results_handle.flush()
            known_keys.add(key)
            verdict_counts[record["verdict"]] += 1
            latency = record.get("latency_seconds")
            latency_note = (
                f" {latency:.1f}s" if isinstance(latency, (int, float)) else ""
            )
            print(
                f"[{processed}] {record['verdict']}{latency_note} "
                f"concept={pair['concept_id']} source={pair['source_id']}",
                file=sys.stderr,
            )
    finally:
        if results_handle is not None:
            results_handle.close()

    mode = "dry-run" if args.dry_run else "run"
    print(
        f"{mode}: {processed} processed, {skipped} skipped (resume), "
        f"{len(pairs)} candidates; verdicts: {dict(sorted(verdict_counts.items()))}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
