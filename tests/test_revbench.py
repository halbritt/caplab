from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from caplab.qualification.ledger import FilesystemQualificationLedger
from caplab.revbench import RevbenchContractError, prepare, score
from caplab.runtime.canonical import canonical_json, sha256_hex


class MemoryRegistrar:
    def __init__(self) -> None:
        self.documents: dict[str, bytes] = {}

    def register_document(self, document, *, kind, schema, registration_id):
        data = canonical_json(document)
        digest = sha256_hex(data)
        self.documents[digest] = data
        return {
            "kind": kind,
            "schema": schema,
            "media_type": "application/json",
            "sha256": digest,
            "byte_count": len(data),
            "locator": f"objects/sha256/{digest[:2]}/{digest}",
            "registration_ref": f"test:{registration_id}",
            "custody": None,
        }

    def resolve(self, ref):
        return self.documents[ref["sha256"]]


class LedgerRegistrar:
    def __init__(self, root: Path) -> None:
        self.ledger = FilesystemQualificationLedger(root)

    def register_document(self, document, *, kind, schema, registration_id):
        del registration_id
        return self.ledger.register_document(document, kind=kind, schema=schema)

    def resolve(self, ref):
        return self.ledger.resolve(ref)


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


def make_binding(registrar: MemoryRegistrar):
    refs = {
        name: registered(registrar, name)
        for name in (
            "route",
            "command",
            "version-probe",
            "inference",
            "instructions",
            "knowledge",
            "tools",
            "permissions",
            "sandbox",
            "runtime",
        )
    }
    binding = {
        "schema_version": "caplab-binding/1",
        "model": {
            "model_id": "example/model",
            "revision": "immutable-r1",
            "weights_ref": None,
            "weights_unavailable_reason": "provider does not expose weights",
        },
        "provider_or_path": {
            "kind": "direct-provider",
            "identifier": "example",
            "revision": "route-r1",
            "resolution": "immutable",
            "observed_at": None,
            "route_ref": refs["route"],
        },
        "harness": {
            "harness_id": "native-example",
            "harness_version": "1",
            "executable_ref": None,
            "executable_unavailable_reason": "provider-managed native harness",
            "command_ref": refs["command"],
            "version_probe_ref": refs["version-probe"],
        },
        "reasoning_effort": "high",
        "configuration": {
            f"{name}_ref": refs[name]
            for name in (
                "inference",
                "instructions",
                "knowledge",
                "tools",
                "permissions",
                "sandbox",
                "runtime",
            )
        },
    }
    binding["binding_id"] = "bnd-" + sha256_hex(canonical_json(binding))
    return binding


