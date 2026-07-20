---
id: caplab-8-native-r2-verification-2026-07-20
artifact_type: verification-record
title: CAPLAB-8 native r2 technical verification
status: pass
created: 2026-07-20
decision_record: adr-0043
verifier: primary-agent
independence: not-independent
---

# CAPLAB-8 native r2 technical verification

## Verdict

**PASS** for the technical closure criteria authorized by ADR 0043.

This is primary-agent technical verification, not an independent verdict and
not CAPLAB acceptance.

## Verified evidence

- The native r2 campaign manifest semantic SHA-256 is
  `c6c6eb3e8b9801cc52150edb5fe1b609e2d1724ffc846268421f4330536526b9`.
- The capture manifest binds exactly 12 normalized captures and validates to
  semantic SHA-256
  `4253106bb1af456d6c3e0349a15b20a44cdd847856bf818b3c1c52f9756f8733`.
- The packet manifest binds exactly six packets and validates to semantic
  SHA-256
  `16ddd4c5e01c4092d58b0f4c85c11e33a2f3d474c677278f73f0ee009ed6f1ef`.
- Every packet recomputes to its recorded hash and passes the identity-leak
  refusal before disposition freeze.
- All six delegated decisions were present, used only the fixed reason
  vocabulary, and froze before reveal. The frozen artifact validates to
  semantic SHA-256
  `311e887f1fe99308a190297020e798bd1218e588dcdefdac76dcb17164e7e063`.
- Reveal revalidated capture, packet, and freeze lineage. The result validates
  to semantic SHA-256
  `8b312518d725d308ce24a1c901d64576dddeb35228ac885eb85dfaac4af1347e`.
- Exact recomputation returned six valid pairs, zero Fable strict
  constraint-advantage pairs, five Fable blinded-preference pairs, and the
  preregistered `hypothesis-disconfirmed` conclusion.
- `make check` passed 198 tests with four authorized integration skips on
  2026-07-20. The suite includes native tuple, proxy refusal, capture,
  blinding, freeze-before-reveal, digest-lineage, and threshold tests.
- No additional subject call was made during normalization, judgment, reveal,
  or verification.

## File bytes

The repository files have these byte-level SHA-256 values:

| File | SHA-256 |
|---|---|
| `packet-manifest.json` | `d9a6163588d6b7263d7627f1dc4ba36854d61ef61239af16a0f09889d8c342ef` |
| `blind-decisions-input.json` | `85d27f25c66cb02091f61a9f24a9a9c2eddc9208a25a4949d96ace5fc342fbf8` |
| `frozen-dispositions.json` | `9e2ec4157b9af0cd71d4343eddbdb41ba50b017af5efc12f90b15e27bbebe726` |
| `revealed-result.json` | `ae686af6b252cf55aef41b737231d78ea302d403d4d7bb12bc5c1e2f663c0d35` |
| raw `capture-manifest.json` | `657812f230790ff9dd1277b982a65363de11928c155dc2edca73073bb1fd8281` |

## Closure boundary

CAPLAB-8's execution, delegated disposition, result, and technical
verification criteria are complete. This pass does not supply an independent
verdict, accept CAPLAB, admit the quarantined proxy attempts, or authorize any
later study.
