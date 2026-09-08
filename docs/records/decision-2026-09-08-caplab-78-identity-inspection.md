# CAPLAB-78: bounded native-identity inspection

## Authorization before inspection

Under ADR 0026 and the active CAPLAB improvement goal, the primary agent
authorizes a read-only identity inspection of the single development
campaign named by CAPLAB-78:

```text
~/.local/share/caplab/campaigns/caplab-review-dissent-001-development-native-r1-2026-07-20
```

Permitted reads are that campaign's manifest and its at-most-16 primary
attempt directories, limited to launch, completion, observation, and raw
native stdout files; the corresponding normalized repository `result.json`
may also be read. Record source locators and content hashes, declared subject
labels, explicit fallback events, and model names in initialization, assistant,
and terminal usage fields. Do not extract prompts, tool payloads, credential
content, or unrelated session history. Stop on an unexpected population,
out-of-root path, symlink, or source mutation during the inspection.

Authorized new artifacts are a private temporary inspection receipt and a
separate repository annotation recording these observations and bounded
decisions. The original raw and normalized evidence stays byte-identical.
No historical evidence is copied into the repository, admitted, registered,
rewritten, purged, or rescored. This annotation is not a new measurement,
gold judgment, or qualification claim. No model calls or spend, other
campaign inspection, other repository changes, ranking, or placement.

After resolving the issue's three decision questions, the primary agent may
append a disposition note to CAPLAB-78 and mark it Done, preserving its
original description and all unrelated fields. Re-read before mutation and
stop on a conflicting concurrent edit; verify the stored state and note.
No comments or messages to other people are authorized. Reopening appends a
new record; it does not erase this inspection. Temporary extraction inputs
may be removed after the provenance-bearing receipt is complete.

## Decision questions

1. Whether to amend, annotate, or leave the normalized record as-is.
2. Whether other slots contain substitution evidence, within an explicitly
   bounded inspection rather than an unbounded historical search.
3. Whether future subject identity should be inferred from the stream or
   preserve the configured subject separately from observed attestation.

The current implementation at `b8c6892` computes `subject_seal` from the
instrument in `review_dissent.native.build_native_review_capture`; its
file-read extraction does not establish the serving model. The later
Codex rollout checks in the artifact-rater path do not repair this separate
native-review normalizer. These are source observations, not evidence that
every archived row has an identity error.

## Inspection and disposition

The bounded inspection confirms one explicit refusal-fallback event,
in `a02-s02-primary` at native stdout line 9, naming
`claude-fable-5` as original model and `claude-opus-4-8` as fallback.
Initialization names Fable; all 33 captured assistant events name Opus 4.8.
The normalized row still carries `subject_id: fable`. The configured label
therefore does not establish the model that produced its visible responses.

The seven other Claude slots have captured assistant events naming Fable
and no explicit fallback event in their retained stdout. This is not proof
that no unrecorded substitution occurred. The eight Codex stdout streams
carry none of the initialization, assistant-model, or terminal model-usage
identity fields inspected here. Their configured identity remains
**unverified by this capture**, not confirmed unchanged.

The original issue says the affected episode's `modelUsage` names three
models. The currently retained terminal usage map names two: Opus 4.8 and
`claude-haiku-4-5-20251001`. Fable is named by initialization and the fallback
event, not by that terminal usage map. All eight Claude slots list Haiku in
terminal usage. Usage of an additional model name alone does not establish
which model authored the principal response; the explicit fallback and
assistant fields supply the stronger observation here.

All 16 original observation records have status `invalid`. This inspection
did not rerun their grader or verify the existing severity-enum explanation.
No new capability result or comparison is derived from them.

## Decisions resolving CAPLAB-78

1. **Annotate separately.** Preserve the original raw custody and normalized
   result exactly. This record is the identity annotation; it must accompany
   an interpretation of the affected row. Do not treat that row as an
   observed Fable response merely because its configured seal says Fable.
   Its existing failed-development disposition is unchanged.
2. **Limit the archive search.** Inspect the 16 primary slots of the named
   campaign, which is now complete. Do not infer archive-wide cleanliness.
   A wider inspection needs a separate bounded decision naming the campaigns
   and the claim it could change; no model calls are needed for that read.
