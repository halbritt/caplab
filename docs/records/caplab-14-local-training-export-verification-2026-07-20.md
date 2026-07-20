---
id: caplab-14-local-training-export-verification-2026-07-20
artifact_type: verification-record
title: CAPLAB-14 local contrastive export verification
status: pass
created: 2026-07-20
decision_record: adr-0048
verifier: primary-agent
independence: not-independent
---

# CAPLAB-14 local contrastive export verification

## Verdict

**PASS** for CAPLAB-14's technical export criteria. This is not independent
verification, training authorization, or CAPLAB acceptance.

## Verified evidence

- Eight exact native-harness calls produced seven valid rows, one preserved
  subject-invalid row, zero harness failures, and no replacements.
- Every exported record binds its local tuple, source row, task family,
  treatment, mechanical outcome, oracle type, label authority, prompt,
  responses, split, and hashes.
- Three `RD-D01` rows are train, four `RD-D02` rows are development, and the
  sealed `RD-H01`/`RD-H02` test identities have no exported rows or bytes.
- The subject-invalid row and every proprietary-provider row are absent.
- The corpus recomputes to semantic SHA-256
  `303a55e6594528ab520d9fbc92d306cd942d4d6a76c68ef314797aa0c84cf1e5`.
- Literal credential, personal-data, email, and host-path scans found no match.
- The dataset card records inclusion, exclusion, reward, split, license,
  privacy, retention, bias, and claim limits.

## Boundary

This pass verifies the committed export. It does not validate a tuning method,
checkpoint, held-out result, general capability claim, or downstream use.
