"""Shared fixtures for catalog-selection tests.

`FakeQuartermaster` is a process-boundary double for the ``catalog project`` command: it
proves how this consumer behaves around the argv seam (failures, timeouts, exact bytes
handed over). The installed Quartermaster tests keep its canned shape honest.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import stat
import sys
import textwrap
from pathlib import Path
from typing import Any

import test_revbench as rb

ROOT = Path(__file__).resolve().parents[1]
SOURCE = str(ROOT / "src")
POLICY = ROOT / "docs/product/contracts/native-agent-systems.json"
_INSTALLED = Path.home() / ".local/bin/quartermaster"
INSTALLED = shutil.which("quartermaster") or (str(_INSTALLED) if _INSTALLED.is_file() else None)
FIXED_SOURCE = os.environ.get("CAPLAB_TEST_QUARTERMASTER_SRC")  # Quartermaster source with a null native home

CANONICAL_HOME = "/fixture/striatum/harness-config/codex"
ALT_HOME = "/fixture/striatum/harness-config/codex-alt"


def route(route_id: str, model: str, *, harness="codex", efforts=("high",), accounts=("codex-main",),
          provider="openai") -> dict[str, Any]:
    return {"id": route_id, "provider": provider, "harness": harness, "model": model, "family": "gpt",
            "efforts": list(efforts), "billing": "subscription", "account_ids": list(accounts)}


def catalog_source(*extra_routes: dict[str, Any]) -> dict[str, Any]:
    def profile(name, account, home):
        return {"id": name, "host": "fixture-host", "consumer": "caplab", "account_id": account,
                "config_home": home, "credential_ref": None}

    def account(name, provider="openai"):
        return {"id": name, "provider": provider, "billing": "subscription", "quota_pool_ids": []}
    return {
        "document": "quartermaster-catalog/1",
        "routes": [route("terra", "gpt-5.6-terra", efforts=("max",)),
                   route("sol", "gpt-6.1-sol", accounts=("codex-main", "codex-alt")), *extra_routes],
        "accounts": [account("codex-main"), account("codex-alt")],
        "profiles": [profile("caplab-codex-main", "codex-main", CANONICAL_HOME),
                     profile("caplab-codex-alt", "codex-alt", ALT_HOME)],
        "aliases": [],
    }


def overlay(*, supervised=("codex", "codex-harm", "claude-code")) -> dict[str, Any]:
    return {
        "document": "quartermaster-consumer-overlay/1", "consumer": "caplab", "host": "fixture-host",
        "harnesses": {"codex": {"efforts": ["high", "max"], "native": {
            "native_harness_id": "codex", "executable": "codex", "version_command": ["codex", "--version"],
            "required_command_tokens": ["exec", "-m", "@model@", "-c", "model_reasoning_effort=@effort@"],
            "config_home": CANONICAL_HOME}}},
        "families": {},
        "accounts": {"codex-main": {"runtime_id": "codex", "population": "supervised-only"},
                     "codex-alt": {"runtime_id": "codex-harm", "population": "supervised-only"},
                     "claude-main": {"runtime_id": "claude-code", "population": "supervised-only"}},
        "discovery": {"roles": [], "metered": "include", "controls": {}},
        "defaults": {},
        "selections": [],
    }


def write_json(path: Path, document: Any) -> Path:
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def tree_snapshot(root: Path) -> list[tuple[str, int, str]]:
    """Every file under root, for proving a refusal changed nothing."""
    return sorted(
        (str(path.relative_to(root)), path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest())
        for path in root.rglob("*") if path.is_file())


def ledger_kinds(ledger: Path) -> list[str]:
    lines = (ledger / "registrations.jsonl").read_text().splitlines()
    return [json.loads(line)["kind"] for line in lines]


def canned_projection(release_id: str, *, tuple_overrides: dict[str, Any] | None = None,
                      key: str = "fixture-static-fixed", native: bool = True) -> dict[str, Any]:
    """What Quartermaster emits for the local-fixture subject (shape checked against the real CLI)."""
    tuple_ = {"model_id": rb.LOCAL_FIXTURE_MODEL, "native_harness_id": rb.LOCAL_FIXTURE_HARNESS, "effort": "fixed",
              "executable": "/usr/bin/true", "required_command_tokens": ["review"],
              "version_command": ["/usr/bin/true", "--version"], **(tuple_overrides or {})}
    entry = {"key": key, "origin": "discovered", "route_id": "fixture-static", "account_id": "fixture-account",
             "effort": "fixed", "profile_id": "caplab-fixture", "family": "fixture", "billing": "subscription",
             "model": tuple_["model_id"], "model_source": "route.model", "enabled": False, "roles": []}
    return {
        "document": "quartermaster-consumer-projection/1", "consumer": "caplab", "host": "fixture-host",
        "release_id": release_id, "overlay_sha256": "sha256:" + "a" * 64, "projection_id": "qcx-" + "b" * 64,
        "entries": [entry],
        "parts": [
            {"name": "sweep_challengers", "form": "fragment", "target": "t", "requires": ["r"],
             "content": {"challengers": []}},
            {"name": "sweep_population", "form": "fragment", "target": "t", "requires": ["r"],
             "content": {"supervised_only_runtimes": ["codex"], "afk_eligible_runtimes": []}},
            {"name": "native_agent_systems", "form": "proposal", "target": "t", "requires": ["r"],
             "content": {"systems": {key: tuple_} if native else {},
                         "excluded": [] if native else [{"key": key, "reason": "config_home_not_canonical"}]}},
        ],
        "rejected": [], "warnings": [],
    }


def fixture_release(home: str | None = None) -> dict[str, Any]:
    """A release-shaped document: Caplab only reads release_id, routes and profiles from it."""
    return {
        "document": "quartermaster-catalog-release/1", "release_id": "qcr-" + "c" * 64, "publisher": "fixture",
        "source": {"path": "/fixture/catalog.json", "sha256": "sha256:" + "d" * 64},
        "catalog": {
            "document": "quartermaster-catalog/1",
            "routes": [{"id": "fixture-static", "provider": "caplab-local-fixture", "harness": "static-fixture",
                        "model": rb.LOCAL_FIXTURE_MODEL, "family": "fixture", "efforts": ["fixed"],
                        "billing": "subscription", "account_ids": ["fixture-account"]}],
            "accounts": [{"id": "fixture-account", "provider": "caplab-local-fixture", "billing": "subscription",
                          "quota_pool_ids": []}],
            "profiles": [{"id": "caplab-fixture", "host": "fixture-host", "consumer": "caplab",
                          "account_id": "fixture-account", "config_home": home, "credential_ref": None}],
            "aliases": []},
    }


class FakeQuartermaster:
    """An executable that answers exactly ``catalog project RELEASE OVERLAY``."""

    def __init__(self, directory: Path, behavior: dict[str, Any] | None = None) -> None:
        self.directory = directory
        self.path = directory / "quartermaster"
        self.calls = directory / "calls.jsonl"
        self.behavior = directory / "behavior.json"
        self.set(behavior or {})
        self.path.write_text(textwrap.dedent(f"""\
            #!{sys.executable}
            import hashlib, json, pathlib, sys, time
            here = pathlib.Path(__file__).parent
            behavior = json.loads((here / "behavior.json").read_text())
            args = sys.argv[1:]
            record = {{"args": args[:2], "count": len(args), "cwd_is_temporary": "caplab-catalog-" in str(pathlib.Path.cwd())}}
            if len(args) == 4:
                release, overlay = (pathlib.Path(a) for a in args[2:])
                record.update(names=[release.name, overlay.name],
                              sha256=[hashlib.sha256(p.read_bytes()).hexdigest() for p in (release, overlay)])
                document = json.loads(release.read_text())
            with (here / "calls.jsonl").open("a") as stream:
                stream.write(json.dumps(record) + "\\n")
            time.sleep(behavior.get("sleep", 0))
            if behavior.get("stdout") is not None:
                text = behavior["stdout"]
                print(text if isinstance(text, str) else json.dumps(text).replace("__RELEASE_ID__", document["release_id"]))
            sys.exit(behavior.get("exit", 0))
            """))
        self.path.chmod(self.path.stat().st_mode | stat.S_IXUSR)

    def set(self, behavior: dict[str, Any]) -> None:
        self.behavior.write_text(json.dumps(behavior))

    def serve(self, projection: dict[str, Any]) -> None:
        body = copy.deepcopy(projection)
        body["release_id"] = "__RELEASE_ID__"
        self.set({"stdout": body})

    def recorded(self) -> list[dict[str, Any]]:
        return [json.loads(line) for line in self.calls.read_text().splitlines()] if self.calls.exists() else []
