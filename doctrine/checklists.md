# Operational Checklists

For every checked item, record an evidence locator, command/result, or explicit
owner decision. `N/A` requires a reason. A checklist is a gate, not evidence by
itself.

## Implementation readiness

- [ ] The requested outcome, non-goals, and acceptance criteria are observable.
- [ ] The change type(s) and allowable semantic change are classified.
- [ ] Applicable repository instructions, accepted decisions, build/generation
      rules, and ownership boundaries have been inspected.
- [ ] Current entry points, affected callers, data/control flow, and integration
      lifecycle are traced.
- [ ] The intended placement follows the owner of the information, invariant,
      policy, or lifecycle rather than convenience.
- [ ] Input, output, boundary, invalid, partial, cancellation/timeout, and expected
      error behavior are selected or escalated.
- [ ] Public/API/data/compatibility implications are explicit.
- [ ] Existing protection is shown to execute the affected path; missing tests or
      characterization are planned before risky structure changes.
- [ ] The implementation is the smallest coherent slice and does not require
      speculative abstraction or unrelated cleanup.
- [ ] Checkpoints, exact verification gates, stop conditions, and rollback or
      safe-forward behavior are specified.
- [ ] The agent has write and semantic authority for every planned effect.

## Architectural evidence

- [ ] The exact architectural decision is stated without embedding a solution.
- [ ] The driver is expressed as concrete stimulus, environment, response,
      measure, owner, and priority where feasible.
- [ ] Current boundaries, dependencies, data/authority ownership, deployment,
      runtime, and failure behavior are evidenced rather than inferred from names.
- [ ] Recurring change, co-change, incidents, domain language, or operational
      constraints demonstrate pressure at architectural scale.
- [ ] Implementation, process, documentation, or local-refactoring causes have
      been considered before labeling the issue architectural.
- [ ] No change, local change, and at least one materially distinct architecture
      option are evaluated.
- [ ] Each option states problem solved, introduced complexity, contraindications,
      migration, reversal cost, scale, and operational consequences.
- [ ] Proposed boundaries align with independent change/invariants/ownership or
      an explicit runtime/deployment/failure requirement.
- [ ] Quality attributes are prioritized tradeoffs, not an unranked wishlist.
- [ ] A small evolutionary slice, compatibility states, fitness criteria, and
      retirement path exist.
- [ ] Selection, implementation, migration, verification, and acceptance authority
      are assigned to actual owners.

## Refactoring evidence

- [ ] The triggering pressure is a recurring change, defect pattern, review cost,
      near-term task, incident, or comprehension bottleneck—not aesthetics alone.
- [ ] Static structure is linked causally to that pressure; rival causes have been
      checked.
- [ ] Smells and metrics are treated as hypotheses and have local examples.
- [ ] History is filtered for generated, formatting, bulk, rename, and phase-specific
      changes before hotspot/co-change conclusions are used.
- [ ] The preservation boundary includes behavior, API, data, ordering, errors,
      timing/resource sensitivity, security, durability, and operations as relevant.
- [ ] Tests or characterization demonstrably exercise affected paths and failure
      modes; gaps limit the claim.
- [ ] Candidate campaigns are ranked by pressure reduction, uncertainty, blast
      radius, feedback speed, and reversibility.
- [ ] The first campaign has one structural objective and excludes semantic repair,
      features, optimization, upgrades, and unrelated cleanup.
- [ ] Every step can compile/run, verify, checkpoint, and reverse independently.
- [ ] Target-state removal and temporary-seam cleanup criteria are explicit.
- [ ] Completion replays the motivating change or uses a defensible proxy to show
      reduced cost.

## Preservation boundary

- [ ] Authorized behavior changes and protected behavior are listed separately.
- [ ] Inputs, outputs, side effects, state transitions, and externally visible
      timing/order are covered.
- [ ] Public and internal APIs, serialization, files, schemas, protocols, and
      compatibility windows are classified.
- [ ] Error type/category, message/metadata contracts, retryability, cancellation,
      idempotency, partial success, and cleanup are covered where material.
- [ ] Persistent data identity, integrity, ownership, retention, migration, and
      rollback semantics are covered.
- [ ] Concurrency, ordering, atomicity, consistency, and race/deadlock expectations
      are covered.
- [ ] Security, privacy, authorization, audit, safety, and durability properties
      are covered.
- [ ] Latency/throughput/resource bounds that are contractual or operationally
      material are covered.
- [ ] Deployment, configuration, observability, alerting, recovery, and runbook
      behavior are covered.
- [ ] Each preserved property maps to a test, probe, review, monitor, or explicit
      unverified-risk statement.

## Characterization

- [ ] The intended change point and dependency obstacles are mapped before seams
      are introduced.
- [ ] Existing behavior is observed at the narrowest stable boundary that can
      detect unintended change.
- [ ] Characterization tests record what the system does, not what the agent thinks
      it should do.
- [ ] Representative normal, boundary, error, stateful, and known production cases
      are included according to risk.
- [ ] Outputs include material side effects, persistent state, emitted messages,
      ordering, and collaborator interactions where those are contractual.
- [ ] Nondeterminism, clocks, randomness, concurrency, external services, and global
      state are controlled or explicitly bounded.
- [ ] Test doubles replace only dependencies needed for sensing or separation and
      preserve relevant semantics.
- [ ] The test fails or changes when a deliberate mutation violates the claimed
      behavior, or its detection limit is stated.
- [ ] Test setup does not reproduce so much implementation detail that harmless
      refactoring breaks the oracle.
- [ ] Undocumented behavior remains protected until an authorized owner releases
      or reclassifies it.

