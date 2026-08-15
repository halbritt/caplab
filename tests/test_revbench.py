from __future__ import annotations

import copy
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from caplab.producer import producer_identity
from caplab.qualification import derive_content_id, validate_measurement
from caplab.qualification.ledger import FilesystemQualificationLedger
from caplab.revbench import RevbenchContractError, execute, prepare, score
from caplab.runtime.canonical import canonical_json, sha256_hex

ROOT = Path(__file__).resolve().parents[1]
LOCAL_FIXTURE_PROVIDER = "caplab-local-fixture"
LOCAL_FIXTURE_REVISION = "revbench-static-fixture-v1"
LOCAL_FIXTURE_MODEL = "caplab/revbench-static-fixture"
LOCAL_FIXTURE_HARNESS = "caplab-revbench-static-fixture"
LOCAL_FIXTURE_HARNESS_VERSION = "fake-native 1"
LOCAL_FIXTURE_TUPLE = "caplab-revbench-static-fixture-fixed"
LOCAL_FIXTURE_VERSION_STDOUT = b"fake-native 1\n"
LOCAL_FIXTURE_VERSION_STDERR = b""


class MemoryRegistrar:
    def __init__(self) -> None:
        self.documents: dict[str, bytes] = {}
        self.registrations: dict[str, tuple[str, int]] = {}

    def register_document(self, document, *, kind, schema, registration_id):
        data = canonical_json(document)
        digest = sha256_hex(data)
        registration_ref = f"test:{registration_id}:{digest}"
        retained = self.registrations.get(registration_ref)
        identity = (digest, len(data))
        if retained is not None and retained != identity:
            raise ValueError("registration identity conflict")
        self.documents[digest] = data
        self.registrations[registration_ref] = identity
        return {
            "kind": kind,
            "schema": schema,
            "media_type": "application/json",
            "sha256": digest,
            "byte_count": len(data),
            "locator": f"objects/sha256/{digest[:2]}/{digest}",
            "registration_ref": registration_ref,
            "custody": None,
        }

    def resolve(self, ref):
        if self.registrations.get(ref["registration_ref"]) != (
            ref["sha256"],
            ref["byte_count"],
        ):
            raise KeyError(ref["registration_ref"])
        return self.documents[ref["sha256"]]

    def register_bytes(self, payload, *, kind, schema, media_type, registration_id):
        digest = sha256_hex(payload)
        registration_ref = f"test:{registration_id}:{digest}"
        identity = (digest, len(payload))
        retained = self.registrations.get(registration_ref)
        if retained is not None and retained != identity:
            raise ValueError("registration identity conflict")
        self.documents[digest] = payload
        self.registrations[registration_ref] = identity
        return {
            "kind": kind,
            "schema": schema,
            "media_type": media_type,
            "sha256": digest,
            "byte_count": len(payload),
            "locator": f"objects/sha256/{digest[:2]}/{digest}",
            "registration_ref": registration_ref,
            "custody": None,
        }


class LedgerRegistrar:
    def __init__(self, root: Path) -> None:
        self.ledger = FilesystemQualificationLedger(root)

    def register_document(self, document, *, kind, schema, registration_id):
        del registration_id
        return self.ledger.register_document(document, kind=kind, schema=schema)

    def resolve(self, ref):
        return self.ledger.resolve(ref)

    def register_bytes(self, payload, *, kind, schema, media_type, registration_id):
        del registration_id
        return self.ledger.register_bytes(
            payload, kind=kind, schema=schema, media_type=media_type
        )


def registered(
    registrar: MemoryRegistrar,
    name: str,
    document=None,
    *,
    kind="fixture",
    schema="fixture/1",
):
    if document is None:
        document = {"name": name}
    return registrar.register_document(
        document, kind=kind, schema=schema, registration_id=name
    )


def registered_bytes(registrar, name, payload, *, kind, schema):
    return registrar.register_bytes(
        payload,
        kind=kind,
        schema=schema,
        media_type="application/octet-stream",
        registration_id=name,
    )


def make_delegation(
    registrar,
    *,
    effect,
    authorized_by,
    delegate_or_mechanism,
    scope,
    valid_from="2026-01-01T00:00:00Z",
    valid_until="2027-01-01T00:00:00Z",
):
    identity = {
        "schema_version": "caplab-authorization-delegation/1",
        "effect": effect,
        "authorized_by": authorized_by,
        "delegate_or_mechanism": delegate_or_mechanism,
        "scope": copy.deepcopy(scope),
        "valid_from": valid_from,
        "valid_until": valid_until,
    }
    document = {
        "delegation_id": "delegation-" + sha256_hex(canonical_json(identity)),
        **identity,
    }
    return registered(
        registrar,
        document["delegation_id"],
        document,
        kind="authorization-delegation",
        schema="caplab-authorization-delegation/1",
    )


def make_binding(registrar: MemoryRegistrar):
    binding, _ = make_executable_binding(registrar, Path("/usr/bin/true"))
    return binding


def make_local_fixture_contract(registrar, executable: Path):
    return registered(
        registrar,
        "fixture-native-contract",
        {
            "schema": "caplab.native-agent-systems/v1",
            "policy": "caplab-revbench-local-fixture-v1",
            "decision_authority": "adr-0062",
            "source_observation": {"contract": "caplab-revbench-local-fixture/1"},
            "systems": {
                LOCAL_FIXTURE_TUPLE: {
                    "model_id": LOCAL_FIXTURE_MODEL,
                    "native_harness_id": LOCAL_FIXTURE_HARNESS,
                    "harness_version": LOCAL_FIXTURE_HARNESS_VERSION,
                    "effort": "fixed",
                    "executable": str(executable),
                    "required_command_tokens": ["review"],
                    "version_command": [str(executable), "--version"],
                    "version_exit_code": 0,
                    "version_stdout_sha256": sha256_hex(LOCAL_FIXTURE_VERSION_STDOUT),
                    "version_stderr_sha256": sha256_hex(LOCAL_FIXTURE_VERSION_STDERR),
                }
            },
            "forbidden_proxy_markers": ["openrouter", "harbor", "terminus"],
            "exceptions": [],
        },
        kind="native-agent-systems-contract",
        schema="caplab.native-agent-systems/v1",
    )


def make_executable_binding(
    registrar: MemoryRegistrar,
    executable: Path,
    *,
    provider_kind: str = "local-serving",
):
    provider = {
        "kind": provider_kind,
        "identifier": LOCAL_FIXTURE_PROVIDER,
        "revision": LOCAL_FIXTURE_REVISION,
        "resolution": "immutable",
        "observed_at": None,
    }
    route_ref = registered(
        registrar,
        "fixture-route",
        {"schema_version": "caplab-provider-route/1", **provider},
        kind="provider-route",
        schema="caplab-provider-route/1",
    )
    executable_ref = registered_bytes(
        registrar,
        "fixture-executable",
        executable.read_bytes(),
        kind="harness-executable",
        schema="caplab-native-executable/1",
    )
    command_ref = registered(
        registrar,
        "fixture-command",
        {
            "schema_version": "caplab-native-harness-command/1",
            "argv": [str(executable), "review"],
        },
        kind="native-harness-command",
        schema="caplab-native-harness-command/1",
    )
    version_command_ref = registered(
        registrar,
        "fixture-version-command",
        {
            "schema_version": "caplab-native-harness-version-command/1",
            "argv": [str(executable), "--version"],
        },
        kind="native-harness-version-command",
        schema="caplab-native-harness-version-command/1",
    )
    version_stdout_ref = registered_bytes(
        registrar,
        "fixture-version-stdout",
        LOCAL_FIXTURE_VERSION_STDOUT,
        kind="native-harness-version-stdout",
        schema="caplab-native-process-stream/1",
    )
    version_stderr_ref = registered_bytes(
        registrar,
        "fixture-version-stderr",
        LOCAL_FIXTURE_VERSION_STDERR,
        kind="native-harness-version-stderr",
        schema="caplab-native-process-stream/1",
    )
    version_probe_ref = registered(
        registrar,
        "fixture-version-probe",
        {
            "command_ref": version_command_ref,
            "exit_code": 0,
            "stdout_ref": version_stdout_ref,
            "stderr_ref": version_stderr_ref,
        },
        kind="native-harness-version-probe",
        schema="caplab-native-harness-version-probe/1",
    )
    network_mode = "not-required"
    sandbox_adapter = Path("/usr/bin/bwrap")
    sandbox_adapter_ref = registered_bytes(
        registrar,
        "fixture-sandbox-executable",
        sandbox_adapter.read_bytes(),
        kind="sandbox-executable",
        schema="caplab-native-executable/1",
    )
    configuration_documents = {
        "inference": (
            "inference-configuration",
            {
                "schema_version": "caplab-revbench-inference/1",
                "command_ref": command_ref,
            },
        ),
        "instructions": (
            "instructions",
            {
                "schema_version": "caplab-revbench-instructions/1",
                "instruction": (
                    "Review the artifact against the requirement and return "
                    "exactly one JSON object."
                ),
            },
        ),
        "knowledge": (
            "knowledge",
            {
                "schema_version": "caplab-revbench-disabled-surface/1",
                "surface": "knowledge",
                "mode": "none",
            },
        ),
        "tools": (
            "tools",
            {
                "schema_version": "caplab-revbench-disabled-surface/1",
                "surface": "tools",
                "mode": "none",
            },
        ),
        "permissions": (
            "permissions",
            {
                "schema_version": "caplab-revbench-execution-permissions/1",
                "environment_keys": [],
                "filesystem_mode": "read-only-root-private-cwd",
                "network_mode": network_mode,
            },
        ),
        "sandbox": (
            "sandbox",
            {
                "schema_version": "caplab-revbench-execution-sandbox/1",
                "adapter_path": str(sandbox_adapter),
                "adapter_ref": sandbox_adapter_ref,
                "root_filesystem": "read-only",
                "working_directory": "private-write",
                "network_mode": network_mode,
            },
        ),
    }
    configurations = {
        name: registered(
            registrar,
            f"fixture-{name}",
            document,
            kind=kind,
            schema="caplab-binding-configuration/1",
        )
        for name, (kind, document) in configuration_documents.items()
    }
    runtime_ref = registered(
        registrar,
        "fixture-runtime",
        {
            "schema_version": "caplab-revbench-execution-runtime/1",
            "executable_path": str(executable),
            "executable_format": "static-elf",
            "environment_keys": [],
            "working_directory": "temporary-empty",
            "network_mode": network_mode,
            "stdin_mode": "canonical-json",
            "stdout_mode": "single-json",
        },
        kind="runtime",
        schema="caplab-binding-configuration/1",
    )
    binding = {
        "schema_version": "caplab-binding/1",
        "model": {
            "model_id": LOCAL_FIXTURE_MODEL,
            "revision": LOCAL_FIXTURE_REVISION,
            "weights_ref": None,
            "weights_unavailable_reason": "fixture has no model weights",
        },
        "provider_or_path": {**provider, "route_ref": route_ref},
        "harness": {
            "harness_id": LOCAL_FIXTURE_HARNESS,
            "harness_version": LOCAL_FIXTURE_HARNESS_VERSION,
            "executable_ref": executable_ref,
            "executable_unavailable_reason": None,
            "command_ref": command_ref,
            "version_probe_ref": version_probe_ref,
        },
        "reasoning_effort": "fixed",
        "configuration": {
            **{f"{name}_ref": ref for name, ref in configurations.items()},
            "runtime_ref": runtime_ref,
        },
    }
    binding["binding_id"] = "bnd-" + sha256_hex(canonical_json(binding))
    contract_ref = make_local_fixture_contract(registrar, executable)
    return binding, contract_ref


