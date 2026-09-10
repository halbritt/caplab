# GitHub release-loss development witness

The original ai-newsroom scanner and the sampled repair's base discard a
successfully fetched eligible release when one request remains in the quota.
The sampled repair, `c04f6c8b3af6bef8876330f37d02c42effd12908`, preserves it while
pausing subsequent release requests. All 36 observations in the corrected
default-scan fixture completed with valid HTTP conditions and the predicted
contrast. They represent one defect family.

The original introduction is outside the census window. Evidence about that
introduction cannot be counted as a defective change drawn from the fixed
population. The sampled September repair removes the loss path; reporting
the earlier bug against that repair would not earn defect-finding credit.

| Property | Original introduction | Sampled repair base | Repair |
| --- | ---: | ---: | ---: |
| Ordinary quota retains both eligible releases | 3/3 | 3/3 | 3/3 |
| Low quota retains the current eligible release | 0/3 | 0/3 | 3/3 |
| Low-quota draft produces no article | 3/3 | 3/3 | 3/3 |
| Low-quota empty response produces no article | 3/3 | 3/3 | 3/3 |

The six low-quota losses are repeated observations across two related
revisions. They are not six independent defects. Source process time totaled
206.12 seconds; every process exited zero before its 15-second limit. A
separate 0.62-second TLS preflight passed. Source, fixture, inventoried runtime
and governing-record hashes remained unchanged; recorded processes terminated.

## Independent basis and causal location

The introduction parent's `README.md` describes a daily-news candidate pipeline
that gives the editor the deduplicated candidates. Its
`newsroom/sources/base.py` contract assigns fetching, filtering and normalization
to the adapter. Those records are from commit
`fd4c031e7d7735ab5103cc0bf23987bf9090491a`, before the adapter implementation.
Their original blobs and SHA-256 values are preserved in the witness plan.

GitHub defines the remaining-quota header as the number of requests left in
the current window. Exhausting a primary limit produces HTTP 403 or 429.
The fixture supplies HTTP 200 and a remaining value of one: this is a
successfully fetched release, and retaining its body requires no further
request. See the [GitHub rate-limit documentation](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api),
checked on September 10, 2026. This live reference is supporting API context,
not a claimed archival copy of the July documentation.

In introduction commit `e7672756e15b45e68e7f0725b54247cc3e93b89a`,
`newsroom/sources/github.py:222–226` breaks out of the release loop after reading
a low remaining quota, before reading the response body. The scanner does
not exist in its parent. The same ordering remains in sampled repair base
`33881f4a341681fb3b29f6cfd87bdb08e1de9134`. The repair moves body parsing into
`_request_list()` and pauses subsequent requests while returning the current
list. These source locations explain the predicted contrast without relying
on the repair title or its author's tests as an oracle.

## Administration

The [bounded authorization](authorization-2026-09-10-reviewer-github-release-witness.md)
and its [namespace](authorization-2026-09-10-reviewer-github-release-witness-2.md),
[capability](authorization-2026-09-10-reviewer-github-release-witness-3.md) and
[fixture corrections](authorization-2026-09-10-reviewer-github-release-witness-4.md)
preserve each earlier attempt and authorize distinct slots.

The final probe calls the original public `GithubAdapter.fetch(72)` from each
complete, read-only source snapshot. Only `state_dir` is configured, pointing
to private temporary storage. All default scans and their pacing sleeps run.
Search endpoints return successful empty lists with ordinary quota. The first
two default release repositories return fixtures dated one hour before the
call; other repositories return empty lists. Conditions change only release
quota, draft status or body emptiness.

A local TLS server answers the actual `https://api.github.com` URLs through
a private hosts mapping and a generated certificate. The standard-library
HTTP client performs certificate verification; no adapter function, clock or
sleep is replaced. The process runs inside isolated user/network namespaces
with only the capability to bind the private HTTPS port. It cannot call the
real GitHub API. It receives no credentials or production state. The only
Python dependencies used by this path are the original package modules and
the installed standard library.

The runner pins source blobs, probe, criteria, Python, standard-library files,
Bubblewrap and OpenSSL executable identities, and checks their hashes before
and after execution. It does not claim a complete operating-system image pin.
Each process retains request/response bodies, returned articles, resulting
state content, launch arguments, PID/start identity, stdout/stderr hashes and
terminal status. The result checker validates the HTTP conditions separately
from the desired article-preservation result.

## Failed preparations remain evidence

The first two preflights could not bind loopback port 443. Neither executed
historical source. The third custody completed all 36 source processes, but
its 12 introduction runs are invalid: that historical constructor ignores
the later configurable scan-list fields, and the fixture returned HTTP 404
for its defaults. The base and repair did reach the intended fixture and
showed loss versus preservation, respectively. Those results are preserved
under their original configuration, without erasing the invalid introduction.

The fourth custody uses each revision's actual default scan. Its first
ordinary introduction result was checked before launching the remaining
slots; every subsequent result was checked before the next launch. This
prevents an HTTP-fixture failure from silently counting as the intended
release-loss observation.

The witness author inspected the original source and repair before defining
the reproduction. The independent basis is the pre-existing product purpose,
API response semantics and actual end-to-end behavior, not independence of
the author. This remains development evidence. It supplies no whole-patch
clean label, admission, semantic reviewer scoring or ranking acceptance.

## Checker challenges and custody

Six in-memory challenges changed copies of a recorded ordinary result while
updating its output hash. HTTP 404, a wrong release path, a missing request and
an unexpected credential were rejected as invalid test conditions. Removing
all returned articles or duplicating an article remained interpretable product
outcomes and failed the preservation/control property. The original custody
was not modified. These checks exercise the witness checker; they do not
validate a free-text reviewer scorer, which remains unimplemented.

Private root:
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/github-release-witness-4`.

- `plan.json`: SHA-256
  `4b5d3a194aaa70b2fc588ddd285308205c8a98cc357f76481445f16c6b469a00`.
- `verification.json`: SHA-256
  `fea9c0c505179214b01adf7b0230fcba53e4b1a740db61f77b6edb05cd03f65d`.
- `checker-challenges.json`: SHA-256
  `26a85b6adecaca1377ad807e5715da4a6288448a2cdd67d6e7094a33b1c37f61`.

The sibling roots ending in `-1`, `-2` and `-3` preserve all earlier plans,
attempts and failures. The tracked probe and runner reproduce the final
administration but cannot replay its consumed slots. The tracked checker can
re-read the custody without executing source or calling any provider:

```bash
python3 scripts/verify_reviewer_github_release_witness.py \
  /home/halbritt/.local/share/caplab/reviewer-ranking-001/development/github-release-witness-4
```
