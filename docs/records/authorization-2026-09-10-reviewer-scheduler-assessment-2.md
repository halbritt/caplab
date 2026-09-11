# Authorize a separate scheduler assessment after binary preflight refusal

Under ADR 0026, the primary agent authorizes one new preparation and one
native assessment at `development/scheduler-assessment-2`. The first
preparation remains unchanged: its credential guard stopped on
`task/source/base/target-hash` before a namespace or model launch. Its native
allowance is closed; no retry in that custody root is authorized.

The file is a tracked 3,606,438-byte Go ELF executable, not a textual hash.
The base and repair copies are byte-identical, SHA-256
`4baa1e80d46bc620f4bb9c7c501bb8b12731d13d929616ddf0ef2b7100867e46`.
They are the only non-UTF-8 files in the frozen task. The assessed patch does
not change this binary, and the assessment permits reading only. Preserve
both originals in the new private custody outside the task mount, along with
their original commit, path, Git blob and content hash. Expose an explicit
omitted-artifact inventory instead. This is an administration change; it is
not evidence that the guard is wrong or permission to weaken it.

Permit exact copies of all task files and provenance from the first
preparation, fixture SHA-256
`c5435dd6231b6f014ddedfa1a0f5bdfb0c3e699eae57d6b6d483e5aef8b6fe0e`.
Only the two unchanged executable copies are excluded from the assessor
mount. Correct the evidence inventory's complete-regular-file wording and
add the explicit omission metadata. Keep all source text, changed files,
original observations and methods, the six reports, semantic expectations,
schema and prompt byte-identical. Verify the exact task delta and preserve
the failed preparation and its records. There was no assessor output to
inspect or use to revise expectations.

Reuse the first preparation's expiry-only derived executor unchanged,
with a separately frozen wrapper and new task inventory. All native identity,
600-second limit, one-launch bound, credential, containment, capture,
cleanup and stop conditions in the first authorization apply. Authorize one
Codex CLI 0.153.4 / gpt-5.6-terra / max invocation and its ten-second namespace
version preflight, with no retries or substitutions. The allowance expires
on consumption or 2026-09-11T04:00:00Z.

Assess the original six semantic contrasts separately from representation.
No old experiment is rescored. No scorer acceptance, corpus admission,
held-out measurement, reviewer ranking or qualification is authorized.
