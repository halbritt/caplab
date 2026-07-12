#!/usr/bin/env python3
"""Build tracked per-book section maps for converted chapter headings.

The corpus conversion flattened many books' heading hierarchies: callout
boxes (WARNING/TIP/NOTE), example and figure captions, definition-list items,
and subsection children became sibling ATX headings. Section extraction that
stops at the next same-or-higher-level heading therefore truncates cited
sections. Each map under ``doctrine/section-maps/`` classifies every heading
in every chapter of one book as a genuine ``section`` boundary or ``embedded``
content, with recorded provenance.

Epistemic framing (see ubiquitous_language.md): entries with
``classified_by: rule:<name>`` are observations of deterministic pattern
matches; ``classified_by: model`` entries are model classifications --
screening evidence subject to the release-gate oracle, not verification;
``classified_by: human`` entries are authoritative and are preserved verbatim
by ``--write``.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import re
import sys
import tempfile
import time
from typing import Any, Callable

import yaml

_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from entailment_eval import (  # noqa: E402
    HEADING_RE,
    TRANSPORT_ERRORS,
    OpenAIClient,
    enumerate_pairs,
    extract_json_object,
)
from validate_doctrine import parse_heading_selector, plain_heading  # noqa: E402

SCHEMA_VERSION = "section-map/1"
DEFAULT_ENDPOINT = "http://localhost:8081/v1"
MODEL_ALIAS = "qwen3.6-35b-a3b"
# Reasoning model: it emits thinking before content, so the completion budget
# must be generous or the JSON answer never arrives (finish_reason: length).
DEFAULT_MAX_TOKENS = 16384
DEFAULT_TIMEOUT_SECONDS = 600.0

NUMBERED_BOOK_THRESHOLD = 50
CONTEXT_LINES = 2
CONTEXT_LINE_BUDGET = 160
UNPARSEABLE_NOTE = "unparseable-default-section"
ROLE_VALUES = ("section", "embedded")
CLASSIFIED_BY_RE = re.compile(r"^(rule:[a-z0-9-]+|model|human)$")

CALLOUT_RE = re.compile(
    r"^(WARNING|TIP|NOTE|CAUTION|IMPORTANT|SIDEBAR|KEY POINT|CHECKLIST|CC2E\.COM)\b",
    re.IGNORECASE,
)
CAPTION_RE = re.compile(
    r"^(Example|Figure|Table|Listing)\s+\d+[-–.]\d+", re.IGNORECASE
)
NUMBERED_RE = re.compile(r"^\d+\.\d+\s")
PAGE_NUMBER_RE = re.compile(r"\s+\d+[a-z]*$")
TOC_ENUMERATION_RE = re.compile(
    r"^(?:\d+|[IVXLC]+|Part\s+[IVXLC\d]+)\.\s*", re.IGNORECASE
)

DEFAULT_REPOSITORY = Path(__file__).resolve().parents[2]

# Signature: classifier(relative_path, lines, prompt_entries, undecided_lines)
# -> {line: (role, note or None)}. Tests may inject a fake.
Classifier = Callable[
    [str, list[str], list[dict[str, Any]], list[int]],
    dict[int, tuple[str, str | None]],
]


def normalized_heading(text: str) -> str:
    return " ".join(plain_heading(text).split()).casefold()


def book_directories(repo_root: Path) -> list[Path]:
    books_dir = repo_root / "books"
    if not books_dir.is_dir():
        return []
    return sorted(
        path
        for path in books_dir.iterdir()
        if path.is_dir() and (path / "chapters").is_dir()
    )


def chapter_files(book_dir: Path) -> list[Path]:
    return sorted((book_dir / "chapters").glob("*.md"))


def chapter_headings(lines: list[str]) -> list[dict[str, Any]]:
    """Every ATX heading as ``{line, level, text}`` (1-based line numbers)."""
    headings: list[dict[str, Any]] = []
    for index, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if match:
            headings.append(
                {"line": index, "level": len(match.group(1)), "text": match.group(2)}
            )
    return headings


def cited_headings(repo_root: Path) -> dict[str, set[str]]:
    """Normalized cited headings per chapter path from concept locators."""
    cited: dict[str, set[str]] = {}
    for pair in enumerate_pairs(repo_root / "doctrine" / "concepts"):
        locator = pair["locator"]
        if " :: " not in locator:
            continue
        relative_path, expected = locator.split(" :: ", 1)
        heading, _selectors = parse_heading_selector(expected)
        cited.setdefault(relative_path, set()).add(normalized_heading(heading))
    return cited


def is_toc_chapter(path: Path, headings: list[dict[str, Any]]) -> bool:
    if "table-of-contents" in path.name:
        return True
    return any(plain_heading(item["text"]) == "Contents" for item in headings)


def toc_entries(text: str) -> set[str]:
    """Normalized section-name candidates from a converted TOC pipe table.

    Cells may join words of one title with ``<br>`` or stack several entries
    in one cell, and usually carry trailing printed page numbers, so each cell
    yields several candidate readings. The TOC signal only ever promotes a
    heading to ``section``; over-generation cannot demote one.
    """
    entries: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        for cell in stripped.strip("|").split("|"):
            cell = cell.strip()
            if not cell or set(cell) <= set("-: "):
                continue
            candidates = [cell.replace("<br>", " ")]
            candidates.extend(
                segment for segment in cell.split("<br>") if len(segment.strip()) >= 2
            )
            for candidate in candidates:
                candidate = " ".join(candidate.split())
                without_page = PAGE_NUMBER_RE.sub("", candidate)
                for variant in (
                    candidate,
                    without_page,
                    TOC_ENUMERATION_RE.sub("", without_page),
                ):
                    normalized = normalized_heading(variant)
                    if normalized:
                        entries.add(normalized)
    return entries


def rule_classification(
    heading: dict[str, Any],
    is_first: bool,
    chapter_cited: set[str],
    numbered_book: bool,
    dominant_level: int,
    toc: set[str],
) -> tuple[str, str, str | None] | None:
    """Apply the deterministic rule ladder; ``None`` means undecided.

    Rules fire in priority order; ``rule:cited`` is ground truth for the
    ``section`` role and overrides an earlier embedded classification.
    """
    plain = plain_heading(heading["text"])
    normalized = " ".join(plain.split()).casefold()
    decided: tuple[str, str, str | None] | None = None
    if is_first:
        decided = ("section", "rule:chapter-title", None)
    elif CALLOUT_RE.match(plain):
        decided = ("embedded", "rule:callout", None)
    elif CAPTION_RE.match(plain):
        decided = ("embedded", "rule:caption", None)
    elif numbered_book and NUMBERED_RE.match(plain):
        decided = ("section", "rule:numbered-book", None)
    elif numbered_book and heading["level"] == dominant_level:
        decided = ("embedded", "rule:numbered-book", None)
    elif normalized in toc:
        decided = ("section", "rule:toc", None)
    if normalized in chapter_cited:
        if decided is None:
            return ("section", "rule:cited", None)
        role, rule_name, _note = decided
        if role != "section":
            return ("section", "rule:cited", f"overrides {rule_name}")
    return decided


def following_context(lines: list[str], heading_line: int) -> list[str]:
    """First non-empty lines after a heading, stopping at the next heading."""
    context: list[str] = []
    for line in lines[heading_line:]:
        if HEADING_RE.match(line):
            break
        stripped = line.strip()
        if stripped:
            context.append(stripped[:CONTEXT_LINE_BUDGET])
            if len(context) == CONTEXT_LINES:
                break
    return context


def preceding_context(lines: list[str], heading_line: int) -> str | None:
    """Last non-empty non-heading line before a heading, if any."""
    for line in reversed(lines[: heading_line - 1]):
        if HEADING_RE.match(line):
            return None
        stripped = line.strip()
        if stripped:
            return stripped[-CONTEXT_LINE_BUDGET:]
    return None


FIXED_REASONS = {
    "rule:chapter-title": "chapter title",
    "rule:callout": "callout keyword",
    "rule:caption": "caption pattern",
    "rule:numbered-book": "numbered-book rule",
    "rule:toc": "listed in the book's printed table of contents",
    "rule:cited": "cited by doctrine",
    "model": "earlier model classification",
    "human": "human judgment",
}


def build_chapter_prompt(
    relative_path: str,
    lines: list[str],
    prompt_entries: list[dict[str, Any]],
    undecided_lines: list[int],
) -> str:
    listing: list[str] = []
    for entry in prompt_entries:
        label = f"- line {entry['line']} (level {entry['level']}) {entry['text']!r}"
        if entry["role"] is not None:
            reason = FIXED_REASONS.get(entry.get("classified_by", ""), "fixed")
            listing.append(f"{label} -> {entry['role']} [already classified: {reason}]")
            continue
        listing.append(f"{label} -> UNDECIDED")
        before = preceding_context(lines, entry["line"])
        if before is not None:
            listing.append(f"    text just before: {before!r}")
        for context_line in following_context(lines, entry["line"]):
            listing.append(f"    text after: {context_line!r}")
    numbers = ", ".join(str(line) for line in undecided_lines)
    return f"""You are classifying Markdown ATX headings in one chapter of a converted book. The conversion flattened the book's heading hierarchy: callout boxes, captions, definition-list items, and subsection children can appear as sibling headings of genuine sections.

