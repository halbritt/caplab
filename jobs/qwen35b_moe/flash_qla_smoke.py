"""Fail-closed Hopper FlashQLA dispatcher, forward, and backward probe."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import importlib.metadata
import json
import math
import os
from pathlib import Path
from collections.abc import Iterator
from typing import Any

from .contract import ContractError
from .fla_dispatch_compat import validate_install as validate_compatibility_install


PROTOCOL = "striatum-flash-qla-smoke/1"
GRADIENT_NAMES = (
    "q",
    "k",
    "v",
    "g",
    "beta",
    "A_log",
    "dt_bias",
    "initial_state",
)


def validate_install() -> dict[str, str]:
    """Validate the coherent package contract without pretending to run a kernel."""
    from fla.ops.gated_delta_rule.backends.flash_qla import FlashQLABackend

    validate_compatibility_install()
    versions = {
        package: importlib.metadata.version(package)
        for package in (
            "flash-linear-attention",
            "fla-core",
            "flash-qla",
            "tilelang",
            "apache-tvm-ffi",
        )
    }
    expected = {
        "flash-linear-attention": "0.5.2",
        "fla-core": "0.5.2",
        "flash-qla": "0.1.2",
        "tilelang": "0.1.9",
        "apache-tvm-ffi": "0.1.9",
    }
    if versions != expected:
        raise ContractError(f"FlashQLA package contract mismatch: {versions!r}")
    if not FlashQLABackend.default_enable or FlashQLABackend.priority != 3:
        raise ContractError("FlashQLA is not the enabled priority Hopper backend")
    return versions


def validate_flash_qla_smoke_receipt(receipt: object) -> dict[str, Any]:
    if not isinstance(receipt, dict):
        raise ContractError("FlashQLA smoke receipt must be an object")
    gradients = receipt.get("gradients")
    device = receipt.get("device")
    dispatch_calls = receipt.get("dispatch_calls")
    if receipt.get("protocol") != PROTOCOL:
        raise ContractError("FlashQLA smoke protocol is invalid")
    if receipt.get("dispatcher") != "FlashQLABackend":
        raise ContractError("FlashQLA dispatcher identity is invalid")
    if receipt.get("production_fused_inputs_adapted") is not True:
        raise ContractError("FlashQLA production fused-input evidence is missing")
    if (
        isinstance(dispatch_calls, bool)
        or not isinstance(dispatch_calls, int)
        or dispatch_calls < 1
    ):
        raise ContractError("FlashQLA implementation was not invoked through the dispatcher")
    if receipt.get("forward_finite") is not True:
        raise ContractError("FlashQLA forward evidence is not finite")
    if receipt.get("loss_finite") is not True:
        raise ContractError("FlashQLA loss evidence is not finite")
    if not isinstance(device, dict) or device.get("compute_capability") != [9, 0]:
        raise ContractError("FlashQLA device evidence is not SM90")
    if not isinstance(gradients, dict) or set(gradients) != set(GRADIENT_NAMES):
        raise ContractError("FlashQLA gradient evidence is incomplete")
    invalid_gradients = [
        name for name in GRADIENT_NAMES if gradients.get(name) != "finite-nonzero"
    ]
    if invalid_gradients:
        raise ContractError(
            f"FlashQLA gradient evidence is invalid: {', '.join(invalid_gradients)}"
        )
    return receipt


@contextmanager
def _observe_flash_qla_calls(module: Any) -> Iterator[dict[str, int]]:
    """Observe the implementation that the FLA backend calls after selection."""
    original = getattr(module, "chunk_gated_delta_rule", None)
    if not callable(original):
        raise ContractError("FlashQLA implementation entry point is unavailable")
    observed = {"count": 0}

    def observed_dispatch(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        observed["count"] += 1
        return original(*args, **kwargs)

    module.chunk_gated_delta_rule = observed_dispatch
    try:
        yield observed
    finally:
        module.chunk_gated_delta_rule = original


def run_flash_qla_smoke(output: Path | None = None) -> dict[str, Any]:
    """Exercise the public FLA dispatcher on the Qwen3.6 Hopper tensor shape."""
    validate_install()
    os.environ["FLA_FLASH_QLA"] = "1"
    try:
        import flash_qla
        import torch
        from fla.ops.gated_delta_rule import chunk_gated_delta_rule
    except ImportError as error:
        raise ContractError("FlashQLA runtime dependencies are unavailable") from error

    if not torch.cuda.is_available():
        raise ContractError("FlashQLA runtime smoke requires CUDA")
    capability = list(torch.cuda.get_device_capability())
    if capability != [9, 0]:
        raise ContractError(
            f"FlashQLA runtime smoke requires SM90, found {capability!r}"
        )

    torch.manual_seed(42)
    torch.cuda.manual_seed_all(42)
    shape = {"batch": 1, "tokens": 64, "qk_heads": 16, "v_heads": 32, "dim": 128}
    q = torch.randn(1, 64, 16, 128, device="cuda", dtype=torch.bfloat16, requires_grad=True)
    k = torch.randn(1, 64, 16, 128, device="cuda", dtype=torch.bfloat16, requires_grad=True)
    v = torch.randn(1, 64, 32, 128, device="cuda", dtype=torch.bfloat16, requires_grad=True)
    g = torch.randn(1, 64, 32, device="cuda", dtype=torch.float32, requires_grad=True)
    beta = torch.randn(1, 64, 32, device="cuda", dtype=torch.bfloat16, requires_grad=True)
    A_log = torch.randn(32, device="cuda", dtype=torch.float32, requires_grad=True)
    dt_bias = torch.randn(32, device="cuda", dtype=torch.float32, requires_grad=True)
    initial_state = torch.randn(1, 32, 128, 128, device="cuda", dtype=torch.float32, requires_grad=True)
    tensors = dict(
        zip(
            GRADIENT_NAMES,
            (q, k, v, g, beta, A_log, dt_bias, initial_state),
            strict=True,
        )
    )

    with _observe_flash_qla_calls(flash_qla) as observed:
        generated, final_state = chunk_gated_delta_rule(
            q=q,
            k=k,
            v=v,
            g=g,
            beta=beta,
            initial_state=initial_state,
            output_final_state=True,
            use_qk_l2norm_in_kernel=True,
            use_gate_in_kernel=True,
            A_log=A_log,
            dt_bias=dt_bias,
            use_beta_sigmoid_in_kernel=True,
            allow_neg_eigval=False,
            state_v_first=True,
        )
        loss = generated.float().square().mean() + final_state.float().square().mean()
        if not bool(torch.isfinite(generated).all() and torch.isfinite(final_state).all()):
            raise ContractError("FlashQLA forward produced non-finite values")
        if not math.isfinite(float(loss.detach())):
            raise ContractError("FlashQLA smoke loss is non-finite")
        loss.backward()

    gradients: dict[str, str] = {}
    for name, tensor in tensors.items():
        gradient = tensor.grad
        if gradient is None or not bool(torch.isfinite(gradient).all()):
            raise ContractError(f"FlashQLA gradient is missing or non-finite: {name}")
        if torch.count_nonzero(gradient).item() == 0:
            raise ContractError(f"FlashQLA gradient is zero: {name}")
        gradients[name] = "finite-nonzero"

    receipt: dict[str, Any] = {
        "protocol": PROTOCOL,
        "dispatcher": "FlashQLABackend",
        "dispatch_calls": observed["count"],
        "production_fused_inputs_adapted": True,
        "device": {
            "name": torch.cuda.get_device_name(),
            "compute_capability": capability,
        },
        "shape": shape,
        "dtype": "bfloat16",
        "forward_finite": True,
        "loss_finite": True,
        "loss": float(loss.detach()),
        "gradients": gradients,
        "versions": validate_install(),
    }
    validate_flash_qla_smoke_receipt(receipt)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True), flush=True)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-install", action="store_true")
    args = parser.parse_args()
    if args.validate_install:
        print(json.dumps(validate_install(), indent=2, sort_keys=True))
    else:
        run_flash_qla_smoke(args.output)


if __name__ == "__main__":
    main()
