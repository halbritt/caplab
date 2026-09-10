# Prepared input linkage before task release

`caplab.prepared_task_capture` connects verified task-input materialization to
`SupervisedTaskCapture.capture_before`. The caller owns authenticated directory
handoff, blocked writers, stable custody ancestry, recorder lifetime, release
and cleanup. The helpers neither launch work nor grant execution authority.

An input selection has exactly `custody` (resolved absolute path),
`input_sha256` (independently retained input receipt digest), and a positive
integer `max_receipt_bytes`. `read_task_selection` verifies the input receipt,
inventory and all payloads and returns newly parsed receipt/inventory objects.
Its optional paired `max_task_bytes` and `max_task_entries` ceilings check the
input's declared allowances before reading payloads. That preliminary receipt
read and full verification each have the selection's metadata allowance.

`capture_prepared_before(selection, recorder, descriptor, *, expected_device,
expected_inode)` borrows the recorder and authenticated descriptor. It verifies
the input, materializes it through the existing descriptor-based writer,
captures the before tree and checks its content identity against the input.
The before receipt reread has the same metadata allowance. Content identity
preserves paths, kinds, modes, bytes/hashes and literal symlink targets; source
timestamps and copy-local object names are outside that identity.

The returned `caplab.prepared-task-before/v1` link contains the input anchor,
before-inventory anchor and full `caplab.task-input-materialization/v1` result.
The supervisor must guard and seal it before acknowledging the blocked child.
The shared `receive_mount` implements that ordering and stores the link under
`prepared_task` in its handoff. No link is emitted for its existing input-free
mode. Errors preserve partial task/capture effects and propagate; the caller
must close the recorder and refuse release. No retry, rollback or cleanup is
performed by the helper.

`verify_prepared_before(selection, before, link, *, expected_before_sha256)`
requires a before receipt whose schema, anchor, payloads and descriptor linkage
the caller has independently verified. It verifies selected input bytes and
requires exact input/before anchors, materialization counts, content identity,
destination identity and result flags. The before content hash must agree
separately; a self-consistent materialization report for a different task fails.
Booleans do not match numerical counts or vice versa.

The `caplab.prepared-task-before-inspection/v1` result reports input/content and
before hashes, `prepared_content_agrees: true`, and `study_eligible: false`.
It does not prove source truth, freeze timing, workload blocking, complete
capture, native execution, independent validation or study eligibility. The
shared native custody inspector requires an explicit `expected_task_input` for
this mode; otherwise it preserves the empty-before requirement and refuses an
unexpected prepared-task link.

The [implementation record](../../records/implementation-2026-09-09-prepared-native-task.md)
names authorization, verification and remaining native/study boundaries.
