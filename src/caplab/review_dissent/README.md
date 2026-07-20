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

There is no subject runner, provider adapter, credential access, network call,
subprocess, inference path, or human-adjudication implementation in this
package. Canned captures prove instrument behavior; they are not subject
attempts, study results, or evidence about an agent configuration.
