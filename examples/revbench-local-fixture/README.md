# Revbench local-fixture first run

This example creates a persistent synthetic workspace and then uses the public
`prepare`, `execute`, and `score` commands. It does not read credentials, use a
provider, or make a network request.

## Prerequisites

- Linux with Python 3.12
- a `cc` command that can produce a static ELF executable
- the real executable `/usr/bin/bwrap`
- the repository dependencies installed as described in the root README

Run the commands from the repository root. Choose a workspace path that is new
or an empty real directory. Replace both authority values below with your own
local operator identity and the source of your authority to run this exercise;
the tool deliberately has no repository-owner default. These values become
durable registered evidence, so use nonsecret identifiers and do not put a
credential or token in either field.

```bash
WORKSPACE=/tmp/caplab-revbench-first-run-example
AUTHORIZED_BY='YOUR LOCAL OPERATOR IDENTITY'
BASIS_DELEGATION='YOUR AUTHORITY SOURCE FOR THIS SYNTHETIC EVIDENCE EXERCISE'
EXECUTION_DELEGATION='YOUR AUTHORITY SOURCE FOR RUNNING THE LOCAL FIXTURE'

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 \
  tools/caplab_revbench_first_run.py scaffold "$WORKSPACE" \
  --authorized-by "$AUTHORIZED_BY" \
  --delegation-source "$BASIS_DELEGATION" \
  --valid-for-seconds 3600
```

`scaffold` compiles the checked-in `fake_native.c` as a static ELF, copies the
source and binary into the workspace, and registers the executable, Binding,
protocol, corpus, case selection, and three mechanical evidence-basis
authorizations. It does not prepare a manifest or launch the executable. The
one-hour interval starts when the command runs and must still cover scoring.

Prepare the sealed two-case experiment through the public Revbench interface:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m caplab.revbench prepare \
  --spec "$WORKSPACE/spec.json" \
  --ledger "$WORKSPACE/ledger" \
  --output "$WORKSPACE/manifest.json" \
  --reference-output "$WORKSPACE/manifest-ref.json"
```

Now authorize only the exact prepared local-fixture manifest. This is a
separate effect from case selection and evidence-basis authorization.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 \
  tools/caplab_revbench_first_run.py authorize "$WORKSPACE" \
  --authorized-by "$AUTHORIZED_BY" \
  --delegation-source "$EXECUTION_DELEGATION" \
  --valid-for-seconds 900
```

The 15-minute interval starts when `authorize` runs. Execute the four blinded
attempts under Bubblewrap, then score their registered captures offline:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m caplab.revbench execute \
  --manifest "$WORKSPACE/manifest.json" \
  --execution-authorization-ref "$WORKSPACE/execution-authorization-ref.json" \
  --ledger "$WORKSPACE/ledger" \
  --output "$WORKSPACE/reviews.json"

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m caplab.revbench score \
  --manifest "$WORKSPACE/manifest.json" \
  --reviews "$WORKSPACE/reviews.json" \
  --ledger "$WORKSPACE/ledger" \
  --output "$WORKSPACE/measurement.json"

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 \
  tools/caplab_revbench_first_run.py inspect "$WORKSPACE"
```

`inspect` is read-only and safe to repeat. It validates the Binding and any
Measurement, then resolves the complete reachable graph of registered evidence
references. A complete run reports four planned, attempted, and usable
attempts. Catch, discrimination, anchor-hit, and conformance rates are `1/1`;
the false-alarm rate is `0/1`.

The workspace retains these main records:

```text
fixture/fake_native.c
fixture/fake-native
inputs/binding.json
inputs/protocol.json
inputs/corpus.json
inputs/case-selection.json
inputs/basis-authorization-*.json
spec.json
manifest.json
manifest-ref.json
execution-delegation.json
execution-authorization.json
execution-authorization-ref.json
reviews.json
measurement.json
ledger/
```

Separate workspaces have different Bindings because the executable's absolute
path is behavior-bearing and appears in registered configuration. Do not
expect byte-identical Binding or manifest documents across destination paths.

The Measurement is an observation. It contains no qualification status. This
example does not apply a qualification policy, issue a Claim, enable or select
a runtime, verify a provider route, or record acceptance.

## Refusals

The scaffolder refuses a nonempty or symlinked destination, a missing compiler
or `/usr/bin/bwrap`, and every live/provider option. The Revbench executor
refuses expired or mismatched authority and executable or Bubblewrap drift.
All output files are exclusive: rerunning a mutating command against an
existing output returns exit code 2 instead of overwriting it. For example, a
reused scaffold destination reports:

```text
error: workspace_must_be_empty
```

If scaffolding stops after creating a partial workspace because of a filesystem
failure, inspect that directory before removing it. Start again with a new or
empty destination; the tool does not clean caller paths automatically.
