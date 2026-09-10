# Historical project dependency and test readiness

The primary agent authorizes bounded local preparation under ADR 0026 for
reviewer-ranking-001. Copy the exact regular-file trees of these Council
commits with commit/tree/blob/hash provenance into owner-private
`reviewer-ranking-001/development/dependency-readiness-1` custody:

- `de4a6d4d195ea0054e275548d49ef12fb5d13d0e`
- `9c66a76836245fbc8d203812a4a36f475341ce0e`
- `c60cb4694a97b0f3151fdc48abfbea2e631ac1fb`
- `c1526c8552ccfa6236c01988aa141d0705eb5d7f`

Create disposable working copies, preserving the source snapshots. Run at
most four `npm ci --ignore-scripts --no-audit --no-fund` installations, each
bounded to 180 seconds, using the exact committed manifests and locks.
Download only registry.npmjs.org dependencies named by those locks, without
owner npm credentials/configuration. Record Node/npm, manifest/lock and
installed-file identities. Do not change versions, repair locks, run package
lifecycle hooks or modify the Council checkout.

After installation, run the original `npm test` once per prepared revision,
at most 180 seconds each, in a fresh network-disabled namespace with empty
home/environment and writable disposable build/test directories. No owner
credential, production service or native model call is authorized. Test
failures and missing prerequisites remain explicit. Source changes caused by
scripts invalidate preservation and must be retained, not silently repaired.
Forward `--maxWorkers=2` to Vitest uniformly to bound test-worker concurrency;
retain the original package test/build scripts and record the exact command.

Maximum four installations and four test launches; 1500 seconds total after
preparation. Shared package cache is allowed; workspaces and test homes are
separate. Preserve all plans, logs, outcomes and dependency inventories. Stop
on lock/source mismatch, non-registry dependency URL, credential requirement
or deadline. No consumed invocation is replayed. Expiry: slot consumption or
2026-09-11T00:00:00Z. This is readiness and behavior evidence, not a reviewer
score, source-defect verdict or ranking acceptance.
