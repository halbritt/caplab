# Runtime storage bounds before native capture integration

Date: 2026-09-08. Baseline: `f30d4e1`. Primary-agent authority:
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Investigate the runtime storage boundary required by
[CAPLAB-79](decision-2026-09-08-caplab-79-capture-design.md). Create this record
and trusted, model-free probe scripts and reports under
`/tmp/caplab-storage-bounds-*`. Run at most six Bubblewrap fixture processes,
each with an unshared network, read-only system and fixture inputs, a one-MiB
private tmpfs, a combined stdout/stderr allowance of 200,000 bytes and ten-second
deadline. Each fixture may attempt at most 32 writes of 65,536 bytes, create at
most 128 empty files, or create a sparse file of at most 64 MiB logical length.
Do not copy the sparse file to host storage. Retain only bounded reports and
process capture. All tmpfs contents disappear with the owned namespace.

Inspect installed Bubblewrap help/source provenance and official kernel and
Bubblewrap documentation. Compare allocated-byte, inode, logical-size and
post-exit observations. Include a fixture that catches an allocation failure,
removes its scratch files and reports success, so final free space cannot be
mistaken for evidence that no limit was encountered. One fixture may make its
bounded writes in a newly created `/other` directory on Bubblewrap's private
root instead of the capped `/scratch` mount, testing mount coverage. No host
directory is writable in any fixture. No untrusted or native
harness code executes. Do not request elevated privileges, change host mounts,
services, cgroups or credentials, or use a live model.

Preserve all existing runtime/capture code, tests, world dossiers, historical
evidence, tracker state, unrelated `docs/designs/` and sibling worktrees. No
study admission, execution budget, code/oracle freeze, ranking, placement,
external message or push. Consolidate advisory evidence and delete exact named
advisory scratch after retaining provenance. Commit this record locally;
authorization expires at commit. Stop on a required effect outside this scope
or an unbounded fixture. Report unsupported substrate behavior rather than
falling back to a weaker claim.

## Question and current boundary

The existing process owner bounds retained stdout/stderr. Native collection
bounds what is copied after the process, but its contract explicitly does not
bound runtime storage before collection. The recent repair-capture integration
used small known payloads; it established no runtime-growth guarantee.

Bubblewrap 0.9.0 advertises `--size BYTES` for its next `--tmpfs` mount. The
question is whether that option alone can satisfy both storage containment and
CAPLAB's requirement to retain a truncation record and stop on capture limits.
This inspection selects no native launcher or campaign budget.

## Observations

Six fresh namespaces completed on Linux `6.8.0-138-generic`, Bubblewrap `0.9.0`
and Python `3.12.3`. The outer capture retained separate raw streams under its
200,000-byte limit and ten-second deadline. All six processes exited 0 with
complete process streams. That is process capture evidence, not proof that all
intended file writes succeeded.

| Fixture | Observed result | Consequence for the proposed guarantee |
| --- | --- | --- |
| Allocated writes in `/scratch` | Sixteen 65,536-byte files succeeded; the next write raised `ENOSPC`. Allocated usage reached exactly 1,048,576 bytes. | The requested allocation cap worked on this mount. |
| Empty files | All 128 creations succeeded with zero allocated data bytes; the reported inode capacity was 16,477,221. | A one-MiB byte cap did not create a correspondingly small entry limit. |
| Sparse file | A 67,108,864-byte logical file with one byte written at its end used 4,096 allocated bytes. | Allocated-byte containment does not bound logical bytes a collector may need to retain. |
| Caught failure followed by cleanup | The fixture reached `ENOSPC`, deleted its scratch files, then wrote `final.txt` containing `complete` and a newline. | A successful exit and restored free space cannot establish that no allocation failure occurred. |
| Clean success control | It wrote the same final file without the failed writes. | Its inspected final view equaled the caught-failure case. |
| Writes outside the capped mount | Thirty-two 65,536-byte files in `/other` succeeded, using 2,097,152 bytes on Bubblewrap's private root. | A cap on `/scratch` does not cover other writable mounts or paths. No host directory was writable. |

The equal final view compares message text, path/logical size/allocated size,
file-content hash, and filesystem capacity/usage counters. It does not compare
inode identities, timestamps or every possible kernel observation. The probe's
separate `private_fixture_observation` deliberately records the caught error as
known test truth. A real producer need not expose that truth; this experiment
does not claim that the full retained probe stdout concealed it.

