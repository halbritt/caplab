---
id: caplab-7-native-preference-instrument-2026-07-20
artifact_type: implementation-record
title: CAPLAB-7 native preference instrument correction
status: model-free-qualified
authority: adr-0040
created: 2026-07-20
---

# CAPLAB-7 native preference instrument correction

CAPLAB-7 now has a separate native-system instrument. It imports only the
subject instruction and six task contracts from the preserved proxy-era
instrument; the loader removes its harness, subjects, order, reveal map, and
budget fields before returning the task bank.

The new instrument binds the Striatum-compatible `claude-fable-5-max` and
`codex-terra-max` commands, new order and reveal identities, zero-call budget,
and native capture requirements. Its renderer seals each fresh task to design
SHA-256
`a66911de20af5ebfbcfdd8ffecbd19f5bf8b5cb2a757083c1e42df4b22eeaef0`
rather than the withdrawn Terminus instrument.

Tests cover native tuple loading, task-only projection, corrected render
identity, native command construction, balanced slot identity, and rejection
of a resealed Terminus substitution. The complete repository gate passed: 186
tests, with four live integration tests skipped by their standing environment
gates. No model, provider, or live harness call occurred.
