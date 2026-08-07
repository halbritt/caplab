"""Lane-faithful prompt rendering and workspace preparation for benchmarking.

The 2026-08-07 audit found that every endpoint-path number measured to date was
invalid because the eval split replayed *another lane's* prompt: 87 of 98
examples originated on argv-mode lanes, where large input bodies are spilled out
of the prompt and replaced with "read it from there" pointers to paths that do
not exist at replay time. A chat endpoint asked to review an artifact it cannot
see rubber-stamps, and the resulting number describes nothing.

This module makes a benchmark row mean what it claims by preparing, per example,
the two things the production supervisor prepares:

  * a real workspace, with the sealed bundle materialized into it, so every
    path the prompt names resolves to the byte-identical body the original
    lane saw; and
  * a prompt rendered for THE LANE BEING MEASURED — inline-everything for a
    stdin/stdout endpoint, the declaration's own transport (with the argv spill
    loop) for a harness lane — against THAT workspace, never a foreign one.

Rendering is delegated to render.py, the byte-exact port of prompt.go, so
nothing here reimplements prompt shape.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass

import render

# The declaration flag that separates the two lane classes. A lane that declares
# it has no filesystem to write into: its whole answer is stdout, and the
# supervisor bridges that to the required output file. Anything else is a coding
# harness that writes its own files.
STDOUT_ONLY = "single-required-output"


@dataclass
class Lane:
    """The measurable facts of a backend declaration's adapter block."""

    backend_id: str
    command: list[str]
    prompt_mode: str
    stdout_only: bool

    def with_provider(self, endpoint: str) -> "Lane":
        """This lane pinned to a different OpenRouter endpoint.

        The declaration's own pin is the production fact; this is for asking
        what a different endpoint would do, which is a question about provider
        selection rather than about the model. Callers record the override.
        """
        command = list(self.command)
        if "-openrouter-provider" in command:
            command[command.index("-openrouter-provider") + 1] = endpoint
        else:
            command += ["-openrouter-provider", endpoint]
        return Lane(self.backend_id, command, self.prompt_mode, self.stdout_only)

    @classmethod
    def from_declaration(cls, declaration: dict) -> "Lane":
        adapter = declaration.get("adapter") or {}
        command = adapter.get("command")
        if not command:
            raise ValueError(f"{declaration.get('id')!r}: declaration has no adapter.command")
        mode = adapter.get("prompt_mode", "stdin")
        if mode not in ("arg", "stdin"):
            raise ValueError(f"{declaration.get('id')!r}: unsupported prompt_mode {mode!r}")
        return cls(
            backend_id=declaration.get("id", ""),
            command=list(command),
            prompt_mode=mode,
            stdout_only=adapter.get("stdout_output") == STDOUT_ONLY,
        )


def required_outputs(manifest: dict) -> list[str]:
    """The output ids the dispatch declares REQUIRED.

    A harness lane is scored on these by name. The previous runner scored the
    newest file in outputs/ instead, so codex — which writes ASSUMPTIONS.md
    after its review-ledger — was scored on its assumptions note, and most of
    the 2026-08-07 harness rows recorded a null verdict for that reason alone.
    """
    return [
        expected["output_id"]
        for expected in manifest.get("expected_outputs") or []
        if expected.get("required")
    ]


def materialize(bundle_dir: str, workspace: str) -> None:
    """Copy the sealed dispatch bundle into a fresh per-example workspace.

    Every environment entry and pinned input is placed at exactly the relative
    path the manifest names, because that is the path the rendered prompt will
    cite. The workspace is rebuilt from scratch each time: a leftover outputs/
    from a previous run would otherwise be scored as this run's answer.
    """
    if os.path.isdir(workspace):
        shutil.rmtree(workspace)
    for subdir in ("environment", "inputs"):
        source = os.path.join(bundle_dir, subdir)
        if os.path.isdir(source):
            shutil.copytree(source, os.path.join(workspace, subdir))
    os.makedirs(os.path.join(workspace, "outputs"), exist_ok=True)


def render_for(lane: Lane, manifest: dict, bundle_dir: str, workspace: str,
               transport: str) -> tuple[bytes, list[str]]:
    """Render the prompt this lane would actually receive for this example.

    transport "fair" renders stdin-mode — every environment entry and input
    inlined — which is what a one-shot chat endpoint must get to see its
    subject at all. transport "declared" replays the declaration's own
    prompt_mode including prompt.go's greedy argv spill loop, which is what a
    harness lane genuinely receives in production; its spilled bodies resolve
    because materialize() put them in this workspace.

    Returns (prompt, dispositions).
    """
    if transport not in ("fair", "declared"):
        raise ValueError(f"unknown transport {transport!r}")
    mode = "stdin" if transport == "fair" else lane.prompt_mode
    return render.render_with_spill(manifest, bundle_dir, workspace, b"", mode)


def subject_visible(dispositions: list[str], workspace: str, manifest: dict) -> bool:
    """Whether this prompt actually lets the model reach its review subject.

    Inlined bodies are visible by construction. A spilled body is visible only
    if the file it points at exists in the workspace the prompt names — the
    exact condition the invalid 2026-08-07 runs failed, and the reason this is
    recorded per row rather than assumed.
    """
    schema_version = manifest.get("schema_version", 1)
    entries = render.materialized_entries(manifest.get("environment") or {}, schema_version)
    paths = [e.path for e in entries] + [i["path"] for i in manifest.get("inputs") or []]
    if len(dispositions) != len(paths):
        return False
    return all(
        disposition == "inline" or os.path.isfile(os.path.join(workspace, path))
        for disposition, path in zip(dispositions, paths)
    )