3. **Keep planned and observed identity separate.** Preserve the subject seal
   as the configured trial assignment. A future capture must link a separate
   observed-identity record to raw bytes and distinguish initialization,
   response-model fields, explicit fallback events, usage-model names, and
   missing evidence. Do not derive a replacement planned seal from whichever
   model happened to answer. Substitution or missing required attestation
   prevents attribution to the planned subject; it is an apparatus/identity
   disposition, not an incorrect reviewer answer. Reclassification requires
   its own authorization and must not hide the assigned denominator.

This resolves the incident's three decision questions, so CAPLAB-78 can be
marked Done as an observation-and-disposition item. It does not establish
future enforcement in `review_dissent.native`, whose normalizer remains as
observed above. That enforcement is required before another native-review
campaign, and CAPLAB-79's capture-design work remains open. No historical
normalizer is rerun by this decision.

## Source custody and verification

The inspection parsed JSONL strictly, checked the existing manifest,
instrument, launch, completion, observation, and normalized-result seals and
links, checked the frozen execution order, and verified raw stdout hashes
against both completion and observation records. All 67 inspected files were
hashed again at the end and were unchanged. No held-out artifact, task or review file, stderr, unrelated campaign, or
live model was read or executed by the inspection script. It did not retain
prompt or tool payloads.

The following table reports captured assistant-event counts, not trials or
independent model responses. Every raw locator is
`<campaign-root>/attempts/<attempt>/native.stdout` under the root authorized
above. `unavailable` means these stdout streams do not carry the inspected
model-identity fields. It is not a model-mismatch assertion.

| Attempt | Configured label | Captured assistant models and event counts | Explicit fallback | Raw stdout SHA-256 |
| --- | --- | --- | --- | --- |

| `a01-s01-primary` | `gpt` | unavailable | none recorded | `ba429b3431fe6c7bdf8fd738e702eae77a950a60b454678c2f5ff124750a7ac2` |
| `a02-s02-primary` | `fable` | claude-opus-4-8: 33 | Fable to Opus 4.8, line 9 | `49b35b9708d27de492a43f0a9843726a05e4d1686cc59bee37b4f7cead9e8709` |
| `a03-s03-primary` | `fable` | claude-fable-5: 24 | none recorded | `0ad4cac66947ac1c4478d34f0aad09dcb02e60886ed09a05c78062f0b22d2dfc` |
| `a04-s04-primary` | `gpt` | unavailable | none recorded | `bd8d33e7da6493815baf0b9e95c0ce29a86cb77a6f63ce78d4604d4d18244640` |
| `a05-s05-primary` | `gpt` | unavailable | none recorded | `855dad0e897c1ce55b10384a4d375db68b09dcb08eff013e3c423292ccf47815` |
| `a06-s06-primary` | `fable` | claude-fable-5: 24 | none recorded | `a027d6450dd8866fb0259a57d36a74b29d1b0c6e39ddee9b5fec245d67e163dc` |
| `a07-s07-primary` | `fable` | claude-fable-5: 20 | none recorded | `3d897011bb8e41318bb9b5e3bc67cb85a72dd7433e953a8bd8ff61fc9142927f` |
| `a08-s08-primary` | `gpt` | unavailable | none recorded | `0210bf1bfc09fca474dfc91b5c1e4f3beff19b4c5ba10587b6af00d08eb89fc9` |
| `a09-s09-primary` | `gpt` | unavailable | none recorded | `7d0f9969b26b228a23be074bb745ff4ac2bd5782539a24cedaf53bfaac9296c0` |
| `a10-s10-primary` | `fable` | claude-fable-5: 27 | none recorded | `41af2d68ebd65e0db787363366ced59d64e7e81aa526e4c37833f2d760dfa1f4` |
| `a11-s11-primary` | `fable` | claude-fable-5: 21 | none recorded | `915e452a77687a13a6e19d5b99053d004aaad014d18dcd369d0c38f144b26b6d` |
| `a12-s12-primary` | `gpt` | unavailable | none recorded | `caf2c7b32e1fe05c3a4bcd2055c53872e15692b26704f3fd2d8d246749c34de3` |
| `a13-s13-primary` | `gpt` | unavailable | none recorded | `f8f9beaf2f7103bbb47b67d38d50352b5bf4fff606c3614bde156d68fd53652b` |
| `a14-s14-primary` | `fable` | claude-fable-5: 24 | none recorded | `3788b18b42acd417bea5eca77d68d3c91cc8e16c9f73d82f2b81cd571bbb9a37` |
| `a15-s15-primary` | `fable` | claude-fable-5: 26 | none recorded | `aae816d875c88bcb8550488c43147029d241eff0d3513fb00e7e5a4e9bec899d` |
| `a16-s16-primary` | `gpt` | unavailable | none recorded | `42570fe4dc216e7201073884249e08f25f006e20ecb132fd3817b44fdef85867` |

