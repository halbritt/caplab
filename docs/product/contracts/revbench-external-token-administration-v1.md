# Revbench external-token administration, version 1

This contract describes the additive, separately named Revbench administration
selected for construction in
[the external-token decision](../../records/decision-2026-10-03-revbench-external-token-administration.md)
and
[the direct-Bubblewrap decision](../../records/decision-2026-10-03-revbench-external-direct-bubblewrap-bundle.md).
It is source and synthetic-test construction only. It grants no live
administration, registration, credential access, provider effect or host
policy change, and it qualifies nothing.

## What is new, and what is not touched

The new method has its own bundle policy
(`src/caplab/revbench/contracts/codex-native-bundle-external-v1.json`,
policy id `codex-terra-max-revbench-live-external-token-direct-bwrap-v1`,
SHA-256 `CODEX_NATIVE_EXTERNAL_BUNDLE_POLICY_SHA256` in `caplab.revbench.codex`),
its own closed public credential profile
(`caplab-revbench-codex-external-credential-profile/1`) and its own private
anchor document. A Binding that uses it has new bundle, runtime, command and
Binding identities and a new clean-source apparatus.

Unchanged and still addressable: the original bundle policy bytes
(`codex-native-bundle-v1.json`, SHA-256 `2113548…a68e`), the original profile
schema and its validators, the external delivery API's default marker policy,
every registered historical member, Binding, manifest and apparatus receipt, and
the original launch path (invocation-owned private stage plus loader). The new
method is never selected by a default, a profile name or a policy name: a Binding
selects it only by registering a bundle policy exactly equal to the installed
pinned external document, and a profile or command that does not agree with that
policy is refused at preparation.

The native subject is the same: Codex 0.147.0 (the pinned 258,278,208-byte static
executable), GPT-5.6 Terra at maximum effort, the configured direct OpenAI
route, the same tools, network declaration (`--share-net` for the review only),
read-only sealed credential mount, fixed environment, response schema, public CA
and resolver data, and the same nonrollback one-shot custody. Qualification
remains advisory for configured routes; nothing transfers from earlier Bindings.

## Credential method

The delivered document comes from
`caplab.codex_external_credential.open_codex_external_credential` version 1 with
the explicitly selected `credential-private-text/v2` marker policy: `auth_mode`
is `chatgptAuthTokens`, the refresh-token key is kept with an empty value, and the
other token strings are unchanged. The review command adds one setting,
`-c cli_auth_credentials_store=file`, so the sealed read-only file is the initial
credential store; an ephemeral store, a host keyring and host configuration are not
used. No external refresh provider or hook is added. Built-in OAuth refresh is
suppressed in Codex source for this mode, which does not mean zero HTTP retries or
exactly-once provider delivery.

Expired identity-token metadata is permitted only by this profile; its issuer,
audience, issue-time, account, subject and source-stability predicates are the
delivery API's, unchanged. The original Revbench profile still refuses an expired
identity token. Local unsigned checks are not provider authentication.

### Public profile and private anchors

The public profile names the method, marker policy, initial store and lifetime
rule and nothing else: no source path, token metadata, whole-cache hash or raw
private claim. Its fields are checked against the pinned policy's
`credential_delivery` description.

The expected source, account and subject SHA-256 values are supplied separately
in a private anchor file, a second 0600 single-link direct child of the same 0700
credential root, mapped with `--credential-anchor PROFILE=FILENAME` (file names
only on the command line). It is a closed JSON document
(`caplab-revbench-external-credential-anchors/1`) bound to the public profile id.
The runtime refuses an anchor file configured under the credential source's own name (a
link to the source cannot stand in: the anchors file must be a single-link regular file
opened without following links), is oversized, malformed, duplicated-key, of another profile, or unreadable,
each with a fixed code that carries no path, hash or file text. Expected values are
never derived from the file being validated.

### Lifetime and lease timing

The required access lifetime is the whole seconds, rounded up, from a fresh UTC
reading to the retained execution deadline (which already bounds the version probes
and every native process), raised to one second only when positive, and refused when
the deadline has passed or exceeds the delivery API's 86,400-second maximum. It is
never truncated and never extends authorization; monotonic process and total
deadlines are unchanged.

The lease is taken after the durable overall one-shot intent and before any version
or provider-capable subprocess. A refusal consumes and seals the same fresh slot
(`preflight-refused`), and recovery cannot relaunch after uncertainty. The lease
exposes a descriptor valid only while its owning context is open and a fresh
exact-byte stream guard per call; every durable stream gets its own guard, a
quarantined capture is unavailable, never an empty success, and refusal codes are
fixed (no source path, claim or exception text). The checks of the original seam for
a direct-child source, a 0700 credential root, owner, mode 0600, one link,
non-following open, stability and size are kept; custody disjointness is the
runtime's, unchanged.

## Direct Bubblewrap and its pinned host closure

