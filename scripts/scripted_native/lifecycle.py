"""Prepare and anchor the fixed diagnostic before any native execution."""

import ast
import json
import os
import stat
from pathlib import Path

from caplab.codex_child_configuration import (
    CodexChildSourceEvidence,
    prepare_codex_child_configuration,
)
from caplab.native_capture_invocation import (
    NativeCaptureContext,
    build_native_capture_invocation,
)
from caplab.native_launch_configuration import (
    NativeLaunchContext,
    build_native_launch_configuration,
)
from caplab.process_capture import seal_capture_json
from caplab.task_capture_verify import _read_file
from probe_native_capture_startup import harness_manifest

REPO = Path(__file__).resolve().parents[2]
POLICY = REPO / "docs/product/contracts/native-agent-systems.json"
PROMPT = b"Local scripted capture diagnostic. Execute the supplied fixed tool call, then report completion. No external work."
RUNTIME_PATHS = (
    "/usr/bin/python3",
    "/usr/bin/node",
    "/usr/bin/strace",
    "/usr/bin/bwrap",
)
BINARY = (
    "node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex"
)
LIMITS = {
    "native_seconds": 30,
    "capture_seconds": 45,
    "unit_seconds": 90,
    "outer_seconds": 100,
    "workload_memory_bytes": 256 * 1024**2,
    "unit_memory_bytes": 512 * 1024**2,
    "swap_bytes": 0,
    "workload_tasks": 128,
    "unit_tasks": 192,
    "stream_bytes": 300000,
    "task_bytes": 1024**2,
    "task_entries": 1000,
    "collection_bytes": 8 * 1024**2,
    "collection_entries": 1000,
    "retained_mount_bytes": 40 * 1024**2,
    "retained_mount_entries": 2000,
    "trace_bytes": 2 * 1024**2,
    "native_file_bytes": 8 * 1024**2,
    "handshake_seconds": 5,
    "freeze_transition_seconds": 2,
}


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def digest(path, maximum=1024**2):
    return _read_file(None, Path(path), maximum, retain=False)[2]


def read_document(path, expected_sha256):
    raw, _, observed = _read_file(None, Path(path), 1024**2, retain=True)
    require(observed == expected_sha256, "document hash differs")
    return json.loads(raw)


def source_pins():
    # Pin active Python implementation, not historical trees, tests or bytecode.
    paths = list((REPO / "src/caplab").rglob("*.py"))
    paths += list(Path(__file__).parent.glob("*.py"))
    paths += [
        REPO / "scripts" / name
        for name in (
            "probe_native_capture_startup.py",
            "probe_cgroup_resource_limits.py",
            "probe_scripted_native_capture.py",
        )
        if (REPO / "scripts" / name).exists()
    ]
    paths.append(POLICY)
    require(len(paths) <= 1000, "implementation source population exceeds allowance")
    return [{"path": str(path), "sha256": digest(path)} for path in sorted(paths)]


def dependency_manifest(root):
    require(
        root.name == "websockets", "dependency root must name the websockets package"
    )
    manifest = harness_manifest(root)
    raw, _, _ = _read_file(None, root / "version.py", 65536, retain=True)
    assignments = {}
    for statement in ast.parse(raw).body:
        if isinstance(statement, ast.Assign) and isinstance(
            statement.value, ast.Constant
        ):
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = statement.value.value
    require(
        assignments.get("released") is True and assignments.get("version") == "15.0.1",
        "requires the supported websockets 15.0.1 release",
    )
    return manifest


