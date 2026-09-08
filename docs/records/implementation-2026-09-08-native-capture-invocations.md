# Identify prospective native capture invocations separately

Date: 2026-09-08. Baseline: `31db89f`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `src/caplab/native_capture_invocation.py`, a prospective invocation builder,
its tests and a versioned contract, plus this record. Use the existing canonical
native-agent policy and validator without changing them or any frozen subject,
manifest, command, launch path or historical evidence. Authorize synthetic
prompt/path inputs, pure command construction, local CLI help/version reads,
focused checks, a model-free integration probe through the bounded process/task
capture API, `make check` and a local commit. No native inference, model spend,
authentication or credential reads, session inspection/copy, historical
admission/rescoring, tracker writes or external messages. Preserve `docs/designs/`,
other worktrees and services. Retain verification evidence and remove only named
doctrine scratch after recording its receipt. Authorization expires at commit.
Stop if a requested profile cannot keep the canonical model/harness/effort tuple
or if execution requires broader effects.

## Decision and scope

The legacy validator permits a bounded list of complete command suffixes. Its
review configuration disables native persistence, while the selected CAPLAB-79
capture design requires persisted sessions and additional exposed events. The
existing containment launcher also lacks an episode-specific persistent runtime
mount. Do not broaden the old suffix allowlist: doing so would silently expand
what old frozen callers can execute. Select a new pure builder with explicitly
identified capture profiles and a separately hashed invocation plan.

The builder first validates the selected canonical native model/harness/effort
and version command, then constructs one fixed prospective capture profile.
It emits the full argv, explicit environment, working directory, exact prompt
hash, declared output locations and the profile/plan hashes. These are planning
and configuration records, not a complete Binding, authorization or evidence of
an executed native process. Runtime paths name the future execution namespace;
this builder does not create mounts, directories or credentials.

Keep native tools and permission behavior explicit: the Codex profile uses the
existing workspace-write mode; the Claude profile retains the legacy skip-
permissions mode and therefore requires external containment. These are new
behavior-bearing capture configurations. No old study becomes comparable merely
because the base model/effort is the same. Additional capture support must be
observed on the exact installed harness/model/account before live use.

The intended adapter path is now concrete: build this plan, freeze and verify
its executable/configuration/containment inputs, provide a private persistent
runtime, run through bounded task/process capture, retain/link native sessions
and diagnostics, then inspect custody and apply the study's evidence gates.
This task implements command construction and verifies its connection to the
bounded capture API with a local argument-observer fixture. It does not claim
that the remaining adapter or native session collector already exists.

## Execution and focused verification

Added one builder and immutable input context. The current native policy bytes
are pinned independently of the existing Revbench policy constant; the builder
checks the actual `native-agent-systems.json` hash, constructs and validates the
base subject using the existing validator, and then applies one fixed new
profile. It returns fresh maps/lists and does not mutate shared input state.
Profile identity covers the fixed argv/environment/location templates; invocation
identity additionally covers the concrete prompt, paths, session and base policy.

The profile definitions remain local to CAPLAB's new configuration owner.
No generic plugin layer, caller-supplied command override or native proxy is
introduced. The dependency direction is new builder to existing subject-policy
validation. Existing launchers are not made to depend on this prospective API.
No-change would leave the current capture design without a policy-preserving
command path; widening old suffixes would weaken frozen callers' boundary.
Future adapter integration must explicitly select this new API and bind its
result rather than silently transforming an old launch.

Six focused tests passed in 0.156 seconds:
`/tmp/caplab-native-invocation-focused.log`. They cover both native tuples,
retained permission modes, persistence/event options, explicit environments,
invalid namespace paths/prompts/session IDs/policy hashes, independent returned
objects and deterministic complete-plan hashes. Old policy validation still
rejects the new capture suffixes. Prompt text beginning with an option and
containing Unicode, newline and shell syntax reaches a local Python argument
observer unchanged as data; bounded task capture retains its stdout and the
custody verifier checks the result. No native harness is impersonated or run by
that observer, and the fixture is not an agent measurement.