def write_fake_native(
    executable: Path,
    *,
    mode: str = "oracle",
    version: str = "fake-native 1\n",
    forbidden_environment_key: str | None = None,
    forbidden_network_port: int | None = None,
    forbidden_filesystem_path: Path | None = None,
) -> None:
    source = r"""
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

static const char *mode = @MODE@;
static const char *version_text = @VERSION@;
static const char *forbidden_environment_key = @ENVIRONMENT_KEY@;
static const char *forbidden_filesystem_path = @FILESYSTEM_PATH@;
static const int forbidden_network_port = @NETWORK_PORT@;

static char *read_stdin(void) {
    size_t used = 0;
    size_t capacity = 4096;
    char *buffer = malloc(capacity);
    if (buffer == NULL) return NULL;
    for (;;) {
        if (used + 2048 + 1 > capacity) {
            capacity *= 2;
            char *larger = realloc(buffer, capacity);
            if (larger == NULL) { free(buffer); return NULL; }
            buffer = larger;
        }
        size_t count = fread(buffer + used, 1, 2048, stdin);
        used += count;
        if (count < 2048) {
            if (ferror(stdin)) { free(buffer); return NULL; }
            break;
        }
    }
    buffer[used] = '\0';
    return buffer;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--version") == 0) {
        fputs(version_text, stdout);
        return 0;
    }
    if (*forbidden_environment_key != '\0' && getenv(forbidden_environment_key) != NULL) {
        fputs("ambient environment leaked", stderr);
        return 91;
    }
    if (forbidden_network_port >= 0) {
        int descriptor = socket(AF_INET, SOCK_STREAM, 0);
        struct sockaddr_in address;
        memset(&address, 0, sizeof(address));
        address.sin_family = AF_INET;
        address.sin_port = htons((unsigned short)forbidden_network_port);
        address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
        if (descriptor >= 0 && connect(descriptor, (struct sockaddr *)&address, sizeof(address)) == 0) {
            fputs("ambient network leaked", stderr);
            close(descriptor);
            return 92;
        }
        if (descriptor >= 0) close(descriptor);
    }
    if (*forbidden_filesystem_path != '\0') {
        FILE *secret = fopen(forbidden_filesystem_path, "rb");
        if (secret != NULL) {
            fputs("ambient filesystem leaked", stderr);
            fclose(secret);
            return 93;
        }
    }
    if (strcmp(mode, "sleep") == 0) {
        sleep(30);
        return 0;
    }
    char *request = read_stdin();
    if (request == NULL) return 94;
    if (strcmp(mode, "stdout-limit") == 0) {
        for (int index = 0; index < 4096; ++index) fputc('x', stdout);
        free(request);
        return 0;
    }
    if (strcmp(mode, "invalid") == 0) {
        fputs("not-json", stdout);
        free(request);
        return 0;
    }
    const char *pointer = NULL;
    int defect = 0;
    if (strstr(request, "\"pointer\":\"/n\"") != NULL) {
        pointer = "/n";
        defect = strstr(request, "\"artifact\":{\"n\":0}") != NULL;
    } else if (strstr(request, "\"pointer\":\"/limits/minimum\"") != NULL) {
        pointer = "/limits/minimum";
        defect = strstr(request, "\"artifact\":{\"label\":\"b\",\"limits\":{\"minimum\":2}}") != NULL;
    } else {
        free(request);
        return 95;
    }
    if (defect) {
        printf("{\"schema_version\":\"caplab-revbench-native-response/1\",\"verdict\":\"defect\",\"anchors\":[\"%s\"]}", pointer);
    } else {
        fputs("{\"schema_version\":\"caplab-revbench-native-response/1\",\"verdict\":\"clean\",\"anchors\":[]}", stdout);
    }
    free(request);
    return 0;
}
"""
    replacements = {
        "@MODE@": json.dumps(mode),
        "@VERSION@": json.dumps(version),
        "@ENVIRONMENT_KEY@": json.dumps(forbidden_environment_key or ""),
        "@FILESYSTEM_PATH@": json.dumps(
            str(forbidden_filesystem_path) if forbidden_filesystem_path else ""
        ),
        "@NETWORK_PORT@": str(
            forbidden_network_port if forbidden_network_port is not None else -1
        ),
    }
    for marker, replacement in replacements.items():
        source = source.replace(marker, replacement)
    source_path = executable.with_suffix(".c")
    source_path.write_text(source, encoding="utf-8")
    subprocess.run(
        ["gcc", "-static", "-O2", "-s", "-o", str(executable), str(source_path)],
        check=True,
        capture_output=True,
    )


def prepare_executable_manifest(registrar: MemoryRegistrar, executable: Path):
    binding, contract_ref = make_executable_binding(registrar, executable)
    return prepare(
        make_spec(
            registrar,
            binding=binding,
            native_system_contract_ref=contract_ref,
        ),
        registrar,
    )


def make_spec(
    registrar: MemoryRegistrar,
    *,
    binding=None,
    native_system_contract_ref=None,
):
    generated_contract_ref = None
    if binding is None:
        binding, generated_contract_ref = make_executable_binding(
            registrar, Path("/usr/bin/true")
        )
    if native_system_contract_ref is None:
        if generated_contract_ref is None:
            raise AssertionError("custom Binding requires its native-system contract")
        native_system_contract_ref = generated_contract_ref
    cases = [
        {
            "case_id": "case-b",
            "control": {"limits": {"minimum": 7}, "label": "b"},
            "mutation": {
                "operator": "replace-json-value/1",
                "pointer": "/limits/minimum",
                "replacement": 2,
            },
            "oracle": {
                "kind": "json-integer-minimum/1",
                "pointer": "/limits/minimum",
                "minimum": 5,
            },
            "defect_anchor": "/limits/minimum",
        },
        {
            "case_id": "case-a",
            "control": {"n": 5},
            "mutation": {
                "operator": "replace-json-value/1",
                "pointer": "/n",
                "replacement": 0,
            },
            "oracle": {
                "kind": "json-integer-minimum/1",
                "pointer": "/n",
                "minimum": 1,
            },
            "defect_anchor": "/n",
        },
    ]
    capability = {
        "name": "artifact-review",
        "version": "1",
        "role": "reviewer",
        "domain": "canonical-json",
        "distribution": "json-integer-minimum/1",
        "card_ref": registered(registrar, "card", kind="capability-card"),
    }
    protocol = registered(registrar, "protocol", kind="protocol")
    corpus = registered(registrar, "corpus", kind="corpus")
    included_case_refs = sorted(
        [
            registered(
                registrar,
                f"selected-{case['case_id']}",
                case,
                kind="case",
                schema="caplab-revbench-case/1",
            )
            for case in cases
        ],
        key=canonical_json,
    )
    population_ref = registered(registrar, "population", kind="case-population")
    selection_scope = {
        "population_ref": population_ref,
        "included_case_refs": included_case_refs,
        "excluded_case_refs": [],
        "selection_inputs": [],
        "exclusion_inputs": [],
        "conditioned_on": [],
    }
    selection_identity = {
        "schema_version": "caplab-case-selection-manifest/1",
        **selection_scope,
        "authorization_ref": make_delegation(
            registrar,
            effect="case-selection",
            authorized_by="repository owner",
            delegate_or_mechanism="caplab.revbench v1 explicit case list",
            scope=selection_scope,
        ),
    }
    selection = {
        "selection_id": "selection-" + sha256_hex(canonical_json(selection_identity)),
        **selection_identity,
    }
    case_selection_ref = registered(
        registrar,
        "selection",
        selection,
        kind="case-selection",
        schema="caplab-case-selection-manifest/1",
    )
    method_ref = registered(registrar, "revbench-method", kind="protocol")
    authorizations = {}
    for key, role in (
        ("truth", "truth"),
        ("case_selection", "case-selection"),
        ("metric_derivation", "metric-derivation"),
    ):
        scope = {
            "binding_ids": [binding["binding_id"]],
            "capability": capability,
            "experiment": {"family": "revbench", "version": "1"},
            "protocol_ref": protocol,
            "corpus_ref": corpus,
            "case_selection_ref": case_selection_ref,
            "method_ref": method_ref,
            "basis_kind": "mechanical-oracle",
            "basis_role": role,
        }
        identity = {
            "schema_version": "caplab-evidence-basis-authorization/1",
            "authority_source_ref": make_delegation(
                registrar,
                effect="evidence-basis",
                authorized_by="repository owner",
                delegate_or_mechanism="caplab.revbench v1 deterministic mechanism",
                scope=scope,
            ),
            "authorized_by": "repository owner",
            "delegate_or_mechanism": "caplab.revbench v1 deterministic mechanism",
            **scope,
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2027-01-01T00:00:00Z",
        }
        authorization = {
            "authorization_id": "basis-auth-" + sha256_hex(canonical_json(identity)),
            **identity,
        }
        authorizations[key] = registered(
            registrar,
            f"auth-{key}",
            authorization,
            kind="evidence-basis-authorization",
            schema="caplab-evidence-basis-authorization/1",
        )
    return {
        "schema_version": "caplab-revbench-spec/1",
        "binding": binding,
        "capability": capability,
        "protocol": protocol,
        "corpus": corpus,
        "native_system_contract_ref": native_system_contract_ref,
        "case_selection_ref": case_selection_ref,
        "basis_authorization_refs": authorizations,
        "cases": cases,
        "provenance": {
            "caplab_version": "0.1.0",
            "caplab_commit": "a" * 40,
            "source_refs": [],
        },
    }


