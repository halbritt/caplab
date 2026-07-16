# Execution and verification records

Execution records state what an authorized executor changed. Verification
records independently compare those effects with frozen criteria. Neither is
acceptance.

CAPLAB-22/P4 produced separate records for campaign
`caplab-p4-roundtrip-2026-07-15`:

- [`caplab-p4-execution-2026-07-15.md`](caplab-p4-execution-2026-07-15.md)
  records the authorized effects and quarantine state; and
- [`caplab-p4-verification-2026-07-15.md`](caplab-p4-verification-2026-07-15.md)
  records the independent PASS by `caplab22_verifier`.

Neither record accepts CAPLAB or authorizes P5.

CAPLAB-23/P5 proposal preparation produced a static-first
[`failure-mode audit`](../../CAPLAB_FAILURE_MODE_AUDIT_CODEX_2026-07-16.md).
The audit records current recovery gaps; it is not an execution or verification
record and does not authorize the proposed campaign.
