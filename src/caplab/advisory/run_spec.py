"""Frozen local experiment configuration for advisory pool resumption.

This is reproducibility metadata, not a verified native Binding or one-shot
execution custody. A process lost before it persists a row remains a separate
attempt-recovery concern.
"""
import hashlib
import json
from pathlib import Path

import yaml

RECORD = "caplab-pool-run-spec/1"
FILENAME = "run-spec.json"


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def declaration_digest(declaration: dict) -> str:
    """Preserve YAML types, including the dates used by native declarations."""
    raw = yaml.safe_dump(declaration, sort_keys=True, allow_unicode=True).encode()
    return hashlib.sha256(raw).hexdigest()


def instrument_sources() -> dict[str, str]:
    """Pin the Python source package that generates and measures pool cases."""
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(__file__).parent.glob("*.py"))}


def read(out_dir: str) -> dict:
    document = json.loads(Path(out_dir, FILENAME).read_text(encoding="utf-8"))
    if (not isinstance(document, dict) or document.get("record") != RECORD
            or not isinstance(document.get("spec"), dict)
            or document.get("sha256") != digest(document["spec"])):
        raise ValueError("invalid pool run specification")
    return document


def bind(out_dir: str, spec: dict) -> str:
    """Create a frozen spec or verify it before any new attempt or row write."""
    path = Path(out_dir, FILENAME)
    fingerprint = digest(spec)
    if path.exists():
        document = read(out_dir)
        if document["sha256"] != fingerprint:
            raise ValueError("pool run specification differs; use a new output directory")
        return fingerprint
    if any(Path(out_dir, name).exists() for name in ("results.jsonl", "summary.json")):
        raise ValueError("existing pool evidence has no frozen run specification")
    document = {"record": RECORD, "sha256": fingerprint, "spec": spec}
    # Exclusive creation prevents replacing a spec another invocation sealed.
    with path.open("x", encoding="utf-8") as out:
        json.dump(document, out, indent=2, sort_keys=True, ensure_ascii=False)
        out.write("\n")
        out.flush()
        import os
        os.fsync(out.fileno())
    return fingerprint
