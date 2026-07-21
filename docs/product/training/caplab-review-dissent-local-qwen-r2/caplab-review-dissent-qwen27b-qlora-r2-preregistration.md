# Qwen3.6-27B review-dissent QLoRA r2 preregistration

The complete scientific contract is inherited byte-for-byte by field from the
r1 machine manifest and is restated in r2's
[`training-experiment.json`](training-experiment.json). R2 changes no model,
training row, target, method, seed, compute ceiling, held-out cell, control,
native harness, analysis, success rule, or claim ceiling.

R2 adds only these preregistered operational gates:

1. one 60-second repeated forward/backward qualification with zero optimizer
   steps and identical adapter hashes before and after;
2. at least four distinct external fleet heartbeats showing exact marker slot
   1 alive, routable, and held by the same lease;
3. a constant Windows boot identity from qualification through training;
4. a five-second lease pulse with a 45-second remote expiry;
5. a Windows Job Object with `KILL_ON_JOB_CLOSE` around each remote phase; and
6. a machine acceptance marker before `training-started.json` may exist.

The r1 partial checkpoint is excluded. Qualification failure consumes no
training attempt. Any failure after the r2 training-start marker consumes the
one attempt. Held-out bytes remain sealed until the step-12 adapter is sealed.

ADR 0053 records the selection and ADR 0054 records execution authority.
