"""Fail-closed Qwen linear-attention binding for paid Hopper runs."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .contract import ContractError


PROTOCOL = "striatum-hopper-linear-attention/1"
CONFIG_KEY = "hopper_linear_attention_backend"
_SUPPORTED_CAPABILITIES = {9, 10}


def _device_capability() -> tuple[int, int]:
    try:
        import torch
    except ImportError as error:
        raise ContractError("torch is required to select a Hopper backend") from error
    if not torch.cuda.is_available():
        raise ContractError("CUDA is required to select a Hopper backend")
    major, minor = torch.cuda.get_device_capability()
    return int(major), int(minor)


def _flash_qla_backend() -> Any:
    try:
        from fla.ops.gated_delta_rule.backends.flash_qla import FlashQLABackend
    except ImportError as error:
        raise ContractError("configured FlashQLA backend is unavailable") from error
    return FlashQLABackend()


def _base_evidence(
    configured: str | None, capability: tuple[int, int], status: str
) -> dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "configured_backend": configured,
        "status": status,
        "compute_capability": list(capability),
        "bound_modules": [],
        "bound_module_count": 0,
        "observed_calls": 0,
    }


def bind_required_hopper_backend(
    model: Any,
    runtime: Mapping[str, Any],
    *,
    compute_capability: tuple[int, int] | None = None,
    backend_factory: Callable[[], Any] = _flash_qla_backend,
) -> dict[str, Any]:
    """Bind Qwen linear layers directly to a configured Hopper backend.

    FLA's generic dispatcher deliberately falls back when a backend rejects a
    call. That policy is unsafe for this paid workflow because the fallback can
    compile for minutes and fail only in backward. A configured Hopper run uses
    FLA's own FlashQLA backend and turns any rejection into a precise error.
    """

    configured = runtime.get(CONFIG_KEY)
    if configured not in {None, "flash_qla"}:
        raise ContractError(
            f"runtime.{CONFIG_KEY} must be 'flash_qla' when configured"
        )
    capability = compute_capability or _device_capability()
    if configured is None:
        return _base_evidence(configured, capability, "not-configured")
    if capability[0] not in _SUPPORTED_CAPABILITIES:
        return _base_evidence(configured, capability, "not-applicable")

    backend = backend_factory()
    if not backend.is_available():
        raise ContractError("configured FlashQLA package is unavailable")
    if not backend.is_enabled():
        raise ContractError(
            "configured FlashQLA backend is disabled by FLA_FLASH_QLA"
        )

    modules = [
        (name, module)
        for name, module in model.named_modules()
        if name.endswith(".linear_attn")
        and callable(getattr(module, "chunk_gated_delta_rule", None))
    ]
    if not modules:
        raise ContractError("configured FlashQLA backend matched zero Qwen linear layers")

    evidence = _base_evidence(configured, capability, "bound")
    evidence["bound_modules"] = [name for name, _ in modules]
    evidence["bound_module_count"] = len(modules)

    def required_call(module_name: str) -> Callable[..., Any]:
        def call(*args: Any, **kwargs: Any) -> Any:
            accepted, reason = backend.verify(
                "chunk_gated_delta_rule", *args, **kwargs
            )
            if not accepted:
                raise ContractError(
                    f"FlashQLA rejected {module_name}: {reason or 'no reason provided'}"
                )
            result = backend.chunk_gated_delta_rule(*args, **kwargs)
            evidence["observed_calls"] += 1
            return result

        return call

    for name, module in modules:
        module.chunk_gated_delta_rule = required_call(name)
    return evidence


def validate_hopper_backend_evidence(value: object) -> dict[str, Any]:
    """Validate post-training evidence for the configured backend."""

    if not isinstance(value, Mapping):
        raise ContractError("Hopper backend evidence is invalid")
    evidence = dict(value)
    expected = {
        "protocol",
        "configured_backend",
        "status",
        "compute_capability",
        "bound_modules",
        "bound_module_count",
        "observed_calls",
    }
    if set(evidence) != expected or evidence.get("protocol") != PROTOCOL:
        raise ContractError("Hopper backend evidence is invalid")
    status = evidence.get("status")
    if status in {"not-configured", "not-applicable"}:
        if (
            evidence.get("bound_modules") != []
            or evidence.get("bound_module_count") != 0
            or evidence.get("observed_calls") != 0
        ):
            raise ContractError("inactive Hopper backend evidence contains calls")
        return evidence
    if status != "bound" or evidence.get("configured_backend") != "flash_qla":
        raise ContractError("Hopper backend evidence is invalid")
    modules = evidence.get("bound_modules")
    count = evidence.get("bound_module_count")
    calls = evidence.get("observed_calls")
    if (
        not isinstance(modules, list)
        or not modules
        or not all(isinstance(name, str) and name for name in modules)
        or isinstance(count, bool)
        or not isinstance(count, int)
        or count != len(modules)
    ):
        raise ContractError("Hopper backend binding evidence is invalid")
    if isinstance(calls, bool) or not isinstance(calls, int) or calls <= 0:
        raise ContractError("no observed FlashQLA layer calls")
    return evidence
