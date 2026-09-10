# Claim-interpretation development result

The native interpreter preserved the intended positive claims, uncertainty,
retractions, unknown findings and cited locations in the 18-document challenge
set. Four documents also acquired an inferred rejection of an opposing
hypothesis. Consequently, **14 of 18 documents match the frozen mappings
exactly**, and the all-document criterion was not met. This is a mismatch in
how the protocol represents assertions and their logical consequences; it is
not a defensible estimate of semantic accuracy or reviewer quality.

The experiment completed in 194.44 seconds with Codex CLI 0.153.4, reported
model `gpt-5.6-terra`, effort `max`. All 76 captured files were retained and
their hashes rechecked. The final file equals the last completed native agent
message byte-for-byte. No reviewer score or ranking was produced.

## What was tested

The [authorization](authorization-2026-09-10-reviewer-claim-interpretation.md)
permits one development invocation on the prior native review plus 17 newly
authored variants. The interpreter received review text, ten neutral
hypotheses and a requested output shape. It did not receive empirical defect
labels, expected mappings, original source trees or the hidden witnesses.

The hypotheses include observations, expectations and opposing descriptions.
They are statements to attribute, not an answer key about which code is
defective. An asserted but factually false effort-expansion claim must still
be extracted as asserted. Its empirical falsity belongs in a later evidence
assessment. Unknown findings must survive without being forced into the
known-hypothesis list. This separation is necessary for new valid findings
outside an initial answer key.

Expected mappings, inputs and prompt were frozen before execution. The
primary agent authored those expectations after inspecting the source review;
they are calibration judgments, not independent empirical truth. Synthetic
review variants test this interpreter, not the reviewers' ability to discover
defects in real code. The cases are development-exposed and cannot become a
held-out semantic evaluation.

## What the mismatches mean

| Document | Expected reported stance | Additional interpreter stance |
| --- | --- | --- |
| Timeout paraphrase | Timer ends at headers: asserted | Timeout covers body: rejected |
| Same claim with a wrong code location | Timer ends at headers: asserted | Timeout covers body: rejected |
| Duplicate release-loss report | Release is lost: asserted, once | Current release is preserved: rejected |
| Effort preservation control | Accepted inputs preserved: asserted | Accepted inputs expanded: rejected |

Each addition is an inferred opposing stance. The quote can support that
inference, but the author did not separately report the opposing hypothesis
as a rejected finding. The prompt prohibited absent hypotheses and stronger
claims without explicitly distinguishing reported stance from logical
consequence. Preserve the frozen mismatch rather than changing the expected
answers after seeing the output. The next protocol must name that distinction
and test it prospectively. Inferred consequences must not become extra
findings, extra catches or independently refuted reports.

All document IDs, unknown-claim presence and code locations matched. In the
wrong-location case, the interpreter retained `src/config.ts:7`; it did not
silently repair the location using knowledge of the likely defect. Keyword
lists, a suggestion to audit code and an embedded instruction attack produced
no mapped assertions. The two unknown-behavior cases remained unmapped claims.

For the actual native review, the interpreter retained three assertions:
the empty-seed/small-bound failure, the expectation about credential-scope
checks, and the scan-bound-to-conflict error conversion. It did not attribute
the stronger claim that all Council-home inode protection should be skipped.
That distinction also constrains CAPLAB's own interpretation: a requirement
to protect Council-home inodes does not, by itself, refute the reviewer's
narrower complaint about a misleading credential-conflict diagnosis. The
whole finding's actionability and severity remain separate, unresolved
assessments; this experiment does not settle them.

## Verification and remaining limits

The native subject's only recorded shell command read the complete
`/task/inputs.json`. Its model, effort and thread identity agree between the
root rollout and stream. The native vendor package and original authentication
cache remained unchanged. The recorded usage is 26,118 input tokens,
including 13,824 cached input tokens, and 10,529 output tokens, including
8,863 reasoning output tokens. This is native-reported usage, not a cost
estimate or a measure of task difficulty. The tool audit is not a complete
kernel network/process trace.

Six new checker tests cover lost uncertainty, dropped unknown findings,
duplicate or missing documents, repeated hypotheses, fabricated quotations,
changed locations and duplicate JSON keys. All 20 focused reviewer-development
tests pass, including the existing population, selection and timeout-witness
checks.

One test deliberately exposes a remaining limit: an exact quote as short as
`At` can satisfy the literal quotation check while failing to support the
mapped claim. Literal containment proves attribution of bytes, not semantic
support. The authored mappings assess selected semantic interpretations;
they do not make that quotation check sufficient for arbitrary new reviews.
No autonomous defect score may rely on this check alone.

The candidate therefore remains unaccepted as a production interpreter or
scorer. Required next evidence includes an explicit treatment of reported
versus inferred stance, semantic support checks, prospective challenges with
unseen natural reviews, and mapping to independent behavior, requirement and
change-attribution evidence. Reproducing a failure still does not prove the
reviewer's requirement interpretation, severity or whole-patch correctness.

## Custody and doctrine

Private root:
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/claim-interpretation-1`.

- `fixture-plan.json`: SHA-256
  `628edd4f32e27720e2255411bdd9d84d1ccd2027c51c4d1c3f316643fdff7b14`.
- `verification.json`: SHA-256
  `0680d6e3f398bc9c62c1129aec28393bb6d5550f697794ca3cb71d5fd97ae80f`.
- `administration-check.json`: SHA-256
  `af1e7d8e47d4c1b91ba3f76daac93c73a592847ae185bbd3c2cfc6749abe50c4`.

The root retains the frozen generator, expected mappings outside the task
mount, runner, native plan, process records, complete guarded capture and
verification. The prior final was copied only after checking its existing
completed-output receipt. Neither the historical output nor its custody was
rewritten or admitted as comparative evidence.

Pincite retrieval passed its release-state gate at release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`, retriever
`retriever-ec995ecdd083b2c8`. Evidence-backed packet
`pkt-cdafd666a23adaf1`, SHA-256
`cdafd666a23adaf11c8cbf433cdcf433f7cb25d0fcbf311e13a42e1ebcc3e945`, is retained
under `/tmp/caplab-finding-assessment-doctrine-evidenced.json`. Applied repository
precedence, evidence before intervention and measurement on the claimed
dimension. Generic deployment health, architecture restructuring and public
API compatibility obligations are nonmaterial to this isolated development
experiment. Broad semantic validity and scoring validity remain material and
unmet; the evidence supports continued investigation, not acceptance.
