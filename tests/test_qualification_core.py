"""Behavioral contracts for CAPLAB qualification semantics."""

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from hashlib import sha256
from typing import Any

from caplab.qualification import (
    EvidenceResolver,
    QualificationContractError,
    build_claim,
    derive_content_id,
    policy_semantic_sha256,
    validate_authorization,
    validate_binding,
    validate_claim,
    validate_measurement,
    validate_policy,
)
from caplab.runtime.canonical import canonical_json


class MemoryResolver(EvidenceResolver):
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.registrations: dict[str, tuple[str, str, int]] = {}

    def add(
        self,
        kind: str,
        schema: str,
        value: Any,
        *,
        media_type: str | None = None,
    ) -> dict[str, Any]:
        payload = value if isinstance(value, bytes) else canonical_json(value)
        if media_type is None:
            media_type = (
                "application/octet-stream"
                if isinstance(value, bytes)
                else "application/json"
            )
        digest = sha256(payload).hexdigest()
        locator = f"objects/sha256/{digest[:2]}/{digest}"
        self.objects[locator] = payload
        registration_ref = f"local:{digest}"
        self.registrations[registration_ref] = (locator, digest, len(payload))
        return {
            "kind": kind,
            "schema": schema,
            "media_type": media_type,
            "sha256": digest,
            "byte_count": len(payload),
            "locator": locator,
            "registration_ref": registration_ref,
            "custody": None,
        }

    def resolve(self, ref: dict[str, Any]) -> bytes:
        registered = self.registrations.get(ref["registration_ref"])
        if registered != (ref["locator"], ref["sha256"], ref["byte_count"]):
            raise KeyError(ref["registration_ref"])
        return self.objects[ref["locator"]]


def canonical_sorted(values: list[Any]) -> list[Any]:
    return sorted(values, key=canonical_json)


def make_delegation(
    resolver: MemoryResolver,
    *,
    effect: str,
    authorized_by: str,
    delegate_or_mechanism: str,
    scope: dict[str, Any],
    valid_from: str = "2026-01-01T00:00:00Z",
    valid_until: str = "2026-12-31T23:59:59Z",
) -> dict[str, Any]:
    delegation = {
        "schema_version": "caplab-authorization-delegation/1",
        "delegation_id": "",
        "effect": effect,
        "authorized_by": authorized_by,
        "delegate_or_mechanism": delegate_or_mechanism,
        "scope": deepcopy(scope),
        "valid_from": valid_from,
        "valid_until": valid_until,
    }
    delegation["delegation_id"] = derive_content_id(
        delegation, "delegation_id", "delegation-"
    )
    return resolver.add(
        "authorization-delegation",
        "caplab-authorization-delegation/1",
        delegation,
    )


def make_binding(resolver: MemoryResolver) -> dict[str, Any]:
    binary = resolver.add("model-weights", "opaque/1", b"model")
    executable = resolver.add("harness-executable", "opaque/1", b"harness")
    provider = {
        "kind": "local-serving",
        "identifier": "local",
        "revision": "server-1",
        "resolution": "immutable",
        "observed_at": None,
    }
    route = resolver.add(
        "provider-route",
        "caplab-provider-route/1",
        {"schema_version": "caplab-provider-route/1", **provider},
    )
    command = resolver.add(
        "native-harness-command",
        "caplab-native-harness-command/1",
        {
            "schema_version": "caplab-native-harness-command/1",
            "argv": ["agent", "review", "--effort", "high"],
        },
    )
    version_command = resolver.add(
        "native-harness-version-command",
        "caplab-native-harness-version-command/1",
        {
            "schema_version": "caplab-native-harness-version-command/1",
            "argv": ["agent", "--version"],
        },
    )
    stdout = resolver.add(
        "stdout", "text/1", b"native-agent 1\n", media_type="text/plain"
    )
    stderr = resolver.add("stderr", "text/1", b"", media_type="text/plain")
    probe = resolver.add(
        "native-harness-version-probe",
        "caplab-native-harness-version-probe/1",
        {
            "command_ref": version_command,
            "exit_code": 0,
            "stdout_ref": stdout,
            "stderr_ref": stderr,
        },
    )
    configuration_kinds = {
        "inference_ref": "inference-configuration",
        "instructions_ref": "instructions",
        "knowledge_ref": "knowledge",
        "tools_ref": "tools",
        "permissions_ref": "permissions",
        "sandbox_ref": "sandbox",
        "runtime_ref": "runtime",
    }
    configuration = {
        name: resolver.add(
            kind,
            "caplab-binding-configuration/1",
            {"name": name},
        )
        for name, kind in configuration_kinds.items()
    }
    binding = {
        "schema_version": "caplab-binding/1",
        "binding_id": "",
        "model": {
            "model_id": "example/model",
            "revision": "rev-1",
            "weights_ref": binary,
            "weights_unavailable_reason": None,
        },
        "provider_or_path": {**provider, "route_ref": route},
        "harness": {
            "harness_id": "native-agent",
            "harness_version": "1",
            "executable_ref": executable,
            "executable_unavailable_reason": None,
            "command_ref": command,
            "version_probe_ref": probe,
        },
        "reasoning_effort": "high",
        "configuration": configuration,
    }
    binding["binding_id"] = derive_content_id(binding, "binding_id", "bnd-")
    return binding


def make_capability(resolver: MemoryResolver) -> dict[str, Any]:
    card = resolver.add(
        "capability-card",
        "caplab-capability-card/1",
        {
            "schema_version": "caplab-capability-card/1",
            "qualification_metrics": ["accuracy"],
        },
    )
    return {
        "name": "code-repair",
        "version": "1",
        "role": "implementation",
        "domain": "python",
        "distribution": "registered-source-population",
        "card_ref": card,
    }


