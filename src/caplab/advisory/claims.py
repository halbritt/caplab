"""Scored advisory claims and their append-only ledger.

A claim states: this subject, under this construct, measured these metric
values, on this evidence, with this custody provenance, as of this time. It
is advisory by construction — no threshold, no qualification status, no
availability, no ranking.

The ledger is a git-tracked JSONL file (`advisory/claims.jsonl`);
deduplication is by content hash, so re-deriving the same claim is an
idempotent no-op and history review is ordinary code review.
"""

from __future__ import annotations

import hashlib
import json
import os

CLAIM_RECORD = "quartermaster-scored-claim/1"
CUSTODY_CLASSES = {"historical-seed", "caplab-advisory"}

REVIEW_DEFECT_DISCRIMINATION = "review.defect_discrimination/1"


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_hash(value) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def build_claim(*, subject_source_id: str, subject_matched: bool,
                construct: str, metrics: dict, custody: str, as_of: str,
                evidence: list[dict], notes: list[str] | None = None) -> dict:
    if custody not in CUSTODY_CLASSES:
        raise ValueError(f"unknown custody class {custody!r}")
    body = {
        "record": CLAIM_RECORD,
        "subject": {"source_id": subject_source_id,
                    "match": "declared-name",
                    "matched_current_declaration": subject_matched},
        "construct": construct,
        "metrics": metrics,
        "custody": custody,
        "as_of": as_of,
        "evidence": evidence,
        "notes": notes or [],
    }
    body["claim_id"] = "qc-" + content_hash(body)[len("sha256:"):][:16]
    return body


class Ledger:
    def __init__(self, path: str):
        self.path = path

    def read(self) -> list[dict]:
        if not os.path.isfile(self.path):
            return []
        with open(self.path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def append(self, claims: list[dict]) -> dict:
        existing = {content_hash({k: v for k, v in c.items() if k != "_content_hash"})
                    for c in self.read()}
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        added = skipped = 0
        with open(self.path, "a", encoding="utf-8") as f:
            for claim in claims:
                digest = content_hash({k: v for k, v in claim.items()
                                       if k != "_content_hash"})
                if digest in existing:
                    skipped += 1
                    continue
                row = dict(claim)
                row["_content_hash"] = digest
                f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                existing.add(digest)
                added += 1
            f.flush()
            os.fsync(f.fileno())
        return {"added": added, "skipped_duplicates": skipped}
