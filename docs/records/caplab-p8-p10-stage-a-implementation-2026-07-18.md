---
id: caplab-p8-p10-stage-a-implementation-2026-07-18
artifact_type: implementation-record
assertion_type: observation
campaign: caplab-backlog-drain-stage-a
decision: adr-0016
implementation_commit: aafcbd5ebf53780720e8e5702c915dc034643a4a
implemented_at: 2026-07-18
status: complete
---

# CAPLAB P8 and P10 Stage A implementation

## Scope and authority

ADR 0016 authorized model-free implementation, tests, and documentation for
CAPLAB-26/P8 and CAPLAB-28/P10. Clean commit
`aafcbd5ebf53780720e8e5702c915dc034643a4a` implements those two deterministic
boundaries. It does not execute either checkpoint against live Study 001 data.
The P7 live continuation still awaits the repository owner's decision.

This work created no database row, object, evidence copy, credential, role
login, model call, human assertion, export, training action, verification
verdict, or acceptance record.

## Implemented behavior

The P8 package accepts the exact selected capability-card bytes, exact ADR 0006
bytes, and one content-addressed P7 observation. It emits a canonical
`caplab-capability-profile-proposal/1` document. The proposal binds the exact
Study 001 result, population, uncertainty, missingness, failures, and credible
rivals. Human inference and every broader claim remain unavailable.

The P10 package accepts the content-addressed P6 registration and its bound P7
observation. It checks all eleven global identity kinds, 20 relational chains,
sealed mechanical labels, verifier outcome coverage, and required
human-disposition lineage. All candidates share one checkout-retries split
group. Candidate status is `derived-not-eligible`; leakage review, eligibility,
export, model use, and training remain unavailable.

Both packages expose file-input, canonical-standard-output CLIs. A mismatch
produces one typed canonical error on standard error and exit status 2. Neither
package has a persistence or network adapter.

## Verification observations

At the clean implementation commit:

- `make check` passed 102 tests; four pre-existing environment-gated
  integrations were skipped;
- `ruff check .` passed;
- `git diff --check` passed; and
- the worktree was clean.

The new tests cover deterministic replay, exact card and decision identities,
changed Study 001 results, promoted upstream claims, exact candidate lineage,
verifier-outcome substitution, missing human lineage, one-family grouping, and
the absence of broader CLI effects. These are implementation tests, not an
independent CAPLAB-33 verdict.

## Doctrine provenance and remaining gates

The final evidenced doctrine packet is `pkt-79437112054f13c0`, content SHA-256
`79437112054f13c044b2dc79705f8ce186eea71c261c210cba080f804f236275`.
It used corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-a90ee3f1cf7b6f26`, and retriever
`retriever-1392f38f05a41086`. All 64 activated evidence obligations were
satisfied. Its authority ceiling is execution without self-acceptance.

No packet obligation remains material to the Stage A implementation. The
separate product gates remain: P7 must be explicitly authorized, executed, and
verified before its observation exists; P8 and P10 must then run against that
observation; P9 and P11 require named human decisions; P12 requires a separate
export authorization; and P13 and P14 remain independent verification and
owner acceptance.
