---
id: caplab-14-local-training-export-2026-07-20
artifact_type: execution-record
title: CAPLAB-14 local training-source campaign and export
status: complete
created: 2026-07-20
decision_records:
  - adr-0047
  - adr-0048
---

# CAPLAB-14 local training-source campaign and export

## Execution

The exact ADR 0047 native tuple completed eight ordered loopback calls through
`striatum-openai-lane` v1 against model file SHA-256
`50e1122946854f2272b44d466c03d17d410d3f02dcd1c021a1f29f6b384a7126`.
The running llama server was idle before every call and was not stopped,
restarted, reconfigured, or otherwise mutated.

Seven responses were schema-valid and one was subject-invalid after truncating
inside a JSON string. There were zero harness failures and no retries. Six
valid reviews scored `1.0`; one clean review scored `0.2`. Held-out content was
not opened.

Raw result semantic SHA-256:
`df92d36f8986ffcd957cfd7cb0ce848f20089c1878664f1fbfb2bd8039b7d38f`.
Raw result file SHA-256:
`67e7ab18a9d9ac558f638145472b52301380ba9273bebe518e3d4f1cee8aa412`.
Raw custody inventory SHA-256:
`fc20e0fa6d9e15cc7a14ec00de38e31275b792515542b5612b8c01e5efdfa4bd`.

## Export

ADR 0048 materialized seven local-only records: three train, four development,
and zero held-out rows. The corpus semantic SHA-256 is
`303a55e6594528ab520d9fbc92d306cd942d4d6a76c68ef314797aa0c84cf1e5`;
file SHA-256 is
`09ec666630189ebbe9bf180d3dd567623f8dbee753871f63ac7f66c712cb87f2`.

The export contains no Claude or OpenAI output, no invalid row, no cross-family
split, and no held-out bytes. Literal secret, personal-data, email, and host-
path scans found no match.

## Boundary

CAPLAB-14 execution and export are complete. This record does not authorize
training, model download, server downtime, held-out access, checkpoint
deployment, Striatum mutation, independent verification, or acceptance.
