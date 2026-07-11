# Evaluation Rubrics

Use these rubrics after the applicable hard gates. Score each criterion `0`, `1`,
or `2`: `0` means absent or contradicted; `1` means present but incomplete,
weakly evidenced, or overly broad; `2` means explicit, proportionate, and linked
to inspectable evidence. `N/A` is allowed only with a one-sentence reason and is
removed from the denominator.

The normalized score is `earned / (2 × applicable criteria)`. A score cannot
override a hard gate, repository contract, or authority limit.

The numeric bands below are provisional retrieval and review aids, not calibrated
probabilities or validated quality thresholds. Record criterion-level evidence and
hard-gate outcomes as the authoritative result. Calibrate bands with independent
raters and observed downstream outcomes before using them as automated acceptance
policy.

## Coding-agent plan

Hard gates: accepted task semantics; known write scope; repository instructions
inspected; no unresolved owner decision disguised as implementation detail.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Outcome and non-goals | Vague activity list | Outcome stated; exclusions weak | Observable outcome, non-goals, and acceptance criteria are explicit |
| Current-path understanding | No evidence of code-path inspection | Entry point or integration inspected | Entry, data/control flow, owners, invariants, and affected callers traced |
| Placement decision | Chosen by convenience or new-file bias | Fits current layout superficially | Placement follows information, invariant, lifecycle, and change ownership with alternatives considered |
| Change classification | Missing or mislabeled | Primary type named | Every embedded change type and its semantic/authority gates are named |
| Edge and failure behavior | Happy path only | Common errors listed | Boundary, invalid, partial, timeout/cancel, retry, and recovery behavior are selected or escalated |
| Protection plan | “Add tests” | Test level named | Existing and new contracts, reproducer/characterization, and exact gates are identified |
| Sequence and reviewability | One broad implementation step | Several steps without proof points | Each coherent checkpoint has expected diff, verification, and stop condition |
| Scope and authority | Assumed | Scope stated | Allowed writes, reserved decisions, escalation triggers, and acceptance owner are explicit |

Provisional readiness bands: `<0.70` revise; `0.70–0.84` proceed only for low-risk work after
closing every zero; `≥0.85` ready if all hard gates pass.

## Implementation

Hard gates: implements authorized semantics; required repository checks pass;
no unreviewed generated/vendored edits; no critical security, data, or durability
regression.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Correctness | Contradicts contract or misses core case | Main path works; gaps remain | Accepted behavior, edge cases, and failures are demonstrated |
| Repository integration | Bypasses conventions/contracts | Mostly conforms | Uses established boundaries, naming, generation, errors, and lifecycle intentionally |
| Responsibility and placement | Scattered or misplaced behavior | Reasonable locality with leakage | Information and invariant owner contains the behavior; callers remain simple |
| API and representation | Leaks volatile details or invalid states | Usable but broader than needed | Minimal coherent surface, explicit invariants, compatibility and cost/failure semantics |
| Control and data flow | Hidden mutation/order or needless indirection | Understandable with effort | Obvious main path, explicit state transitions, bounded side effects, appropriate data structures |
| Failure behavior | Swallowed, ambiguous, or unsafe | Some cases handled | Expected failures, context, cleanup, cancellation/retry/idempotency, and observability are coherent |
| Tests and evidence | Tests do not exercise change | Primary outcome covered | Risk-driven contracts, negative/boundary cases, and regression path are proven |
| Simplicity and scope | Speculative framework or unrelated churn | Minor excess | Smallest sufficient design; duplication/abstraction decision is evidence-based |
| Reviewability | Mixed concerns, opaque diff | Reviewable with reconstruction | Semantic and structural intent are separable; rationale and verification are easy to audit |

Provisional readiness bands: `<0.75` reject or revise; `0.75–0.89` conditionally acceptable
after closing zeros; `≥0.90` technically ready, subject to authorized acceptance.

## Architectural assessment