Definitions:
- "section": the heading starts a new logical unit of the chapter that a reader would find in the book's table of contents.
- "embedded": the heading is a callout box, caption, definition-list item, story or sidebar title, or a flattened child inside the preceding section's discussion.

Cues:
- If the text just before an undecided heading ends with a colon, the heading is almost always an item of a flattened list or definition list -> embedded.
- Where sibling headings are already classified as sections because they are listed in the book's printed table of contents, an undecided heading of similar depth that is absent from that table is usually embedded (the printed table can truncate a few titles, so treat this as a strong hint, not proof).
- A heading that names a self-contained topic a reader would look up, followed by its own multi-paragraph discussion, is a section.

Chapter: {relative_path}
Ordered headings (level = number of leading '#'; already-classified headings are fixed context; UNDECIDED headings show the nearest surrounding text):
{chr(10).join(listing)}

Classify every UNDECIDED heading. Respond with exactly one JSON object and nothing else, mapping each undecided heading's line number to its role, for example: {{"16": "embedded", "22": "section"}}. Include every undecided line number: {numbers}."""


def model_classify_chapter(
    client: OpenAIClient,
    relative_path: str,
    lines: list[str],
    prompt_entries: list[dict[str, Any]],
    undecided_lines: list[int],
) -> dict[int, tuple[str, str | None]]:
    """One model request per chapter; unusable answers default to section.

    Defaulting to ``section`` is the safe direction: it can only under-extend
    a section during extraction, never wrongly swallow a sibling section.
    """
    prompt = build_chapter_prompt(relative_path, lines, prompt_entries, undecided_lines)
    parsed: dict[str, Any] | None = None
    for _attempt in range(2):
        try:
            content, _finish_reason, _latency = client.chat(prompt)
        except TRANSPORT_ERRORS:
            continue
        candidate = extract_json_object(content)
        if isinstance(candidate, dict):
            parsed = candidate
            break
    results: dict[int, tuple[str, str | None]] = {}
    for line in undecided_lines:
        value = None if parsed is None else parsed.get(str(line))
        if isinstance(value, str) and value.strip().lower() in ROLE_VALUES:
            results[line] = (value.strip().lower(), None)
        else:
            results[line] = ("section", UNPARSEABLE_NOTE)
    return results