def prepare(output, *, codex_root, websockets_root):
    output, source, dependency = Path(output), Path(codex_root), Path(websockets_root)
    require(
        output.is_absolute()
        and output.parent.resolve() == output.parent
        and not output.exists(),
        "fresh resolved custody root required",
    )
    require(
        all(
            not output.is_relative_to(path) and not path.is_relative_to(output)
            for path in (source, dependency)
        ),
        "custody overlaps an input tree",
    )
    installation = harness_manifest(source)
    library = dependency_manifest(dependency)
    invocation = build_native_capture_invocation(
        POLICY,
        "codex-terra-max",
        context=NativeCaptureContext("/work", "/episode", PROMPT),
    )
    launch = build_native_launch_configuration(
        POLICY,
        invocation,
        expected_invocation_sha256=invocation["invocation_sha256"],
        context=NativeLaunchContext("codex-scripted-local/v1", 1),
    )
    (binary,) = [entry for entry in installation["entries"] if entry["path"] == BINARY]
    source_check = prepare_codex_child_configuration(
        POLICY,
        invocation,
        launch,
        source,
        evidence=CodexChildSourceEvidence(
            invocation["invocation_sha256"],
            launch["launch_configuration_sha256"],
            binary["sha256"],
            1024**3,
        ),
    )
    pins = source_pins()
    runtime = [
        {
            "invoked_path": str(path),
            "path": str(path.resolve()),
            "sha256": digest(path.resolve(), 1024**3),
        }
        for path in map(Path, RUNTIME_PATHS)
    ]
    output.mkdir(mode=0o700)
    info = output.stat()
    prepared = {
        "schema": "caplab.scripted-native-preparation/v1",
        "custody_root": str(output),
        "custody_identity": {"device": info.st_dev, "inode": info.st_ino},
        "invocation": invocation,
        "harness_manifest": installation,
        "dependency_manifest": library,
        "source_profile": source_check["profile"],
        "source_files": source_check["source_files"],
        "implementation_pins": pins,
        "runtime_pins": runtime,
        "limits": dict(LIMITS),
        "attempt_limit": 1,
        "execution_authorized": False,
        "binding_complete": False,
        "study_eligible": False,
    }
    seal_capture_json(output, "preparation.json", prepared)
    return {
        "custody_root": str(output),
        "preparation_sha256": digest(output / "preparation.json"),
    }


def read_preparation(output, *, expected_sha256):
    output = Path(output)
    require(
        output.is_absolute() and output.resolve() == output,
        "resolved custody root required",
    )
    prepared = read_document(output / "preparation.json", expected_sha256)
    require(
        isinstance(prepared, dict)
        and set(prepared)
        == {
            "schema",
            "custody_root",
            "custody_identity",
            "invocation",
            "harness_manifest",
            "dependency_manifest",
            "source_profile",
            "source_files",
            "implementation_pins",
            "runtime_pins",
            "limits",
            "attempt_limit",
            "execution_authorized",
            "binding_complete",
            "study_eligible",
        },
        "invalid preparation fields",
    )
    require(
        prepared.get("schema") == "caplab.scripted-native-preparation/v1",
        "unsupported preparation",
    )
    require(
        prepared.get("custody_root") == str(output), "preparation custody root differs"
    )
    info = output.stat()
    require(
        prepared.get("custody_identity")
        == {"device": info.st_dev, "inode": info.st_ino},
        "preparation custody identity differs",
    )
    require(
        json.dumps(prepared.get("limits"), sort_keys=True, allow_nan=False)
        == json.dumps(LIMITS, sort_keys=True)
        and type(prepared.get("attempt_limit")) is int
        and prepared["attempt_limit"] == 1,
        "diagnostic limits differ",
    )
    require(
        prepared.get("execution_authorized") is False
        and prepared.get("study_eligible") is False
        and prepared.get("binding_complete") is False,
        "preparation cannot grant authority or eligibility",
    )
    expected = build_native_capture_invocation(
        POLICY,
        "codex-terra-max",
        context=NativeCaptureContext("/work", "/episode", PROMPT),
    )
    require(
        prepared.get("invocation") == expected, "fixed diagnostic invocation differs"
    )
    require(stat.S_IMODE(info.st_mode) & 0o077 == 0, "custody root is not private")
    runtime = prepared["runtime_pins"]
    require(
        isinstance(runtime, list)
        and len(runtime) == len(RUNTIME_PATHS)
        and all(
            isinstance(pin, dict) and set(pin) == {"invoked_path", "path", "sha256"}
            for pin in runtime
        )
        and [pin["invoked_path"] for pin in runtime] == list(RUNTIME_PATHS),
        "system runtime pins differ",
    )
    return prepared


