# Placement-policy fixtures {#el:placement-policy-fixtures}

Bodies for the placement-policy parser: one accepted policy and one refusal per
validation rule. The repository's own policy lives at `policy/scheduler.yaml`;
the pass ids (`fixture-build`, `fixture-review`) and backend ids
(`fixture-alpha`, `fixture-beta`) here are fixture names, never fleet passes or
fleet backends.

Each refusal fixture is named for the refusal class it proves:

- `absent-*` — a required declaration is missing. Absence is never a default.
- `unsupported-*` — a key or prefer shape outside the accepted vocabulary,
  including the `expiring_capacity` key and the `mode` match the retired
  `harvest-expiring-first` rule used.
- `out-of-domain-*` — a declared value outside its closed domain.
- `incomplete-*` — a declaration present but not fully stated.
- `ambiguous-*` — one thing declared twice, or two shapes in one rule.
- `unresolvable-*` — an operative declaration that can bind nothing: a pass no
  catalog carries, a backend nothing places, or a rule an earlier rule already
  subsumes under first-full-match.

