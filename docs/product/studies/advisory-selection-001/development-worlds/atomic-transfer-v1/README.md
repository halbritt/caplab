# Atomic-transfer development world

This is a development repair exercise for testing a correctness oracle. It is
not an admitted study world, codebook, reviewer benchmark or capability result.
The [construction record](../../../../../records/construction-2026-09-08-atomic-transfer-world.md)
names authorization, author exposure, verification and remaining gates.

The task concerns a local SQLite ledger. A successful transfer moves integer
units and records its request ID. Exact retries must be harmless, conflicting
retries must fail, and a statement failure must not leave half a transfer.
The distinction matters because balances can look correct on a happy path while
retries or interruptions damage the ledger.

| Artifact | Role |
|---|---|
| `TASK.md` | Task and acceptance contract, authored before the implementations |
| `parent/transfer.py` | Broken starting implementation |
| `repairs/transaction.py` | Candidate repair using an immediate transaction and separate debit/credit updates |
| `repairs/savepoint.py` | Candidate repair using savepoint rollback and one set-based update of both accounts |
| `negatives/retry_only.py` | Handles repeated IDs but retains non-atomic writes |
| `negatives/false_success.py` | Rolls back SQLite failures but reports success |
| `oracle.py` | Pure ledger model, state/return checks and bounded statement-failure experiments |
| `development.json` | Content identities, exposure and explicit exclusions; not a protected study freeze |

The two candidate repairs use different update and rollback strategies. Their
checks use the same logical state model; no comparison to patch text or concept
words occurs. Passing these checks supports the stated finite examples and
failure boundaries, not exhaustive correctness or independent validation.

Run the development checks from the CAPLAB repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python3 -m unittest test_atomic_transfer_world -v
```

The oracle reports separate fresh-transfer, retry, conflicting-retry, input,
funds, Unicode, sequence and statement-failure observations. It has no aggregate
score. The tests additionally exercise two concurrent connections for competing
withdrawals and duplicate request IDs. Those schedules are evidence, not a proof
of all interleavings. SQLite busy/locked errors are permitted by the task and
must leave no partial transfer. The caller owns retry policy.

For each supported witness, the fault experiment first counts direct
`connection.execute` calls on a successful fresh or replay path. It then creates
a fresh database for every boundary and raises one synthetic SQLite error before
that call executes. It checks error propagation, unchanged state, closed
transaction and subsequent retry. This includes transaction publication calls
made through `execute`; it does not simulate post-commit response loss, power
loss or storage corruption. Exact successful retries exercise the response-loss
recovery rule without claiming to inject a network failure.

The fault wrapper supports `execute` and `in_transaction`. Other connection
operations produce `unavailable`; they do not establish a defect in an otherwise
correct implementation. Direct cursor operations, implicit context-manager
commits, stored functions and SQL triggered indirectly are not comprehensively
instrumented. The supplied witnesses were inspected to use only the supported
surface. The oracle is for trusted local development code, **not a sandbox or
an adversarial candidate runner**. Before assessing a new implementation,
validate its observation coverage; do not treat an unobserved failure boundary
as a pass or expose the oracle to a future study subject without an explicit
visibility decision.

The primary agent authored task, fixtures and oracle in the same ongoing
CAPLAB context, after exposure to governance, code-authoring rules and engineering
doctrine. Its exact author Binding is not attested in this dossier. There is no
independent validator, blinded task-authoring claim, concept nomination, B/P
pairing, behavioral code, protected freeze, native episode or human accuracy
anchor. The oracle itself still needs independent review before study use.

This world and its derivatives are permanently excluded from any claim of an
unobserved study population. Their behavior may be used for authorized
development, but a new hash does not erase exposure. No target concept or
population eligibility is inferred from the task theme. Correctness, concept
uptake, reviewer capability and real-world value remain distinct.
