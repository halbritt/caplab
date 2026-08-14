"""Strict, offline revbench preparation and scoring.

The public functions in this module consume untrusted JSON-shaped values.  Type
annotations document the internal contract; every value-level invariant is
also checked at runtime before evidence can affect a result.
"""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any, Protocol, TypeAlias, runtime_checkable

from caplab.runtime.canonical import CanonicalizationError, canonical_json, sha256_hex


JsonValue: TypeAlias = (
    None | bool | int | str | list["JsonValue"] | dict[str, "JsonValue"]
)
ContentRef: TypeAlias = dict[str, JsonValue]


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
    provenance = _object(
        value, path, {"caplab_version", "caplab_commit", "source_refs"}
    )
    _string(provenance["caplab_version"], f"{path}.caplab_version")
    _string(provenance["caplab_commit"], f"{path}.caplab_commit", pattern=_COMMIT)
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
        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise RevbenchContractError(f"{path}: is not a real UTC timestamp") from error
    return timestamp


def _validate_reviews(reviews: Any, manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    reviews = _object(
        reviews,
        "reviews",
        {"schema_version", "experiment_id", "observed_at", "attempts"},
    )
    _const(
        reviews["schema_version"], "caplab-revbench-reviews/1", "reviews.schema_version"
    )
    _string(reviews["experiment_id"], "reviews.experiment_id", pattern=_EXPERIMENT_ID)
    if reviews["experiment_id"] != manifest["experiment_id"]:
        _fail("reviews.experiment_id", "does not match the manifest experiment")
    _validate_timestamp(reviews["observed_at"], "reviews.observed_at")
    attempts = _array(reviews["attempts"], "reviews.attempts", minimum=1)
    known_cases = {case["case_id"] for case in manifest["cases"]}
    seen: set[tuple[str, str]] = set()
    seen_attempt_digests: set[str] = set()
    for index, value in enumerate(attempts):
        path = f"reviews.attempts[{index}]"
        attempt = _object(
            value,
            path,
            {
                "case_id",
                "arm",
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
        )
        _validate_content_ref(attempt["prompt_ref"], f"{path}.prompt_ref")
        _validate_content_ref(attempt["output_ref"], f"{path}.output_ref")
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
    for name in ("population_ref", "authorization_ref"):
        _validate_content_ref(selection[name], f"case_selection_ref document.{name}")
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
        _validate_content_ref(
            authorization["authority_source_ref"],
            f"{path} document.authority_source_ref",
            kind="decision-record",
        )
        _string(authorization["authorized_by"], f"{path} document.authorized_by")
        _string(
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


def _verify_attempt_evidence(
    attempt: Mapping[str, Any],
    experiment_id: str,
    manifest_binding: Mapping[str, Any],
    review_observed_at: str,
    registrar: ArtifactRegistrar,
    path: str,
) -> None:
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
    _string(envelope["attempt_id"], f"{path}.attempt_ref document.attempt_id")
    envelope_identity = copy.deepcopy(dict(envelope))
    envelope_identity.pop("attempt_id")
    expected_attempt_id = "attempt-" + sha256_hex(canonical_json(envelope_identity))
    if envelope["attempt_id"] != expected_attempt_id:
        _fail(f"{path}.attempt_ref document.attempt_id", "is not content-derived")
    _validate_provenance(
        envelope["provenance"], f"{path}.attempt_ref document.provenance"
    )
    review_projection = copy.deepcopy(dict(attempt))
    review_projection.pop("attempt_ref")
    envelope_projection = copy.deepcopy(dict(envelope))
    for field in ("schema_version", "attempt_id", "experiment_id", "provenance"):
        envelope_projection.pop(field)
    if canonical_json(envelope_projection) != canonical_json(review_projection):
        _fail(
            path,
            "review attempt does not equal its registered attempt envelope projection",
        )
    if envelope["experiment_id"] != experiment_id:
        _fail(
            f"{path}.attempt_ref document.experiment_id", "does not match the manifest"
        )
    _resolve_all_refs(envelope, registrar, f"{path}.attempt_ref document")

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
            "observed_at",
            "observed_binding",
            "native_system_contract_ref",
            "capture_ref",
            "prompt_ref",
            "output_ref",
        },
    )
    _const(
        attestation["schema_version"],
        "caplab-native-attempt-attestation/1",
        f"{path}.attestation_ref document.schema_version",
    )
    _string(
        attestation["attestation_id"], f"{path}.attestation_ref document.attestation_id"
    )
    attestation_identity = copy.deepcopy(dict(attestation))
    attestation_identity.pop("attestation_id")
    expected_attestation_id = "attestation-" + sha256_hex(
        canonical_json(attestation_identity)
    )
    if attestation["attestation_id"] != expected_attestation_id:
        _fail(
            f"{path}.attestation_ref document.attestation_id", "is not content-derived"
        )
    attested_at = _validate_timestamp(
        attestation["observed_at"], f"{path}.attestation_ref document.observed_at"
    )
    if attested_at > review_observed_at:
        _fail(
            f"{path}.attestation_ref document.observed_at",
            "is later than the review observation",
        )
    try:
        _validate_binding(
            attestation["observed_binding"], f"{path}.attestation.observed_binding"
        )
    except RevbenchContractError as error:
        raise RevbenchContractError(
            f"{path}: attested observed Binding is invalid"
        ) from error
    if canonical_json(attestation["observed_binding"]) != canonical_json(
        attempt["observed_binding"]
    ):
        _fail(
            path,
            "attested observed Binding does not equal the captured observed Binding",
        )
    if canonical_json(attestation["observed_binding"]) != canonical_json(
        manifest_binding
    ):
        _fail(path, "attested observed Binding does not equal the manifest Binding")
    for field in ("experiment_id", "case_id", "arm", "prompt_ref", "output_ref"):
        expected = experiment_id if field == "experiment_id" else attempt[field]
        if canonical_json(attestation[field]) != canonical_json(expected):
            _fail(
                f"{path}.attestation_ref document.{field}",
                "does not match the review attempt",
            )
    _validate_content_ref(
        attestation["native_system_contract_ref"],
        f"{path}.attestation_ref document.native_system_contract_ref",
        kind="native-agent-systems-contract",
        schema="caplab.native-agent-systems/v1",
    )
    _validate_content_ref(
        attestation["capture_ref"],
        f"{path}.attestation_ref document.capture_ref",
        kind="native-attempt-capture",
    )
    _resolve_all_refs(attestation, registrar, f"{path}.attestation_ref document")


def _metric(
    numerator: int,
    denominator: int,
    basis_ids: list[str],
    case_selection_ref: Mapping[str, Any],
) -> dict[str, JsonValue]:
    if denominator < 1:
        raise AssertionError("metric denominators must be positive")
    return {
        "value": {"numerator": numerator, "denominator": denominator},
        "basis_ids": list(basis_ids),
        "case_selection_ref": copy.deepcopy(dict(case_selection_ref)),
    }


def score(
    manifest: Mapping[str, Any],
    reviews: Mapping[str, Any],
    registrar: ArtifactRegistrar,
) -> dict[str, JsonValue]:
    """Derive one qualification Measurement from captured native reviews."""

    validated_manifest = _validate_manifest(manifest, registrar)
    validated_reviews = _validate_reviews(reviews, validated_manifest)
    _resolve_all_refs(validated_reviews, registrar, "reviews")
    _validate_basis_authorizations(
        validated_manifest,
        registrar,
        observed_at=validated_reviews["observed_at"],
    )

    attempts: dict[tuple[str, str], Mapping[str, Any]] = {}
    conforming = 0
    for index, attempt in enumerate(validated_reviews["attempts"]):
        path = f"reviews.attempts[{index}]"
        # These four evidence objects are independently resolved even though a
        # caller supplied syntactically complete references.
        _resolve_ref(attempt["attempt_ref"], registrar, f"{path}.attempt_ref")
        _resolve_ref(attempt["prompt_ref"], registrar, f"{path}.prompt_ref")
        _resolve_ref(attempt["output_ref"], registrar, f"{path}.output_ref")
        _verify_attempt_evidence(
            attempt,
            validated_manifest["experiment_id"],
            validated_manifest["binding"],
            validated_reviews["observed_at"],
            registrar,
            path,
        )
        attempts[(attempt["case_id"], attempt["arm"])] = attempt
        if attempt["disposition"] == "complete" and (
            (attempt["verdict"] == "clean" and not attempt["anchors"])
            or (attempt["verdict"] == "defect" and bool(attempt["anchors"]))
        ):
            conforming += 1
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
        anchor_denominator = (
            mutant_defect_calls if mutant_defect_calls else usable_pairs
        )
        metrics.update(
            {
                "anchor_hit_rate": _metric(
                    exact_anchor_calls,
                    anchor_denominator,
                    basis_ids,
                    validated_manifest["case_selection_ref"],
                ),
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
        "provenance": copy.deepcopy(validated_manifest["provenance"]),
    }
    measurement_id = "meas-" + sha256_hex(canonical_json(identity))
    return {
        "schema_version": identity["schema_version"],
        "measurement_id": measurement_id,
        **{key: value for key, value in identity.items() if key != "schema_version"},
    }