def reseal_case_scope(registrar: MemoryRegistrar, spec):
    selection = json.loads(registrar.resolve(spec["case_selection_ref"]))
    selection["included_case_refs"] = sorted(
        [
            registered(
                registrar,
                f"reselected-{case['case_id']}",
                case,
                kind="case",
                schema="caplab-revbench-case/1",
            )
            for case in spec["cases"]
        ],
        key=canonical_json,
    )
    selection_scope = {
        key: selection[key]
        for key in (
            "population_ref",
            "included_case_refs",
            "excluded_case_refs",
            "selection_inputs",
            "exclusion_inputs",
            "conditioned_on",
        )
    }
    selection["authorization_ref"] = make_delegation(
        registrar,
        effect="case-selection",
        authorized_by="repository owner",
        delegate_or_mechanism="caplab.revbench v1 explicit case list",
        scope=selection_scope,
    )
    selection_identity = copy.deepcopy(selection)
    selection_identity.pop("selection_id")
    selection["selection_id"] = "selection-" + sha256_hex(
        canonical_json(selection_identity)
    )
    selection_ref = registered(
        registrar,
        f"reselection-{selection['selection_id']}",
        selection,
        kind="case-selection",
        schema="caplab-case-selection-manifest/1",
    )
    spec["case_selection_ref"] = selection_ref
    for role, old_ref in list(spec["basis_authorization_refs"].items()):
        authorization = json.loads(registrar.resolve(old_ref))
        authorization["case_selection_ref"] = selection_ref
        authorization_scope = {
            key: authorization[key]
            for key in (
                "binding_ids",
                "capability",
                "experiment",
                "protocol_ref",
                "corpus_ref",
                "case_selection_ref",
                "method_ref",
                "basis_kind",
                "basis_role",
            )
        }
        authorization["authority_source_ref"] = make_delegation(
            registrar,
            effect="evidence-basis",
            authorized_by=authorization["authorized_by"],
            delegate_or_mechanism=authorization["delegate_or_mechanism"],
            scope=authorization_scope,
            valid_from=authorization["valid_from"],
            valid_until=authorization["valid_until"],
        )
        authorization_identity = copy.deepcopy(authorization)
        authorization_identity.pop("authorization_id")
        authorization["authorization_id"] = "basis-auth-" + sha256_hex(
            canonical_json(authorization_identity)
        )
        spec["basis_authorization_refs"][role] = registered(
            registrar,
            f"rescoped-{role}-{authorization['authorization_id']}",
            authorization,
            kind="evidence-basis-authorization",
            schema="caplab-evidence-basis-authorization/1",
        )


def make_execution_authorization(
    registrar,
    manifest,
    *,
    limits_override=None,
    valid_from="2026-01-01T00:00:00Z",
    valid_until="2027-01-01T00:00:00Z",
    apparatus_ref=None,
    custody_domain_id=None,
):
    manifest_ref = registered(
        registrar,
        f"manifest-{manifest['experiment_id']}",
        manifest,
        kind="revbench-manifest",
        schema="caplab-revbench-manifest/1",
    )
    limits = {
        "max_version_probe_processes": len(manifest["cases"]) * 2,
        "max_native_review_processes": len(manifest["cases"]) * 2,
        "timeout_seconds_per_process": 30,
        "total_wall_seconds": 120,
        "max_stdout_bytes_per_process": 65536,
        "max_stderr_bytes_per_process": 65536,
    }
    limits.update(limits_override or {})
    scope = {
        "experiment_id": manifest["experiment_id"],
        "manifest_ref": manifest_ref,
        "binding_id": manifest["binding"]["binding_id"],
        "native_system_contract_ref": manifest["native_system_contract_ref"],
        "command_ref": manifest["binding"]["harness"]["command_ref"],
        "version_probe_ref": manifest["binding"]["harness"]["version_probe_ref"],
        "effect_class": (
            "local-fixture"
            if manifest["binding"]["provider_or_path"]["kind"] == "local-serving"
            else "live-native-provider"
        ),
        "limits": limits,
    }
    if manifest["binding"]["provider_or_path"]["kind"] != "local-serving":
        if apparatus_ref is None:
            raise ValueError("live execution authorization requires apparatus_ref")
        if custody_domain_id is None:
            raise ValueError("live execution authorization requires custody_domain_id")
        scope["apparatus_ref"] = copy.deepcopy(apparatus_ref)
        scope["custody_domain_id"] = custody_domain_id
    identity = {
        "schema_version": "caplab-revbench-execution-authorization/1",
        "authority_source_ref": make_delegation(
            registrar,
            effect="revbench-execution",
            authorized_by="repository owner",
            delegate_or_mechanism="caplab.revbench execute v1",
            scope=scope,
            valid_from=valid_from,
            valid_until=valid_until,
        ),
        "authorized_by": "repository owner",
        "delegate_or_mechanism": "caplab.revbench execute v1",
        **scope,
        "valid_from": valid_from,
        "valid_until": valid_until,
    }
    authorization = {
        "authorization_id": "revbench-execution-auth-"
        + sha256_hex(canonical_json(identity)),
        **identity,
    }
    return registered(
        registrar,
        authorization["authorization_id"],
        authorization,
        kind="revbench-execution-authorization",
        schema="caplab-revbench-execution-authorization/1",
    )