def make_case_selection(
    resolver: MemoryResolver, conditioned_on: list[str] | None = None
) -> dict[str, Any]:
    population = resolver.add("case-population", "population/1", {"name": "source"})
    included = resolver.add("case", "case/1", {"case_id": "case-1"})
    selection_input = resolver.add(
        "case-selection-input", "selection-input/1", {"rule": "all"}
    )
    selection_scope = {
        "population_ref": population,
        "included_case_refs": [included],
        "excluded_case_refs": [],
        "selection_inputs": [selection_input],
        "exclusion_inputs": [],
        "conditioned_on": canonical_sorted(conditioned_on or []),
    }
    authority = make_delegation(
        resolver,
        effect="case-selection",
        authorized_by="repository-owner",
        delegate_or_mechanism="pinned case selection",
        scope=selection_scope,
    )
    manifest = {
        "schema_version": "caplab-case-selection-manifest/1",
        "selection_id": "",
        **selection_scope,
        "authorization_ref": authority,
    }
    manifest["selection_id"] = derive_content_id(manifest, "selection_id", "selection-")
    return resolver.add("case-selection", "caplab-case-selection-manifest/1", manifest)


def make_basis_authorization(
    resolver: MemoryResolver,
    *,
    binding: dict[str, Any],
    capability: dict[str, Any],
    experiment: dict[str, Any],
    protocol: dict[str, Any],
    corpus: dict[str, Any],
    case_selection: dict[str, Any],
    kind: str,
    role: str,
) -> dict[str, Any]:
    method = resolver.add(
        "measurement-method", "method/1", {"method": f"{kind}:{role}"}
    )
    scope = {
        "binding_ids": [binding["binding_id"]],
        "capability": capability,
        "experiment": experiment,
        "protocol_ref": protocol,
        "corpus_ref": corpus,
        "case_selection_ref": case_selection,
        "method_ref": method,
        "basis_kind": kind,
        "basis_role": role,
    }
    authority = make_delegation(
        resolver,
        effect="evidence-basis",
        authorized_by="repository-owner",
        delegate_or_mechanism="pinned test mechanism",
        scope=scope,
    )
    authorization = {
        "schema_version": "caplab-evidence-basis-authorization/1",
        "authorization_id": "",
        "authority_source_ref": authority,
        "authorized_by": "repository-owner",
        "delegate_or_mechanism": "pinned test mechanism",
        **scope,
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_until": "2026-12-31T23:59:59Z",
    }
    authorization["authorization_id"] = derive_content_id(
        authorization, "authorization_id", "basis-auth-"
    )
    return resolver.add(
        "evidence-basis-authorization",
        "caplab-evidence-basis-authorization/1",
        authorization,
    )


def make_measurement(
    resolver: MemoryResolver,
    *,
    basis_kind: str = "mechanical-oracle",
    conditioned_on: list[str] | None = None,
    binding: dict[str, Any] | None = None,
    include_fate: bool = True,
) -> dict[str, Any]:
    binding = binding or make_binding(resolver)
    capability = make_capability(resolver)
    experiment = {"family": "repair-benchmark", "version": "1"}
    protocol = resolver.add("protocol", "protocol/1", {"protocol": "repair-v1"})
    corpus = resolver.add("corpus", "corpus/1", {"corpus": "held-out-v1"})
    case_selection = make_case_selection(resolver, conditioned_on)
    evidence_kind = {
        "mechanical-oracle": "mechanical-oracle-result",
        "human-authorized": "human-authorized-judgment",
        "model-judgment": "model-judgment",
    }[basis_kind]
    bases: list[dict[str, Any]] = []
    for role in ("truth", "case-selection", "metric-derivation"):
        evidence = resolver.add(evidence_kind, "basis-evidence/1", {"role": role})
        authorization = make_basis_authorization(
            resolver,
            binding=binding,
            capability=capability,
            experiment=experiment,
            protocol=protocol,
            corpus=corpus,
            case_selection=case_selection,
            kind=basis_kind,
            role=role,
        )
        basis = {
            "basis_id": "",
            "kind": basis_kind,
            "role": role,
            "evidence_ref": evidence,
            "authorization_ref": authorization,
        }
        basis["basis_id"] = derive_content_id(basis, "basis_id", "basis-")
        bases.append(basis)
    bases = canonical_sorted(bases)
    fate_ref = resolver.add("observation", "observation/1", {"source": "scheduler"})
    measurement = {
        "schema_version": "caplab-measurement/1",
        "measurement_id": "",
        "observed_at": "2026-06-01T00:00:00Z",
        "binding": binding,
        "capability": capability,
        "experiment": experiment,
        "protocol": protocol,
        "corpus": corpus,
        "evidence_basis": bases,
        "disposition": "complete",
        "sample_flow": {
            "planned": 10,
            "attempted": 10,
            "usable": 10,
            "excluded": 0,
            "missing": 0,
            "subject_failures": 0,
            "infrastructure_failures": 0,
        },
        "metrics": {
            "accuracy": {
                "value": {"numerator": 4, "denominator": 5},
                "basis_ids": canonical_sorted([basis["basis_id"] for basis in bases]),
                "case_selection_ref": case_selection,
            }
        },
        "evidence": {
            "bundle_ref": resolver.add("evidence-bundle", "bundle/1", b"bundle"),
            "run_refs": [resolver.add("attempt", "attempt/1", b"attempt")],
        },
        "covariates": (
            [{"name": "downstream_fate", "value": "admitted", "evidence_ref": fate_ref}]
            if include_fate
            else []
        ),
        "provenance": {
            "caplab_version": "0.1.0",
            "caplab_commit": "1" * 40,
            "source_refs": [],
        },
    }
    measurement["measurement_id"] = derive_content_id(
        measurement, "measurement_id", "meas-"
    )
    return measurement


