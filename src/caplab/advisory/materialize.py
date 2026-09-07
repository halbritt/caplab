"""Materialize a case's base production into its workspace (plan tree-v1 rev 2 §2.3–2.4).

Every case gets exactly what production gave its reviewer, written as plain
files under `<case>/base/`, with recoverable exchange objects the artifact
names under `<case>/evidence/`, and a manifest whose digest is verified
before and after every attempt. Nothing here talks to a model.

Base sources (the §2.3 amendment, council #57):

- `whole-tree`: a repo-doc's repository at its registered commit
  (`git archive`); an anchored-era change set's `materialized_base` object
  (the git tree at the anchor commit with the product overlay, as
  striatum's driver expanded it for the run); or a change set whose body
  carries a `git-tree` anchor whose commit is in history.
- `partial-product-tree`: the product object a change set declares
  (`base.content_hash` or `base_composition.resulting_base_hash`) when the
  store still holds it and no whole tree does.
- `none-by-design`: exchange prose; production pinned the artifact alone.
- `lost`: a change set whose declared base object is absent from the store.

The per-substrate source is precomputed into a base registry
(`advisory/tree-v1-bases.json`, built by scripts/tree_v1_bases.py from the
striatum ledger, the graph store and git) so that materialization at sweep
time needs no ledger and no model of striatum's internals.

Product canonical form and tree hash reproduce striatum's
`changeset.CanonicalProduct` / `TreeHash` (Go `json.MarshalIndent` with two
spaces, struct field order, a trailing newline, HTML-safe escaping); the
oracle in scripts/tree_v1_bases.py proves the reproduction against every
stored object it touches, and a change set whose declared hashes do not
re-derive fails closed there.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import unicodedata

GRAPH_STORE = os.path.expanduser(
    "~/.local/share/striatum/graphs/019f22ef-0cb4-780f-9b82-b210bab24325")
REPOS = {"caplab": os.path.expanduser("~/git/caplab"),
         "striatum-next": os.path.expanduser("~/git/striatum-next")}
BASE_SOURCES = ("whole-tree", "partial-product-tree", "none-by-design", "lost")
MANIFEST_RECORD = "caplab-tree-v1-base-manifest/1"


# --- graph store objects ---------------------------------------------------

def store_object(content_hash: str, root: str = GRAPH_STORE) -> bytes | None:
    """The decompressed bytes of a graph-store object, or None when absent
    or undecodable (an object that will not decode is, for base purposes,
    absent — and the caller says so)."""
    path = os.path.join(root, "objects", "sha256", content_hash[:2],
                        content_hash[2:4], content_hash + ".zst")
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:4] != b"SOB1":
        return None
    done = subprocess.run(["zstd", "-d", "-c"], input=raw[16:], capture_output=True)
    if done.returncode != 0:
        return None
    if hashlib.sha256(done.stdout).hexdigest() != content_hash:
        return None
    return done.stdout


# --- striatum's product tree, reproduced -----------------------------------

def _go_json(value) -> str:
    """Go's encoding/json rendering of a Python value, indent two spaces:
    map keys sorted, `<`, `>`, `&`, U+2028 and U+2029 escaped."""
    text = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False)
    return (text.replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026").replace("\u2028", "\\u2028")
            .replace("\u2029", "\\u2029"))


def canonical_product(files: dict, anchor: dict | None = None,
                      deletes: list | None = None) -> bytes:
    """changeset.CanonicalProduct: struct order schema_version, files,
    anchor (omitempty), deletes (omitempty); files sorted by key; newline."""
    product: dict = {"schema_version": 1, "files": {k: files[k] for k in sorted(files)}}
    if anchor:
        product["anchor"] = anchor
    if deletes:
        product["deletes"] = list(deletes)
    return (_go_json(product) + "\n").encode()


def tree_hash(files: dict, anchor: dict | None = None, deletes: list | None = None) -> str:
    return hashlib.sha256(canonical_product(files, anchor, deletes)).hexdigest()


def apply_overlay(base: dict, change_set: dict) -> tuple[dict | None, list[dict]]:
    """changeset.ApplyOverlay: the change set's deletes then files onto the
    base product. Returns (product, conflicts); anchored bases carry deletes
    as tombstones, unanchored bases refuse a delete of an absent path."""
    files = dict(base.get("files") or {})
    anchor = base.get("anchor")
    cs_files = change_set.get("files") or {}
    cs_deletes = sorted(change_set.get("deletes") or [])
    if anchor:
        tombstones = set(base.get("deletes") or [])
        for path in cs_deletes:
            files.pop(path, None)
            tombstones.add(path)
        for path in sorted(cs_files):
            files[path] = cs_files[path]
            tombstones.discard(path)
        return {"schema_version": 1, "files": files, "anchor": anchor,
                "deletes": sorted(tombstones)}, []
    conflicts = []
    for path in cs_deletes:
        if path not in files:
            conflicts.append({"class": "apply_failure", "path": path,
                              "detail": "delete of a path absent from the base"})
            continue
        del files[path]
    for path in sorted(cs_files):
        files[path] = cs_files[path]
    if conflicts:
        return None, conflicts
    return {"schema_version": 1, "files": files}, []


def declared_base_hash(change_set: dict) -> str | None:
    """changeset.BaseHash: v1 `base.content_hash`, v2
    `base_composition.resulting_base_hash`."""
    if change_set.get("schema_version") == 2 or "base_composition" in change_set:
        return (change_set.get("base_composition") or {}).get("resulting_base_hash")
    return (change_set.get("base") or {}).get("content_hash")


# --- writing a tree safely -------------------------------------------------

class UnsafeEntry(ValueError):
    pass


def _normalize(path: str) -> str:
    if not path or path.startswith("/") or "\\" in path:
        raise UnsafeEntry(f"refusing path {path!r}")
    parts = path.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise UnsafeEntry(f"refusing path {path!r}")
    return unicodedata.normalize("NFC", path)


def write_files(files: dict, dest: str) -> list[dict]:
    """Write `files` (path -> text) under `dest`. Rejects absolute paths,
    `..`, empty components, duplicates after normalization and case-fold
    collisions. Returns the manifest entries."""
    seen_norm: set[str] = set()
    seen_fold: set[str] = set()
    entries = []
    for path in sorted(files):
        norm = _normalize(path)
        if norm in seen_norm:
            raise UnsafeEntry(f"duplicate normalized path {norm!r}")
        fold = norm.casefold()
        if fold in seen_fold:
            raise UnsafeEntry(f"case-fold collision on {norm!r}")
        seen_norm.add(norm)
        seen_fold.add(fold)
        content = files[path]
        if not isinstance(content, str):
            raise UnsafeEntry(f"non-text content at {path!r}")
        data = content.encode("utf-8")
        full = os.path.join(dest, norm)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(data)
        os.chmod(full, 0o444)
        entries.append({"path": norm, "type": "file", "mode": "0444",
                        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    return entries


def git_archive_files(repo: str, commit: str) -> dict:
    """The repository's tracked text files at `commit`, as path -> text.
    Binary files (undecodable as UTF-8) are omitted and listed by the
    manifest; symlinks are omitted (a symlink to an absolute path is an
    unsafe entry, and a relative one is not content the reviewer needs)."""
    listing = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "-z", commit],
                             capture_output=True, check=True).stdout
    files, skipped = {}, []
    for rec in listing.split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        mode, _kind, blob = meta.decode().split()
        rel = path.decode("utf-8", errors="surrogateescape")
        if mode == "120000":
            skipped.append({"path": rel, "why": "symlink"})
            continue
        if mode == "160000":
            skipped.append({"path": rel, "why": "submodule"})
            continue
        data = subprocess.run(["git", "-C", repo, "cat-file", "blob", blob],
                              capture_output=True, check=True).stdout
        try:
            files[rel] = data.decode("utf-8")
        except UnicodeDecodeError:
            skipped.append({"path": rel, "why": "binary"})
    files["__skipped__"] = skipped  # popped by the caller
    return files


# --- the materializer ------------------------------------------------------

def base_files(record: dict) -> tuple[dict | None, list[dict], dict]:
    """(files, skipped, identity) for one base-registry record, or (None, [],
    identity) for a case with no base. Raises when a recorded source is no
    longer reachable — the registry said it was, and silence would score
    the case as if it were."""
    source = record["base_source"]
    how = record.get("materializer")
    identity = {"base_source": source, "materializer": how}
    if source in ("none-by-design", "lost"):
        return None, [], identity
    if how == "git-archive":
        repo = REPOS[record["repo"]]
        files = git_archive_files(repo, record["commit"])
        skipped = files.pop("__skipped__")
        identity.update(repo=record["repo"], commit=record["commit"])
        return files, skipped, identity
    if how in ("materialized_base", "product-object"):
        body = store_object(record["object"])
        if body is None:
            raise RuntimeError(f"{record['object']} left the store since the registry was built")
        product = json.loads(body)
        identity.update(object=record["object"], anchor=product.get("anchor"))
        return dict(product.get("files") or {}), [], identity
    raise ValueError(f"unknown materializer {how!r}")


def materialize_case(record: dict, case_dir: str) -> dict:
    """Write `base/`, `evidence/` and `base-manifest.json` for one case.
    Idempotent: an existing materialization whose manifest verifies is kept."""
    manifest_path = os.path.join(case_dir, "base-manifest.json")
    if os.path.isfile(manifest_path) and verify_manifest(case_dir):
        with open(manifest_path, encoding="utf-8") as f:
            return json.load(f)
    for sub in ("base", "evidence"):
        shutil.rmtree(os.path.join(case_dir, sub), ignore_errors=True)
    os.makedirs(case_dir, exist_ok=True)
    files, skipped, identity = base_files(record)
    entries: list[dict] = []
    if files is not None:
        base_dir = os.path.join(case_dir, "base")
        os.makedirs(base_dir)
        entries = write_files(files, base_dir)
    evidence_entries = []
    for item in record.get("evidence") or []:
        ev_dir = os.path.join(case_dir, "evidence", "exchange")
        os.makedirs(ev_dir, exist_ok=True)
        data = (json.dumps(item["payload"], indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode()
        name = f"{item['name']}.json"
        with open(os.path.join(ev_dir, name), "wb") as f:
            f.write(data)
        evidence_entries.append({"path": f"exchange/{name}", "kind": item["kind"],
                                 "ledger_seq": item.get("seq"),
                                 "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    manifest = {
        "record": MANIFEST_RECORD,
        "substrate_id": record.get("substrate_id"),
        **identity,
        "entries": entries,
        "skipped": skipped,
        "evidence": evidence_entries,
        "file_count": len(entries),
        "bytes": sum(e["bytes"] for e in entries),
    }
    manifest["digest"] = manifest_digest(manifest)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
        f.write("\n")
    return manifest


def manifest_digest(manifest: dict) -> str:
    body = {k: v for k, v in manifest.items() if k != "digest"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def verify_manifest(case_dir: str) -> bool:
    """True when every manifest entry is present with its recorded digest and
    nothing else exists under base/ and evidence/."""
    manifest_path = os.path.join(case_dir, "base-manifest.json")
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except (OSError, ValueError):
        return False
    if manifest.get("digest") != manifest_digest(manifest):
        return False
    for root_name, key in (("base", "entries"), ("evidence", "evidence")):
        root = os.path.join(case_dir, root_name)
        expected = {e["path"]: e["sha256"] for e in manifest.get(key) or []}
        found = {}
        if os.path.isdir(root):
            for dirpath, dirnames, filenames in os.walk(root):
                for name in filenames:
                    full = os.path.join(dirpath, name)
                    if os.path.islink(full):
                        return False
                    with open(full, "rb") as f:
                        found[os.path.relpath(full, root)] = hashlib.sha256(f.read()).hexdigest()
        elif expected:
            return False
        if found != expected:
            return False
    return True


def load_registry(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    return doc["bases"] if "bases" in doc else doc
