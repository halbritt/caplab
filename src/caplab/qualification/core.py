"""Deterministic qualification records and policy evaluation.

The public functions in this module form the semantic boundary behind the
versioned JSON contracts.  JSON Schema remains useful for interchange, but it
cannot establish content identity, evidence registration, lineage, exact
rational evaluation, or authority scope.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Protocol, runtime_checkable

from caplab.runtime.canonical import CanonicalizationError, canonical_json, sha256_hex

from .errors import QualificationContractError


_HEX = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_REGISTRATION = re.compile(r"^[a-z][a-z0-9-]{2,127}:[A-Za-z0-9._:-]{1,255}$")
_CLAIM_ID = re.compile(r"^claim-[0-9a-f]{64}$")
_NAME = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_SAFE_PATH = re.compile(r"^[A-Za-z0-9._/-]+$")


@runtime_checkable
class EvidenceResolver(Protocol):
    """Registration-aware adapter for immutable local evidence.

    Implementations receive the complete content reference and must refuse a
    reference whose ``registration_ref`` is not present in their authoritative
    registry.  The core independently verifies the returned bytes against the
    reference's locator, byte count, and digest.
    """

    def resolve(self, ref: Mapping[str, Any]) -> bytes:
        """Return the registered immutable bytes named by *ref*."""


def _error(path: str, message: str) -> QualificationContractError:
    return QualificationContractError(f"{path}: {message}")


def _owned(value: Mapping[str, Any], path: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise _error(path, "must be an object")
    try:
        encoded = canonical_json(value)
        owned = json.loads(encoded)
    except (CanonicalizationError, UnicodeError, json.JSONDecodeError) as error:
        raise _error(path, str(error)) from error
    if not isinstance(owned, dict):  # defensive: Mapping encoded as an object
        raise _error(path, "must be an object")
    return owned


def _exact_object(value: Any, path: str, fields: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error(path, "must be an object")
    actual = set(value)
    if actual != fields:
        missing = sorted(fields - actual)
        unknown = sorted(actual - fields)
        details: list[str] = []
        if missing:
            details.append(f"missing {missing}")
        if unknown:
            details.append(f"unknown {unknown}")
        raise _error(path, "; ".join(details))
    return value


def _string(value: Any, path: str, *, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise _error(path, "must be a non-empty string")
    if unicodedata.normalize("NFC", value) != value:
        raise _error(path, "must be NFC-normalized")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise _error(path, "has invalid syntax")
    return value


def _integer(value: Any, path: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise _error(path, "must be an integer")
    if minimum is not None and value < minimum:
        raise _error(path, f"must be at least {minimum}")
    return value


def _enum(value: Any, path: str, choices: set[str]) -> str:
    if not isinstance(value, str) or value not in choices:
        raise _error(path, f"must be one of {sorted(choices)}")
    return value


def _timestamp(value: Any, path: str) -> datetime:
    text = _string(value, path, pattern=_UTC)
    try:
        parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise _error(path, "must be a valid UTC timestamp") from error
    return parsed


def _canonical_key(value: Any) -> bytes:
    try:
        return canonical_json(value)
    except CanonicalizationError as error:
        raise QualificationContractError(str(error)) from error


def _set_array(value: Any, path: str, *, minimum: int = 0) -> list[Any]:
    if not isinstance(value, list):
        raise _error(path, "must be an array")
    if len(value) < minimum:
        raise _error(path, f"must contain at least {minimum} item(s)")
    keys = [_canonical_key(item) for item in value]
    if keys != sorted(keys):
        raise _error(path, "must be in canonical order")
    if len(keys) != len(set(keys)):
        raise _error(path, "must not contain duplicates")
    return value


def _ratio(value: Any, path: str, *, rate: bool = False) -> Fraction:
    ratio = _exact_object(value, path, {"numerator", "denominator"})
    numerator = _integer(ratio["numerator"], f"{path}.numerator")
    denominator = _integer(ratio["denominator"], f"{path}.denominator", minimum=1)
    if math.gcd(abs(numerator), denominator) != 1:
        raise _error(path, "must be a reduced rational")
    if rate and not (0 <= numerator <= denominator):
        raise _error(path, "rate must be between zero and one")
    return Fraction(numerator, denominator)


def derive_content_id(
    document: Mapping[str, Any], id_field: str, prefix: str
) -> str:
    """Derive an identity after omitting the document's identity field."""

    if not isinstance(document, Mapping):
        raise QualificationContractError("document must be an object")
    if not isinstance(id_field, str) or not id_field:
        raise QualificationContractError("id_field must be a non-empty string")
    if not isinstance(prefix, str) or not prefix:
        raise QualificationContractError("prefix must be a non-empty string")
    try:
        payload = {key: value for key, value in document.items() if key != id_field}
        return prefix + sha256_hex(canonical_json(payload))
    except CanonicalizationError as error:
        raise QualificationContractError(str(error)) from error


_CONTENT_FIELDS = {
    "kind",
    "schema",
    "media_type",
    "sha256",
    "byte_count",
    "locator",
    "registration_ref",
    "custody",
}


def _validate_content_ref(
    value: Any,
    resolver: EvidenceResolver,
    path: str,
    *,
    kind: str | None = None,
    schema: str | None = None,
) -> bytes:
    ref = _exact_object(value, path, _CONTENT_FIELDS)
    actual_kind = _string(ref["kind"], f"{path}.kind")
    actual_schema = _string(ref["schema"], f"{path}.schema")
    _string(ref["media_type"], f"{path}.media_type")
    digest = _string(ref["sha256"], f"{path}.sha256", pattern=_HEX)
    byte_count = _integer(ref["byte_count"], f"{path}.byte_count", minimum=0)
    expected_locator = f"objects/sha256/{digest[:2]}/{digest}"
    if ref["locator"] != expected_locator:
        raise _error(f"{path}.locator", "must be derived from sha256")
    _string(ref["registration_ref"], f"{path}.registration_ref", pattern=_REGISTRATION)
    custody = ref["custody"]
    if custody is not None:
        custody = _exact_object(
            custody,
            f"{path}.custody",
            {"repository", "commit", "path", "source_sha256"},
        )
        _string(custody["repository"], f"{path}.custody.repository")
        _string(custody["commit"], f"{path}.custody.commit", pattern=_COMMIT)
        custody_path = _string(custody["path"], f"{path}.custody.path")
        segments = custody_path.split("/")
        if (
            custody_path.startswith("/")
            or _SAFE_PATH.fullmatch(custody_path) is None
            or any(segment in {"", ".", ".."} for segment in segments)
        ):
            raise _error(f"{path}.custody.path", "must be a normalized repository-relative path")
        _string(custody["source_sha256"], f"{path}.custody.source_sha256", pattern=_HEX)
    if kind is not None and actual_kind != kind:
        raise _error(f"{path}.kind", f"must be {kind!r}")
    if schema is not None and actual_schema != schema:
        raise _error(f"{path}.schema", f"must be {schema!r}")
    if not isinstance(resolver, EvidenceResolver):
        raise _error(path, "resolver does not implement EvidenceResolver")
    try:
        payload = resolver.resolve(ref)
    except (KeyError, LookupError, OSError) as error:
        raise _error(path, f"registered evidence cannot be resolved: {error}") from error
    if not isinstance(payload, bytes):
        raise _error(path, "resolver must return bytes")
    if len(payload) != byte_count:
        raise _error(path, "resolved byte count does not match reference")
    if sha256_hex(payload) != digest:
        raise _error(path, "resolved digest does not match reference")
    if ref["media_type"] == "application/json":
        try:
            parsed = json.loads(payload.decode("utf-8"))
            if canonical_json(parsed) != payload:
                raise _error(path, "resolved JSON is not canonical")
        except (UnicodeError, json.JSONDecodeError, CanonicalizationError) as error:
            raise _error(path, "resolved JSON is invalid") from error
    return payload


