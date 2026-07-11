# Universal Engineering Doctrine

This layer applies across engineering roles. It does not select a design school,
grant execution authority, or override repository evidence. Detailed operational
records live under `concepts/`; the table below is the compact retrieval surface.

| Principle | Operational rule | Evidence that earns action | Stop or narrow when |
|---|---|---|---|
| Repository precedence | Follow explicit task authority, accepted repository contracts, and current runtime facts before generic doctrine. | Applicable instructions, accepted decisions, executable repository gates, and current target state. | Contracts conflict, authority is unclear, or following a generic rule would violate a local invariant. |
| Evidence before intervention | State the problem as an observable condition and gather evidence capable of distinguishing action from no action. | Reproduction, structural violation, recurring change pressure, incident, measured constraint, or accepted requirement appropriate to the claim. | The evidence is only aesthetic, anecdotal, source-prestige based, or unrelated to the proposed remedy. |
| Classify the change | Name the intended change type before planning mechanics; apply every type's semantic, authority, and verification gates. | Accepted desired effect and preservation boundary. | Work labeled refactoring, cleanup, or optimization contains unapproved behavior, architecture, migration, or dependency change. |
| Preserve behavior by default | Treat existing observable behavior as protected unless an authorized contract identifies what may change. | Explicit behavior-change authority plus acceptance criteria. | Intended behavior is ambiguous, undocumented behavior may be relied on, or available tests cannot support the preservation claim. |
| Minimize simultaneous uncertainty | Change one causal or structural variable at a time when diagnosis, preservation, or measurement matters. | A baseline and a sequence whose checkpoints isolate effects. | A broad diff prevents attribution, rollback, review, or benchmark comparison. |
| Prefer local reasoning | Place behavior and information so a maintainer can understand and change a responsibility without reconstructing distant hidden state. | Repeated navigation, cross-boundary knowledge, parameter leakage, scattered invariants, or coordinated edits tied to one concept. | Localizing duplicates an authority, weakens an invariant, or hides an unavoidable distributed contract. |
| Reduce change amplification | Restructure only when one conceptual change repeatedly requires disproportionate, risky, or cross-owner edits. | History, co-change, incident, review, or implementation evidence identifying the same change axis. | Churn is generated, one-off, phase-specific, or caused by requirements rather than structure. |
| Make invariants explicit | Give each invariant a clear owner, representation, enforcement point, failure policy, and test or monitor proportionate to risk. | Domain policy, accepted contract, data constraint, incident, or repeated defensive checks. | The proposed invariant is merely a preference, duplicates another authority, or cannot be stated over observable state. |
| Preserve information hiding | Hide design decisions likely to change behind a boundary that offers a simpler, stable contract. | Multiple callers currently depend on volatile representation or mechanism details. | The boundary leaks the same complexity, adds a pass-through layer, or obscures essential cost and failure semantics. |
| Earn abstraction | Introduce indirection only for demonstrated variation, independent evolution, policy/mechanism separation, substitution, ownership, deployment, or repeated knowledge. | At least one concrete pressure plus evidence that the abstraction reduces net reasoning or change cost. | Only one speculative future use exists, the interface mirrors an implementation, or duplication is not yet understood. |
| Separate semantic and structural work | Keep behavior change, defect repair, refactoring, optimization, migration, and cleanup as distinct checkpoints. | Change-type classification and protection for each checkpoint. | Reviewers cannot tell which diff causes which observable effect. |
| Prefer reversible, reviewable steps | Choose the smallest coherent step that can be verified, reverted, and explained independently. | A checkpoint plan, fast feedback, and rollback or safe-forward route. | A step creates a long-lived inconsistent state, violates atomicity, or cannot meet a mandatory compatibility window. |
| Make failure explicit | Define expected error, timeout, retry, partial-success, cancellation, and recovery behavior at boundaries where failure is material. | Operational scenario, API contract, incident, or resource/consistency constraint. | Added handling masks the cause, retries unsafe work, duplicates responsibility, or invents policy without an owner. |
| Measure claimed improvements | Preserve a representative baseline and measure the dimension named by an optimization or process claim. | Valid profile, benchmark, history analysis, or operational metric with known limits. | The signal is unrepresentative, noisy, confounded, or lacks semantic regression protection. |
| Keep no-change viable | Leave code or architecture unchanged when the expected reduction in demonstrated pressure does not exceed migration, indirection, learning, and operational cost. | Explicit comparison of current cost, change forecast, alternatives, and reversal cost. | The recommendation depends on aesthetics, symmetry, fashion, or a source's preferred architecture. |
| Distinguish assertion levels | Label observation, inference, recommendation, decision, verification, and acceptance; never silently promote one to the next. | Provenance for observations, rival hypotheses for inference, authority for decisions, and criteria for verification/acceptance. | The artifact obscures uncertainty, authority, or who owns acceptance. |
| Respect authority and stop conditions | Work only within the granted action level and target scope; evidence cannot create permission. | Explicit task authority or accepted repository mechanism. | Required action changes semantics, architecture, data, dependencies, operations, publication, or scope beyond the grant. |

## Required decision frame

Before recommending or executing material work, produce:

1. **Decision question:** the exact choice or change being considered; it becomes a
   decision only when an authorized owner records a selection.
2. **Authority:** who may observe, diagnose, select, execute, verify, and accept it.
3. **Evidence:** observations that establish the problem and evidence still missing.
4. **Context:** repository archetype, lifecycle, language, operational and risk constraints.
5. **Preservation:** behavior, API, data, ordering, failure, performance, security,
   durability, and operational properties that may not change.
6. **Options:** no change and at least one lower-cost or more reversible alternative
   when material tradeoffs exist.
7. **Step:** the smallest coherent, reviewable action and its rollback or safe-forward path.
8. **Verification:** criteria, baseline, commands or probes, and residual uncertainty.
9. **Stop:** evidence or scope transitions that require reversal or escalation.

## Universal anti-patterns

The following are never sufficient evidence on their own:

- a large file, long function, code smell, old code, or high churn;
- directory names, dependency counts, diagrams, or architectural symmetry;
- a passing test suite without proof that it exercises the relevant contract;
- a single profile, fastest benchmark run, or unrepresentative load test;
- simultaneous edits, blame, ownership diffusion, or an incident without causal analysis;
- one implementation, one duplicated fragment, or a hypothetical future variant;
- framework availability, source prestige, community fashion, or agent preference;
- technical access, prior unrelated permission, or silence as execution authority.