def make_policy(
    resolver: MemoryResolver,
    measurement: dict[str, Any],
    *,
    threshold: dict[str, int] | None = None,
    with_authority: bool = True,
    permitted_basis_kind: str = "mechanical-oracle",
    valid_from: str = "2026-01-01T00:00:00Z",
    valid_until: str = "2026-12-31T23:59:59Z",
) -> dict[str, Any]:
    name = "repair-production"
    version = "1"
    policy = {
        "schema_version": "caplab-qualification-policy/1",
        "policy_id": "",
        "name": name,
        "version": version,
        "capability": deepcopy(measurement["capability"]),
        "applies_to": {
            "experiment": deepcopy(measurement["experiment"]),
            "protocol_sha256": measurement["protocol"]["sha256"],
            "corpus_sha256": measurement["corpus"]["sha256"],
            "binding_resolutions": [
                measurement["binding"]["provider_or_path"]["resolution"]
            ],
        },
        "requirements": {
            "minimum_usable": 1,
            "maximum_missing_rate": {"numerator": 0, "denominator": 1},
            "maximum_infrastructure_failure_rate": {"numerator": 0, "denominator": 1},
            "basis_kinds": [permitted_basis_kind],
        },
        "criteria": [
            {
                "metric": "accuracy",
                "operator": "metric_at_least",
                "threshold": threshold or {"numerator": 3, "denominator": 4},
            }
        ],
        "outcomes": {
            "met": "qualified",
            "not_met": "unqualified",
            "insufficient": "advisory",
            "no_measurement": "unmeasured",
        },
        "authority": None,
        "provenance": {
            "caplab_version": "0.1.0",
            "caplab_commit": "2" * 40,
            "source_refs": [],
        },
    }
    if with_authority:
        policy_identity = {
            "name": name,
            "version": version,
            "semantic_sha256": policy_semantic_sha256(policy),
        }
        authority_scope = {
            "binding_ids": [measurement["binding"]["binding_id"]],
            "capability": deepcopy(measurement["capability"]),
            "policy": policy_identity,
            "permitted_statuses": ["qualified", "unqualified"],
        }
        authority = {
            "schema_version": "caplab-qualification-authorization/1",
            "authorization_id": "",
            "authority_source_ref": make_delegation(
                resolver,
                effect="qualification",
                authorized_by="repository-owner",
                delegate_or_mechanism="mechanical policy evaluator",
                scope=authority_scope,
                valid_from=valid_from,
                valid_until=valid_until,
            ),
            "authorized_by": "repository-owner",
            "delegate_or_mechanism": "mechanical policy evaluator",
            **authority_scope,
            "valid_from": valid_from,
            "valid_until": valid_until,
        }
        authority["authorization_id"] = derive_content_id(
            authority, "authorization_id", "auth-"
        )
        policy["authority"] = authority
    policy["policy_id"] = derive_content_id(policy, "policy_id", "pol-")
    return policy


def reseal_qualification_authority(
    resolver: MemoryResolver, policy: dict[str, Any]
) -> None:
    authority = policy["authority"]
    scope = {
        "binding_ids": authority["binding_ids"],
        "capability": authority["capability"],
        "policy": authority["policy"],
        "permitted_statuses": authority["permitted_statuses"],
    }
    authority["authority_source_ref"] = make_delegation(
        resolver,
        effect="qualification",
        authorized_by=authority["authorized_by"],
        delegate_or_mechanism=authority["delegate_or_mechanism"],
        scope=scope,
        valid_from=authority["valid_from"],
        valid_until=authority["valid_until"],
    )
    authority["authorization_id"] = derive_content_id(
        authority, "authorization_id", "auth-"
    )
    policy["policy_id"] = derive_content_id(policy, "policy_id", "pol-")


