---
id: adr-0070
artifact_type: architecture-decision-record
title: Opt-in retrieval command assignment custody and shared admission
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-10-08
supersedes: []
---

# Retrieval command shared admission

Select the requested opt-in retrieval CommandAdapter integration under ADR0026.
The external enrollment pins a normalized retrieval spec and every command arm
in it. Each experiment/arm/query/seed owns one durable native launch right,
independent of changed command or request bytes. Reserve/prepare before possible
outer creation; use the existing SDK for all resource accounting. Positive
Popen return counts the outer child, including later exec failures. A constructor
exception is unresolved. A completion wholly before Popen can retire a closed
unused right. No new resource ledger or provider-percentage conversion exists.

The configured profile is an explicit operator declaration of the finite
account/pool domain this arm consumes, not provider-authenticated identity or a
native-agent Binding. This does not authorize a model or harness substitution.
Preserve the retrieval request/response and scoring contracts, sealed roster,
raw bytes, timeout/output limits, scrubbed environment and historical runs.
Unenrolled commands retain their existing behavior. Cairn helpers/database
processes and other producers are not enrolled by this slice.

Enrolled commands use a separate bwrap session, held PID1 observation and
`--die-with-parent`. An actual stronger crash control showed application
execution after block-writer EOF despite eventual parent-death killing. Add a
pinned in-sandbox Python exec gate: it reads exactly one explicit release byte
from the owned stdin pipe before execing the original command; EOF exits 78.
The capped native feeder sends that byte only after admission/readiness checks,
then the unaltered request. The gate is a startup stage of this same outer
launch, not another outer harness or a separately admitted native subject.
Its source/interpreter and containment argv are pinned; `-I -S` isolates its
Python imports from command HOME/cwd/site configuration. Parent death without a
completion still provides no retained accounting closure. Retain same-boot UTC/monotonic creation brackets and the
owned namespace-init pidfd death before proposing settlement. Unknown custody,
cleanup or clocks remains held. Restart reads original intent/output/completion;
it never retries a consumed assignment. An unfinished historical experiment is
not rewritten. A new evidence output may project retained assignment outcomes
with explicit recovery provenance. Changed pins or intent refuse that projection.

Authorize source changes in agent293's isolated worktree, provider-free actual
process/SDK tests in private homes, construction of a source-pinned wheel, and
verified opt-in installation of the tested source. Preserve current main and
installed predecessors until the exact tested commit has a recorded integration
selection. Preserve active runs, provider credentials, historical evidence and
qualification cohorts. No production SDK-home mutation, model/provider calls,
measurement acceptance or live cohort qualification is selected by this ADR.
Stop and retain unexpected setup, process, accounting or provenance results;
repair demonstrated source/fixture defects with explicit receipts rather than
silently weakening controls. Installed fixture success is not native scientific
qualification or universal producer coverage.