def make_reviews(registrar: MemoryRegistrar, manifest, outcomes=None):
    outcomes = outcomes or {}
    execution_authorization_ref = make_execution_authorization(registrar, manifest)
    probe = json.loads(
        registrar.resolve(manifest["binding"]["harness"]["version_probe_ref"])
    )
    attempts = []
    for case_index, case in enumerate(manifest["cases"]):
        for assignment_index, arm in enumerate(case["assignment_order"]):
            disposition, verdict, anchors = outcomes.get(
                (case["case_id"], arm),
                (
                    "complete",
                    "clean" if arm == "control" else "defect",
                    [] if arm == "control" else [case["defect_anchor"]],
                ),
            )
            native_input = {
                "schema_version": "caplab-revbench-native-input/1",
                "instruction": "Review the artifact against the requirement and return exactly one JSON object.",
                "requirement": case["oracle"],
                "artifact": case[arm]["content"],
                "response_schema_version": "caplab-revbench-native-response/1",
            }
            input_ref = registered(
                registrar,
                f"input-{case['case_id']}-{arm}",
                native_input,
                kind="native-input",
                schema="caplab-revbench-native-input/1",
            )
            stdin_ref = registered_bytes(
                registrar,
                f"stdin-{case['case_id']}-{arm}",
                canonical_json(native_input),
                kind="native-process-stdin",
                schema="caplab-native-process-stream/1",
            )
            prompt_ref = registered(
                registrar,
                f"prompt-v2-{case['case_id']}-{arm}",
                {
                    "schema_version": "caplab-revbench-prompt/1",
                    "experiment_id": manifest["experiment_id"],
                    "case_id": case["case_id"],
                    "arm": arm,
                    "assignment_index": assignment_index,
                    "binding_id": manifest["binding"]["binding_id"],
                    "protocol_ref": manifest["protocol"],
                    "rendered_input_ref": input_ref,
                },
                kind="prompt",
                schema="caplab-revbench-prompt/1",
            )
            if disposition == "complete":
                raw_stdout = canonical_json(
                    {
                        "schema_version": "caplab-revbench-native-response/1",
                        "verdict": verdict,
                        "anchors": anchors,
                    }
                )
                parse_status = "valid"
                exit_code = 0
                termination = "exited"
                native_invoked = True
            elif disposition == "subject-failure":
                raw_stdout = b"not-json"
                parse_status = "invalid"
                verdict, anchors = "invalid", []
                exit_code = 0
                termination = "exited"
                native_invoked = True
            else:
                raw_stdout = b""
                parse_status = "invalid"
                verdict, anchors = "invalid", []
                exit_code = 1
                termination = "exited"
                native_invoked = True
            stdout_ref = registered_bytes(
                registrar,
                f"stdout-{case['case_id']}-{arm}",
                raw_stdout,
                kind="native-process-stdout",
                schema="caplab-native-process-stream/1",
            )
            stderr_ref = registered_bytes(
                registrar,
                f"stderr-{case['case_id']}-{arm}",
                b"",
                kind="native-process-stderr",
                schema="caplab-native-process-stream/1",
            )
            output_ref = registered(
                registrar,
                f"output-v2-{case['case_id']}-{arm}",
                {
                    "schema_version": "caplab-native-output/1",
                    "experiment_id": manifest["experiment_id"],
                    "case_id": case["case_id"],
                    "arm": arm,
                    "assignment_index": assignment_index,
                    "binding_id": manifest["binding"]["binding_id"],
                    "raw_stdout_ref": stdout_ref,
                    "parse_status": parse_status,
                    "verdict": verdict,
                    "anchors": anchors,
                },
                kind="native-output",
                schema="caplab-native-output/1",
            )
            ordinal = case_index * 2 + assignment_index
            started_at = f"2026-08-14T11:59:{ordinal * 2:02d}Z"
            completed_at = f"2026-08-14T11:59:{ordinal * 2 + 1:02d}Z"
            version_stdout_ref = registered_bytes(
                registrar,
                f"observed-version-stdout-{case['case_id']}-{arm}",
                registrar.resolve(probe["stdout_ref"]),
                kind="native-process-stdout",
                schema="caplab-native-process-stream/1",
            )
            version_stderr_ref = registered_bytes(
                registrar,
                f"observed-version-stderr-{case['case_id']}-{arm}",
                registrar.resolve(probe["stderr_ref"]),
                kind="native-process-stderr",
                schema="caplab-native-process-stream/1",
            )
            version_identity = {
                "schema_version": "caplab-native-version-observation/1",
                "execution_authorization_ref": execution_authorization_ref,
                "experiment_id": manifest["experiment_id"],
                "binding_id": manifest["binding"]["binding_id"],
                "expected_version_probe_ref": manifest["binding"]["harness"][
                    "version_probe_ref"
                ],
                "command_ref": probe["command_ref"],
                "started_at": started_at,
                "completed_at": started_at,
                "stdout_ref": version_stdout_ref,
                "stdout_complete": True,
                "stderr_ref": version_stderr_ref,
                "stderr_complete": True,
                "exit_code": 0,
                "termination": "exited",
                "matches_expected": True,
            }
            version = {
                "observation_id": "version-observation-"
                + sha256_hex(canonical_json(version_identity)),
                **version_identity,
            }
            version_ref = registered(
                registrar,
                version["observation_id"],
                version,
                kind="native-version-observation",
                schema="caplab-native-version-observation/1",
            )
            capture_identity = {
                "schema_version": "caplab-native-attempt-capture/1",
                "execution_authorization_ref": execution_authorization_ref,
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "binding_id": manifest["binding"]["binding_id"],
                "observed_binding": copy.deepcopy(manifest["binding"]),
                "started_at": started_at,
                "completed_at": completed_at,
                "command_ref": manifest["binding"]["harness"]["command_ref"],
                "version_observation_ref": version_ref,
                "prompt_ref": prompt_ref,
                "stdin_ref": stdin_ref,
                "stdout_ref": stdout_ref,
                "stdout_complete": True,
                "stderr_ref": stderr_ref,
                "stderr_complete": True,
                "output_ref": output_ref,
                "native_invoked": native_invoked,
                "exit_code": exit_code,
                "termination": termination,
            }
            capture = {
                "capture_id": "capture-" + sha256_hex(canonical_json(capture_identity)),
                **capture_identity,
            }
            capture_ref = registered(
                registrar,
                capture["capture_id"],
                capture,
                kind="native-attempt-capture",
                schema="caplab-native-attempt-capture/1",
            )
            attestation_identity = {
                "schema_version": "caplab-native-attempt-attestation/1",
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "observed_at": completed_at,
                "observed_binding": copy.deepcopy(manifest["binding"]),
                "native_system_contract_ref": manifest["native_system_contract_ref"],
                "execution_authorization_ref": execution_authorization_ref,
                "version_observation_ref": version_ref,
                "capture_ref": capture_ref,
                "prompt_ref": prompt_ref,
                "output_ref": output_ref,
            }
            attestation = {
                "attestation_id": "attestation-"
                + sha256_hex(canonical_json(attestation_identity)),
                **attestation_identity,
            }
            attestation_ref = registered(
                registrar,
                attestation["attestation_id"],
                attestation,
                kind="native-attempt-attestation",
                schema="caplab-native-attempt-attestation/1",
            )
            envelope_identity = {
                "schema_version": "caplab-native-review-attempt/1",
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "assignment_index": assignment_index,
                "binding_id": manifest["binding"]["binding_id"],
                "observed_binding": copy.deepcopy(manifest["binding"]),
                "attestation_ref": attestation_ref,
                "prompt_ref": prompt_ref,
                "disposition": disposition,
                "verdict": verdict,
                "anchors": anchors,
                "output_ref": output_ref,
                "provenance": copy.deepcopy(manifest["provenance"]),
            }
            envelope = {
                "attempt_id": "attempt-"
                + sha256_hex(canonical_json(envelope_identity)),
                **envelope_identity,
            }
            attempt_ref = registered(
                registrar,
                envelope["attempt_id"],
                envelope,
                kind="attempt",
                schema="caplab-native-review-attempt/1",
            )
            attempts.append(
                {
                    "case_id": case["case_id"],
                    "arm": arm,
                    "assignment_index": assignment_index,
                    "binding_id": manifest["binding"]["binding_id"],
                    "observed_binding": copy.deepcopy(manifest["binding"]),
                    "attempt_ref": attempt_ref,
                    "attestation_ref": attestation_ref,
                    "prompt_ref": prompt_ref,
                    "disposition": disposition,
                    "verdict": verdict,
                    "anchors": anchors,
                    "output_ref": output_ref,
                }
            )
    identity = {
        "schema_version": "caplab-revbench-reviews/1",
        "experiment_id": manifest["experiment_id"],
        "execution_authorization_ref": execution_authorization_ref,
        "started_at": "2026-08-14T11:59:00Z",
        "observed_at": "2026-08-14T12:00:00Z",
        "status": "complete",
        "stop_reason": None,
        "attempts": attempts,
    }
    return {
        "execution_id": "execution-" + sha256_hex(canonical_json(identity)),
        **identity,
    }


def reseal_execution(reviews):
    identity = copy.deepcopy(reviews)
    identity.pop("execution_id")
    reviews["execution_id"] = "execution-" + sha256_hex(canonical_json(identity))


def reseal_attempt_envelope(registrar: MemoryRegistrar, attempt):
    old_envelope = json.loads(registrar.resolve(attempt["attempt_ref"]))
    identity = {
        "schema_version": "caplab-native-review-attempt/1",
        "experiment_id": old_envelope["experiment_id"],
        **{
            key: copy.deepcopy(value)
            for key, value in attempt.items()
            if key != "attempt_ref"
        },
        "provenance": old_envelope["provenance"],
    }
    envelope = {
        "attempt_id": "attempt-" + sha256_hex(canonical_json(identity)),
        **identity,
    }
    attempt["attempt_ref"] = registered(
        registrar,
        f"resealed-{envelope['attempt_id']}",
        envelope,
        kind="attempt",
        schema="caplab-native-review-attempt/1",
    )


