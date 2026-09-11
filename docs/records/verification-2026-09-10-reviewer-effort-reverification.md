# Effort-control verification reconstructed from retained evidence

The Council effort-parser control now has a retained, challenged verification
method. Recomputing its results from the original captures confirms the
corrected batch's bounded preservation evidence and rejects the first batch's
malformed fixture. No Council code or reviewer was executed in this step.

| Original batch | Inputs per revision | Accepted per revision | Category failures per revision | Frozen criteria |
|---|---:|---:|---:|---|
| `effort-control-1` | 135 | 2 | 42 | Fail |
| `effort-control-2` | 135 | 44 | 0 | Pass |

Both batches produced identical outcomes across their base and change. In the
first batch, 42 expected valid inputs failed at `launch_argv` because the
fixture supplied a relative executable path. Agreement therefore did not
establish preservation of the intended effort-handling properties. The new
checker retains these failures instead of accepting equality alone.

The corrected batch's 44 accepted inputs preserve their complete input values,
including effort presence or absence. Its 91 rejections identify the effort
field. Both revisions report zero TypeScript diagnostics; the changed module's
single added fallback call has argument type `never`. Only
`src/v3/config.ts` differs between the exact Git trees.

## Verification and custody

Under the [bounded authorization](authorization-2026-09-10-reviewer-effort-reverification.md),
checked all 25 original receipt members and 784 source-file instances across
the two batches. Git tree membership, blob identities, source module hashes,
probe/case hashes, original authorizations, exact sandbox commands and normal
completion records agree. All 6,633 dependency inventory entries and the Node
and Bubblewrap binaries still match each batch's plan.

Seven checker tests pass, including eight negative challenge variants for
missing or duplicate observations, identical wrong outcomes, changed accepted
effort, compiler diagnostics, a reachable fallback and altered capture/source
bytes. The first test failed before the verifier existed; that result is
retained. The first successful reconstruction used the repository's dependency
inventory helper. The final method pins a copy of that helper in private
custody and reproduces the same behavioral results. A further read-only
reconstruction equals the final verification document.

The [public receipt](../product/studies/reviewer-ranking-001/effort-reverification-development-receipt.json)
anchors 17 artifacts in private custody
`~/.local/share/caplab/reviewer-ranking-001/development/effort-reverification-1`.
Plan SHA-256:
`3faf8c295ae4d8850d7f16e85d255c2f0416452c7544a84011558b0d443b04f6`.
Verification SHA-256:
`93dd19be4780633fe545dacfdace8fe6eff9f1f3c6cc268ce8d52bf6c69db9d4`.
Original custody and the earlier result remain unchanged. This is a new method
that reconstructs the result; the missing original verification method has
not been recovered.

## Admission disposition

The evidence supports the named member-pinning behavior and compiler
exhaustiveness. Its expected acceptance categories encode existing parser
behavior, without establishing that every product choice is correct. The
configuration-file caller was not executed. Preserve these limits and reopen
any property contradicted by a newly substantiated finding.

No case is admitted by this record. Inspection found that the existing live
admission command is specifically bound to Study 001 and ADR 0014's expired
authorization. It was not executed or changed. A current scoped admission
path and durable evidence registration remain necessary before promoting
these development artifacts. Current dependency equality does not supply
that durability. Scorer acceptance, matched controls, pilot validity and
comparative measurements also remain open.

The existing doctrine packet `pkt-cdafd666a23adaf1` supplies the general
evidence-before-scoring and bounded-authority guidance. Repository criteria,
original source behavior and compiler observations supply this case's
evidence; doctrine does not establish case truth or ranking validity.
