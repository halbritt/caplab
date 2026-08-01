# Dependency policy

The `*.in` files describe compatibility. Ordinary libraries use bounded ranges;
the Qwen, PEFT, CUDA, and Hopper-kernel tuples stay exact because they form tested
binary and model-family interfaces.

The generated `*.lock` files describe one release. They pin the complete
transitive graph for Python 3.12 on x86-64 manylinux and include accepted artifact
hashes. The worker image installs only from these locks with `--require-hashes`.
The GPU overlay is compiled with `--no-deps` because its build-time dependencies
must come from the already-installed runtime lock.

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
