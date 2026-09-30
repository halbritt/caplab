"""Validated contracts for the Cairn retrieval evaluation harness.

`validate_spec` freezes a `caplab-retrieval-spec/1` document into a normalized
dict; `validate_attempt` checks one attempt record against that spec. Both are
pure: no filesystem, network, or clock access. Everything invalid raises
`ContractError` with a stable `code` and a JSON-pointer-like `path`.

Identifiers (experiment, note, query, arm) are slugs: 1-128 characters from
[A-Za-z0-9._-], starting with a letter or digit. `:` is reserved as the
assignment separator, so `assignment_id(arm, query, seed)` is unambiguous.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any

SPEC_SCHEMA = "caplab-retrieval-spec/1"
ATTEMPT_STATUSES = ("ok", "error", "timeout", "interrupted", "not_started")
FAILURE_STATUSES = ("error", "timeout", "interrupted")
ADAPTERS = ("command", "cairn")
ANSWERABLE = "answerable"

_SLUG = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
LIMITS = {
    "corpus": 100_000, "queries": 10_000, "arms": 32, "cutoffs": 16, "max_cutoff": 1_000,
    "seeds": 100, "max_seed": 2**31 - 1, "timeout_seconds": 86_400, "body_bytes": 1 << 20,
    "text_bytes": 64 << 10, "labels": 10_000, "ranked": 10_000, "string_bytes": 4_096,
    "latency_ns": 10**15,
}
_SPEC_KEYS = {"schema_version", "experiment_id", "corpus", "queries", "arms", "cutoffs", "seeds", "timeout_seconds"}
_NOTE_KEYS = {"id", "body", "kind", "shareable", "repo", "supersede_with"}
_QUERY_KEYS = {"id", "text", "relevant_ids", "forbidden_ids", "stratum"}
_ARM_KEYS = {"id", "adapter", "configuration"}
_CONFIG_KEYS = {
    "command": ({"argv"}, {"argv"}),
    "cairn": ({"binary", "checkout"}, {"binary", "checkout", "semantic_worker", "semantic_mode"}),
}
SEMANTIC_MODES = ("off", "on")
_ATTEMPT_KEYS = {"assignment_id", "arm", "query_id", "seed", "status", "ranked_ids", "delivered_ids",
                 "latency_ns", "error", "observation"}


class ContractError(ValueError):
    def __init__(self, code: str, path: str, message: str):
        super().__init__(f"{code} at {path}: {message}")
        self.code, self.path, self.message = code, path, message


def _fail(code, path, message):
    raise ContractError(code, path, message)


def _object(value, path, required, allowed):
    if not isinstance(value, dict):
        _fail("TYPE", path, "must be an object")
    missing = sorted(required - value.keys())
    if missing:
        _fail("MISSING_FIELD", path, "missing " + ", ".join(missing))
    unknown = sorted(value.keys() - allowed)
    if unknown:
        _fail("UNKNOWN_FIELD", path, "unknown " + ", ".join(unknown))
    return value


def _slug(value, path):
    if not isinstance(value, str) or not _SLUG.fullmatch(value):
        _fail("INVALID_ID", path, "must be a 1-128 character slug of [A-Za-z0-9._-] starting alphanumeric")
    return value


def _text(value, path, limit, allow_empty=False):
    if not isinstance(value, str) or (not value and not allow_empty):
        _fail("TYPE", path, "must be a nonempty string" if not allow_empty else "must be a string")
    if len(value.encode("utf-8", "surrogatepass")) > limit:
        _fail("TOO_LARGE", path, f"exceeds {limit} UTF-8 bytes")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        _fail("INVALID_TEXT", path, "contains unpaired surrogates")
    return value


def _integer(value, path, minimum, maximum):
    if type(value) is not int:  # bool and float are rejected
        _fail("TYPE", path, "must be an integer")
    if not minimum <= value <= maximum:
        _fail("OUT_OF_RANGE", path, f"must be between {minimum} and {maximum}")
    return value


def _list(value, path, limit, allow_empty=True):
    if not isinstance(value, list):
        _fail("TYPE", path, "must be an array")
    if not allow_empty and not value:
        _fail("EMPTY", path, "must not be empty")
    if len(value) > limit:
        _fail("TOO_LARGE", path, f"exceeds {limit} items")
    return value


def _unique_ids(values, path, known=None):
    seen = set()
    for i, value in enumerate(values):
        _slug(value, f"{path}/{i}")
        if value in seen:
            _fail("DUPLICATE_ID", f"{path}/{i}", f"duplicate {value!r}")
        if known is not None and value not in known:
            _fail("UNKNOWN_ID", f"{path}/{i}", f"{value!r} is not a corpus note")
        seen.add(value)
    return list(values)


def _finite_json(value, path, depth=0):
    """Reject NaN/Infinity, non-string keys and unbounded nesting in free-form objects."""
    if depth > 32:
        _fail("TOO_DEEP", path, "nesting exceeds 32 levels")
    if isinstance(value, float) and not math.isfinite(value):
        _fail("NOT_FINITE", path, "must be a finite number")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                _fail("TYPE", path, "object keys must be strings")
            _finite_json(item, f"{path}/{key}", depth + 1)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _finite_json(item, f"{path}/{i}", depth + 1)
    elif value is not None and not isinstance(value, (str, int, float, bool)):
        _fail("TYPE", path, "must be JSON data")
    return value


def _arm_configuration(adapter, value, path):
    required, allowed = _CONFIG_KEYS[adapter]
    config = _object(value, path, required, allowed)
    out = {}
    if adapter == "command":
        argv = _list(config["argv"], f"{path}/argv", 256, allow_empty=False)
        out["argv"] = [_text(a, f"{path}/argv/{i}", LIMITS["string_bytes"]) for i, a in enumerate(argv)]
    else:
        for key in ("binary", "checkout", "semantic_worker"):
            if key in config:
                out[key] = _text(config[key], f"{path}/{key}", LIMITS["string_bytes"])
        mode = config.get("semantic_mode", "off")
        if mode not in SEMANTIC_MODES:
            _fail("INVALID_VALUE", f"{path}/semantic_mode", f"must be one of {SEMANTIC_MODES}")
        # "on" without a worker stays representable: a real baseline must be able
        # to request semantic discovery and record labelled lexical fallback.
        out["semantic_mode"] = mode
    return out


def validate_spec(document: Any) -> dict:
    """Validate and normalize a `caplab-retrieval-spec/1` document.

    Normalization fills defaults (kind "note", shareable true, forbidden_ids [],
    stratum "answerable", semantic_mode "off"), sorts cutoffs and seeds, and adds
    nothing else. The result is suitable for `canonical_json` sealing.
    """
    spec = _object(document, "", _SPEC_KEYS, _SPEC_KEYS)
    if spec["schema_version"] != SPEC_SCHEMA:
        _fail("UNKNOWN_SCHEMA", "/schema_version", f"expected {SPEC_SCHEMA}")
    out = {"schema_version": SPEC_SCHEMA, "experiment_id": _slug(spec["experiment_id"], "/experiment_id")}

    corpus = _list(spec["corpus"], "/corpus", LIMITS["corpus"], allow_empty=False)
    notes, ids = [], set()
    for i, raw in enumerate(corpus):
        path = f"/corpus/{i}"
        note = _object(raw, path, {"id", "body"}, _NOTE_KEYS)
        nid = _slug(note["id"], f"{path}/id")
        if nid in ids:
            _fail("DUPLICATE_ID", f"{path}/id", f"duplicate note {nid!r}")
        ids.add(nid)
        item = {"id": nid, "body": _text(note["body"], f"{path}/body", LIMITS["body_bytes"]),
                "kind": _text(note.get("kind", "note"), f"{path}/kind", 64), "shareable": note.get("shareable", True)}
        if type(item["shareable"]) is not bool:
            _fail("TYPE", f"{path}/shareable", "must be a boolean")
        if "repo" in note:
            item["repo"] = _text(note["repo"], f"{path}/repo", LIMITS["string_bytes"])
        if "supersede_with" in note:
            item["supersede_with"] = _slug(note["supersede_with"], f"{path}/supersede_with")
        notes.append(item)
    for i, note in enumerate(notes):
        target = note.get("supersede_with")
        if target is not None and (target not in ids or target == note["id"]):
            _fail("UNKNOWN_ID", f"/corpus/{i}/supersede_with", "must name a different corpus note")
    out["corpus"] = notes

    queries = _list(spec["queries"], "/queries", LIMITS["queries"], allow_empty=False)
    qids, normalized = set(), []
    for i, raw in enumerate(queries):
        path = f"/queries/{i}"
        query = _object(raw, path, {"id", "text", "relevant_ids"}, _QUERY_KEYS)
        qid = _slug(query["id"], f"{path}/id")
        if qid in qids:
            _fail("DUPLICATE_ID", f"{path}/id", f"duplicate query {qid!r}")
        qids.add(qid)
        relevant = _unique_ids(_list(query["relevant_ids"], f"{path}/relevant_ids", LIMITS["labels"]), f"{path}/relevant_ids", ids)
        forbidden = _unique_ids(_list(query.get("forbidden_ids", []), f"{path}/forbidden_ids", LIMITS["labels"]), f"{path}/forbidden_ids", ids)
        overlap = sorted(set(relevant) & set(forbidden))
        if overlap:
            _fail("INCONSISTENT_LABELS", path, "relevant and forbidden overlap: " + ", ".join(overlap))
        stratum = _slug(query.get("stratum", ANSWERABLE), f"{path}/stratum")
        if stratum == ANSWERABLE and not relevant:
            _fail("INCONSISTENT_LABELS", f"{path}/stratum", "an answerable query needs relevant_ids; label empty-gold controls with another stratum")
        normalized.append({"id": qid, "text": _text(query["text"], f"{path}/text", LIMITS["text_bytes"]),
                           "relevant_ids": relevant, "forbidden_ids": forbidden, "stratum": stratum})
    out["queries"] = normalized

    arms = _list(spec["arms"], "/arms", LIMITS["arms"], allow_empty=False)
    arm_ids, arm_out = set(), []
    for i, raw in enumerate(arms):
        path = f"/arms/{i}"
        arm = _object(raw, path, _ARM_KEYS, _ARM_KEYS)
        aid = _slug(arm["id"], f"{path}/id")
        if aid in arm_ids:
            _fail("DUPLICATE_ID", f"{path}/id", f"duplicate arm {aid!r}")
        arm_ids.add(aid)
        if arm["adapter"] not in ADAPTERS:
            _fail("INVALID_VALUE", f"{path}/adapter", f"must be one of {ADAPTERS}")
        arm_out.append({"id": aid, "adapter": arm["adapter"],
                        "configuration": _arm_configuration(arm["adapter"], arm["configuration"], f"{path}/configuration")})
    out["arms"] = arm_out

    cutoffs = _list(spec["cutoffs"], "/cutoffs", LIMITS["cutoffs"], allow_empty=False)
    for i, k in enumerate(cutoffs):
        _integer(k, f"/cutoffs/{i}", 1, LIMITS["max_cutoff"])
    if len(set(cutoffs)) != len(cutoffs):
        _fail("DUPLICATE_ID", "/cutoffs", "cutoffs must be distinct")
    seeds = _list(spec["seeds"], "/seeds", LIMITS["seeds"], allow_empty=False)
    for i, s in enumerate(seeds):
        _integer(s, f"/seeds/{i}", 0, LIMITS["max_seed"])
    if len(set(seeds)) != len(seeds):
        _fail("DUPLICATE_ID", "/seeds", "seeds must be distinct")
    out["cutoffs"], out["seeds"] = sorted(cutoffs), sorted(seeds)
    out["timeout_seconds"] = _integer(spec["timeout_seconds"], "/timeout_seconds", 1, LIMITS["timeout_seconds"])
    return out


def assignment_id(arm: str, query_id: str, seed: int) -> str:
    return f"{arm}:{query_id}:{seed}"


def assignments(spec: dict) -> list[dict]:
    """The full sealed roster, in arm, query, seed order: every (arm, query, seed)."""
    return [{"assignment_id": assignment_id(a["id"], q["id"], s), "arm": a["id"], "query_id": q["id"], "seed": s}
            for a in spec["arms"] for q in spec["queries"] for s in spec["seeds"]]


def canonical_json(value: Any) -> bytes:
    """Deterministic UTF-8 JSON (sorted keys, no whitespace, no NaN) for sealing."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def spec_digest(spec: dict) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(spec)).hexdigest()


