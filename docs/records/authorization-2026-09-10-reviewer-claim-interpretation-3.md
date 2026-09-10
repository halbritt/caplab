# Opaque reasoning capture projection and new interpretation slot

Under ADR 0026, authorize a narrowly scoped capture projection and a new
development custody `reviewer-ranking-001/development/claim-interpretation-3`.
Preserve the second experiment unchanged: its native process completed, but
one root rollout was quarantined and its assessment was withheld. It cannot
be recovered or promoted by changing its old completeness rule.

Implement and test a projection only for Codex native JSONL response-item
records whose payload type is `reasoning` and whose `encrypted_content` is a
string. Omit that opaque field, retaining its original byte length and hash,
row index and original whole-file hash in a separate receipt. Preserve every
other JSON value, including summaries, tool calls, tool outputs, final text
and metadata. Preserve untouched JSONL lines byte-for-byte. Reject malformed
JSON, duplicate keys, or unexpected encrypted-content shapes. Run the existing
credential-private-text/v3 guard on both projected content and its receipt
before either reaches durable capture. Do not remove or weaken any credential
marker, decode opaque reasoning, or retain unguarded ciphertext.

The projection addresses an observed capture boundary, not reviewer quality.
The prior cutoff is inside opaque encrypted content. A read-only check also
confirmed that the public JOSE field name `kid` is a v3 marker and rejects
ordinary text containing that word. The discarded bytes are unavailable, so
the exact triggering marker is unknown. Do not claim that a specific collision
or credential leak has been established for the prior run.

After projection tests pass, authorize copying the second experiment's
hash-checked task inputs, prompt, semantic expectations, assessment cases and
outcome plan into the new custody. Keep all 24 documents and assessment
criteria unchanged. Add the exact projection implementation hash and its
explicit omission policy to the new native plan before execution. The native
subject receives no empirical truth or projection implementation.

Authorize one new native Codex CLI 0.153.4 / `codex-terra-max` invocation, one
10-second version preflight and a 600-second process limit, with all the second
authorization's identity, credential, isolation and no-ranking boundaries.
This is a new consumed-once slot, not a replay of the old identity. Expiry:
consumption or 2026-09-11T00:00:00Z. Stop on drift, projection failure, remaining
quarantine, credential failure or deadline. Complete readable capture must
still be demonstrated before development assessment; no partial final is a
substitute. This does not accept a production scorer or comparative ranking.