The normalized `result.json` SHA-256 remains
`f3810f55f8b68c032f473e4433581a97451c8bbe2cb4eecd91ffa8bad64adb5e`.
The native instrument file SHA-256 is
`1e7747342ede592f5ddd6553233ea36c80282266251bf7e30feebb06edf6a242`;
the campaign manifest file SHA-256 is
`0499700c6f7db81ffb530fbe314e921844239bdb698141c34f637a6a9c29423b`.
The private inspection receipt is `/tmp/caplab-78-identity-inspection-final.json`,
SHA-256 `915a3b3d9996012dc621042bf704ffcb1f1cd84868e808cd5f8dfe888058f075`.
It retains the complete 67-file hash inventory and extracted identity fields.
The inspection script `/tmp/caplab-78-inspect.py` has SHA-256
`d629f638a02cff048d1d749b07a627fb4bd7af0452666bbd7b61289b862d455a`. Its successful log is
`/tmp/caplab-78-inspection-final.log`. These hashes provide local consistency
and provenance, not an independently authenticated provider identity or
proof that every native event was captured.

## Advisory receipt and planning projection

The advisory packet is `pkt-e8eb4aae0f365582`, content SHA-256
`e8eb4aae0f365582c1ff28c62750260a19d7bfdb7eca9e621a362a4d08632bd6`. It uses release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Applied concepts are
`universal-evidence-before-intervention`, `domain-identity-entity`,
`universal-repository-contract-precedence`, and
`agent-conduct-authority-bounded-action`. The configured assignment survives
the observation of a different model; it must not be silently redefined to
fit the response. Repository authority governs; the packet's execute ceiling
does not supply permission. Citation consumption is recorded locally.

All remaining packet obligations are nonmaterial to this incident annotation
and decision disposition, with the stated prospective implementation limit:

| Concept | Missing requirements | Reason |
| --- | --- | --- |
| domain-language-model-loop | model expressed in executable behavior | Future observed-identity enforcement is explicitly incomplete. This closes the incident's decision questions, not that implementation. |
| domain-modeling-investment-gate | business differentiation and product lifespan; business-value and expert-access evidence; expert access and feedback cadence; recurring ambiguity, contradiction, or rule defect; team capacity to sustain the model | Existing CAPLAB identity terms and authority apply; no new domain-modeling campaign or framework investment is selected. |
| task:repository-assessment | evidence-co-change; evidence-generated-artifacts; evidence-tests; evidence-version-history | No runtime code or generated product artifact changes. The read-only inspection checked actual source bytes and metadata seals; a fresh full software suite would not establish the historical observation. |
| testing-deterministic-async-observation | repeated or adversarial scheduling results | No concurrent execution or scheduling policy changes. The inspection process completed with exit zero and explicit assertions. |

CAPLAB-78 (`b3d7646b-386c-4a8d-afd0-d941fce43d5a`) was changed from Ready to
Done with the scoped note appended. Read-back verified the expected state,
the submitted description (allowing only Plane's added outer `div`), and
unchanged title, priority, assignees, labels, parent, project, and issue
number. The entire original description remains present. Its original
SHA-256 is `c89e1d502097d67578c150c91fbb36224475ba13542c42cd2f15a2a447f254b4`;
the stored description SHA-256 after the update is
`0606bfa28bf94775209f80768e81b0e387c142ebc92f3e66698a2172a77f17cc`.
Evidence: `/tmp/caplab-78-before-update.json`,
`/tmp/caplab-78-update-result.json`, and `/tmp/caplab-78-after-update.json`.
All 67 inspected source files were rehashed unchanged after the projection
update. No other issue was changed. A fresh list read
(`/tmp/caplab-roadmap-after-78.json`) shows 19 open roadmap items. The
broader goal remains incomplete.
