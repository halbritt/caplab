# Historical project dependency readiness

The four Council snapshots now have their exact lockfile dependencies, and
their original build commands complete. Full test readiness is unresolved.
The selected effort-change pair has the same 134 failed test headings, which
prevents treating those failures as evidence against that change.

This is preparation for useful reviewer task access. Test counts are not
reviewer scores, defect counts, or whole-change clean labels.

## Scope and execution

| Role | Exact commit |
| --- | --- |
| Introduction base | `de4a6d4d195ea0054e275548d49ef12fb5d13d0e` |
| Introduction change | `9c66a76836245fbc8d203812a4a36f475341ce0e` |
| Effort base | `c60cb4694a97b0f3151fdc48abfbea2e631ac1fb` |
| Effort change | `c1526c8552ccfa6236c01988aa141d0705eb5d7f` |

The [first authorization](authorization-2026-09-10-reviewer-dependency-readiness.md)
covered four isolated `npm ci` installations and four tests. Lockfile v3
records contain 121 package entries for each introduction revision and 314
for each effort revision. Every resolved package URL names the public npm
registry and includes an integrity value. Installs disabled lifecycle scripts,
audit and funding calls, used empty npm configurations and an isolated cache,
and completed successfully. Node was v24.19.0; npm was 11.17.0.

The first test namespace lacked `/var/tmp`, `/sbin/ldconfig.real` and localhost
resolution. The [second authorization](authorization-2026-09-10-reviewer-dependency-readiness-2.md)
corrected those paths and supplied private offline npm caches. All four basic
namespace preflights passed. It preserved first-batch results and copied only
dependency files named by the successful installation inventories, validating
bytes and symlinks before copying. It downloaded nothing further.

Each test invoked the original `npm test -- --maxWorkers=2` with networking
disabled, private source workspaces, no owner credentials and a 180-second
process limit. Every test process exited normally with status 1; none reached
the outer deadline. The two effort runs each took about 178 seconds including
their builds.

| Snapshot | First namespace: passed / failed | Corrected namespace: passed / failed |
| --- | ---: | ---: |
| Introduction base | 87 / 2 | 88 / 1 |
| Introduction change | 202 / 82 | 228 / 56 |
| Effort base | Test startup failed | 655 / 134 |
| Effort change | Test startup failed | 655 / 134 |

## Remaining environment and interpretation gaps

The introduction base's remaining failure is a porcelain PTY command timing
out. Most failures in the later snapshots report that the nested executor's
`slirp4netns` exited before readiness. Other failures include missing historical
Claude/Codex installations, package-install cache misses, process identity
errors, fixture comparisons and a host-service delivery timeout. Those latter
assertions have not all been causally classified. Do not declare every failure
an environment defect merely because several share that explanation.

The two effort revisions have identical ordered lists of all 134 failed test
headings. This corroborates a shared baseline in this namespace; it does not
establish all untested behavior or complete equivalence. The dedicated
[effort witness](verification-2026-09-10-reviewer-effort-control.md) remains the
evidence for that change's named preservation properties.

Historical test fixtures expect older native CLI installations, including
Codex 0.147.0. These are task dependencies, separate from the reviewer subject
Codex 0.153.4. Installing or substituting a test fixture would not redefine the
reviewer's native identity. Full comparative execution still needs an explicit
decision about supported tests and the complete tool environment.

## Custody and checks

Private roots under
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/`:

- `dependency-readiness-1`: plan SHA-256
  `d2ac2f152cb3f28f4b3768721d67590a2da5c41467dd4b945615a480824c6252`.
- `dependency-readiness-2`: plan SHA-256
  `ef1a06c89e33d56f02d06c932aa3c2bbfe0b2b1e7b3ffdcc4730fecf2516df06`.
- `dependency-readiness-2/verification.json`: SHA-256
  `f37356836e9eb15d550b917cbf7a4fe058dac3b55db1b9b024e774575d949b8f`.

Both roots retain frozen runners, exact source provenance and dependency
inventories. Every slot retains command, PID/start identity, stdout, stderr
and terminal status. The verification receipt hashes those files, extracts
the recorded totals and compares the effort failures. All original source
files, installed dependency bytes/symlinks and 1,610 inventoried npm files
still match their recorded hashes. Newly generated test/cache files are not
part of the installed dependency inventory. File modes were not pinned by
that inventory. No native reviewer, provider or production service was called.
