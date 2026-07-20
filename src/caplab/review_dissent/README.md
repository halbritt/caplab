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
