---
id: caplab-16-qwen27b-qlora-attempt-2026-07-21
artifact_type: execution-record
status: infrastructure-failed
authority: adr-0050
disposition: adr-0051
created: 2026-07-21
---

# CAPLAB-16 Qwen3.6-27B QLoRA attempt

## Executed boundary

The attempt acquired `peecee`'s `marker` slot 1 under lease
`2f3b3131-0b9e-43dd-b91d-34c6a8ee7c4c`, unloaded only the resident
`qwen3.6:27b` Ollama model, installed the frozen isolated toolchain, downloaded
all 29 files of Qwen checkpoint revision
`6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, verified the index SHA-256, and
ran the frozen no-update preflight.

Environment evidence records Windows 11, RTX 3090 Ti, CUDA 13.0, Python
3.12.13, Torch `2.12.1+cu130`, Transformers `5.14.1`, PEFT `0.19.1`, TRL
`1.8.0`, BitsAndBytes `0.49.2`, and Accelerate `1.14.0`.

## Failure timeline

| UTC | Observation |
|---|---|
| `00:14:29` | `training-started.json` written; sole attempt consumed. |
| `00:17:15` | Step-3 partial adapter file completed its write. |
| `00:17:37` | Fleet heartbeat first recorded `nvidia-smi` timeout; both `peecee` slots became non-live. |
| after fence | Lease runner reported lease loss and stopped the local SSH child group. |
| cleanup | The remote PowerShell/Python tree remained; PIDs and command lines were verified and the exact tree was terminated. |
| post-cleanup | `nvidia-smi` still timed out, fleet slots remained de-listed, and Ollama `/api/tags` remained responsive. |

This is an infrastructure outcome, not evidence of review behavior or tuned
capability. The step-3 directory lacks `trainer_state.json` and is not a sealed
checkpoint candidate.

## Preserved evidence

Raw custody contains eight files. The deterministic inventory SHA-256 is
`9e0b9b1e00745e58dbac8583d2b70548d4b236ea71a5cacc1878063833345c98`.
Important identities are:

- environment:
  `816ce35a11ce353a51440c1e935ba4eb9f838cd823eaaab7abaef0f7dc274512`;
- preflight:
  `dfe6dea676a8f1bb5adf72d991d3fc4fd9836b88d642af451273bd4d15728dd7`;
- training-start marker:
  `a2e1a9d865d2eea83c7678721b45911c7eb1e70822db8633f34658906cc87653`;
- partial adapter:
  `157c234e9b99f6b59bb1885c85fe83fd6bba3a76e3c64ec7eedf842d8f577ff2`.

No final result, final adapter, evaluation server, held-out read, native-harness
evaluation call, general control call, deployment, Striatum mutation, or paid
effect occurred.
