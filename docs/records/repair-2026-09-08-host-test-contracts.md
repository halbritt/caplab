# Align host tests with the retained contracts

Date: 2026-09-08. Execution and verification under the repository owner's
active improvement goal. No live model calls or bundle-policy changes.

The full check after the
[gate accounting repair](repair-2026-09-08-review-gate-accounting.md) exposed
two obsolete test expectations:

- `test_repository_contract` required `.github/workflows/check.yml`.
  Commit `63e9beb2b7dabc05164db27dcacb3d33f8aa5802` removed that workflow
  under the Principal's 2026-08-23 decision to run checks on the host. The
  replacement test checks the README's host instructions: install the
  hash-pinned runtime and test dependencies before `make check`.
- `test_revbench_codex` checked only whether a file existed at the Codex
  installation path, then expected the frozen bundle to accept its bytes.
  The installed executable now has SHA-256
  `56ef98ab4032d317ab26e9b5e5a175650717351edb16ed9cde0cb6d1734d62da`
  and size 258,659,424 bytes. The retained policy requires
  `cb0a15567e9a60a5820d54b0f6ae86d504dc3805c1eab21a47f70e3eb7b73a40`
  and 258,278,208 bytes. The runtime correctly refused preparation.

The host-binary test now requires that refusal when the installed identity
differs. It keeps the acceptance assertions for a matching installed binary.
Its passing result on this host verifies rejection of drift, not availability
of the original live bundle. The runtime validation, policy hashes, harness
version, and subject tuple remain unchanged. No extra test is skipped.

Both corrected tests passed in a focused run. The zero-call CLI plan still
reports 16 analog cells, three control attempts and one mutant per cell,
three natural-case attempts, and a maximum of 67 calls if a run is separately
authorized. The floors remain proposed and unadopted.

Final `make check`: **695 tests, four skips, no failures or errors**, in
144.518 seconds. The four existing skips cover the authorization-gated P4
campaign and three PostgreSQL integration tests without a configured test
database. They are not verified by this run. The local log is
`/tmp/caplab-gate-make-check-final.log`; `git diff --check` also passed.
