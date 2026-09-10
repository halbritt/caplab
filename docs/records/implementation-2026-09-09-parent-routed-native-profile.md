# Adopt parent-owned routing in a distinct native diagnostic profile

Baseline `cc798af3cfc13e6e20728462a31a2e626509c635`. The preceding routing
integration passed 1,479 tests with four existing skips, including real nested
sandbox and restricted TCP controls. Actual routed native attempt 2 remains a
preserved UID-map failure. The current native profile still maps the workload
to root in the network-owning user namespace.

Under the continuing owner goal and ADR 0026, select a distinct
`codex-scripted-routed/v2` launch profile and
`caplab.scripted-native-preparation/v4`. Authorize implementation in the native
launch configuration builder, scripted diagnostic preparation, bootstrap,
runner, outer routing, inspection and CLI, shared custody inspection, and
focused tests. Add this record and a versioned contract. The new preparation
must bind exactly the new profile; old profiles and preparation formats retain
their behavior. Keep implementation/runtime/input pins, one-shot authorization
and consumption, native identity/trace/frozen-child checks, quarantine,
destination rules, resource and stream ceilings, workload cleanup and all
prior custody intact.

The selected trusted bootstrap creates one child user namespace in process,
after raising loopback and before dropping capabilities. It denies setgroups,
maps internal UID/GID 1000 singly to parent zero, clears all five capability
sets and sets no-new-privs before mount handoff. The trusted initial Bubblewrap
setup may request CAP_SETFCAP for this mapping; this capability must not remain
in the workload. Existing routing helpers enter the checked network owner using
`parent-user/v1`. Retained native inspection must derive that selection from
the anchored preparation and require the new routing records through the
existing authenticated handoff and terminal manifest.

Authorize fresh synthetic controls and tests under `/tmp/caplab-parent-native-*`
and temporary roots, followed by full checks and a verified commit/push. This
record does not authorize an installed native launch, model/provider call,
spending, real authentication, historical custody effects, tracker writes,
messages, scoring or study execution. A fresh exact native preparation and
separate one-attempt authorization follow verified implementation. Preserve
unrelated `docs/designs/`. Stop on identity, mapping, source or privilege
disagreement; quarantine refusal; or incomplete owned cleanup. Do not retry any
prior attempt. This implementation authority expires at its commit.

## Implementation and synthetic verification

Added the trusted `scripts/scripted_native/workload_identity.py` setup function.
It requires mapped root, creates one child user namespace, denies setgroups,
writes the selected mappings and requires resulting UID/GID 1000. The bootstrap
calls it only for the explicit sealed parent selection, then performs the
existing routed capability drop and no-new-privs checks. The runner mounts that
source read-only only for v2 and requests CAP_SETFCAP only during its initial
setup. Source preparation includes the new module in the existing implementation
pin inventory.

Preparation v4 binds routed/v2 exactly; v3 still binds routed/v1. The native
launch configuration names a distinct profile identity while retaining the same
fixed fixture command and endpoint settings. Runner and outer-worker selection
cover both routed profiles. V2 alone selects `parent-user/v1` for routing. Native
inspection derives that profile from preparation and carries it through shared
custody inspection, preserving the existing independent handoff and terminal
anchors. Existing profiles, limits, helpers and one-shot consumption semantics
remain. See the new [contract](../product/contracts/scripted-native-routed-v2.md).

The new preparation test first failed with `unsupported scripted launch profile`
in `/tmp/caplab-parent-native-preparation-red.log`. After implementing the new
profile, 24 preparation/launch tests passed in 1.837 seconds. The first expanded
28-test run had one pre-handoff timeout in the new routing test. Its test setup
tried to import the new module from a repository path absent from the minimal
inner fixture. The corrected fixture executes the module's exact source bytes,
with the same capability-drop setup used by the existing kernel controls. The
failure log remains `/tmp/caplab-parent-native-focused.log`; the corrected run
passed all 28 tests in 3.709 seconds in
`/tmp/caplab-parent-native-focused-corrected.log`.

The added tests cover v4/preparation profile relabeling, distinct launch hash
and trace inspection, and actual production setup followed by nested Bubblewrap
and restricted access to the supervised fixture. Existing local/routed v1 tests
are retained. No installed Codex executable was launched by these controls.

A fresh retained control is at
`/tmp/caplab-parent-native-retained-control/capture/run`. The parent directory
holds its exact command and thirteen changed Python source pins. The test used
the production outer namespace, task-input preparation, supervised fixture,
new workload setup source, parent routing and retained inspector. Its result
is `verified-observation` with identity SHA-256
`97f3f78a497bf8523f4171f93b7799741f037c383f8bf621822f9e35ea0aa217`.
The control rechecked its source pins and parent namespace identities after
normal cleanup. Full routing, handoff, task and process custody is retained;
this is a synthetic setup observation, not an installed-native attempt.

## Advisory basis and limits

The validated Pincite release/gate is unchanged from the preceding routing
integration: release `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
The initial packet is `pkt-c1eca2ce18643219`. Four typed evidence records produced
packet `pkt-63fa9d0862774e2d`, content SHA-256
`63fa9d0862774e2d662e858ad27ca5b2efe71c7466f2f13a14a55be1879f2c5a`.
Packets, renders, evidence, validated decision receipt and both served-packet
citation classifications are retained under `/tmp/caplab-parent-native-*`.

Used concepts are `python-structured-cleanup`, `domain-identity-entity`,
`universal-preserve-behavior-by-default`,
`universal-repository-contract-precedence`,
`agent-conduct-authority-bounded-action` and
`universal-evidence-before-intervention`. Identity guidance applies to the
existing Binding/profile distinction; no new entity model is introduced.
Repository locators remain foreign citations. No material advisory obligation
remains for this implementation and synthetic-control claim. Nine nonmaterial
obligations remain individually classified in
`/tmp/caplab-parent-native-obligations.json`: five concern investment in a deep
domain-modeling campaign that this change does not undertake, and four concern
CI/version matrices or toolchain-policy conformance that it does not claim.

Leaving the original mapped-root profile as the only option preserves the
observed native failure. Altering v1 in place obscures the runtime identity of
prior preparations. The distinct profile preserves those boundaries while
using already verified routing behavior. Reopen on an installed-native failure,
identity/privilege/source disagreement, or existing-profile/lifecycle drift.
Full installed-native v2 verification, representative repairs and observer-cost
measurements remain material next work. This record grants no independent
acceptance or capability claim.

## Final checks and custody

The full `make check` run, with the pinned WebSocket test dependency enabled,
passed 1482 tests in 230.186 seconds with 4 existing skips. The skips require
the separately authorized P4 live campaign or a PostgreSQL integration DSN;
those environments are not verified by this run. The full log is
`/tmp/caplab-parent-native-full-suite.log`. Scoped Ruff formatting and F checks
and `git diff --check` passed. No Python source changed after the retained
control/full-suite sources were pinned.

All 72 private artifacts in the preceding parent-routing verification manifest
and all 197 private artifacts in the second native-attempt manifest were
rehashed unchanged; see `/tmp/caplab-parent-native-preservation.json`.
The new verification manifest is `/tmp/caplab-parent-native-verification.json`,
SHA-256 `74ce3841cea5b1f2682e44edc8140fe14647ec4c6a78b90d4b41c43428cdb30f`, with 92 private
artifacts and 14 source/contract pins. The final record is committed separately
to avoid a self-referential hash.
