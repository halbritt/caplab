# Finding: 36 of 71 control adjudications rest on the out-of-contract rule

- Date: 2026-09-06. Named by council plan `tree-v1` rev 2 §0.3; this record
  is the one §11 owes.

**Observation.** The adjudication ledger (`advisory/control-adjudications.jsonl`)
holds 71 records: 58 by mechanical oracle, 13 by human or Principal ruling.
Thirty-six of them (25 sound, 11 defective) are grounded, wholly or partly,
in the audit rule that an allegation depending on material outside the
artifact is out-of-contract — recorded, never scored. The mechanical checks
behind those records verify that the alleged text is present in the artifact
and then rule reference resolution out of scope.

**Inference.** That rule was correct for `iso-v1`, where no reviewer could
resolve a reference, so a refusal on resolvability told us about the
environment rather than the artifact. Under `tree-v1` reference resolution is
in-contract: a reviewer that resolves a reference against the pinned base and
finds it false is right, and one that refuses a reference the base resolves is
wrong. The 36 labels therefore describe controls under one environment and
cannot be carried into the next by assertion.

**What follows (plan §4).** Before any scored `tree-v1` run, every one of the
36 is re-derived with a resolution step against the exact base:
`resolved-valid` (label stands), `resolved-invalid` (control defective),
`evidence-unavailable` (case unscorable), `reference-unresolvable-anywhere`
(unscorable by default, flagged; never auto-sound, never auto-defective),
`reference-not-required` (label stands). Only labels that are formally
environment-invariant — mechanical in-set predicates such as the 41-hex
commit check or the anchor collision — carry forward without re-run. Human
and Principal rulings are re-examined case by case and re-affirmed or
re-ruled by the Principal. Missing custody never rewrites ground truth in
either direction.

**Consequence for published numbers.** Every `iso-v1` false-alarm rate of
2026-09-04/05 was computed over these labels. They stand as `iso-v1` claims
(content-hashed, preserved). Where §4 changes a denominator or a truth label,
a corrected `iso-v1` claim is re-emitted and labelled as corrected, and any
consumer that copied the original is named (plan §7).