The first development test import failed because a non-ASCII character was
written in a Python bytes literal. The fixture was corrected to explicit UTF-8
encoding before verification. This is not a pre-existing product defect or a
red/green regression claim.

Source hashes and unused-import checks are retained in
`/tmp/caplab-native-invocation-source-check.json`; no unused direct imports were
found. The source check verifies that existing native policy, legacy launchers,
and bounded capture producers are byte-identical to `31db89f`. Python 3.12.3
is the tested local interpreter. No dependency, formatter or CI change occurs.

Native help/version reads completed without an inference call: Codex CLI
0.153.4 and Claude Code 2.1.263. These are current inspection observations,
not selected study versions. The prior CAPLAB-79 record observed Claude 2.1.260;
that older inspection is not current compatibility evidence. The help files
advertise the selected capture flags. Official documentation was opened for
persistence, summary controls and Claude stream/debug/session options; URLs are
linked from the [contract](../product/contracts/native-capture-invocations-v1.md).
Support for actual event/session/diagnostic emission and detailed summaries
remains unverified on any model/account.

Two example plans are retained in `/tmp/caplab-native-invocation-example.json`.
Their profile hashes are:

- `codex-persisted-events/1`:
  `36af328a060250ca406d99b5a04e23285347689ec45550e2738cf025ffb96e4f`.
- `claude-persisted-events/1`:
  `24560c3f54f739f505c6ebb4d2261e865d199d3bedfd34b54934258fec19eb33`.

The corresponding invocation hashes are
`8212ee33fceb49be0ae2100fa906c1229a739ee92ae08bc71ea8e55ef6eda9a4` and
`ba665f6d651c3de38a8e9f64d1de79aa764af73b052a327f9a22a7a83dd4201e`.
These plans authorize nothing. They contain no credentials or historical task
content and do not claim complete native capture.

## Doctrine receipt

The release retrieval-state gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`. Final packet:
`pkt-70b6c643d79eb40a`, content SHA-256
`70b6c643d79eb40aec770b837f65b628e250ccd747b3bf596daf95db92015b30`.
One evidence-gathering pass supplied five typed records. Four citations were
classified as `valid-packet-citation`: `universal-preserve-behavior-by-default`
for leaving the old suffix boundary intact; `implementation-placement-by-ownership`
for the prospective configuration owner; `python-text-bytes-boundary` for exact
UTF-8 prompt handling; and `agent-conduct-authority-bounded-action` for explicit
non-authorizing plans. The packet reports baseline/routed guidance without a
precisely nominated concept; it is advisory, not a native protocol specification.

Six remaining obligations are nonmaterial to this implementation:

| Concept | Exact unmet requirements | Reason |
|---|---|---|
| `implementation-placement-by-ownership` | recurring change evidence when available | The accepted prospective capture requirement supplies the need; no historical change-frequency or coupling claim is made. |
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | No tooling change or cross-matrix conformance claim; current local tests establish the declared behavior. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | No formatter/checker policy change or static conformance claim. |
| `python-runtime-static-boundary` | annotation maintenance cost; configured checker and Python version | Local Python is recorded; no configured checker or annotation-cost claim is made. Inputs are validated at runtime. |

## Completion checks

`make check` passed 1,014 tests with four skips in 156.400 seconds:
`/tmp/caplab-native-invocation-make-check.log`. Source/test hashes remained
unchanged after that run began. The documentation guard checked the actual API,
fixed profile fields, hash boundaries and the limits of help-only verification.
The prose pass replaced broad capture claims with prospective command semantics.

The consolidated receipt is `/tmp/caplab-native-invocation-verification.json`.
Eleven named doctrine scratch files were removed after retaining packet,
obligation and citation receipts. Help/version files, examples and test logs
remain. No tracker, frozen instrument or historical capture changed. The next
required implementation is a private persistent runtime and bounded, stable,
episode-specific session/diagnostic collection tied to the native output ID.
The full native adapter and the CAPLAB goal remain incomplete.
