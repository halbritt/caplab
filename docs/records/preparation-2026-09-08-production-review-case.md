# Prepare a reviewable production case without assigning a correctness label

Date: 2026-09-08. Baseline: `b60af49`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before preparation

Create `docs/product/advisory/review-case-403583.md` as a concise, explicitly
unadjudicated case brief and link it from `production-review-report.md` in that
directory. This record and those two files are the only repository edit targets.
The brief must lead with the task, exact original/later distinction, review
question, verified observation and unresolved judgments. It is a navigation
surface, not an evidence admission, label, score or new adjudication instrument.

Read and verify the fixed canary report at
`/tmp/caplab-production-followup-tyk04scp/report/report.json`, SHA-256
`f39441c9c42264abc8566e9e068c7480e5cb6dfd23cced8e9ae96c3e06498f19`, to identify
only run403588's exact source links. Read existing committed inspection records
and the private verification receipts named by them for the two fixed candidates
and their native probes. Retain only hashes, locators and structural/context
summaries in the brief; no historical transcript, complete review, prompt,
command-output body or source-code copying into the repository.

A missing original prompt or contract must remain unavailable unless a further
amendment names exact objects and bounded extraction. Do not substitute the
later review's prompt as the original's instructions. Preserve the withdrawn
compact/expanded hash claim as withdrawn; do not revive it as a defect.

Use private `/tmp/caplab-review-case-*` metadata/advisory artifacts, verify
source hashes and local links, consolidate advisory provenance before removing
only named scratch, and commit locally. Authority expires at commit. No model,
historical code or captured-command execution; no candidate/source mutation,
gold label, independent judgment, evidence registration, coder exposure,
tracker write, external message, push or service change. Preserve historical
custody, unrelated `docs/designs/`, worktrees and timers. Stop on changed source
identity, conflicting governing context or broader required effects.

## Exact governing-context extraction amendment

The fixed canary row for run403588 links contract
`649545a930c199f16c441194f4851fed27f504c682740a17884eec54e3560f1d` and a
`launched_prompt` semantic-exhaust object
`1a51075027b4c3680dc4a31464f5cca2eb0a1330e23178da11e3068a7632440d`.
Authorize copying only those two compressed historical objects from
`~/.local/share/striatum/graphs/019f22ef-0cb4-780f-9b82-b210bab24325/objects/sha256/`
to fresh private `/tmp/caplab-review-case-*` custody and decoding them with the
local `zstd` binary through bounded process capture. Require no-follow regular
sources, at most one MiB compressed and one MiB decoded per object, five seconds,
complete streams, exit zero and exact content hashes. Recheck compressed source
hashes after decoding. Retain original paths, compressed/content hashes, bytes,
commands and process receipts. Missing or changed sources stop extraction.

Inspect only the original review's assigned scope, target identities and
assumptions needed for the brief. Derived short summaries and hashes may appear
in the brief; full prompt and contract remain private. No other historical
object copying, prompt execution, source mutation or evidence admission is
permitted. These context observations do not create adjudication authority.

### Decoder correction

The first decoder invocation exited 1 with complete streams and no stdout:
`zstd` refused the store envelope as an unsupported format. Preserve its
compressed copy and receipt at `/tmp/caplab-review-case-context-ji6r7fa4/`.
The native object reader at the already retained historical source path
`internal/store/object.go` specifies a 16-byte `SOB1` envelope before the zstd
payload. Authorize one corrected extraction of the same two objects in a new
private directory: validate magic, version/codec and declared length using that
reader's format, preserve the whole stored object, and decode only its payload.
Keep the same byte/deadline limits and require declared-length and SHA-256
agreement. No fallback format or source substitution is permitted.

## Verified context and delivered brief

The corrected extraction recovered the original contract (3,272 bytes) and
launched prompt (69,091 bytes), each matching its required hash. Custody is
`/tmp/caplab-review-case-context-dnr6p_oo/`, including whole stored envelopes,
zstd payloads, commands, complete stream receipts and source provenance.
The initial failed extraction remains separate and is not successful evidence.
An ancillary version-display shell line also failed because it supplied no
executable; retrieval uses the separately successful gate and packet commands,
not that display line.

The original prompt names subject version403583 and change-set hash73f1d90,
adversarial posture v1, contract v2 and `base_mode: anchored-expanded`. It
explicitly distinguishes compact base pin54a9eb7 from expanded base489e019 and
names original result3f42e278. It directs independent inspection against the
expanded base and exact origin Work Graph. The contract's refusal boundary is
predicate/decision violation or demonstrated harm on the changed surface;
findings outside that boundary require `accept_with_findings`. These are
observed assigned instructions, not a newly issued review contract.

The new [case brief](../product/advisory/review-case-403583.md) puts the concrete
review question and observed result before its custody details. It distinguishes
change-set hashes from reconstructed product hashes, original and later
versions, fixture evidence from production replay, and finding-level evidence
from a whole-verdict judgment. It links the correction so the withdrawn hash
claim cannot silently return through an old record. The existing production
report guide now links this brief.

The brief does not satisfy Striatum's formal adjudication-preparation pass
contract, whose sealed bundle, paired dossiers and admission requirements have
not been run. It does not claim blinding or replace the independent ruling
required for gold accrual. No adjudication record, control-soundness label,
score, ranking or criterion count is changed. A local navigation page is chosen
over copying full historical inputs into the product docs or inventing a new
labeling interface while authority and independent outcomes remain absent.

## Verification and advisory closure

Current verification rechecked the original prompt's linkage in the fixed
report, both context object envelopes and decoded hashes, the two historical
canonical candidates, all 3,120 retained fixture files and the prior native
stream receipts. Local links and the report-guide entry were checked. Full
source bodies remain outside the repository. This documentation-only change
adds no tests and does not rerun the full suite or the historical fixture.

Pincite's retrieval-state gate passed against release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Final packet
`pkt-7f870a1a9c140b06` incorporates four typed records for authority, exact
context, the brief's boundaries and current verification. The first reassembly
named a nonexistent evidence filename and was rejected; the same evidence bytes
were renamed to the intended name before successful assembly. No conclusion
relies on that rejected invocation.

Four consumed citations classified as valid: repository-contract precedence,
evidence before intervention, explicit invariants and bounded authority.
Thirty-two remaining generic obligations are individually retained as
nonmaterial with rationales in `/tmp/caplab-review-case-verification.json`.
They do not support repair causality, representative workload claims, broader
architecture/conformance conclusions or independent adjudication. The receipt
also retains packet hash and versions, exact source locators, typed evidence,
artifact hashes and citation classifications. Ten named advisory scratch files
are consolidated there before removal; context custody, scripts and immutable
authorization/brief snapshots remain.

The brief and guide link are locally integrated under the named delegation.
No correctness ruling or acceptance is made. The broader goal remains active.
