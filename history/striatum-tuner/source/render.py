"""Faithful Python port of striatum-next's lane prompt renderer.

Source of truth: internal/backend/llm/prompt.go (renderPromptProjection,
kindInstruction, reviewLedgerInstruction, anchoredSubjectChangeSetInstruction).
The port is byte-exact: rendered prompts are verified against the
`rendered_prompt_hash` each submission's attempt closure recorded, so any
drift from the Go renderer is detected per-example, never silently absorbed.

All rendering is done in bytes; artifact bodies are inserted verbatim.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass

ONE_SHOT_PREAMBLE = (
    "You are one execution lane of one compiler pass run. This is a one-shot,\n"
    "non-interactive dispatch: never ask questions, never wait for input. When the\n"
    "task is ambiguous, choose the most conservative interpretation and record\n"
    "every assumption you made as a bullet list in the file outputs/ASSUMPTIONS.md\n"
    "(create it only if you made assumptions). Do the work now — do not describe a\n"
    "plan and exit."
)

OUTPUT_RULES = (
    "Write every required output as a single file at exactly the path given,\n"
    "relative to your working directory. Markdown artifact bodies must give every\n"
    "heading an element anchor suffix of the form {#el:slug} (stable, kebab-case).\n"
    "Do not create files outside the outputs/ directory except scratch work."
)

PACKET_CHANGE_SET_REVIEW_CONTEXT_SCHEMA = "packet-change-set-review/1"


def go_quote(s: str) -> str:
    """Go's %q for a string. The values quoted in prompt.go are identities and
    hex hashes (plain printable ASCII), for which %q equals JSON quoting."""
    return json.dumps(s, ensure_ascii=True)


def review_ledger_instruction(subject: dict[str, str]) -> str:
    instruction = (
        'This output is JSON, not markdown: {"posture": "<review posture>", "verdict": '
        '"accept" | "accept_with_findings" | "needs_revision" | "reject", "summary": '
        '"<one paragraph>", "findings": [{"severity": "major" | "minor", "finding": "..."}]}. '
        "Review the pinned input independently and adversarially; accept only work that is "
        "internally coherent, complete for its stage, and consistent with the environment "
        "excerpts. An accept_with_findings verdict lists only minor findings."
    )
    if (
        subject.get("review_context_schema") != PACKET_CHANGE_SET_REVIEW_CONTEXT_SCHEMA
        or subject.get("base_mode") != "anchored-expanded"
    ):
        return instruction
    g = lambda k: subject.get(k, "")
    return instruction + (
        " This anchored Change Set review carries a sealed mechanical context ({}). "
        "The candidate's base_composition.resulting_base_hash={} equals base_pin_hash={}; "
        "both name the compact anchored Product-body identity, not the expanded application "
        "tree or the result tree. inputs/00-base-pin carries that compact Product body. "
        "inputs/01-base is the expanded inline Product tree whose hash is "
        "materialized_base_hash={}; the mechanical expansion reports "
        "base_materialization_succeeded={}, derived_materialized_base_hash={}, and "
        "materialized_base_matches_derived={}. inputs/01-base is the overlay application "
        "base (overlay_application_base_hash={}). base_pin_equals_materialized_base={} is "
        "expected for these two different representations; hash inequality is not a defect, "
        "and the compact Product body must never be used as the application tree. "
        "Independently inspect the candidate overlay against inputs/01-base; the mechanical "
        "derivation reports result_derivation_succeeded={}, derived_result_tree_hash={}, "
        "result_tree_hash={}, and derived_result_matches_declared={}. Validate "
        "packet_anchor={} and packet_element_hash={} against the exact origin Work Graph at "
        "inputs/02-work-graph (work_graph_version_hash={}), not against any historical Work "
        "Graph embedded in the Product. The mechanical packet derivation reports "
        "packet_element_derivation_succeeded={}, derived_packet_element_hash={}, and "
        "packet_element_matches_declared={}. A false derivation or match is a candidate "
        "defect to report, not missing review context."
    ).format(
        g("review_context_schema"),
        g("resulting_base_hash"),
        g("base_pin_hash"),
        g("materialized_base_hash"),
        g("base_materialization_succeeded"),
        g("derived_materialized_base_hash"),
        g("materialized_base_matches_derived"),
        g("overlay_application_base_hash"),
        g("base_pin_equals_materialized_base"),
        g("result_derivation_succeeded"),
        g("derived_result_tree_hash"),
        g("result_tree_hash"),
        g("derived_result_matches_declared"),
        g("packet_anchor"),
        g("packet_element_hash"),
        g("work_graph_version_hash"),
        g("packet_element_derivation_succeeded"),
        g("derived_packet_element_hash"),
        g("packet_element_matches_declared"),
    )


PROPOSAL_INSTRUCTION = (
    "A proposal states problem, motivation, target state, explicit non-goals, and "
    "constraints — no architectural commitments, interface definitions, or "
    "implementation sequencing (those belong to later stages)."
)

DESIGN_INSTRUCTION = (
    'A design states what should exist and why: the decision structure, alternatives '
    'considered and rejected with reasons, and a "## Decision (clauses)" section whose '
    "bullet clauses (bold-titled, numbered C1, C2, ...) are the binding semantic state a "
    'decision record will project verbatim. Include "## Consequences" and "## Constrains" '
    "sections."
)

IMPLEMENTATION_PLAN_INSTRUCTION = (
    "An implementation plan states how the design is built or encoded: ordered work with "
    "acceptance criteria and verification mapping, honest deferrals, and no new "
    "architectural decisions (those belong to the design). Fix the packet boundaries and "
    "semantic application order in a fenced ```striatum-work-graph block containing JSON "
    '{"packets": [{"id": "...", "purpose": "...", "derived_from": "<plan-element anchor>", '
    '"inputs": ["<declared input>"], "outputs": ["<declared output>"], "depends_on": '
    '["<sibling id>"], "write_scope": ["<path prefix>"], "acceptance_checks": '
    '["<registered check set or id>"]}], "index": ["<every packet id exactly once in '
    'authored topological application order>"]}: one packet per independently buildable '
    "unit, parallel packets declaring disjoint write scopes, every packet deriving from a "
    "plan element. The index is semantic and MUST be authored; packetization validates it "
    "and never recomputes it from packet names. Every list field is explicit, including "
    "empty inputs and depends_on. Each acceptance_checks entry MUST already exist in the "
    "repository check registry — either a registered check-set name or a registered "
    "check id — or work-graph legality refuses the packet "
    '(acceptance_check_unresolvable); the always-available sets are "code" (mechanical '
    'build/test teeth, for any code or data packet), "subject-default" (markdown '
    "body-anchor checks, ONLY for a packet whose write scope is prose/docs it authors), "
    'and "stalls-guards". A packet may NOT name a check it introduces, nor an '
    "acceptance-criteria label (ac-1.1) or a made-up id (check:foo): a new check this "
    "delivery adds is delivery work — the packet writes the check entrypoint AND "
    'registers it in policy/checks/repository.json, gates itself on "code", and names the '
    "new set only in prose acceptance criteria. Packetization lowers this block "
    "mechanically."
)

IMPLEMENTATION_PLAN_TREE_NOTE = (
    ' The current repository tree is staged at inputs/01-base — this is the "current '
    'integrated head" your design\'s seam descriptions resolve against. Use it to CONFIRM '
    "each seam (each existing file or place the design describes) denotes exactly one "
    "location, and to name real, existing paths as packet write_scope prefixes and (where "
    "a packet edits an existing file) outputs. A work-graph packet names FILES and "
    "DIRECTORIES, never functions or symbols: a packet whose purpose is to change a seam "
    "declares the containing file/directory in write_scope and states the seam's definite "
    "description in its purpose; the concrete function and call-site binding is the build "
    "lane's work against this same tree, guided by that purpose. A definite description "
    "that does not denote in inputs/01-base, or denotes ambiguously, is a real finding "
    "against the design to state in prose — never a reason to emit no work graph. You "
    "always have enough to author a complete, machine-parseable work graph over the staged "
    "tree; producing a pass-error or refusal instead of the work-graph block is itself a "
    "defect."
)

CHANGE_SET_PACKETLESS_INSTRUCTION = (
    'This output is JSON, not markdown. Emit a packetless schema_version 1 Change Set: '
    '{"schema_version": 1, "base": {"product_identity": "", "content_hash": ""}, "packet": '
    '{"work_graph_identity": "", "work_graph_hash": "", "packet_id": ""}, "files": '
    '{"<path>": "<full new file content>"}, "deletes": [], "result_tree_hash": "<hash of '
    'the standalone files tree>"}. This build has no sealed packet or base-composition '
    "context. Do not invent packet or base-composition pins: leave every v1 base and "
    "packet field empty and do not emit base_composition. files carries FULL new file "
    "content, never a diff; deletes is explicit and empty because the base is empty; "
    "result_tree_hash is computed over the standalone files tree (the resulting tree IS "
    "exactly your files map, since the base is empty). result_tree_hash is NOT a guess and "
    "NOT a hash of your JSON: it is sha256 over the CANONICAL LINKED TREE, defined exactly "
    'as json.MarshalIndent({"schema_version": 1, "files": {<every path in the resulting '
    'tree>: <full content>}}, "", "  ") with a single trailing newline appended. Keys are '
    "Go's json ordering (schema_version, files, then files keys sorted lexicographically) "
    "and the indent is two spaces. Compute it mechanically — write the tree to a file "
    "and hash it, never estimate it. A declared hash that does not equal the derived one "
    "is refused at admission and the whole build is rebuilt, so verify it before you emit. "
    "Produce real, correct code. Every Go source file MUST be gofmt-canonical and each "
    "file ends with exactly one newline after its last non-blank line."
)

CHANGE_SET_PACKET_INSTRUCTION = (
    "This output is JSON, not markdown. Emit schema_version 2 and echo the objective's "
    'exact packet and base-composition context: {"schema_version": 2, "packet": '
    '{"work_graph_identity": "...", "work_graph_version_hash": "...", "packet_anchor": '
    '"...", "packet_element_hash": "..."}, "base_composition": {"observed_product": '
    '{"identity": "...", "version_seq": 1, "content_hash": "..."}, "ancestors": '
    '[{"application_index": 0, "change_set": {"identity": "...", "version_seq": 1, '
    '"content_hash": "..."}}], "resulting_base_hash": "..."}, "files": {"<path>": "<full '
    'new file content>"}, "deletes": ["<path>"], "result_tree_hash": "<hash of base plus '
    'overlay>"}. Implement exactly the packet named in the objective, editing against the '
    "composed base provided as the pinned input. Every path in files and deletes MUST fall "
    "within the packet's write_scope — writes outside it are refused. files carries "
    "FULL new file content, never a diff. Do not reconstruct or shorten any pin: copy "
    "every packet/base field verbatim from the sealed objective. Compute result_tree_hash "
    "by applying files and deletes to the fully materialized Product tree at "
    "inputs/01-base, then hashing that resulting tree. If inputs/00-base-pin exists, it is "
    "compact anchored identity only: never use it as the application tree or as the tree "
    "hashed for result_tree_hash. Anchors are expanded before overlay application; "
    "inputs/01-base already carries the expanded tree. result_tree_hash is NOT a guess and "
    "NOT a hash of your JSON: it is sha256 over the CANONICAL LINKED TREE, defined exactly "
    'as json.MarshalIndent({"schema_version": 1, "files": {<every path in the resulting '
    'tree>: <full content>}}, "", "  ") with a single trailing newline appended. Keys are '
    "Go's json ordering (schema_version, files, then files keys sorted lexicographically) "
    "and the indent is two spaces. Compute it mechanically — write the tree to a file "
    "and hash it, never estimate it. A declared hash that does not equal the derived one "
    "is refused at admission and the whole build is rebuilt, so verify it before you emit. "
    "Produce real, correct code. Every Go source file MUST be gofmt-canonical and each "
    "file ends with exactly one newline after its last non-blank line."
)


def anchored_subject_change_set_instruction(base_hash: str, observed_product: str) -> str:
    op, bh = go_quote(observed_product), go_quote(base_hash)
    return (
        "This output is JSON, not markdown. Emit a schema_version 1 anchored Change Set: "
        '{{"schema_version": 1, "base": {{"product_identity": {op}, "content_hash": {bh}}}, '
        '"packet": {{"work_graph_identity": "", "work_graph_hash": "", "packet_id": ""}}, '
        '"files": {{"<path>": "<full new file content>"}}, "deletes": ["<path>"], '
        '"result_tree_hash": "<hash of the repository tree at inputs/01-base with your '
        'overlay applied>"}}. The base is the CURRENT repository tree, staged expanded at '
        "inputs/01-base and pinned compact at inputs/00-base-pin whose content_hash is "
        "{bh} — copy that hash verbatim into base.content_hash, and do NOT invent a "
        "work-graph or packet pin (leave them empty). Your files and deletes are your "
        "delivery OVERLAID ONTO the repository at inputs/01-base: files carries FULL new "
        "content for every path you add or modify, deletes lists paths you remove. Do NOT "
        "add go.mod, go.sum, or re-emit unchanged repository files — they already "
        "exist in the base; emitting a standalone tree that drops the repository is the "
        "hollow-Product defect this shape exists to prevent. Compute result_tree_hash by "
        "applying files and deletes to the fully materialized tree at inputs/01-base, then "
        "hashing that resulting tree — the canonical linked tree is "
        'json.MarshalIndent({{"schema_version": 1, "files": {{<every path in the resulting '
        'tree>: <full content>}}}}, "", "  ") with one trailing newline, sha256\'d; write '
        "it to a file and hash it, never estimate it. Produce real, correct code that "
        "builds against the repository (go build ./... over inputs/01-base plus your "
        "overlay must pass). Every Go source file MUST be gofmt-canonical and end with "
        "exactly one newline."
    ).format(op=op, bh=bh)


PACKET_BUILD_CONTEXT_KEYS = (
    "packet_anchor",
    "base_composition",
    "work_graph_identity",
    "work_graph_version_hash",
    "packet_element_hash",
    "resulting_base_hash",
    "write_scope",
)


def has_packet_build_context(subject: dict[str, str]) -> bool:
    return any(k in subject for k in PACKET_BUILD_CONTEXT_KEYS)


def kind_instruction(kind: str, subject: dict[str, str]) -> str:
    if kind == "review-ledger":
        return review_ledger_instruction(subject)
    if kind == "proposal":
        return PROPOSAL_INSTRUCTION
    if kind == "design":
        return DESIGN_INSTRUCTION
    if kind == "implementation-plan":
        note = IMPLEMENTATION_PLAN_TREE_NOTE if "repository_tree_hash" in subject else ""
        return IMPLEMENTATION_PLAN_INSTRUCTION + note
    if kind == "change-set":
        if not has_packet_build_context(subject):
            if "anchored_base_hash" in subject:
                return anchored_subject_change_set_instruction(
                    subject["anchored_base_hash"],
                    subject.get("observed_product_identity", ""),
                )
            return CHANGE_SET_PACKETLESS_INSTRUCTION
        return CHANGE_SET_PACKET_INSTRUCTION
    return ""


@dataclass
class EnvEntry:
    kind: str
    id: str
    hash: str
    path: str


def materialized_entries(environment: dict, schema_version: int) -> list[EnvEntry]:
    if schema_version >= 2:
        raw = environment.get("entries") or []
    else:
        raw = (environment.get("decisions") or []) + (environment.get("policies") or [])
    return [EnvEntry(e.get("kind", ""), e["id"], e["hash"], e["path"]) for e in raw]


def render_prompt(
    manifest: dict,
    bundle_dir: str,
    work_dir: str,
    corrective: bytes,
    dispositions: list[str] | None,
) -> bytes:
    """Render the prompt projection for one attempt.

    dispositions: the attempt closure's source_map dispositions in order
    (environment entries first, then inputs) — the record of what the Go
    renderer actually inlined. None means inline everything (stdin mode).
    """
    schema_version = manifest.get("schema_version", 1)
    env_entries = materialized_entries(manifest.get("environment") or {}, schema_version)
    inputs = manifest.get("inputs") or []

    env_bodies = [
        open(os.path.join(bundle_dir, e.path), "rb").read() for e in env_entries
    ]
    input_bodies = [
        open(os.path.join(bundle_dir, i["path"]), "rb").read() for i in inputs
    ]

    n = len(env_entries) + len(inputs)
    if dispositions is None:
        inline = [True] * n
    else:
        if len(dispositions) != n:
            raise ValueError(
                f"source map has {len(dispositions)} entries, bundle has {n}"
            )
        inline = [d == "inline" for d in dispositions]

    b = bytearray()
    w = b.extend
    w(ONE_SHOT_PREAMBLE.encode())
    w(b"\n\n")
    run = manifest["run"]
    w(f"Pass: {run['pass_id']} (contract v{run['contract_version']})\n".encode())
    objective = manifest.get("objective") or {}
    w(f"Objective: {objective.get('summary', '')}\n".encode())
    subject = objective.get("subject") or {}
    for key in sorted(subject):
        w(f"  {key}: {subject[key]}\n".encode())
    w(b"\n")

    if env_entries:
        w(b"## Environment (the declared decision clauses and policies binding this run)\n\n")
        for i, entry in enumerate(env_entries):
            body = env_bodies[i]
            label = entry.id if schema_version < 2 else f"{entry.kind}:{entry.id}:{entry.hash}"
            if not inline[i]:
                w(
                    f"--- environment {label} — {len(body)} bytes, not inlined; "
                    f"materialized at {entry.path} (relative to your working directory): "
                    f"read it from there ---\n\n".encode()
                )
                continue
            w(f"--- environment {label} ---\n".encode())
            w(body)
            w(f"\n--- end environment {label} ---\n\n".encode())

    if inputs:
        w(b"## Pinned inputs\n\n")
        for i, inp in enumerate(inputs):
            identity = inp["identity"]
            if inline[len(env_entries) + i]:
                w(f"--- input {identity} ---\n".encode())
                w(input_bodies[i])
                w(f"\n--- end input {identity} ---\n\n".encode())
                continue
            w(
                f"--- input {identity} — {len(input_bodies[i])} bytes, not inlined; "
                f"materialized at {inp['path']} (relative to your working directory): "
                f"read it from there ---\n\n".encode()
            )

    w(b"## Required outputs\n\n")
    for expected in manifest.get("expected_outputs") or []:
        line = f"- outputs/{expected['output_id']} — artifact kind {go_quote(expected['kind'])}"
        w(line.encode())
        if expected.get("required"):
            w(b" (required)")
        w(b"\n")
        instruction = kind_instruction(expected["kind"], subject)
        if instruction:
            w(f"  {instruction}\n".encode())
    w(b"\n")
    w(OUTPUT_RULES.encode())
    if work_dir:
        w(
            f"\n\nYour working directory is {work_dir}. Every required output path above "
            f"is relative to exactly that directory (for example "
            f"{os.path.join(work_dir, 'outputs', '...')}).".encode()
        )
    if corrective:
        w(b"\n\n## Corrective note from the previous attempt\n\n")
        w(corrective)
        w(b"\n")
    return bytes(b)


def prompt_hash(prompt: bytes) -> str:
    return hashlib.sha256(prompt).hexdigest()


PROMPT_ARG_MAX_BYTES = 128 << 10


def render_with_spill(
    manifest: dict,
    bundle_dir: str,
    work_dir: str,
    corrective: bytes,
    prompt_mode: str,
) -> tuple[bytes, list[str]]:
    """Port of renderPrompt's inline selection + greedy argv spill loop
    (prompt.go:103-135), for records that carry no attempt closure. Returns
    (prompt, dispositions)."""
    schema_version = manifest.get("schema_version", 1)
    env_entries = materialized_entries(manifest.get("environment") or {}, schema_version)
    inputs = manifest.get("inputs") or []
    bodies = [
        open(os.path.join(bundle_dir, e.path), "rb").read() for e in env_entries
    ] + [open(os.path.join(bundle_dir, i["path"]), "rb").read() for i in inputs]

    inline = [prompt_mode == "stdin" or b"\x00" not in body for body in bodies]

    def rendered() -> bytes:
        return render_prompt(
            manifest, bundle_dir, work_dir, corrective,
            ["inline" if x else "path" for x in inline],
        )

    prompt = rendered()
    if prompt_mode == "arg":
        while len(prompt) >= PROMPT_ARG_MAX_BYTES:
            best = -1
            best_prompt = b""
            for i, is_inline in enumerate(inline):
                if not is_inline:
                    continue
                inline[i] = False
                candidate = rendered()
                inline[i] = True
                if len(candidate) >= len(prompt):
                    continue
                if best < 0 or len(candidate) < len(best_prompt):
                    best = i
                    best_prompt = candidate
            if best < 0:
                raise ValueError("argv-mode prompt cannot fit after context spill")
            inline[best] = False
            prompt = best_prompt
    return prompt, ["inline" if x else "path" for x in inline]
