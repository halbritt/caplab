---
id: adr-0069
artifact_type: architecture-decision-record
title: Pool refusal containment and interrupted assignment recovery
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-10-08
supersedes: []
---

# Pool refusal containment and interrupted assignment recovery

Independent Opus310 and real supervisor-exit controls demonstrate two defects
in the ADR0068 implementation: an unobserved blocked PID1 can launch after a
refused pool supervisor exits, and a completed assignment cannot rebuild its
lost measurement row. Keeping the writer open only delays EOF until exit; it
does not establish physical refusal containment.

Under ADR0026, select and authorize this source repair, provider-free real
process/SDK tests in private synthetic homes, wheel construction and verified
opt-in tool installation. Preserve active campaign pins, historical custody,
native deadlines, one-shot assignments, native subject policy and the SDK's
sole resource authority. Stop and retain receipts on unexplained process,
accounting or provenance results. No provider run, production admission-home
mutation, measurement registration or qualification acceptance is selected.

Each prospective pool outer monitor is a separately owned session leader. On
startup refusal, signal its group with SIGKILL before reaping the leader,
attempt held-PID1 abort before fallible completion/reconciliation, and positively
observe death when a witness exists. Group signalling does not manufacture SDK
quiescence when no witness exists. Keep such accounting held. Preserve the
original exception, including interruption, and expose secondary cleanup failures
as exception notes and native completion facts rather than replacing it.

Direct invocation still refuses the same assigned launch. Enrolled case
resumption explicitly reads that assignment instead: verify its intent and
stream/completion preimages, rebuild from complete native outputs, or report an
unusable assigned outcome when completion/output is absent. Recovery prepares
or spawns nothing for that assignment and cannot grant a new retry. Unknown
custody, an active supervisor, or a crash is not positive closure. Changed pins,
prompt, plan or output refuse; do not make a new key to escape the refusal.
Native elapsed duration is retained as integer milliseconds; no event timestamp
is invented. Older completion bytes remain readable and unwritten. Missing old
duration remains missing in the projection.

An expired enrollment may recover already assigned outputs; creating any new
assignment still checks the original expiry and timeout. Frozen instrument
source/run-spec identity remains mandatory, so this is not authorization to
rewrite or relabel historical administrations under new source.

This corrects ADR0068's controlled no-witness refusal path. Abrupt supervisor
SIGKILL in the held window can still release the application by descriptor EOF;
that broader crash topology remains unqualified. Retained accounting cannot
prove physical noncreation. Remaining producers and actual provider-account
authentication remain separate native integration work, not inferred coverage.