def _resolved_json(
    value: Any,
    resolver: EvidenceResolver,
    path: str,
    *,
    kind: str | None = None,
    schema: str | None = None,
) -> dict[str, Any]:
    payload = _validate_content_ref(value, resolver, path, kind=kind, schema=schema)
    try:
        result = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise _error(path, "must resolve to a JSON object") from error
    if not isinstance(result, dict):
        raise _error(path, "must resolve to a JSON object")
    return result


def _validate_model(value: Any, resolver: EvidenceResolver, path: str) -> None:
    model = _exact_object(
        value,
        path,
        {"model_id", "revision", "weights_ref", "weights_unavailable_reason"},
    )
    _string(model["model_id"], f"{path}.model_id")
    _string(model["revision"], f"{path}.revision")
    weights = model["weights_ref"]
    reason = model["weights_unavailable_reason"]
    if weights is None:
        _string(reason, f"{path}.weights_unavailable_reason")
    else:
        if reason is not None:
            raise _error(f"{path}.weights_unavailable_reason", "must be null when weights_ref is present")
        _validate_content_ref(weights, resolver, f"{path}.weights_ref")


def _validate_provider(value: Any, resolver: EvidenceResolver, path: str) -> None:
    provider = _exact_object(
        value,
        path,
        {"kind", "identifier", "revision", "resolution", "observed_at", "route_ref"},
    )
    _enum(provider["kind"], f"{path}.kind", {"direct-provider", "proxy-provider", "local-serving", "other"})
    _string(provider["identifier"], f"{path}.identifier")
    _string(provider["revision"], f"{path}.revision")
    resolution = _enum(provider["resolution"], f"{path}.resolution", {"immutable", "observed-route"})
    if resolution == "immutable":
        if provider["observed_at"] is not None:
            raise _error(f"{path}.observed_at", "must be null for an immutable route")
    else:
        _timestamp(provider["observed_at"], f"{path}.observed_at")
    _validate_content_ref(provider["route_ref"], resolver, f"{path}.route_ref")


def _validate_version_probe(
    value: Any,
    resolver: EvidenceResolver,
    path: str,
    command_ref: dict[str, Any],
) -> None:
    probe = _resolved_json(value, resolver, path)
    probe = _exact_object(probe, f"{path} document", {"command_ref", "exit_code", "stdout_ref", "stderr_ref"})
    _validate_content_ref(probe["command_ref"], resolver, f"{path} document.command_ref")
    if _canonical_key(probe["command_ref"]) != _canonical_key(command_ref):
        raise _error(f"{path} document.command_ref", "does not match harness command_ref")
    exit_code = _integer(probe["exit_code"], f"{path} document.exit_code")
    if exit_code != 0:
        raise _error(f"{path} document.exit_code", "version probe must succeed")
    stdout = _validate_content_ref(
        probe["stdout_ref"], resolver, f"{path} document.stdout_ref"
    )
    stderr = _validate_content_ref(
        probe["stderr_ref"], resolver, f"{path} document.stderr_ref"
    )
    if not stdout and not stderr:
        raise _error(path, "version probe must capture a version response")


def _validate_harness(value: Any, resolver: EvidenceResolver, path: str) -> None:
    harness = _exact_object(
        value,
        path,
        {
            "harness_id",
            "harness_version",
            "executable_ref",
            "executable_unavailable_reason",
            "command_ref",
            "version_probe_ref",
        },
    )
    _string(harness["harness_id"], f"{path}.harness_id")
    _string(harness["harness_version"], f"{path}.harness_version")
    executable = harness["executable_ref"]
    reason = harness["executable_unavailable_reason"]
    if executable is None:
        _string(reason, f"{path}.executable_unavailable_reason")
    else:
        if reason is not None:
            raise _error(f"{path}.executable_unavailable_reason", "must be null when executable_ref is present")
        _validate_content_ref(executable, resolver, f"{path}.executable_ref")
    _validate_content_ref(harness["command_ref"], resolver, f"{path}.command_ref")
    _validate_version_probe(
        harness["version_probe_ref"],
        resolver,
        f"{path}.version_probe_ref",
        harness["command_ref"],
    )


def _validate_configuration(value: Any, resolver: EvidenceResolver, path: str) -> None:
    fields = {
        "inference_ref",
        "instructions_ref",
        "knowledge_ref",
        "tools_ref",
        "permissions_ref",
        "sandbox_ref",
        "runtime_ref",
    }
    configuration = _exact_object(value, path, fields)
    for field in sorted(fields):
        _validate_content_ref(configuration[field], resolver, f"{path}.{field}")


