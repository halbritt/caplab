"""Run the installed Quartermaster projection command and read its output.

The seam is one explicit argv: ``<command...> catalog project RELEASE OVERLAY``.
The release and overlay bytes read here are the bytes handed to Quartermaster
(through private copies), so retained provenance names what was consumed.
Quartermaster remains the only catalog validator and model inventory.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECTION_DOCUMENT = "quartermaster-consumer-projection/1"
CONSUMER = "caplab"
MAX_BYTES = 16 * 1024 * 1024
TIMEOUT_SECONDS = 60
_PASSED_ENVIRONMENT = ("PATH", "PYTHONPATH", "LANG", "LC_ALL", "SYSTEMROOT")
_PROJECTION_ID = re.compile(r"qcx-[0-9a-f]{64}\Z")
_RELEASE_ID = re.compile(r"qcr-[0-9a-f]{64}\Z")
_OVERLAY_DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
NATIVE_FIELDS = (
    "model_id",
    "native_harness_id",
    "effort",
    "executable",
    "required_command_tokens",
    "version_command",
)


class CatalogSelectionError(ValueError):
    """A catalog input was refused; the message is a stable lowercase code."""


@dataclass(frozen=True)
class Projection:
    """One Quartermaster projection plus the exact bytes it was made from."""

    command: tuple[str, ...]
    release_bytes: bytes
    overlay_bytes: bytes
    output_bytes: bytes
    document: dict[str, Any]
    release: dict[str, Any]

    def part(self, name: str) -> dict[str, Any]:
        return next(part for part in self.document["parts"] if part["name"] == name)


def _refuse(code: str) -> CatalogSelectionError:
    return CatalogSelectionError(code)


def _read(path: Path) -> bytes:
    try:
        data = Path(path).read_bytes()
    except OSError as error:
        raise _refuse("catalog_input_unreadable") from error
    if len(data) > MAX_BYTES:
        raise _refuse("catalog_input_too_large")
    return data


def _object(data: bytes, code: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise _refuse(code) from error
    if not isinstance(value, dict):
        raise _refuse(code)
    return value


def load_projection(
    release_path: Path,
    overlay_path: Path,
    command: Sequence[str],
    *,
    timeout: float = TIMEOUT_SECONDS,
) -> Projection:
    """Project one retained release through an explicitly configured command."""

    argv = tuple(command)
    if not argv or not all(isinstance(token, str) and token for token in argv):
        raise _refuse("catalog_quartermaster_argv_invalid")
    release_bytes, overlay_bytes = _read(release_path), _read(overlay_path)
    release = _object(release_bytes, "catalog_release_invalid")
    _object(overlay_bytes, "catalog_overlay_invalid")
    with tempfile.TemporaryDirectory(prefix="caplab-catalog-") as directory:
        copies = []
        for name, data in (("release.json", release_bytes), ("overlay.json", overlay_bytes)):
            copy = Path(directory, name)
            copy.write_bytes(data)
            copies.append(str(copy))
        environment = {k: os.environ[k] for k in _PASSED_ENVIRONMENT if k in os.environ}
        try:
            completed = subprocess.run(
                [*argv, "catalog", "project", *copies],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                cwd=directory,
                env=environment,
                timeout=timeout,
                check=False,
            )
        except (FileNotFoundError, PermissionError, NotADirectoryError) as error:
            raise _refuse("catalog_quartermaster_unavailable") from error
        except subprocess.TimeoutExpired as error:
            raise _refuse("catalog_projection_failed") from error
    if completed.returncode != 0:
        raise _refuse("catalog_projection_failed")
    if len(completed.stdout) > MAX_BYTES:
        raise _refuse("catalog_projection_invalid")
    document = _object(completed.stdout, "catalog_projection_invalid")
    _validate_projection(document, release)
    return Projection(argv, release_bytes, overlay_bytes, completed.stdout, document, release)


def _validate_projection(document: dict[str, Any], release: dict[str, Any]) -> None:
    """Check only what this consumer relies on; Quartermaster owns the rest."""

    def text(value: Any, pattern: re.Pattern[str] | None = None) -> bool:
        return isinstance(value, str) and (pattern is None or bool(pattern.match(value)))

    if document.get("document") != PROJECTION_DOCUMENT:
        raise _refuse("catalog_projection_invalid")
    if document.get("consumer") != CONSUMER:
        raise _refuse("catalog_projection_consumer_mismatch")
    if not (
        text(document.get("projection_id"), _PROJECTION_ID)
        and text(document.get("release_id"), _RELEASE_ID)
        and text(document.get("overlay_sha256"), _OVERLAY_DIGEST)
        and text(document.get("host"))
    ):
        raise _refuse("catalog_projection_invalid")
    if document["release_id"] != release.get("release_id"):
        raise _refuse("catalog_release_mismatch")
    entries, parts = document.get("entries"), document.get("parts")
    if not isinstance(entries, list) or not isinstance(parts, list):
        raise _refuse("catalog_projection_invalid")
    keys = set()
    for entry in entries:
        if not isinstance(entry, dict) or not all(
            text(entry.get(field))
            for field in ("key", "origin", "route_id", "account_id", "effort", "profile_id", "model")
        ) or not isinstance(entry.get("enabled"), bool) or entry["key"] in keys:
            raise _refuse("catalog_projection_invalid")
        keys.add(entry["key"])
    expected = {"sweep_challengers": "fragment", "sweep_population": "fragment",
                "native_agent_systems": "proposal"}
    named = {part.get("name"): part for part in parts if isinstance(part, dict)}
    for name, form in expected.items():
        if named.get(name, {}).get("form") != form or not isinstance(named[name].get("content"), dict):
            raise _refuse("catalog_projection_invalid")
    native = named["native_agent_systems"]["content"]
    systems, excluded = native.get("systems"), native.get("excluded")
    if not isinstance(systems, dict) or not isinstance(excluded, list):
        raise _refuse("catalog_projection_invalid")
    for key, system in systems.items():
        if key not in keys or not isinstance(system, dict) or set(system) != set(NATIVE_FIELDS):
            raise _refuse("catalog_projection_invalid")
    population = named["sweep_population"]["content"]
    for field in ("supervised_only_runtimes", "afk_eligible_runtimes"):
        runtimes = population.get(field)
        if not isinstance(runtimes, list) or not all(text(item) for item in runtimes):
            raise _refuse("catalog_projection_invalid")
    catalog = release.get("catalog")
    if not isinstance(catalog, dict) or not all(
        isinstance(catalog.get(name), list) for name in ("routes", "accounts", "profiles")
    ):
        raise _refuse("catalog_release_invalid")