def check_inputs(prepared):
    require(
        source_pins() == prepared["implementation_pins"],
        "implementation source changed",
    )
    require(
        harness_manifest(Path(prepared["harness_manifest"]["source"]))
        == prepared["harness_manifest"],
        "native installation changed",
    )
    require(
        dependency_manifest(Path(prepared["dependency_manifest"]["source"]))
        == prepared["dependency_manifest"],
        "fixture dependency changed",
    )
    for pin in prepared["runtime_pins"]:
        require(
            str(Path(pin["invoked_path"]).resolve()) == pin["path"]
            and digest(pin["path"], 1024**3) == pin["sha256"],
            "system runtime changed",
        )


def consume(
    output,
    *,
    expected_preparation_sha256,
    authorization_path,
    expected_authorization_sha256,
):
    """Validate independent anchors, then durably spend one attempt without launching.

    Caller owns actual authorization, private stable custody and input quiescence.
    A partial consumption file remains spent; no automatic repair or replay.
    """
    output = Path(output)
    prepared = read_preparation(output, expected_sha256=expected_preparation_sha256)
    authorization = read_document(authorization_path, expected_authorization_sha256)
    require(
        isinstance(authorization, dict)
        and set(authorization)
        == {
            "schema",
            "preparation_sha256",
            "custody_root",
            "attempt_limit",
            "decision_owner",
            "authority_source",
            "permitted_effect",
        },
        "invalid execution authorization fields",
    )
    require(
        authorization["schema"] == "caplab.scripted-native-authorization/v1"
        and authorization["permitted_effect"] == "one-scripted-native-diagnostic",
        "execution authorization effect differs",
    )
    require(
        authorization["preparation_sha256"] == expected_preparation_sha256
        and authorization["custody_root"] == str(output)
        and type(authorization["attempt_limit"]) is int
        and authorization["attempt_limit"] == 1,
        "execution authorization scope differs",
    )
    require(
        all(
            isinstance(authorization[key], str) and 0 < len(authorization[key]) <= 1024
            for key in ("decision_owner", "authority_source")
        ),
        "execution authority source is missing",
    )
    check_inputs(prepared)
    receipt = {
        "schema": "caplab.scripted-native-consumption/v1",
        "preparation_sha256": expected_preparation_sha256,
        "authorization_sha256": expected_authorization_sha256,
        "custody_root": str(output),
        "attempts_consumed": 1,
        "decision_owner": authorization["decision_owner"],
        "authority_source": authorization["authority_source"],
    }
    descriptor = os.open(
        output / "consumption.json",
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
        0o600,
    )
    with os.fdopen(descriptor, "w") as stream:
        json.dump(receipt, stream, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(
        output, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    )
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return receipt


def execute(
    output,
    *,
    expected_preparation_sha256,
    authorization_path,
    expected_authorization_sha256,
):
    """Spend the allowance before launch and seal available outcomes, including failure."""
    from . import runner

    output = Path(output)
    consume(
        output,
        expected_preparation_sha256=expected_preparation_sha256,
        authorization_path=authorization_path,
        expected_authorization_sha256=expected_authorization_sha256,
    )
    prepared = read_preparation(output, expected_sha256=expected_preparation_sha256)
    try:
        outcome = runner.run(output / "run", prepared, expected_preparation_sha256)
        check_inputs(prepared)
    except Exception as error:
        outcome = {
            "native_attempt_succeeded": False,
            "execution_error": {
                "type": type(error).__name__,
                "message": str(error)[:512],
            },
        }
    try:
        capture = (
            harness_manifest(output / "run") if (output / "run").is_dir() else None
        )
    except (OSError, RuntimeError, ValueError) as error:
        capture = None
        outcome = outcome | {
            "native_attempt_succeeded": False,
            "capture_manifest_error": {
                "type": type(error).__name__,
                "message": str(error)[:512],
            },
        }
    result = {
        "schema": "caplab.scripted-native-result/v1",
        "preparation_sha256": expected_preparation_sha256,
        "consumption_sha256": digest(output / "consumption.json"),
        "outcome": outcome,
        "capture_manifest": capture,
        "verification_performed": False,
        "binding_complete": False,
        "study_eligible": False,
    }
    runner.seal(output, "result.json", result)
    return {
        "result_sha256": digest(output / "result.json"),
        **outcome,
        "binding_complete": False,
        "study_eligible": False,
    }
