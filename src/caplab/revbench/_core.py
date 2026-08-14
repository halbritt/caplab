"""Strict, offline revbench preparation and scoring.

The public functions in this module consume untrusted JSON-shaped values.  Type
annotations document the internal contract; every value-level invariant is
also checked at runtime before evidence can affect a result.
"""

from __future__ import annotations

import copy
import json
import math
import os
import re
import stat
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from caplab.producer import ProducerIdentityError, producer_identity
from caplab.qualification import (
    QualificationContractError,
)
from caplab.qualification import (
    validate_binding as validate_qualification_binding,
)
from caplab.qualification import (
    validate_measurement as validate_qualification_measurement,
)
from caplab.runtime.canonical import CanonicalizationError, canonical_json, sha256_hex
from caplab.subject_identity import (
    CANONICAL_NATIVE_AGENT_SYSTEM_POLICY_SHA256,
    NativeAgentSystemContractError,
    validate_native_agent_systems,
)

type JsonValue = None | bool | int | str | list[JsonValue] | dict[str, JsonValue]
type ContentRef = dict[str, JsonValue]


class RevbenchContractError(ValueError):
    """The supplied revbench artifact or registered evidence is invalid."""


@runtime_checkable
class ArtifactRegistrar(Protocol):
    """The content-addressed registration seam required by revbench."""

    def register_document(
        self,
        document: JsonValue,
        *,
        kind: str,
        schema: str,
        registration_id: str,
    ) -> ContentRef: ...

    def resolve(self, ref: Mapping[str, Any]) -> bytes: ...


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_BINDING_ID = re.compile(r"^bnd-[0-9a-f]{64}$")
_CASE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_EXPERIMENT_ID = _CASE_ID
_UTC_TIMESTAMP = re.compile(
    r"^[0-9]{4}-(0[1-9]|1[0-2])-([0-2][0-9]|3[01])T"
    r"([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]Z$"
)
_POINTER = re.compile(r"^(?:/(?:[^~/]|~[01])*)*$")
_REGISTRATION_REF = re.compile(r"^[a-z][a-z0-9-]{2,127}:[A-Za-z0-9._:-]{1,255}$")
_CAPABILITY_NAME = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_NATIVE_INPUT_INSTRUCTION = (
    "Review the artifact against the requirement and return exactly one JSON object."
)
_LOCAL_FIXTURE_PROFILE = {
    "provider_identifier": "caplab-local-fixture",
    "revision": "revbench-static-fixture-v1",
    "model_id": "caplab/revbench-static-fixture",
    "harness_id": "caplab-revbench-static-fixture",
    "harness_version": "fake-native 1",
    "effort": "fixed",
    "tuple_id": "caplab-revbench-static-fixture-fixed",
}
_LOCAL_FIXTURE_POLICY = "caplab-revbench-local-fixture-v1"
_LOCAL_FIXTURE_AUTHORITY = "adr-0062"
_LOCAL_FIXTURE_SOURCE = {"contract": "caplab-revbench-local-fixture/1"}
_LOCAL_FIXTURE_VERSION_STDOUT_SHA256 = (
    "6f5f9aa1f1b2abab63257536c3a55dc13fa1a04a4d4dcf19d68cbe68934318c7"
)
_LOCAL_FIXTURE_VERSION_STDERR_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
_REQUIRED_PROXY_MARKERS = ["openrouter", "harbor", "terminus"]
_CUSTODY_PATH = re.compile(
    r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))(?!.*(?:^|/)\.(?:/|$))[A-Za-z0-9._/-]+$"
)

_CONTENT_REF_FIELDS = {
    "kind",
    "schema",
    "media_type",
    "sha256",
    "byte_count",
    "locator",
    "registration_ref",
    "custody",
}


def _fail(path: str, message: str) -> None:
    raise RevbenchContractError(f"{path}: {message}")