Hard gates: decision question and authority are explicit; current state is
evidenced; no architecture school is assumed as the target; no-change is
evaluated.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Architectural driver | Aesthetic or solution-first | General quality attribute | Concrete stimulus, environment, response, measure, owner, and priority |
| Current-state evidence | Diagram or directory inference | Static evidence only | Static, runtime/operational, history/domain evidence triangulated as relevant |
| Boundary pressure | “Decouple” or “split” assertion | One plausible pressure | Independent change, invariant/data ownership, deployment, failure, or policy pressure is demonstrated |
| Alternatives | Preferred pattern only | Two options | No change plus materially distinct options, costs, contraindications, and reversal paths |
| Tradeoffs | Benefits only | Generic costs | Quality, cognitive, operational, migration, coordination, and option costs tied to evidence |
| Scale and reversibility | Big-bang destination | Staging mentioned | Small fitness-tested slice, compatibility state, rollback/safe-forward, and retirement path |
| Domain and ownership | Names imply domains | Ownership partly addressed | Language, policy, data authority, team/operations ownership, and context differences align |
| Fitness and uncertainty | Success is subjective | Some metrics | Falsifiable fitness criteria, baseline, review point, residual questions, and stop conditions |
| Authority discipline | Assessment silently authorizes work | Approval need mentioned | Recommendation, selection, execution, verification, and acceptance owners are distinct |

Provisional readiness bands: `<0.75` not decision-ready; `0.75–0.89` candidate assessment
requiring named evidence; `≥0.90` ready for owner selection, not self-authorization.

## Refactoring assessment

Hard gates: structural pressure is demonstrated; preservation boundary is
explicit; semantic repair is excluded or separately classified; target scope is
authorized.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Change pressure | Smell/aesthetics only | Plausible maintenance complaint | Repeated change, defects, review cost, incidents, or near-term work tied to structure |
| Causal diagnosis | Structure assumed guilty | Candidate cause stated | Rival causes considered; static/history/runtime evidence links structure to pressure |
| Preservation boundary | “No behavior change” only | Key APIs/tests named | Behavior, API, data, ordering, error, timing/resource, security, and operations scoped |
| Characterization | Existing suite assumed | Relevant tests identified | Tests/probes demonstrably cover affected paths; unknown behavior is captured or excluded |
| Campaign choice | Broad cleanup | Bounded target | Ranked candidates; first campaign offers best pressure reduction per uncertainty and cost |
| Sequencing | One large rewrite | Steps listed | Seam/preparation, one structural move at a time, verification, checkpoint, and rollback |
| Target-state restraint | Pattern-driven redesign | Improvement stated | Smallest target removes named pressure; temporary structures and cleanup criteria explicit |
| Stop/reversal | None | Generic “if tests fail” | Specific preservation failure, scope expansion, weak feedback, or pressure non-improvement stops work |
| Evidence of benefit | Cleaner appearance | Reduced metric asserted | Original change/review task is replayed or a defensible proxy demonstrates reduced cost |

Provisional readiness bands: `<0.80` not earned; `0.80–0.89` proposal only; `≥0.90` campaign
ready if every hard gate and execution authority passes.

## Repair plan

Hard gates: expected behavior is accepted; defect is reproduced or uncertainty is
explicitly classified; repair authority is distinct from diagnosis authority.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Symptom and impact | Vague failure | Symptom described | Reproducer, affected users/systems, frequency, severity, and environment recorded |
| Causal chain | Fix guessed from location | Leading hypothesis | Observations connect trigger, state, fault, propagation, and symptom; rivals falsified |
| Repair scope | Symptom suppression or redesign | Plausible local change | Smallest causal repair plus required invariant/guard; adjacent causes considered |
| Regression protection | Test after fix only | Reproducer planned | Test/probe fails before, passes after, and asserts contract at stable boundary |
| Preservation | Unstated | Existing suite relied on | Unrelated behavior, data, failure, compatibility, and operations explicitly protected |
| Rollout and recovery | None | Rollback mentioned | Deployment/feature gate, observability, rollback/safe-forward, and state recovery fit impact |
| Uncertainty and escalation | Overconfident | Some caveats | Evidence gaps, probabilistic assumptions, owner choices, and stop triggers explicit |

Provisional readiness bands: `<0.80` continue diagnosis; `0.80–0.89` low-risk repair candidate;
`≥0.90` execution-ready within granted authority.

