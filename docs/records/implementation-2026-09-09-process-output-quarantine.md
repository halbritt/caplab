# Quarantine known secrets before prospective process capture writes

Baseline: `f1d0253`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md) and the
continuing CAPLAB improvement request.

## Decision and authorization

The new process recorder writes stdout/stderr directly to durable capture.
Its recently added input-descriptor path deliberately performs no credential
handling. The existing Revbench credential owner supplies a cross-chunk exact
secret gate, but the prospective recorder cannot use it. Synthetic HTTP auth
probes establish transport/error behavior, not safe real-credential capture.

Authorize an optional `quarantine_factory` seam on
`src/caplab/process_capture.py`, its contract, focused real-process tests and
this record. Reuse the existing Revbench gate in tests; do not move, rewrite or
loosen the legacy credential adapter. A small structural protocol describes
feed/finish/abandon and a quarantined flag without importing the native provider
adapter into the generic process owner. The factory creates two distinct owned
stream gates before custody/launch. The caller supplies a trusted factory and
bounds its private data and buffering; a type annotation is not security proof.

Successful guarded capture must preserve exact original bytes, counts and
hashes. Count the byte allowance against received bytes, including withheld
overlap; buffering cannot extend the stream allowance. Flush a gate only on
observed EOF. On a matched secret or incomplete guarded capture, terminate/reap
the child group, abandon withheld data and propagate a fixed nonsecret error
without publishing a final receipt. Retain already-written safe prefixes in
restricted custody. Default unguarded behavior and v1 receipt schema remain
unchanged. No automatic retry, redacted-success fallback or transformed raw
capture is permitted. Check raw/emitted equality before successful publication.

Preserve explicit argv/env snapshots, descriptor borrowing, timeout and quota
semantics, exclusive private custody, cleanup, source identities and historical
records. No authentication-administration adoption, actual credential read,
native/model/provider execution, tracker mutation, historical evidence import,
message, push or other worktree/service change. Preserve `docs/designs/`.
Authorize fabricated input/output fixtures, local focused and full tests and
private advisory/verification artifacts under `/tmp/caplab-output-quarantine-*`.
Commit only the bounded source/tests/contract/record change after verification;
authorization expires at commit.

This is an infrastructure prerequisite for CAPLAB-80/84, not their completion.
Known-value quarantine cannot detect transformed, encoded or cross-stream
fragmented secrets, unknown personal data, persisted native files or task
artifacts. The broader capture adapter still needs credential and full-surface
privacy decisions. No all-surface protection or authentication readiness claim
is selected.

## Alternatives and verification plan

Leaving the recorder unchanged preserves an explicit gap before authenticated
capture. Copying the matching algorithm creates two implementations of private
stream policy; importing the entire native adapter into the generic recorder
reverses the desired dependency. The selected factory lets the credential owner
retain policy while the recorder owns reads, writes, limits and cleanup.

Verify actual child leakage is stopped before a secret reaches any durable
capture file, including a secret split across reads; exact safe output survives
withheld overlap and EOF; stdout/stderr have separate gates; timeout and quota
fail closed without flushing an incomplete overlap; factories/invalid/shared
gates fail before launch; exceptions terminate/reap the actual child; unchanged
callers and full suite pass. A complete guarded receipt must also reject a gate
that silently transforms, drops or reorders safe bytes. These are synthetic
mechanism checks, not independent privacy acceptance or a native trial.


The abstraction pressure is policy/mechanism separation between the existing
credential gate and the newer recorder. The shared invariant is exact safe byte
preservation with withholding until a possible secret prefix is resolved; the
credential owner knows private values, while each recorder knows its sinks and
process lifetime. One explicit factory adds four protocol operations and no
provider imports, policy registry or new matching implementation. Revisit the
seam if the selected native adapter does not use an exact-value gate or needs
incompatible semantics; it is not a general-purpose transformation plugin.
Legacy matching and exception behavior remain untouched.

The first focused test failed on the absent factory argument before any child
launch. Prior tests directly exercise the existing quarantine's cross-chunk,
binary/nested-scalar and EOF behavior; new recorder integration must still pass
actual-process leakage, safe-output, limit and cleanup checks before completion.
No current real credential leak is asserted from this synthetic baseline.


## Implementation and focused verification

The recorder now accepts the trusted optional factory and owns its two gates
through an ExitStack. It validates distinct identity, methods and initial flag
before custody creation. Any callable cleanup on a returned rejected object
is adopted before rejection, without cleaning a duplicate object twice.
Gate cleanup runs on setup and process errors and before receipt publication.
The old Revbench matcher, credential parser and public adapter are unchanged.

