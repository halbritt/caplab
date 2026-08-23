from __future__ import annotations

import base64
import copy
import inspect
import json
import os
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource

from caplab.qualification import validate_measurement
from caplab.revbench.codex import (
    CODEX_NATIVE_BUNDLE_POLICY_SHA256,
    CodexAdapterError,
    CodexJSONLTransportError,
    CodexProcessObservation,
    CodexResponseSchemaError,
    _require_exact_tracked_package,
    codex_native_bundle_policy,
    codex_native_bundle_policy_bytes,
    credential_memfd,
    derive_codex_response,
    execution_apparatus_receipt,
    response_derivation_document,
)
from caplab.revbench import RevbenchContractError, execute, prepare, score
from caplab.revbench import __main__ as revbench_cli
from caplab.revbench.custody import FilesystemLiveExecutionRuntime
from caplab.runtime.canonical import CanonicalizationError, canonical_json, sha256_hex
from caplab.subject_identity import (
    NativeAgentSystemContractError,
    validate_native_agent_systems,
)
from tests.test_revbench import (
    MemoryRegistrar,
    make_execution_authorization,
    make_spec,
    registered,
    registered_bytes,
    reseal_execution,
    write_fake_native,
)


ROOT = Path(__file__).resolve().parents[1]
CODEX_EXECUTABLE = Path(
    "/home/halbritt/.npm-global/lib/node_modules/@openai/codex/node_modules/"
    "@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex"
)
LIVE_SUBJECT = "acct_0123456789abcdef0123456789abcdef"
LIVE_ACCOUNT = "workspace_0123456789abcdef0123456789abcdef"
LIVE_EMAIL = "private.person.7f31@example.invalid"
LIVE_NAME = "Private Sentinel Name 7f31"
LIVE_CUSTOM_KEY = "private_claim_key_sentinel_7f31"
LIVE_CUSTOM_VALUE = "private claim value 7f31"
LIVE_ORG_ID = "org_0123456789abcdef7f31"
LIVE_ORG_LABEL = "Private Sentinel Organization 7f31"
LIVE_NESTED_KEY = "private_nested_claim_key_sentinel_7f31"
LIVE_NESTED_VALUE = "private nested claim value 7f31"
LIVE_SHORT_NESTED_KEY = "shortkey7f31"
LIVE_SHORT_NESTED_VALUE = "private short nested claim value 7f31"
LIVE_LIST_VALUE = "private custom list value 7f31"
LIVE_SHORT_TOP_LEVEL_KEY = "shorttop7f31"


