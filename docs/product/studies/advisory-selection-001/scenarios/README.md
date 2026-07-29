# scenarios

All 20 scenarios are **authored** (2026-07-29, workflow `wf_dcc02d05-04e`):
each directory holds `world/` (buildable, tests green, defect latent),
`TASK.md` (60–120 words, consumer register, authored blind to
`retrieval_terms`/`routing`), `reference.md`, `codes.json` (concept codes +
SCOPE, none firing on the untouched world), and an empty `headroom.json`.

Each was adversarially verified by an independent agent: tests re-run, task
word count and vocabulary checked against the concept record, every code
applied to the pristine tree and to the reference repair.

**Nothing is admitted.** Admission requires *measured* unaided headroom in
`[0.25, 0.75]` (`none` arm, k >= 5) — see `../README.md`. `headroom.json`
stays empty until that measurement runs. See `MANIFEST.md` for per-scenario
status.