def build_fixture_claim(
    resolver: MemoryResolver,
    measurement: dict[str, Any],
    policy: dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    measurement_ref = resolver.add("measurement", "caplab-measurement/1", measurement)
    policy_ref = resolver.add(
        "qualification-policy", "caplab-qualification-policy/1", policy
    )
    return build_claim(
        measurement,
        policy,
        measurement_ref=measurement_ref,
        policy_ref=policy_ref,
        generated_at=kwargs.pop("generated_at", "2026-06-02T00:00:00Z"),
        supersedes=kwargs.pop("supersedes", []),
        resolver=resolver,
        caplab_version="0.1.0",
        caplab_commit="3" * 40,
        caplab_package_sha256="4" * 64,
        **kwargs,
    )


class ContentIdentityTests(unittest.TestCase):
    def test_identity_is_canonical_and_does_not_mutate_the_document(self) -> None:
        document = {
            "record_id": "ignored",
            "label": "Cafe\u0301",
            "nested": {"count": 1},
        }
        original = {
            "record_id": "ignored",
            "label": "Cafe\u0301",
            "nested": {"count": 1},
        }

        first = derive_content_id(document, "record_id", "rec-")
        second = derive_content_id(
            {"nested": {"count": 1}, "label": "Caf\u00e9"},
            "record_id",
            "rec-",
        )

        self.assertEqual(first, second)
        self.assertRegex(first, r"^rec-[0-9a-f]{64}$")
        self.assertEqual(document, original)


class BindingValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.resolver = MemoryResolver()
        self.binding = make_binding(self.resolver)

    def test_exact_immutable_binding_is_copied_and_validated(self) -> None:
        original = deepcopy(self.binding)
        validated = validate_binding(self.binding, self.resolver)

        self.assertEqual(validated, original)
        self.assertIsNot(validated, self.binding)
        self.assertIsNot(validated["model"], self.binding["model"])

    def test_each_behavior_bearing_change_changes_binding_identity(self) -> None:
        mutations = (
            ("reasoning_effort", "medium"),
            ("provider_or_path.identifier", "other-provider"),
            ("harness.harness_version", "2"),
            (
                "configuration.inference_ref",
                self.resolver.add(
                    "inference-configuration",
                    "caplab-binding-configuration/1",
                    {"temperature": 1},
                ),
            ),
        )
        for path, replacement in mutations:
            with self.subTest(path=path):
                changed = deepcopy(self.binding)
                target = changed
                parts = path.split(".")
                for part in parts[:-1]:
                    target = target[part]
                target[parts[-1]] = replacement
                if path == "provider_or_path.identifier":
                    provider = changed["provider_or_path"]
                    provider["route_ref"] = self.resolver.add(
                        "provider-route",
                        "caplab-provider-route/1",
                        {
                            "schema_version": "caplab-provider-route/1",
                            **{
                                key: provider[key]
                                for key in (
                                    "kind",
                                    "identifier",
                                    "revision",
                                    "resolution",
                                    "observed_at",
                                )
                            },
                        },
                    )
                changed["binding_id"] = derive_content_id(changed, "binding_id", "bnd-")
                self.assertNotEqual(changed["binding_id"], self.binding["binding_id"])
                validate_binding(changed, self.resolver)

    def test_unknown_or_mutable_binding_is_rejected(self) -> None:
        unknown = deepcopy(self.binding)
        unknown["surprise"] = True
        with self.assertRaises(QualificationContractError):
            validate_binding(unknown, self.resolver)

        mutable = deepcopy(self.binding)
        mutable["model"]["weights_ref"] = None
        mutable["model"]["weights_unavailable_reason"] = None
        mutable["binding_id"] = derive_content_id(mutable, "binding_id", "bnd-")
        with self.assertRaises(QualificationContractError):
            validate_binding(mutable, self.resolver)

    def test_malformed_or_unresolved_content_reference_is_rejected(self) -> None:
        malformed = deepcopy(self.binding)
        malformed["model"]["weights_ref"]["locator"] = "objects/sha256/00/bad"
        malformed["binding_id"] = derive_content_id(malformed, "binding_id", "bnd-")
        with self.assertRaises(QualificationContractError):
            validate_binding(malformed, self.resolver)

        corrupt = deepcopy(self.binding)
        corrupt["model"]["weights_ref"]["byte_count"] += 1
        corrupt["binding_id"] = derive_content_id(corrupt, "binding_id", "bnd-")
        with self.assertRaises(QualificationContractError):
            validate_binding(corrupt, self.resolver)

    def test_binding_references_are_typed_and_nonempty(self) -> None:
        wrong_weights = deepcopy(self.binding)
        wrong_weights["model"]["weights_ref"] = self.resolver.add(
            "model-judgment", "judgment/1", b"not model weights"
        )
        wrong_weights["binding_id"] = derive_content_id(
            wrong_weights, "binding_id", "bnd-"
        )
        with self.assertRaises(QualificationContractError):
            validate_binding(wrong_weights, self.resolver)

        empty_executable = deepcopy(self.binding)
        empty_executable["harness"]["executable_ref"] = self.resolver.add(
            "harness-executable", "opaque/1", b""
        )
        empty_executable["binding_id"] = derive_content_id(
            empty_executable, "binding_id", "bnd-"
        )
        with self.assertRaises(QualificationContractError):
            validate_binding(empty_executable, self.resolver)

        wrong_configuration = deepcopy(self.binding)
        wrong_configuration["configuration"]["tools_ref"] = self.resolver.add(
            "downstream-fate", "observation/1", {"fate": "final"}
        )
        wrong_configuration["binding_id"] = derive_content_id(
            wrong_configuration, "binding_id", "bnd-"
        )
        with self.assertRaises(QualificationContractError):
            validate_binding(wrong_configuration, self.resolver)

    def test_registration_and_version_probe_consistency_are_required(self) -> None:
        unregistered = deepcopy(self.binding)
        reference = unregistered["configuration"]["tools_ref"]
        self.resolver.registrations.pop(reference["registration_ref"])
        with self.assertRaises(QualificationContractError):
            validate_binding(unregistered, self.resolver)

        self.resolver = MemoryResolver()
        cross_registered = make_binding(self.resolver)
        wrong_registration = self.resolver.add("other", "other/1", b"other")
        cross_registered["configuration"]["tools_ref"]["registration_ref"] = (
            wrong_registration["registration_ref"]
        )
        cross_registered["binding_id"] = derive_content_id(
            cross_registered, "binding_id", "bnd-"
        )
        with self.assertRaises(QualificationContractError):
            validate_binding(cross_registered, self.resolver)

        self.resolver = MemoryResolver()
        binding = make_binding(self.resolver)
        wrong_command = self.resolver.add("command", "command/1", {"argv": ["other"]})
        probe_ref = binding["harness"]["version_probe_ref"]
        probe = {
            "command_ref": wrong_command,
            "exit_code": 0,
            "stdout_ref": self.resolver.add(
                "stdout", "text/1", b"1", media_type="text/plain"
            ),
            "stderr_ref": self.resolver.add(
                "stderr", "text/1", b"", media_type="text/plain"
            ),
        }
        replacement = self.resolver.add("version-probe", "probe/1", probe)
        binding["harness"]["version_probe_ref"] = replacement
        binding["binding_id"] = derive_content_id(binding, "binding_id", "bnd-")
        with self.assertRaises(QualificationContractError):
            validate_binding(binding, self.resolver)

        binding = make_binding(self.resolver)
        probe_ref = binding["harness"]["version_probe_ref"]
        probe = json.loads(self.resolver.resolve(probe_ref).decode("utf-8"))
        probe["exit_code"] = 1
        binding["harness"]["version_probe_ref"] = self.resolver.add(
            "version-probe", "probe/1", probe
        )
        binding["binding_id"] = derive_content_id(binding, "binding_id", "bnd-")
        with self.assertRaises(QualificationContractError):
            validate_binding(binding, self.resolver)


class MeasurementAndPolicyValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.resolver = MemoryResolver()
        self.measurement = make_measurement(self.resolver)
        self.policy = make_policy(self.resolver, self.measurement)

    def test_measurement_policy_and_typed_authorization_are_owned(self) -> None:
        measurement_before = deepcopy(self.measurement)
        policy_before = deepcopy(self.policy)

        validated_measurement = validate_measurement(self.measurement, self.resolver)
        validated_policy = validate_policy(self.policy, self.resolver)
        validated_authorization = validate_authorization(
            self.policy["authority"], self.resolver
        )

        self.assertEqual(self.measurement, measurement_before)
        self.assertEqual(self.policy, policy_before)
        self.assertEqual(validated_measurement, measurement_before)
        self.assertEqual(validated_policy, policy_before)
        self.assertEqual(
            validated_authorization["authorization_id"],
            self.policy["authority"]["authorization_id"],
        )

    def test_impossible_sample_flow_rational_and_lineage_are_rejected(self) -> None:
        impossible_flow = deepcopy(self.measurement)
        impossible_flow["sample_flow"]["usable"] = 9
        impossible_flow["measurement_id"] = derive_content_id(
            impossible_flow, "measurement_id", "meas-"
        )
        with self.assertRaises(QualificationContractError):
            validate_measurement(impossible_flow, self.resolver)

        unreduced = deepcopy(self.measurement)
        unreduced["metrics"]["accuracy"]["value"] = {
            "numerator": 8,
            "denominator": 10,
        }
        unreduced["measurement_id"] = derive_content_id(
            unreduced, "measurement_id", "meas-"
        )
        with self.assertRaises(QualificationContractError):
            validate_measurement(unreduced, self.resolver)

        missing_basis = deepcopy(self.measurement)
        missing_basis["metrics"]["accuracy"]["basis_ids"][0] = "basis-" + "0" * 64
        missing_basis["metrics"]["accuracy"]["basis_ids"] = canonical_sorted(
            missing_basis["metrics"]["accuracy"]["basis_ids"]
        )
        missing_basis["measurement_id"] = derive_content_id(
            missing_basis, "measurement_id", "meas-"
        )
        with self.assertRaises(QualificationContractError):
            validate_measurement(missing_basis, self.resolver)

    def test_fate_and_outcome_metric_aliases_are_rejected_but_fate_covariate_is_valid(
        self,
    ) -> None:
        validate_measurement(self.measurement, self.resolver)
        self.assertEqual(self.measurement["covariates"][0]["name"], "downstream_fate")

        for alias in ("downstream-fate", "fate_score", "attempt.outcome"):
            with self.subTest(alias=alias):
                policy = deepcopy(self.policy)
                policy["criteria"][0]["metric"] = alias
                policy["policy_id"] = derive_content_id(policy, "policy_id", "pol-")
                with self.assertRaises(QualificationContractError):
                    validate_policy(policy, self.resolver)

    def test_bad_policy_rate_and_authorization_id_are_rejected(self) -> None:
        policy = deepcopy(self.policy)
        policy["requirements"]["maximum_missing_rate"] = {
            "numerator": 2,
            "denominator": 1,
        }
        policy["policy_id"] = derive_content_id(policy, "policy_id", "pol-")
        with self.assertRaises(QualificationContractError):
            validate_policy(policy, self.resolver)

        authority = deepcopy(self.policy["authority"])
        authority["binding_ids"] = ["bnd-" + "0" * 64]
        with self.assertRaises(QualificationContractError):
            validate_authorization(authority, self.resolver)

    def test_qualification_authorization_pins_policy_semantics(self) -> None:
        changed = deepcopy(self.policy)
        changed["criteria"][0]["threshold"] = {
            "numerator": 9,
            "denominator": 10,
        }
        changed["policy_id"] = derive_content_id(changed, "policy_id", "pol-")

        claim = build_fixture_claim(self.resolver, self.measurement, changed)

        self.assertEqual(claim["qualification"]["status"], "advisory")
        self.assertIn(
            "qualification-authorization-policy-mismatch",
            claim["qualification"]["limitations"],
        )

    def test_basis_authority_source_must_be_typed_and_scoped(self) -> None:
        measurement = deepcopy(self.measurement)
        for basis in measurement["evidence_basis"]:
            authorization = json.loads(
                self.resolver.resolve(basis["authorization_ref"]).decode("utf-8")
            )
            authorization["authority_source_ref"] = self.resolver.add(
                "model-judgment", "judgment/1", {"decision": "looks fine"}
            )
            authorization["authorization_id"] = derive_content_id(
                authorization, "authorization_id", "basis-auth-"
            )
            basis["authorization_ref"] = self.resolver.add(
                "evidence-basis-authorization",
                "caplab-evidence-basis-authorization/1",
                authorization,
            )
            basis["basis_id"] = derive_content_id(basis, "basis_id", "basis-")
        measurement["evidence_basis"] = canonical_sorted(measurement["evidence_basis"])
        for metric in measurement["metrics"].values():
            metric["basis_ids"] = canonical_sorted(
                [basis["basis_id"] for basis in measurement["evidence_basis"]]
            )
        measurement["measurement_id"] = derive_content_id(
            measurement, "measurement_id", "meas-"
        )

        with self.assertRaises(QualificationContractError):
            validate_measurement(measurement, self.resolver)

    def test_resolved_json_requires_canonical_application_json(self) -> None:
        policy = deepcopy(self.policy)
        pretty = json.dumps(policy, indent=2).encode("utf-8")
        policy_ref = self.resolver.add(
            "qualification-policy",
            "caplab-qualification-policy/1",
            pretty,
            media_type="text/plain",
        )
        measurement_ref = self.resolver.add(
            "measurement", "caplab-measurement/1", self.measurement
        )

        with self.assertRaises(QualificationContractError):
            build_claim(
                self.measurement,
                policy,
                measurement_ref=measurement_ref,
                policy_ref=policy_ref,
                generated_at="2026-06-02T00:00:00Z",
                supersedes=[],
                resolver=self.resolver,
                caplab_version="0.1.0",
                caplab_commit="3" * 40,
                caplab_package_sha256="4" * 64,
            )


class ClaimEvaluationTests(unittest.TestCase):
    def test_fate_is_stored_but_structurally_absent_from_decision_projection(
        self,
    ) -> None:
        resolver = MemoryResolver()
        measurement = make_measurement(resolver, include_fate=True)
        policy = make_policy(resolver, measurement)

        claim = build_fixture_claim(resolver, measurement, policy)

        self.assertEqual(claim["qualification"]["status"], "qualified")
        self.assertEqual(claim["assertion_type"], "decision")
        self.assertNotIn("covariates", claim["measurement"])
        self.assertNotIn(
            "downstream_fate", canonical_json(claim["qualification"]).decode()
        )
        self.assertEqual(validate_claim(claim, resolver), claim)

    def test_fate_or_model_conditioned_selection_is_advisory(self) -> None:
        for condition in ("downstream_fate", "model_judgment", "human_judgment"):
            with self.subTest(condition=condition):
                resolver = MemoryResolver()
                measurement = make_measurement(resolver, conditioned_on=[condition])
                policy = make_policy(resolver, measurement)
                claim = build_fixture_claim(resolver, measurement, policy)

                self.assertEqual(claim["qualification"]["status"], "advisory")
                expected = {
                    "downstream_fate": "fate-conditioned-case-selection:accuracy",
                    "model_judgment": "model-conditioned-case-selection:accuracy",
                    "human_judgment": "conditioned-case-selection:human_judgment:accuracy",
                }[condition]
                self.assertIn(expected, claim["qualification"]["limitations"])

    def test_model_judgment_is_advisory_only(self) -> None:
        resolver = MemoryResolver()
        measurement = make_measurement(resolver, basis_kind="model-judgment")
        policy = make_policy(
            resolver, measurement, permitted_basis_kind="mechanical-oracle"
        )
        claim = build_fixture_claim(resolver, measurement, policy)

        self.assertEqual(claim["qualification"]["status"], "advisory")
        self.assertIn(
            "evidence-basis-kind-not-permitted", claim["qualification"]["limitations"]
        )

    def test_mechanical_and_human_authorized_bases_can_decide(self) -> None:
        for kind in ("mechanical-oracle", "human-authorized"):
            with self.subTest(kind=kind):
                resolver = MemoryResolver()
                measurement = make_measurement(resolver, basis_kind=kind)
                policy = make_policy(resolver, measurement, permitted_basis_kind=kind)
                claim = build_fixture_claim(resolver, measurement, policy)
                self.assertEqual(claim["qualification"]["status"], "qualified")
                self.assertEqual(validate_claim(claim, resolver), claim)

    def test_case_selection_basis_need_not_be_mislabeled_as_metric_derivation(
        self,
    ) -> None:
        resolver = MemoryResolver()
        measurement = make_measurement(resolver)
        selection_basis_id = next(
            basis["basis_id"]
            for basis in measurement["evidence_basis"]
            if basis["role"] == "case-selection"
        )
        measurement["metrics"]["accuracy"]["basis_ids"].remove(selection_basis_id)
        measurement["measurement_id"] = derive_content_id(
            measurement, "measurement_id", "meas-"
        )
        policy = make_policy(resolver, measurement)
        claim = build_fixture_claim(resolver, measurement, policy)
        self.assertEqual(claim["qualification"]["status"], "qualified")

    def test_capability_card_metric_inventory_is_authoritative(self) -> None:
        resolver = MemoryResolver()
        measurement = make_measurement(resolver)
        card = resolver.add(
            "capability-card",
            "caplab-capability-card/1",
            {
                "schema_version": "caplab-capability-card/1",
                "qualification_metrics": ["precision"],
            },
        )
        measurement["capability"]["card_ref"] = card
        for basis in measurement["evidence_basis"]:
            authorization = json.loads(
                resolver.resolve(basis["authorization_ref"]).decode("utf-8")
            )
            authorization["capability"] = measurement["capability"]
            authorization["authorization_id"] = derive_content_id(
                authorization, "authorization_id", "basis-auth-"
            )
            basis["authorization_ref"] = resolver.add(
                "evidence-basis-authorization",
                "caplab-evidence-basis-authorization/1",
                authorization,
            )
            basis["basis_id"] = derive_content_id(basis, "basis_id", "basis-")
        measurement["evidence_basis"] = canonical_sorted(measurement["evidence_basis"])
        measurement["metrics"]["accuracy"]["basis_ids"] = canonical_sorted(
            [basis["basis_id"] for basis in measurement["evidence_basis"]]
        )
        measurement["measurement_id"] = derive_content_id(
            measurement, "measurement_id", "meas-"
        )
        policy = make_policy(resolver, measurement)
        with self.assertRaises(QualificationContractError):
            build_fixture_claim(resolver, measurement, policy)

    def test_same_measurement_with_different_thresholds_has_different_outcomes(
        self,
    ) -> None:
        resolver = MemoryResolver()
        measurement = make_measurement(resolver)
        passing = make_policy(
            resolver, measurement, threshold={"numerator": 3, "denominator": 4}
        )
        failing = make_policy(
            resolver, measurement, threshold={"numerator": 9, "denominator": 10}
        )

        qualified = build_fixture_claim(resolver, measurement, passing)
        unqualified = build_fixture_claim(resolver, measurement, failing)

        self.assertEqual(qualified["qualification"]["status"], "qualified")
        self.assertEqual(unqualified["qualification"]["status"], "unqualified")
        self.assertNotEqual(qualified["claim_id"], unqualified["claim_id"])

    def test_claim_identity_excludes_only_trusted_issuance_time(self) -> None:
        resolver = MemoryResolver()
        measurement = make_measurement(resolver)
        policy = make_policy(resolver, measurement)
        measurement_before = deepcopy(measurement)
        policy_before = deepcopy(policy)
        first = build_fixture_claim(
            resolver, measurement, policy, generated_at="2026-06-02T00:00:00Z"
        )
        second = build_fixture_claim(
            resolver, measurement, policy, generated_at="2026-06-03T00:00:00Z"
        )

        self.assertEqual(first["claim_id"], second["claim_id"])
        self.assertNotEqual(first["generated_at"], second["generated_at"])
        self.assertEqual(measurement, measurement_before)
        self.assertEqual(policy, policy_before)

    def test_unknown_bytes_or_observed_route_are_advisory(self) -> None:
        for mutation in ("weights", "executable", "route"):
            with self.subTest(mutation=mutation):
                resolver = MemoryResolver()
                binding = make_binding(resolver)
                if mutation == "weights":
                    binding["model"]["weights_ref"] = None
                    binding["model"]["weights_unavailable_reason"] = (
                        "provider does not expose weights"
                    )
                elif mutation == "executable":
                    binding["harness"]["executable_ref"] = None
                    binding["harness"]["executable_unavailable_reason"] = (
                        "managed harness"
                    )
                else:
                    binding["provider_or_path"]["resolution"] = "observed-route"
                    binding["provider_or_path"]["observed_at"] = "2026-06-01T00:00:00Z"
                    provider = binding["provider_or_path"]
                    provider["route_ref"] = resolver.add(
                        "provider-route",
                        "caplab-provider-route/1",
                        {
                            "schema_version": "caplab-provider-route/1",
                            **{
                                key: provider[key]
                                for key in (
                                    "kind",
                                    "identifier",
                                    "revision",
                                    "resolution",
                                    "observed_at",
                                )
                            },
                        },
                    )
                binding["binding_id"] = derive_content_id(binding, "binding_id", "bnd-")
                measurement = make_measurement(resolver, binding=binding)
                policy = make_policy(resolver, measurement)
                claim = build_fixture_claim(resolver, measurement, policy)
                self.assertEqual(claim["qualification"]["status"], "advisory")

    def test_protocol_corpus_capability_and_binding_mismatches_are_rejected(
        self,
    ) -> None:
        resolver = MemoryResolver()
        measurement = make_measurement(resolver)
        base_policy = make_policy(resolver, measurement, with_authority=False)
        different_card = resolver.add(
            "capability-card",
            "caplab-capability-card/1",
            {
                "schema_version": "caplab-capability-card/1",
                "qualification_metrics": ["accuracy"],
                "revision": "different",
            },
        )
        mutations = {
            "protocol": ("applies_to", "protocol_sha256", "0" * 64),
            "corpus": ("applies_to", "corpus_sha256", "0" * 64),
            "card": ("capability", "card_ref", different_card),
            "role": ("capability", "role", "review"),
            "domain": ("capability", "domain", "rust"),
            "distribution": ("capability", "distribution", "other-population"),
        }
        for label, (section, field, value) in mutations.items():
            with self.subTest(label=label):
                policy = deepcopy(base_policy)
                policy[section][field] = value
                policy["policy_id"] = derive_content_id(policy, "policy_id", "pol-")
                with self.assertRaises(QualificationContractError):
                    build_fixture_claim(resolver, measurement, policy)

        other_binding = make_binding(resolver)
        other_binding["reasoning_effort"] = "medium"
        other_binding["binding_id"] = derive_content_id(
            other_binding, "binding_id", "bnd-"
        )
        with self.assertRaises(QualificationContractError):
            build_fixture_claim(
                resolver,
                measurement,
                base_policy,
                binding=other_binding,
            )

    def test_missing_evidence_and_authority_scope_or_time_only_yield_advisory(
        self,
    ) -> None:
        scenarios: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
        resolver = MemoryResolver()
        measurement = make_measurement(resolver)
        empty_evidence = deepcopy(measurement)
        empty_evidence["evidence"]["bundle_ref"] = resolver.add(
            "evidence-bundle", "bundle/1", b""
        )
        empty_evidence["evidence"]["run_refs"] = []
        empty_evidence["measurement_id"] = derive_content_id(
            empty_evidence, "measurement_id", "meas-"
        )
        scenarios.append(
            ("missing", empty_evidence, make_policy(resolver, empty_evidence))
        )
        scenarios.append(
            (
                "expired",
                measurement,
                make_policy(
                    resolver,
                    measurement,
                    valid_from="2025-01-01T00:00:00Z",
                    valid_until="2025-12-31T23:59:59Z",
                ),
            )
        )
        scenarios.append(
            (
                "not-yet-valid",
                measurement,
                make_policy(
                    resolver,
                    measurement,
                    valid_from="2027-01-01T00:00:00Z",
                    valid_until="2027-12-31T23:59:59Z",
                ),
            )
        )
        status_policy = make_policy(resolver, measurement)
        status_policy["authority"]["permitted_statuses"] = ["unqualified"]
        reseal_qualification_authority(resolver, status_policy)
        scenarios.append(("status", measurement, status_policy))
        binding_policy = make_policy(resolver, measurement)
        binding_policy["authority"]["binding_ids"] = ["bnd-" + "0" * 64]
        reseal_qualification_authority(resolver, binding_policy)
        scenarios.append(("binding", measurement, binding_policy))
        capability_policy = make_policy(resolver, measurement)
        capability_policy["authority"]["capability"]["role"] = "review"
        reseal_qualification_authority(resolver, capability_policy)
        scenarios.append(("capability", measurement, capability_policy))
        named_policy = make_policy(resolver, measurement)
        named_policy["authority"]["policy"]["name"] = "different-policy"
        reseal_qualification_authority(resolver, named_policy)
        scenarios.append(("policy", measurement, named_policy))

        for label, measured, policy in scenarios:
            with self.subTest(label=label):
                claim = build_fixture_claim(resolver, measured, policy)
                self.assertEqual(claim["qualification"]["status"], "advisory")

    def test_basis_authorization_scope_and_time_must_match_measurement(self) -> None:
        resolver = MemoryResolver()
        measurement = make_measurement(resolver)
        basis = measurement["evidence_basis"][0]
        authorization_ref = basis["authorization_ref"]
        authorization = deepcopy(
            json.loads(resolver.resolve(authorization_ref).decode("utf-8"))
        )
        authorization["basis_role"] = (
            "truth" if basis["role"] != "truth" else "case-selection"
        )
        authorization["authorization_id"] = derive_content_id(
            authorization, "authorization_id", "basis-auth-"
        )
        basis["authorization_ref"] = resolver.add(
            "evidence-basis-authorization",
            "caplab-evidence-basis-authorization/1",
            authorization,
        )
        basis["basis_id"] = derive_content_id(basis, "basis_id", "basis-")
        measurement["evidence_basis"] = canonical_sorted(measurement["evidence_basis"])
        measurement["measurement_id"] = derive_content_id(
            measurement, "measurement_id", "meas-"
        )
        with self.assertRaises(QualificationContractError):
            validate_measurement(measurement, resolver)

    def test_impossible_claim_result_and_self_supersession_are_rejected(self) -> None:
        resolver = MemoryResolver()
        measurement = make_measurement(resolver)
        policy = make_policy(resolver, measurement)
        claim = build_fixture_claim(resolver, measurement, policy)

        impossible = deepcopy(claim)
        impossible["qualification"]["criteria"][0]["result"] = "not-met"
        with self.assertRaises(QualificationContractError):
            validate_claim(impossible, resolver)

        self_referential = deepcopy(claim)
        self_referential["supersedes"] = [self_referential["claim_id"]]
        with self.assertRaises(QualificationContractError):
            validate_claim(self_referential, resolver)

    def test_unmeasured_requires_an_explicit_binding_and_has_no_measurement_evidence(
        self,
    ) -> None:
        resolver = MemoryResolver()
        measurement = make_measurement(resolver)
        policy = make_policy(resolver, measurement)
        policy_ref = resolver.add(
            "qualification-policy", "caplab-qualification-policy/1", policy
        )

        claim = build_claim(
            None,
            policy,
            binding=measurement["binding"],
            measurement_ref=None,
            policy_ref=policy_ref,
            generated_at="2026-06-02T00:00:00Z",
            supersedes=[],
            resolver=resolver,
            caplab_version="0.1.0",
            caplab_commit="3" * 40,
            caplab_package_sha256="4" * 64,
        )
        self.assertEqual(claim["qualification"]["status"], "unmeasured")
        self.assertIsNone(claim["measurement"])
        self.assertEqual(claim["evidence"], {"bundle_ref": None, "run_refs": []})
        self.assertEqual(validate_claim(claim, resolver), claim)

        with self.assertRaises(QualificationContractError):
            build_claim(
                None,
                policy,
                measurement_ref=None,
                policy_ref=policy_ref,
                generated_at="2026-06-02T00:00:00Z",
                supersedes=[],
                resolver=resolver,
                caplab_version="0.1.0",
                caplab_commit="3" * 40,
                caplab_package_sha256="4" * 64,
            )


if __name__ == "__main__":
    unittest.main()