def make_entry(
    heading: dict[str, Any], role: str, classified_by: str, note: str | None = None
) -> dict[str, Any]:
    entry = {
        "line": heading["line"],
        "level": heading["level"],
        "text": heading["text"],
        "role": role,
        "classified_by": classified_by,
    }
    if note:
        entry["note"] = note
    return entry


def preserved_human_entry(
    old_entry: dict[str, Any], heading: dict[str, Any]
) -> dict[str, Any]:
    """Keep a human entry's judgment and extra fields; refresh its position."""
    entry = dict(old_entry)
    entry["line"] = heading["line"]
    entry["level"] = heading["level"]
    entry["text"] = heading["text"]
    return entry


def build_book_map(
    book_dir: Path,
    repo_root: Path,
    cited: dict[str, set[str]],
    existing: dict[str, Any] | None,
    classifier: Classifier | None,
) -> tuple[dict[str, Any], Counter]:
    """Build one book's section-map document.

    Human entries are preserved (never reclassified or dropped). When a
    chapter's bytes are unchanged, existing model entries are reused instead
    of re-asking the model; rule classifications are always recomputed.
    """
    files = chapter_files(book_dir)
    texts = {path: path.read_bytes() for path in files}
    headings_by_file = {
        path: chapter_headings(texts[path].decode("utf-8").splitlines())
        for path in files
    }
    all_headings = [item for path in files for item in headings_by_file[path]]
    numbered_count = sum(
        1 for item in all_headings if NUMBERED_RE.match(plain_heading(item["text"]))
    )
    numbered_book = numbered_count >= NUMBERED_BOOK_THRESHOLD
    dominant_level = (
        Counter(item["level"] for item in all_headings).most_common(1)[0][0]
        if all_headings
        else 0
    )
    toc: set[str] = set()
    for path in files:
        if is_toc_chapter(path, headings_by_file[path]):
            toc |= toc_entries(texts[path].decode("utf-8"))

    existing_chapters: dict[str, dict[str, Any]] = {}
    if existing:
        for record in existing.get("chapters", []):
            if isinstance(record, dict) and isinstance(record.get("path"), str):
                existing_chapters[record["path"]] = record

    stats: Counter = Counter()
    chapters: list[dict[str, Any]] = []
    for path in files:
        relative = path.relative_to(repo_root).as_posix()
        sha = hashlib.sha256(texts[path]).hexdigest()
        lines = texts[path].decode("utf-8").splitlines()
        headings = headings_by_file[path]
        chapter_cited = cited.get(relative, set())
        old = existing_chapters.get(relative)
        sha_current = bool(old) and old.get("chapter_sha256") == sha
        old_by_line: dict[int, dict[str, Any]] = {}
        if old:
            for item in old.get("headings", []):
                if isinstance(item, dict) and isinstance(item.get("line"), int):
                    old_by_line.setdefault(item["line"], item)

        # Human judgments survive a chapter rewrite: carry them to the same
        # heading text (nth occurrence to nth occurrence). Entries whose text
        # vanished are kept verbatim so --check surfaces them to a human.
        carried_humans: dict[int, dict[str, Any]] = {}
        leftover_humans: list[dict[str, Any]] = []
        if old and not sha_current:
            positions: dict[str, list[int]] = {}
            for item in headings:
                positions.setdefault(item["text"], []).append(item["line"])
            used: Counter = Counter()
            for item in old.get("headings", []):
                if not isinstance(item, dict) or item.get("classified_by") != "human":
                    continue
                text = item.get("text")
                available = positions.get(text, [])
                if used[text] < len(available):
                    carried_humans[available[used[text]]] = item
                    used[text] += 1
                else:
                    leftover_humans.append(dict(item))

        entries: list[dict[str, Any] | None] = []
        undecided_lines: list[int] = []
        for position, heading in enumerate(headings):
            line = heading["line"]
            old_entry = old_by_line.get(line) if sha_current else None
            if old_entry and old_entry.get("classified_by") == "human":
                entries.append(preserved_human_entry(old_entry, heading))
                continue
            if line in carried_humans:
                entries.append(preserved_human_entry(carried_humans[line], heading))
                continue
            # A "pin:" note preserves a reviewed override (e.g. a frontier
            # full-chapter reading that corrects a rule) across rewrites, the
            # same way human entries survive; it stays honestly attributed to
            # its non-human classifier.
            if (
                old_entry
                and isinstance(old_entry.get("note"), str)
                and old_entry["note"].startswith("pin:")
                and old_entry.get("role") in ROLE_VALUES
            ):
                entries.append(preserved_human_entry(old_entry, heading))
                continue
            decided = rule_classification(
                heading,
                position == 0,
                chapter_cited,
                numbered_book,
                dominant_level,
                toc,
            )
            if decided is not None:
                role, classified_by, note = decided
                entries.append(make_entry(heading, role, classified_by, note))
                continue
            if (
                old_entry
                and old_entry.get("classified_by") == "model"
                and old_entry.get("text") == heading["text"]
                and old_entry.get("role") in ROLE_VALUES
            ):
                entries.append(
                    make_entry(
                        heading,
                        old_entry["role"],
                        "model",
                        old_entry.get("note"),
                    )
                )
                continue
            entries.append(None)
            undecided_lines.append(line)

        if undecided_lines:
            if classifier is None:
                raise RuntimeError(
                    f"{relative}: {len(undecided_lines)} undecided headings "
                    "but no model classifier is available"
                )
            heading_by_line = {item["line"]: item for item in headings}
            prompt_entries = [
                {
                    "line": item["line"],
                    "level": item["level"],
                    "text": item["text"],
                    "role": entry["role"] if entry is not None else None,
                    "classified_by": (
                        entry["classified_by"] if entry is not None else None
                    ),
                }
                for item, entry in zip(headings, entries)
            ]
            outcomes = classifier(relative, lines, prompt_entries, undecided_lines)
            for index, entry in enumerate(entries):
                if entry is not None:
                    continue
                line = headings[index]["line"]
                role, note = outcomes.get(line, ("section", UNPARSEABLE_NOTE))
                if role not in ROLE_VALUES:
                    role, note = "section", UNPARSEABLE_NOTE
                entries[index] = make_entry(heading_by_line[line], role, "model", note)

        final_entries = [entry for entry in entries if entry is not None]
        final_entries.extend(leftover_humans)
        for entry in final_entries:
            stats[f"role={entry.get('role')}"] += 1
            stats[f"classified_by={entry.get('classified_by')}"] += 1
        stats["headings"] += len(final_entries)
        stats["model_calls"] += 1 if undecided_lines else 0
        stats["model_classified_now"] += len(undecided_lines)
        chapters.append(
            {"path": relative, "chapter_sha256": sha, "headings": final_entries}
        )

    document = {
        "schema_version": SCHEMA_VERSION,
        "book": book_dir.name,
        "chapters": chapters,
    }
    return document, stats