Incoming and emitted bytes have separate counters and digests. The shared
allowance counts received bytes even when a gate withholds them. EOF releases
pending safe bytes; timeout/quota stops abandon them and raise a fixed error.
Secret/invalid-state, transformed output and cleanup errors produce no final
receipt. Successful guarded output must match the original per-stream lengths
and SHA-256 and uses the original v1 receipt shape. Factory construction occurs
before the existing capture deadline; the caller must bound it and its state.
No provider module, generic transformation registry or matching algorithm was
added to the recorder.

Twelve new tests use real Python child processes and the existing exact-secret
gate. A fabricated secret longer than the maximum read buffer exercises a
mandatory cross-read split; no full secret reaches any durable capture file,
and the live child is killed/reaped with both pipes closed. Other checks cover
stderr, safe binary/non-ASCII EOF output at the exact combined quota, nonzero
native exit with complete output, pending-overlap abandonment on timeout and
quota, invalid/shared factories, factory and rejected-gate cleanup, transformation,
output expansion, invalid runtime flag, cleanup-publication ordering, and actual
child cleanup through feed/storage errors.

The first test failed on the absent factory argument. Three subsequent
regressions were observed before their repairs: a transforming gate could
publish changed bytes, a non-boolean false-like flag passed output, and a
rejected gate's cleanup was omitted. Each has a retained failing log under
`/tmp/caplab-output-quarantine-`; all focused tests then passed. The final
focused run completed 38 tests in 2.205 seconds. These include the 26 existing
process/descriptor tests and twelve new cases. Fabricated values are the only
secret inputs used. No native harness or provider was invoked.

A fresh Plane read at baseline retained 12 open roadmap items, with CAPLAB-84
In Progress and CAPLAB-80/85 Ready. Snapshot paths are
`/tmp/caplab-roadmap-20260909-f1d0253.json` and
`/tmp/caplab-roadmap-states-20260909-f1d0253.json`. No tracker state changed.
This opt-in API has no active campaign consumer in this change; an adopting
native adapter must freeze the factory/policy and handle missing receipts.
The component receipt deliberately does not claim that a gate was selected.
Known-secret protection is limited to the supplied trusted policy on two
streams; persisted files, transformed leakage and full-surface privacy still
need separate work. No representative measurement or roadmap completion follows.

## Advisory and review

Pincite's validated release gate passed with source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9` and retriever
`retriever-ec995ecdd083b2c8`. Initial packet `pkt-a8f5b8debbccccaf`
preceded two bounded evidence passes: the first covered authority, contracts,
existing source and test assertions; the second covered actual new source and
completed focused integration tests. Final packet `pkt-6484e991fb9bbe62` has
content SHA-256 `6484e991fb9bbe62414ee5f355e80e634c5536ce23e193c4c2f6751221c235b2`. The Markdown packets were read.

The six remaining obligations are individually retained as nonmaterial
language/toolchain matrices and configurations: no Python/dependency migration,
new checker or repository-wide idiom choice is proposed. Current Makefile,
adjacent code and existing APIs were inspected, and the repository's checks
remain required. The non-ASCII obligation was discharged by the binary/UTF-8
round-trip test rather than waived at completion.

Used concepts are `python-structured-cleanup`, `python-mutable-ownership`,
`universal-earned-abstraction`, `universal-repository-contract-precedence`,
`universal-preserve-behavior-by-default` and `universal-evidence-before-intervention`.
They support owned gate cleanup, distinct state, the policy/mechanism seam,
protected legacy behavior and actual failure evidence. The AI failure-mode
review checked propagation rather than fallback success, actual subprocess
execution, runtime protocol checks, output-limit accounting and no duplicated
matcher/provider import. Verification is local engineering evidence, not an
independent privacy judgment or acceptance of a native study.


## Final verification

`make check` passed all 1,264 tests in 152.974 seconds, with four skips. Its log
is `/tmp/caplab-output-quarantine-make-check.log`. Ruff's undefined-name/unused-
import check passed for the changed runtime and new tests. No runtime logic
changed after that full-suite run. Local links and whitespace checks passed.
Only the recorder, its contract, twelve tests and this record changed.

Pincite release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f` was rechecked;
all six selected concepts classified as valid packet citations. The runtime
change is verified for the stated synthetic cases, with no new native or
provider execution and no broader privacy/capability acceptance.

Private manifest `/tmp/caplab-output-quarantine-verification.json`, SHA-256
`3ecf296bc94b1012e7435291bc596a5556f5738cbdf19e5cf416785bb1c3a13e`, retains 23 artifact
identities and final runtime/test/contract hashes. Fourteen advisory scratch
files were embedded byte-for-byte, checked and removed. Failure and passing
test logs, the initial decision scope and roadmap snapshots remain available.
