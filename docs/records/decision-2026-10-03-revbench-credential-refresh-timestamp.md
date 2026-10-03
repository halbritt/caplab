---
artifact_type: decision-record
status: selected
decision_owner: root252-primary-agent
decision_authority: adr-0026-and-repository-owner-compatibility-repair-task-2026-10-03
implementer: agent-256
created: 2026-10-03
affected_contexts:
  - caplab-revbench
---

# Native credential refresh timestamp compatibility

## Authority and reopening

Root252, acting as the primary agent under active
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md) and the
current repository-owner implementation mandate, selects this bounded
administration change. Agent-256 implements it for independent Sonnet review.

The whole-read
[September 8 characterization](verification-2026-09-08-native-codex-auth-format.md)
explicitly required a new administration decision before changing the old
Revbench guard. That record remains unchanged. Its offline synthetic Codex
0.153.4 status results are compatibility evidence, not provider authentication
or proof about the older Codex 0.147.0 subject. This decision reopens only
refresh-metadata parsing in that subject's credential administration; it does
not reopen expiry, identity, private-claim or native-execution policy.

Baseline main is `d5a5f6b19a27c2c728440fdafb443a52e7939d48`.
The separate catalog-preparation candidate remains pinned at
`af6261218b41b74864f2a0a8fa979ebb84fc3030`; neither its source nor frozen
preparation/evidence inputs are edited by this repair.

## Selected behavior

`caplab.revbench.codex.credential_memfd()` accepts `last_refresh` as a valid
calendar timestamp with this exact ASCII shape:

```text
YYYY-MM-DDTHH:MM:SSZ
YYYY-MM-DDTHH:MM:SS.<1 through 9 decimal digits>Z
```

Fields must be zero-padded, with uppercase `T` and `Z`. A fraction is optional;
empty fractions, more than nine digits, offsets (including `+00:00`), whitespace,
non-ASCII digits, impossible dates and seconds outside 0–59 are refused with
`credential_last_refresh_invalid`. Calendar validity is checked independently
of the fraction. No timestamp normalization, truncation of delivered metadata,
rounding, credential refresh, or source write occurs. The sealed anonymous copy
retains the exact original document bytes and the entire supplied refresh
string remains a secret-quarantine marker.

This matches the refresh grammar already documented for the separate
[external-token credential API](../product/contracts/codex-external-credential-v1.md).
It does not import that API's different expiry policy into Revbench.

## Preservation and limits

Preserve the native subject: Codex CLI 0.147.0, GPT-5.6 Terra, maximum effort,
`chatgpt` credential method, pinned native bundle and configured provider route.
All closed document/token/profile, account/subject digest, issuer/audience,
ID-token expiry, private-claim, quarantine, file ownership/mode, sealed delivery,
no-refresh and no-writeback checks remain in force. An expired ID token still
refuses delivery, even with a valid nanosecond refresh timestamp. No tokens,
issuer/audience defaults or public claims are invented to obtain success.

Native auth parsing is not provider authentication, account capacity or
observed model identity. A configured route remains configured. Existing
advisory Measurement/qualification status may remain advisory; this repair
does not require upgrading subscription Bindings contrary to Caplab policy.
Actual catalog enrollment/admission evidence remains separate.

Root252 additionally reports a separate read-only predicate diagnostic of the
exact primary credential: seven top-level `credential_custom_claim_key_invalid`
and one `credential_nested_claim_key_invalid` observations, with source bytes
unchanged and no raw names/values retained. This is supplied evidence, not a
real-credential inspection by the implementer. Those constraints remain
unchanged; the timestamp repair alone does not make that credential executable.

After reviewed integration, regenerate source/runtime apparatus identities
through supported preparation. Do not edit inherited experiments, profiles,
receipts or historical evidence to fit this implementation. The native bundle
policy/member pins and subject tuple are not rewritten by this change.

Root252 selects eventual supported native credential refresh outside the
experiment, immediately before execution, with explicit same-account digest
and freshness checks. **No refresh is performed or authorized for execution
by this source task.** Exact live administration still requires its own later
registered, time-bounded delegation and authorization under
[ADR 0063](../decisions/adr-0063-bounded-codex-live-revbench-execution.md).
No provider, auth-status or native invocation, real-credential read,
registration or deployment accompanies this repair.

## Synthetic verification

The first public-API nanosecond fixture failed before implementation with
`credential_last_refresh_invalid`. It passes after the parser repair, retaining
source and sealed-copy bytes exactly, refusing sealed writes and quarantining
the full refresh string. Additional public fixtures cover whole seconds,
every fractional width 1–9, a valid leap day, 29 malformed/type/calendar/offset
cases and nine identity/expiry/auth-method/private-claim refusal cases. Tests use only
fabricated credentials in owned temporary directories.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest \
  tests.test_revbench_codex.CodexCredentialTests -v
```

All 10 credential tests pass. The broader Codex adapter and separate
external-token gate ran 57 tests: 56 passed, one host-bound Bubblewrap byte-pin
check failed. The same check fails identically on untouched baseline main;
neither host bytes nor frozen policy is changed to obtain a green result. Exact
commands/results are retained in the implementation report. Verification is not independent
acceptance or live readiness. Sonnet independently reviews the committed
candidate before integration.

## Reopening conditions

Reopen separately before accepting other timestamp zones/precisions, changing
token expiry or identity/private-claim/quarantine semantics, changing the native
subject/bundle, permitting credential writes or refresh during the experiment,
or strengthening authentication, routing, capacity or qualification claims.
