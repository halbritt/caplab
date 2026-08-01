"""Fail-closed CUDA driver and llama.cpp device readiness checks."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
import re
import subprocess
from typing import cast

from .contract import ContractError


CUDA_BACKEND_LIBRARY = Path("/opt/llama.cpp/build/bin/libggml-cuda.so")
LLAMA_CLI = Path("/opt/llama.cpp/build/bin/llama-cli")
MIN_H100_MEMORY_MIB = 80_000

_DRIVER = re.compile(
    r"^\s*libcuda\.so\.1\s+=>\s+(\S+)\s+\(0x[0-9a-fA-F]+\)\s*$",
    re.MULTILINE,
)
_DEVICE = re.compile(
    r"^\s*(CUDA[0-9]+):\s+(.+?)\s+"
    r"\(([0-9]+) MiB,\s+[0-9]+ MiB free\)\s*$",
    re.MULTILINE,
)


def inspect_cuda_runtime(
    cuda_backend_library: Path = CUDA_BACKEND_LIBRARY,
    llama_cli: Path = LLAMA_CLI,
) -> dict[str, object]:
    """Inspect the live driver binding and require exactly one H100 device."""

    if not cuda_backend_library.is_file():
        raise ContractError(
            f"llama.cpp CUDA backend is unavailable: {cuda_backend_library}"
        )
    if not llama_cli.is_file() or not llama_cli.stat().st_mode & 0o111:
        raise ContractError(f"llama.cpp CLI is unavailable: {llama_cli}")
    ldd_output = _run(("ldd", str(cuda_backend_library)), "CUDA driver resolution")
    devices_output = _run((str(llama_cli), "--list-devices"), "llama.cpp devices")
    return validate_cuda_observations(
        ldd_output,
        devices_output,
        cuda_backend_library=cuda_backend_library,
        llama_cli=llama_cli,
    )


def validate_cuda_observations(
    ldd_output: str,
    devices_output: str,
    *,
    cuda_backend_library: Path = CUDA_BACKEND_LIBRARY,
    llama_cli: Path = LLAMA_CLI,
) -> dict[str, object]:
    """Validate captured loader and device output and return its receipt."""

    drivers = _DRIVER.findall(ldd_output)
    if len(drivers) != 1:
        raise ContractError(
            "libcuda.so.1 did not resolve to exactly one driver library"
        )
    driver = Path(drivers[0])
    if not driver.is_absolute():
        raise ContractError("libcuda.so.1 resolved to a non-absolute driver path")
    if "stubs" in driver.parts:
        raise ContractError("libcuda.so.1 resolved to a CUDA stub library")

    devices = _DEVICE.findall(devices_output)
    if len(devices) != 1:
        raise ContractError("llama.cpp did not report exactly one CUDA device")
    backend, name, raw_memory_mib = devices[0]
    memory_mib = int(raw_memory_mib)
    if backend != "CUDA0" or "H100" not in name:
        raise ContractError("llama.cpp did not report the required H100 as CUDA0")
    if memory_mib < MIN_H100_MEMORY_MIB:
        raise ContractError("llama.cpp reported less than 80 GB for the H100")

    receipt: dict[str, object] = {
        "protocol": "striatum-cuda-runtime/1",
        "cuda_backend_library": str(cuda_backend_library),
        "driver_library": str(driver),
        "llama_cli": str(llama_cli),
        "device": {
            "backend": backend,
            "name": name,
            "memory_mib": memory_mib,
        },
    }
    return validate_cuda_runtime_receipt(receipt)


def validate_cuda_runtime_receipt(
    candidate: Mapping[str, object],
) -> dict[str, object]:
    """Validate a CUDA runtime receipt before terminal packaging."""

    expected_fields = {
        "protocol",
        "cuda_backend_library",
        "driver_library",
        "llama_cli",
        "device",
    }
    if set(candidate) != expected_fields:
        raise ContractError("CUDA runtime receipt fields are not exact")
    if candidate.get("protocol") != "striatum-cuda-runtime/1":
        raise ContractError("CUDA runtime receipt protocol is invalid")
    if candidate.get("cuda_backend_library") != str(CUDA_BACKEND_LIBRARY):
        raise ContractError("CUDA runtime receipt names another backend library")
    if candidate.get("llama_cli") != str(LLAMA_CLI):
        raise ContractError("CUDA runtime receipt names another llama.cpp CLI")
    driver_value = candidate.get("driver_library")
    if not isinstance(driver_value, str):
        raise ContractError("CUDA runtime receipt driver path is invalid")
    driver = Path(driver_value)
    if not driver.is_absolute() or "stubs" in driver.parts:
        raise ContractError("CUDA runtime receipt names a stub or relative driver")

    raw_device = candidate.get("device")
    if not isinstance(raw_device, Mapping):
        raise ContractError("CUDA runtime receipt device is invalid")
    device = cast(Mapping[str, object], raw_device)
    if set(device) != {"backend", "name", "memory_mib"}:
        raise ContractError("CUDA runtime receipt device fields are not exact")
    name = device.get("name")
    memory_mib = device.get("memory_mib")
    if (
        device.get("backend") != "CUDA0"
        or not isinstance(name, str)
        or "H100" not in name
    ):
        raise ContractError("CUDA runtime receipt does not identify the required H100")
    if (
        isinstance(memory_mib, bool)
        or not isinstance(memory_mib, int)
        or memory_mib < MIN_H100_MEMORY_MIB
    ):
        raise ContractError("CUDA runtime receipt H100 memory is invalid")
    return {
        "protocol": "striatum-cuda-runtime/1",
        "cuda_backend_library": str(CUDA_BACKEND_LIBRARY),
        "driver_library": str(driver),
        "llama_cli": str(LLAMA_CLI),
        "device": {
            "backend": "CUDA0",
            "name": name,
            "memory_mib": memory_mib,
        },
    }


def _run(command: Sequence[str], label: str) -> str:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ContractError(f"{label} command failed") from error
    if completed.returncode != 0:
        raise ContractError(f"{label} command exited {completed.returncode}")
    return completed.stdout + "\n" + completed.stderr