## Abstraction justification

- [ ] The variation, shared knowledge, policy/mechanism split, substitution,
      ownership, deployment, or independent-evolution pressure is concrete.
- [ ] At least two real examples exist, or one boundary requirement independently
      justifies indirection.
- [ ] Similar code has been compared for shared meaning, not only similar syntax.
- [ ] Expected future variants come from accepted roadmap/domain evidence rather
      than imagination.
- [ ] The abstraction has one coherent contract with explicit invariants, cost,
      lifecycle, errors, and ownership.
- [ ] The abstraction reduces net concepts, caller knowledge, or change amplification;
      it is not merely another name for the implementation.
- [ ] Direct coupling, local duplication, configuration, composition, or a smaller
      helper has been considered.
- [ ] Consumers can use the abstraction without downcasts, escape hatches, flag
      combinations, or knowledge of hidden implementations.
- [ ] Testing substitution does not expose implementation details in a public API.
- [ ] Removal or change is feasible if the predicted variation does not emerge.

## Performance evidence

- [ ] The user/operational objective names workload, environment, metric, target,
      percentile/throughput/resource budget, and time horizon.
- [ ] A representative pre-change baseline is retained.
- [ ] Profiling identifies the relevant resource path under the target workload.
- [ ] The benchmark controls build mode, warmup, repetitions, variance, input
      distribution, caches, limits, and observer effects.
- [ ] Compiler elimination, dead work, coordinated omission, batching, and setup
      cost are addressed where applicable.
- [ ] Algorithm, data movement/I/O, allocation/layout, and only then local
      instruction-level options are considered at the appropriate scale.
- [ ] Concurrency is justified by workload and includes ordering, cancellation,
      backpressure, race, contention, and resource analysis.
- [ ] Semantic tests cover precision, ordering, freshness, errors, fairness,
      durability, and other dimensions the optimization could trade.
- [ ] Before/after comparison uses the same harness and reports uncertainty, tail
      behavior, and non-target resource regressions.
- [ ] Added complexity is proportionate to durable measured benefit and has a
      fallback/reversal path.
- [ ] A stable regression guard or production validation/monitoring plan exists.

## Agent authority

- [ ] The current level—observe, diagnose, recommend, propose, select, authorize,
      execute, verify, or accept—is explicit.
- [ ] The authority source is quoted or linked and is current.
- [ ] Repository/path, data, environment, remote, people, publication, and time
      scope are bounded as relevant.
- [ ] Allowed semantic change and protected behavior are explicit.
- [ ] Product, architecture, domain, dependency, data, security, operational, and
      acceptance decisions reserved for owners are identified.
- [ ] Diagnostic experiments and their side effects fit the authority level.
- [ ] Access, prior unrelated approval, silence, passing tests, and technical
      confidence have not been treated as permission.
- [ ] Material scope transitions require new authority rather than an agent-made
      assumption.
- [ ] Verification evidence and authorized acceptance are reported separately.

## Stop and escalate

- [ ] Stop if intended behavior or acceptance criteria are ambiguous enough to
      change semantics.
- [ ] Stop if available evidence cannot distinguish a defect from accepted or
      relied-upon behavior.
- [ ] Stop if preservation feedback is absent, flaky, too slow for the planned
      campaign, or does not exercise the changed path.
- [ ] Stop if a structural step requires feature, repair, optimization, migration,
      dependency, public-API, data, or architectural change outside the classification.
- [ ] Stop if required writes cross named repository, path, environment, data,
      remote, publication, or people scope.
- [ ] Stop if a high-impact or irreversible action lacks rehearsal, rollback,
      safe-forward, recovery, or authorized exception.
- [ ] Stop if new evidence falsifies the causal model or shows that the proposed
      action will not reduce the named pressure.
- [ ] Stop if repository contracts conflict and precedence cannot be established.
- [ ] Stop if verification would expose secrets, personal data, production load,
      or destructive side effects not explicitly authorized.
- [ ] Escalate with observations, competing interpretations, decision required,
      viable options, risks, smallest unblocker, and a clean current state.

## API review

- [ ] Consumers and their actual use cases are identified.
- [ ] The API exposes domain/policy meaning rather than storage or framework detail.
- [ ] Required operations are coherent; speculative operations are absent.
- [ ] Invalid states are prevented or rejected at one clear boundary.
- [ ] Ownership, lifetime, mutation, concurrency, cost, blocking, and side effects
      are visible where callers need them.
- [ ] Errors, cancellation, partial results, retryability, and compatibility are
      explicit.
- [ ] Naming follows repository and language conventions and distinguishes concepts
      that vary independently.
- [ ] Extension/versioning paths do not promise unsupported generality.
- [ ] Tests exercise the public contract without binding harmless implementation
      details.

## Debugging and repair

- [ ] Symptom, expected behavior, environment, frequency, severity, and last-known
      good state are recorded.
- [ ] A minimal reproducer or bounded incident evidence is preserved before changes.
- [ ] Observations are separated from interpretations.
- [ ] Competing hypotheses name predicted evidence and falsification tests.
- [ ] One variable is changed per diagnostic experiment where feasible.
- [ ] Instrumentation observes the suspected boundary and is removable, privacy-safe,
      and low enough overhead for the environment.
- [ ] The causal chain covers trigger, state, fault, propagation, and observed impact.
- [ ] The repair addresses the earliest controlled cause rather than merely suppressing
      the final symptom.
- [ ] A regression test/probe fails before and passes after, or the limitation is
      explicit.
- [ ] Diagnostic artifacts are removed or intentionally converted into supported
      observability, and adjacent paths are rechecked.