def validate_binding(
    document: Mapping[str, Any], resolver: EvidenceResolver
) -> dict[str, Any]:
    """Validate and return an owned canonical ``caplab-binding/1`` document."""

    binding = _owned(document, "binding")
    _exact_object(
        binding,
        "binding",
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
    if binding["schema_version"] != "caplab-binding/1":
        raise _error("binding.schema_version", "must be 'caplab-binding/1'")
    _string(binding["binding_id"], "binding.binding_id", pattern=re.compile(r"^bnd-[0-9a-f]{64}$"))
    _validate_model(binding["model"], resolver, "binding.model")
    _validate_provider(binding["provider_or_path"], resolver, "binding.provider_or_path")
    _validate_harness(binding["harness"], resolver, "binding.harness")
    _string(binding["reasoning_effort"], "binding.reasoning_effort")
    _validate_configuration(binding["configuration"], resolver, "binding.configuration")
    expected = derive_content_id(binding, "binding_id", "bnd-")
    if binding["binding_id"] != expected:
        raise _error("binding.binding_id", "does not match canonical binding content")
    return binding


def _validate_capability(
    value: Any, resolver: EvidenceResolver, path: str
) -> tuple[dict[str, Any], set[str] | None]:
    capability = _exact_object(
        value,
        path,
        {"name", "version", "role", "domain", "distribution", "card_ref"},
    )
    _string(capability["name"], f"{path}.name", pattern=_NAME)
    for field in ("version", "role", "domain", "distribution"):
        _string(capability[field], f"{path}.{field}")
    card_payload = _validate_content_ref(
        capability["card_ref"], resolver, f"{path}.card_ref", kind="capability-card"
    )
    if capability["card_ref"]["media_type"] != "application/json":
        return capability, None
    try:
        card = json.loads(card_payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise _error(f"{path}.card_ref", "JSON capability card cannot be decoded") from error
    if not isinstance(card, dict):
        raise _error(f"{path}.card_ref", "JSON capability card must be an object")
    declared = card.get("qualification_metrics")
    if declared is None:
        return capability, None
    metrics = _set_array(declared, f"{path}.card_ref document.qualification_metrics")
    inventory: set[str] = set()
    for index, metric in enumerate(metrics):
        inventory.add(_metric_name(metric, f"{path}.card_ref document.qualification_metrics[{index}]"))
    return capability, inventory


def _validate_experiment(value: Any, path: str) -> dict[str, Any]:
    experiment = _exact_object(value, path, {"family", "version"})
    _string(experiment["family"], f"{path}.family")
    _string(experiment["version"], f"{path}.version")
    return experiment


def _validate_provenance(value: Any, resolver: EvidenceResolver, path: str) -> None:
    provenance = _exact_object(value, path, {"caplab_version", "caplab_commit", "source_refs"})
    _string(provenance["caplab_version"], f"{path}.caplab_version")
    _string(provenance["caplab_commit"], f"{path}.caplab_commit", pattern=_COMMIT)
    refs = _set_array(provenance["source_refs"], f"{path}.source_refs")
    for index, ref in enumerate(refs):
        _validate_content_ref(ref, resolver, f"{path}.source_refs[{index}]")


def _metric_name(value: Any, path: str) -> str:
    name = _string(value, path, pattern=_NAME)
    tokens = re.split(r"[._-]", name)
    collapsed = "".join(tokens)
    if (
        "fate" in collapsed
        or "outcome" in collapsed
        or "admission" in collapsed
        or "providerverdict" in collapsed
        or "schedulerchoice" in collapsed
        or "backendrank" in collapsed
    ):
        raise _error(path, "reserved fate/outcome or routing metric names cannot qualify")
    return name


def _validate_basis_authorization(
    value: Any, resolver: EvidenceResolver, path: str
) -> dict[str, Any]:
    authorization = _resolved_json(
        value,
        resolver,
        path,
        kind="evidence-basis-authorization",
        schema="caplab-evidence-basis-authorization/1",
    )
    document_path = f"{path} document"
    _exact_object(
        authorization,
        document_path,
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
    if authorization["schema_version"] != "caplab-evidence-basis-authorization/1":
        raise _error(f"{document_path}.schema_version", "has the wrong schema version")
    _string(
        authorization["authorization_id"],
        f"{document_path}.authorization_id",
        pattern=re.compile(r"^basis-auth-[0-9a-f]{64}$"),
    )
    _validate_content_ref(
        authorization["authority_source_ref"],
        resolver,
        f"{document_path}.authority_source_ref",
    )
    _string(authorization["authorized_by"], f"{document_path}.authorized_by")
    _string(
        authorization["delegate_or_mechanism"],
        f"{document_path}.delegate_or_mechanism",
    )
    binding_ids = _set_array(
        authorization["binding_ids"], f"{document_path}.binding_ids", minimum=1
    )
    for index, binding_id in enumerate(binding_ids):
        _string(
            binding_id,
            f"{document_path}.binding_ids[{index}]",
            pattern=re.compile(r"^bnd-[0-9a-f]{64}$"),
        )
    capability, _ = _validate_capability(
        authorization["capability"], resolver, f"{document_path}.capability"
    )
    authorization["capability"] = capability
    _validate_experiment(authorization["experiment"], f"{document_path}.experiment")
    _validate_content_ref(
        authorization["protocol_ref"],
        resolver,
        f"{document_path}.protocol_ref",
        kind="protocol",
    )
    _validate_content_ref(
        authorization["corpus_ref"],
        resolver,
        f"{document_path}.corpus_ref",
        kind="corpus",
    )
    _validate_content_ref(
        authorization["case_selection_ref"],
        resolver,
        f"{document_path}.case_selection_ref",
        kind="case-selection",
        schema="caplab-case-selection-manifest/1",
    )
    _validate_content_ref(
        authorization["method_ref"], resolver, f"{document_path}.method_ref"
    )
    _enum(
        authorization["basis_kind"],
        f"{document_path}.basis_kind",
        {"mechanical-oracle", "human-authorized", "model-judgment"},
    )
    _enum(
        authorization["basis_role"],
        f"{document_path}.basis_role",
        {"truth", "case-selection", "metric-derivation"},
    )
    valid_from = _timestamp(authorization["valid_from"], f"{document_path}.valid_from")
    valid_until = _timestamp(authorization["valid_until"], f"{document_path}.valid_until")
    if valid_from > valid_until:
        raise _error(document_path, "valid_from must not be after valid_until")
    expected = derive_content_id(authorization, "authorization_id", "basis-auth-")
    if authorization["authorization_id"] != expected:
        raise _error(
            f"{document_path}.authorization_id",
            "does not match canonical basis authorization content",
        )
    return authorization


def _validate_basis(
    value: Any, resolver: EvidenceResolver, path: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    basis = _exact_object(
        value,
        path,
        {"basis_id", "kind", "role", "evidence_ref", "authorization_ref"},
    )
    _string(basis["basis_id"], f"{path}.basis_id", pattern=re.compile(r"^basis-[0-9a-f]{64}$"))
    kind = _enum(
        basis["kind"],
        f"{path}.kind",
        {"mechanical-oracle", "human-authorized", "model-judgment"},
    )
    _enum(basis["role"], f"{path}.role", {"truth", "case-selection", "metric-derivation"})
    evidence_kind = {
        "mechanical-oracle": "mechanical-oracle-result",
        "human-authorized": "human-authorized-judgment",
        "model-judgment": "model-judgment",
    }[kind]
    _validate_content_ref(
        basis["evidence_ref"], resolver, f"{path}.evidence_ref", kind=evidence_kind
    )
    authorization = _validate_basis_authorization(
        basis["authorization_ref"], resolver, f"{path}.authorization_ref"
    )
    expected = derive_content_id(basis, "basis_id", "basis-")
    if basis["basis_id"] != expected:
        raise _error(f"{path}.basis_id", "does not match canonical basis content")
    if authorization["basis_kind"] != kind:
        raise _error(f"{path}.authorization_ref", "basis kind is outside authorization scope")
    if authorization["basis_role"] != basis["role"]:
        raise _error(f"{path}.authorization_ref", "basis role is outside authorization scope")
    return basis, authorization


def _validate_case_selection(
    value: Any, resolver: EvidenceResolver, path: str
) -> set[str]:
    manifest = _resolved_json(
        value,
        resolver,
        path,
        kind="case-selection",
        schema="caplab-case-selection-manifest/1",
    )
    _exact_object(
        manifest,
        f"{path} document",
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
    if manifest["schema_version"] != "caplab-case-selection-manifest/1":
        raise _error(f"{path} document.schema_version", "has the wrong schema version")
    selection_id = _string(manifest["selection_id"], f"{path} document.selection_id")
    _string(
        selection_id,
        f"{path} document.selection_id",
        pattern=re.compile(r"^selection-[0-9a-f]{64}$"),
    )
    expected = derive_content_id(manifest, "selection_id", "selection-")
    if selection_id != expected:
        raise _error(f"{path} document.selection_id", "does not match canonical selection content")
    _validate_content_ref(manifest["population_ref"], resolver, f"{path} document.population_ref")
    reference_lists = (
        "included_case_refs",
        "excluded_case_refs",
        "selection_inputs",
        "exclusion_inputs",
    )
    list_keys: dict[str, set[bytes]] = {}
    for field in reference_lists:
        refs = _set_array(manifest[field], f"{path} document.{field}")
        list_keys[field] = {_canonical_key(ref) for ref in refs}
        for index, ref in enumerate(refs):
            _validate_content_ref(ref, resolver, f"{path} document.{field}[{index}]")
    if list_keys["included_case_refs"] & list_keys["excluded_case_refs"]:
        raise _error(f"{path} document", "included and excluded cases must be disjoint")
    conditioned_values = _set_array(manifest["conditioned_on"], f"{path} document.conditioned_on")
    conditioned: set[str] = set()
    for index, item in enumerate(conditioned_values):
        conditioned.add(
            _enum(
                item,
                f"{path} document.conditioned_on[{index}]",
                {
                    "downstream_fate",
                    "model_judgment",
                    "human_judgment",
                    "provider_verdict",
                    "scheduler_choice",
                    "admission",
                    "backend_rank",
                    "task_difficulty",
                    "attempt_outcome",
                },
            )
        )
    _validate_content_ref(
        manifest["authorization_ref"], resolver, f"{path} document.authorization_ref"
    )
    return conditioned


def _validate_sample_flow(value: Any, path: str) -> dict[str, int]:
    fields = {
        "planned",
        "attempted",
        "usable",
        "excluded",
        "missing",
        "subject_failures",
        "infrastructure_failures",
    }
    flow = _exact_object(value, path, fields)
    counts = {field: _integer(flow[field], f"{path}.{field}", minimum=0) for field in fields}
    if counts["attempted"] + counts["missing"] != counts["planned"]:
        raise _error(path, "attempted + missing must equal planned")
    if (
        counts["usable"]
        + counts["excluded"]
        + counts["subject_failures"]
        + counts["infrastructure_failures"]
        != counts["attempted"]
    ):
        raise _error(
            path,
            "usable + excluded + subject_failures + infrastructure_failures must equal attempted",
        )
    return counts


def _validate_measurement_evidence(
    value: Any, resolver: EvidenceResolver, path: str
) -> None:
    evidence = _exact_object(value, path, {"bundle_ref", "run_refs"})
    _validate_content_ref(evidence["bundle_ref"], resolver, f"{path}.bundle_ref", kind="evidence-bundle")
    refs = _set_array(evidence["run_refs"], f"{path}.run_refs")
    for index, ref in enumerate(refs):
        _validate_content_ref(ref, resolver, f"{path}.run_refs[{index}]", kind="attempt")


def _validate_covariates(value: Any, resolver: EvidenceResolver, path: str) -> None:
    covariates = _set_array(value, path)
    for index, item in enumerate(covariates):
        item_path = f"{path}[{index}]"
        covariate = _exact_object(item, item_path, {"name", "value", "evidence_ref"})
        name = _string(covariate["name"], f"{item_path}.name", pattern=_NAME)
        scalar = covariate["value"]
        if isinstance(scalar, float) or isinstance(scalar, (dict, list)):
            raise _error(f"{item_path}.value", "must be a canonical JSON scalar")
        if scalar is not None and not isinstance(scalar, (str, int, bool)):
            raise _error(f"{item_path}.value", "must be a canonical JSON scalar")
        if name == "downstream_fate" and (not isinstance(scalar, str) or not scalar):
            raise _error(f"{item_path}.value", "downstream_fate must be non-empty text")
        _validate_content_ref(covariate["evidence_ref"], resolver, f"{item_path}.evidence_ref")


def _validate_measurement_owned(
    measurement: dict[str, Any], resolver: EvidenceResolver
) -> tuple[dict[str, Any], dict[str, set[str]], set[str] | None]:
    _exact_object(
        measurement,
        "measurement",
        {
            "schema_version",
            "measurement_id",
            "observed_at",
            "binding",
            "capability",
            "experiment",
            "protocol",
            "corpus",
            "evidence_basis",
            "disposition",
            "sample_flow",
            "metrics",
            "evidence",
            "covariates",
            "provenance",
        },
    )
    if measurement["schema_version"] != "caplab-measurement/1":
        raise _error("measurement.schema_version", "must be 'caplab-measurement/1'")
    _string(
        measurement["measurement_id"],
        "measurement.measurement_id",
        pattern=re.compile(r"^meas-[0-9a-f]{64}$"),
    )
    _timestamp(measurement["observed_at"], "measurement.observed_at")
    measurement["binding"] = validate_binding(measurement["binding"], resolver)
    capability, inventory = _validate_capability(measurement["capability"], resolver, "measurement.capability")
    measurement["capability"] = capability
    _validate_experiment(measurement["experiment"], "measurement.experiment")
    _validate_content_ref(measurement["protocol"], resolver, "measurement.protocol", kind="protocol")
    _validate_content_ref(measurement["corpus"], resolver, "measurement.corpus", kind="corpus")
    basis_values = _set_array(measurement["evidence_basis"], "measurement.evidence_basis")
    bases: dict[str, dict[str, Any]] = {}
    basis_authorizations: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(basis_values):
        basis, authorization = _validate_basis(
            value, resolver, f"measurement.evidence_basis[{index}]"
        )
        if basis["basis_id"] in bases:
            raise _error("measurement.evidence_basis", "basis_id values must be unique")
        bases[basis["basis_id"]] = basis
        basis_authorizations[basis["basis_id"]] = authorization
    _enum(
        measurement["disposition"],
        "measurement.disposition",
        {"complete", "incomplete", "invalid", "infrastructure-failure"},
    )
    _validate_sample_flow(measurement["sample_flow"], "measurement.sample_flow")
    metrics = measurement["metrics"]
    if not isinstance(metrics, dict):
        raise _error("measurement.metrics", "must be an object")
    selections: dict[str, set[str]] = {}
    for name, metric_value in metrics.items():
        metric_name = _metric_name(name, f"measurement.metrics.{name}")
        metric = _exact_object(
            metric_value,
            f"measurement.metrics.{name}",
            {"value", "basis_ids", "case_selection_ref"},
        )
        _ratio(metric["value"], f"measurement.metrics.{name}.value")
        basis_ids = _set_array(metric["basis_ids"], f"measurement.metrics.{name}.basis_ids", minimum=1)
        for index, basis_id in enumerate(basis_ids):
            _string(
                basis_id,
                f"measurement.metrics.{name}.basis_ids[{index}]",
                pattern=re.compile(r"^basis-[0-9a-f]{64}$"),
            )
            if basis_id not in bases:
                raise _error(
                    f"measurement.metrics.{name}.basis_ids[{index}]",
                    "does not name a declared evidence basis",
                )
        selections[metric_name] = _validate_case_selection(
            metric["case_selection_ref"], resolver, f"measurement.metrics.{name}.case_selection_ref"
        )
        for basis_id in basis_ids:
            authorization = basis_authorizations[basis_id]
            if not _content_equal(
                authorization["case_selection_ref"], metric["case_selection_ref"]
            ):
                raise _error(
                    f"measurement.metrics.{name}.basis_ids",
                    "basis authorization case selection does not match metric",
                )
    observed_at = _timestamp(measurement["observed_at"], "measurement.observed_at")
    for basis_id, authorization in basis_authorizations.items():
        auth_path = f"measurement evidence basis {basis_id} authorization"
        if measurement["binding"]["binding_id"] not in authorization["binding_ids"]:
            raise _error(auth_path, "does not authorize this Binding")
        if not _content_equal(measurement["capability"], authorization["capability"]):
            raise _error(auth_path, "does not authorize this capability")
        if not _content_equal(measurement["experiment"], authorization["experiment"]):
            raise _error(auth_path, "does not authorize this experiment")
        if not _content_equal(measurement["protocol"], authorization["protocol_ref"]):
            raise _error(auth_path, "does not authorize this protocol")
        if not _content_equal(measurement["corpus"], authorization["corpus_ref"]):
            raise _error(auth_path, "does not authorize this corpus")
        if not (
            _timestamp(authorization["valid_from"], f"{auth_path}.valid_from")
            <= observed_at
            <= _timestamp(authorization["valid_until"], f"{auth_path}.valid_until")
        ):
            raise _error(auth_path, "does not authorize the observation time")
    _validate_measurement_evidence(measurement["evidence"], resolver, "measurement.evidence")
    _validate_covariates(measurement["covariates"], resolver, "measurement.covariates")
    _validate_provenance(measurement["provenance"], resolver, "measurement.provenance")
    expected = derive_content_id(measurement, "measurement_id", "meas-")
    if measurement["measurement_id"] != expected:
        raise _error("measurement.measurement_id", "does not match canonical measurement content")
    return measurement, selections, inventory


def validate_measurement(
    document: Mapping[str, Any], resolver: EvidenceResolver
) -> dict[str, Any]:
    """Validate and return an owned canonical ``caplab-measurement/1`` document."""

    measurement = _owned(document, "measurement")
    return _validate_measurement_owned(measurement, resolver)[0]


def _validate_authorization_owned(
    authorization: dict[str, Any], resolver: EvidenceResolver
) -> dict[str, Any]:
    _exact_object(
        authorization,
        "authorization",
        {
            "schema_version",
            "authorization_id",
            "authority_source_ref",
            "authorized_by",
            "delegate_or_mechanism",
            "binding_ids",
            "capability",
            "policy",
            "permitted_statuses",
            "valid_from",
            "valid_until",
        },
    )
    if authorization["schema_version"] != "caplab-qualification-authorization/1":
        raise _error(
            "authorization.schema_version",
            "must be 'caplab-qualification-authorization/1'",
        )
    _string(
        authorization["authorization_id"],
        "authorization.authorization_id",
        pattern=re.compile(r"^auth-[0-9a-f]{64}$"),
    )
    _validate_content_ref(
        authorization["authority_source_ref"],
        resolver,
        "authorization.authority_source_ref",
        kind="decision-record",
    )
    _string(authorization["authorized_by"], "authorization.authorized_by")
    _string(
        authorization["delegate_or_mechanism"],
        "authorization.delegate_or_mechanism",
    )
    binding_ids = _set_array(
        authorization["binding_ids"], "authorization.binding_ids", minimum=1
    )
    for index, binding_id in enumerate(binding_ids):
        _string(
            binding_id,
            f"authorization.binding_ids[{index}]",
            pattern=re.compile(r"^bnd-[0-9a-f]{64}$"),
        )
    capability, _ = _validate_capability(
        authorization["capability"], resolver, "authorization.capability"
    )
    authorization["capability"] = capability
    policy = _exact_object(authorization["policy"], "authorization.policy", {"name", "version"})
    _string(policy["name"], "authorization.policy.name")
    _string(policy["version"], "authorization.policy.version")
    statuses = _set_array(
        authorization["permitted_statuses"],
        "authorization.permitted_statuses",
        minimum=1,
    )
    for index, status in enumerate(statuses):
        _enum(
            status,
            f"authorization.permitted_statuses[{index}]",
            {"qualified", "unqualified"},
        )
    valid_from = _timestamp(authorization["valid_from"], "authorization.valid_from")
    valid_until = _timestamp(authorization["valid_until"], "authorization.valid_until")
    if valid_from > valid_until:
        raise _error("authorization", "valid_from must not be after valid_until")
    expected = derive_content_id(authorization, "authorization_id", "auth-")
    if authorization["authorization_id"] != expected:
        raise _error(
            "authorization.authorization_id",
            "does not match canonical authorization content",
        )
    return authorization


def validate_authorization(
    document: Mapping[str, Any], resolver: EvidenceResolver
) -> dict[str, Any]:
    """Validate and return an owned typed qualification authorization."""

    return _validate_authorization_owned(_owned(document, "authorization"), resolver)


def _validate_policy_owned(
    policy: dict[str, Any], resolver: EvidenceResolver
) -> tuple[dict[str, Any], set[str] | None]:
    _exact_object(
        policy,
        "policy",
        {
            "schema_version",
            "policy_id",
            "name",
            "version",
            "capability",
            "applies_to",
            "requirements",
            "criteria",
            "outcomes",
            "authority",
            "provenance",
        },
    )
    if policy["schema_version"] != "caplab-qualification-policy/1":
        raise _error("policy.schema_version", "must be 'caplab-qualification-policy/1'")
    _string(policy["policy_id"], "policy.policy_id", pattern=re.compile(r"^pol-[0-9a-f]{64}$"))
    _string(policy["name"], "policy.name")
    _string(policy["version"], "policy.version")
    capability, inventory = _validate_capability(policy["capability"], resolver, "policy.capability")
    policy["capability"] = capability

    applies = _exact_object(
        policy["applies_to"],
        "policy.applies_to",
        {"experiment", "protocol_sha256", "corpus_sha256", "binding_resolutions"},
    )
    _validate_experiment(applies["experiment"], "policy.applies_to.experiment")
    _string(applies["protocol_sha256"], "policy.applies_to.protocol_sha256", pattern=_HEX)
    _string(applies["corpus_sha256"], "policy.applies_to.corpus_sha256", pattern=_HEX)
    resolutions = _set_array(
        applies["binding_resolutions"],
        "policy.applies_to.binding_resolutions",
        minimum=1,
    )
    for index, resolution in enumerate(resolutions):
        _enum(
            resolution,
            f"policy.applies_to.binding_resolutions[{index}]",
            {"immutable", "observed-route"},
        )

    requirements = _exact_object(
        policy["requirements"],
        "policy.requirements",
        {
            "minimum_usable",
            "maximum_missing_rate",
            "maximum_infrastructure_failure_rate",
            "basis_kinds",
        },
    )
    _integer(requirements["minimum_usable"], "policy.requirements.minimum_usable", minimum=0)
    _ratio(
        requirements["maximum_missing_rate"],
        "policy.requirements.maximum_missing_rate",
        rate=True,
    )
    _ratio(
        requirements["maximum_infrastructure_failure_rate"],
        "policy.requirements.maximum_infrastructure_failure_rate",
        rate=True,
    )
    kinds = _set_array(requirements["basis_kinds"], "policy.requirements.basis_kinds", minimum=1)
    for index, kind in enumerate(kinds):
        _enum(
            kind,
            f"policy.requirements.basis_kinds[{index}]",
            {"mechanical-oracle", "human-authorized"},
        )

    criteria = _set_array(policy["criteria"], "policy.criteria", minimum=1)
    for index, value in enumerate(criteria):
        path = f"policy.criteria[{index}]"
        criterion = _exact_object(value, path, {"metric", "operator", "threshold"})
        _metric_name(criterion["metric"], f"{path}.metric")
        _enum(criterion["operator"], f"{path}.operator", {"metric_at_least", "metric_at_most"})
        _ratio(criterion["threshold"], f"{path}.threshold")

    outcomes = _exact_object(
        policy["outcomes"],
        "policy.outcomes",
        {"met", "not_met", "insufficient", "no_measurement"},
    )
    expected_outcomes = {
        "met": "qualified",
        "not_met": "unqualified",
        "insufficient": "advisory",
        "no_measurement": "unmeasured",
    }
    if outcomes != expected_outcomes:
        raise _error("policy.outcomes", "must use the fixed version 1 outcomes")

    authority = policy["authority"]
    if authority is not None:
        authority = _validate_authorization_owned(authority, resolver)
        policy["authority"] = authority

    _validate_provenance(policy["provenance"], resolver, "policy.provenance")
    expected = derive_content_id(policy, "policy_id", "pol-")
    if policy["policy_id"] != expected:
        raise _error("policy.policy_id", "does not match canonical policy content")
    return policy, inventory


def validate_policy(
    document: Mapping[str, Any], resolver: EvidenceResolver
) -> dict[str, Any]:
    """Validate and return an owned ``caplab-qualification-policy/1``."""

    return _validate_policy_owned(_owned(document, "policy"), resolver)[0]


def _content_equal(left: Any, right: Any) -> bool:
    return _canonical_key(left) == _canonical_key(right)


def _validate_document_reference(
    ref: Any,
    document: dict[str, Any],
    resolver: EvidenceResolver,
    path: str,
    *,
    kind: str,
    schema: str,
) -> dict[str, Any]:
    resolved = _resolved_json(ref, resolver, path, kind=kind, schema=schema)
    if not _content_equal(resolved, document):
        raise _error(path, "resolved document does not match supplied document")
    return ref


def _fraction_or_zero(numerator: int, denominator: int) -> Fraction:
    return Fraction(numerator, denominator) if denominator else Fraction(0, 1)


def _authorization_limitations(
    authorization: dict[str, Any] | None,
    *,
    binding: dict[str, Any],
    capability: dict[str, Any],
    policy: dict[str, Any],
    status: str,
    generated_at: datetime,
) -> list[str]:
    if authorization is None:
        return ["qualification-authorization-missing"]
    limitations: list[str] = []
    if binding["binding_id"] not in authorization["binding_ids"]:
        limitations.append("qualification-authorization-binding-mismatch")
    if not _content_equal(capability, authorization["capability"]):
        limitations.append("qualification-authorization-capability-mismatch")
    if authorization["policy"] != {"name": policy["name"], "version": policy["version"]}:
        limitations.append("qualification-authorization-policy-mismatch")
    if status not in authorization["permitted_statuses"]:
        limitations.append("qualification-authorization-status-mismatch")
    valid_from = _timestamp(authorization["valid_from"], "authorization.valid_from")
    valid_until = _timestamp(authorization["valid_until"], "authorization.valid_until")
    if generated_at < valid_from:
        limitations.append("qualification-authorization-not-yet-valid")
    if generated_at > valid_until:
        limitations.append("qualification-authorization-expired")
    return limitations


_INVALIDATION_TRIGGERS = sorted(
    [
        "binding-changed",
        "capability-card-changed",
        "corpus-changed",
        "evidence-invalidated",
        "policy-changed",
        "protocol-changed",
    ]
)


def _claim_content_id(claim: Mapping[str, Any]) -> str:
    basis = {
        key: value
        for key, value in claim.items()
        if key not in {"claim_id", "generated_at"}
    }
    try:
        return "claim-" + sha256_hex(canonical_json(basis))
    except CanonicalizationError as error:
        raise QualificationContractError(str(error)) from error


def build_claim(
    measurement: Mapping[str, Any] | None,
    policy: Mapping[str, Any],
    *,
    binding: Mapping[str, Any] | None = None,
    measurement_ref: Mapping[str, Any] | None,
    policy_ref: Mapping[str, Any],
    generated_at: str,
    supersedes: Sequence[str],
    resolver: EvidenceResolver,
    caplab_version: str,
    caplab_commit: str,
) -> dict[str, Any]:
    """Evaluate one exact Measurement under one Policy and build its Claim."""

    governing, policy_inventory = _validate_policy_owned(_owned(policy, "policy"), resolver)
    policy_ref_value = _owned(policy_ref, "policy_ref")
    _validate_document_reference(
        policy_ref_value,
        governing,
        resolver,
        "policy_ref",
        kind="qualification-policy",
        schema="caplab-qualification-policy/1",
    )
    generated = _timestamp(generated_at, "generated_at")
    _string(caplab_version, "caplab_version")
    _string(caplab_commit, "caplab_commit", pattern=_COMMIT)
    if isinstance(supersedes, (str, bytes)) or not isinstance(supersedes, Sequence):
        raise _error("supersedes", "must be an array")
    supersedes_value = list(supersedes)
    _set_array(supersedes_value, "supersedes")
    for index, claim_id in enumerate(supersedes_value):
        _string(claim_id, f"supersedes[{index}]", pattern=_CLAIM_ID)

    if measurement is None:
        if measurement_ref is not None:
            raise _error("measurement_ref", "must be null when measurement is null")
        if binding is None:
            raise _error("binding", "is required when measurement is null")
        bound = validate_binding(binding, resolver)
        criterion_results = sorted(
            [
                {
                    "metric": criterion["metric"],
                    "operator": criterion["operator"],
                    "threshold": criterion["threshold"],
                    "observed": None,
                    "result": "indeterminate",
                }
                for criterion in governing["criteria"]
            ],
            key=_canonical_key,
        )
        source_refs_by_key = {
            _canonical_key(ref): ref
            for ref in [*governing["provenance"]["source_refs"], policy_ref_value]
        }
        claim: dict[str, Any] = {
            "schema_version": "caplab-qualification-claim/1",
            "claim_id": "",
            "generated_at": generated_at,
            "assertion_type": "recommendation",
            "binding": bound,
            "capability": governing["capability"],
            "qualification": {
                "status": "unmeasured",
                "policy_id": governing["policy_id"],
                "policy_name": governing["name"],
                "policy_version": governing["version"],
                "policy_ref": policy_ref_value,
                "authorization": governing["authority"],
                "criteria": criterion_results,
                "limitations": ["eligible-measurement-absent"],
                "expires_at": (
                    governing["authority"]["valid_until"]
                    if governing["authority"] is not None
                    else None
                ),
                "invalidation_triggers": _INVALIDATION_TRIGGERS,
            },
            "measurement": None,
            "evidence": {"bundle_ref": None, "run_refs": []},
            "provenance": {
                "caplab_version": caplab_version,
                "caplab_commit": caplab_commit,
                "source_refs": [
                    source_refs_by_key[key] for key in sorted(source_refs_by_key)
                ],
            },
            "supersedes": supersedes_value,
        }
        claim["claim_id"] = _claim_content_id(claim)
        if claim["claim_id"] in supersedes_value:
            raise _error("supersedes", "a claim cannot supersede itself")
        return _owned(claim, "claim")

    if measurement_ref is None:
        raise _error("measurement_ref", "is required when measurement is supplied")
    measured, selections, card_inventory = _validate_measurement_owned(
        _owned(measurement, "measurement"), resolver
    )
    if binding is not None:
        supplied_binding = validate_binding(binding, resolver)
        if not _content_equal(supplied_binding, measured["binding"]):
            raise _error("binding", "does not exactly match Measurement binding")
    measurement_ref_value = _owned(measurement_ref, "measurement_ref")
    _validate_document_reference(
        measurement_ref_value,
        measured,
        resolver,
        "measurement_ref",
        kind="measurement",
        schema="caplab-measurement/1",
    )

    if not _content_equal(measured["capability"], governing["capability"]):
        raise _error("policy.capability", "does not exactly match Measurement capability")
    if not _content_equal(measured["experiment"], governing["applies_to"]["experiment"]):
        raise _error("policy.applies_to.experiment", "does not exactly match Measurement experiment")
    if measured["protocol"]["sha256"] != governing["applies_to"]["protocol_sha256"]:
        raise _error("policy.applies_to.protocol_sha256", "does not match Measurement protocol")
    if measured["corpus"]["sha256"] != governing["applies_to"]["corpus_sha256"]:
        raise _error("policy.applies_to.corpus_sha256", "does not match Measurement corpus")
    if card_inventory is not None and policy_inventory is not None and card_inventory != policy_inventory:
        raise _error("policy.capability.card_ref", "resolved metric inventory is inconsistent")

    bases_by_id = {basis["basis_id"]: basis for basis in measured["evidence_basis"]}
    criterion_results: list[dict[str, Any]] = []
    for policy_criterion in governing["criteria"]:
        metric_name = policy_criterion["metric"]
        if metric_name not in measured["metrics"]:
            raise _error(f"measurement.metrics.{metric_name}", "policy criterion metric is absent")
        if card_inventory is not None and metric_name not in card_inventory:
            raise _error(
                f"policy.criteria.{metric_name}",
                "criterion metric is absent from capability-card qualification_metrics",
            )
        observed_value = measured["metrics"][metric_name]["value"]
        observed = _ratio(observed_value, f"measurement.metrics.{metric_name}.value")
        threshold = _ratio(policy_criterion["threshold"], f"policy.criteria.{metric_name}.threshold")
        met = (
            observed >= threshold
            if policy_criterion["operator"] == "metric_at_least"
            else observed <= threshold
        )
        criterion_results.append(
            {
                "metric": metric_name,
                "operator": policy_criterion["operator"],
                "threshold": policy_criterion["threshold"],
                "observed": observed_value,
                "result": "met" if met else "not-met",
            }
        )
    criterion_results.sort(key=_canonical_key)

    limitations: list[str] = []
    binding = measured["binding"]
    resolution = binding["provider_or_path"]["resolution"]
    if resolution not in governing["applies_to"]["binding_resolutions"]:
        limitations.append("binding-resolution-outside-policy-scope")
    if resolution != "immutable":
        limitations.append("binding-not-immutable")
    if binding["model"]["weights_ref"] is None:
        limitations.append("model-weights-unavailable")
    if binding["harness"]["executable_ref"] is None:
        limitations.append("harness-executable-unavailable")
    if measured["disposition"] != "complete":
        limitations.append("measurement-not-complete")

    flow = measured["sample_flow"]
    requirements = governing["requirements"]
    if flow["usable"] < 1:
        limitations.append("decision-sample-absent")
    if flow["usable"] < requirements["minimum_usable"]:
        limitations.append("minimum-usable-not-met")
    missing_rate = _fraction_or_zero(flow["missing"], flow["planned"])
    if missing_rate > _ratio(requirements["maximum_missing_rate"], "policy.requirements.maximum_missing_rate", rate=True):
        limitations.append("maximum-missing-rate-exceeded")
    infrastructure_rate = _fraction_or_zero(
        flow["infrastructure_failures"], flow["attempted"]
    )
    if infrastructure_rate > _ratio(
        requirements["maximum_infrastructure_failure_rate"],
        "policy.requirements.maximum_infrastructure_failure_rate",
        rate=True,
    ):
        limitations.append("maximum-infrastructure-failure-rate-exceeded")

    permitted_kinds = set(requirements["basis_kinds"])
    declared_roles = {basis["role"] for basis in measured["evidence_basis"]}
    if not {"truth", "case-selection", "metric-derivation"}.issubset(declared_roles):
        limitations.append("required-evidence-basis-roles-missing")
    if any(basis["kind"] not in permitted_kinds for basis in measured["evidence_basis"]):
        limitations.append("evidence-basis-kind-not-permitted")
    for result in criterion_results:
        metric_name = result["metric"]
        metric = measured["metrics"][metric_name]
        lineage_roles = {bases_by_id[basis_id]["role"] for basis_id in metric["basis_ids"]}
        if not {"truth", "metric-derivation"}.issubset(lineage_roles):
            limitations.append(f"metric-lineage-incomplete:{metric_name}")
        has_selection_basis = False
        for basis in measured["evidence_basis"]:
            if basis["role"] != "case-selection":
                continue
            basis_authorization = _validate_basis_authorization(
                basis["authorization_ref"],
                resolver,
                f"measurement evidence basis {basis['basis_id']} authorization_ref",
            )
            if _content_equal(
                basis_authorization["case_selection_ref"], metric["case_selection_ref"]
            ):
                has_selection_basis = True
                break
        if not has_selection_basis:
            limitations.append(f"case-selection-lineage-missing:{metric_name}")
        if "downstream_fate" in selections[metric_name]:
            limitations.append(f"fate-conditioned-case-selection:{metric_name}")
        if "model_judgment" in selections[metric_name]:
            limitations.append(f"model-conditioned-case-selection:{metric_name}")
        for condition in selections[metric_name] - {"downstream_fate", "model_judgment"}:
            limitations.append(f"conditioned-case-selection:{condition}:{metric_name}")

    bundle_payload = _validate_content_ref(
        measured["evidence"]["bundle_ref"],
        resolver,
        "measurement.evidence.bundle_ref",
        kind="evidence-bundle",
    )
    if not bundle_payload:
        limitations.append("evidence-bundle-empty")
    if not measured["evidence"]["run_refs"]:
        limitations.append("run-evidence-missing")
    elif any(
        not _validate_content_ref(ref, resolver, f"measurement.evidence.run_refs[{index}]", kind="attempt")
        for index, ref in enumerate(measured["evidence"]["run_refs"])
    ):
        limitations.append("run-evidence-empty")

    provisional = "qualified" if all(item["result"] == "met" for item in criterion_results) else "unqualified"
    limitations.extend(
        _authorization_limitations(
            governing["authority"],
            binding=binding,
            capability=measured["capability"],
            policy=governing,
            status=provisional,
            generated_at=generated,
        )
    )
    limitations = sorted(set(limitations))
    status = provisional if not limitations else "advisory"
    assertion_type = "decision" if status in {"qualified", "unqualified"} else "recommendation"

    measurement_summary = {
        "measurement_id": measured["measurement_id"],
        "measurement_ref": measurement_ref_value,
        "observed_at": measured["observed_at"],
        "binding_id": binding["binding_id"],
        "capability": measured["capability"],
        "disposition": measured["disposition"],
        "experiment": measured["experiment"],
        "protocol_ref": measured["protocol"],
        "corpus_ref": measured["corpus"],
        "sample_count": flow["usable"],
        "sample_flow": measured["sample_flow"],
        "metrics": measured["metrics"],
        "bases": measured["evidence_basis"],
    }
    source_refs_by_key: dict[bytes, dict[str, Any]] = {}
    for ref in [
        *measured["provenance"]["source_refs"],
        *governing["provenance"]["source_refs"],
        measurement_ref_value,
        policy_ref_value,
    ]:
        source_refs_by_key[_canonical_key(ref)] = ref
    source_refs = [source_refs_by_key[key] for key in sorted(source_refs_by_key)]
    claim: dict[str, Any] = {
        "schema_version": "caplab-qualification-claim/1",
        "claim_id": "",
        "generated_at": generated_at,
        "assertion_type": assertion_type,
        "binding": binding,
        "capability": measured["capability"],
        "qualification": {
            "status": status,
            "policy_id": governing["policy_id"],
            "policy_name": governing["name"],
            "policy_version": governing["version"],
            "policy_ref": policy_ref_value,
            "authorization": governing["authority"],
            "criteria": criterion_results,
            "limitations": limitations,
            "expires_at": (
                governing["authority"]["valid_until"]
                if governing["authority"] is not None
                else None
            ),
            "invalidation_triggers": _INVALIDATION_TRIGGERS,
        },
        "measurement": measurement_summary,
        "evidence": measured["evidence"],
        "provenance": {
            "caplab_version": caplab_version,
            "caplab_commit": caplab_commit,
            "source_refs": source_refs,
        },
        "supersedes": supersedes_value,
    }
    claim["claim_id"] = _claim_content_id(claim)
    if claim["claim_id"] in supersedes_value:
        raise _error("supersedes", "a claim cannot supersede itself")
    return _owned(claim, "claim")


def validate_claim(
    document: Mapping[str, Any], resolver: EvidenceResolver
) -> dict[str, Any]:
    """Validate a Claim by resolving and re-evaluating its immutable inputs."""

    claim = _owned(document, "claim")
    _exact_object(
        claim,
        "claim",
        {
            "schema_version",
            "claim_id",
            "generated_at",
            "assertion_type",
            "binding",
            "capability",
            "qualification",
            "measurement",
            "evidence",
            "provenance",
            "supersedes",
        },
    )
    if claim["schema_version"] != "caplab-qualification-claim/1":
        raise _error("claim.schema_version", "must be 'caplab-qualification-claim/1'")
    _string(claim["claim_id"], "claim.claim_id", pattern=_CLAIM_ID)
    _set_array(claim["supersedes"], "claim.supersedes")
    if claim["claim_id"] in claim["supersedes"]:
        raise _error("claim.supersedes", "a claim cannot supersede itself")
    measurement_summary = claim["measurement"]
    if measurement_summary is not None and not isinstance(measurement_summary, dict):
        raise _error("claim.measurement", "must be an object")
    qualification = claim["qualification"]
    if not isinstance(qualification, dict):
        raise _error("claim.qualification", "must be an object")
    measurement_ref = (
        measurement_summary.get("measurement_ref")
        if measurement_summary is not None
        else None
    )
    policy_ref = qualification.get("policy_ref")
    measured_document = None
    if measurement_ref is not None:
        measured_document = _resolved_json(
            measurement_ref,
            resolver,
            "claim.measurement.measurement_ref",
            kind="measurement",
            schema="caplab-measurement/1",
        )
    policy_document = _resolved_json(
        policy_ref,
        resolver,
        "claim.qualification.policy_ref",
        kind="qualification-policy",
        schema="caplab-qualification-policy/1",
    )
    provenance = claim["provenance"]
    if not isinstance(provenance, dict):
        raise _error("claim.provenance", "must be an object")
    rebuilt = build_claim(
        measured_document,
        policy_document,
        binding=claim["binding"] if measured_document is None else None,
        measurement_ref=measurement_ref,
        policy_ref=policy_ref,
        generated_at=claim["generated_at"],
        supersedes=claim["supersedes"],
        resolver=resolver,
        caplab_version=provenance.get("caplab_version"),
        caplab_commit=provenance.get("caplab_commit"),
    )
    if not _content_equal(claim, rebuilt):
        raise _error("claim", "does not match deterministic policy evaluation")
    if claim["claim_id"] != _claim_content_id(claim):
        raise _error("claim.claim_id", "does not match canonical claim content")
    return claim