These observations agree with the documented distinction: tmpfs `size` limits
allocated bytes, while `nr_inodes` is a separate mount parameter.
[Linux kernel tmpfs documentation](https://www.kernel.org/doc/html/latest/filesystems/tmpfs.html)
Bubblewrap 0.9.0 applies `--size` to its next tmpfs operation and constructs
that mount's options from mode and size.
[Bubblewrap 0.9.0 source](https://raw.githubusercontent.com/containers/bubblewrap/v0.9.0/bubblewrap.c)
The inspected upstream source is version-matched reference evidence, not an
attestation that the installed distribution binary has identical source.
The probe separately records the installed executable hash.

## Inference and next implementation boundary

**Do not adopt `--size` alone as a complete runtime-storage or capture gate.**
It is a useful allocation containment mechanism within its mount. These
counterexamples rule out the stronger guarantee without changing its useful
bounded meaning. No existing CAPLAB owner claims that stronger guarantee, so
this is a design prerequisite finding rather than a repaired production bug.

A native launcher needs separately verified answers for:

1. Coverage of every writable filesystem, including private root, task,
   runtime, temporary and shared-memory surfaces; no unbudgeted alternate path.
2. Aggregate allocated bytes and inode/entry growth, with logical capture size
   separately bounded by the retained inventory owner. Repeated or deleted
   writes and sparse files must not be confused with the final logical size.
3. An independently retained, lasting indication of an enforced limit, or
   another justified completeness mechanism that cannot infer success from the
   process exit or final free space. Polling final usage cannot solve the
   demonstrated caught-error case.
4. Preservation of permitted outputs before destroying ephemeral storage,
   outside the subject's writable boundary, including abnormal termination.
   The six disposable probes did not implement that native artifact handoff.

The existing bounded collector remains necessary. A block cap cannot replace
its logical-byte and entry checks, and the collector cannot retroactively limit
runtime allocations. A future scoped implementation must combine the resource
and custody requirements rather than treating either as evidence of the other.
No filesystem backend, inode parameter, limit-detection mechanism or numeric
campaign budget is selected by this inspection.

## Verification and custody

`/tmp/caplab-storage-bounds-probe.json` contains exact commands, process receipts
and hashes, observed counts, versions, binary identity and fixture identity.
Raw process custody is `/tmp/caplab-storage-bounds-probe-a6ive4nz/`. The driver,
fixture and readable output remain under the `/tmp/caplab-storage-bounds-`
prefix. `checks.json` records successful assertions for all six expected
outcomes and the equal inspected final views. `sources.json` identifies the
downloaded official sources and the seven unchanged CAPLAB source/contract
files by commit, path, length and hash.

No sparse payload was copied to host storage. Namespace teardown removed its
temporary files. No actual native harness, model, account or historical study
artifact was used. These are new development probes, not representative episode
costs, independent validation or study evidence. Runtime source and tests remain
unchanged, so the full suite was not rerun. No roadmap item is closed.

## Advisory disposition and closure

The retrieval-state gate passed against the validated Pincite release at
`/home/halbritt/.local/share/pincite/release`, release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet:
`pkt-214b460aa7085617`, content SHA-256
`214b460aa7085617855b40af95b65571863c966a8cc8923b4766d384377fd74e`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`.

The question matched no precisely nominated concepts; the packet supplied
baseline engineering guidance. OS-specific findings come from the retained
experiments and official sources, not from a doctrine authority claim.
Applied `universal-repository-contract-precedence` to CAPLAB's separate storage
and capture requirements, `universal-evidence-before-intervention` to testing
the candidate guarantee before adopting it, and `universal-no-change-option`
to retaining current owners pending a sufficient launcher design. Citation
classification is retained with the consolidated verification manifest.

Nine unmet obligations are nonmaterial to this bounded inspection:

| Concept | Unmet requirements | Scope reason |
| --- | --- | --- |
| implementation-placement-by-ownership | recurring change evidence when available | No production owner or interface is added or moved. |
| implementation-repository-language-conformance | CI and build matrix; formatter and static-tool configuration | No toolchain or platform change; this local substrate observation is version-scoped. |
| python-repository-shaped-idiom | Python and dependency version matrix; formatter linter and type-checker configuration | No dependency or formatter change and no cross-version compatibility claim. |
| python-runtime-static-boundary | annotation maintenance cost; checker and trust-boundary evidence; configured checker and Python version | No static checker, annotation or trust-boundary implementation is selected; only fixed trusted probes execute. |
| python-text-bytes-boundary | representative non-ASCII data | The storage experiment uses fixed ASCII payloads and numeric counters; it changes no text decoding or normalization. |

`/tmp/caplab-storage-bounds-verification.json` consolidates source/probe hashes,
typed evidence, expected-outcome checks, citation classification and the exact
scratch cleanup list. Eleven named advisory scratch files are removed after
consolidation; all six process captures, scripts, reports and official-source
snapshots remain. There is no live process to wait on or restart.

This record is committed locally. No runtime repair, independent acceptance,
study readiness or roadmap completion is claimed. The probe authorization is
consumed and expires at commit; additional probes or implementation require a
new scoped record under the existing delegation. The CAPLAB goal stays active.
