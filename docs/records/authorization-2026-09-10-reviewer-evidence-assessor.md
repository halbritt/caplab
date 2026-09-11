# Challenge evidence assessment on natural findings

Under ADR 0026 and the active reviewer-ranking goal, authorize one bounded
native evidence-assessor experiment in private custody
`reviewer-ranking-001/development/evidence-assessor-1`. The assessor interprets
reported findings against independent evidence; it is not a reviewer discovery
trial and produces no ranking measurement.

Permit exact, hash-checked copies of:

- `claude-output-1/final-report.json`, SHA-256
  `40fc1ea84cc5e78a7c4bc056179be3ef83f63f93e836d65fcf63bcdf133dfd45`;
- `finding-units-review-1/capture/final-message.txt`, SHA-256
  `ad47259eb3ab98374b03ac07635dfa8f59ffa62d99716441fa4dd755dcd92e84`;
- the full original task from `newsroom-natural-output-2`, checked against its
  preparation hash `0a5f444de83daac52326e778a5c4977997a01011b242edcfa0cedf1d464c402c`,
  retaining base `1bfe5a656bcb2c663891afd5f980211a3ef144a8`, change
  `544f7e3c43eaa0c06cf17d9e93613d33c0cfb66f` and original provenance;
- observation.json, requests.json and available harvest.stdout/harvest.stderr
  from the completed captures of `newsroom-findings-witness-1` and
  `partial-refresh-witness-1`, checked against their original inventories;
- the three original upstream source/document files and provenance manifest
  under `claude-output-1/references`, checked against manifest SHA-256
  `45e159993103b49f93f46e8a31a8bc6562d3bbc96238ac50201b82018fb72cd5`.

Copy source reports unchanged outside the assessor mount. Inside it, preserve
every natural finding and limitation with neutral document/finding IDs; remove
only author/run identity metadata. Preserve original quoted paths and explain
the source-root mapping in the assessor prompt. Derive controlled variants
that reverse the RSS condition, assert only the incorrect v244 premise,
duplicate a confirmed finding, withdraw a report, and contain relevant
keywords without asserting a defect. These variants challenge scoring and
must never become reviewer measurements. Keep the original/synthetic mapping
and primary-agent expected assessments outside the mount, frozen before the
assessor invocation. Five natural findings plus six controlled finding
occurrences form seven documents; repetitions are not independent cases.

The assessor receives original source, requirements and captured observations,
not prior assessments, verification verdicts, reviewer identities, expected
labels, rankings or private runtime logs. Evidence of behavior is distinct
from a requirement, change attribution and an acceptance effect. Required
assessments are confirmed introduced defect, refuted claim, unresolved, mixed,
or no defect claim. Preserve reported uncertainty/withdrawal and advisory/block
judgments exactly. Group duplicate root causes only within a report. Do not
infer severity or a blocking policy from correctness alone. Matching labels,
valid citations and JSON are necessary checks, not sufficient semantic proof;
inspect whether each explanation is actually supported. All frozen cases must
satisfy the stated checks before this bounded challenge passes.

Authorize one native Codex CLI 0.153.4 `codex-terra-max` invocation, enforced
through native-agent-systems.json, with a 600-second outer deadline and one
ten-second namespace version preflight. Use the existing sealed external-token
projection, credential-private-text/v4 and readable-rollout projection. Pin
prompt, schema, inputs, expected assessments, runner, native vendor package
and support before launch. Suppress user configuration/rules, apps, plugins,
remote plugins and skill search. Preserve native system behavior otherwise.
Read-only task, fresh volatile home/runtime and scratch; no other source,
answer keys or previous contexts mounted. Network is for the native provider;
no external research or target-service access. Do not execute the original
projects or repair them. No hard dollar cap, refresh, account pooling or retry.

Preserve native output and failures under the established guarded capture
rules. Stop on input drift, credential refusal, identity mismatch, unsafe
capture or deadline. Delete only the new volatile runtime after capture.
Allowance expires on consumption or 2026-09-11T02:00:00Z. The experiment may
expose errors but cannot establish general scorer validity from one exposed
source change. No case admission, comparative result, scorer acceptance,
ranking or operational qualification is authorized.

Before preparation, also permit copying each of the two witness roots'
`witness/probe.py` files after verifying their recorded witness inventories.
These expose the exact synthetic inputs and invocation method behind the
observations. They are read-only evidence, not executable tasks. Do not copy
hidden verdicts, prior finding assessments or verification conclusions.
