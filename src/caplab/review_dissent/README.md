# CAPLAB review-dissent instrument

This package owns the model-free qualification boundary for
`caplab-review-dissent-001`. The frozen manifest is
[`docs/product/studies/review-dissent-001/instrument.json`](../../../docs/product/studies/review-dissent-001/instrument.json).

`load_calibration_instrument` validates and loads only the development
artifact while exposing the held-out aggregate seal. It never opens held-out
content. `load_qualification_instrument` is the separate CAPLAB-12-only path
that validates both splits and the zero-call estimate. `render_review_cell`
creates one deterministic review image without an oracle. `grade_canned_review`
captures explicit synthetic outcomes, verifies target preservation, and keeps
infrastructure failures outside the harm score. `build_blinded_review_packet`
removes mechanical, treatment, subject, and provider identity from the still
empty human-review form.

`caplab.review_dissent.live` is the separate ADR 0038 execution boundary. It
loads development content through `load_calibration_instrument`, checks the
held-out aggregate seal without opening held-out content, enforces the frozen
two-subject order and budgets, and writes each launch, completion, provider
result binding, and artifact tree to append-only raw custody. It invokes one
sequential Harbor trial only through the explicit `run` command. A prior
attempt must have a sealed observation before another call is possible.

The live runner does not purchase provider credits, change billing, admit
evidence, export data, train a model, change Striatum policy, independently
verify a result, or accept a study. Canned captures remain qualification
fixtures rather than subject attempts or model evidence.

The separate `native` and `native_results` path retains the configured subject
seal and adds a raw-stdout-linked `model_identity` assessment in version 2
captures. Explicit fallback, mismatching model fields, and missing required
model evidence withhold the mechanical score, including refusal credit.
Execution status and assigned slots survive this identity exclusion; it does
not create replacement eligibility. Summaries count exclusions by configured
subject and cannot use an unattested score to declare calibration.

Claude initialization and all captured assistant model fields must agree in
a structurally bounded stream. Auxiliary usage-model names are recorded
separately. Codex stdout alone remains unverified; rollout integration is
still required. A matching assessment establishes only native-reported model
agreement, not full Binding identity, authenticated provider identity, or
capture completeness. Existing version 1 evidence is unchanged; this source
repair authorizes no historical normalization or new live campaign.

Exposed Claude partial-message model fields and structured fallback blocks or
usage iterations also participate in that check. The
[streaming evidence contract](../../../docs/product/contracts/native-stream-model-evidence-v1.md)
names the exact surfaces and their limits. Matching completed messages cannot
erase contradictory partial evidence; partial messages alone cannot establish
completion. No native launch flags or frozen bindings change through this repair.

Version 2 native observations retain the same model assessment before scoring.
Custody loading recomputes it from stdout and checks the recorded assignment
and lineage. Preparation reloads custody, rejects stale caller accounting,
and refuses another attempt after missing or mismatched model evidence.
This stop also prevents an infrastructure replacement while identity remains
unavailable. Matching model evidence preserves the existing replacement rule.

Read-only accounting retains all recorded attempts. `identity_stop` identifies
the first exclusion; `attempts_after_identity_stop` counts later recorded
attempts without authorizing them. `unattempted_primary_slots` counts assigned
slots with no primary attempt, including the remaining slots of a stopped
campaign. These fields do not redefine execution status or reviewer scores.