def make_spec(registrar: MemoryRegistrar):
    binding = make_binding(registrar)
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
                kind="revbench-case",
                schema="caplab-revbench-case/1",
            )
            for case in cases
        ],
        key=canonical_json,
    )
    selection_identity = {
        "schema_version": "caplab-case-selection-manifest/1",
        "population_ref": registered(registrar, "population", kind="case-population"),
        "included_case_refs": included_case_refs,
        "excluded_case_refs": [],
        "selection_inputs": [],
        "exclusion_inputs": [],
        "conditioned_on": [],
        "authorization_ref": registered(
            registrar, "selection-authorization", kind="decision-record"
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
    authority_source_ref = registered(
        registrar, "basis-authority", kind="decision-record"
    )
    method_ref = registered(registrar, "revbench-method", kind="protocol")
    authorizations = {}
    for key, role in (
        ("truth", "truth"),
        ("case_selection", "case-selection"),
        ("metric_derivation", "metric-derivation"),
    ):
        identity = {
            "schema_version": "caplab-evidence-basis-authorization/1",
            "authority_source_ref": authority_source_ref,
            "authorized_by": "repository owner",
            "delegate_or_mechanism": "caplab.revbench v1 deterministic mechanism",
            "binding_ids": [binding["binding_id"]],
            "capability": capability,
            "experiment": {"family": "revbench", "version": "1"},
            "protocol_ref": protocol,
            "corpus_ref": corpus,
            "case_selection_ref": case_selection_ref,
            "method_ref": method_ref,
            "basis_kind": "mechanical-oracle",
            "basis_role": role,
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
                kind="revbench-case",
                schema="caplab-revbench-case/1",
            )
            for case in spec["cases"]
        ],
        key=canonical_json,
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


def make_reviews(registrar: MemoryRegistrar, manifest, outcomes=None):
    outcomes = outcomes or {}
    attempts = []
    native_system_contract_ref = registered(
        registrar,
        "native-system-contract",
        {"schema_version": "caplab.native-agent-systems/v1", "systems": []},
        kind="native-agent-systems-contract",
        schema="caplab.native-agent-systems/v1",
    )
    for case in manifest["cases"]:
        for arm in ("control", "mutant"):
            disposition, verdict, anchors = outcomes.get(
                (case["case_id"], arm),
                (
                    "complete",
                    "clean" if arm == "control" else "defect",
                    [] if arm == "control" else [case["defect_anchor"]],
                ),
            )
            prompt_ref = registered(
                registrar,
                f"prompt-{case['case_id']}-{arm}",
                {"artifact": case[arm]["content"]},
                kind="prompt",
                schema="caplab-revbench-prompt/1",
            )
            output_ref = registered(
                registrar,
                f"output-{case['case_id']}-{arm}",
                {"verdict": verdict, "anchors": anchors},
                kind="native-output",
                schema="caplab-native-output/1",
            )
            capture_ref = registered(
                registrar,
                f"capture-{case['case_id']}-{arm}",
                {"case_id": case["case_id"], "arm": arm},
                kind="native-attempt-capture",
                schema="caplab-native-attempt-capture/1",
            )
            attestation_identity = {
                "schema_version": "caplab-native-attempt-attestation/1",
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
                "observed_at": "2026-08-14T11:59:59Z",
                "observed_binding": copy.deepcopy(manifest["binding"]),
                "native_system_contract_ref": native_system_contract_ref,
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
                f"attestation-{case['case_id']}-{arm}",
                attestation,
                kind="native-attempt-attestation",
                schema="caplab-native-attempt-attestation/1",
            )
            envelope_identity = {
                "schema_version": "caplab-native-review-attempt/1",
                "experiment_id": manifest["experiment_id"],
                "case_id": case["case_id"],
                "arm": arm,
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
                f"attempt-{case['case_id']}-{arm}",
                envelope,
                kind="attempt",
                schema="caplab-native-review-attempt/1",
            )
            attempts.append(
                {
                    "case_id": case["case_id"],
                    "arm": arm,
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
    return {
        "schema_version": "caplab-revbench-reviews/1",
        "experiment_id": manifest["experiment_id"],
        "observed_at": "2026-08-14T12:00:00Z",
        "attempts": attempts,
    }


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
        self.assertEqual(values["discrimination"], {"numerator": 0, "denominator": 2})
        self.assertEqual(values["anchor_hit_rate"], {"numerator": 1, "denominator": 2})
        self.assertEqual(values["conformance_rate"], {"numerator": 4, "denominator": 4})
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
                ("case-a", "mutant"): ("complete", "defect", []),
                ("case-b", "mutant"): ("complete", "defect", ["/not-the-defect"]),
            },
        )

        measurement = score(manifest, reviews, registrar)

        self.assertEqual(
            measurement["metrics"]["catch_rate"]["value"],
            {"numerator": 0, "denominator": 2},
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
            {("case-b", "mutant"): ("complete", "invalid", [])},
        )
        invalid = score(manifest, reviews, registrar)
        self.assertEqual(invalid["disposition"], "invalid")
        self.assertEqual(invalid["sample_flow"]["excluded"], 2)
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
        with self.assertRaisesRegex(RevbenchContractError, "attested observed Binding"):
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
                    "run",
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


if __name__ == "__main__":
    unittest.main()
