# Opt-in retrieval command shared admission

ADR0070 introduces `caplab-retrieval-shared-admission/1`. Existing retrieval
spec/attempt/response schemas and unenrolled commands are unchanged. This
administration covers **all command arms in one pinned spec**, each
experiment/arm/query/seed assignment once. It refuses Cairn arms: their
createdb, database server, git, search and worker helpers are not covered by
counting a command wrapper. Other Caplab producers remain separate.

Create an owner-controlled durable nonrollback directory, disjoint from command
workspaces. Initialize its native identity without reserving capacity:

```sh
mkdir -m 700 /absolute/retrieval-custody
caplab retrieval admission-domain --custody /absolute/retrieval-custody
```

Prepare an existing `caplab-shared-admission-enrollment/2` for each arm, with the
pinned SDK executable/source-tree, one designated home, catalog release,
overlay, policy, mutable observations path, selected enabled entry, caller and
returned custody domain. `binding_id` is the prospective administration's
identity assertion; this adapter does not construct or validate a native-agent
Binding. Its `credential_profile_sha256` is the SHA256 hex digest of canonical
UTF-8 JSON (sorted keys, compact separators, no newline) of:

```json
{"schema_version":"caplab-retrieval-declared-profile/1","profile_id":"EXACT_CATALOG_PROFILE","host":"EXACT_CATALOG_HOST","account_id":"EXACT_CATALOG_ACCOUNT","config_home":null}
```

Use the catalog's actual `config_home`, including null. This profile is the
operator's explicit mapping of the **pinned command arm** into a finite declared
account/pool domain. The command still receives its native credential-scrubbed
environment and temporary HOME. The consumer does not authenticate physical
provider identity, load credentials from the profile, substitute a model or
construct an execution Binding. A wrapper's indirect provider/native-agent
paths still need their actual product contracts and authority. Possibly aliased
accounts can be conservatively joined through catalog `quota_pool_ids`; the SDK
owns atomic enforcement across those pools. Do not invent account labels or
provider-window applicability. Provider percentages remain independent vetoes.

The configuration has exactly these fields:

```json
{"schema_version":"caplab-retrieval-shared-admission/1","custody_root":"/absolute/retrieval-custody","valid_until":"UTC_ADMINISTRATION_EXPIRY_Z","spec_sha256":"sha256:NORMALIZED_SPEC_DIGEST","arms":[{"arm_id":"EXACT_ARM_ID","enrollment_path":"/absolute/arm-enrollment.json","enrollment_sha256":"RAW_FILE_SHA256_HEX"}]}
```

Compute `spec_sha256` with `caplab.retrieval.contracts.spec_digest` after
`validate_spec`. Cover every arm exactly once. Each enrollment file's hash is
of its exact bytes. Expiry must fit the SDK's selected windows and cannot be
moved to escape a refused assignment.

```sh
caplab retrieval admission-describe --spec /absolute/spec.json \
  --shared-admission /absolute/retrieval-enrollment.json
caplab retrieval run --spec /absolute/spec.json --output /absolute/new-run \
  --shared-admission /absolute/retrieval-enrollment.json
caplab retrieval admission-reconcile --spec /absolute/spec.json \
  --shared-admission /absolute/retrieval-enrollment.json
```

Python callers use `run_experiment(spec, new_output,
shared_admission=configuration_path)`. Injected adapters are refused with
enrollment. Describe initializes/retains native enrollment identity but never
reserves or launches. Reconcile validates retained assignment intent,
completion and output preimages before proposing SDK effects; it never
reserves, prepares or creates a child. Expired enrollment can reconcile and
project existing outputs; new assignments still enforce the original expiry.

The original per-assignment timeout includes admission work. Each command gets
one shared slot/right before possible outer creation. An actual Popen return
counts one outer child even if later exec fails. A constructor/preexec/exec
exception is unresolved, not zero. Positive closure entirely before Popen
returns an unused right. Lost SDK replies recover against the same native
assignment; a new random key is not a retry mechanism.

Enrolled commands use an owned bwrap session with a held, reuse-safe PID1
witness, `--die-with-parent`, an explicit one-byte stdin exec gate, read-only host root, writable temporary working
home, and hidden native custody/shared SDK home. Native output caps, raw request
and response bytes, timeouts and scoring remain. Creation and tree-end evidence
uses measured same-boot UTC/monotonic brackets, not a fabricated exact timestamp.
Native completion plus held namespace-init death is needed for settlement.
Missing witnesses, clocks, completion or closure remains held. Supervisor death
is not itself an accounting oracle, even when containment kills its descendants.

The evidence plan pins enrollment and command files; observations retain the
actual accounting result, custody path and `fresh-assignment` or
`retained-completion` basis. The loaded admission/custody/containment modules
are also source-pinned in runner provenance. Custody outputs are separately
retained exact bytes. An unfinished experiment is not rewritten: a new evidence
output may project already completed assignments under the same spec/pins;
unknown assignments become error attempts without launching. Native failure
outputs cannot be promoted to complete scored responses. Pin/intent/output
drift refuses recovery. Keep original custody roots and do not clone them to
mint rights.

Requirements are Linux bwrap and pidfd support plus SDK interval1, response2
and reconciliation3 capabilities. No provider calls, live cohort qualification,
account authentication or universal producer coverage follows from local fixture
success or installed source correspondence. The historical pool held-window
SIGKILL limit is unchanged. A stronger real retrieval control found that
`--die-with-parent` alone permits brief application execution after block-writer
EOF. This route also pins an isolated Python startup gate that reads one release
byte before execing the actual command. EOF exits without exec; the feeder sends
that byte only after actual admission/readiness, followed by unaltered request
bytes. The gate creates no second outer harness, daemon or resource ledger.
The original command executable remains the native subject. Dynamic libraries
and Python standard-library bytes remain host dependencies, not sealed code
custody. The retained crash controls observe actual PID1 death and absence of
application markers; missing durable closure still keeps SDK accounting held.