def dump_map(document: dict[str, Any]) -> str:
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=4096)


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.tmp-", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with open(descriptor, "wb", closefd=True) as stream:
            stream.write(data)
            stream.flush()
        temporary.chmod(0o644)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def maps_dir_for(repo_root: Path) -> Path:
    return repo_root / "doctrine" / "section-maps"


def load_existing_map(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else None


def write_maps(
    repo_root: Path,
    books: list[Path],
    cited: dict[str, set[str]],
    classifier: Classifier | None,
) -> tuple[list[str], Counter]:
    maps_dir = maps_dir_for(repo_root)
    changed: list[str] = []
    totals: Counter = Counter()
    for book_dir in books:
        map_path = maps_dir / f"{book_dir.name}.yaml"
        existing = load_existing_map(map_path)
        document, stats = build_book_map(
            book_dir, repo_root, cited, existing, classifier
        )
        totals.update(stats)
        data = dump_map(document).encode("utf-8")
        if not map_path.is_file() or map_path.read_bytes() != data:
            atomic_write(map_path, data)
            changed.append(map_path.name)
    return changed, totals


def check_entry_shape(problems: list[str], label: str, entry: Any) -> bool:
    if not isinstance(entry, dict):
        problems.append(f"{label}: heading entry is not a mapping")
        return False
    valid = True
    if entry.get("role") not in ROLE_VALUES:
        problems.append(f"{label}: invalid role {entry.get('role')!r}")
        valid = False
    classified_by = entry.get("classified_by")
    if not isinstance(classified_by, str) or not CLASSIFIED_BY_RE.match(classified_by):
        problems.append(f"{label}: invalid classified_by {classified_by!r}")
        valid = False
    depth = entry.get("depth")
    if depth is not None and (not isinstance(depth, int) or not 1 <= depth <= 9):
        problems.append(f"{label}: invalid depth {depth!r}")
        valid = False
    return valid


def check_maps(
    repo_root: Path,
    books: list[Path],
    cited: dict[str, set[str]],
    all_books: bool,
) -> tuple[list[str], Counter]:
    maps_dir = maps_dir_for(repo_root)
    problems: list[str] = []
    totals: Counter = Counter()
    if all_books and maps_dir.is_dir():
        known = {book.name for book in books}
        for path in sorted(maps_dir.glob("*.yaml")):
            if path.stem not in known:
                problems.append(
                    f"{path.relative_to(repo_root).as_posix()}: "
                    "no matching book with a chapters/ directory under books/"
                )
    for book_dir in books:
        map_path = maps_dir / f"{book_dir.name}.yaml"
        map_label = map_path.relative_to(repo_root).as_posix()
        document = load_existing_map(map_path)
        if document is None:
            problems.append(f"{book_dir.name}: missing section map {map_label}")
            continue
        if document.get("schema_version") != SCHEMA_VERSION:
            problems.append(
                f"{map_label}: unsupported schema version "
                f"{document.get('schema_version')!r}"
            )
        if document.get("book") != book_dir.name:
            problems.append(
                f"{map_label}: book {document.get('book')!r} != {book_dir.name!r}"
            )
        records: dict[str, dict[str, Any]] = {}
        for record in document.get("chapters", []):
            if not isinstance(record, dict) or not isinstance(record.get("path"), str):
                problems.append(f"{map_label}: malformed chapter record")
                continue
            if record["path"] in records:
                problems.append(f"{map_label}: duplicate chapter {record['path']}")
            records[record["path"]] = record
        disk = {
            path.relative_to(repo_root).as_posix(): path
            for path in chapter_files(book_dir)
        }
        for relative in sorted(set(disk) - set(records)):
            problems.append(f"{map_label}: chapter not covered: {relative}")
        for relative in sorted(set(records) - set(disk)):
            problems.append(f"{map_label}: mapped chapter missing on disk: {relative}")
        for relative in sorted(set(disk) & set(records)):
            record = records[relative]
            data = disk[relative].read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            if record.get("chapter_sha256") != sha:
                problems.append(f"{map_label}: stale chapter_sha256 for {relative}")
            file_headings = [
                (item["line"], item["level"], item["text"])
                for item in chapter_headings(data.decode("utf-8").splitlines())
            ]
            entries = record.get("headings", [])
            map_headings = []
            for entry in entries:
                if not check_entry_shape(problems, f"{map_label}: {relative}", entry):
                    continue
                map_headings.append(
                    (entry.get("line"), entry.get("level"), entry.get("text"))
                )
                totals[f"role={entry['role']}"] += 1
                totals[f"classified_by={entry['classified_by']}"] += 1
                totals["headings"] += 1
            missing = sorted(set(file_headings) - set(map_headings))
            extra = sorted(set(map_headings) - set(file_headings))
            for line, level, text in missing:
                problems.append(
                    f"{map_label}: {relative}: heading not in map: "
                    f"line {line} (level {level}) {text!r}"
                )
            for line, level, text in extra:
                problems.append(
                    f"{map_label}: {relative}: mapped heading not in chapter: "
                    f"line {line} (level {level}) {text!r}"
                )
            for expected in sorted(cited.get(relative, set())):
                matches = [
                    entry
                    for entry in entries
                    if isinstance(entry, dict)
                    and isinstance(entry.get("text"), str)
                    and normalized_heading(entry["text"]) == expected
                ]
                if not matches:
                    problems.append(
                        f"{map_label}: {relative}: cited heading has no map entry: "
                        f"{expected!r}"
                    )
                for entry in matches:
                    if entry.get("role") != "section":
                        problems.append(
                            f"{map_label}: {relative}: cited heading is not a "
                            f"section: line {entry.get('line')} {entry.get('text')!r} "
                            f"(role={entry.get('role')!r}, "
                            f"classified_by={entry.get('classified_by')!r})"
                        )
        totals["chapters"] += len(records)
        totals["books"] += 1
    return problems, totals


def print_stats(repo_root: Path, books: list[Path]) -> None:
    maps_dir = maps_dir_for(repo_root)
    totals: Counter = Counter()
    for book_dir in books:
        document = load_existing_map(maps_dir / f"{book_dir.name}.yaml")
        if document is None:
            print(f"{book_dir.name}: no section map")
            continue
        counts: Counter = Counter()
        headings = 0
        for record in document.get("chapters", []):
            for entry in record.get("headings", []):
                if not isinstance(entry, dict):
                    continue
                headings += 1
                counts[f"role={entry.get('role')}"] += 1
                counts[f"classified_by={entry.get('classified_by')}"] += 1
        totals.update(counts)
        totals["headings"] += headings
        roles = " ".join(
            f"{key.removeprefix('role=')}={counts[key]}"
            for key in sorted(key for key in counts if key.startswith("role="))
        )
        provenance = " ".join(
            f"{key.removeprefix('classified_by=')}={counts[key]}"
            for key in sorted(key for key in counts if key.startswith("classified_by="))
        )
        print(f"{book_dir.name}: headings={headings} | {roles} | {provenance}")
    roles = " ".join(
        f"{key.removeprefix('role=')}={totals[key]}"
        for key in sorted(key for key in totals if key.startswith("role="))
    )
    provenance = " ".join(
        f"{key.removeprefix('classified_by=')}={totals[key]}"
        for key in sorted(key for key in totals if key.startswith("classified_by="))
    )
    print(f"TOTAL: headings={totals['headings']} | {roles} | {provenance}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--write", action="store_true", help="build/update the section maps"
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="fail listing coverage, staleness, and cited-role problems",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="print per-book counts by role and classified_by",
    )
    parser.add_argument("--book", default=None, help="restrict to one book slug")
    parser.add_argument(
        "--endpoint", default=DEFAULT_ENDPOINT, help="OpenAI-compatible base URL"
    )
    parser.add_argument(
        "--model",
        default=MODEL_ALIAS,
        help="model name sent in requests (llama.cpp ignores it)",
    )
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="per-request timeout in seconds",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="repository root override (mainly for tests)",
    )
    args = parser.parse_args(argv)
    if not (args.write or args.check or args.stats):
        parser.error("one of --write, --check, or --stats is required")

    repo_root = (args.repo_root or DEFAULT_REPOSITORY).resolve()
    books = book_directories(repo_root)
    if args.book is not None:
        books = [book for book in books if book.name == args.book]
        if not books:
            print(f"ERROR: unknown book slug: {args.book}", file=sys.stderr)
            return 2
    cited = cited_headings(repo_root)

    exit_code = 0
    if args.write:
        client = OpenAIClient(
            args.endpoint, args.timeout, args.max_tokens, model=args.model
        )

        def classifier(
            relative_path: str,
            lines: list[str],
            prompt_entries: list[dict[str, Any]],
            undecided_lines: list[int],
        ) -> dict[int, tuple[str, str | None]]:
            started = time.monotonic()
            outcomes = model_classify_chapter(
                client, relative_path, lines, prompt_entries, undecided_lines
            )
            elapsed = time.monotonic() - started
            counts = Counter(role for role, _note in outcomes.values())
            defaulted = sum(
                1 for _role, note in outcomes.values() if note == UNPARSEABLE_NOTE
            )
            print(
                f"model {relative_path}: undecided={len(undecided_lines)} -> "
                f"{dict(sorted(counts.items()))} defaulted={defaulted} "
                f"({elapsed:.1f}s)",
                file=sys.stderr,
            )
            return outcomes

        changed, totals = write_maps(repo_root, books, cited, classifier)
        summary = (
            f"{totals['headings']} headings in {len(books)} book(s); "
            f"{totals['model_calls']} model call(s), "
            f"{totals['model_classified_now']} newly model-classified"
        )
        if changed:
            print(f"UPDATED: {', '.join(changed)}; {summary}")
        else:
            print(f"OK: section maps unchanged; {summary}")

    if args.check:
        problems, totals = check_maps(
            repo_root, books, cited, all_books=args.book is None
        )
        if problems:
            for problem in problems:
                print(f"ERROR: {problem}", file=sys.stderr)
            print(f"FAILED: {len(problems)} problem(s)", file=sys.stderr)
            exit_code = 1
        else:
            print(
                f"OK: section maps current: {totals['books']} books, "
                f"{totals['chapters']} chapters, {totals['headings']} headings "
                f"({totals['role=section']} section, "
                f"{totals['role=embedded']} embedded)"
            )

    if args.stats:
        print_stats(repo_root, books)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