class PrepareTests(unittest.TestCase):
    def test_prepare_is_deterministic_and_builds_verified_mutants(self):
        registrar = MemoryRegistrar()
        spec = make_spec(registrar)

        first = prepare(spec, registrar)
        second = prepare(copy.deepcopy(spec), registrar)

        self.assertEqual(first, second)
        self.assertEqual(
            [case["case_id"] for case in first["cases"]], ["case-a", "case-b"]
        )
        self.assertEqual(first["family"], "revbench")
        self.assertEqual(first["family_version"], "1")
        for case in first["cases"]:
            self.assertTrue(case["control"]["oracle_result"])
            self.assertFalse(case["mutant"]["oracle_result"])
            self.assertEqual(
                case["control"]["sha256"],
                sha256_hex(canonical_json(case["control"]["content"])),
            )
            self.assertEqual(
                case["mutant"]["sha256"],
                sha256_hex(canonical_json(case["mutant"]["content"])),
            )

    def test_prepare_rejects_unknown_fields_and_broken_oracles(self):
        registrar = MemoryRegistrar()
        spec = make_spec(registrar)
        spec["surprise"] = True
        with self.assertRaisesRegex(RevbenchContractError, "unknown field"):
            prepare(spec, registrar)

        spec = make_spec(registrar)
        spec["cases"][0]["mutation"]["replacement"] = 99
        with self.assertRaisesRegex(RevbenchContractError, "below minimum"):
            prepare(spec, registrar)

        spec = make_spec(registrar)
        spec["cases"].append(copy.deepcopy(spec["cases"][0]))
        with self.assertRaisesRegex(RevbenchContractError, "duplicate"):
            prepare(spec, registrar)

        spec = make_spec(registrar)
        spec["cases"][0]["mutation"]["pointer"] = "/limits/01"
        spec["cases"][0]["oracle"]["pointer"] = "/limits/01"
        spec["cases"][0]["defect_anchor"] = "/limits/01"
        with self.assertRaisesRegex(
            RevbenchContractError, "does not exist|array index"
        ):
            prepare(spec, registrar)

    def test_prepare_resolves_all_registered_references(self):
        registrar = MemoryRegistrar()
        spec = make_spec(registrar)
        auth_ref = spec["basis_authorization_refs"]["truth"]
        registrar.documents[auth_ref["sha256"]] = b"tampered"

        with self.assertRaisesRegex(RevbenchContractError, "byte count|SHA-256"):
            prepare(spec, registrar)

    def test_prepare_requires_registered_native_tuple_and_valid_binding(self):
        registrar = MemoryRegistrar()
        spec = make_spec(registrar)
        spec["native_system_contract_ref"] = registered(
            registrar,
            "empty-native-contract",
            {
                "schema": "caplab.native-agent-systems/v1",
                "systems": {},
                "exceptions": [],
            },
            kind="native-agent-systems-contract",
            schema="caplab.native-agent-systems/v1",
        )
        with self.assertRaisesRegex(RevbenchContractError, "systems|tuple"):
            prepare(spec, registrar)

        spec = make_spec(registrar)
        spec["binding"]["harness"]["version_probe_ref"] = registered(
            registrar,
            "malformed-probe",
            {"name": "not a version probe"},
            kind="fixture",
            schema="fixture/1",
        )
        spec["binding"]["binding_id"] = derive_content_id(
            spec["binding"], "binding_id", "bnd-"
        )
        with self.assertRaisesRegex(RevbenchContractError, "version_probe"):
            prepare(spec, registrar)

    def test_prepare_refuses_caller_defined_live_provider_policy(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable)
            binding, contract_ref = make_executable_binding(
                registrar, executable, provider_kind="direct-provider"
            )
            spec = make_spec(
                registrar,
                binding=binding,
                native_system_contract_ref=contract_ref,
            )

            with self.assertRaisesRegex(
                RevbenchContractError,
                "does not match docs/product/contracts/native-agent-systems.json",
            ):
                prepare(spec, registrar)

    def test_prepare_refuses_unsupported_live_provider_profile(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable)
            binding, _ = make_executable_binding(
                registrar, executable, provider_kind="direct-provider"
            )
            policy = json.loads(
                (ROOT / "docs/product/contracts/native-agent-systems.json").read_bytes()
            )
            contract_ref = registered(
                registrar,
                "repository-native-system-contract",
                policy,
                kind="native-agent-systems-contract",
                schema="caplab.native-agent-systems/v1",
            )
            spec = make_spec(
                registrar,
                binding=binding,
                native_system_contract_ref=contract_ref,
            )

            with self.assertRaisesRegex(
                RevbenchContractError,
                "binding.provider_or_path.identifier",
            ):
                prepare(spec, registrar)

    def test_prepare_refuses_local_fixture_impersonation_and_version_claims(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable)
            binding, contract_ref = make_executable_binding(registrar, executable)

            impersonated = copy.deepcopy(binding)
            impersonated["model"]["model_id"] = "gpt-5.6-terra"
            impersonated["harness"]["harness_id"] = "codex"
            impersonated["reasoning_effort"] = "max"
            impersonated["binding_id"] = derive_content_id(
                impersonated, "binding_id", "bnd-"
            )
            with self.assertRaisesRegex(
                RevbenchContractError, "binding.model.model_id"
            ):
                prepare(
                    make_spec(
                        registrar,
                        binding=impersonated,
                        native_system_contract_ref=contract_ref,
                    ),
                    registrar,
                )

            wrong_version = copy.deepcopy(binding)
            wrong_version["harness"]["harness_version"] = "made-up-version"
            wrong_version["binding_id"] = derive_content_id(
                wrong_version, "binding_id", "bnd-"
            )
            with self.assertRaisesRegex(
                RevbenchContractError, "binding.harness.harness_version"
            ):
                prepare(
                    make_spec(
                        registrar,
                        binding=wrong_version,
                        native_system_contract_ref=contract_ref,
                    ),
                    registrar,
                )

    def test_prepare_refuses_hidden_local_fixture_command_selectors(self):
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable)
            for override in (
                ["-mswapped/model"],
                ["-cmodel_provider=local"],
                ["--profile", "attacker"],
            ):
                with self.subTest(override=override):
                    registrar = MemoryRegistrar()
                    binding, contract_ref = make_executable_binding(
                        registrar, executable
                    )
                    command = json.loads(
                        registrar.resolve(binding["harness"]["command_ref"])
                    )
                    command["argv"].extend(override)
                    binding["harness"]["command_ref"] = registered(
                        registrar,
                        "hidden-selector-command",
                        command,
                        kind="native-harness-command",
                        schema="caplab-native-harness-command/1",
                    )
                    binding["binding_id"] = derive_content_id(
                        binding, "binding_id", "bnd-"
                    )

                    with self.assertRaisesRegex(
                        RevbenchContractError,
                        "binding.harness.command_ref document.argv",
                    ):
                        prepare(
                            make_spec(
                                registrar,
                                binding=binding,
                                native_system_contract_ref=contract_ref,
                            ),
                            registrar,
                        )

    def test_prepare_pins_local_fixture_executable_and_probe_bytes(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable)
            binding, contract_ref = make_executable_binding(registrar, executable)

            no_executable = copy.deepcopy(binding)
            no_executable["harness"]["executable_ref"] = None
            no_executable["harness"]["executable_unavailable_reason"] = (
                "caller did not retain fixture bytes"
            )
            no_executable["binding_id"] = derive_content_id(
                no_executable, "binding_id", "bnd-"
            )
            with self.assertRaisesRegex(
                RevbenchContractError, "executable_ref.*required"
            ):
                prepare(
                    make_spec(
                        registrar,
                        binding=no_executable,
                        native_system_contract_ref=contract_ref,
                    ),
                    registrar,
                )

            wrong_probe = copy.deepcopy(binding)
            probe = json.loads(
                registrar.resolve(wrong_probe["harness"]["version_probe_ref"])
            )
            probe["stdout_ref"] = registered_bytes(
                registrar,
                "wrong-version-stdout",
                b"fake-native 999\n",
                kind="native-harness-version-stdout",
                schema="caplab-native-process-stream/1",
            )
            wrong_probe["harness"]["version_probe_ref"] = registered(
                registrar,
                "wrong-version-probe",
                probe,
                kind="native-harness-version-probe",
                schema="caplab-native-harness-version-probe/1",
            )
            wrong_probe["binding_id"] = derive_content_id(
                wrong_probe, "binding_id", "bnd-"
            )
            with self.assertRaisesRegex(
                RevbenchContractError,
                "does not match the pinned fixture version observation",
            ):
                prepare(
                    make_spec(
                        registrar,
                        binding=wrong_probe,
                        native_system_contract_ref=contract_ref,
                    ),
                    registrar,
                )

            forged_policy = json.loads(registrar.resolve(contract_ref))
            forged_policy["systems"][LOCAL_FIXTURE_TUPLE]["version_stdout_sha256"] = (
                sha256_hex(b"fake-native 999\n")
            )
            forged_contract_ref = registered(
                registrar,
                "forged-version-contract",
                forged_policy,
                kind="native-agent-systems-contract",
                schema="caplab.native-agent-systems/v1",
            )
            with self.assertRaisesRegex(RevbenchContractError, "version_stdout_sha256"):
                prepare(
                    make_spec(
                        registrar,
                        binding=wrong_probe,
                        native_system_contract_ref=forged_contract_ref,
                    ),
                    registrar,
                )

    def test_revbench_v1_refuses_hidden_selection_inputs(self):
        registrar = MemoryRegistrar()
        spec = make_spec(registrar)
        selection = json.loads(registrar.resolve(spec["case_selection_ref"]))
        selection["selection_inputs"] = [
            registered(
                registrar,
                "hidden-fate-input",
                {"downstream_fate": "final"},
                kind="downstream-fate",
                schema="observation/1",
            )
        ]
        selection["selection_id"] = derive_content_id(
            selection, "selection_id", "selection-"
        )
        spec["case_selection_ref"] = registered(
            registrar,
            "fate-selected-cases",
            selection,
            kind="case-selection",
            schema="caplab-case-selection-manifest/1",
        )

        with self.assertRaisesRegex(RevbenchContractError, "no selection inputs"):
            prepare(spec, registrar)

    def test_prepare_keeps_pointer_aliases_distinct(self):
        registrar = MemoryRegistrar()
        spec = make_spec(registrar)
        spec["cases"] = [
            {
                "case_id": "alias",
                "control": {"a/b": 5, "a~1b": 9},
                "mutation": {
                    "operator": "replace-json-value/1",
                    "pointer": "/a~01b",
                    "replacement": 0,
                },
                "oracle": {
                    "kind": "json-integer-minimum/1",
                    "pointer": "/a~01b",
                    "minimum": 1,
                },
                "defect_anchor": "/a~01b",
            }
        ]
        reseal_case_scope(registrar, spec)

        manifest = prepare(spec, registrar)

        self.assertEqual(manifest["cases"][0]["mutant"]["content"]["a~1b"], 0)
        self.assertEqual(manifest["cases"][0]["mutant"]["content"]["a/b"], 5)


