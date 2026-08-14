# Quartermaster ingestion handoff v1

Status: the artifact boundary is implemented and verified with an independent
fixture consumer. A Quartermaster importer and runtime registry are not part of
CAPLAB.

## Input boundary

CAPLAB publishes one canonical `caplab-qualification-export/1` JSON document
with:

- one exact Binding and capability distribution;
- every selected append-only Claim in that series;
- Claim evidence and authority references;
- producer source-commit and package-byte identities; and
- the names and SHA-256 identities of the public schemas.

Create the artifact with `caplab qualification export`. Its normative shape and
semantic checks are defined by:

- [`qualification-export-v1.schema.json`](../contracts/qualification-export-v1.schema.json);
- [`qualification-claim-v1.schema.json`](../contracts/qualification-claim-v1.schema.json);
- [`qualification-records-v1.schema.json`](../contracts/qualification-records-v1.schema.json);
- [`qualification-schema-catalog-v1.json`](../contracts/qualification-schema-catalog-v1.json);
  and
- the [qualification contract](../contracts/caplab-qualification-contract-v1.md).

The export is an artifact, not a database API. It contains no credentials, raw
evidence bytes, host paths, runtime inventory, enabled state, availability,
health, quota, price, preference, placement, or Dispatch decision.

## Importer obligations

A Quartermaster importer must fail closed unless it can:

1. verify canonical JSON bytes and the export content ID;
2. load the named schemas from an approved local release, recompute every
   schema digest, and validate the export and each Claim;
3. recompute Binding, Measurement, policy, Claim, and export identities and
   their exact cross-references;
4. reject duplicate, dangling, cross-scope, self-referential, or cyclic
   supersession edges;
5. preserve the complete Claim, evidence references, source artifact digest,
   schema identities, and producer provenance without rewriting them;
6. make replay idempotent and reject an existing ID paired with different
   bytes; and
7. record the independent Quartermaster admission authority and delivery
   channel used to accept the artifact.

JSON Schema establishes shape only. The semantic checks above are required.
The fixture consumer at
[`tools/fake_quartermaster_consumer.py`](../../../tools/fake_quartermaster_consumer.py)
demonstrates independent validation without importing `caplab`. It is test
code, not the Quartermaster implementation or an admission authority.

## Runtime ownership

Importing a Claim makes it a preserved qualification record. It does not make
the Claim active. Quartermaster must separately own and record:

- which unsuperseded Claim, if any, its policy accepts;
- whether the exact Binding is installed, enabled, reachable, healthy, within
  quota, and permitted;
- administrative disablement and preference; and
- the capability-to-Binding projection supplied to Dispatch.

CAPLAB must not be queried for those live facts. Multiple unsuperseded heads
are a visible input to Quartermaster policy, not an ambiguity for CAPLAB to
hide.

## Exact follow-on

The next Quartermaster slice is an independent, append-only importer for the
v1 export and schema catalog. It should start from the fixture consumer's
public-contract checks, add a protected artifact-admission channel, persist the
unaltered artifact and Claim graph, and expose no active Binding until a
separate owner-authorized runtime-selection policy resolves the graph against
Quartermaster's own inventory.

Acceptance needs one clean-package integration test that exports from CAPLAB,
imports without the `caplab` package, replays idempotently, rejects each hostile
graph/hash case, and proves that import alone creates no enabled or selected
runtime Binding. A signature or otherwise protected delivery identity must be
specified before treating artifacts from an untrusted writer as authentic;
content hashes prove integrity, not who authorized publication.