def _object(value: Any, path: str, fields: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(path, "must be an object")
    if any(not isinstance(key, str) for key in value):
        _fail(path, "object keys must be strings")
    actual = set(value)
    missing = sorted(fields - actual)
    if missing:
        _fail(path, f"missing field {missing[0]!r}")
    unknown = sorted(actual - fields)
    if unknown:
        _fail(path, f"unknown field {unknown[0]!r}")
    return value


def _string(value: Any, path: str, *, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value:
        _fail(path, "must be a non-empty string")
    if pattern is not None and pattern.fullmatch(value) is None:
        _fail(path, "has an invalid format")
    return value


def _integer(value: Any, path: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(path, "must be an integer")
    if minimum is not None and value < minimum:
        _fail(path, f"must be at least {minimum}")
    return value


def _array(value: Any, path: str, *, minimum: int = 0) -> list[Any]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    if len(value) < minimum:
        _fail(path, f"must contain at least {minimum} item(s)")
    return value


def _const(value: Any, expected: Any, path: str) -> None:
    if value != expected or type(value) is not type(expected):
        _fail(path, f"must equal {expected!r}")


def _sorted_unique(values: Sequence[Any], path: str) -> None:
    try:
        encoded = [canonical_json(value) for value in values]
    except CanonicalizationError as error:
        _fail(path, str(error))
    if len(set(encoded)) != len(encoded):
        _fail(path, "must not contain duplicates")
    if encoded != sorted(encoded):
        _fail(path, "must be in canonical sorted order")


def _validate_content_ref(
    value: Any,
    path: str,
    *,
    kind: str | None = None,
    schema: str | None = None,
) -> Mapping[str, Any]:
    ref = _object(value, path, _CONTENT_REF_FIELDS)
    _string(ref["kind"], f"{path}.kind")
    _string(ref["schema"], f"{path}.schema")
    _string(ref["media_type"], f"{path}.media_type")
    digest = _string(ref["sha256"], f"{path}.sha256", pattern=_SHA256)
    _integer(ref["byte_count"], f"{path}.byte_count", minimum=0)
    _const(ref["locator"], f"objects/sha256/{digest[:2]}/{digest}", f"{path}.locator")
    _string(
        ref["registration_ref"], f"{path}.registration_ref", pattern=_REGISTRATION_REF
    )
    if kind is not None:
        _const(ref["kind"], kind, f"{path}.kind")
    if schema is not None:
        _const(ref["schema"], schema, f"{path}.schema")
    custody = ref["custody"]
    if custody is not None:
        custody = _object(
            custody,
            f"{path}.custody",
            {"repository", "commit", "path", "source_sha256"},
        )
        _string(custody["repository"], f"{path}.custody.repository")
        _string(custody["commit"], f"{path}.custody.commit", pattern=_COMMIT)
        _string(custody["path"], f"{path}.custody.path", pattern=_CUSTODY_PATH)
        _string(
            custody["source_sha256"], f"{path}.custody.source_sha256", pattern=_SHA256
        )
    return ref


def _resolve_ref(
    ref: Mapping[str, Any], registrar: ArtifactRegistrar, path: str
) -> bytes:
    _validate_content_ref(ref, path)
    try:
        data = registrar.resolve(ref)
    except Exception as error:
        raise RevbenchContractError(
            f"{path}: registered reference could not be resolved"
        ) from error
    if not isinstance(data, bytes):
        _fail(path, "registrar.resolve() must return bytes")
    if len(data) != ref["byte_count"]:
        _fail(path, "resolved byte count does not match reference")
    if sha256_hex(data) != ref["sha256"]:
        _fail(path, "resolved SHA-256 does not match reference")
    return data


def _resolve_all_refs(
    value: Any, registrar: ArtifactRegistrar, path: str = "document"
) -> None:
    if isinstance(value, Mapping):
        if set(value) == _CONTENT_REF_FIELDS:
            _resolve_ref(value, registrar, path)
            return
        for key, child in value.items():
            _resolve_all_refs(child, registrar, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _resolve_all_refs(child, registrar, f"{path}[{index}]")


def _validate_binding(value: Any, path: str = "binding") -> Mapping[str, Any]:
    binding = _object(
        value,
        path,
        {
            "schema_version",
            "binding_id",
            "model",
            "provider_or_path",
            "harness",
            "reasoning_effort",
            "configuration",
        },
    )
    _const(binding["schema_version"], "caplab-binding/1", f"{path}.schema_version")
    _string(binding["binding_id"], f"{path}.binding_id", pattern=_BINDING_ID)
    model = _object(
        binding["model"],
        f"{path}.model",
        {"model_id", "revision", "weights_ref", "weights_unavailable_reason"},
    )
    _string(model["model_id"], f"{path}.model.model_id")
    _string(model["revision"], f"{path}.model.revision")
    if model["weights_ref"] is None:
        _string(
            model["weights_unavailable_reason"],
            f"{path}.model.weights_unavailable_reason",
        )
    else:
        _validate_content_ref(model["weights_ref"], f"{path}.model.weights_ref")
        if model["weights_unavailable_reason"] is not None:
            _fail(
                f"{path}.model.weights_unavailable_reason",
                "must be null when weights_ref is present",
            )

    provider = _object(
        binding["provider_or_path"],
        f"{path}.provider_or_path",
        {"kind", "identifier", "revision", "resolution", "observed_at", "route_ref"},
    )
    if provider["kind"] not in {
        "direct-provider",
        "proxy-provider",
        "local-serving",
        "other",
    }:
        _fail(f"{path}.provider_or_path.kind", "is unsupported")
    _string(provider["identifier"], f"{path}.provider_or_path.identifier")
    _string(provider["revision"], f"{path}.provider_or_path.revision")
    if provider["resolution"] not in {"immutable", "observed-route"}:
        _fail(f"{path}.provider_or_path.resolution", "is unsupported")
    if provider["resolution"] == "immutable":
        if provider["observed_at"] is not None:
            _fail(
                f"{path}.provider_or_path.observed_at",
                "must be null for immutable resolution",
            )
    else:
        _string(
            provider["observed_at"],
            f"{path}.provider_or_path.observed_at",
            pattern=_UTC_TIMESTAMP,
        )
    _validate_content_ref(provider["route_ref"], f"{path}.provider_or_path.route_ref")

    harness = _object(
        binding["harness"],
        f"{path}.harness",
        {
            "harness_id",
            "harness_version",
            "executable_ref",
            "executable_unavailable_reason",
            "command_ref",
            "version_probe_ref",
        },
    )
    _string(harness["harness_id"], f"{path}.harness.harness_id")
    _string(harness["harness_version"], f"{path}.harness.harness_version")
    if harness["executable_ref"] is None:
        _string(
            harness["executable_unavailable_reason"],
            f"{path}.harness.executable_unavailable_reason",
        )
    else:
        _validate_content_ref(
            harness["executable_ref"], f"{path}.harness.executable_ref"
        )
        if harness["executable_unavailable_reason"] is not None:
            _fail(
                f"{path}.harness.executable_unavailable_reason",
                "must be null when executable_ref is present",
            )
    _validate_content_ref(harness["command_ref"], f"{path}.harness.command_ref")
    _validate_content_ref(
        harness["version_probe_ref"], f"{path}.harness.version_probe_ref"
    )
    _string(binding["reasoning_effort"], f"{path}.reasoning_effort")
    configuration = _object(
        binding["configuration"],
        f"{path}.configuration",
        {
            "inference_ref",
            "instructions_ref",
            "knowledge_ref",
            "tools_ref",
            "permissions_ref",
            "sandbox_ref",
            "runtime_ref",
        },
    )
    for name, ref in configuration.items():
        _validate_content_ref(ref, f"{path}.configuration.{name}")

    identity = copy.deepcopy(dict(binding))
    identity.pop("binding_id")
    try:
        expected = "bnd-" + sha256_hex(canonical_json(identity))
    except CanonicalizationError as error:
        _fail(path, str(error))
    if binding["binding_id"] != expected:
        _fail(f"{path}.binding_id", "does not match the complete Binding")
    return binding


def _validate_capability(value: Any, path: str = "capability") -> Mapping[str, Any]:
    capability = _object(
        value,
        path,
        {"name", "version", "role", "domain", "distribution", "card_ref"},
    )
    _string(capability["name"], f"{path}.name", pattern=_CAPABILITY_NAME)
    for name in ("version", "role", "domain"):
        _string(capability[name], f"{path}.{name}")
    _const(capability["distribution"], "json-integer-minimum/1", f"{path}.distribution")
    _validate_content_ref(
        capability["card_ref"], f"{path}.card_ref", kind="capability-card"
    )
    return capability


def _validate_provenance(value: Any, path: str = "provenance") -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(path, "must be an object")
    fields = set(value)
    base = {"caplab_version", "caplab_commit", "source_refs"}
    if fields not in {frozenset(base), frozenset(base | {"caplab_package_sha256"})}:
        _fail(
            path,
            "must contain only version, commit, optional package digest, and source refs",
        )
    provenance = value
    _string(provenance["caplab_version"], f"{path}.caplab_version")
    _string(provenance["caplab_commit"], f"{path}.caplab_commit", pattern=_COMMIT)
    if "caplab_package_sha256" in provenance:
        _string(
            provenance["caplab_package_sha256"],
            f"{path}.caplab_package_sha256",
            pattern=_SHA256,
        )
    refs = _array(provenance["source_refs"], f"{path}.source_refs")
    for index, ref in enumerate(refs):
        _validate_content_ref(ref, f"{path}.source_refs[{index}]")
    _sorted_unique(refs, f"{path}.source_refs")
    return provenance


def _pointer(value: Any, path: str) -> str:
    return _string(value, path, pattern=_POINTER)


def _pointer_tokens(pointer: str) -> list[str]:
    if pointer == "":
        return []
    return [
        token.replace("~1", "/").replace("~0", "~") for token in pointer[1:].split("/")
    ]


def _at_pointer(document: JsonValue, pointer: str, path: str) -> JsonValue:
    current: JsonValue = document
    for token in _pointer_tokens(pointer):
        if isinstance(current, dict):
            if token not in current:
                _fail(path, f"JSON Pointer {pointer!r} does not exist")
            current = current[token]
        elif isinstance(current, list):
            if (
                token == "-"
                or not token.isdigit()
                or (len(token) > 1 and token.startswith("0"))
            ):
                _fail(path, f"JSON Pointer {pointer!r} has an invalid array index")
            index = int(token)
            if index >= len(current):
                _fail(path, f"JSON Pointer {pointer!r} is out of bounds")
            current = current[index]
        else:
            _fail(path, f"JSON Pointer {pointer!r} traverses a scalar")
    return current


def _replace_pointer(
    document: JsonValue, pointer: str, replacement: int, path: str
) -> JsonValue:
    result: JsonValue = json.loads(canonical_json(document))
    tokens = _pointer_tokens(pointer)
    if not tokens:
        return replacement
    parent_pointer = (
        ""
        if len(tokens) == 1
        else "/"
        + "/".join(token.replace("~", "~0").replace("/", "~1") for token in tokens[:-1])
    )
    parent = _at_pointer(result, parent_pointer, path)
    token = tokens[-1]
    if isinstance(parent, dict):
        if token not in parent:
            _fail(path, f"JSON Pointer {pointer!r} does not exist")
        parent[token] = replacement
    elif isinstance(parent, list):
        if (
            token == "-"
            or not token.isdigit()
            or (len(token) > 1 and token.startswith("0"))
        ):
            _fail(path, f"JSON Pointer {pointer!r} has an invalid array index")
        index = int(token)
        if index >= len(parent):
            _fail(path, f"JSON Pointer {pointer!r} is out of bounds")
        parent[index] = replacement
    else:
        _fail(path, f"JSON Pointer {pointer!r} traverses a scalar")
    return result


def _validate_spec(spec: Any) -> Mapping[str, Any]:
    spec = _object(
        spec,
        "spec",
        {
            "schema_version",
            "binding",
            "capability",
            "protocol",
            "corpus",
            "native_system_contract_ref",
            "case_selection_ref",
            "basis_authorization_refs",
            "cases",
            "provenance",
        },
    )
    _const(spec["schema_version"], "caplab-revbench-spec/1", "spec.schema_version")
    _validate_binding(spec["binding"], "spec.binding")
    _validate_capability(spec["capability"], "spec.capability")
    _validate_content_ref(spec["protocol"], "spec.protocol", kind="protocol")
    _validate_content_ref(spec["corpus"], "spec.corpus", kind="corpus")
    _validate_content_ref(
        spec["native_system_contract_ref"],
        "spec.native_system_contract_ref",
        kind="native-agent-systems-contract",
        schema="caplab.native-agent-systems/v1",
    )
    _validate_content_ref(
        spec["case_selection_ref"],
        "spec.case_selection_ref",
        kind="case-selection",
        schema="caplab-case-selection-manifest/1",
    )
    authorizations = _object(
        spec["basis_authorization_refs"],
        "spec.basis_authorization_refs",
        {"truth", "case_selection", "metric_derivation"},
    )
    for role, ref in authorizations.items():
        _validate_content_ref(
            ref,
            f"spec.basis_authorization_refs.{role}",
            kind="evidence-basis-authorization",
            schema="caplab-evidence-basis-authorization/1",
        )
    cases = _array(spec["cases"], "spec.cases", minimum=1)
    seen: set[str] = set()
    for index, value in enumerate(cases):
        path = f"spec.cases[{index}]"
        case = _object(
            value, path, {"case_id", "control", "mutation", "oracle", "defect_anchor"}
        )
        case_id = _string(case["case_id"], f"{path}.case_id", pattern=_CASE_ID)
        if case_id in seen:
            _fail(f"{path}.case_id", "duplicates another case")
        seen.add(case_id)
        try:
            canonical_json(case["control"])
        except CanonicalizationError as error:
            _fail(f"{path}.control", str(error))
        mutation = _object(
            case["mutation"], f"{path}.mutation", {"operator", "pointer", "replacement"}
        )
        _const(
            mutation["operator"], "replace-json-value/1", f"{path}.mutation.operator"
        )
        mutation_pointer = _pointer(mutation["pointer"], f"{path}.mutation.pointer")
        replacement = _integer(mutation["replacement"], f"{path}.mutation.replacement")
        oracle = _object(
            case["oracle"], f"{path}.oracle", {"kind", "pointer", "minimum"}
        )
        _const(oracle["kind"], "json-integer-minimum/1", f"{path}.oracle.kind")
        oracle_pointer = _pointer(oracle["pointer"], f"{path}.oracle.pointer")
        minimum = _integer(oracle["minimum"], f"{path}.oracle.minimum")
        anchor = _pointer(case["defect_anchor"], f"{path}.defect_anchor")
        if not (mutation_pointer == oracle_pointer == anchor):
            _fail(
                path,
                "mutation, oracle, and defect anchor must use the same JSON Pointer",
            )
        control_value = _at_pointer(case["control"], oracle_pointer, f"{path}.control")
        _integer(control_value, f"{path}.control{oracle_pointer}")
        if control_value < minimum:
            _fail(f"{path}.control", "oracle target must meet the inclusive minimum")
        if replacement >= minimum:
            _fail(f"{path}.mutation.replacement", "must be below minimum")
    _validate_provenance(spec["provenance"], "spec.provenance")
    return spec


def prepare(
    spec: Mapping[str, Any], registrar: ArtifactRegistrar
) -> dict[str, JsonValue]:
    """Validate a revbench spec and deterministically prepare its manifest."""

    validated = _validate_spec(spec)
    _resolve_all_refs(validated, registrar, "spec")
    try:
        validate_qualification_binding(validated["binding"], registrar)
    except QualificationContractError as error:
        raise RevbenchContractError(f"spec.binding: {error}") from error
    _validate_native_binding(
        validated["binding"], validated["native_system_contract_ref"], registrar
    )
    _validate_case_selection(
        validated["case_selection_ref"],
        registrar,
        expected_cases=validated["cases"],
    )
    _validate_basis_authorizations(validated, registrar)
    manifest_cases: list[dict[str, JsonValue]] = []
    for case in sorted(validated["cases"], key=lambda item: item["case_id"]):
        control: JsonValue = json.loads(canonical_json(case["control"]))
        replacement = case["mutation"]["replacement"]
        pointer = case["mutation"]["pointer"]
        mutant = _replace_pointer(
            control, pointer, replacement, f"case {case['case_id']}"
        )
        # Re-read both values after construction: the oracle result is not copied
        # from preparation assumptions.
        control_result = (
            _integer(_at_pointer(control, pointer, "control"), "control target")
            >= case["oracle"]["minimum"]
        )
        mutant_result = (
            _integer(_at_pointer(mutant, pointer, "mutant"), "mutant target")
            >= case["oracle"]["minimum"]
        )
        if not control_result:
            _fail(f"case {case['case_id']}", "control fails target oracle")
        if mutant_result:
            _fail(f"case {case['case_id']}", "mutant does not fail target oracle")
        control_hash = sha256_hex(canonical_json(control))
        mutant_hash = sha256_hex(canonical_json(mutant))
        order_hash = sha256_hex(
            canonical_json(
                {
                    "case_id": case["case_id"],
                    "control_sha256": control_hash,
                    "mutant_sha256": mutant_hash,
                }
            )
        )
        assignment_order: list[JsonValue]
        if int(order_hash[0], 16) % 2:
            assignment_order = ["mutant", "control"]
        else:
            assignment_order = ["control", "mutant"]
        manifest_cases.append(
            {
                "case_id": case["case_id"],
                "assignment_order": assignment_order,
                "control": {
                    "content": control,
                    "sha256": control_hash,
                    "oracle_result": True,
                },
                "mutant": {
                    "content": mutant,
                    "sha256": mutant_hash,
                    "oracle_result": False,
                },
                "mutation": copy.deepcopy(case["mutation"]),
                "oracle": copy.deepcopy(case["oracle"]),
                "defect_anchor": case["defect_anchor"],
            }
        )
    identity: dict[str, JsonValue] = {
        "schema_version": "caplab-revbench-manifest/1",
        "family": "revbench",
        "family_version": "1",
        "binding": copy.deepcopy(validated["binding"]),
        "capability": copy.deepcopy(validated["capability"]),
        "protocol": copy.deepcopy(validated["protocol"]),
        "corpus": copy.deepcopy(validated["corpus"]),
        "native_system_contract_ref": copy.deepcopy(
            validated["native_system_contract_ref"]
        ),
        "case_selection_ref": copy.deepcopy(validated["case_selection_ref"]),
        "basis_authorization_refs": copy.deepcopy(
            validated["basis_authorization_refs"]
        ),
        "cases": manifest_cases,
        "provenance": copy.deepcopy(validated["provenance"]),
    }
    experiment_id = "revbench-" + sha256_hex(canonical_json(identity))
    return {
        "schema_version": identity["schema_version"],
        "experiment_id": experiment_id,
        **{key: value for key, value in identity.items() if key != "schema_version"},
    }


def _validate_manifest(
    manifest: Any, registrar: ArtifactRegistrar
) -> Mapping[str, Any]:
    manifest = _object(
        manifest,
        "manifest",
        {
            "schema_version",
            "experiment_id",
            "family",
            "family_version",
            "binding",
            "capability",
            "protocol",
            "corpus",
            "native_system_contract_ref",
            "case_selection_ref",
            "basis_authorization_refs",
            "cases",
            "provenance",
        },
    )
    _const(
        manifest["schema_version"],
        "caplab-revbench-manifest/1",
        "manifest.schema_version",
    )
    _string(manifest["experiment_id"], "manifest.experiment_id", pattern=_EXPERIMENT_ID)
    _const(manifest["family"], "revbench", "manifest.family")
    _const(manifest["family_version"], "1", "manifest.family_version")
    cases = _array(manifest["cases"], "manifest.cases", minimum=1)
    case_ids: list[str] = []
    for index, value in enumerate(cases):
        path = f"manifest.cases[{index}]"
        case = _object(
            value,
            path,
            {
                "case_id",
                "assignment_order",
                "control",
                "mutant",
                "mutation",
                "oracle",
                "defect_anchor",
            },
        )
        case_ids.append(_string(case["case_id"], f"{path}.case_id", pattern=_CASE_ID))
        order = _array(case["assignment_order"], f"{path}.assignment_order")
        if len(order) != 2 or set(order) != {"control", "mutant"}:
            _fail(
                f"{path}.assignment_order",
                "must contain control and mutant exactly once",
            )
        for arm, expected_result in (("control", True), ("mutant", False)):
            arm_value = _object(
                case[arm],
                f"{path}.{arm}",
                {"content", "sha256", "oracle_result"},
            )
            try:
                canonical_json(arm_value["content"])
            except CanonicalizationError as error:
                _fail(f"{path}.{arm}.content", str(error))
            _string(arm_value["sha256"], f"{path}.{arm}.sha256", pattern=_SHA256)
            _const(
                arm_value["oracle_result"],
                expected_result,
                f"{path}.{arm}.oracle_result",
            )
    if len(set(case_ids)) != len(case_ids):
        _fail("manifest.cases", "contains a duplicate case_id")
    if case_ids != sorted(case_ids):
        _fail("manifest.cases", "must be ordered by case_id")

    reconstructed_spec = {
        "schema_version": "caplab-revbench-spec/1",
        "binding": copy.deepcopy(manifest["binding"]),
        "capability": copy.deepcopy(manifest["capability"]),
        "protocol": copy.deepcopy(manifest["protocol"]),
        "corpus": copy.deepcopy(manifest["corpus"]),
        "native_system_contract_ref": copy.deepcopy(
            manifest["native_system_contract_ref"]
        ),
        "case_selection_ref": copy.deepcopy(manifest["case_selection_ref"]),
        "basis_authorization_refs": copy.deepcopy(manifest["basis_authorization_refs"]),
        "cases": [
            {
                "case_id": case["case_id"],
                "control": copy.deepcopy(case["control"]["content"]),
                "mutation": copy.deepcopy(case["mutation"]),
                "oracle": copy.deepcopy(case["oracle"]),
                "defect_anchor": case["defect_anchor"],
            }
            for case in cases
        ],
        "provenance": copy.deepcopy(manifest["provenance"]),
    }
    expected = prepare(reconstructed_spec, registrar)
    if manifest["experiment_id"] != expected["experiment_id"]:
        _fail(
            "manifest.experiment_id", "does not match the complete prepared experiment"
        )
    try:
        matches = canonical_json(manifest) == canonical_json(expected)
    except CanonicalizationError as error:
        _fail("manifest", str(error))
    if not matches:
        _fail("manifest", "does not match independently recomputed preparation")
    return manifest


def _validate_timestamp(value: Any, path: str) -> str:
    timestamp = _string(value, path, pattern=_UTC_TIMESTAMP)
    try:
        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as error:
        raise RevbenchContractError(f"{path}: is not a real UTC timestamp") from error
    return timestamp


def _validate_reviews(reviews: Any, manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    reviews = _object(
        reviews,
        "reviews",
        {
            "schema_version",
            "execution_id",
            "experiment_id",
            "execution_authorization_ref",
            "started_at",
            "observed_at",
            "status",
            "stop_reason",
            "attempts",
        },
    )
    _const(
        reviews["schema_version"], "caplab-revbench-reviews/1", "reviews.schema_version"
    )
    _string(reviews["experiment_id"], "reviews.experiment_id", pattern=_EXPERIMENT_ID)
    if reviews["experiment_id"] != manifest["experiment_id"]:
        _fail("reviews.experiment_id", "does not match the manifest experiment")
    started_at = _validate_timestamp(reviews["started_at"], "reviews.started_at")
    observed_at = _validate_timestamp(reviews["observed_at"], "reviews.observed_at")
    if started_at > observed_at:
        _fail("reviews", "execution interval is inverted")
    _validate_content_ref(
        reviews["execution_authorization_ref"],
        "reviews.execution_authorization_ref",
        kind="revbench-execution-authorization",
        schema="caplab-revbench-execution-authorization/1",
    )
    if reviews["status"] not in {"complete", "stopped"}:
        _fail("reviews.status", "is unsupported")
    stop_reasons = {
        "preflight-refused",
        "spawn-failure",
        "timeout",
        "stdout-limit",
        "stderr-limit",
        "authorization-expired",
        "exited",
    }
    if reviews["status"] == "complete":
        if reviews["stop_reason"] is not None:
            _fail("reviews.stop_reason", "must be null for a complete execution")
    elif reviews["stop_reason"] not in stop_reasons:
        _fail("reviews.stop_reason", "is required for a stopped execution")
    attempts = _array(reviews["attempts"], "reviews.attempts")
    known_cases = {case["case_id"]: case for case in manifest["cases"]}
    case_positions = {
        case["case_id"]: index for index, case in enumerate(manifest["cases"])
    }
    seen: set[tuple[str, str]] = set()
    seen_attempt_digests: set[str] = set()
    observed_order: list[tuple[int, int]] = []
    for index, value in enumerate(attempts):
        path = f"reviews.attempts[{index}]"
        attempt = _object(
            value,
            path,
            {
                "case_id",
                "arm",
                "assignment_index",
                "binding_id",
                "observed_binding",
                "attempt_ref",
                "attestation_ref",
                "prompt_ref",
                "disposition",
                "verdict",
                "anchors",
                "output_ref",
            },
        )
        case_id = _string(attempt["case_id"], f"{path}.case_id", pattern=_CASE_ID)
        if case_id not in known_cases:
            _fail(f"{path}.case_id", "is not present in the manifest")
        arm = attempt["arm"]
        if arm not in {"control", "mutant"}:
            _fail(f"{path}.arm", "must be control or mutant")
        assignment_index = _integer(
            attempt["assignment_index"], f"{path}.assignment_index", minimum=0
        )
        expected_assignment_index = known_cases[case_id]["assignment_order"].index(arm)
        if assignment_index != expected_assignment_index:
            _fail(
                f"{path}.assignment_index",
                "does not match the manifest assignment order",
            )
        observed_order.append((case_positions[case_id], assignment_index))
        key = (case_id, arm)
        if key in seen:
            _fail(path, "is a duplicate case/arm attempt")
        seen.add(key)
        _string(attempt["binding_id"], f"{path}.binding_id", pattern=_BINDING_ID)
        if attempt["binding_id"] != manifest["binding"]["binding_id"]:
            _fail(f"{path}.binding_id", "does not match the manifest Binding")
        _validate_binding(attempt["observed_binding"], f"{path}.observed_binding")
        try:
            binding_matches = canonical_json(
                attempt["observed_binding"]
            ) == canonical_json(manifest["binding"])
        except CanonicalizationError as error:
            _fail(f"{path}.observed_binding", str(error))
        if not binding_matches:
            _fail(f"{path}.observed_binding", "does not equal the manifest Binding")
        attempt_ref = _validate_content_ref(
            attempt["attempt_ref"],
            f"{path}.attempt_ref",
            kind="attempt",
            schema="caplab-native-review-attempt/1",
        )
        if attempt_ref["sha256"] in seen_attempt_digests:
            _fail(f"{path}.attempt_ref", "reuses another attempt envelope")
        seen_attempt_digests.add(attempt_ref["sha256"])
        _validate_content_ref(
            attempt["attestation_ref"],
            f"{path}.attestation_ref",
            kind="native-attempt-attestation",
            schema="caplab-native-attempt-attestation/1",
        )
        _validate_content_ref(
            attempt["prompt_ref"],
            f"{path}.prompt_ref",
            kind="prompt",
            schema="caplab-revbench-prompt/1",
        )
        _validate_content_ref(
            attempt["output_ref"],
            f"{path}.output_ref",
            kind="native-output",
            schema="caplab-native-output/1",
        )
        if attempt["disposition"] not in {
            "complete",
            "subject-failure",
            "infrastructure-failure",
        }:
            _fail(f"{path}.disposition", "is unsupported")
        if attempt["verdict"] not in {"clean", "defect", "invalid"}:
            _fail(f"{path}.verdict", "is unsupported")
        anchors = _array(attempt["anchors"], f"{path}.anchors")
        for anchor_index, anchor in enumerate(anchors):
            _pointer(anchor, f"{path}.anchors[{anchor_index}]")
        _sorted_unique(anchors, f"{path}.anchors")
    if observed_order != sorted(observed_order):
        _fail("reviews.attempts", "must follow manifest case and assignment order")
    expected_attempt_count = len(manifest["cases"]) * 2
    if len(attempts) > expected_attempt_count:
        _fail("reviews.attempts", "exceeds the sealed manifest attempt count")
    if reviews["status"] == "complete" and len(attempts) != expected_attempt_count:
        _fail("reviews.attempts", "complete execution must contain every assignment")
    return reviews


def _parse_canonical_json_ref(
    ref: Mapping[str, Any], registrar: ArtifactRegistrar, path: str
) -> Any:
    data = _resolve_ref(ref, registrar, path)
    try:
        document = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RevbenchContractError(f"{path}: resolved bytes are not JSON") from error
    try:
        encoded = canonical_json(document)
    except CanonicalizationError as error:
        _fail(path, str(error))
    if encoded != data:
        _fail(path, "resolved JSON is not in canonical form")
    return document


def _read_sealed_executable(path: Path) -> tuple[bytes, int]:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise RevbenchContractError(
            "binding.harness.executable_ref: executable is unavailable"
        ) from error
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            _fail(
                "binding.harness.executable_ref",
                "executable must be a real regular file",
            )
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks), metadata.st_mode
    except OSError as error:
        raise RevbenchContractError(
            "binding.harness.executable_ref: executable is unreadable"
        ) from error
    finally:
        os.close(descriptor)


def _validate_local_fixture_policy(
    policy: Mapping[str, Any],
    binding: Mapping[str, Any],
    command_argv: Sequence[str],
    version_argv: Sequence[str],
    probe: Mapping[str, Any],
    registrar: ArtifactRegistrar,
) -> None:
    policy = _object(
        policy,
        "native_system_contract_ref document",
        {
            "schema",
            "policy",
            "decision_authority",
            "source_observation",
            "systems",
            "forbidden_proxy_markers",
            "exceptions",
        },
    )
    _const(
        policy["policy"],
        _LOCAL_FIXTURE_POLICY,
        "native_system_contract_ref document.policy",
    )
    _const(
        policy["decision_authority"],
        _LOCAL_FIXTURE_AUTHORITY,
        "native_system_contract_ref document.decision_authority",
    )
    if canonical_json(policy["source_observation"]) != canonical_json(
        _LOCAL_FIXTURE_SOURCE
    ):
        _fail(
            "native_system_contract_ref document.source_observation",
            "does not identify the repository-owned synthetic fixture profile",
        )
    if policy["forbidden_proxy_markers"] != _REQUIRED_PROXY_MARKERS:
        _fail(
            "native_system_contract_ref document.forbidden_proxy_markers",
            "must contain the complete repository proxy-marker set",
        )
    _const(
        policy["exceptions"],
        [],
        "native_system_contract_ref document.exceptions",
    )

    provider = binding["provider_or_path"]
    for field, expected in (
        ("identifier", _LOCAL_FIXTURE_PROFILE["provider_identifier"]),
        ("revision", _LOCAL_FIXTURE_PROFILE["revision"]),
        ("resolution", "immutable"),
        ("observed_at", None),
    ):
        _const(provider[field], expected, f"binding.provider_or_path.{field}")
    model = binding["model"]
    _const(
        model["model_id"],
        _LOCAL_FIXTURE_PROFILE["model_id"],
        "binding.model.model_id",
    )
    _const(
        model["revision"],
        _LOCAL_FIXTURE_PROFILE["revision"],
        "binding.model.revision",
    )
    harness = binding["harness"]
    _const(
        harness["harness_id"],
        _LOCAL_FIXTURE_PROFILE["harness_id"],
        "binding.harness.harness_id",
    )
    _const(
        harness["harness_version"],
        _LOCAL_FIXTURE_PROFILE["harness_version"],
        "binding.harness.harness_version",
    )
    _const(
        binding["reasoning_effort"],
        _LOCAL_FIXTURE_PROFILE["effort"],
        "binding.reasoning_effort",
    )

    systems = _object(
        policy["systems"],
        "native_system_contract_ref document.systems",
        {_LOCAL_FIXTURE_PROFILE["tuple_id"]},
    )
    expected = _object(
        systems[_LOCAL_FIXTURE_PROFILE["tuple_id"]],
        (
            "native_system_contract_ref document.systems."
            + _LOCAL_FIXTURE_PROFILE["tuple_id"]
        ),
        {
            "model_id",
            "native_harness_id",
            "harness_version",
            "effort",
            "executable",
            "required_command_tokens",
            "version_command",
            "version_exit_code",
            "version_stdout_sha256",
            "version_stderr_sha256",
        },
    )
    for field in ("model_id", "harness_version", "effort"):
        _const(
            expected[field],
            _LOCAL_FIXTURE_PROFILE[field],
            f"native_system_contract_ref document.systems fixture.{field}",
        )
    _const(
        expected["native_harness_id"],
        _LOCAL_FIXTURE_PROFILE["harness_id"],
        "native_system_contract_ref document.systems fixture.native_harness_id",
    )

    executable_text = _string(
        expected["executable"],
        "native_system_contract_ref document.systems fixture.executable",
    )
    executable_path = Path(executable_text)
    if not executable_path.is_absolute():
        _fail(
            "native_system_contract_ref document.systems fixture.executable",
            "must be an absolute path",
        )
    _const(
        expected["required_command_tokens"],
        ["review"],
        "native_system_contract_ref document.systems fixture.required_command_tokens",
    )
    _const(
        expected["version_command"],
        [executable_text, "--version"],
        "native_system_contract_ref document.systems fixture.version_command",
    )
    _const(
        list(command_argv),
        [executable_text, "review"],
        "binding.harness.command_ref document.argv",
    )
    if not version_argv or version_argv[0] != executable_text:
        _fail(
            "binding.harness.version_probe_ref",
            "does not use the sealed executable",
        )
    executable_ref = harness["executable_ref"]
    if executable_ref is None:
        _fail(
            "binding.harness.executable_ref",
            "is required for the synthetic fixture profile",
        )
    registered_executable = _resolve_ref(
        executable_ref, registrar, "binding.harness.executable_ref"
    )
    observed_executable, executable_mode = _read_sealed_executable(executable_path)
    if observed_executable != registered_executable:
        _fail(
            "binding.harness.executable_ref",
            "does not match executable bytes",
        )
    if executable_mode & 0o111 == 0:
        _fail("binding.harness.executable_ref", "executable mode is absent")

    _const(
        expected["version_exit_code"],
        0,
        "native_system_contract_ref document.systems fixture.version_exit_code",
    )
    _const(
        probe["exit_code"], 0, "binding.harness.version_probe_ref document.exit_code"
    )
    pinned_stream_digests = {
        "stdout": _LOCAL_FIXTURE_VERSION_STDOUT_SHA256,
        "stderr": _LOCAL_FIXTURE_VERSION_STDERR_SHA256,
    }
    for stream in ("stdout", "stderr"):
        expected_digest = _string(
            expected[f"version_{stream}_sha256"],
            (
                "native_system_contract_ref document.systems fixture."
                f"version_{stream}_sha256"
            ),
            pattern=_SHA256,
        )
        _const(
            expected_digest,
            pinned_stream_digests[stream],
            (
                "native_system_contract_ref document.systems fixture."
                f"version_{stream}_sha256"
            ),
        )
        observed = _resolve_ref(
            probe[f"{stream}_ref"],
            registrar,
            f"binding.harness.version_probe_ref document.{stream}_ref",
        )
        if sha256_hex(observed) != expected_digest:
            _fail(
                f"binding.harness.version_probe_ref document.{stream}_ref",
                "does not match the pinned fixture version observation",
            )


def _validate_native_binding(
    binding: Mapping[str, Any],
    contract_ref: Mapping[str, Any],
    registrar: ArtifactRegistrar,
) -> None:
    policy = _parse_canonical_json_ref(
        contract_ref, registrar, "native_system_contract_ref"
    )
    if not isinstance(policy, Mapping):
        _fail("native_system_contract_ref", "must resolve to an object")
    if policy.get("schema") != "caplab.native-agent-systems/v1":
        _fail("native_system_contract_ref document.schema", "has the wrong schema")
    systems = policy.get("systems")
    if not isinstance(systems, Mapping) or not systems:
        _fail("native_system_contract_ref document.systems", "must be non-empty")
    if policy.get("exceptions") != []:
        _fail(
            "native_system_contract_ref document.exceptions",
            "requires a new repository-owner contract",
        )

    provider_kind = binding["provider_or_path"]["kind"]
    if provider_kind != "local-serving":
        if sha256_hex(canonical_json(policy)) != (
            CANONICAL_NATIVE_AGENT_SYSTEM_POLICY_SHA256
        ):
            _fail(
                "native_system_contract_ref",
                "does not match docs/product/contracts/native-agent-systems.json",
            )
        _fail(
            "binding.provider_or_path.kind",
            "live native provider preparation is not implemented in revbench v1",
        )

    command = _parse_canonical_json_ref(
        binding["harness"]["command_ref"], registrar, "binding.harness.command_ref"
    )
    if not isinstance(command, Mapping) or set(command) != {"schema_version", "argv"}:
        _fail("binding.harness.command_ref document", "has the wrong command shape")
    _const(
        command["schema_version"],
        "caplab-native-harness-command/1",
        "binding.harness.command_ref document.schema_version",
    )
    command_argv = _array(
        command["argv"], "binding.harness.command_ref document.argv", minimum=1
    )
    for index, token in enumerate(command_argv):
        _string(token, f"binding.harness.command_ref document.argv[{index}]")

    probe = _parse_canonical_json_ref(
        binding["harness"]["version_probe_ref"],
        registrar,
        "binding.harness.version_probe_ref",
    )
    if not isinstance(probe, Mapping) or set(probe) != {
        "command_ref",
        "exit_code",
        "stdout_ref",
        "stderr_ref",
    }:
        _fail("binding.harness.version_probe_ref document", "has the wrong probe shape")
    version_command = _parse_canonical_json_ref(
        probe["command_ref"],
        registrar,
        "binding.harness.version_probe_ref document.command_ref",
    )
    if not isinstance(version_command, Mapping) or set(version_command) != {
        "schema_version",
        "argv",
    }:
        _fail(
            "binding.harness.version_probe_ref document.command_ref document",
            "has the wrong command shape",
        )
    _const(
        version_command["schema_version"],
        "caplab-native-harness-version-command/1",
        "binding.harness.version_probe_ref document.command_ref document.schema_version",
    )
    version_argv = _array(
        version_command["argv"],
        "binding.harness.version_probe_ref document.command_ref document.argv",
        minimum=1,
    )
    for index, token in enumerate(version_argv):
        _string(
            token,
            f"binding.harness.version_probe_ref document.command_ref document.argv[{index}]",
        )

    _validate_local_fixture_policy(
        policy,
        binding,
        command_argv,
        version_argv,
        probe,
        registrar,
    )

    matching_tuple_ids = [
        tuple_id
        for tuple_id, expected in systems.items()
        if isinstance(tuple_id, str)
        and isinstance(expected, Mapping)
        and expected.get("model_id") == binding["model"]["model_id"]
        and expected.get("native_harness_id") == binding["harness"]["harness_id"]
        and expected.get("effort") == binding["reasoning_effort"]
    ]
    if len(matching_tuple_ids) != 1:
        _fail(
            "binding",
            "does not identify exactly one tuple in native_system_contract_ref",
        )
    subject = {
        "tuple_id": matching_tuple_ids[0],
        "model_id": binding["model"]["model_id"],
        "native_harness_id": binding["harness"]["harness_id"],
        "effort": binding["reasoning_effort"],
        "command": list(command_argv),
        "version_command": list(version_argv),
    }
    try:
        validate_native_agent_systems(policy, {binding["binding_id"]: subject})
    except NativeAgentSystemContractError as error:
        raise RevbenchContractError(
            f"native system contract rejected Binding: {error}"
        ) from error


def _validate_delegation_ref(
    ref: Mapping[str, Any],
    registrar: ArtifactRegistrar,
    path: str,
    *,
    effect: str,
    authorized_by: str,
    delegate_or_mechanism: str,
    scope: Mapping[str, Any],
    valid_from: str,
    valid_until: str,
) -> None:
    _validate_content_ref(
        ref,
        path,
        kind="authorization-delegation",
        schema="caplab-authorization-delegation/1",
    )
    delegation = _parse_canonical_json_ref(ref, registrar, path)
    delegation = _object(
        delegation,
        f"{path} document",
        {
            "schema_version",
            "delegation_id",
            "effect",
            "authorized_by",
            "delegate_or_mechanism",
            "scope",
            "valid_from",
            "valid_until",
        },
    )
    _const(
        delegation["schema_version"],
        "caplab-authorization-delegation/1",
        f"{path} document.schema_version",
    )
    expected = {
        "effect": effect,
        "authorized_by": authorized_by,
        "delegate_or_mechanism": delegate_or_mechanism,
        "scope": scope,
        "valid_from": valid_from,
        "valid_until": valid_until,
    }
    for field, expected_value in expected.items():
        if canonical_json(delegation[field]) != canonical_json(expected_value):
            _fail(f"{path} document.{field}", "does not match authorization scope")
    identity = copy.deepcopy(dict(delegation))
    identity.pop("delegation_id")
    if delegation["delegation_id"] != "delegation-" + sha256_hex(
        canonical_json(identity)
    ):
        _fail(f"{path} document.delegation_id", "is not content-derived")


def _validate_execution_authorization(
    ref: Mapping[str, Any],
    manifest: Mapping[str, Any],
    registrar: ArtifactRegistrar,
    *,
    observed_at: str | None = None,
) -> Mapping[str, Any]:
    """Validate one registered, tightly scoped revbench execution authority."""

    _validate_content_ref(
        ref,
        "execution_authorization_ref",
        kind="revbench-execution-authorization",
        schema="caplab-revbench-execution-authorization/1",
    )
    authorization = _parse_canonical_json_ref(
        ref, registrar, "execution_authorization_ref"
    )
    authorization = _object(
        authorization,
        "execution_authorization_ref document",
        {
            "schema_version",
            "authorization_id",
            "authority_source_ref",
            "authorized_by",
            "delegate_or_mechanism",
            "experiment_id",
            "manifest_ref",
            "binding_id",
            "native_system_contract_ref",
            "command_ref",
            "version_probe_ref",
            "effect_class",
            "limits",
            "valid_from",
            "valid_until",
        },
    )
    _const(
        authorization["schema_version"],
        "caplab-revbench-execution-authorization/1",
        "execution_authorization_ref document.schema_version",
    )
    _string(
        authorization["authorization_id"],
        "execution_authorization_ref document.authorization_id",
    )
    authorized_by = _string(
        authorization["authorized_by"],
        "execution_authorization_ref document.authorized_by",
    )
    delegate_or_mechanism = _string(
        authorization["delegate_or_mechanism"],
        "execution_authorization_ref document.delegate_or_mechanism",
    )
    manifest_ref = _validate_content_ref(
        authorization["manifest_ref"],
        "execution_authorization_ref document.manifest_ref",
        kind="revbench-manifest",
        schema="caplab-revbench-manifest/1",
    )
    if _resolve_ref(
        manifest_ref,
        registrar,
        "execution_authorization_ref document.manifest_ref",
    ) != canonical_json(manifest):
        _fail(
            "execution_authorization_ref document.manifest_ref",
            "does not resolve to the supplied manifest",
        )
    _const(
        authorization["experiment_id"],
        manifest["experiment_id"],
        "execution_authorization_ref document.experiment_id",
    )
    _const(
        authorization["binding_id"],
        manifest["binding"]["binding_id"],
        "execution_authorization_ref document.binding_id",
    )
    for field, expected in (
        ("native_system_contract_ref", manifest["native_system_contract_ref"]),
        ("command_ref", manifest["binding"]["harness"]["command_ref"]),
        ("version_probe_ref", manifest["binding"]["harness"]["version_probe_ref"]),
    ):
        if canonical_json(authorization[field]) != canonical_json(expected):
            _fail(
                f"execution_authorization_ref document.{field}",
                "does not match the prepared Binding",
            )
    expected_effect_class = (
        "local-fixture"
        if manifest["binding"]["provider_or_path"]["kind"] == "local-serving"
        else "live-native-provider"
    )
    _const(
        authorization["effect_class"],
        expected_effect_class,
        "execution_authorization_ref document.effect_class",
    )
    limits = _object(
        authorization["limits"],
        "execution_authorization_ref document.limits",
        {
            "max_version_probe_processes",
            "max_native_review_processes",
            "timeout_seconds_per_process",
            "total_wall_seconds",
            "max_stdout_bytes_per_process",
            "max_stderr_bytes_per_process",
        },
    )
    expected_attempts = len(manifest["cases"]) * 2
    for field in ("max_version_probe_processes", "max_native_review_processes"):
        if (
            _integer(
                limits[field],
                f"execution_authorization_ref document.limits.{field}",
                minimum=1,
            )
            != expected_attempts
        ):
            _fail(
                f"execution_authorization_ref document.limits.{field}",
                "must equal the sealed manifest attempt count",
            )
    timeout_seconds = _integer(
        limits["timeout_seconds_per_process"],
        "execution_authorization_ref document.limits.timeout_seconds_per_process",
        minimum=1,
    )
    total_wall_seconds = _integer(
        limits["total_wall_seconds"],
        "execution_authorization_ref document.limits.total_wall_seconds",
        minimum=1,
    )
    if timeout_seconds > 3600 or total_wall_seconds > 86400:
        _fail("execution_authorization_ref document.limits", "exceeds v1 time ceilings")
    for field in (
        "max_stdout_bytes_per_process",
        "max_stderr_bytes_per_process",
    ):
        byte_limit = _integer(
            limits[field],
            f"execution_authorization_ref document.limits.{field}",
            minimum=1,
        )
        if byte_limit > 16 * 1024 * 1024:
            _fail(
                f"execution_authorization_ref document.limits.{field}",
                "exceeds the v1 byte ceiling",
            )
    valid_from = _validate_timestamp(
        authorization["valid_from"],
        "execution_authorization_ref document.valid_from",
    )
    valid_until = _validate_timestamp(
        authorization["valid_until"],
        "execution_authorization_ref document.valid_until",
    )
    if valid_from > valid_until:
        _fail("execution_authorization_ref document", "valid interval is inverted")
    scope = {
        field: authorization[field]
        for field in (
            "experiment_id",
            "manifest_ref",
            "binding_id",
            "native_system_contract_ref",
            "command_ref",
            "version_probe_ref",
            "effect_class",
            "limits",
        )
    }
    _validate_delegation_ref(
        authorization["authority_source_ref"],
        registrar,
        "execution_authorization_ref document.authority_source_ref",
        effect="revbench-execution",
        authorized_by=authorized_by,
        delegate_or_mechanism=delegate_or_mechanism,
        scope=scope,
        valid_from=valid_from,
        valid_until=valid_until,
    )
    identity = copy.deepcopy(dict(authorization))
    identity.pop("authorization_id")
    expected_id = "revbench-execution-auth-" + sha256_hex(canonical_json(identity))
    if authorization["authorization_id"] != expected_id:
        _fail(
            "execution_authorization_ref document.authorization_id",
            "is not content-derived",
        )
    if observed_at is not None:
        observed = _validate_timestamp(observed_at, "execution observed_at")
        if observed < valid_from or observed > valid_until:
            _fail(
                "execution observed_at",
                "is outside the execution authorization interval",
            )
    _resolve_all_refs(authorization, registrar, "execution_authorization_ref document")
    return authorization


def _validate_case_selection(
    selection_ref: Mapping[str, Any],
    registrar: ArtifactRegistrar,
    *,
    expected_cases: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any]:
    selection = _parse_canonical_json_ref(
        selection_ref, registrar, "case_selection_ref"
    )
    selection = _object(
        selection,
        "case_selection_ref document",
        {
            "schema_version",
            "selection_id",
            "population_ref",
            "included_case_refs",
            "excluded_case_refs",
            "selection_inputs",
            "exclusion_inputs",
            "conditioned_on",
            "authorization_ref",
        },
    )
    _const(
        selection["schema_version"],
        "caplab-case-selection-manifest/1",
        "case_selection_ref document.schema_version",
    )
    _string(selection["selection_id"], "case_selection_ref document.selection_id")
    _validate_content_ref(
        selection["population_ref"],
        "case_selection_ref document.population_ref",
        kind="case-population",
    )
    for name in (
        "included_case_refs",
        "excluded_case_refs",
        "selection_inputs",
        "exclusion_inputs",
    ):
        refs = _array(selection[name], f"case_selection_ref document.{name}")
        for index, ref in enumerate(refs):
            _validate_content_ref(ref, f"case_selection_ref document.{name}[{index}]")
        _sorted_unique(refs, f"case_selection_ref document.{name}")
    conditioned_on = _array(
        selection["conditioned_on"], "case_selection_ref document.conditioned_on"
    )
    allowed_conditions = {
        "downstream_fate",
        "model_judgment",
        "human_judgment",
        "provider_verdict",
        "scheduler_choice",
        "admission",
        "backend_rank",
        "task_difficulty",
        "attempt_outcome",
    }
    for index, condition in enumerate(conditioned_on):
        if condition not in allowed_conditions:
            _fail(
                f"case_selection_ref document.conditioned_on[{index}]", "is unsupported"
            )
    _sorted_unique(conditioned_on, "case_selection_ref document.conditioned_on")
    if conditioned_on:
        _fail(
            "case_selection_ref document.conditioned_on",
            "must be empty for the source-population revbench distribution",
        )
    if selection["selection_inputs"] or selection["exclusion_inputs"]:
        _fail(
            "case_selection_ref document",
            "revbench v1 requires an explicit case list with no selection inputs",
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
    delegation = _parse_canonical_json_ref(
        selection["authorization_ref"],
        registrar,
        "case_selection_ref document.authorization_ref",
    )
    if not isinstance(delegation, Mapping):
        _fail(
            "case_selection_ref document.authorization_ref", "must resolve to an object"
        )
    _validate_delegation_ref(
        selection["authorization_ref"],
        registrar,
        "case_selection_ref document.authorization_ref",
        effect="case-selection",
        authorized_by=delegation.get("authorized_by"),
        delegate_or_mechanism=delegation.get("delegate_or_mechanism"),
        scope=selection_scope,
        valid_from=delegation.get("valid_from"),
        valid_until=delegation.get("valid_until"),
    )
    identity = copy.deepcopy(dict(selection))
    identity.pop("selection_id")
    expected = "selection-" + sha256_hex(canonical_json(identity))
    if selection["selection_id"] != expected:
        _fail("case_selection_ref document.selection_id", "is not content-derived")
    _resolve_all_refs(selection, registrar, "case_selection_ref document")
    selected_case_bytes = sorted(
        canonical_json(
            _parse_canonical_json_ref(
                ref,
                registrar,
                f"case_selection_ref document.included_case_refs[{index}]",
            )
        )
        for index, ref in enumerate(selection["included_case_refs"])
    )
    expected_case_bytes = sorted(canonical_json(case) for case in expected_cases)
    if selected_case_bytes != expected_case_bytes:
        _fail(
            "case_selection_ref document.included_case_refs",
            "does not identify exactly the revbench spec cases",
        )
    return selection


def _validate_basis_authorizations(
    artifact: Mapping[str, Any],
    registrar: ArtifactRegistrar,
    *,
    observed_at: str | None = None,
) -> None:
    roles = {
        "truth": "truth",
        "case_selection": "case-selection",
        "metric_derivation": "metric-derivation",
    }
    for key, public_role in roles.items():
        path = f"basis_authorization_refs.{key}"
        authorization = _parse_canonical_json_ref(
            artifact["basis_authorization_refs"][key], registrar, path
        )
        authorization = _object(
            authorization,
            f"{path} document",
            {
                "schema_version",
                "authorization_id",
                "authority_source_ref",
                "authorized_by",
                "delegate_or_mechanism",
                "binding_ids",
                "capability",
                "experiment",
                "protocol_ref",
                "corpus_ref",
                "case_selection_ref",
                "method_ref",
                "basis_kind",
                "basis_role",
                "valid_from",
                "valid_until",
            },
        )
        _const(
            authorization["schema_version"],
            "caplab-evidence-basis-authorization/1",
            f"{path} document.schema_version",
        )
        _string(authorization["authorization_id"], f"{path} document.authorization_id")
        authorized_by = _string(
            authorization["authorized_by"], f"{path} document.authorized_by"
        )
        delegate_or_mechanism = _string(
            authorization["delegate_or_mechanism"],
            f"{path} document.delegate_or_mechanism",
        )
        binding_ids = _array(
            authorization["binding_ids"], f"{path} document.binding_ids", minimum=1
        )
        for index, binding_id in enumerate(binding_ids):
            _string(
                binding_id, f"{path} document.binding_ids[{index}]", pattern=_BINDING_ID
            )
        _sorted_unique(binding_ids, f"{path} document.binding_ids")
        if list(binding_ids) != [artifact["binding"]["binding_id"]]:
            _fail(f"{path} document.binding_ids", "does not exactly scope this Binding")
        _validate_capability(authorization["capability"], f"{path} document.capability")
        if canonical_json(authorization["capability"]) != canonical_json(
            artifact["capability"]
        ):
            _fail(
                f"{path} document.capability", "does not exactly scope this capability"
            )
        experiment = _object(
            authorization["experiment"],
            f"{path} document.experiment",
            {"family", "version"},
        )
        _const(experiment["family"], "revbench", f"{path} document.experiment.family")
        _const(experiment["version"], "1", f"{path} document.experiment.version")
        for field, expected, kind, schema in (
            ("protocol_ref", artifact["protocol"], "protocol", None),
            ("corpus_ref", artifact["corpus"], "corpus", None),
            (
                "case_selection_ref",
                artifact["case_selection_ref"],
                "case-selection",
                "caplab-case-selection-manifest/1",
            ),
        ):
            _validate_content_ref(
                authorization[field],
                f"{path} document.{field}",
                kind=kind,
                schema=schema,
            )
            if canonical_json(authorization[field]) != canonical_json(expected):
                _fail(
                    f"{path} document.{field}",
                    "does not exactly match the revbench scope",
                )
        _validate_content_ref(
            authorization["method_ref"], f"{path} document.method_ref"
        )
        _const(
            authorization["basis_kind"],
            "mechanical-oracle",
            f"{path} document.basis_kind",
        )
        _const(authorization["basis_role"], public_role, f"{path} document.basis_role")
        valid_from = _validate_timestamp(
            authorization["valid_from"], f"{path} document.valid_from"
        )
        valid_until = _validate_timestamp(
            authorization["valid_until"], f"{path} document.valid_until"
        )
        if valid_from > valid_until:
            _fail(f"{path} document", "valid interval is inverted")
        if observed_at is not None and not (valid_from <= observed_at <= valid_until):
            _fail(path, "does not authorize the Measurement observation time")
        scope = {
            key_name: authorization[key_name]
            for key_name in (
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
        _validate_delegation_ref(
            authorization["authority_source_ref"],
            registrar,
            f"{path} document.authority_source_ref",
            effect="evidence-basis",
            authorized_by=authorized_by,
            delegate_or_mechanism=delegate_or_mechanism,
            scope=scope,
            valid_from=authorization["valid_from"],
            valid_until=authorization["valid_until"],
        )
        identity = copy.deepcopy(dict(authorization))
        identity.pop("authorization_id")
        expected_id = "basis-auth-" + sha256_hex(canonical_json(identity))
        if authorization["authorization_id"] != expected_id:
            _fail(f"{path} document.authorization_id", "is not content-derived")
        _resolve_all_refs(authorization, registrar, f"{path} document")


def _verified_registration(
    registrar: ArtifactRegistrar,
    document: JsonValue,
    *,
    kind: str,
    schema: str,
    registration_id: str,
) -> ContentRef:
    try:
        returned = registrar.register_document(
            document,
            kind=kind,
            schema=schema,
            registration_id=registration_id,
        )
    except Exception as error:
        raise RevbenchContractError(
            f"registration {registration_id!r} failed"
        ) from error
    ref = _validate_content_ref(
        returned, f"registration {registration_id!r}", kind=kind, schema=schema
    )
    resolved = _resolve_ref(ref, registrar, f"registration {registration_id!r}")
    if resolved != canonical_json(document):
        _fail(
            f"registration {registration_id!r}",
            "did not resolve to the registered document",
        )
    return copy.deepcopy(dict(ref))


def _basis(
    *,
    role: str,
    evidence_ref: Mapping[str, Any],
    authorization_ref: Mapping[str, Any],
) -> dict[str, JsonValue]:
    fields: dict[str, JsonValue] = {
        "kind": "mechanical-oracle",
        "role": role,
        "evidence_ref": copy.deepcopy(dict(evidence_ref)),
        "authorization_ref": copy.deepcopy(dict(authorization_ref)),
    }
    return {"basis_id": "basis-" + sha256_hex(canonical_json(fields)), **fields}


def _verify_execution_attempt_evidence(
    attempt: Mapping[str, Any],
    manifest: Mapping[str, Any],
    execution_authorization_ref: Mapping[str, Any],
    review_observed_at: str,
    registrar: ArtifactRegistrar,
    path: str,
) -> tuple[str, str]:
    """Reconstruct one supported execution attempt from its registered bytes."""

    experiment_id = manifest["experiment_id"]
    binding = manifest["binding"]
    manifest_case = next(
        case for case in manifest["cases"] if case["case_id"] == attempt["case_id"]
    )
    envelope = _parse_canonical_json_ref(
        attempt["attempt_ref"], registrar, f"{path}.attempt_ref"
    )
    envelope = _object(
        envelope,
        f"{path}.attempt_ref document",
        {
            "schema_version",
            "attempt_id",
            "experiment_id",
            "case_id",
            "arm",
            "assignment_index",
            "binding_id",
            "observed_binding",
            "attestation_ref",
            "prompt_ref",
            "disposition",
            "verdict",
            "anchors",
            "output_ref",
            "provenance",
        },
    )
    _const(
        envelope["schema_version"],
        "caplab-native-review-attempt/1",
        f"{path}.attempt_ref document.schema_version",
    )
    envelope_identity = copy.deepcopy(dict(envelope))
    envelope_identity.pop("attempt_id")
    if envelope["attempt_id"] != "attempt-" + sha256_hex(
        canonical_json(envelope_identity)
    ):
        _fail(f"{path}.attempt_ref document.attempt_id", "is not content-derived")
    projection = copy.deepcopy(dict(envelope))
    for field in ("schema_version", "attempt_id", "experiment_id", "provenance"):
        projection.pop(field)
    supplied = copy.deepcopy(dict(attempt))
    supplied.pop("attempt_ref")
    if canonical_json(projection) != canonical_json(supplied):
        _fail(path, "review attempt does not equal its registered envelope projection")
    _validate_provenance(
        envelope["provenance"], f"{path}.attempt_ref document.provenance"
    )

    prompt = _parse_canonical_json_ref(
        attempt["prompt_ref"], registrar, f"{path}.prompt_ref"
    )
    prompt = _object(
        prompt,
        f"{path}.prompt_ref document",
        {
            "schema_version",
            "experiment_id",
            "case_id",
            "arm",
            "assignment_index",
            "binding_id",
            "protocol_ref",
            "rendered_input_ref",
        },
    )
    expected_prompt = {
        "schema_version": "caplab-revbench-prompt/1",
        "experiment_id": experiment_id,
        "case_id": attempt["case_id"],
        "arm": attempt["arm"],
        "assignment_index": attempt["assignment_index"],
        "binding_id": binding["binding_id"],
        "protocol_ref": manifest["protocol"],
    }
    for field, expected in expected_prompt.items():
        if canonical_json(prompt[field]) != canonical_json(expected):
            _fail(
                f"{path}.prompt_ref document.{field}",
                "does not match prepared assignment",
            )
    _validate_content_ref(
        prompt["rendered_input_ref"],
        f"{path}.prompt_ref document.rendered_input_ref",
        kind="native-input",
        schema="caplab-revbench-native-input/1",
    )
    native_input = _parse_canonical_json_ref(
        prompt["rendered_input_ref"],
        registrar,
        f"{path}.prompt_ref document.rendered_input_ref",
    )
    expected_input = {
        "schema_version": "caplab-revbench-native-input/1",
        "instruction": _NATIVE_INPUT_INSTRUCTION,
        "requirement": manifest_case["oracle"],
        "artifact": manifest_case[attempt["arm"]]["content"],
        "response_schema_version": "caplab-revbench-native-response/1",
    }
    if canonical_json(native_input) != canonical_json(expected_input):
        _fail(
            f"{path}.prompt_ref document.rendered_input_ref",
            "does not match blinded native input",
        )

    output = _parse_canonical_json_ref(
        attempt["output_ref"], registrar, f"{path}.output_ref"
    )
    output = _object(
        output,
        f"{path}.output_ref document",
        {
            "schema_version",
            "experiment_id",
            "case_id",
            "arm",
            "assignment_index",
            "binding_id",
            "raw_stdout_ref",
            "parse_status",
            "verdict",
            "anchors",
        },
    )
    expected_output = {
        "schema_version": "caplab-native-output/1",
        "experiment_id": experiment_id,
        "case_id": attempt["case_id"],
        "arm": attempt["arm"],
        "assignment_index": attempt["assignment_index"],
        "binding_id": binding["binding_id"],
        "verdict": attempt["verdict"],
        "anchors": attempt["anchors"],
    }
    for field, expected in expected_output.items():
        if canonical_json(output[field]) != canonical_json(expected):
            _fail(
                f"{path}.output_ref document.{field}", "does not match review attempt"
            )
    _validate_content_ref(
        output["raw_stdout_ref"],
        f"{path}.output_ref document.raw_stdout_ref",
        kind="native-process-stdout",
        schema="caplab-native-process-stream/1",
    )
    raw_stdout = _resolve_ref(
        output["raw_stdout_ref"], registrar, f"{path}.output_ref raw_stdout_ref"
    )
    if output["parse_status"] == "valid":

        def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate native response key")
                result[key] = value
            return result

        try:
            response = json.loads(raw_stdout, object_pairs_hook=unique_pairs)
        except (UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise RevbenchContractError(
                f"{path}.output_ref: raw stdout is not one JSON response"
            ) from error
        response = _object(
            response,
            f"{path}.output_ref raw response",
            {"schema_version", "verdict", "anchors"},
        )
        _const(
            response["schema_version"],
            "caplab-revbench-native-response/1",
            f"{path}.output_ref raw response.schema_version",
        )
        if response["verdict"] not in {"clean", "defect"}:
            _fail(f"{path}.output_ref raw response.verdict", "is unsupported")
        anchors = _array(response["anchors"], f"{path}.output_ref raw response.anchors")
        for index, anchor in enumerate(anchors):
            _pointer(anchor, f"{path}.output_ref raw response.anchors[{index}]")
        _sorted_unique(anchors, f"{path}.output_ref raw response.anchors")
        if (response["verdict"] == "clean" and anchors) or (
            response["verdict"] == "defect" and not anchors
        ):
            _fail(f"{path}.output_ref raw response", "verdict and anchors disagree")
        if response["verdict"] != output["verdict"] or canonical_json(
            anchors
        ) != canonical_json(output["anchors"]):
            _fail(f"{path}.output_ref", "does not project raw stdout")
    elif output["parse_status"] == "invalid":
        if output["verdict"] != "invalid" or output["anchors"] != []:
            _fail(f"{path}.output_ref", "invalid parse must remain invalid")
    else:
        _fail(f"{path}.output_ref document.parse_status", "is unsupported")

    attestation = _parse_canonical_json_ref(
        attempt["attestation_ref"], registrar, f"{path}.attestation_ref"
    )
    attestation = _object(
        attestation,
        f"{path}.attestation_ref document",
        {
            "schema_version",
            "attestation_id",
            "experiment_id",
            "case_id",
            "arm",
            "assignment_index",
            "observed_at",
            "observed_binding",
            "native_system_contract_ref",
            "execution_authorization_ref",
            "version_observation_ref",
            "capture_ref",
            "prompt_ref",
            "output_ref",
        },
    )
    attestation_identity = copy.deepcopy(dict(attestation))
    attestation_identity.pop("attestation_id")
    if attestation["attestation_id"] != "attestation-" + sha256_hex(
        canonical_json(attestation_identity)
    ):
        _fail(
            f"{path}.attestation_ref document.attestation_id", "is not content-derived"
        )
    expected_attestation = {
        "schema_version": "caplab-native-attempt-attestation/1",
        "experiment_id": experiment_id,
        "case_id": attempt["case_id"],
        "arm": attempt["arm"],
        "assignment_index": attempt["assignment_index"],
        "observed_binding": binding,
        "native_system_contract_ref": manifest["native_system_contract_ref"],
        "execution_authorization_ref": execution_authorization_ref,
        "prompt_ref": attempt["prompt_ref"],
        "output_ref": attempt["output_ref"],
    }
    for field, expected in expected_attestation.items():
        if canonical_json(attestation[field]) != canonical_json(expected):
            _fail(
                f"{path}.attestation_ref document.{field}",
                "does not match prepared execution",
            )
    attested_at = _validate_timestamp(
        attestation["observed_at"], f"{path}.attestation_ref document.observed_at"
    )
    if attested_at > review_observed_at:
        _fail(
            f"{path}.attestation_ref document.observed_at",
            "is later than execution observation",
        )

    _validate_content_ref(
        attestation["capture_ref"],
        f"{path}.attestation_ref document.capture_ref",
        kind="native-attempt-capture",
        schema="caplab-native-attempt-capture/1",
    )
    _validate_content_ref(
        attestation["version_observation_ref"],
        f"{path}.attestation_ref document.version_observation_ref",
        kind="native-version-observation",
        schema="caplab-native-version-observation/1",
    )
    capture = _parse_canonical_json_ref(
        attestation["capture_ref"], registrar, f"{path}.capture_ref"
    )
    capture = _object(
        capture,
        f"{path}.capture_ref document",
        {
            "schema_version",
            "capture_id",
            "execution_authorization_ref",
            "experiment_id",
            "case_id",
            "arm",
            "assignment_index",
            "binding_id",
            "observed_binding",
            "started_at",
            "completed_at",
            "command_ref",
            "version_observation_ref",
            "prompt_ref",
            "stdin_ref",
            "stdout_ref",
            "stdout_complete",
            "stderr_ref",
            "stderr_complete",
            "output_ref",
            "native_invoked",
            "exit_code",
            "termination",
        },
    )
    capture_identity = copy.deepcopy(dict(capture))
    capture_identity.pop("capture_id")
    if capture["capture_id"] != "capture-" + sha256_hex(
        canonical_json(capture_identity)
    ):
        _fail(f"{path}.capture_ref document.capture_id", "is not content-derived")
    expected_capture = {
        "schema_version": "caplab-native-attempt-capture/1",
        "execution_authorization_ref": execution_authorization_ref,
        "experiment_id": experiment_id,
        "case_id": attempt["case_id"],
        "arm": attempt["arm"],
        "assignment_index": attempt["assignment_index"],
        "binding_id": binding["binding_id"],
        "observed_binding": binding,
        "command_ref": binding["harness"]["command_ref"],
        "version_observation_ref": attestation["version_observation_ref"],
        "prompt_ref": attempt["prompt_ref"],
        "stdout_ref": output["raw_stdout_ref"],
        "output_ref": attempt["output_ref"],
    }
    for field, expected in expected_capture.items():
        if canonical_json(capture[field]) != canonical_json(expected):
            _fail(
                f"{path}.capture_ref document.{field}",
                "does not match prepared execution",
            )
    for field in ("stdout_complete", "stderr_complete", "native_invoked"):
        if not isinstance(capture[field], bool):
            _fail(f"{path}.capture_ref document.{field}", "must be boolean")
    for field, kind in (
        ("stdin_ref", "native-process-stdin"),
        ("stdout_ref", "native-process-stdout"),
        ("stderr_ref", "native-process-stderr"),
    ):
        _validate_content_ref(
            capture[field],
            f"{path}.capture.{field}",
            kind=kind,
            schema="caplab-native-process-stream/1",
        )
    if _resolve_ref(
        capture["stdin_ref"], registrar, f"{path}.capture.stdin_ref"
    ) != canonical_json(native_input):
        _fail(f"{path}.capture.stdin_ref", "does not equal blinded input bytes")
    _resolve_ref(capture["stdout_ref"], registrar, f"{path}.capture.stdout_ref")
    _resolve_ref(capture["stderr_ref"], registrar, f"{path}.capture.stderr_ref")

    version = _parse_canonical_json_ref(
        capture["version_observation_ref"],
        registrar,
        f"{path}.version_observation_ref",
    )
    version = _object(
        version,
        f"{path}.version_observation_ref document",
        {
            "schema_version",
            "observation_id",
            "execution_authorization_ref",
            "experiment_id",
            "binding_id",
            "expected_version_probe_ref",
            "command_ref",
            "started_at",
            "completed_at",
            "stdout_ref",
            "stdout_complete",
            "stderr_ref",
            "stderr_complete",
            "exit_code",
            "termination",
            "matches_expected",
        },
    )
    version_identity = copy.deepcopy(dict(version))
    version_identity.pop("observation_id")
    if version["observation_id"] != "version-observation-" + sha256_hex(
        canonical_json(version_identity)
    ):
        _fail(
            f"{path}.version_observation_ref document.observation_id",
            "is not content-derived",
        )
    probe = _parse_canonical_json_ref(
        binding["harness"]["version_probe_ref"],
        registrar,
        f"{path}.expected_version_probe_ref",
    )
    expected_version = {
        "schema_version": "caplab-native-version-observation/1",
        "execution_authorization_ref": execution_authorization_ref,
        "experiment_id": experiment_id,
        "binding_id": binding["binding_id"],
        "expected_version_probe_ref": binding["harness"]["version_probe_ref"],
        "command_ref": probe["command_ref"],
    }
    for field, expected in expected_version.items():
        if canonical_json(version[field]) != canonical_json(expected):
            _fail(
                f"{path}.version_observation_ref document.{field}",
                "does not match Binding probe",
            )
    for field in ("stdout_complete", "stderr_complete", "matches_expected"):
        if not isinstance(version[field], bool):
            _fail(f"{path}.version.{field}", "must be boolean")
    if version["termination"] not in {
        "exited",
        "spawn-failure",
        "timeout",
        "stdout-limit",
        "stderr-limit",
        "authorization-expired",
    }:
        _fail(f"{path}.version.termination", "is unsupported")
    if version["exit_code"] is not None:
        _integer(version["exit_code"], f"{path}.version.exit_code")
    for field, kind in (
        ("stdout_ref", "native-process-stdout"),
        ("stderr_ref", "native-process-stderr"),
    ):
        _validate_content_ref(
            version[field],
            f"{path}.version.{field}",
            kind=kind,
            schema="caplab-native-process-stream/1",
        )
    version_stdout = _resolve_ref(
        version["stdout_ref"], registrar, f"{path}.version.stdout_ref"
    )
    version_stderr = _resolve_ref(
        version["stderr_ref"], registrar, f"{path}.version.stderr_ref"
    )
    expected_match = (
        version["termination"] == "exited"
        and version["exit_code"] == probe["exit_code"] == 0
        and version["stdout_complete"] is True
        and version["stderr_complete"] is True
        and version_stdout
        == _resolve_ref(
            probe["stdout_ref"], registrar, f"{path}.expected_version_stdout"
        )
        and version_stderr
        == _resolve_ref(
            probe["stderr_ref"], registrar, f"{path}.expected_version_stderr"
        )
    )
    if version["matches_expected"] is not expected_match:
        _fail(
            f"{path}.version_observation_ref document.matches_expected",
            "does not match probe bytes",
        )
    if capture["native_invoked"] and not expected_match:
        _fail(f"{path}.capture.native_invoked", "cannot follow version drift")

    version_started_at = _validate_timestamp(
        version["started_at"], f"{path}.version.started_at"
    )
    version_completed_at = _validate_timestamp(
        version["completed_at"], f"{path}.version.completed_at"
    )
    if version_started_at > version_completed_at:
        _fail(f"{path}.version", "has an inverted interval")
    started_at = _validate_timestamp(
        capture["started_at"], f"{path}.capture.started_at"
    )
    completed_at = _validate_timestamp(
        capture["completed_at"], f"{path}.capture.completed_at"
    )
    if started_at > completed_at or completed_at != attested_at:
        _fail(f"{path}.capture", "has an invalid attested interval")
    if started_at != version_started_at or version_completed_at > completed_at:
        _fail(f"{path}.capture", "does not contain the version-probe interval")
    _validate_execution_authorization(
        execution_authorization_ref, manifest, registrar, observed_at=started_at
    )
    exit_code = capture["exit_code"]
    if exit_code is not None:
        _integer(exit_code, f"{path}.capture.exit_code")
    termination = capture["termination"]
    if termination not in {
        "exited",
        "preflight-refused",
        "spawn-failure",
        "timeout",
        "stdout-limit",
        "stderr-limit",
        "authorization-expired",
    }:
        _fail(f"{path}.capture.termination", "is unsupported")
    if termination != "authorization-expired":
        _validate_execution_authorization(
            execution_authorization_ref,
            manifest,
            registrar,
            observed_at=completed_at,
        )
    if attempt["disposition"] == "complete":
        valid = (
            capture["native_invoked"]
            and termination == "exited"
            and exit_code == 0
            and capture["stdout_complete"]
            and capture["stderr_complete"]
            and output["parse_status"] == "valid"
        )
    elif attempt["disposition"] == "subject-failure":
        valid = (
            capture["native_invoked"]
            and termination == "exited"
            and exit_code == 0
            and output["parse_status"] == "invalid"
            and attempt["verdict"] == "invalid"
        )
    else:
        valid = (
            output["parse_status"] == "invalid"
            and attempt["verdict"] == "invalid"
            and not (
                capture["native_invoked"] and termination == "exited" and exit_code == 0
            )
        )
    if not valid:
        _fail(f"{path}.capture", "contradicts attempt disposition")
    if termination == "stdout-limit" and capture["stdout_complete"]:
        _fail(f"{path}.capture.stdout_complete", "contradicts stdout-limit")
    if termination == "stderr-limit" and capture["stderr_complete"]:
        _fail(f"{path}.capture.stderr_complete", "contradicts stderr-limit")
    if termination in {"preflight-refused", "authorization-expired"} and (
        capture["native_invoked"] or exit_code is not None
    ):
        _fail(f"{path}.capture", "contradicts pre-invocation refusal")
    return started_at, completed_at


def _metric(
    numerator: int,
    denominator: int,
    basis_ids: list[str],
    case_selection_ref: Mapping[str, Any],
) -> dict[str, JsonValue]:
    if denominator < 1:
        raise AssertionError("metric denominators must be positive")
    divisor = math.gcd(abs(numerator), denominator)
    return {
        "value": {
            "numerator": numerator // divisor,
            "denominator": denominator // divisor,
        },
        "basis_ids": list(basis_ids),
        "case_selection_ref": copy.deepcopy(dict(case_selection_ref)),
    }


def score(
    manifest: Mapping[str, Any],
    reviews: Mapping[str, Any],
    registrar: ArtifactRegistrar,
) -> dict[str, JsonValue]:
    """Derive one qualification Measurement from captured native reviews."""

    try:
        producer_version, producer_commit, producer_package_sha256 = producer_identity()
    except ProducerIdentityError as error:
        raise RevbenchContractError(
            f"producer identity unavailable: {error}"
        ) from error

    validated_manifest = _validate_manifest(manifest, registrar)
    validated_reviews = _validate_reviews(reviews, validated_manifest)
    _validate_execution_authorization(
        validated_reviews["execution_authorization_ref"],
        validated_manifest,
        registrar,
        observed_at=validated_reviews["started_at"],
    )
    _resolve_all_refs(validated_reviews, registrar, "reviews")
    _validate_basis_authorizations(
        validated_manifest,
        registrar,
        observed_at=validated_reviews["observed_at"],
    )

    attempts: dict[tuple[str, str], Mapping[str, Any]] = {}
    capture_intervals: dict[tuple[str, str], tuple[str, str]] = {}
    conforming = 0
    for index, attempt in enumerate(validated_reviews["attempts"]):
        path = f"reviews.attempts[{index}]"
        # These four evidence objects are independently resolved even though a
        # caller supplied syntactically complete references.
        _resolve_ref(attempt["attempt_ref"], registrar, f"{path}.attempt_ref")
        _resolve_ref(attempt["prompt_ref"], registrar, f"{path}.prompt_ref")
        _resolve_ref(attempt["output_ref"], registrar, f"{path}.output_ref")
        capture_intervals[(attempt["case_id"], attempt["arm"])] = (
            _verify_execution_attempt_evidence(
                attempt,
                validated_manifest,
                validated_reviews["execution_authorization_ref"],
                validated_reviews["observed_at"],
                registrar,
                path,
            )
        )
        attempts[(attempt["case_id"], attempt["arm"])] = attempt
        if attempt["disposition"] == "complete" and (
            (attempt["verdict"] == "clean" and not attempt["anchors"])
            or (attempt["verdict"] == "defect" and bool(attempt["anchors"]))
        ):
            conforming += 1
    execution_identity = copy.deepcopy(dict(validated_reviews))
    execution_identity.pop("execution_id")
    expected_execution_id = "execution-" + sha256_hex(
        canonical_json(execution_identity)
    )
    if validated_reviews["execution_id"] != expected_execution_id:
        _fail("reviews.execution_id", "is not content-derived")
    _verified_registration(
        registrar,
        copy.deepcopy(dict(validated_reviews)),
        kind="revbench-execution",
        schema="caplab-revbench-reviews/1",
        registration_id=validated_reviews["execution_id"],
    )
    for case in validated_manifest["cases"]:
        first_arm, second_arm = case["assignment_order"]
        first = capture_intervals.get((case["case_id"], first_arm))
        second = capture_intervals.get((case["case_id"], second_arm))
        if first is not None and second is not None and first[1] > second[0]:
            _fail(
                f"reviews case {case['case_id']}",
                "capture times contradict manifest assignment order",
            )
    planned = len(validated_manifest["cases"]) * 2
    attempted = len(validated_reviews["attempts"])
    missing = planned - attempted
    usable = 0
    excluded = 0
    subject_failures = 0
    infrastructure_failures = 0
    usable_pairs = 0
    caught_mutants = 0
    false_alarms = 0
    exact_anchor_calls = 0
    mutant_defect_calls = 0
    excluded_cases: list[dict[str, JsonValue]] = []

    for case in validated_manifest["cases"]:
        pair = {
            arm: attempts.get((case["case_id"], arm)) for arm in ("control", "mutant")
        }
        eligible: dict[str, bool] = {}
        reasons: list[str] = []
        for arm, attempt in pair.items():
            if attempt is None:
                eligible[arm] = False
                reasons.append(f"missing-{arm}")
            elif attempt["disposition"] == "subject-failure":
                eligible[arm] = False
                subject_failures += 1
                reasons.append(f"subject-failure-{arm}")
            elif attempt["disposition"] == "infrastructure-failure":
                eligible[arm] = False
                infrastructure_failures += 1
                reasons.append(f"infrastructure-failure-{arm}")
            elif attempt["verdict"] == "invalid":
                eligible[arm] = False
                excluded += 1
                reasons.append(f"invalid-{arm}")
            else:
                eligible[arm] = True
        if all(eligible.values()):
            usable += 2
            usable_pairs += 1
            control = pair["control"]
            mutant = pair["mutant"]
            if control["verdict"] == "defect":
                false_alarms += 1
            if mutant["verdict"] == "defect":
                mutant_defect_calls += 1
                if mutant["anchors"] == [case["defect_anchor"]]:
                    exact_anchor_calls += 1
                    caught_mutants += 1
        else:
            # A valid arm whose partner is absent or unusable remains visible as
            # excluded rather than silently disappearing from the partition.
            excluded += sum(1 for arm in ("control", "mutant") if eligible[arm])
            excluded_cases.append(
                {"case_id": case["case_id"], "reasons": sorted(reasons)}
            )

    sample_flow: dict[str, JsonValue] = {
        "planned": planned,
        "attempted": attempted,
        "usable": usable,
        "excluded": excluded,
        "missing": missing,
        "subject_failures": subject_failures,
        "infrastructure_failures": infrastructure_failures,
    }
    if attempted + missing != planned:
        raise AssertionError("attempt partition is inconsistent")
    if usable + excluded + subject_failures + infrastructure_failures != attempted:
        raise AssertionError("attempt disposition partition is inconsistent")

    experiment_id = validated_manifest["experiment_id"]
    truth_document: JsonValue = {
        "schema_version": "caplab-revbench-truth-basis/1",
        "experiment_id": experiment_id,
        "distribution": "json-integer-minimum/1",
        "claim_boundary": "only the declared integer-minimum invariant",
        "cases": [
            {
                "case_id": case["case_id"],
                "control_sha256": case["control"]["sha256"],
                "mutant_sha256": case["mutant"]["sha256"],
                "pointer": case["oracle"]["pointer"],
                "minimum": case["oracle"]["minimum"],
                "control_result": True,
                "mutant_result": False,
            }
            for case in validated_manifest["cases"]
        ],
    }
    selection_document: JsonValue = {
        "schema_version": "caplab-revbench-case-selection-basis/1",
        "experiment_id": experiment_id,
        "case_selection_ref": copy.deepcopy(validated_manifest["case_selection_ref"]),
        "planned_case_ids": [case["case_id"] for case in validated_manifest["cases"]],
        "usable_case_ids": [
            case["case_id"]
            for case in validated_manifest["cases"]
            if all(
                (attempt := attempts.get((case["case_id"], arm))) is not None
                and attempt["disposition"] == "complete"
                and attempt["verdict"] != "invalid"
                for arm in ("control", "mutant")
            )
        ],
        "excluded_cases": excluded_cases,
    }
    derivation_document: JsonValue = {
        "schema_version": "caplab-revbench-metric-derivation-basis/1",
        "experiment_id": experiment_id,
        "observed_at": validated_reviews["observed_at"],
        "sample_flow": sample_flow,
        "counts": {
            "usable_pairs": usable_pairs,
            "caught_mutants": caught_mutants,
            "false_alarm_controls": false_alarms,
            "exact_anchor_calls": exact_anchor_calls,
            "mutant_defect_calls": mutant_defect_calls,
            "conforming_attempts": conforming,
        },
        "definitions": {
            "catch_rate": "caught mutants / usable pairs",
            "false_alarm_rate": "false-alarm controls / usable pairs",
            "discrimination": "(caught mutants - false-alarm controls) / usable pairs",
            "anchor_hit_rate": "exact-anchor mutant calls / mutant defect calls",
            "conformance_rate": "conforming attempts / planned attempts",
        },
    }
    evidence_refs = {
        "truth": _verified_registration(
            registrar,
            truth_document,
            kind="mechanical-oracle-result",
            schema="caplab-revbench-truth-basis/1",
            registration_id=f"revbench-truth-{experiment_id}",
        ),
        "case-selection": _verified_registration(
            registrar,
            selection_document,
            kind="mechanical-oracle-result",
            schema="caplab-revbench-case-selection-basis/1",
            registration_id=f"revbench-selection-{experiment_id}",
        ),
        "metric-derivation": _verified_registration(
            registrar,
            derivation_document,
            kind="mechanical-oracle-result",
            schema="caplab-revbench-metric-derivation-basis/1",
            registration_id=f"revbench-metrics-{experiment_id}-{validated_reviews['observed_at']}",
        ),
    }
    bases = [
        _basis(
            role=public_role,
            evidence_ref=evidence_refs[public_role],
            authorization_ref=validated_manifest["basis_authorization_refs"][key],
        )
        for key, public_role in (
            ("truth", "truth"),
            ("case_selection", "case-selection"),
            ("metric_derivation", "metric-derivation"),
        )
    ]
    bases.sort(key=canonical_json)
    basis_ids = sorted(basis["basis_id"] for basis in bases)
    metrics: dict[str, JsonValue] = {
        "conformance_rate": _metric(
            conforming,
            planned,
            basis_ids,
            validated_manifest["case_selection_ref"],
        )
    }
    if usable_pairs:
        metrics.update(
            {
                "catch_rate": _metric(
                    caught_mutants,
                    usable_pairs,
                    basis_ids,
                    validated_manifest["case_selection_ref"],
                ),
                "discrimination": _metric(
                    caught_mutants - false_alarms,
                    usable_pairs,
                    basis_ids,
                    validated_manifest["case_selection_ref"],
                ),
                "false_alarm_rate": _metric(
                    false_alarms,
                    usable_pairs,
                    basis_ids,
                    validated_manifest["case_selection_ref"],
                ),
            }
        )
        if mutant_defect_calls:
            metrics["anchor_hit_rate"] = _metric(
                exact_anchor_calls,
                mutant_defect_calls,
                basis_ids,
                validated_manifest["case_selection_ref"],
            )
    run_refs = sorted(
        (
            copy.deepcopy(attempt["attempt_ref"])
            for attempt in validated_reviews["attempts"]
        ),
        key=canonical_json,
    )
    bundle_document: JsonValue = {
        "schema_version": "caplab-revbench-evidence-bundle/1",
        "experiment_id": experiment_id,
        "run_refs": run_refs,
    }
    bundle_ref = _verified_registration(
        registrar,
        bundle_document,
        kind="evidence-bundle",
        schema="caplab-revbench-evidence-bundle/1",
        registration_id=f"revbench-bundle-{experiment_id}-{validated_reviews['observed_at']}",
    )
    if infrastructure_failures:
        disposition = "infrastructure-failure"
    elif any(
        attempt["disposition"] == "complete" and attempt["verdict"] == "invalid"
        for attempt in validated_reviews["attempts"]
    ):
        disposition = "invalid"
    elif missing or subject_failures or excluded:
        disposition = "incomplete"
    else:
        disposition = "complete"
    identity: dict[str, JsonValue] = {
        "schema_version": "caplab-measurement/1",
        "observed_at": validated_reviews["observed_at"],
        "binding": copy.deepcopy(validated_manifest["binding"]),
        "capability": copy.deepcopy(validated_manifest["capability"]),
        "experiment": {"family": "revbench", "version": "1"},
        "protocol": copy.deepcopy(validated_manifest["protocol"]),
        "corpus": copy.deepcopy(validated_manifest["corpus"]),
        "evidence_basis": bases,
        "disposition": disposition,
        "sample_flow": sample_flow,
        "metrics": metrics,
        "evidence": {"bundle_ref": bundle_ref, "run_refs": run_refs},
        "covariates": [],
        "provenance": {
            "caplab_version": producer_version,
            "caplab_commit": producer_commit,
            "caplab_package_sha256": producer_package_sha256,
            "source_refs": copy.deepcopy(
                validated_manifest["provenance"]["source_refs"]
            ),
        },
    }
    measurement_id = "meas-" + sha256_hex(canonical_json(identity))
    measurement = {
        "schema_version": identity["schema_version"],
        "measurement_id": measurement_id,
        **{key: value for key, value in identity.items() if key != "schema_version"},
    }
    try:
        return validate_qualification_measurement(measurement, registrar)
    except QualificationContractError as error:
        raise RevbenchContractError(
            f"derived measurement violates the qualification contract: {error}"
        ) from error
