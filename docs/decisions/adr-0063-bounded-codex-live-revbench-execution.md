---
id: adr-0063
artifact_type: architecture-decision-record
title: Bounded Codex live Revbench execution and custody
status: decided
decision_owner: primary-agent
decision_authority: adr-0026-and-repository-owner-build-task-2026-08-15
created: 2026-08-15
decided_at: 2026-08-15
supersedes:
  - adr-0062-live-provider-refusal
superseded_by: null
affected_contexts:
  - caplab-revbench
  - caplab-qualification
related_specs:
  - caplab-qualification-contract-v1
  - native-agent-systems-v1
related_plans:
  - caplab-tuner-merge-build-task
---

# Bounded Codex live Revbench execution and custody

## Context and authority

ADR 0062 kept benchmark execution in CAPLAB but initially refused every live
provider because no provider-specific sealed launcher or durable streaming
custody seam existed. The repository owner directed CAPLAB to own benchmark
execution but supplied no registered delegation or authorization for a live
provider effect. The coordinator therefore limited construction verification
to provider-free tests. Under the product-decision delegation in ADR 0026, the
implementing coordinator and delegate selected this bounded Codex 0.147 slice
and its construction boundary. ADR 0039 continues to define the
behavior-bearing subject and forbids proxy substitution.

Neither the owner task nor this delegated implementation decision authorizes a
benchmark administration. A future live effect still requires its own
registered, exact, time-bounded execution delegation and authorization. Green
tests verify the implementation; they do not accept it, qualify the Binding, or
authorize a provider call.

## Decision

Revbench v1 supports exactly one live-native profile in addition to the local
fixture: the `codex-terra-max` tuple from the frozen native-agent-systems
contract, using Codex CLI 0.147.0, GPT-5.6 Terra, maximum effort, and the direct
OpenAI Responses configuration. Preparation requires `configured-route` with
no observation timestamp. It records configured intent, not provider-observed
routing, and remains advisory under qualification v1.

The additive repository-owned bundle pins the Codex executable and version
streams, exact command and configuration flags, Bubblewrap and its userspace
closure, ordered containment templates, fixed environment, response schema,
minimal public DNS and nsswitch assets, CA bytes, hostname, and evidence
limits. The subject runs in an empty-root namespace without a host shell,
filesystem, user configuration, rules, plugins, MCP servers, or web-search
surface. Shared networking is available only as the declared Codex transport
dependency. Kernel, CPU, `/proc`, namespace support, and the host kernel TCB
are observed apparatus context rather than sealed bundle members.

Live authority binds the manifest, Binding, native contract, commands, limits,
interval, exact clean-source execution-apparatus receipt, and custody-domain
identity. The no-effect `prepare-live-runtime` operation creates or reads the
custody-domain identity and registers the apparatus receipt without reading a
credential or starting a provider process. Fresh execution is supported only
through the exact isolated system-Python source entrypoint. It rejects site
hooks, virtual environments, extra interpreter flags, package symlinks,
untracked package members, source-root shadowing, a dirty checkout, apparatus
drift, and a different custody domain before a new launch.

The private custody root is owner-controlled, durable, nonrollback, and
disjoint from the repository, package, evidence ledger, and credential root.
Manifest/case/arm/assignment/process identities, rather than authorization ID,
key one-shot effect tombstones. Intent and streams are synchronized before
effect or evidence boundaries. Recovery retains durable prefixes and never
retries an incomplete or uncertain outer launch, even after authority expiry.
Replication requires a new manifest/experiment identity.

Credential administration remains outside evidence. A registered nonsecret
profile binds operator-declared hashes of high-entropy account and subject
claims but does not authenticate them. One dedicated owner-mode source is read
through a nonblocking descriptor into an anonymous sealed memfd and mounted
read-only. Refresh and writeback are forbidden. An exact-scalar streaming gate
withholds token, account, subject, and decoded private/custom claim material
before durable writes; a match produces a privacy-quarantined infrastructure
receipt with no public stream bytes.

Live evidence registers the overall intent, every process receipt, complete
raw streams where safe, version observation, native output, raw-to-derived
response record, capture, attestation, attempt, and reviews. Scoring resolves
and recomputes the whole graph, including assignment adjacency, effect/process
identities, launch plans, apparatus, authorization, stream digests, JSONL state
machine, and deterministic oracle. Complete terminal JSONL with an invalid
agent response is subject failure. Transport ambiguity, process failure,
limits, quarantine, or uncertain recovery is infrastructure failure.

## Limits and consequences

The custody guarantee is at-most-once CAPLAB outer containment launch within
one intact nonrollback root. It is not exactly-once provider delivery, does not
control Codex-internal HTTP retry, and cannot survive custody rollback, loss,
or malicious same-user mutation. Starting Bubblewrap does not prove that Codex
or a provider request started. Credential claims are locally parsed but not
signature-verified. Exact-scalar quarantine does not detect transformed,
encoded, or fragmented leakage. The dynamic containment adapter and subject
still depend on the observed host kernel.

CAPLAB continues to own experiment execution and evidence. Qualification owns
Measurement and Claim semantics. Quartermaster remains an artifact consumer;
this decision creates no runtime registry, Dispatch, fleet, training,
deployment, placement, or acceptance authority.

## Verification and reopening

Standing verification covers exact Binding and configured-route validation,
blinding, real subprocess custody, launch-plan swaps, stream limits, monotonic
deadlines, crash windows, no-retry recovery, credential rotation, cross-chunk
quarantine, secret-free public evidence, deterministic scoring, selective
omission, schema/catalog/package identity, isolated source invocation, and
archive/source provenance. Tests use synthetic subprocess seams and make no
provider/model call or read of the operator's global credentials.

Reopen before adding a tuple, provider, harness version, credential method,
writable credential mount, network/tool surface, retry, different custody
identity, archive-installed live executor, observed-route claim, provider
receipt, or stronger delivery/secrecy statement. Those are new product and
authority decisions, not compatible configuration changes.

## Doctrine receipt

Design used advisory Pincite packets `pkt-539571eaaeff4760` (content SHA-256
`539571eaaeff476059dfdbe90393d047610373dc2e9e5d0be41f0241a8716772`)
and `pkt-dd935b7ab4a5a108` (content SHA-256
`dd935b7ab4a5a108d23c9e17bc14e83d24a9b1a3a2dc17c5c4604666dc9c03bb`).
Both came from validated corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`, and
release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.

Structured citation classification against index SHA-256
`0772a6d3a482dde28e3c38f6f2169dd551ca147300d044bd0d8473b6671e7b74`
classified all six cited concepts as `valid-packet-citation`:
`universal-repository-contract-precedence`,
`universal-evidence-before-intervention`,
`agent-conduct-authority-bounded-action`,
`implementation-explicit-failure-policy`,
`implementation-fail-fast-or-recover`, and `operations-least-privilege`.
Repository-owner direction and ADR 0026, not doctrine, supply decision
authority.