class ScoreTests(unittest.TestCase):
    def test_execute_uses_real_blinded_native_process_then_scores(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            host_secret = Path(temporary) / "host-secret"
            host_secret.write_text("must stay outside the sandbox", encoding="utf-8")
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                listener.listen()
                write_fake_native(
                    executable,
                    forbidden_environment_key="CAPLAB_EXECUTION_SECRET",
                    forbidden_network_port=listener.getsockname()[1],
                    forbidden_filesystem_path=host_secret,
                )
                binding, contract_ref = make_executable_binding(registrar, executable)
                manifest = prepare(
                    make_spec(
                        registrar,
                        binding=binding,
                        native_system_contract_ref=contract_ref,
                    ),
                    registrar,
                )
                authorization_ref = make_execution_authorization(registrar, manifest)

                with mock.patch.dict(
                    os.environ, {"CAPLAB_EXECUTION_SECRET": "do-not-leak"}
                ):
                    reviews = execute(manifest, authorization_ref, registrar)
                measurement = score(manifest, reviews, registrar)

        self.assertEqual(reviews["status"], "complete")
        self.assertEqual(len(reviews["attempts"]), 4)
        self.assertEqual(measurement["disposition"], "complete")
        self.assertEqual(
            measurement["metrics"]["catch_rate"]["value"],
            {"numerator": 1, "denominator": 1},
        )
        for attempt in reviews["attempts"]:
            prompt = json.loads(registrar.resolve(attempt["prompt_ref"]))
            native_input = json.loads(registrar.resolve(prompt["rendered_input_ref"]))
            self.assertNotIn("arm", native_input)
            self.assertNotIn("defect_anchor", native_input)
            self.assertNotIn("mutation", native_input)

    def test_real_execution_records_validate_against_published_schema(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable)
            binding, contract_ref = make_executable_binding(registrar, executable)
            spec = make_spec(
                registrar,
                binding=binding,
                native_system_contract_ref=contract_ref,
            )
            manifest = prepare(spec, registrar)
            authorization_ref = make_execution_authorization(registrar, manifest)
            reviews = execute(manifest, authorization_ref, registrar)

        contracts = ROOT / "docs" / "product" / "contracts"
        schema = json.loads((contracts / "revbench-v1.schema.json").read_bytes())
        claim_schema = json.loads(
            (contracts / "qualification-claim-v1.schema.json").read_bytes()
        )
        live_schema = json.loads(
            (contracts / "revbench-live-native-v1.schema.json").read_bytes()
        )
        Draft202012Validator.check_schema(schema)
        Draft202012Validator.check_schema(live_schema)
        registry = Registry().with_resources(
            (
                (claim_schema["$id"], Resource.from_contents(claim_schema)),
                (live_schema["$id"], Resource.from_contents(live_schema)),
            )
        )
        validator = Draft202012Validator(schema, registry=registry)
        record_versions = {
            "caplab-revbench-execution-runtime/1",
            "caplab-revbench-inference/1",
            "caplab-revbench-instructions/1",
            "caplab-revbench-disabled-surface/1",
            "caplab-revbench-execution-permissions/1",
            "caplab-revbench-execution-sandbox/1",
            "caplab-revbench-native-input/1",
            "caplab-revbench-native-response/1",
            "caplab-revbench-prompt/1",
            "caplab-native-version-observation/1",
            "caplab-native-output/1",
            "caplab-native-attempt-capture/1",
            "caplab-native-attempt-attestation/1",
            "caplab-native-review-attempt/1",
        }
        documents = [
            spec,
            manifest,
            json.loads(registrar.resolve(authorization_ref)),
            reviews,
        ]
        for raw in registrar.documents.values():
            try:
                document = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if (
                isinstance(document, dict)
                and document.get("schema_version") in record_versions
            ):
                documents.append(document)

        for document in documents:
            with self.subTest(schema_version=document["schema_version"]):
                validator.validate(document)

    def test_execute_refuses_drifted_executable_and_sandbox_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            registrar = MemoryRegistrar()
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable)
            manifest = prepare_executable_manifest(registrar, executable)
            authorization_ref = make_execution_authorization(registrar, manifest)
            executable.write_bytes(executable.read_bytes() + b"\n# drift\n")

            with self.assertRaisesRegex(
                RevbenchContractError, "does not match executable bytes"
            ):
                execute(manifest, authorization_ref, registrar)

        with tempfile.TemporaryDirectory() as temporary:
            registrar = MemoryRegistrar()
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable)
            manifest = prepare_executable_manifest(registrar, executable)
            authorization_ref = make_execution_authorization(registrar, manifest)
            sandbox = json.loads(
                registrar.resolve(manifest["binding"]["configuration"]["sandbox_ref"])
            )
            adapter_ref = sandbox["adapter_ref"]
            registrar.documents[adapter_ref["sha256"]] = b"drift"

            with self.assertRaisesRegex(RevbenchContractError, "byte count|SHA-256"):
                execute(manifest, authorization_ref, registrar)

    def test_execute_refuses_dynamic_or_unsupported_live_native_profiles(self):
        with tempfile.TemporaryDirectory() as temporary:
            registrar = MemoryRegistrar()
            executable = Path(temporary) / "dynamic-native"
            executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            executable.chmod(0o700)
            manifest = prepare_executable_manifest(registrar, executable)
            authorization_ref = make_execution_authorization(registrar, manifest)

            with self.assertRaisesRegex(
                RevbenchContractError, "self-contained static ELF"
            ):
                execute(manifest, authorization_ref, registrar)

        with tempfile.TemporaryDirectory() as temporary:
            registrar = MemoryRegistrar()
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable)
            binding, _ = make_executable_binding(
                registrar,
                executable,
                provider_kind="direct-provider",
            )
            contract_ref = registered(
                registrar,
                "repository-native-system-contract",
                json.loads(
                    (
                        ROOT / "docs/product/contracts/native-agent-systems.json"
                    ).read_bytes()
                ),
                kind="native-agent-systems-contract",
                schema="caplab.native-agent-systems/v1",
            )

            with self.assertRaisesRegex(
                RevbenchContractError,
                "binding.provider_or_path.identifier",
            ):
                prepare(
                    make_spec(
                        registrar,
                        binding=binding,
                        native_system_contract_ref=contract_ref,
                    ),
                    registrar,
                )

    def test_version_drift_stops_before_native_review(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable, version="fake-native 2\n")
            manifest = prepare_executable_manifest(registrar, executable)
            authorization_ref = make_execution_authorization(registrar, manifest)

            reviews = execute(manifest, authorization_ref, registrar)
            measurement = score(manifest, reviews, registrar)

        self.assertEqual(reviews["status"], "stopped")
        self.assertEqual(reviews["stop_reason"], "preflight-refused")
        self.assertEqual(len(reviews["attempts"]), 1)
        attempt = reviews["attempts"][0]
        self.assertEqual(attempt["disposition"], "infrastructure-failure")
        attestation = json.loads(registrar.resolve(attempt["attestation_ref"]))
        capture = json.loads(registrar.resolve(attestation["capture_ref"]))
        version = json.loads(registrar.resolve(attestation["version_observation_ref"]))
        self.assertFalse(version["matches_expected"])
        self.assertFalse(capture["native_invoked"])
        self.assertEqual(capture["termination"], "preflight-refused")
        self.assertEqual(measurement["disposition"], "infrastructure-failure")

    def test_nonreading_native_times_out_with_large_nonblocking_stdin(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable, mode="sleep")
            binding, contract_ref = make_executable_binding(registrar, executable)
            spec = make_spec(
                registrar,
                binding=binding,
                native_system_contract_ref=contract_ref,
            )
            for case in spec["cases"]:
                case["control"]["padding"] = "x" * (1024 * 1024)
            reseal_case_scope(registrar, spec)
            manifest = prepare(spec, registrar)
            authorization_ref = make_execution_authorization(
                registrar,
                manifest,
                limits_override={
                    "timeout_seconds_per_process": 1,
                    "total_wall_seconds": 10,
                },
            )

            started = time.monotonic()
            reviews = execute(manifest, authorization_ref, registrar)
            elapsed = time.monotonic() - started
            measurement = score(manifest, reviews, registrar)

        self.assertLess(elapsed, 5)
        self.assertEqual(reviews["status"], "stopped")
        self.assertEqual(reviews["stop_reason"], "timeout")
        attempt = reviews["attempts"][0]
        attestation = json.loads(registrar.resolve(attempt["attestation_ref"]))
        capture = json.loads(registrar.resolve(attestation["capture_ref"]))
        self.assertEqual(capture["termination"], "timeout")
        self.assertGreater(capture["stdin_ref"]["byte_count"], 1024 * 1024)
        self.assertEqual(measurement["disposition"], "infrastructure-failure")

    def test_output_limit_retains_registered_prefix_and_stops(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable, mode="stdout-limit")
            manifest = prepare_executable_manifest(registrar, executable)
            authorization_ref = make_execution_authorization(
                registrar,
                manifest,
                limits_override={"max_stdout_bytes_per_process": 64},
            )

            reviews = execute(manifest, authorization_ref, registrar)
            measurement = score(manifest, reviews, registrar)

        self.assertEqual(reviews["status"], "stopped")
        self.assertEqual(reviews["stop_reason"], "stdout-limit")
        attempt = reviews["attempts"][0]
        attestation = json.loads(registrar.resolve(attempt["attestation_ref"]))
        capture = json.loads(registrar.resolve(attestation["capture_ref"]))
        self.assertEqual(capture["termination"], "stdout-limit")
        self.assertFalse(capture["stdout_complete"])
        self.assertEqual(capture["stdout_ref"]["byte_count"], 64)
        self.assertEqual(len(registrar.resolve(capture["stdout_ref"])), 64)
        self.assertEqual(measurement["disposition"], "infrastructure-failure")

    def test_invalid_subject_response_is_sealed_and_execution_continues(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable, mode="invalid")
            manifest = prepare_executable_manifest(registrar, executable)
            authorization_ref = make_execution_authorization(registrar, manifest)

            reviews = execute(manifest, authorization_ref, registrar)
            measurement = score(manifest, reviews, registrar)

        self.assertEqual(reviews["status"], "complete")
        self.assertEqual(len(reviews["attempts"]), 4)
        self.assertTrue(
            all(
                attempt["disposition"] == "subject-failure"
                and attempt["verdict"] == "invalid"
                for attempt in reviews["attempts"]
            )
        )
        self.assertEqual(measurement["disposition"], "incomplete")
        self.assertEqual(measurement["sample_flow"]["subject_failures"], 4)

    def test_execute_refuses_expired_authority_before_spawning(self):
        registrar = MemoryRegistrar()
        with tempfile.TemporaryDirectory() as temporary:
            executable = Path(temporary) / "fake-native"
            write_fake_native(executable)
            manifest = prepare_executable_manifest(registrar, executable)
            authorization_ref = make_execution_authorization(
                registrar,
                manifest,
                valid_from="2025-01-01T00:00:00Z",
                valid_until="2025-01-02T00:00:00Z",
            )

            with self.assertRaisesRegex(
                RevbenchContractError, "outside the execution authorization"
            ):
                execute(manifest, authorization_ref, registrar)

    def test_stopped_execution_before_first_attempt_scores_as_incomplete(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        reviews = make_reviews(registrar, manifest)
        reviews["attempts"] = []
        reviews["status"] = "stopped"
        reviews["stop_reason"] = "authorization-expired"
        reseal_execution(reviews)

        measurement = score(manifest, reviews, registrar)

        self.assertEqual(measurement["disposition"], "incomplete")
        self.assertEqual(
            measurement["sample_flow"],
            {
                "planned": 4,
                "attempted": 0,
                "usable": 0,
                "excluded": 0,
                "missing": 4,
                "subject_failures": 0,
                "infrastructure_failures": 0,
            },
        )
        self.assertEqual(measurement["evidence"]["run_refs"], [])
        self.assertEqual(validate_measurement(measurement, registrar), measurement)

    def test_score_derives_exact_paired_metrics_and_lineage(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        outcomes = {
            ("case-b", "control"): ("complete", "defect", ["/limits/minimum"]),
            ("case-b", "mutant"): ("complete", "defect", ["/wrong"]),
        }
        reviews = make_reviews(registrar, manifest, outcomes)

        measurement = score(manifest, reviews, registrar)
        repeated = score(manifest, copy.deepcopy(reviews), registrar)

        self.assertEqual(measurement, repeated)
        self.assertEqual(measurement["schema_version"], "caplab-measurement/1")
        self.assertEqual(measurement["disposition"], "complete")
        self.assertEqual(
            measurement["sample_flow"],
            {
                "planned": 4,
                "attempted": 4,
                "usable": 4,
                "excluded": 0,
                "missing": 0,
                "subject_failures": 0,
                "infrastructure_failures": 0,
            },
        )
        values = {
            name: metric["value"] for name, metric in measurement["metrics"].items()
        }
        self.assertEqual(values["catch_rate"], {"numerator": 1, "denominator": 2})
        self.assertEqual(values["false_alarm_rate"], {"numerator": 1, "denominator": 2})
        self.assertEqual(values["discrimination"], {"numerator": 0, "denominator": 1})
        self.assertEqual(values["anchor_hit_rate"], {"numerator": 1, "denominator": 2})
        self.assertEqual(values["conformance_rate"], {"numerator": 1, "denominator": 1})
        self.assertEqual(validate_measurement(measurement, registrar), measurement)
        self.assertEqual(
            (
                measurement["provenance"]["caplab_version"],
                measurement["provenance"]["caplab_commit"],
                measurement["provenance"]["caplab_package_sha256"],
            ),
            producer_identity(),
        )
        self.assertEqual(
            {basis["role"] for basis in measurement["evidence_basis"]},
            {"truth", "case-selection", "metric-derivation"},
        )
        all_basis_ids = sorted(
            basis["basis_id"] for basis in measurement["evidence_basis"]
        )
        for metric in measurement["metrics"].values():
            self.assertEqual(metric["basis_ids"], all_basis_ids)
            self.assertEqual(
                metric["case_selection_ref"], manifest["case_selection_ref"]
            )
        self.assertEqual(len(measurement["evidence"]["run_refs"]), 4)

    def test_generic_refusal_and_wrong_anchor_receive_no_catch_credit(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        reviews = make_reviews(
            registrar,
            manifest,
            {
                ("case-a", "mutant"): ("subject-failure", "invalid", []),
                ("case-b", "mutant"): ("complete", "defect", ["/not-the-defect"]),
            },
        )

        measurement = score(manifest, reviews, registrar)

        self.assertEqual(
            measurement["metrics"]["catch_rate"]["value"],
            {"numerator": 0, "denominator": 1},
        )
        self.assertEqual(
            measurement["metrics"]["conformance_rate"]["value"],
            {"numerator": 3, "denominator": 4},
        )

    def test_missing_or_invalid_arm_excludes_the_pair_without_improving_scores(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        reviews = make_reviews(registrar, manifest)
        reviews["attempts"] = [
            attempt
            for attempt in reviews["attempts"]
            if not (attempt["case_id"] == "case-b" and attempt["arm"] == "mutant")
        ]
        reviews["status"] = "stopped"
        reviews["stop_reason"] = "authorization-expired"
        reseal_execution(reviews)

        measurement = score(manifest, reviews, registrar)

        self.assertEqual(measurement["sample_flow"]["missing"], 1)
        self.assertEqual(measurement["sample_flow"]["excluded"], 1)
        self.assertEqual(measurement["sample_flow"]["usable"], 2)
        self.assertEqual(
            measurement["metrics"]["catch_rate"]["value"],
            {"numerator": 1, "denominator": 1},
        )

        reviews = make_reviews(
            registrar,
            manifest,
            {("case-b", "mutant"): ("subject-failure", "invalid", [])},
        )
        invalid = score(manifest, reviews, registrar)
        self.assertEqual(invalid["disposition"], "incomplete")
        self.assertEqual(invalid["sample_flow"]["subject_failures"], 1)
        self.assertEqual(invalid["sample_flow"]["excluded"], 1)
        self.assertEqual(invalid["sample_flow"]["usable"], 2)

        reviews = make_reviews(
            registrar,
            manifest,
            {("case-b", "mutant"): ("infrastructure-failure", "invalid", [])},
        )
        failed = score(manifest, reviews, registrar)
        self.assertEqual(failed["disposition"], "infrastructure-failure")
        self.assertEqual(failed["sample_flow"]["infrastructure_failures"], 1)
        self.assertEqual(failed["sample_flow"]["excluded"], 1)

    def test_duplicate_attempt_and_stale_observed_binding_are_refused(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        reviews = make_reviews(registrar, manifest)
        reviews["attempts"].append(copy.deepcopy(reviews["attempts"][0]))
        with self.assertRaisesRegex(RevbenchContractError, "duplicate"):
            score(manifest, reviews, registrar)

        reviews = make_reviews(registrar, manifest)
        attempt = reviews["attempts"][0]
        attempt["observed_binding"]["reasoning_effort"] = "low"
        identity = copy.deepcopy(attempt["observed_binding"])
        identity.pop("binding_id")
        attempt["observed_binding"]["binding_id"] = "bnd-" + sha256_hex(
            canonical_json(identity)
        )
        with self.assertRaisesRegex(RevbenchContractError, "manifest Binding"):
            score(manifest, reviews, registrar)

    def test_each_observed_binding_dimension_is_exact(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        replacement_ref = registered(registrar, "replacement-configuration")
        changes = {
            "provider": lambda binding: binding["provider_or_path"].__setitem__(
                "identifier", "other-provider"
            ),
            "harness": lambda binding: binding["harness"].__setitem__(
                "harness_id", "other-harness"
            ),
            "effort": lambda binding: binding.__setitem__("reasoning_effort", "low"),
            "configuration": lambda binding: binding["configuration"].__setitem__(
                "instructions_ref", replacement_ref
            ),
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                reviews = make_reviews(registrar, manifest)
                observed = reviews["attempts"][0]["observed_binding"]
                change(observed)
                identity = copy.deepcopy(observed)
                identity.pop("binding_id")
                observed["binding_id"] = "bnd-" + sha256_hex(canonical_json(identity))
                with self.assertRaisesRegex(RevbenchContractError, "manifest Binding"):
                    score(manifest, reviews, registrar)

    def test_attested_binding_and_registered_attempt_bytes_are_verified(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        reviews = make_reviews(registrar, manifest)
        attempt = reviews["attempts"][0]
        attested = json.loads(registrar.resolve(attempt["attestation_ref"]))
        attested["observed_binding"]["provider_or_path"]["identifier"] = (
            "wrong-provider"
        )
        binding_identity = copy.deepcopy(attested["observed_binding"])
        binding_identity.pop("binding_id")
        attested["observed_binding"]["binding_id"] = "bnd-" + sha256_hex(
            canonical_json(binding_identity)
        )
        attestation_identity = copy.deepcopy(attested)
        attestation_identity.pop("attestation_id")
        attested["attestation_id"] = "attestation-" + sha256_hex(
            canonical_json(attestation_identity)
        )
        wrong_ref = registered(
            registrar,
            "wrong-attestation",
            attested,
            kind="native-attempt-attestation",
            schema="caplab-native-attempt-attestation/1",
        )
        attempt["attestation_ref"] = wrong_ref
        reseal_attempt_envelope(registrar, attempt)
        with self.assertRaisesRegex(
            RevbenchContractError, "attestation_ref.*observed_binding"
        ):
            score(manifest, reviews, registrar)

        reviews = make_reviews(registrar, manifest)
        attempt = reviews["attempts"][0]
        registrar.documents[attempt["attempt_ref"]["sha256"]] = b"broken"
        with self.assertRaisesRegex(RevbenchContractError, "byte count|SHA-256"):
            score(manifest, reviews, registrar)

    def test_cross_attempt_reference_swaps_are_refused(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        reviews = make_reviews(registrar, manifest)
        first, second = reviews["attempts"][:2]
        first["prompt_ref"], second["prompt_ref"] = (
            second["prompt_ref"],
            first["prompt_ref"],
        )

        with self.assertRaisesRegex(RevbenchContractError, "envelope projection"):
            score(manifest, reviews, registrar)

    def test_assignment_order_is_part_of_each_registered_attempt(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        reviews = make_reviews(registrar, manifest)
        attempt = reviews["attempts"][0]
        attempt["assignment_index"] = 1 - attempt["assignment_index"]
        reseal_attempt_envelope(registrar, attempt)

        with self.assertRaisesRegex(RevbenchContractError, "assignment order"):
            score(manifest, reviews, registrar)

    def test_resealed_control_bytes_cannot_receive_mutant_credit(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        reviews = make_reviews(registrar, manifest)
        case = manifest["cases"][0]
        mutant = next(
            attempt
            for attempt in reviews["attempts"]
            if attempt["case_id"] == case["case_id"] and attempt["arm"] == "mutant"
        )
        assignment_index = mutant["assignment_index"]
        prompt_ref = registered(
            registrar,
            "forged-mutant-prompt",
            {
                "schema_version": "caplab-revbench-prompt/1",
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": "mutant",
                "assignment_index": assignment_index,
                "binding_id": manifest["binding"]["binding_id"],
                "artifact": case["control"]["content"],
            },
            kind="prompt",
            schema="caplab-revbench-prompt/1",
        )
        output_ref = registered(
            registrar,
            "forged-mutant-output",
            {
                "schema_version": "caplab-native-output/1",
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": "mutant",
                "assignment_index": assignment_index,
                "binding_id": manifest["binding"]["binding_id"],
                "verdict": "clean",
                "anchors": [],
            },
            kind="native-output",
            schema="caplab-native-output/1",
        )
        old_attestation = json.loads(registrar.resolve(mutant["attestation_ref"]))
        old_capture = json.loads(registrar.resolve(old_attestation["capture_ref"]))
        old_capture["prompt_ref"] = prompt_ref
        old_capture["output_ref"] = output_ref
        old_capture["capture_id"] = derive_content_id(
            old_capture, "capture_id", "capture-"
        )
        capture_ref = registered(
            registrar,
            "forged-mutant-capture",
            old_capture,
            kind="native-attempt-capture",
            schema="caplab-native-attempt-capture/1",
        )
        old_attestation["capture_ref"] = capture_ref
        old_attestation["prompt_ref"] = prompt_ref
        old_attestation["output_ref"] = output_ref
        old_attestation["attestation_id"] = derive_content_id(
            old_attestation, "attestation_id", "attestation-"
        )
        attestation_ref = registered(
            registrar,
            "forged-mutant-attestation",
            old_attestation,
            kind="native-attempt-attestation",
            schema="caplab-native-attempt-attestation/1",
        )
        mutant.update(
            {
                "prompt_ref": prompt_ref,
                "output_ref": output_ref,
                "attestation_ref": attestation_ref,
                "verdict": "clean",
                "anchors": [],
            }
        )
        reseal_attempt_envelope(registrar, mutant)

        with self.assertRaisesRegex(RevbenchContractError, "prompt_ref"):
            score(manifest, reviews, registrar)

    def test_anchor_hit_rate_is_absent_without_mutant_defect_calls(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        outcomes = {
            (case["case_id"], "mutant"): ("complete", "clean", [])
            for case in manifest["cases"]
        }

        measurement = score(
            manifest, make_reviews(registrar, manifest, outcomes), registrar
        )

        self.assertNotIn("anchor_hit_rate", measurement["metrics"])

    def test_revbench_is_fate_blind(self):
        registrar = MemoryRegistrar()
        spec = make_spec(registrar)
        manifest = prepare(spec, registrar)
        measurement = score(manifest, make_reviews(registrar, manifest), registrar)

        self.assertEqual(measurement["covariates"], [])
        contaminated = copy.deepcopy(spec)
        contaminated["downstream_fate"] = "final"
        with self.assertRaisesRegex(RevbenchContractError, "unknown field"):
            prepare(contaminated, registrar)

    def test_unknown_review_fields_and_manifest_protocol_tampering_are_refused(self):
        registrar = MemoryRegistrar()
        manifest = prepare(make_spec(registrar), registrar)
        reviews = make_reviews(registrar, manifest)
        reviews["attempts"][0]["unexpected"] = True
        with self.assertRaisesRegex(RevbenchContractError, "unknown field"):
            score(manifest, reviews, registrar)

        manifest = copy.deepcopy(manifest)
        manifest["protocol"] = registered(registrar, "other-protocol", kind="protocol")
        with self.assertRaisesRegex(
            RevbenchContractError, "protocol_ref|experiment_id"
        ):
            score(manifest, make_reviews(registrar, manifest), registrar)

        manifest = prepare(make_spec(registrar), registrar)
        manifest["cases"][0]["mutant"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(RevbenchContractError, "recomputed|manifest"):
            score(manifest, make_reviews(registrar, manifest), registrar)

    def test_authorizations_are_exactly_scoped_and_valid_at_observation_time(self):
        registrar = MemoryRegistrar()
        spec = make_spec(registrar)
        original_ref = spec["basis_authorization_refs"]["truth"]
        authorization = json.loads(registrar.resolve(original_ref))
        authorization["basis_role"] = "case-selection"
        identity = copy.deepcopy(authorization)
        identity.pop("authorization_id")
        authorization["authorization_id"] = "basis-auth-" + sha256_hex(
            canonical_json(identity)
        )
        spec["basis_authorization_refs"]["truth"] = registered(
            registrar,
            "wrong-role-authorization",
            authorization,
            kind="evidence-basis-authorization",
            schema="caplab-evidence-basis-authorization/1",
        )
        with self.assertRaisesRegex(RevbenchContractError, "basis_role"):
            prepare(spec, registrar)

        spec = make_spec(registrar)
        original_ref = spec["basis_authorization_refs"]["truth"]
        authorization = json.loads(registrar.resolve(original_ref))
        authorization["valid_until"] = "2026-02-01T00:00:00Z"
        authorization_scope = {
            key: authorization[key]
            for key in (
                "binding_ids",
                "capability",
                "experiment",
                "protocol_ref",
                "corpus_ref",
                "case_selection_ref",
                "method_ref",
                "basis_kind",
                "basis_role",
            )
        }
        authorization["authority_source_ref"] = make_delegation(
            registrar,
            effect="evidence-basis",
            authorized_by=authorization["authorized_by"],
            delegate_or_mechanism=authorization["delegate_or_mechanism"],
            scope=authorization_scope,
            valid_from=authorization["valid_from"],
            valid_until=authorization["valid_until"],
        )
        identity = copy.deepcopy(authorization)
        identity.pop("authorization_id")
        authorization["authorization_id"] = "basis-auth-" + sha256_hex(
            canonical_json(identity)
        )
        spec["basis_authorization_refs"]["truth"] = registered(
            registrar,
            "expired-authorization",
            authorization,
            kind="evidence-basis-authorization",
            schema="caplab-evidence-basis-authorization/1",
        )
        manifest = prepare(spec, registrar)
        with self.assertRaisesRegex(RevbenchContractError, "observation time"):
            score(manifest, make_reviews(registrar, manifest), registrar)

    def test_fate_conditioned_case_selection_is_refused(self):
        registrar = MemoryRegistrar()
        spec = make_spec(registrar)
        selection = json.loads(registrar.resolve(spec["case_selection_ref"]))
        selection["conditioned_on"] = ["downstream_fate"]
        identity = copy.deepcopy(selection)
        identity.pop("selection_id")
        selection["selection_id"] = "selection-" + sha256_hex(canonical_json(identity))
        spec["case_selection_ref"] = registered(
            registrar,
            "fate-conditioned-selection",
            selection,
            kind="case-selection",
            schema="caplab-case-selection-manifest/1",
        )
        with self.assertRaisesRegex(RevbenchContractError, "conditioned_on"):
            prepare(spec, registrar)


class CliTests(unittest.TestCase):
    def test_module_cli_prepares_and_runs_with_canonical_files(self):
        source_root = str(Path(__file__).resolve().parents[1] / "src")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger_root = root / "ledger"
            registrar = LedgerRegistrar(ledger_root)
            spec = make_spec(registrar)
            spec_path = root / "spec.json"
            manifest_path = root / "manifest.json"
            spec_path.write_bytes(canonical_json(spec))
            environment = dict(os.environ, PYTHONPATH=source_root)
            prepared = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caplab.revbench",
                    "prepare",
                    "--spec",
                    str(spec_path),
                    "--ledger",
                    str(ledger_root),
                    "--output",
                    str(manifest_path),
                ],
                cwd=root,
                env=environment,
                check=False,
                capture_output=True,
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr.decode())
            self.assertEqual(prepared.stdout, manifest_path.read_bytes())
            frozen_manifest_bytes = manifest_path.read_bytes()
            replay = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caplab.revbench",
                    "prepare",
                    "--spec",
                    str(spec_path),
                    "--ledger",
                    str(ledger_root),
                    "--output",
                    str(manifest_path),
                ],
                cwd=root,
                env=environment,
                check=False,
                capture_output=True,
            )
            self.assertEqual(replay.returncode, 2)
            self.assertEqual(manifest_path.read_bytes(), frozen_manifest_bytes)
            manifest = json.loads(manifest_path.read_bytes())

            reviews = make_reviews(registrar, manifest)
            reviews_path = root / "reviews.json"
            measurement_path = root / "measurement.json"
            reviews_path.write_bytes(canonical_json(reviews))
            scored = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caplab.revbench",
                    "score",
                    "--manifest",
                    str(manifest_path),
                    "--reviews",
                    str(reviews_path),
                    "--ledger",
                    str(ledger_root),
                    "--output",
                    str(measurement_path),
                ],
                cwd=root,
                env=environment,
                check=False,
                capture_output=True,
            )
            self.assertEqual(scored.returncode, 0, scored.stderr.decode())
            self.assertEqual(scored.stdout, measurement_path.read_bytes())
            measurement = json.loads(measurement_path.read_bytes())
            self.assertEqual(measurement["schema_version"], "caplab-measurement/1")

    def test_module_cli_refuses_object_bytes_without_registration_records(self):
        registrar = MemoryRegistrar()
        spec = make_spec(registrar)
        source_root = str(Path(__file__).resolve().parents[1] / "src")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger_root = root / "ledger"
            ledger_root.mkdir()
            for digest, data in registrar.documents.items():
                target = ledger_root / f"objects/sha256/{digest[:2]}/{digest}"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            spec_path = root / "spec.json"
            output_path = root / "manifest.json"
            spec_path.write_bytes(canonical_json(spec))

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caplab.revbench",
                    "prepare",
                    "--spec",
                    str(spec_path),
                    "--ledger",
                    str(ledger_root),
                    "--output",
                    str(output_path),
                ],
                cwd=root,
                env=dict(os.environ, PYTHONPATH=source_root),
                check=False,
                capture_output=True,
            )

            self.assertEqual(completed.returncode, 2)
            self.assertFalse(output_path.exists())
            error = json.loads(completed.stderr)
            self.assertIn("registered reference", error["message"])

    def test_module_cli_returns_two_and_canonical_error_on_expected_refusal(self):
        source_root = str(Path(__file__).resolve().parents[1] / "src")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger_root = root / "ledger"
            spec_path = root / "spec.json"
            output_path = root / "manifest.json"
            spec_path.write_bytes(canonical_json({"schema_version": "wrong"}))
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caplab.revbench",
                    "prepare",
                    "--spec",
                    str(spec_path),
                    "--ledger",
                    str(ledger_root),
                    "--output",
                    str(output_path),
                ],
                cwd=root,
                env=dict(os.environ, PYTHONPATH=source_root),
                check=False,
                capture_output=True,
            )

            self.assertEqual(completed.returncode, 2)
            self.assertEqual(completed.stdout, b"")
            self.assertFalse(output_path.exists())
            error = json.loads(completed.stderr)
            self.assertEqual(error["schema_version"], "caplab-revbench-error/1")
            self.assertEqual(completed.stderr, canonical_json(error) + b"\n")

    def test_module_cli_argument_refusal_is_canonical(self):
        source_root = str(Path(__file__).resolve().parents[1] / "src")
        completed = subprocess.run(
            [sys.executable, "-m", "caplab.revbench", "prepare"],
            env=dict(os.environ, PYTHONPATH=source_root),
            check=False,
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, b"")
        error = json.loads(completed.stderr)
        self.assertEqual(error["schema_version"], "caplab-revbench-error/1")
        self.assertEqual(completed.stderr, canonical_json(error) + b"\n")

    def test_module_cli_refuses_symlinked_ledger_root(self):
        source_root = str(Path(__file__).resolve().parents[1] / "src")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real_ledger = root / "real-ledger"
            registrar = LedgerRegistrar(real_ledger)
            spec = make_spec(registrar)
            spec_path = root / "spec.json"
            spec_path.write_bytes(canonical_json(spec))
            linked_ledger = root / "ledger-link"
            linked_ledger.symlink_to(real_ledger, target_is_directory=True)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "caplab.revbench",
                    "prepare",
                    "--spec",
                    str(spec_path),
                    "--ledger",
                    str(linked_ledger),
                    "--output",
                    str(root / "manifest.json"),
                ],
                cwd=root,
                env=dict(os.environ, PYTHONPATH=source_root),
                check=False,
                capture_output=True,
            )

            self.assertEqual(completed.returncode, 2)
            self.assertIn("ledger_root_not_real_directory", completed.stderr.decode())


if __name__ == "__main__":
    unittest.main()
