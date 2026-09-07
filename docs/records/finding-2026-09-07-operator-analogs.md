# Which injection operators plant a defect that actually occurs

- Date: 2026-09-07. Standing order §0.3 of
  `instruction-2026-09-07-review-validation-study.md`. Reference set: the
  26 controls the adjudication ledger has proved defective
  (`advisory/control-adjudications.jsonl`, dispositions `defective`, bases
  read in full). Code: `QUALIFICATION_OPERATORS` / `SENTINEL_ONLY_OPERATORS`
  in `caplab.advisory.operators`; scoring excludes sentinel rows from catch
  and false alarm and reports them under `sentinel_by_defect_class`.
- The instrument has sixteen operators, not fifteen: `dangling_reference` is
  a sixteenth vendored operator. Five have an analog; eleven do not.

## Natural-analog (kept in qualification claims)

| operator | what it plants | analog among the 26 (control id, the defect as adjudicated) |
|---|---|---|
| `unearned_verification_claim` | a verification claim the artifact's own content does not earn | `qs-40583720` receipts assert `exit_code 0`, digests and seals for executions the same set says did not run; `71ac079a` and `1c9196ec` "proves … byte-for-byte" guards that grep comment strings; `b9919beb` docs claim Bind serialises the ledger while Bind never calls Marshal |
| `contradicted_clause` | two statements in one artifact that cannot both hold | `e57c4ab7` README says a test validates against schemas, the test loads none; `425bccdb` one backend.yaml says "healthy again" and "now the spend-limited one" on the same date; `qs-5ea16d21` 0/13 tabulated, "22 matched arms" asserted; `a17d0d0b` W14 vs W22.3 on which state is `[not_available]` |
| `refuted_conclusion` | a conclusion the artifact's own content refutes | `qs-42ac7af2` ADR 0057 authorizes r2 on figures that show the demand exceeds the whole card; `f42f9365` documented provenance write sits after an unconditional return; `b755eb26` documented branch made unreachable by the same file's accounting; `qs-71a0c8dd` a mandated scope code satisfied by the untouched tree, which the same section forbids |
| `decorative_check` | an acceptance check that is named but never truly runs or binds | `qs-415d0b93` "exact registered argv" silently replaced by a PATH `go`, so an unresolvable check cannot fail; `qs-ccfd2a5f` a plan naming check ids it never identifies; `qs-907a07da` a check marked pass over two unequal inputs; `614cac36` a pin validator that checks formats only |
| `broken_internal_crossref` | an internal reference or anchor that does not point where it claims | `qs-922bffcd` one element anchor id for two documents, with attribute syntax leaked into the link text |

## No natural analog (regression sentinel only)

| operator | what it plants | nearest real case, and why it is not an analog |
|---|---|---|
| `base_dropped` | the base declaration removed | none of the 26 lacks a base declaration; `c778cba8` ships an *empty* base pin beside its documented-field defect, a different shape |
| `dangling_reference` | a reference to an element that does not exist | none; the real reference defects are contradictions between two present elements |
| `dropped_section` | a required section deleted | none; no adjudicated defect is a missing section |
| `duplicated_section` | a section repeated | none |
| `hash_mismatch` | a declared sha256 perturbed | none among the 26 as adjudicated. `qs-641d18fb`'s declared `result_tree_hash` names a tree that was never produced (found by the materializer oracle on 2026-09-06), but its defective ruling rests on dead code after a return; the hash finding is a candidate analog, not an adjudicated one |
| `hollow_delivery` | the delivery reduced to one file | none among the 26. Production shows the shape (`cancellation 320479`: an empty patch asserting a 1,135-file result), so this is the first operator to revisit if the reference set grows |
| `overclaimed_level` | a claim level raised one notch | none; the level defects that occur are unearned claims, above |
| `requirement_inversion` | a normative clause negated | none |
| `scope_violation` | a later-stage commitment inserted | none |
| `swapped_section_bodies` | two section bodies exchanged | none |
| `truncated_tail` | the artifact cut mid-sentence | none |

## What the re-scoring shows

Re-issued on the five kept operators, every iso-v1 claim has 13 pairs and
nine sound controls:

| binding | catch | false alarm |
|---|---|---|
| agy-gemini-3-7-flash-high | 13/13 | 0/9 |
| agy-gemini-3-8-flash-high | 13/13 | 2/9 |
| cc-glm-5-3-flash-high | 13/13 | 2/9 |
| cc-glm-5-3-max | 13/13 | 1/9 |
| claude-fable-5-1-high | 13/13 | 2/9 |
| claude-opus-5-high | 13/13 | 2/9 |
| codex-sol-high | 13/13 | 9/9 |
| oc-glm-5-3 | 13/13 | 1/9 |
| or-gemini-3-7-flash-high | 12/13 | 0/9 |

Eight of nine bindings catch every planted analog defect. The catch
ordering the board showed for three weeks came from the eleven sentinel
operators: structural perturbations that every binding catches at a
different rate and that production never produces. On the defects that
occur, the instrument does not separate these bindings on catch at all; it
separates them only on false alarm, and false alarm is the axis iso-v1
already invalidated for verification-oriented bindings.
