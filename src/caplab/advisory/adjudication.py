"""Control-soundness adjudications.

The matched-pair instrument assumes the control arm is sound, because the
artifact reached `fate == final`. The 2026-08-16 finding showed that
assumption can fail: shipped artifacts carried internal contradictions a
strong reference correctly refused. When a control is genuinely defective
the metric runs backwards — the reviewer that refuses it is detecting and is
charged a false alarm, while the reviewer that clears it is missing a defect
and is scored correct.

An adjudication records what is actually known about one control substrate:

- `sound` — examined, no defect found; a refusal of it is a false alarm.
- `defective` — examined, a defect established; a refusal is a CATCH the
  instrument cannot score, so the pair is excluded from the false-alarm
  measure rather than counted either way.
- `unadjudicated` — not examined. The default. A refusal is *counted* as a
  false alarm, because assuming otherwise would let any subject escape the
  metric by refusing everything — but the count of unaudited refusals is
  reported beside the rate, so no reader mistakes an unexamined number for
  an established one.

A `defective` or `sound` disposition needs one of the two basis kinds
CAPLAB admits as decision-grounding:

- `mechanical-oracle` — a deterministic check anyone can rerun, recorded with
  the check itself. "The README claims the test validates against a schema;
  the test loads no schema file" is not an opinion.
- `human-adjudication` (including the retained `principal-ruling` spelling)
  — a named authority accepted an argument. Required
  whenever the basis is a model's reasoning rather than a reproducible
  check, because judging a shipped artifact is a statement about another
  system's output and CAPLAB does not own it.

A model review on its own is neither. It supplies the argument that makes
one of the two worth obtaining.
"""

from __future__ import annotations

import copy
import json
import os

ADJUDICATION_RECORD = "caplab-control-adjudication/1"
DISPOSITIONS = {"sound", "defective", "unadjudicated"}
BASIS_KINDS = {"mechanical-oracle", "human-adjudication", "principal-ruling"}


def _unique_fields(pairs):
    record = {}
    for key, value in pairs:
        if key in record:
            raise ValueError(f"duplicate adjudication field {key!r}")
        record[key] = value
    return record


def _validate_record(record: dict) -> dict:
    """Own a structurally valid record; this does not authenticate its judgment."""
    if not isinstance(record, dict) or record.get("record") != ADJUDICATION_RECORD:
        raise ValueError("invalid adjudication record tag")
    record = copy.deepcopy(record)
    for field in ("dispatch_id", "as_of", "disposition", "basis_kind"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f"adjudication {field} must be a nonempty string")
    if record["disposition"] not in DISPOSITIONS:
        raise ValueError("unknown adjudication disposition")
    if record["basis_kind"] not in BASIS_KINDS:
        raise ValueError("unknown adjudication basis kind")
    for field in ("basis", "adjudicated_by"):
        if not isinstance(record.get(field), str):
            raise ValueError(f"adjudication {field} must be a string")
        if record["disposition"] != "unadjudicated" and not record[field].strip():
            raise ValueError(f"a sound/defective disposition requires {field}")
    evidence, notes = record.get("evidence"), record.get("notes")
    if not isinstance(evidence, list) or any(not isinstance(e, dict) for e in evidence):
        raise ValueError("adjudication evidence must be a list of objects")
    if not isinstance(notes, list) or any(not isinstance(n, str) for n in notes):
        raise ValueError("adjudication notes must be a list of strings")
    if (record["disposition"] != "unadjudicated"
            and record["basis_kind"] == "mechanical-oracle" and not evidence):
        raise ValueError("a mechanical-oracle basis must record the check that was run")
    try:
        # Check the exact JSON representation, including nested key collisions.
        encoded = json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8")
        json.loads(encoded, object_pairs_hook=_unique_fields)
    except (TypeError, ValueError, RecursionError) as error:
        raise ValueError("adjudication must contain unambiguous finite JSON values") from error
    return record


class Adjudications:
    """Control dispositions, keyed by the dispatch id of the control arm."""

    def __init__(self, records: list[dict] | None = None):
        self._by_dispatch: dict[str, dict] = {}
        for record in records or []:
            owned = _validate_record(record)
            self._by_dispatch[owned["dispatch_id"]] = owned

    @classmethod
    def load(cls, path: str) -> "Adjudications":
        if not path or not os.path.isfile(path):
            return cls([])
        with open(path, encoding="utf-8") as f:
            return cls([json.loads(line, object_pairs_hook=_unique_fields) for line in f if line.strip()])

    def alias(self, recorded_key: str, control_key: str) -> None:
        """Make a record filed under `recorded_key` answer for `control_key`.

        A record already filed under `control_key` is never overwritten: the
        key scoring uses wins, and the alias only fills a gap."""
        record = self._by_dispatch.get(recorded_key)
        if record is not None and control_key not in self._by_dispatch:
            self._by_dispatch[control_key] = record

    def disposition(self, dispatch_id: str) -> str:
        record = self._by_dispatch.get(dispatch_id)
        return record["disposition"] if record else "unadjudicated"

    def is_defective(self, dispatch_id: str) -> bool:
        return self.disposition(dispatch_id) == "defective"

    def __len__(self) -> int:
        return len(self._by_dispatch)


def build_adjudication(*, dispatch_id: str, disposition: str, basis: str,
                       adjudicated_by: str, as_of: str,
                       basis_kind: str = "human-adjudication",
                       evidence: list[dict] | None = None,
                       notes: list[str] | None = None) -> dict:
    return _validate_record({
        "record": ADJUDICATION_RECORD,
        "dispatch_id": dispatch_id,
        "disposition": disposition,
        "basis": basis,
        "basis_kind": basis_kind,
        "adjudicated_by": adjudicated_by,
        "as_of": as_of,
        "evidence": [] if evidence is None else evidence,
        "notes": [] if notes is None else notes,
    })


def append(path: str, records: list[dict]) -> dict:
    records = [_validate_record(record) for record in records]
    existing = {r["dispatch_id"] for r in Adjudications.load(path)._by_dispatch.values()}
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    added = skipped = 0
    with open(path, "a", encoding="utf-8") as f:
        for record in records:
            if record["dispatch_id"] in existing:
                skipped += 1
                continue
            f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            existing.add(record["dispatch_id"])
            added += 1
        f.flush()
        os.fsync(f.fileno())
    return {"added": added, "skipped_existing": skipped}
