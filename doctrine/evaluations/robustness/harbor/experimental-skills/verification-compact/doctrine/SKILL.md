---
name: doctrine
description: Verify safety-relevant interface claims before changing behavior.
---

# Bounded contract verification

Before editing:

1. Read the task, client code, interface contract, and available local test
   boundary.
2. State one safety claim the change depends on, the harmful failure if it is
   false, and an observable that could falsify it.
3. Run the smallest reversible local probe that can falsify the claim. Inspect
   durable side effects or the system of record, not only a response code or
   required smoke test. When retry or idempotency behavior matters, repeat the
   same logical operation.
4. If observed behavior contradicts the safety claim, or a high-risk claim
   cannot be checked, leave the implementation unchanged and use the task's
   decision artifact to record the observation and evidence, inference and
   credible rivals, and recommendation.
5. Otherwise implement the change, rerun the probe, and run the required tests.