The new bundle runs the root-controlled `/usr/bin/bwrap` in place, under that
path's existing host permission, with the original outer flags and an empty
environment. It stages, writes and removes nothing, and adds no AppArmor grant,
loader grant, sysctl change or install. It pins:

* the adapter (SHA-256 `e3189038…0f71`, 72,160 bytes), its `PT_INTERP` interpreter,
  and every library its transitive `DT_NEEDED` closure loads, each with the
  distribution symlinks and directories on its path (owner, group, mode, link
  target) and the final file's SHA-256 and size;
* the loader inputs that can change resolution: the loader-cache entries of exactly
  those libraries (including any hardware-capability variant), the absence of
  `/etc/ld.so.preload`, and the absence of `RPATH`/`RUNPATH` in every member. The
  empty launch environment closes `LD_LIBRARY_PATH` and the other loader
  variables; the closure is stated, not inferred from the adapter hash.

This is the host's own build, not the earlier recovered closure: the adapter differs
from the old pin in 56 of 72,160 bytes and the host loader and libc differ from the
old pinned bytes. A host package update therefore requires a separately prepared,
reviewed bundle; it is refused, not re-pinned, and nothing falls back to whatever
version is present.

**Trust assumption (explicit).** Direct ELF loading cannot give an atomic
descriptor snapshot of host dependencies against a concurrent privileged update. The
bundle selects the assumption that privileged host maintainers do not change this
closure during an authorized administration. It does not resist a malicious root and
is not proof that an unobserved privileged change did not happen. The assumption is
stated in the policy, in `caplab.revbench.host_closure`, and in the execution
apparatus receipt (`protocol.host_closure_trust`).

Immediately before each launch (`_run_owned_process`), `verify_host_closure`
re-resolves every pinned path and refuses a missing, changed, group/other-writable,
non-root-owned, setuid, file-capability-bearing or ambiguously resolved member with
a fixed code `host_closure_<category>:<member id>`. Runtime code reads and checks
the protected host files; it never writes, publishes, overwrites or deletes them.

### Retained evidence of the check

Both outcomes are written to custody before any process can start, as
`host-closure-check.json` beside the process streams (`caplab-revbench-host-closure-check/1`:
process id, SHA-256 of the pinned closure description, member count, time, result
`verified` or `refused`, and the fixed refusal code). A refusal completes the process
as `not-invoked` / `preflight-refused`. Recovery reads the record back, including for
an uncertain capture. The process receipt carries it as `host_closure_check_ref`
only for a bundle that pins a closure. Scoring requires it before an `invoked`
process, refuses it for a bundle that pins none, and checks that it names this
process and the pinned closure, was made before launch, and agrees with the receipt
(a refusal only ever precedes a `not-invoked` stop).

## Evidence and apparatus

The apparatus receipt keeps pinning the original bundle policy digest and, for
receipts generated from this revision, also names the external policy digest and the
host trust assumption; a receipt with the original three protocol fields still
validates. The published `revbench-live-native-v1.schema.json` gains the external
profile, the external policy as a second exactly pinned document, the optional
receipt field and the check record, and its schema-catalog digest changes
accordingly; documents of the original method validate as before.

## Verification status and limits

Synthetic tests with fabricated credentials, a fabricated host tree and a fake
process runner cover: original policy bytes, defaults and replay unchanged; the
external policy differing only as selected; closed profile and agreement refusals at
preparation; private anchors; lifetime rounding and refusal; lease descriptor
lifetime, source immutability and per-stream guards; marker-policy categories versus
private equal occurrences; post-intent refusal sealing the slot; every closure
mutation class; retained check, drift, crash recovery and scoring refusals;
launch-plan and policy substitution at scoring; schema validity of the evidence;
apparatus identity stability when the adapter is imported; and the CLI.

The live process runner's cleanup, shared with the original method, now refuses a
process-group identity that is not a plain integer greater than one before any signal or
wait (a mock's coerced value or `1` would otherwise broadcast to every permitted process),
and closes every owned pipe and the capture even when signalling or closing fails, keeping
the primary exception reachable. Its regressions and the mutation checks run with every
signal primitive intercepted.

Not verified and not claimed: that the pinned Codex binary parses the delivered
document or honors `cli_auth_credentials_store=file`, read-only delivery in a live
mount, usability of a real credential's capture under the v2 marker policy, any
provider behavior, and the host namespace permission itself (separate work; this
bundle neither grants nor modifies it). The host's current `/usr/bin/bwrap` is not
the bytes pinned by the original bundle, so the original policy's host-byte
comparison test fails on this host independently of this change. Exact-text
quarantine does not detect transformed secrets or zero memory.

## Reopening

Reopen for different tuple or native bytes, a different credential API or marker
behavior, different private/public identity placement, refresh or writeback, weaker
lifetime rules, a different adapter or loader-closure model, new host privileges,
altered custody or retry semantics, a new network or tool surface, or stronger
authentication, secrecy or qualification claims.
