---
id: caplab-13-development-calibration-implementation-2026-07-20
artifact_type: implementation-record
title: CAPLAB-13 development calibration implementation checkpoint
status: blocked-before-first-call
authority: adr-0038
created: 2026-07-20
---

# CAPLAB-13 development calibration implementation checkpoint

## Implemented

The committed live boundary validates the exact ADR 0038 manifest, loads only
the eight development cells, and compares the already-frozen held-out
aggregate seal without opening `heldout.json`. It freezes 16 ordered primary
slots across the two exact subject routes, at most four infrastructure-only
replacements, and the trial, token, time, and USD ceilings.

The runner verifies Harbor, Terminus source, Docker, provider identities and
prices, and credential presence without printing the credential. It renders
one neutral development cell, seals the exact command and input tree before
the call, captures Harbor output privately, and requires a sealed explicit
observation before another call. Campaign accounting is derived only from raw
custody. Zero-token rejected provider requests may record zero cost; other
missing metrics stop.

## Verification

Focused tests cover:

- development-only loading while a guarded `Path.read_bytes` refuses any
  `heldout.json` access;
- exact command and provider-default reasoning without an invalid literal
  override;
- frozen-order accounting and infrastructure-only replacement;
- one-cell rendering and pre-call launch custody; and
- zero-token provider-rejection accounting.

The live validation and infrastructure preflight passed on 2026-07-20 with
Harbor `0.18.0`, Terminus source SHA-256
`c6b72b8c6289809b2ff3a3009b8f118fa1edb1da205f48d0b56c6938a49cb12f`,
Docker server `29.6.1`, both exact provider catalog rows and prices, and the
credential present but unread.

## Execution state

No CAPLAB-13 provider call has occurred. CAPLAB-8 established the current
external provider state immediately before this implementation: an OpenRouter
request stopped with HTTP 402 because the account balance could not reserve
the frozen 1,024 completion tokens. The API key's separate weekly guardrail
still had USD 49.767989625 remaining, so changing that guardrail would not
repair the unfunded account balance.

ADR 0038 excludes credit purchase, payment-method use, and billing mutation.
The exact CAPLAB-13 first call therefore remains stopped. This checkpoint is
implementation and preflight evidence, not trial execution, calibration
evidence, independent verification, inference, or acceptance.