def source_tree_snapshot(root: Path) -> tuple[tuple[str, str, str], ...]:
    """Return an exact, path-local snapshot for source-mutation assertions."""

    entries: list[tuple[str, str, str]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            entries.append((relative, "symlink", os.readlink(path)))
        elif path.is_file():
            entries.append((relative, "file", sha256_hex(path.read_bytes())))
        elif path.is_dir():
            entries.append((relative, "directory", ""))
        else:
            entries.append((relative, "other", ""))
    return tuple(entries)


def synthetic_clean_apparatus():
    receipt = execution_apparatus_receipt(require_clean=False)
    receipt["caplab"]["checkout_state"] = "clean"
    identity = copy.deepcopy(receipt)
    identity.pop("apparatus_id")
    receipt["apparatus_id"] = "apparatus-" + sha256_hex(canonical_json(identity))
    return receipt


def synthetic_live_credential(*, extra_nested_claims=None) -> bytes:
    organization = {
        "id": LIVE_ORG_ID,
        "label": LIVE_ORG_LABEL,
        LIVE_NESTED_KEY: LIVE_NESTED_VALUE,
        **(extra_nested_claims or {}),
    }
    token = ".".join(
        (
            base64.urlsafe_b64encode(
                canonical_json(
                    {"alg": "RS256", "kid": "kid_0123456789abcdef", "typ": "JWT"}
                )
            )
            .rstrip(b"=")
            .decode(),
            base64.urlsafe_b64encode(
                canonical_json(
                    {
                        "sub": LIVE_SUBJECT,
                        "iss": "https://auth.openai.com",
                        "aud": ["https://api.openai.com/v1"],
                        "iat": 1_700_000_000,
                        "exp": 4_102_444_800,
                        "email": LIVE_EMAIL,
                        "name": LIVE_NAME,
                        LIVE_CUSTOM_KEY: LIVE_CUSTOM_VALUE,
                        "organization": organization,
                    }
                )
            )
            .rstrip(b"=")
            .decode(),
            "c2lnbmF0dXJlX2J5dGVz",
        )
    )
    return canonical_json(
        {
            "auth_mode": "chatgpt",
            "OPENAI_API_KEY": None,
            "tokens": {
                "id_token": token,
                "access_token": "private-access-token",
                "refresh_token": "private-refresh-token",
                "account_id": LIVE_ACCOUNT,
            },
            "last_refresh": "2026-08-14T00:00:00Z",
        }
    )


def make_live_codex_binding(
    registrar: MemoryRegistrar,
    *,
    policy=None,
    member_bytes=None,
):
    policy = copy.deepcopy(policy or codex_native_bundle_policy())
    member_bytes = member_bytes or {}

    def resolved_member(role: str, path: str) -> bytes:
        if role in member_bytes:
            return member_bytes[role]
        repository_resources = {
            "resource:resolver": (
                ROOT / "src/caplab/revbench/contracts/resolv-public-v1.conf"
            ),
            "resource:nsswitch": (
                ROOT / "src/caplab/revbench/contracts/nsswitch-public-v1.conf"
            ),
        }
        if role in repository_resources:
            return repository_resources[role].read_bytes()
        return Path(path).read_bytes()

    launcher = policy["launcher"]
    provider = {
        "kind": "direct-provider",
        "identifier": "openai",
        "revision": "responses-api",
        "resolution": "configured-route",
        "observed_at": None,
    }
    route_ref = registered(
        registrar,
        "codex-live-route",
        {"schema_version": "caplab-provider-route/1", **provider},
        kind="provider-route",
        schema="caplab-provider-route/1",
    )
    executable_ref = registered_bytes(
        registrar,
        "codex-native-executable",
        resolved_member("executable", str(CODEX_EXECUTABLE)),
        kind="harness-executable",
        schema="caplab-native-executable/1",
    )
    command_ref = registered(
        registrar,
        "codex-live-command",
        {
            "schema_version": "caplab-native-harness-command/1",
            "argv": launcher["review_argv"],
        },
        kind="native-harness-command",
        schema="caplab-native-harness-command/1",
    )
    version_command_ref = registered(
        registrar,
        "codex-live-version-command",
        {
            "schema_version": "caplab-native-harness-version-command/1",
            "argv": launcher["version_argv"],
        },
        kind="native-harness-version-command",
        schema="caplab-native-harness-version-command/1",
    )
    version_stdout_ref = registered_bytes(
        registrar,
        "codex-live-version-stdout",
        b"codex-cli 0.147.0\n",
        kind="native-harness-version-stdout",
        schema="caplab-native-process-stream/1",
    )
    version_stderr_ref = registered_bytes(
        registrar,
        "codex-live-version-stderr",
        b"",
        kind="native-harness-version-stderr",
        schema="caplab-native-process-stream/1",
    )
    version_probe_ref = registered(
        registrar,
        "codex-live-version-probe",
        {
            "command_ref": version_command_ref,
            "exit_code": 0,
            "stdout_ref": version_stdout_ref,
            "stderr_ref": version_stderr_ref,
        },
        kind="native-harness-version-probe",
        schema="caplab-native-harness-version-probe/1",
    )
    bundle_policy_ref = registered(
        registrar,
        "codex-live-bundle-policy",
        policy,
        kind="native-runtime-bundle-policy",
        schema="caplab-revbench-codex-native-bundle-policy/1",
    )
    response_schema_ref = registered(
        registrar,
        "codex-live-response-schema",
        policy["response_schema"],
        kind="native-response-schema",
        schema="caplab-revbench-native-response-schema/1",
    )
    sandbox_ref = registered_bytes(
        registrar,
        "codex-live-bwrap",
        resolved_member("adapter", policy["containment"]["adapter_path"]),
        kind="sandbox-executable",
        schema="caplab-native-executable/1",
    )
    runtime_resource_refs = {
        name: registered_bytes(
            registrar,
            f"codex-live-resource-{name}",
            resolved_member(f"resource:{name}", path),
            kind="native-runtime-resource",
            schema="caplab-native-runtime-resource/1",
        )
        for name, path in {
            "ca_certificates": policy["containment"]["ca_certificates_target"],
            "resolver": policy["containment"]["resolver_target"],
            "nsswitch": policy["containment"]["nsswitch_target"],
        }.items()
    }
    adapter_runtime = policy["adapter_runtime"]
    loader_ref = registered_bytes(
        registrar,
        "codex-live-bwrap-loader",
        resolved_member("adapter-loader", adapter_runtime["loader"]["path"]),
        kind="sandbox-runtime-resource",
        schema="caplab-native-runtime-resource/1",
    )
    library_refs = [
        {
            "name": library["name"],
            "ref": registered_bytes(
                registrar,
                f"codex-live-bwrap-{library['name']}",
                resolved_member(f"adapter-library:{library['name']}", library["path"]),
                kind="sandbox-runtime-resource",
                schema="caplab-native-runtime-resource/1",
            ),
        }
        for library in adapter_runtime["libraries"]
    ]
    credential_profile_ref = registered(
        registrar,
        "codex-live-credential-profile",
        {
            "schema_version": "caplab-revbench-codex-credential-profile/1",
            "profile_id": "caplab-openai-revbench",
            "provider": "openai",
            "auth_method": "chatgpt",
            "identity_basis": "operator-declared-unverified-token-claims",
            "provider_account_id_sha256": sha256_hex(LIVE_ACCOUNT.encode()),
            "provider_subject_sha256": sha256_hex(LIVE_SUBJECT.encode()),
            "identity_token_issuer": "https://auth.openai.com",
            "identity_token_audience": ["https://api.openai.com/v1"],
        },
        kind="credential-profile",
        schema="caplab-revbench-codex-credential-profile/1",
    )
    configurations = {}
    documents = {
        "inference": {
            "schema_version": "caplab-revbench-codex-inference/1",
            "command_ref": command_ref,
            "bundle_policy_ref": bundle_policy_ref,
            "response_adapter": policy["response_adapter"],
        },
        "instructions": {
            "schema_version": "caplab-revbench-instructions/1",
            "instruction": (
                "Review the artifact against the requirement and return exactly one JSON object."
            ),
        },
        "knowledge": {
            "schema_version": "caplab-revbench-disabled-surface/1",
            "surface": "knowledge",
            "mode": "none",
        },
        "tools": {
            "schema_version": "caplab-revbench-codex-tools/1",
            "surface": "tools",
            "mode": "native-harness-empty-root",
            "host_shell_mounted": False,
            "host_filesystem_mounted": False,
            "user_configuration": "ignored",
            "rules": "ignored",
            "mcp_servers": [],
            "plugins": [],
            "web_search": "disabled",
        },
        "permissions": {
            "schema_version": "caplab-revbench-codex-permissions/1",
            "environment_keys": sorted(policy["environment"]),
            "filesystem_mode": "empty-root-private-cwd",
            "network_mode": "ambient-authorized",
        },
        "sandbox": {
            "schema_version": "caplab-revbench-codex-sandbox/1",
            "adapter_path": policy["containment"]["adapter_path"],
            "adapter_ref": sandbox_ref,
            "root_filesystem": "empty-tmpfs",
            "working_directory": "private-write",
            "network_mode": "ambient-authorized",
            "namespace": "empty-root-unshare-all-share-net",
            "die_with_parent": True,
            "new_session": True,
            "shell_mounted": False,
            "host_filesystem_mounted": False,
        },
        "runtime": {
            "schema_version": "caplab-revbench-codex-runtime/1",
            "bundle_policy_ref": bundle_policy_ref,
            "tuple_id": "codex-terra-max",
            "executable_ref": executable_ref,
            "sandbox_adapter_ref": sandbox_ref,
            "adapter_runtime_refs": {
                "loader_ref": loader_ref,
                "library_refs": library_refs,
            },
            "ca_certificates_ref": runtime_resource_refs["ca_certificates"],
            "resolver_ref": runtime_resource_refs["resolver"],
            "nsswitch_ref": runtime_resource_refs["nsswitch"],
            "response_schema_ref": response_schema_ref,
            "credential_profile_ref": credential_profile_ref,
            "environment": policy["environment"],
            "working_directory": "/work",
            "network_mode": "ambient-authorized",
            "stdin_mode": "canonical-json",
            "stdout_mode": "codex-jsonl",
            "custody_mode": "durable-prefix-one-shot",
        },
    }
    kinds = {
        "inference": "inference-configuration",
        "instructions": "instructions",
        "knowledge": "knowledge",
        "tools": "tools",
        "permissions": "permissions",
        "sandbox": "sandbox",
        "runtime": "runtime",
    }
    for name, document in documents.items():
        configurations[f"{name}_ref"] = registered(
            registrar,
            f"codex-live-{name}",
            document,
            kind=kinds[name],
            schema="caplab-binding-configuration/1",
        )
    binding = {
        "schema_version": "caplab-binding/1",
        "model": {
            "model_id": "gpt-5.6-terra",
            "revision": "provider-hosted",
            "weights_ref": None,
            "weights_unavailable_reason": "provider-hosted weights are unavailable",
        },
        "provider_or_path": {**provider, "route_ref": route_ref},
        "harness": {
            "harness_id": "codex",
            "harness_version": "codex-cli 0.147.0",
            "executable_ref": executable_ref,
            "executable_unavailable_reason": None,
            "command_ref": command_ref,
            "version_probe_ref": version_probe_ref,
        },
        "reasoning_effort": "max",
        "configuration": configurations,
    }
    binding["binding_id"] = "bnd-" + sha256_hex(canonical_json(binding))
    native_policy_ref = registered(
        registrar,
        "repository-native-system-contract",
        json.loads(
            (ROOT / "docs/product/contracts/native-agent-systems.json").read_bytes()
        ),
        kind="native-agent-systems-contract",
        schema="caplab.native-agent-systems/v1",
    )
    return binding, native_policy_ref


def make_synthetic_bundle_fixture(root: Path):
    executable = root / "synthetic-codex"
    write_fake_native(executable, version="codex-cli 0.147.0\n")
    elf = executable.read_bytes()
    policy = copy.deepcopy(codex_native_bundle_policy())
    policy["launcher"]["executable_sha256"] = sha256_hex(elf)
    policy["launcher"]["executable_byte_count"] = len(elf)
    policy["containment"]["adapter_path"] = "/synthetic/bwrap"
    policy["containment"]["adapter_sha256"] = sha256_hex(elf)
    policy["containment"]["adapter_byte_count"] = len(elf)
    members = {"executable": elf, "adapter": elf}
    loader = b"synthetic-loader"
    policy["adapter_runtime"]["loader"]["path"] = "/synthetic/loader"
    policy["adapter_runtime"]["loader"]["sha256"] = sha256_hex(loader)
    policy["adapter_runtime"]["loader"]["byte_count"] = len(loader)
    members["adapter-loader"] = loader
    for index, library in enumerate(policy["adapter_runtime"]["libraries"]):
        payload = f"synthetic-library-{index}".encode()
        library["path"] = f"/synthetic/{library['name']}"
        library["sha256"] = sha256_hex(payload)
        library["byte_count"] = len(payload)
        members[f"adapter-library:{library['name']}"] = payload
    for name, resource in policy["pinned_host_resources"].items():
        payload = f"synthetic-resource-{name}".encode()
        resource["sha256"] = sha256_hex(payload)
        resource["byte_count"] = len(payload)
        members[f"resource:{name}"] = payload
    return policy, members


def _content_id(document, field: str, prefix: str) -> str:
    identity = copy.deepcopy(document)
    identity.pop(field)
    return prefix + sha256_hex(canonical_json(identity))


def reseal_live_attempt(
    registrar: MemoryRegistrar,
    projection,
    *,
    output_changes,
    disposition,
    verdict,
    anchors,
    harness_completion,
):
    output = json.loads(registrar.resolve(projection["output_ref"]))
    output.update(copy.deepcopy(output_changes))
    output_ref = registered(
        registrar,
        f"tampered-output-{sha256_hex(canonical_json(output))}",
        output,
        kind="live-native-output",
        schema="caplab-live-native-output/1",
    )
    attestation = json.loads(registrar.resolve(projection["attestation_ref"]))
    capture = json.loads(registrar.resolve(attestation["capture_ref"]))
    capture.update(
        {
            "capture_id": "",
            "output_ref": output_ref,
            "native_harness_completion": harness_completion,
        }
    )
    capture["capture_id"] = _content_id(capture, "capture_id", "live-capture-")
    capture_ref = registered(
        registrar,
        capture["capture_id"],
        capture,
        kind="live-native-attempt-capture",
        schema="caplab-live-native-attempt-capture/1",
    )
    attestation.update(
        {
            "attestation_id": "",
            "capture_ref": capture_ref,
            "output_ref": output_ref,
        }
    )
    attestation["attestation_id"] = _content_id(
        attestation, "attestation_id", "live-attestation-"
    )
    attestation_ref = registered(
        registrar,
        attestation["attestation_id"],
        attestation,
        kind="live-native-attempt-attestation",
        schema="caplab-live-native-attempt-attestation/1",
    )
    envelope = json.loads(registrar.resolve(projection["attempt_ref"]))
    envelope.update(
        {
            "attempt_id": "",
            "attestation_ref": attestation_ref,
            "output_ref": output_ref,
            "disposition": disposition,
            "verdict": verdict,
            "anchors": copy.deepcopy(anchors),
        }
    )
    envelope["attempt_id"] = _content_id(envelope, "attempt_id", "live-attempt-")
    attempt_ref = registered(
        registrar,
        envelope["attempt_id"],
        envelope,
        kind="attempt",
        schema="caplab-live-native-review-attempt/1",
    )
    projection.update(
        {
            "attempt_ref": attempt_ref,
            "attestation_ref": attestation_ref,
            "output_ref": output_ref,
            "disposition": disposition,
            "verdict": verdict,
            "anchors": copy.deepcopy(anchors),
        }
    )


class CodexResponseAdapterTests(unittest.TestCase):
    def test_installed_bundle_policy_has_the_repository_pinned_byte_identity(self):
        payload = codex_native_bundle_policy_bytes()
        self.assertEqual(sha256_hex(payload), CODEX_NATIVE_BUNDLE_POLICY_SHA256)
        policy = codex_native_bundle_policy()
        self.assertEqual(
            policy["native_agent_system"]["canonical_policy_sha256"],
            "56bd254c2500d4d5913460aae307cbf5b81aafdb1830d5fe66a7d429432fc5d2",
        )
        self.assertEqual(policy["native_agent_system"]["tuple_id"], "codex-terra-max")
        self.assertEqual(
            policy["launcher"]["executable_sha256"],
            "cb0a15567e9a60a5820d54b0f6ae86d504dc3805c1eab21a47f70e3eb7b73a40",
        )

    @unittest.skipUnless(os.environ.get("HOME") == "/home/halbritt",
                         "pins this host's exact CA bundle bytes; host-bound")
    def test_pinned_adapter_and_network_resources_match_same_exact_bytes(self):
        policy = codex_native_bundle_policy()
        resources = {
            "ca_certificates": Path("/etc/ssl/certs/ca-certificates.crt"),
            "resolver": ROOT / "src/caplab/revbench/contracts/resolv-public-v1.conf",
            "nsswitch": ROOT / "src/caplab/revbench/contracts/nsswitch-public-v1.conf",
        }
        for name, path in resources.items():
            with self.subTest(resource=name):
                payload = path.read_bytes()
                pinned = policy["pinned_host_resources"][name]
                self.assertEqual(len(payload), pinned["byte_count"])
                self.assertEqual(sha256_hex(payload), pinned["sha256"])
                if name in {"resolver", "nsswitch"}:
                    self.assertEqual(pinned["source"], f"repository:{path.name}")
                    self.assertNotIn(b"search ", payload)
                    self.assertNotIn(b"domain ", payload)
        adapter = Path(policy["containment"]["adapter_path"]).read_bytes()
        self.assertEqual(len(adapter), policy["containment"]["adapter_byte_count"])
        self.assertEqual(sha256_hex(adapter), policy["containment"]["adapter_sha256"])
        adapter_members = [
            policy["adapter_runtime"]["loader"],
            *policy["adapter_runtime"]["libraries"],
        ]
        for member in adapter_members:
            with self.subTest(adapter_member=member["path"]):
                payload = Path(member["path"]).read_bytes()
                self.assertEqual(len(payload), member["byte_count"])
                self.assertEqual(sha256_hex(payload), member["sha256"])

    def test_apparatus_bootstrap_is_stable_before_and_after_bundle_resolution(self):
        first = execution_apparatus_receipt(require_clean=False)
        codex_native_bundle_policy()
        second = execution_apparatus_receipt(require_clean=False)

        self.assertEqual(first, second)

    def test_apparatus_inventory_covers_complete_runtime_trees(self):
        receipt = execution_apparatus_receipt(require_clean=False)
        identities = {
            member["identity"] for member in receipt["python"]["loaded_runtime_members"]
        }
        expected = set()
        excluded = {
            Path(os.path.abspath(value))
            for name in ("purelib", "platlib")
            if isinstance((value := sysconfig.get_path(name)), str) and value
        }
        seen_roots = set()
        for root_name in ("stdlib", "platstdlib"):
            root = Path(os.path.abspath(sysconfig.get_path(root_name)))
            if root.resolve() in seen_roots:
                continue
            seen_roots.add(root.resolve())
            for path in root.rglob("*"):
                absolute = Path(os.path.abspath(path))
                if any(
                    absolute == candidate or candidate in absolute.parents
                    for candidate in excluded
                ):
                    continue
                if path.is_file():
                    expected.add(
                        f"python-runtime:{root_name}:{path.relative_to(root).as_posix()}"
                    )
        self.assertTrue(expected.issubset(identities))

    def test_apparatus_id_is_stable_across_fresh_preflight_and_execute_processes(self):
        scripts = (
            (
                "from caplab.revbench.codex import execution_apparatus_receipt;"
                "print(execution_apparatus_receipt(require_clean=False)['apparatus_id'])"
            ),
            (
                "from datetime import datetime;"
                "from caplab.revbench.codex import codex_native_bundle_policy,"
                "execution_apparatus_receipt;"
                "codex_native_bundle_policy();"
                "datetime.strptime('2026-08-15T00:00:00Z','%Y-%m-%dT%H:%M:%SZ');"
                "print(execution_apparatus_receipt(require_clean=False)['apparatus_id'])"
            ),
        )
        observed = []
        for script in scripts:
            result = subprocess.run(
                [sys.executable, "-c", script],
                cwd=ROOT,
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONPATH": str(ROOT / "src"),
                    "PYTHONDONTWRITEBYTECODE": "1",
                },
                check=True,
                capture_output=True,
                text=True,
            )
            observed.append(result.stdout.strip())

        self.assertEqual(observed[0], observed[1])

    def test_isolated_source_authority_preflight_is_cross_process_stable(self):
        with tempfile.TemporaryDirectory() as temporary:
            outer = Path(temporary)
            repository = outer / "repository"
            package = repository / "src" / "caplab"
            package.parent.mkdir(parents=True)
            shutil.copytree(ROOT / "src" / "caplab", package)
            for cache in package.rglob("__pycache__"):
                shutil.rmtree(cache)
            shutil.copy2(ROOT / "pyproject.toml", repository / "pyproject.toml")
            subprocess.run(["/usr/bin/git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(
                ["/usr/bin/git", "add", "src/caplab", "pyproject.toml"],
                cwd=repository,
                check=True,
            )
            subprocess.run(
                [
                    "/usr/bin/git",
                    "-c",
                    "user.name=CAPLAB",
                    "-c",
                    "user.email=caplab@example.invalid",
                    "commit",
                    "-qm",
                    "isolated apparatus fixture",
                ],
                cwd=repository,
                check=True,
            )
            operations = outer / "operations"
            operations.mkdir(mode=0o700)
            ledger = operations / "ledger"
            custody = operations / "custody"
            custody.mkdir(mode=0o700)
            entrypoint = package / "revbench" / "live_entrypoint.py"
            outputs = [operations / f"authority-{index}.json" for index in range(2)]
            commands = (
                [str(entrypoint)],
                ["src/caplab/revbench/live_entrypoint.py"],
            )

            for output, script_token in zip(outputs, commands, strict=True):
                result = subprocess.run(
                    [
                        "/usr/bin/python3",
                        "-I",
                        "-S",
                        "-B",
                        "-X",
                        "pycache_prefix=/nonexistent/caplab-revbench-pycache-v1",
                        *script_token,
                        "prepare-live-runtime",
                        "--ledger",
                        str(ledger),
                        "--live-custody-root",
                        str(custody),
                        "--output",
                        str(output),
                    ],
                    cwd=repository,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

            first = json.loads(outputs[0].read_bytes())
            second = json.loads(outputs[1].read_bytes())
            self.assertEqual(first, second)
            self.assertEqual(first["apparatus_ref"], second["apparatus_ref"])
            custody_root = custody / "revbench-live-effects"
            for empty_directory in (
                "authorizations",
                "effect-intents",
                "effects",
                "manifests",
            ):
                self.assertEqual(list((custody_root / empty_directory).iterdir()), [])

    def test_apparatus_validation_is_independent_of_scorer_process_flags(self):
        receipt = execution_apparatus_receipt(require_clean=False)
        with tempfile.TemporaryDirectory() as temporary:
            receipt_path = Path(temporary) / "apparatus.json"
            receipt_path.write_bytes(canonical_json(receipt))
            script = (
                "import json,sys;"
                f"sys.path.insert(0,{str(ROOT / 'src')!r});"
                "from caplab.revbench.codex import validate_execution_apparatus_receipt;"
                f"document=json.load(open({str(receipt_path)!r},encoding='utf-8'));"
                "validate_execution_apparatus_receipt(document,allow_dirty=True);"
                "print('valid')"
            )
            result = subprocess.run(
                [sys.executable, "-I", "-S", "-B", "-c", script],
                check=True,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.stdout, "valid\n")

    def test_live_entrypoint_requires_the_isolated_source_profile(self):
        entrypoint = ROOT / "src" / "caplab" / "revbench" / "live_entrypoint.py"
        refused = subprocess.run(
            ["/usr/bin/python3", str(entrypoint), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(
            refused.stderr.encode(),
            canonical_json(
                {
                    "schema_version": "caplab-revbench-error/1",
                    "error_type": "RevbenchContractError",
                    "code": "live_source_invocation_profile_required",
                    "message": "live_source_invocation_profile_required",
                }
            )
            + b"\n",
        )
        error_schema = json.loads(
            (ROOT / "docs/product/contracts/revbench-error-v1.schema.json").read_bytes()
        )
        Draft202012Validator.check_schema(error_schema)
        Draft202012Validator(error_schema).validate(json.loads(refused.stderr))

        for extra_option in (("-X", "dev"), ("-W", "error")):
            hostile = subprocess.run(
                [
                    "/usr/bin/python3",
                    "-I",
                    "-S",
                    "-B",
                    *extra_option,
                    "-X",
                    "pycache_prefix=/nonexistent/caplab-revbench-pycache-v1",
                    str(entrypoint),
                    "--help",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            with self.subTest(extra_option=extra_option):
                self.assertEqual(hostile.returncode, 2)
                self.assertEqual(hostile.stderr.encode(), refused.stderr.encode())

        relative = subprocess.run(
            [
                "/usr/bin/python3",
                "-I",
                "-S",
                "-B",
                "-X",
                "pycache_prefix=/nonexistent/caplab-revbench-pycache-v1",
                "src/caplab/revbench/live_entrypoint.py",
                "--help",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(relative.returncode, 0, relative.stderr)
        self.assertIn("prepare-live-runtime", relative.stdout)
        supported_prog = " ".join(
            (
                "/usr/bin/python3",
                "-I",
                "-S",
                "-B",
                "-X",
                "pycache_prefix=/nonexistent/caplab-revbench-pycache-v1",
                str(entrypoint.resolve()),
            )
        )
        self.assertIn(f"usage: {supported_prog}", relative.stdout)
        self.assertNotIn("python -m caplab.revbench", relative.stdout)

        module_help = subprocess.run(
            [sys.executable, "-m", "caplab.revbench", "--help"],
            cwd=ROOT,
            env=dict(os.environ, PYTHONPATH=str(ROOT / "src")),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(module_help.returncode, 0, module_help.stderr)
        self.assertNotIn("prepare-live-runtime", module_help.stdout)
        self.assertNotIn("--credential-root", module_help.stdout)
        self.assertIn("local fixture", module_help.stdout)

        source_root = ROOT / "src"
        source_before = source_tree_snapshot(source_root)
        self.addCleanup(
            lambda: self.assertEqual(
                source_tree_snapshot(source_root),
                source_before,
                "live-entrypoint tests must not mutate the shared source tree",
            )
        )
        with tempfile.TemporaryDirectory() as temporary:
            checkout = Path(temporary) / "disposable-checkout"
            head = subprocess.run(
                ["/usr/bin/git", "-C", str(ROOT), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            subprocess.run(
                [
                    "/usr/bin/git",
                    "clone",
                    "--quiet",
                    "--no-checkout",
                    "--no-hardlinks",
                    str(ROOT),
                    str(checkout),
                ],
                check=True,
            )
            subprocess.run(
                [
                    "/usr/bin/git",
                    "-C",
                    str(checkout),
                    "checkout",
                    "--quiet",
                    "--detach",
                    head,
                ],
                check=True,
            )
            shadow = checkout / "src" / "secrets.py"
            self.assertFalse(shadow.exists())
            shadow.write_text(
                "raise RuntimeError('live source root shadow imported')\n",
                encoding="utf-8",
            )
            disposable_entrypoint = (
                checkout / "src" / "caplab" / "revbench" / "live_entrypoint.py"
            )
            accepted = subprocess.run(
                [
                    "/usr/bin/python3",
                    "-I",
                    "-S",
                    "-B",
                    "-X",
                    "pycache_prefix=/nonexistent/caplab-revbench-pycache-v1",
                    str(disposable_entrypoint),
                    "--help",
                ],
                cwd=checkout,
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertIn("prepare-live-runtime", accepted.stdout)
        self.assertEqual(source_tree_snapshot(source_root), source_before)

    def test_live_apparatus_refuses_ignored_symlink_and_regular_package_members(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary)
            package = repository / "src" / "caplab"
            package.mkdir(parents=True)
            (package / "__init__.py").write_text("\n", encoding="utf-8")
            (repository / ".gitignore").write_text(
                "src/caplab/ignored-*\n", encoding="utf-8"
            )
            subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
            subprocess.run(
                ["git", "add", ".gitignore", "src/caplab/__init__.py"],
                cwd=repository,
                check=True,
            )
            _require_exact_tracked_package(repository, package)

            symlink = package / "ignored-symlink.py"
            symlink.symlink_to("__init__.py")
            with self.assertRaisesRegex(CodexAdapterError, "symlink_refused"):
                _require_exact_tracked_package(repository, package)
            symlink.unlink()

            ignored = package / "ignored-regular.py"
            ignored.write_text("sentinel = True\n", encoding="utf-8")
            with self.assertRaisesRegex(CodexAdapterError, "untracked_package"):
                _require_exact_tracked_package(repository, package)

    def test_derives_the_last_agent_message_before_the_terminal_turn(self):
        response = {
            "schema_version": "caplab-revbench-native-response/1",
            "verdict": "defect",
            "anchors": ["/n"],
        }
        events = [
            {"type": "thread.started", "thread_id": "thread-1"},
            {"type": "turn.started"},
            {
                "type": "item.completed",
                "item": {
                    "id": "item-1",
                    "type": "agent_message",
                    "text": json.dumps(response, indent=2),
                },
            },
            {"type": "turn.completed", "usage": {"input_tokens": 1}},
        ]
        raw = b"".join(canonical_json(event) + b"\n" for event in events)

        derived = derive_codex_response(raw)

        self.assertEqual(derived.response, response)
        self.assertEqual(derived.response_bytes, canonical_json(response))
        self.assertEqual(derived.selected_event_index, 2)
        self.assertEqual(derived.selected_item_id, "item-1")
        stdout_ref = {"sha256": sha256_hex(raw)}
        response_ref = {"sha256": sha256_hex(derived.response_bytes)}
        self.assertEqual(
            response_derivation_document(derived, stdout_ref, response_ref),
            {
                "schema_version": "caplab-revbench-response-derivation/1",
                "adapter": "codex-jsonl-final-agent-message/1",
                "raw_stdout_ref": stdout_ref,
                "selected_event_index": 2,
                "selected_event_type": "item.completed",
                "selected_item_id": "item-1",
                "extracted_text_sha256": sha256_hex(
                    json.dumps(response, indent=2).encode()
                ),
                "derived_response_ref": response_ref,
            },
        )

    def test_rejects_nonterminal_or_ambiguous_jsonl(self):
        response = canonical_json(
            {
                "schema_version": "caplab-revbench-native-response/1",
                "verdict": "clean",
                "anchors": [],
            }
        ).decode()
        valid_message = {
            "type": "item.completed",
            "item": {"id": "item-1", "type": "agent_message", "text": response},
        }
        hostile = (
            b'{"type":"thread.started","type":"turn.started"}\n',
            canonical_json({"type": "thread.started"})
            + b"\n"
            + canonical_json(valid_message)
            + b"\n",
            canonical_json({"type": "thread.started"})
            + b"\n"
            + canonical_json(valid_message)
            + b"\n"
            + canonical_json({"type": "turn.completed"})
            + b"\n"
            + canonical_json({"type": "item.completed", "item": {}})
            + b"\n",
            canonical_json({"type": "thread.started"})
            + b"\n"
            + canonical_json(valid_message)
            + b"\n"
            + canonical_json({"type": "turn.completed"}),
            canonical_json({"type": "thread.started"})
            + b"\n"
            + canonical_json({"type": "thread.started"})
            + b"\n"
            + canonical_json({"type": "turn.started"})
            + b"\n"
            + canonical_json(valid_message)
            + b"\n"
            + canonical_json({"type": "turn.completed"})
            + b"\n",
            canonical_json({"type": "thread.started"})
            + b"\n"
            + canonical_json(valid_message)
            + b"\n"
            + canonical_json({"type": "turn.completed"})
            + b"\n",
            canonical_json({"type": "thread.started"})
            + b"\n"
            + canonical_json({"type": "turn.started"})
            + b"\n"
            + canonical_json({"type": "turn.started"})
            + b"\n"
            + canonical_json(valid_message)
            + b"\n"
            + canonical_json({"type": "turn.completed"})
            + b"\n",
        )
        for payload in hostile:
            with self.subTest(payload=payload):
                with self.assertRaises(CodexAdapterError):
                    derive_codex_response(payload)

    def test_distinguishes_terminal_invalid_response_from_transport_failure(self):
        terminal_invalid = b"".join(
            canonical_json(event) + b"\n"
            for event in (
                {"type": "thread.started", "thread_id": "thread-1"},
                {"type": "turn.started"},
                {
                    "type": "item.completed",
                    "item": {
                        "id": "item-1",
                        "type": "agent_message",
                        "text": "not native response JSON",
                    },
                },
                {"type": "turn.completed"},
            )
        )
        with self.assertRaises(CodexResponseSchemaError):
            derive_codex_response(terminal_invalid)
        with self.assertRaises(CodexJSONLTransportError):
            derive_codex_response(terminal_invalid.rsplit(b"\n", 2)[0] + b"\n")


class CodexLiveBindingTests(unittest.TestCase):
    @unittest.skipUnless(CODEX_EXECUTABLE.is_file(), "pinned Codex binary unavailable")
    def test_prepare_accepts_only_the_packed_exact_codex_bundle(self):
        registrar = MemoryRegistrar()
        binding, native_policy_ref = make_live_codex_binding(registrar)

        manifest = prepare(
            make_spec(
                registrar,
                binding=binding,
                native_system_contract_ref=native_policy_ref,
            ),
            registrar,
        )

        self.assertEqual(manifest["binding"], binding)
        self.assertEqual(
            binding["harness"]["executable_ref"]["sha256"],
            "cb0a15567e9a60a5820d54b0f6ae86d504dc3805c1eab21a47f70e3eb7b73a40",
        )

    def test_shared_subject_validator_does_not_accept_revbench_bypass_suffix(self):
        policy = json.loads(
            (ROOT / "docs/product/contracts/native-agent-systems.json").read_bytes()
        )
        bundle = codex_native_bundle_policy()
        with self.assertRaisesRegex(
            NativeAgentSystemContractError, "command_identity_override"
        ):
            validate_native_agent_systems(
                policy,
                {
                    "outside-revbench": {
                        "tuple_id": "codex-terra-max",
                        "model_id": "gpt-5.6-terra",
                        "native_harness_id": "codex",
                        "effort": "max",
                        "command": bundle["launcher"]["review_argv"],
                        "version_command": ["codex", "--version"],
                    }
                },
            )

    def test_live_codex_refuses_immutable_or_observed_route_substitutions(self):
        with tempfile.TemporaryDirectory() as temporary:
            policy, member_bytes = make_synthetic_bundle_fixture(Path(temporary))
            for resolution, observed_at in (
                ("immutable", None),
                ("observed-route", "2026-08-15T00:00:00Z"),
            ):
                with self.subTest(resolution=resolution):
                    registrar = MemoryRegistrar()
                    binding, native_policy_ref = make_live_codex_binding(
                        registrar, policy=policy, member_bytes=member_bytes
                    )
                    provider = binding["provider_or_path"]
                    provider["resolution"] = resolution
                    provider["observed_at"] = observed_at
                    provider["route_ref"] = registered(
                        registrar,
                        f"substituted-route-{resolution}",
                        {
                            "schema_version": "caplab-provider-route/1",
                            **{
                                field: provider[field]
                                for field in (
                                    "kind",
                                    "identifier",
                                    "revision",
                                    "resolution",
                                    "observed_at",
                                )
                            },
                        },
                        kind="provider-route",
                        schema="caplab-provider-route/1",
                    )
                    binding["binding_id"] = "bnd-" + sha256_hex(
                        canonical_json(
                            {
                                key: value
                                for key, value in binding.items()
                                if key != "binding_id"
                            }
                        )
                    )
                    with (
                        mock.patch(
                            "caplab.revbench._core.codex_native_bundle_policy",
                            return_value=copy.deepcopy(policy),
                        ),
                        self.assertRaisesRegex(
                            RevbenchContractError, "provider_or_path.resolution"
                        ),
                    ):
                        prepare(
                            make_spec(
                                registrar,
                                binding=binding,
                                native_system_contract_ref=native_policy_ref,
                            ),
                            registrar,
                        )


class CodexLiveExecutionTests(unittest.TestCase):
    def _run_fake_subprocess_seam(self, mode="valid"):
        bundle_temporary = tempfile.TemporaryDirectory()
        self.addCleanup(bundle_temporary.cleanup)
        policy, member_bytes = make_synthetic_bundle_fixture(
            Path(bundle_temporary.name)
        )
        self._synthetic_policy = policy
        registrar = MemoryRegistrar()
        binding, native_policy_ref = make_live_codex_binding(
            registrar, policy=policy, member_bytes=member_bytes
        )
        with mock.patch(
            "caplab.revbench._core.codex_native_bundle_policy",
            return_value=copy.deepcopy(policy),
        ):
            manifest = prepare(
                make_spec(
                    registrar,
                    binding=binding,
                    native_system_contract_ref=native_policy_ref,
                ),
                registrar,
            )
        apparatus = synthetic_clean_apparatus()
        apparatus_ref = registered(
            registrar,
            apparatus["apparatus_id"],
            apparatus,
            kind="execution-apparatus-receipt",
            schema="caplab-revbench-execution-apparatus/1",
        )
        calls: list[tuple[str, str]] = []
        native_calls = 0

        def fake_runner(
            logical_argv,
            stdin,
            *,
            bundle,
            capture,
            credential,
            monotonic_deadline,
        ):
            nonlocal native_calls
            self.assertGreater(monotonic_deadline, 0)
            timestamp = capture.intent["intent_recorded_at"]
            quarantined = False
            if logical_argv[-1] == "--version":
                self.assertIsNone(credential)
                stdout = b"codex-cli 0.147.0\n"
                stderr = b""
            else:
                native_calls += 1
                self.assertIsNotNone(credential)
                native_input = json.loads(stdin)
                oracle = native_input["requirement"]
                value = native_input["artifact"]
                for token in oracle["pointer"].strip("/").split("/"):
                    value = value[token]
                response = {
                    "schema_version": "caplab-revbench-native-response/1",
                    "verdict": "clean" if value >= oracle["minimum"] else "defect",
                    "anchors": []
                    if value >= oracle["minimum"]
                    else [oracle["pointer"]],
                }
                response_text = (
                    "not native response JSON"
                    if mode == "invalid-response" and native_calls == 1
                    else canonical_json(response).decode()
                )
                events = [
                    {"type": "thread.started", "thread_id": "thread-1"},
                    {"type": "turn.started"},
                    {
                        "type": "item.completed",
                        "item": {
                            "id": "item-1",
                            "type": "agent_message",
                            "text": response_text,
                        },
                    },
                    {"type": "turn.completed", "usage": {"input_tokens": 1}},
                ]
                stdout = b"".join(canonical_json(event) + b"\n" for event in events)
                stderr = b""
                quarantine_targets = {
                    "privacy-quarantine": b"private-access-token",
                    "nested-key-privacy-quarantine": LIVE_NESTED_KEY.encode(),
                    "nested-value-privacy-quarantine": LIVE_NESTED_VALUE.encode(),
                }
                target = quarantine_targets.get(mode)
                if target is not None and native_calls == 1:
                    assert credential is not None
                    gate = credential.stream_quarantine()
                    midpoint = len(target) // 2
                    stdout = gate.feed(b"safe quarantined prefix:" + target[:midpoint])
                    stdout += gate.feed(target[midpoint:] + b":unsafe tail")
                    stdout += gate.finish()
                    self.assertTrue(gate.quarantined)
                    quarantined = True
                else:
                    quarantined = False
            capture.write_stdout(stdout)
            capture.write_stderr(stderr)
            observation = CodexProcessObservation(
                timestamp,
                timestamp,
                timestamp,
                timestamp,
                stdout,
                not quarantined,
                stderr,
                not quarantined,
                -15 if quarantined else 0,
                "privacy-quarantine" if quarantined else "exited",
                "invoked",
            )
            capture.complete(
                {
                    "schema_version": "caplab-revbench-live-process-completion/1",
                    "process_id": capture.intent["process_id"],
                    "launch_attempted_at": timestamp,
                    "process_started_at": timestamp,
                    "process_completed_at": timestamp,
                    "completion_recorded_at": timestamp,
                    "stdout_complete": not quarantined,
                    "stderr_complete": not quarantined,
                    "exit_code": -15 if quarantined else 0,
                    "termination": ("privacy-quarantine" if quarantined else "exited"),
                    "invocation_state": "invoked",
                }
            )
            calls.append(
                (
                    capture.intent["launch_plan"]["effect_scope"]["process_kind"],
                    logical_argv[0],
                )
            )
            return observation

        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            ledger_root = parent / "ledger"
            ledger_root.mkdir(mode=0o700)
            credential_root = parent / "credentials-private-root-7f31"
            credential_root.mkdir(mode=0o700)
            credential_source = credential_root / "owner-secret-source-7f31.json"
            credential_payload = synthetic_live_credential(
                extra_nested_claims=(
                    {LIVE_SHORT_NESTED_KEY: LIVE_SHORT_NESTED_VALUE}
                    if mode == "short-nested-key-preflight-refused"
                    else None
                )
            )
            credential_source.write_bytes(
                b"not-a-credential-document"
                if mode == "credential-preflight-refused"
                else credential_payload
            )
            credential_source.chmod(0o600)
            runtime = FilesystemLiveExecutionRuntime(
                ledger_root,
                credential_root=credential_root,
                credential_sources={"caplab-openai-revbench": credential_source.name},
            )
            authorization_ref = make_execution_authorization(
                registrar,
                manifest,
                apparatus_ref=apparatus_ref,
                custody_domain_id=runtime.custody_domain_id,
            )
            with (
                mock.patch(
                    "caplab.revbench.execution.run_codex_process",
                    side_effect=fake_runner,
                ),
                mock.patch(
                    "caplab.revbench.execution.execution_apparatus_receipt",
                    return_value=apparatus,
                ),
                mock.patch(
                    "caplab.revbench.codex.codex_native_bundle_policy",
                    return_value=copy.deepcopy(policy),
                ),
                mock.patch(
                    "caplab.revbench._core.codex_native_bundle_policy",
                    return_value=copy.deepcopy(policy),
                ),
            ):
                reviews = execute(
                    manifest,
                    authorization_ref,
                    registrar,
                    live_runtime=runtime,
                )
            if mode in {
                "credential-preflight-refused",
                "short-nested-key-preflight-refused",
            }:
                credential_source.write_bytes(synthetic_live_credential())
                credential_source.chmod(0o600)
                with (
                    mock.patch(
                        "caplab.revbench.execution.run_codex_process",
                        side_effect=AssertionError(
                            "sealed credential refusal must not launch again"
                        ),
                    ),
                    mock.patch(
                        "caplab.revbench.execution.execution_apparatus_receipt",
                        side_effect=AssertionError(
                            "sealed credential refusal must use retained identity"
                        ),
                    ),
                    mock.patch(
                        "caplab.revbench._core.codex_native_bundle_policy",
                        return_value=copy.deepcopy(policy),
                    ),
                ):
                    self._last_replay = execute(
                        manifest,
                        authorization_ref,
                        registrar,
                        live_runtime=runtime,
                    )
            with mock.patch(
                "caplab.revbench._core.codex_native_bundle_policy",
                return_value=copy.deepcopy(policy),
            ):
                measurement = score(manifest, reviews, registrar)
            self._last_registered_evidence = b"\n".join(registrar.documents.values())
            self._last_reviews_export = canonical_json(reviews)
            self._last_measurement_export = canonical_json(measurement)
            self._last_public_evidence = b"\n".join(
                (
                    self._last_registered_evidence,
                    self._last_reviews_export,
                    self._last_measurement_export,
                )
            )
            self._last_private_custody = b"\n".join(
                path.read_bytes()
                for path in sorted(runtime.root.rglob("*"))
                if path.is_file() and not path.is_symlink()
            )
            self._last_credential_source = str(credential_source).encode()
            credential_document = json.loads(credential_payload)
            tokens = credential_document["tokens"]
            private_scalars = [
                tokens["id_token"],
                tokens["access_token"],
                tokens["refresh_token"],
                tokens["account_id"],
                LIVE_SUBJECT,
                LIVE_EMAIL,
                LIVE_NAME,
                LIVE_CUSTOM_KEY,
                LIVE_CUSTOM_VALUE,
                LIVE_ORG_ID,
                LIVE_ORG_LABEL,
                LIVE_NESTED_KEY,
                LIVE_NESTED_VALUE,
                str(credential_root),
                credential_root.name,
                str(credential_source),
                credential_source.name,
            ]
            if mode == "short-nested-key-preflight-refused":
                private_scalars.extend((LIVE_SHORT_NESTED_KEY, LIVE_SHORT_NESTED_VALUE))
            self._last_private_scalars = tuple(
                value.encode() for value in private_scalars
            )
            self._last_private_hashes = tuple(
                sha256_hex(value).encode()
                for value in (
                    tokens["id_token"].encode(),
                    tokens["access_token"].encode(),
                    tokens["refresh_token"].encode(),
                    credential_payload,
                )
            )

        return registrar, manifest, reviews, measurement, calls, credential_source

    def _score_tampered(self, manifest, reviews, registrar):
        with mock.patch(
            "caplab.revbench._core.codex_native_bundle_policy",
            return_value=copy.deepcopy(self._synthetic_policy),
        ):
            return score(manifest, reviews, registrar)

    def test_fake_subprocess_seam_executes_and_scores_registered_jsonl(self):
        registrar, _manifest, reviews, measurement, calls, credential_source = (
            self._run_fake_subprocess_seam()
        )
        self.assertEqual(reviews["status"], "complete")
        self.assertEqual(len(reviews["attempts"]), 4)
        self.assertEqual(len(calls), 8)
        self.assertEqual(measurement["disposition"], "complete")
        self.assertEqual(
            measurement["metrics"]["catch_rate"]["value"],
            {"numerator": 1, "denominator": 1},
        )
        for attempt in reviews["attempts"]:
            output = json.loads(registrar.resolve(attempt["output_ref"]))
            self.assertNotEqual(
                registrar.resolve(output["raw_stdout_ref"]),
                registrar.resolve(output["derived_response_ref"]),
            )
            self.assertIsNotNone(output["response_derivation_ref"])
        exported = canonical_json(reviews)
        self.assertNotIn(b"private-access-token", exported)
        self.assertNotIn(b"private-refresh-token", exported)
        self.assertNotIn(str(credential_source).encode(), exported)
        combined = self._last_public_evidence + self._last_private_custody
        for secret in self._last_private_scalars:
            self.assertNotIn(secret, combined)
        for private_hash in self._last_private_hashes:
            self.assertNotIn(private_hash, combined)
        self.assertNotIn(self._last_credential_source, combined)
        self.assertNotIn(b"owner-secret-source-7f31.json", combined)

    def test_terminal_invalid_response_is_subject_failure_and_execution_continues(self):
        registrar, _manifest, reviews, _measurement, calls, _source = (
            self._run_fake_subprocess_seam("invalid-response")
        )
        self.assertEqual(reviews["status"], "complete")
        self.assertEqual(len(calls), 8)
        self.assertEqual(reviews["attempts"][0]["disposition"], "subject-failure")
        output = json.loads(registrar.resolve(reviews["attempts"][0]["output_ref"]))
        self.assertEqual(output["parse_status"], "invalid-response")
        self.assertIsNone(output["derived_response_ref"])

    def test_privacy_quarantine_retains_receipt_but_registers_no_stream_bytes(self):
        registrar, _manifest, reviews, _measurement, calls, _source = (
            self._run_fake_subprocess_seam("privacy-quarantine")
        )
        self.assertEqual(reviews["status"], "stopped")
        self.assertEqual(reviews["stop_reason"], "privacy-quarantine")
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(reviews["process_receipt_refs"]), 2)
        output = json.loads(registrar.resolve(reviews["attempts"][0]["output_ref"]))
        self.assertEqual(output["parse_status"], "privacy-quarantine")
        self.assertIsNone(output["raw_stdout_ref"])
        receipt = json.loads(registrar.resolve(reviews["process_receipt_refs"][1]))
        self.assertEqual(receipt["stream_disposition"], "privacy-quarantined")
        self.assertIsNone(receipt["stdout_ref"])

    def test_nested_custom_claim_key_and_value_never_reach_evidence(self):
        for mode in (
            "nested-key-privacy-quarantine",
            "nested-value-privacy-quarantine",
        ):
            with self.subTest(mode=mode):
                _registrar, _manifest, reviews, measurement, calls, _source = (
                    self._run_fake_subprocess_seam(mode)
                )
                self.assertEqual(reviews["status"], "stopped")
                self.assertEqual(reviews["stop_reason"], "privacy-quarantine")
                self.assertEqual(measurement["disposition"], "infrastructure-failure")
                self.assertEqual(len(calls), 2)
                surfaces = {
                    "custody": self._last_private_custody,
                    "registrar": self._last_registered_evidence,
                    "reviews-export": self._last_reviews_export,
                    "measurement-export": self._last_measurement_export,
                }
                for surface_name, surface in surfaces.items():
                    with self.subTest(mode=mode, surface=surface_name):
                        self.assertNotIn(LIVE_NESTED_KEY.encode(), surface)
                        self.assertNotIn(LIVE_NESTED_VALUE.encode(), surface)

    def test_sealed_credential_refusal_cannot_be_replayed_after_secret_rotation(self):
        _registrar, _manifest, reviews, measurement, calls, _source = (
            self._run_fake_subprocess_seam("credential-preflight-refused")
        )

        self.assertEqual(reviews, self._last_replay)
        self.assertEqual(reviews["status"], "stopped")
        self.assertEqual(reviews["stop_reason"], "preflight-refused")
        self.assertEqual(reviews["attempts"], [])
        self.assertEqual(reviews["process_receipt_refs"], [])
        self.assertEqual(calls, [])
        self.assertEqual(measurement["disposition"], "infrastructure-failure")
        for surface in (
            self._last_private_custody,
            self._last_registered_evidence,
            self._last_reviews_export,
            self._last_measurement_export,
        ):
            self.assertNotIn(LIVE_SHORT_NESTED_KEY.encode(), surface)
            self.assertNotIn(LIVE_SHORT_NESTED_VALUE.encode(), surface)

    def test_unknown_short_nested_claim_refuses_without_launch_or_replay(self):
        _registrar, _manifest, reviews, measurement, calls, _source = (
            self._run_fake_subprocess_seam("short-nested-key-preflight-refused")
        )

        self.assertEqual(reviews, self._last_replay)
        self.assertEqual(reviews["status"], "stopped")
        self.assertEqual(reviews["stop_reason"], "preflight-refused")
        self.assertEqual(reviews["attempts"], [])
        self.assertEqual(reviews["process_receipt_refs"], [])
        self.assertEqual(calls, [])
        self.assertEqual(measurement["disposition"], "infrastructure-failure")

    def test_uncertain_version_recovery_seals_without_a_second_launch(self):
        bundle_temporary = tempfile.TemporaryDirectory()
        self.addCleanup(bundle_temporary.cleanup)
        policy, member_bytes = make_synthetic_bundle_fixture(
            Path(bundle_temporary.name)
        )
        registrar = MemoryRegistrar()
        binding, native_policy_ref = make_live_codex_binding(
            registrar, policy=policy, member_bytes=member_bytes
        )
        with mock.patch(
            "caplab.revbench._core.codex_native_bundle_policy",
            return_value=copy.deepcopy(policy),
        ):
            manifest = prepare(
                make_spec(
                    registrar,
                    binding=binding,
                    native_system_contract_ref=native_policy_ref,
                ),
                registrar,
            )
        apparatus = synthetic_clean_apparatus()
        apparatus_ref = registered(
            registrar,
            apparatus["apparatus_id"],
            apparatus,
            kind="execution-apparatus-receipt",
            schema="caplab-revbench-execution-apparatus/1",
        )

        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            ledger_root = parent / "ledger"
            credential_root = parent / "credentials"
            ledger_root.mkdir(mode=0o700)
            credential_root.mkdir(mode=0o700)
            credential_source = credential_root / "credential.json"
            credential_source.write_bytes(synthetic_live_credential())
            credential_source.chmod(0o600)
            runtime = FilesystemLiveExecutionRuntime(
                ledger_root,
                credential_root=credential_root,
                credential_sources={"caplab-openai-revbench": credential_source.name},
            )
            authorization_ref = make_execution_authorization(
                registrar,
                manifest,
                apparatus_ref=apparatus_ref,
                custody_domain_id=runtime.custody_domain_id,
            )

            def interrupted_runner(
                _logical_argv,
                _stdin,
                *,
                bundle,
                capture,
                credential,
                monotonic_deadline,
            ):
                del bundle, credential, monotonic_deadline
                capture.write_stdout(b"durable-version-prefix")
                capture.close()
                raise RuntimeError("simulated executor interruption")

            patches = (
                mock.patch(
                    "caplab.revbench.execution.execution_apparatus_receipt",
                    return_value=apparatus,
                ),
                mock.patch(
                    "caplab.revbench.codex.codex_native_bundle_policy",
                    return_value=copy.deepcopy(policy),
                ),
                mock.patch(
                    "caplab.revbench._core.codex_native_bundle_policy",
                    return_value=copy.deepcopy(policy),
                ),
            )
            with (
                patches[0],
                patches[1],
                patches[2],
                mock.patch(
                    "caplab.revbench.execution.run_codex_process",
                    side_effect=interrupted_runner,
                ),
                self.assertRaisesRegex(RuntimeError, "simulated executor interruption"),
            ):
                execute(
                    manifest,
                    authorization_ref,
                    registrar,
                    live_runtime=runtime,
                )

            with (
                mock.patch(
                    "caplab.revbench.execution.execution_apparatus_receipt",
                    side_effect=AssertionError("recovery must use retained apparatus"),
                ),
                mock.patch(
                    "caplab.revbench.codex.codex_native_bundle_policy",
                    return_value=copy.deepcopy(policy),
                ),
                mock.patch(
                    "caplab.revbench._core.codex_native_bundle_policy",
                    return_value=copy.deepcopy(policy),
                ),
                mock.patch(
                    "caplab.revbench.execution.run_codex_process",
                    side_effect=AssertionError("recovery must not launch a process"),
                ),
            ):
                reviews = execute(
                    manifest,
                    authorization_ref,
                    registrar,
                    live_runtime=runtime,
                )
                replay = execute(
                    manifest,
                    authorization_ref,
                    registrar,
                    live_runtime=runtime,
                )
                measurement = score(manifest, reviews, registrar)

            self.assertEqual(reviews, replay)
            self.assertEqual(reviews["status"], "stopped")
            self.assertEqual(reviews["stop_reason"], "executor-interrupted")
            self.assertEqual(reviews["attempts"], [])
            self.assertEqual(len(reviews["process_receipt_refs"]), 1)
            receipt = json.loads(registrar.resolve(reviews["process_receipt_refs"][0]))
            self.assertEqual(receipt["outer_launch_state"], "uncertain")
            self.assertIsNotNone(receipt["recovery_ref"])
            self.assertEqual(measurement["disposition"], "infrastructure-failure")
            self.assertEqual(measurement["evidence"]["run_refs"], [])

            bundle = json.loads(
                registrar.resolve(measurement["evidence"]["bundle_ref"])
            )
            self.assertEqual(
                json.loads(registrar.resolve(bundle["execution_ref"])), reviews
            )
            tampered_bundle = copy.deepcopy(bundle)
            tampered_bundle["execution_ref"] = copy.deepcopy(
                reviews["execution_authorization_ref"]
            )
            registrar.documents[measurement["evidence"]["bundle_ref"]["sha256"]] = (
                canonical_json(tampered_bundle)
            )
            with self.assertRaisesRegex(Exception, "resolved (?:byte count|SHA-256)"):
                validate_measurement(measurement, registrar)

    def test_registered_live_evidence_validates_against_published_schemas(self):
        registrar, manifest, reviews, _measurement, _calls, _source = (
            self._run_fake_subprocess_seam()
        )
        contracts = ROOT / "docs" / "product" / "contracts"
        root_schema = json.loads((contracts / "revbench-v1.schema.json").read_bytes())
        live_schema = json.loads(
            (contracts / "revbench-live-native-v1.schema.json").read_bytes()
        )
        claim_schema = json.loads(
            (contracts / "qualification-claim-v1.schema.json").read_bytes()
        )
        Draft202012Validator.check_schema(root_schema)
        Draft202012Validator.check_schema(live_schema)
        registry = Registry().with_resources(
            (
                (claim_schema["$id"], Resource.from_contents(claim_schema)),
                (live_schema["$id"], Resource.from_contents(live_schema)),
            )
        )
        root_validator = Draft202012Validator(root_schema, registry=registry)
        live_validator = Draft202012Validator(live_schema, registry=registry)
        expected_live_versions = {
            "caplab-revbench-execution-apparatus/1",
            "caplab-revbench-codex-native-bundle-policy/1",
            "caplab-revbench-codex-credential-profile/1",
            "caplab-revbench-codex-inference/1",
            "caplab-revbench-codex-tools/1",
            "caplab-revbench-codex-permissions/1",
            "caplab-revbench-codex-sandbox/1",
            "caplab-revbench-codex-runtime/1",
            "caplab-revbench-response-derivation/1",
            "caplab-revbench-live-execution-intent/1",
            "caplab-revbench-live-process-receipt/1",
            "caplab-live-native-version-observation/1",
            "caplab-live-native-output/1",
            "caplab-live-native-attempt-capture/1",
            "caplab-live-native-attempt-attestation/1",
            "caplab-live-native-review-attempt/1",
            "caplab-revbench-reviews/1",
        }
        seen = set()
        for raw in registrar.documents.values():
            try:
                document = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if not isinstance(document, dict):
                continue
            schema_version = document.get("schema_version")
            if schema_version in expected_live_versions:
                if schema_version == ("caplab-revbench-codex-native-bundle-policy/1"):
                    # The hermetic runner uses deliberately synthetic member
                    # bytes.  Validate only the shipped production constant as
                    # public bundle-policy evidence.
                    continue
                if schema_version == "caplab-revbench-codex-sandbox/1":
                    # The hermetic orchestration seam replaces only the host
                    # adapter path and bytes.  Validate the repository-pinned
                    # public shape rather than widening its exact contract.
                    document = copy.deepcopy(document)
                    document["adapter_path"] = "/usr/bin/bwrap"
                with self.subTest(schema_version=schema_version):
                    live_validator.validate(document)
                seen.add(schema_version)
        live_validator.validate(codex_native_bundle_policy())
        seen.add("caplab-revbench-codex-native-bundle-policy/1")
        root_validator.validate(manifest)
        root_validator.validate(reviews)
        authorization = next(
            json.loads(raw)
            for raw in registrar.documents.values()
            if raw.startswith(b'{"apparatus_ref":')
        )
        root_validator.validate(authorization)
        self.assertEqual(seen, expected_live_versions)

        wrong_ref = copy.deepcopy(reviews)
        wrong_ref["process_receipt_refs"][0]["kind"] = "prompt"
        with self.assertRaises(ValidationError):
            live_validator.validate(wrong_ref)

        for mutation in ("added", "changed"):
            hostile_bundle = codex_native_bundle_policy()
            if mutation == "added":
                hostile_bundle["containment"]["host_mount"] = "/"
            else:
                hostile_bundle["environment"]["PATH"] = "/usr/bin"
            with (
                self.subTest(bundle_mutation=mutation),
                self.assertRaises(ValidationError),
            ):
                live_validator.validate(hostile_bundle)

    def test_score_refuses_valid_terminal_jsonl_relabelled_as_transport_failure(self):
        registrar, manifest, reviews, _measurement, _calls, _source = (
            self._run_fake_subprocess_seam()
        )
        tampered = copy.deepcopy(reviews)
        reseal_live_attempt(
            registrar,
            tampered["attempts"][0],
            output_changes={
                "parse_status": "invalid-transport",
                "derived_response_ref": None,
                "response_derivation_ref": None,
                "verdict": "invalid",
                "anchors": [],
            },
            disposition="infrastructure-failure",
            verdict="invalid",
            anchors=[],
            harness_completion="unavailable",
        )
        tampered["status"] = "stopped"
        tampered["stop_reason"] = "response-transport-invalid"
        tampered["attempts"] = tampered["attempts"][:1]
        tampered["process_receipt_refs"] = tampered["process_receipt_refs"][:2]
        reseal_execution(tampered)

        with self.assertRaisesRegex(
            RevbenchContractError,
            "transport failure unexpectedly has a valid terminal envelope",
        ):
            self._score_tampered(manifest, tampered, registrar)

    def test_score_refuses_selective_omission_after_successful_version_probe(self):
        registrar, manifest, reviews, _measurement, _calls, _source = (
            self._run_fake_subprocess_seam()
        )
        tampered = copy.deepcopy(reviews)
        tampered["status"] = "stopped"
        tampered["stop_reason"] = "exited"
        tampered["attempts"] = tampered["attempts"][:-1]
        tampered["process_receipt_refs"] = tampered["process_receipt_refs"][:-1]
        reseal_execution(tampered)

        with self.assertRaisesRegex(
            RevbenchContractError,
            "cannot omit the native process after a successful version probe",
        ):
            self._score_tampered(manifest, tampered, registrar)

    def test_score_refuses_later_only_attempt_selection(self):
        registrar, manifest, reviews, _measurement, _calls, _source = (
            self._run_fake_subprocess_seam()
        )
        tampered = copy.deepcopy(reviews)
        tampered["status"] = "stopped"
        tampered["stop_reason"] = "exited"
        tampered["attempts"] = [tampered["attempts"][1]]
        tampered["process_receipt_refs"] = tampered["process_receipt_refs"][:2]
        reseal_execution(tampered)

        with self.assertRaisesRegex(RevbenchContractError, "exact prefix"):
            self._score_tampered(manifest, tampered, registrar)

    def test_score_refuses_quarantine_receipt_enum_mismatch(self):
        registrar, manifest, reviews, _measurement, _calls, _source = (
            self._run_fake_subprocess_seam("privacy-quarantine")
        )
        tampered = copy.deepcopy(reviews)
        receipt = json.loads(registrar.resolve(tampered["process_receipt_refs"][1]))
        receipt["termination"] = "timeout"
        receipt["receipt_id"] = ""
        receipt["receipt_id"] = _content_id(
            receipt, "receipt_id", "live-process-receipt-"
        )
        receipt_ref = registered(
            registrar,
            receipt["receipt_id"],
            receipt,
            kind="live-process-receipt",
            schema="caplab-revbench-live-process-receipt/1",
        )
        tampered["process_receipt_refs"][1] = receipt_ref
        reseal_execution(tampered)

        with self.assertRaisesRegex(RevbenchContractError, "privacy quarantine"):
            self._score_tampered(manifest, tampered, registrar)

    def test_public_execute_exposes_no_runner_hooks_and_rejects_fake_runtimes(self):
        self.assertEqual(
            list(inspect.signature(execute).parameters),
            [
                "manifest",
                "execution_authorization_ref",
                "registrar",
                "live_runtime",
            ],
        )
        with self.assertRaises(TypeError):
            execute({}, {}, object(), live_process_runner=lambda *_: None)

        registrar, manifest, reviews, _measurement, _calls, _source = (
            self._run_fake_subprocess_seam()
        )

        class RuntimeSubclass(FilesystemLiveExecutionRuntime):
            pass

        for fake in (object(), object.__new__(RuntimeSubclass)):
            with (
                self.subTest(runtime_type=type(fake).__name__),
                mock.patch(
                    "caplab.revbench._core.codex_native_bundle_policy",
                    return_value=copy.deepcopy(self._synthetic_policy),
                ),
            ):
                with self.assertRaisesRegex(
                    RevbenchContractError, "explicit durable custody runtime"
                ):
                    execute(
                        manifest,
                        reviews["execution_authorization_ref"],
                        registrar,
                        live_runtime=fake,
                    )


class CodexLiveCliTests(unittest.TestCase):
    def _main_error(self, argv, *, live_source=False):
        emitted = []
        emit_patch = mock.patch(
            "caplab.revbench.__main__._emit",
            side_effect=lambda document, **_kwargs: emitted.append(document),
        )
        source_patch = mock.patch(
            "caplab.revbench.__main__.require_live_source_invocation"
        )
        with emit_patch:
            if live_source:
                with source_patch:
                    result = revbench_cli.main(argv, live_source=True)
            else:
                result = revbench_cli.main(argv)
            self.assertEqual(result, 2)
        self.assertEqual(len(emitted), 1)
        return canonical_json(emitted[0])

    def test_prepare_live_runtime_is_no_effect_idempotent_and_domain_bound(self):
        apparatus = synthetic_clean_apparatus()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger = root / "ledger"
            custody_one = root / "custody-one"
            custody_two = root / "custody-two"
            custody_one.mkdir(mode=0o700)
            custody_two.mkdir(mode=0o700)
            outputs = [root / f"authority-{index}.json" for index in range(3)]
            refs = [root / f"authority-{index}.ref.json" for index in range(3)]

            def invoke(custody, output, reference):
                args = revbench_cli.build_parser(live_source=True).parse_args(
                    [
                        "prepare-live-runtime",
                        "--ledger",
                        str(ledger),
                        "--live-custody-root",
                        str(custody),
                        "--output",
                        str(output),
                        "--reference-output",
                        str(reference),
                    ]
                )
                with (
                    mock.patch(
                        "caplab.revbench.__main__.execution_apparatus_receipt",
                        return_value=apparatus,
                    ),
                    mock.patch(
                        "caplab.revbench.__main__.require_live_source_invocation"
                    ),
                    mock.patch("caplab.revbench.__main__._emit"),
                    mock.patch(
                        "subprocess.Popen",
                        side_effect=AssertionError("provider process must not start"),
                    ),
                ):
                    self.assertEqual(revbench_cli.run(args, live_source=True), 0)

            invoke(custody_one, outputs[0], refs[0])
            invoke(custody_one, outputs[1], refs[1])
            invoke(custody_two, outputs[2], refs[2])

            first = json.loads(outputs[0].read_bytes())
            replay = json.loads(outputs[1].read_bytes())
            other = json.loads(outputs[2].read_bytes())
            self.assertEqual(first, replay)
            self.assertEqual(refs[0].read_bytes(), refs[1].read_bytes())
            self.assertNotEqual(first["custody_domain_id"], other["custody_domain_id"])
            self.assertEqual(
                first["apparatus_ref"]["sha256"],
                sha256_hex(canonical_json(apparatus)),
            )

            contracts = ROOT / "docs" / "product" / "contracts"
            live_schema = json.loads(
                (contracts / "revbench-live-native-v1.schema.json").read_bytes()
            )
            claim_schema = json.loads(
                (contracts / "qualification-claim-v1.schema.json").read_bytes()
            )
            registry = Registry().with_resource(
                claim_schema["$id"], Resource.from_contents(claim_schema)
            )
            Draft202012Validator(live_schema, registry=registry).validate(first)

    def test_execute_cli_requires_complete_live_options_and_rejects_them_locally(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger = root / "ledger"
            live_manifest = root / "live-manifest.json"
            local_manifest = root / "local-manifest.json"
            missing_authorization = root / "missing-authorization.json"
            output = root / "output.json"
            live_manifest.write_bytes(
                canonical_json(
                    {"binding": {"provider_or_path": {"kind": "direct-provider"}}}
                )
            )
            local_manifest.write_bytes(
                canonical_json(
                    {"binding": {"provider_or_path": {"kind": "local-serving"}}}
                )
            )

            incomplete = revbench_cli.build_parser(live_source=True).parse_args(
                [
                    "execute",
                    "--manifest",
                    str(live_manifest),
                    "--execution-authorization-ref",
                    str(missing_authorization),
                    "--ledger",
                    str(ledger),
                    "--output",
                    str(output),
                ]
            )
            with (
                self.assertRaisesRegex(
                    RevbenchContractError, "live_execution_private_runtime_required"
                ),
                mock.patch("caplab.revbench.__main__.require_live_source_invocation"),
            ):
                revbench_cli.run(incomplete, live_source=True)

            local_with_live_option = revbench_cli.build_parser(
                live_source=True
            ).parse_args(
                [
                    "execute",
                    "--manifest",
                    str(local_manifest),
                    "--execution-authorization-ref",
                    str(missing_authorization),
                    "--ledger",
                    str(ledger),
                    "--output",
                    str(output),
                    "--live-custody-root",
                    str(root),
                ]
            )
            with self.assertRaisesRegex(
                RevbenchContractError, "local_fixture_rejects_live_runtime_options"
            ):
                revbench_cli.run(local_with_live_option, live_source=True)

    def test_generic_live_routes_refuse_before_ledger_or_custody_mutation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger = root / "ledger"
            custody = root / "custody"
            output = root / "output.json"
            authority = root / "authorization.json"
            live_manifest = root / "live-manifest.json"
            live_manifest.write_bytes(
                canonical_json(
                    {"binding": {"provider_or_path": {"kind": "direct-provider"}}}
                )
            )

            prepare_diagnostic = self._main_error(
                [
                    "prepare-live-runtime",
                    "--ledger",
                    str(ledger),
                    "--live-custody-root",
                    str(custody),
                    "--output",
                    str(output),
                ]
            )
            self.assertFalse(ledger.exists())
            self.assertFalse(custody.exists())
            self.assertFalse(output.exists())
            self.assertIn(b"argument_error", prepare_diagnostic)

            execute_diagnostic = self._main_error(
                [
                    "execute",
                    "--manifest",
                    str(live_manifest),
                    "--execution-authorization-ref",
                    str(authority),
                    "--ledger",
                    str(ledger),
                    "--output",
                    str(output),
                ]
            )
            self.assertFalse(ledger.exists())
            self.assertFalse(custody.exists())
            self.assertFalse(output.exists())
            self.assertIn(
                b"live_source_invocation_profile_required", execute_diagnostic
            )

    def test_document_argument_errors_are_role_coded_and_path_free(self):
        private_directory = "owner-private-document-root-7f31"
        private_names = {
            "spec": "owner-private-spec-7f31.json",
            "manifest": "owner-private-manifest-7f31.json",
            "authorization": "owner-private-authorization-7f31.json",
            "reviews": "owner-private-reviews-7f31.json",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / private_directory
            root.mkdir()
            ledger = Path(temporary) / "ledger"
            output = Path(temporary) / "output.json"
            paths = {name: root / value for name, value in private_names.items()}
            for path in paths.values():
                path.write_text("not-json", encoding="utf-8")
            minimal_manifest = root / "valid-local-manifest.json"
            minimal_manifest.write_bytes(
                canonical_json(
                    {"binding": {"provider_or_path": {"kind": "local-serving"}}}
                )
            )
            diagnostics = (
                self._main_error(
                    [
                        "prepare",
                        "--spec",
                        str(paths["spec"]),
                        "--ledger",
                        str(ledger),
                        "--output",
                        str(output),
                    ]
                ),
                self._main_error(
                    [
                        "execute",
                        "--manifest",
                        str(paths["manifest"]),
                        "--execution-authorization-ref",
                        str(paths["authorization"]),
                        "--ledger",
                        str(ledger),
                        "--output",
                        str(output),
                    ]
                ),
                self._main_error(
                    [
                        "execute",
                        "--manifest",
                        str(minimal_manifest),
                        "--execution-authorization-ref",
                        str(paths["authorization"]),
                        "--ledger",
                        str(ledger),
                        "--output",
                        str(output),
                    ]
                ),
                self._main_error(
                    [
                        "score",
                        "--manifest",
                        str(minimal_manifest),
                        "--reviews",
                        str(paths["reviews"]),
                        "--ledger",
                        str(ledger),
                        "--output",
                        str(output),
                    ]
                ),
            )

        combined = b"\n".join(diagnostics)
        for private_value in (private_directory, *private_names.values()):
            self.assertNotIn(private_value.encode(), combined)
        for role, diagnostic in zip(
            ("spec", "manifest", "execution_authorization", "reviews"),
            diagnostics,
            strict=True,
        ):
            self.assertIn(f"{role}_document_invalid".encode(), diagnostic)

        error_schema = json.loads(
            (ROOT / "docs/product/contracts/revbench-error-v1.schema.json").read_bytes()
        )
        Draft202012Validator.check_schema(error_schema)
        validator = Draft202012Validator(error_schema)
        for diagnostic in diagnostics:
            validator.validate(json.loads(diagnostic))

    def test_error_envelope_is_closed_for_every_public_error_category(self):
        schema = json.loads(
            (ROOT / "docs/product/contracts/revbench-error-v1.schema.json").read_bytes()
        )
        validator = Draft202012Validator(schema)
        private_path = "/tmp/owner-private-error-path-7f31"
        documents = (
            revbench_cli._error_document(RevbenchContractError("argument_error")),
            revbench_cli._error_document(CanonicalizationError("not canonical")),
            revbench_cli._error_document(ValueError("")),
            revbench_cli._error_document(OSError(private_path)),
        )
        for document in documents:
            validator.validate(document)
            self.assertNotIn(private_path.encode(), canonical_json(document))
        hostile = {**documents[0], "private_detail": private_path}
        with self.assertRaises(ValidationError):
            validator.validate(hostile)

    def test_cli_private_runtime_failures_and_unknown_options_are_path_free(self):
        private_root_name = "private-credential-root-sentinel-7f31"
        private_source_name = "owner-auth-source-sentinel-7f31.json"
        private_scalar = "private-token-sentinel-7f31"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger = root / "ledger"
            custody = root / "custody"
            custody.mkdir(mode=0o700)
            live_manifest = root / "live-manifest.json"
            live_manifest.write_bytes(
                canonical_json(
                    {"binding": {"provider_or_path": {"kind": "direct-provider"}}}
                )
            )
            missing_authorization = root / "authorization.json"
            output = root / "output.json"
            missing_private_root = root / private_root_name

            common = [
                "execute",
                "--manifest",
                str(live_manifest),
                "--execution-authorization-ref",
                str(missing_authorization),
                "--ledger",
                str(ledger),
                "--output",
                str(output),
                "--live-custody-root",
                str(custody),
                "--credential-root",
                str(missing_private_root),
                "--credential-profile-source",
                f"caplab-openai-revbench={private_source_name}",
            ]
            diagnostics = [self._main_error(common, live_source=True)]
            diagnostics.append(
                self._main_error(
                    [
                        "execute",
                        "--credential-roo",
                        f"{private_scalar}={private_source_name}",
                    ],
                    live_source=True,
                )
            )

            insecure_private_root = root / f"{private_root_name}-mode"
            insecure_private_root.mkdir(mode=0o755)
            diagnostics.append(
                self._main_error(
                    [
                        *common[: common.index("--credential-root") + 1],
                        str(insecure_private_root),
                        "--credential-profile-source",
                        f"caplab-openai-revbench={private_source_name}",
                    ],
                    live_source=True,
                )
            )

        combined = b"\n".join(diagnostics)
        for private_value in (
            private_root_name,
            private_source_name,
            private_scalar,
        ):
            self.assertNotIn(private_value.encode(), combined)
        self.assertIn(b"credential_root_unavailable", diagnostics[0])
        self.assertIn(b"argument_error", diagnostics[1])
        self.assertIn(b"credential_root_ownership_or_mode_invalid", diagnostics[2])


class CodexCredentialTests(unittest.TestCase):
    def _credential(
        self,
        subject: str,
        account_id: str,
        *,
        algorithm="RS256",
        extra_claims=None,
    ) -> bytes:
        claims = {
            "sub": subject,
            "iss": "https://auth.openai.com",
            "aud": ["https://api.openai.com/v1"],
            "iat": 1_700_000_000,
            "exp": 4_102_444_800,
            **(extra_claims or {}),
        }
        token = ".".join(
            (
                base64.urlsafe_b64encode(
                    canonical_json(
                        {"alg": algorithm, "kid": "kid_0123456789abcdef", "typ": "JWT"}
                    )
                )
                .rstrip(b"=")
                .decode(),
                base64.urlsafe_b64encode(canonical_json(claims)).rstrip(b"=").decode(),
                "c2lnbmF0dXJlX2J5dGVz",
            )
        )
        return canonical_json(
            {
                "auth_mode": "chatgpt",
                "OPENAI_API_KEY": None,
                "tokens": {
                    "id_token": token,
                    "access_token": "private-access-token",
                    "refresh_token": "private-refresh-token",
                    "account_id": account_id,
                },
                "last_refresh": "2026-08-14T00:00:00Z",
            }
        )

    def _profile(self, subject: str, account_id: str):
        return {
            "schema_version": "caplab-revbench-codex-credential-profile/1",
            "profile_id": "caplab-openai-revbench",
            "provider": "openai",
            "auth_method": "chatgpt",
            "identity_basis": "operator-declared-unverified-token-claims",
            "provider_account_id_sha256": sha256_hex(account_id.encode()),
            "provider_subject_sha256": sha256_hex(subject.encode()),
            "identity_token_issuer": "https://auth.openai.com",
            "identity_token_audience": ["https://api.openai.com/v1"],
        }

    def test_credential_is_validated_once_and_exposed_only_by_sealed_memfd(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "dedicated-auth.json"
            subject = "acct_0123456789abcdef0123456789abcdef"
            account_id = "workspace_0123456789abcdef0123456789abcdef"
            payload = self._credential(subject, account_id)
            source.write_bytes(payload)
            source.chmod(0o600)
            Path(temporary).chmod(0o700)
            profile = self._profile(subject, account_id)

            with credential_memfd(
                source, profile, credential_root=Path(temporary)
            ) as credential:
                descriptor = credential.descriptor
                self.assertNotIn("private-access-token", repr(credential))
                self.assertNotIn("private-refresh-token", repr(credential))
                self.assertNotIn(
                    str(source), os.readlink(f"/proc/self/fd/{descriptor}")
                )
                os.lseek(descriptor, 0, os.SEEK_SET)
                self.assertEqual(os.read(descriptor, len(payload) + 1), payload)
                with self.assertRaises(OSError):
                    os.write(descriptor, b"tamper")
                credential.assert_streams_safe(b"ordinary output", b"ordinary error")
                with self.assertRaisesRegex(CodexAdapterError, "secret_quarantine"):
                    credential.assert_streams_safe(
                        b"ordinary output", b"failure: private-refresh-token"
                    )
                quarantine = credential.stream_quarantine()
                safe = quarantine.feed(b"warning private-ref")
                safe += quarantine.feed(b"resh-token should not persist")
                self.assertTrue(quarantine.quarantined)
                self.assertNotIn(b"private-refresh-token", safe)
                self.assertNotIn(b"private-refresh-token", quarantine.finish())

            self.assertFalse(Path(f"/proc/self/fd/{descriptor}").exists())

    def test_credential_quarantine_covers_every_decoded_private_string_claim(self):
        private_claims = {
            "email": "private.person.7f31@example.invalid",
            "name": "Private Sentinel Name 7f31",
            "private_claim_key_sentinel_7f31": "private claim value 7f31",
            "delegations": [LIVE_LIST_VALUE],
            "organization": {
                "id": "org_0123456789abcdef7f31",
                "label": "Private Sentinel Organization 7f31",
                "private_nested_claim_key_sentinel_7f31": (
                    "private nested claim value 7f31"
                ),
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            source = root / "auth.json"
            subject = "acct_0123456789abcdef0123456789abcdef"
            account_id = "workspace_0123456789abcdef0123456789abcdef"
            source.write_bytes(
                self._credential(
                    subject,
                    account_id,
                    extra_claims=private_claims,
                )
            )
            source.chmod(0o600)

            with credential_memfd(
                source,
                self._profile(subject, account_id),
                credential_root=root,
            ) as credential:
                sentinels = (
                    subject,
                    account_id,
                    private_claims["email"],
                    private_claims["name"],
                    "private_claim_key_sentinel_7f31",
                    private_claims["private_claim_key_sentinel_7f31"],
                    LIVE_LIST_VALUE,
                    private_claims["organization"]["id"],
                    private_claims["organization"]["label"],
                    "private_nested_claim_key_sentinel_7f31",
                    private_claims["organization"][
                        "private_nested_claim_key_sentinel_7f31"
                    ],
                )
                for sentinel in sentinels:
                    with self.subTest(sentinel=sentinel):
                        gate = credential.stream_quarantine()
                        encoded = sentinel.encode()
                        midpoint = len(encoded) // 2
                        retained = gate.feed(b"safe-prefix:" + encoded[:midpoint])
                        retained += gate.feed(encoded[midpoint:] + b":tail")
                        self.assertTrue(gate.quarantined)
                        self.assertNotIn(encoded, retained)
                        self.assertNotIn(encoded, gate.finish())
                ordinary_response = canonical_json(
                    {
                        "schema_version": "caplab-revbench-native-response/1",
                        "verdict": "clean",
                        "anchors": [],
                    }
                )
                ordinary = b"".join(
                    canonical_json(event) + b"\n"
                    for event in (
                        {"type": "thread.started", "thread_id": "thread-ordinary"},
                        {"type": "turn.started"},
                        {
                            "type": "item.completed",
                            "item": {
                                "id": "item-ordinary",
                                "type": "agent_message",
                                "text": (
                                    "benign chatgpt email name organization "
                                    "delegations id label text "
                                    + ordinary_response.decode("utf-8")
                                ),
                            },
                        },
                        {
                            "type": "turn.completed",
                            "usage": {"input_tokens": 1, "output_tokens": 2},
                        },
                    )
                )
                ordinary_gate = credential.stream_quarantine()
                retained = (
                    b"".join(
                        ordinary_gate.feed(ordinary[index : index + 7])
                        for index in range(0, len(ordinary), 7)
                    )
                    + ordinary_gate.finish()
                )
                self.assertFalse(ordinary_gate.quarantined)
                self.assertEqual(retained, ordinary)

            source.write_bytes(
                self._credential(
                    subject,
                    account_id,
                    extra_claims={
                        "organization": {
                            "id": "org_0123456789abcdef7f31",
                            LIVE_SHORT_NESTED_KEY: LIVE_SHORT_NESTED_VALUE,
                        }
                    },
                )
            )
            source.chmod(0o600)
            with self.assertRaisesRegex(
                CodexAdapterError, "credential_nested_claim_key_invalid"
            ):
                with credential_memfd(
                    source,
                    self._profile(subject, account_id),
                    credential_root=root,
                ):
                    self.fail("unknown short nested claim must not be accepted")

            source.write_bytes(
                self._credential(
                    subject,
                    account_id,
                    extra_claims={
                        LIVE_SHORT_TOP_LEVEL_KEY: "private top-level value 7f31"
                    },
                )
            )
            source.chmod(0o600)
            with self.assertRaisesRegex(
                CodexAdapterError, "credential_custom_claim_key_invalid"
            ):
                with credential_memfd(
                    source,
                    self._profile(subject, account_id),
                    credential_root=root,
                ):
                    self.fail("unknown short top-level claim must not be accepted")

    def test_credential_refuses_custom_non_string_claim_leaves(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            source = root / "auth.json"
            subject = "acct_0123456789abcdef0123456789abcdef"
            account_id = "workspace_0123456789abcdef0123456789abcdef"

            unsupported_claims = {
                "numeric": {"email": 7},
                "boolean-in-list": {"delegations": ["private string", True]},
                "null-in-object": {
                    "organization": {
                        "id": "org_0123456789abcdef7f31",
                        "label": None,
                    }
                },
            }
            for label, extra_claims in unsupported_claims.items():
                with self.subTest(label=label):
                    source.write_bytes(
                        self._credential(
                            subject,
                            account_id,
                            extra_claims=extra_claims,
                        )
                    )
                    source.chmod(0o600)
                    with self.assertRaisesRegex(
                        CodexAdapterError, "credential_custom_claim_value_invalid"
                    ):
                        with credential_memfd(
                            source,
                            self._profile(subject, account_id),
                            credential_root=root,
                        ):
                            self.fail("custom non-string scalar must not be accepted")

    def test_credential_refuses_mode_subject_and_symlink_swaps(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "dedicated-auth.json"
            subject = "acct_0123456789abcdef0123456789abcdef"
            account_id = "workspace_0123456789abcdef0123456789abcdef"
            root.chmod(0o700)
            source.write_bytes(self._credential(subject, account_id))
            profile = self._profile(subject, account_id)
            source.chmod(0o644)
            with self.assertRaisesRegex(CodexAdapterError, "mode"):
                with credential_memfd(source, profile, credential_root=root):
                    pass
            source.chmod(0o600)
            wrong = {**profile, "provider_subject_sha256": "0" * 64}
            with self.assertRaisesRegex(CodexAdapterError, "subject"):
                with credential_memfd(source, wrong, credential_root=root):
                    pass
            link = root / "auth-link.json"
            link.symlink_to(source)
            with self.assertRaisesRegex(CodexAdapterError, "open"):
                with credential_memfd(link, profile, credential_root=root):
                    pass
            link.unlink()
            hardlink = root / "auth-hardlink.json"
            os.link(source, hardlink)
            with self.assertRaisesRegex(CodexAdapterError, "mode"):
                with credential_memfd(source, profile, credential_root=root):
                    pass

    def test_credential_fifo_is_refused_without_blocking(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            source = root / "auth.json"
            os.mkfifo(source, 0o600)
            subject = "acct_0123456789abcdef0123456789abcdef"
            account_id = "workspace_0123456789abcdef0123456789abcdef"

            started = time.monotonic()
            with self.assertRaisesRegex(CodexAdapterError, "mode"):
                with credential_memfd(
                    source,
                    self._profile(subject, account_id),
                    credential_root=root,
                ):
                    pass
            self.assertLess(time.monotonic() - started, 1.0)

    def test_credential_refuses_unapproved_jwt_or_outside_source_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            subject = "acct_0123456789abcdef0123456789abcdef"
            account_id = "workspace_0123456789abcdef0123456789abcdef"
            source = root / "auth.json"
            source.write_bytes(self._credential(subject, account_id, algorithm="none"))
            source.chmod(0o600)
            with self.assertRaisesRegex(CodexAdapterError, "algorithm"):
                with credential_memfd(
                    source, self._profile(subject, account_id), credential_root=root
                ):
                    pass
            outside = root.parent / f"outside-{root.name}.json"
            try:
                outside.write_bytes(self._credential(subject, account_id))
                outside.chmod(0o600)
                with self.assertRaisesRegex(CodexAdapterError, "root"):
                    with credential_memfd(
                        outside,
                        self._profile(subject, account_id),
                        credential_root=root,
                    ):
                        pass
            finally:
                outside.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
