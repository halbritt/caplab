# Evaluation snapshot gate

The active CAPLAB evaluation gate compares a deterministic candidate snapshot
to a separately approved baseline and policy:

- [`synthetic-replay-baseline-v1.json`](synthetic-replay-baseline-v1.json) is
  the initial fresh synthetic baseline selected by ADR 0032; and
- [`synthetic-replay-policy-v1.json`](synthetic-replay-policy-v1.json) binds
  that baseline's canonical identity, coverage floor, and exact score rules.

There is no baseline writer or automatic update command. A different baseline
requires a new decision and a new policy identity. The current artifacts use
only the fresh CAPLAB fixture; they contain no historical BOOKS result.
