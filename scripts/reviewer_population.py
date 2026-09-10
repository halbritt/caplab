#!/usr/bin/env python3
"""Census pinned mainline changes without reading review outcomes or fix labels."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


LANGUAGES = {
    ".py": "Python", ".go": "Go", ".rs": "Rust", ".js": "JavaScript",
    ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".c": "C", ".h": "C/C++", ".cc": "C++", ".cpp": "C++",
    ".java": "Java", ".rb": "Ruby", ".sh": "Shell", ".sql": "SQL",
}
EXCLUDED_PREFIXES = ("history/", "vendor/", "node_modules/", ".venv/")
POLICY = {
    "ancestry": "first-parent; merge delta against first parent",
    "window": "start inclusive, end exclusive; committer timestamp",
    "languages_by_suffix": LANGUAGES,
    "excluded_prefixes": list(EXCLUDED_PREFIXES),
    "eligibility": "non-root commit changing at least one included code path",
    "selection_inputs": ["source tip", "ancestry", "committer time", "changed paths"],
    "truth_labels": "none; eligibility does not establish correctness or representativeness",
}


def git(repository: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ["git", "--no-pager", "--no-replace-objects", "-c", "core.fsmonitor=false", "-C", str(repository), *arguments],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def timestamp(value: str) -> int:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.microsecond:
        raise ValueError("window requires timezone-aware whole seconds")
    return int(parsed.timestamp())


def validate_sources(sources: list[dict]) -> None:
    if not sources:
        raise ValueError("at least one pinned repository is required")
    names, repositories = set(), set()
    for source in sources:
        if set(source) != {"name", "path", "tip"}:
            raise ValueError("source requires exactly name, path, tip")
        if not isinstance(source["name"], str) or not source["name"]:
            raise ValueError("source name must be nonempty")
        if not isinstance(source["tip"], str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", source["tip"]):
            raise ValueError("source tip must be a full commit object id")
        repository = Path(source["path"])
        if not repository.is_absolute() or not repository.is_dir():
            raise ValueError("source path must be an existing absolute directory")
        if source["name"] in names or repository.resolve() in repositories:
            raise ValueError("duplicate source name or repository")
        names.add(source["name"])
        repositories.add(repository.resolve())
        if git(repository, "rev-parse", "--is-shallow-repository").strip() != b"false":
            raise ValueError("shallow history cannot establish a complete census")
        actual = git(repository, "rev-parse", "--verify", source["tip"] + "^{commit}").decode().strip()
        if actual != source["tip"]:
            raise ValueError("source tip is not an exact commit")


def changed_paths(repository: Path, parent: str, commit: str) -> list[dict]:
    arguments = ("diff", "--no-ext-diff", "--no-textconv", "--no-renames")
    raw = git(repository, *arguments, "--raw", "--no-abbrev", "-z", parent, commit, "--")
    fields = raw.split(b"\0")
    if fields.pop() != b"" or len(fields) % 2:
        raise ValueError("malformed raw diff")
    paths = []
    for header, encoded_path in zip(fields[::2], fields[1::2]):
        old_mode, new_mode, old_blob, new_blob, status = header.decode("ascii").split()
        path = encoded_path.decode("utf-8", errors="surrogateescape")
        language = LANGUAGES.get(PurePosixPath(path).suffix)
        excluded = next((prefix for prefix in EXCLUDED_PREFIXES if path.startswith(prefix)), None)
        paths.append({
            "path": path, "status": status, "before_blob": old_blob, "after_blob": new_blob,
            "before_mode": old_mode.removeprefix(":"), "after_mode": new_mode,
            "language": language, "included_code": language is not None and excluded is None,
            "exclusion": "excluded-prefix:" + excluded if excluded else (None if language else "non-code-suffix"),
        })
    numstat = git(repository, *arguments, "--numstat", "-z", parent, commit, "--")
    sizes = {}
    for row in numstat.split(b"\0")[:-1]:
        added, deleted, encoded_path = row.split(b"\t", 2)
        sizes[encoded_path.decode("utf-8", errors="surrogateescape")] = {
            "added_lines": None if added == b"-" else int(added),
            "deleted_lines": None if deleted == b"-" else int(deleted),
        }
    if set(sizes) != {entry["path"] for entry in paths}:
        raise ValueError("raw diff and numstat paths disagree")
    for entry in paths:
        entry.update(sizes[entry["path"]])
    return paths


def census_source(source: dict, start: int, end: int) -> dict:
    repository = Path(source["path"])
    history = git(repository, "log", "--first-parent", "--format=%H%x00%P%x00%ct", source["tip"], "--")
    rows = []
    for line in history.decode("ascii").splitlines():
        commit, parent_text, committed_at = line.split("\0")
        if not start <= int(committed_at) < end:
            continue
        parents = parent_text.split()
        paths = changed_paths(repository, parents[0], commit) if parents else []
        code_paths = [entry for entry in paths if entry["included_code"]]
        reason = "no-base-parent" if not parents else ("included-code-change" if code_paths else "no-included-code-change")
        rows.append({
            "commit": commit, "parents": parents, "committer_timestamp": int(committed_at),
            "tree": git(repository, "rev-parse", commit + "^{tree}").decode().strip(),
            "eligible": bool(parents and code_paths), "reason": reason,
            "changed_paths": paths, "code_path_count": len(code_paths),
        })
    rows.sort(key=lambda row: (row["committer_timestamp"], row["commit"]))
    counts = Counter(row["reason"] for row in rows)
    languages = Counter(entry["language"] for row in rows for entry in row["changed_paths"] if entry["included_code"])
    return {**source, "mainline_commits_in_window": len(rows),
            "eligible_commits": sum(row["eligible"] for row in rows),
            "dispositions": dict(sorted(counts.items())),
            "changed_code_paths_by_language": dict(sorted(languages.items())), "commits": rows}


def census(sources: list[dict], start: str, end: str) -> dict:
    lower, upper = timestamp(start), timestamp(end)
    if lower >= upper:
        raise ValueError("census window must be nonempty and increasing")
    validate_sources(sources)
    report = {
        "schema": "caplab.reviewer-population-census/v1", "policy": POLICY,
        "window": {"start": start, "end": end},
        "repositories": [census_source(source, lower, upper) for source in sorted(sources, key=lambda source: source["name"])],
        "interpretation": "mainline change metadata; not review incidents, truth labels, evidence admission or a ranking",
    }
    report["content_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = census(json.loads(args.sources.read_text()), args.start, args.end)
    with args.out.open("x", encoding="utf-8") as output:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": str(args.out), "content_sha256": report["content_sha256"],
                      "repositories": [{k: repository[k] for k in ("name", "mainline_commits_in_window", "eligible_commits")}
                                       for repository in report["repositories"]]}))


if __name__ == "__main__":
    main()
