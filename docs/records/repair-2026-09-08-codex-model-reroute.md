# Withhold configured-subject attribution after a Codex reroute

Date: 2026-09-08. Baseline: `3c41b1e`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Repair the explicit Codex model-reroute evidence path in
`src/caplab/codex_events.py`, `artifact_rater.py`, `ladder_subject.py`,
`review_dissent/native.py` and `revbench/codex.py`. Add focused synthetic tests,
a versioned contract, this record and a link from the native model-evidence
contract. Hash and inspect the retained public official source snapshot at
`/tmp/caplab-codex-final-event_processor_with_jsonl_output.rs`, pinned to
OpenAI Codex commit `3d2ee51ca2d5db578f328aa75e20aa22c0197c9a`; it is source
evidence, not historical native capture. Record a new synthetic before/after
counterexample and preservation checks under `/tmp/caplab-codex-reroute-*`.
Use pure parsers and new temporary test custody only. Run focused/full checks
and make a local commit; remove named doctrine scratch after consolidation.

Preserve native completion and final-file consistency as distinct observations:
a model reroute can complete and produce matching bytes, but must not supply
configured-subject attribution or a ratable native judgment. Keep existing
non-reroute behavior and historical evidence unchanged. Do not reopen the closed
ladder, reseal a frozen campaign, run native inference/version/auth, read native
homes or credentials, admit evidence, rank or place reviewers, write the tracker
or send external messages. Preserve policy, profiles, launchers, capture owners,
`docs/designs/`, worktrees and services. Retain logs/probes. Authorization expires
at commit. Stop if the format requires guessing model IDs from arbitrary prose,
if provenance requires historical capture reads, or if a frozen dependency
closure must be changed; scope any required new-fixture adjustment separately.

## Decision

The inspected native JSONL processor represents `ModelRerouted` as a completed
`error` item whose message starts with the exact native formatter prefix
`model rerouted: `. Existing attribution paths check top-level failures or
model fields and miss that marker. Add one shared envelope predicate and an
explicit attribution guard. Do not parse model names from this lossy formatted
string or search agent/tool text recursively. Keep raw reroute message, native
item ID and line in the model observation. Absence of this marker proves no
positive Codex model identity.

No change would preserve the reproduced attribution defect. Treating every
completed error item as a failed turn would also erase distinct completion
observations and reject unrelated warnings. The selected guard handles the
explicit native marker at attribution consumers and preserves those observations.

## Execution and verification

Added the shared predicate and stream guard, then applied them to artifact
rating, ladder classification, Revbench response derivation and Codex review
identity assessment. Review observations retain raw marker messages, item IDs
and one-based lines; they do not infer replacement model identities. The
[versioned contract](../product/contracts/codex-model-reroute-v1.md) specifies
consumer behavior and claim limits.

The official JSONL processor snapshot, pinned to the source commit above, has
SHA-256 `2f71fbf8a1b0a79bd342ed3c9caa414f1c5e06d9e52d6a94461799f304a9f255`.
Its `ServerNotification::ModelRerouted` branch emits the completed-error marker
and leaves Codex running. This is public source evidence, not a live native
reroute observation.

The before/after probe used the same marker in separate artifact-judgment and
Revbench response fixtures. The unchanged judgment stream has SHA-256
`725f44283bc955b35d5f8dac41524b80d3c36ec917cb9637372c6dce5b5b2523`.

| Observation | Before | After |
|---|---|---|
| Matching artifact judgment and sidecar | Judgment derived | `CalibrationError`: model reroute |
| Schema-valid Revbench response | Response derived | `CodexJSONLTransportError`: model reroute |
| Passing ladder pin, zero exit, task write | Behavioral attempt | Infrastructure disposition |
| Codex model assessment | Model-unverified, no explicit marker observation | Model-mismatch with raw reroute observation |
| Native completion and final-message bytes | Completed and matching | Completed and matching |

Ten new focused tests passed in 0.621 seconds. They cover the four consumers,
missing item IDs, repeated/raw markers, generic warnings and quoted markers,
non-ASCII final text, preserved Claude assessment, and a new retained-custody
fixture whose final-file agreement remains true alongside a reroute. Review
capture tests verify withheld score with unchanged assignment and execution
status. These are synthetic fixture outcomes, not study measurements.

`make check` completed with exit 0: **1,131 tests, four skipped, 157.889 seconds**.
AST comparison against `3c41b1e` preserves every existing top-level function/class
except the four authorized consumer functions. Thirteen protected files remain
byte-identical, including the capture owners, native policy, review continuation
and Revbench execution. The latter's existing transport-error handler withholds
the derived response, assigns infrastructure failure and stops the batch. The
review continuation gate already stops on any identity status other than
`native-model-match`; that handler was inspected, not changed.

Revbench inventories all CAPLAB package files when identifying its apparatus.
The new import therefore requires no frozen dependency-list adjustment or
campaign reseal. Existing source and apparatus tests passed. No native inference,
version probe, credential read, historical-evidence mutation or tracker write
was performed for this repair. Temporary test custody was removed by its owners;
the preserved `docs/designs/` directory remains outside this change.

Retained verification artifacts:

- `/tmp/caplab-codex-reroute-before.json` and `-after.json`: synthetic outcomes.
- `/tmp/caplab-codex-reroute-source-check.json`: definition and file preservation.
- `/tmp/caplab-codex-reroute-focused.log` and `-make-check.log`: terminal checks.
- `/tmp/caplab-codex-reroute-verification.json`: artifact hashes, doctrine and
  citation identities, check results, unmet obligations and exact scratch cleanup.

## Doctrine disposition

Validated release: `/home/halbritt/.local/share/pincite/release`, commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`. The initial packet discovered obligations; five
typed records and the completed full check supplied the bounded evidence.
Final packet: `pkt-e42442e710512ac8`, content SHA-256
`e42442e710512ac88876a380fc4d10f77df0222e2bfdc524bce1dfc121978f4c`.

Applied `universal-repository-contract-precedence` to the authorization boundary,
`universal-evidence-before-intervention` to the before/after counterexample,
`implementation-placement-by-ownership` to the shared native-envelope predicate,
and `universal-preserve-behavior-by-default` to completion and non-reroute behavior.
All four citations classified as valid packet citations. The generic routed
implementation label does not replace this record's semantic-repair classification.

Six missing obligations remain nonmaterial to this repair:

- `recurring change evidence when available`: a concrete attribution defect
  establishes the intervention pressure; no churn-based restructuring is proposed.
- `CI and build matrix` and `Python and dependency version matrix`: local Python
  3.12.3 and the repository's >=3.12 requirement were checked; no interpreter,
  dependency or cross-platform compatibility change is claimed.
- `formatter and static-tool configuration` and `formatter linter and type-checker
  configuration`: no such configuration is changed; the repository's existing
  test command and whitespace check passed. No new static-tool guarantee is claimed.
- `annotation maintenance cost`: no annotation migration or checker program is
  introduced; executable boundary checks determine the behavior.

Eleven named doctrine scratch files are removed after consolidation; logs,
counterexamples, source snapshot and verification manifest are retained. No
independent acceptance verdict, positive Codex model identity, live reroute
frequency or reviewer-selection accuracy is established. Authorization expires
at the local commit containing this record.
