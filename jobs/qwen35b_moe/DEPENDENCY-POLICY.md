# Dependency policy

The `*.in` files describe compatibility. Ordinary libraries use bounded ranges;
the Qwen, PEFT, CUDA, and Hopper-kernel tuples stay exact because they form tested
binary and model-family interfaces.

The generated `*.lock` files describe one release. They pin the complete
transitive graph for Python 3.12 on x86-64 manylinux and include accepted artifact
hashes. The worker image installs only from these locks with `--require-hashes`.
The GPU overlay is compiled with `--no-deps` because its build-time dependencies
must come from the already-installed runtime lock or be declared explicitly in
the overlay. `ninja` is a bounded tool dependency; the four CUDA extension and
kernel packages remain the exact tested compatibility tuple.

Torch 2.8 discards a wrapper when `torch.compiler.disable` is applied around an
already-disabled function. FLA 0.5.2 consequently bypasses its Hopper backend
dispatcher for `chunk_gated_delta_rule`. Its FlashQLA backend also rejects the
fused raw gate and beta inputs that the Qwen3.5/3.6 layer always supplies. No
newer released FLA or FlashQLA tuple corrects these integration defects.

The image therefore applies two fail-closed source corrections after install. It
removes the redundant inner disable decorator while retaining FLA's disabled
dispatch wrapper. It also adapts raw gate and beta inputs inside only the
FlashQLA backend, using FLA's reference gate transform before invoking the fused
kernel. This preserves autograd through the raw gate, beta, `A_log`, and
`dt_bias`; FLA's own tests define the manual transform as equivalent to its
in-kernel path. Every wheel preimage and corrected postimage is SHA-256-bound, so
a future FLA source change fails the build instead of receiving an unreviewed
patch. Remove these corrections only after a tested FLA release incorporates the
equivalent upstream fixes.

The pinned llama.cpp revision cannot reorder Qwen3.5 linear-attention value
heads when the input is a factorized LoRA tensor: its generic implementation
tries to reshape the LoRA row dimension and raises `NotImplementedError`.
`llama-qwen35-lora-reorder.patch` expresses the same permutation as an
`index_select`. Output-row selection changes the LoRA B factor; input-column
selection changes the A factor. The image checks that the patch applies to the
exact pinned revision. Runtime export checks the retained patch hash, its
reverse application, and the two-file tracked diff before conversion starts.

Regenerate after an intentional compatibility change:

```bash
python3 -m jobs.qwen35b_moe.lock_dependencies
```

Verify that source constraints and committed locks agree:

```bash
python3 -m jobs.qwen35b_moe.lock_dependencies --check
```

An update is accepted only after Gate 1, Gate 2 BF16, and Gate 3 MoE pass against
the newly built immutable image. FP8 is a separate experiment after BF16.