## Performance recommendation

Hard gates: quantified objective; representative baseline; semantic preservation
criteria; authority for measurement environment and any tradeoff.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Objective | “Make faster” | Metric named | Workload, percentile/throughput/resource metric, target, environment, and budget named |
| Measurement validity | Anecdote/single run | Benchmark exists | Warmup, repetitions, variance, input distribution, build, limits, and observer effects controlled |
| Bottleneck evidence | Code looks slow | Profile points to area | Profile and causal model show where target resource/time is consumed and why |
| Candidate leverage | Micro-tweak first | Plausible optimization | Algorithm/data flow first; allocation/layout/I/O/concurrency considered at appropriate level |
| Semantics and tradeoffs | Unstated | Core tests named | Precision, ordering, freshness, fairness, error, durability, cost, and tail effects preserved/authorized |
| Comparison | Before/after headline | Average improvement | Same harness, noise/significance, multiple loads, regressions, and non-target resources reported |
| Maintainability and reversal | Fragile cleverness | Cost acknowledged | Complexity budget, documentation, fallback, reversal, and future regression guard justified by gain |
| Scope and confidence | Generalizes broadly | Limited caveat | Claims bounded to measured workload; residual risk and production validation plan explicit |

Provisional readiness bands: `<0.80` speculative; `0.80–0.89` experiment-ready; `≥0.90`
recommendation-ready, with owner approval for any tradeoff.

## Review

Hard gates: review scope and accepted contracts are known; findings are tied to
the actual diff/current source; preferences cannot be blockers.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Correctness focus | Style dominates | Main behavior considered | Data/control paths, invariants, edges, concurrency, failures, and compatibility checked by risk |
| Evidence quality | Assertion without locator | Locator or rationale | Exact evidence, causal consequence, reproducer/test where feasible, confidence and limits |
| Severity | Everything equal | Labels used inconsistently | Blocker/defect/risk/suggestion/preference reflect impact, likelihood, contract, and remedy urgency |
| Architectural consistency | Pattern preference | Existing shape considered | Accepted boundaries/decisions checked; implementation defect not inflated into architecture |
| Security/durability/operations | Ignored | Generic concern | Relevant trust, data, retry, rollback, observability, and failure consequences traced |
| Scope proportionality | Unrelated wishlist | Some scope creep | Findings concern introduced risk or directly required integration; follow-ups separated |
| Remedy restraint | Prescribes redesign | One fix suggested | Smallest adequate remedy; alternatives allowed; reviewer does not seize design authority |
| Uncertainty | Hidden | Confidence implied | Observation/inference split, missing evidence, false-positive conditions, and verification path stated |

Provisional readiness bands: `<0.75` review is not actionable; `0.75–0.89` useful with edits;
`≥0.90` review-ready. A single proven blocker remains a blocker regardless of score.

## Agent scope and authority discipline

Hard gate: the agent can cite the source of its authority and the exact target
scope. Failure is an automatic stop for mutating action.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Action level | Assumed | Role named | Observe/diagnose/recommend/propose/select/authorize/execute/verify/accept ceiling explicit |
| Target scope | “Repository” broadly | Paths/system named | Files, data, environments, people, remotes, publication, and exclusions bounded as relevant |
| Semantic authority | Inferred | Change described | Allowed behavior change and protected behavior explicitly separated |
| Reserved decisions | Agent decides silently | Some approvals noted | Product, architecture, data, dependency, security, operational, and acceptance owners identified |
| Evidence discipline | Confidence substitutes for proof | Evidence listed | Claim-relative evidence, provenance, insufficiency, and rival explanations reported |
| Escalation | Continues through ambiguity | Generic stop | Concrete scope/authority/semantic/risk transitions trigger stop with an inspectable handoff |
| Verification versus acceptance | Self-declares done | Tests reported | Technical verification, residual uncertainty, and authorized acceptance remain distinct |
| Side effects and reversibility | Hidden | Major writes mentioned | Every material local/remote/operational/public side effect and rollback path disclosed |

Provisional readiness bands: `<0.90` do not mutate; `≥0.90` may act only up to the explicitly
granted level. Any hard-gate failure overrides the score.