def validate_attempt(attempt: Any, spec: dict) -> dict:
    """Validate one attempt against a normalized spec; returns a normalized copy.

    `ranked_ids` must be unique corpus IDs; `delivered_ids` is None when the
    adapter did not observe delivery (never inferred from rank). Only `ok`
    attempts may carry results; any other status must carry a structured error
    (except `not_started`) and no ranked or delivered IDs.
    """
    a = _object(attempt, "", _ATTEMPT_KEYS - {"delivered_ids", "error", "observation"}, _ATTEMPT_KEYS)
    arms = {arm["id"] for arm in spec["arms"]}
    queries = {q["id"] for q in spec["queries"]}
    corpus = {n["id"] for n in spec["corpus"]}
    if a["arm"] not in arms:
        _fail("UNKNOWN_ID", "/arm", f"{a['arm']!r} is not a spec arm")
    if a["query_id"] not in queries:
        _fail("UNKNOWN_ID", "/query_id", f"{a['query_id']!r} is not a spec query")
    seed = a["seed"]
    if type(seed) is not int or seed not in spec["seeds"]:
        _fail("UNKNOWN_ID", "/seed", f"{seed!r} is not a spec seed")
    expected = assignment_id(a["arm"], a["query_id"], seed)
    if a["assignment_id"] != expected:
        _fail("INCONSISTENT_ASSIGNMENT", "/assignment_id", f"expected {expected!r}")
    status = a["status"]
    if status not in ATTEMPT_STATUSES:
        _fail("INVALID_VALUE", "/status", f"must be one of {ATTEMPT_STATUSES}")
    ranked = _unique_ids(_list(a["ranked_ids"], "/ranked_ids", LIMITS["ranked"]), "/ranked_ids", corpus)
    delivered = a.get("delivered_ids")
    if delivered is not None:
        delivered = _unique_ids(_list(delivered, "/delivered_ids", LIMITS["ranked"]), "/delivered_ids", corpus)
    latency = a["latency_ns"]
    if status == "not_started" and latency is None:
        pass
    else:
        _integer(latency, "/latency_ns", 0, LIMITS["latency_ns"])
    error = a.get("error")
    if status == "ok":
        if error is not None:
            _fail("INCONSISTENT_STATUS", "/error", "an ok attempt has no error")
    else:
        if ranked or delivered:
            _fail("INCONSISTENT_STATUS", "/ranked_ids", f"a {status} attempt carries no results")
        if status != "not_started":
            if not isinstance(error, dict) or not isinstance(error.get("code"), str) or not error["code"]:
                _fail("MISSING_FIELD", "/error", f"a {status} attempt needs an error object with a nonempty code")
        elif error is not None and not isinstance(error, dict):
            _fail("TYPE", "/error", "must be an object or null")
    if error is not None:
        _finite_json(error, "/error")
    observation = a.get("observation", {})
    if not isinstance(observation, dict):
        _fail("TYPE", "/observation", "must be an object")
    _finite_json(observation, "/observation")
    return {"assignment_id": expected, "arm": a["arm"], "query_id": a["query_id"], "seed": seed, "status": status,
            "ranked_ids": ranked, "delivered_ids": delivered, "latency_ns": latency, "error": error,
            "observation": observation}
