from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from caplab.qualification import (
    derive_content_id,
    validate_binding,
    validate_measurement,
)
from caplab.qualification.ledger import FilesystemQualificationLedger
from caplab.runtime.canonical import canonical_json
from tools import caplab_revbench_first_run as first_run_tool


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "caplab_revbench_first_run.py"
CONTRACTS = ROOT / "docs" / "product" / "contracts"
CONTENT_REF_FIELDS = {
    "kind",
    "schema",
    "media_type",
    "sha256",
    "byte_count",
    "locator",
    "registration_ref",
    "custody",
}
AUXILIARY_REGISTERED_SCHEMAS = {
    "caplab-binding-configuration/1",
    "caplab-native-harness-command/1",
    "caplab-native-harness-version-command/1",
    "caplab-native-harness-version-probe/1",
    "caplab-provider-route/1",
    "caplab-revbench-case-selection-basis/1",
    "caplab-revbench-case/1",
    "caplab-revbench-evidence-bundle/1",
    "caplab-revbench-local-fixture/1",
    "caplab-revbench-metric-derivation-basis/1",
    "caplab-revbench-response-derivation/1",
    "caplab-revbench-truth-basis/1",
    "caplab.native-agent-systems/v1",
}


def _run(
    arguments: list[str],
    *,
    cwd: Path,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    process_environment = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPATH=str(ROOT / "src"),
    )
    process_environment.update(environment or {})
    return subprocess.run(
        arguments,
        cwd=cwd,
        env=process_environment,
        check=False,
        capture_output=True,
    )


def _workspace_content_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _content_refs(value: object) -> list[dict[str, object]]:
    if isinstance(value, dict):
        if set(value) == CONTENT_REF_FIELDS:
            return [value]
        return [ref for nested in value.values() for ref in _content_refs(nested)]
    if isinstance(value, list):
        return [ref for nested in value for ref in _content_refs(nested)]
    return []


def _registered_document_graph(
    ledger: FilesystemQualificationLedger,
    roots: list[dict[str, object]],
) -> list[tuple[dict[str, object], dict[str, object]]]:
    pending = [ref for document in roots for ref in _content_refs(document)]
    resolved_refs: set[bytes] = set()
    documents: list[tuple[dict[str, object], dict[str, object]]] = []
    while pending:
        ref = pending.pop()
        ref_key = canonical_json(ref)
        if ref_key in resolved_refs:
            continue
        payload = ledger.resolve(ref)
        self_digest = hashlib.sha256(payload).hexdigest()
        if self_digest != ref["sha256"]:
            raise AssertionError("resolved reference digest changed")
        resolved_refs.add(ref_key)
        if ref["media_type"] != "application/json":
            continue
        document = json.loads(payload)
        if not isinstance(document, dict) or canonical_json(document) != payload:
            raise AssertionError("registered JSON is not a canonical object")
        documents.append((ref, document))
        pending.extend(_content_refs(document))
    return documents


def _scaffold_workspace(
    workspace: Path, *, valid_for_seconds: int = 600
) -> subprocess.CompletedProcess[bytes]:
    return _run(
        [
            sys.executable,
            str(TOOL),
            "scaffold",
            str(workspace),
            "--authorized-by",
            "CAPLAB test operator",
            "--delegation-source",
            "explicit local first-run evidence delegation",
            "--valid-for-seconds",
            str(valid_for_seconds),
        ],
        cwd=ROOT,
    )


def _prepare_workspace(workspace: Path) -> subprocess.CompletedProcess[bytes]:
    return _run(
        [
            sys.executable,
            "-m",
            "caplab.revbench",
            "prepare",
            "--spec",
            str(workspace / "spec.json"),
            "--ledger",
            str(workspace / "ledger"),
            "--output",
            str(workspace / "manifest.json"),
            "--reference-output",
            str(workspace / "manifest-ref.json"),
        ],
        cwd=ROOT,
    )


def _authorize_workspace(
    workspace: Path, *, valid_for_seconds: int = 600
) -> subprocess.CompletedProcess[bytes]:
    return _run(
        [
            sys.executable,
            str(TOOL),
            "authorize",
            str(workspace),
            "--authorized-by",
            "CAPLAB test operator",
            "--delegation-source",
            "explicit local first-run execution delegation",
            "--valid-for-seconds",
            str(valid_for_seconds),
        ],
        cwd=ROOT,
    )


def _execute_workspace(
    workspace: Path, *, authorization_ref: Path | None = None
) -> subprocess.CompletedProcess[bytes]:
    return _run(
        [
            sys.executable,
            "-m",
            "caplab.revbench",
            "execute",
            "--manifest",
            str(workspace / "manifest.json"),
            "--execution-authorization-ref",
            str(authorization_ref or workspace / "execution-authorization-ref.json"),
            "--ledger",
            str(workspace / "ledger"),
            "--output",
            str(workspace / "reviews.json"),
        ],
        cwd=ROOT,
    )


class FirstRunTests(unittest.TestCase):
    def test_scaffold_refuses_when_fixed_bubblewrap_adapter_is_unavailable(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "workspace"
            stderr = io.StringIO()

            # Bubblewrap is a fixed host boundary; do not rename the real adapter.
            with mock.patch.object(
                first_run_tool, "BUBBLEWRAP", root / "missing-bwrap"
            ):
                with redirect_stderr(stderr):
                    return_code = first_run_tool.main(
                        [
                            "scaffold",
                            str(workspace),
                            "--authorized-by",
                            "CAPLAB test operator",
                            "--delegation-source",
                            "explicit local first-run evidence delegation",
                            "--valid-for-seconds",
                            "600",
                        ]
                    )

            self.assertEqual(return_code, 2)
            self.assertIn("bubblewrap_unavailable", stderr.getvalue())
            self.assertFalse(workspace.exists())

    def test_execute_refuses_persistent_fixture_executable_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            scaffolded = _scaffold_workspace(workspace)
            self.assertEqual(scaffolded.returncode, 0, scaffolded.stderr.decode())
            prepared = _prepare_workspace(workspace)
            self.assertEqual(prepared.returncode, 0, prepared.stderr.decode())
            authorized = _authorize_workspace(workspace)
            self.assertEqual(authorized.returncode, 0, authorized.stderr.decode())
            executable = workspace / "fixture" / "fake-native"
            with executable.open("ab") as stream:
                stream.write(b"drift")

            refused = _execute_workspace(workspace)

            self.assertEqual(refused.returncode, 2)
            self.assertIn(b"does not match executable bytes", refused.stderr)
            self.assertFalse((workspace / "reviews.json").exists())

    def test_execute_refuses_expired_first_run_authorization_before_launch(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            scaffolded = _scaffold_workspace(workspace)
            self.assertEqual(scaffolded.returncode, 0, scaffolded.stderr.decode())
            prepared = _prepare_workspace(workspace)
            self.assertEqual(prepared.returncode, 0, prepared.stderr.decode())
            authorized = _authorize_workspace(workspace, valid_for_seconds=1)
            self.assertEqual(authorized.returncode, 0, authorized.stderr.decode())
            time.sleep(2.1)

            refused = _execute_workspace(workspace)

            self.assertEqual(refused.returncode, 2)
            self.assertIn(b"outside the execution authorization", refused.stderr)
            self.assertFalse((workspace / "reviews.json").exists())

    def test_execute_refuses_authorization_scoped_to_another_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            scaffolded = _scaffold_workspace(workspace)
            self.assertEqual(scaffolded.returncode, 0, scaffolded.stderr.decode())
            prepared = _prepare_workspace(workspace)
            self.assertEqual(prepared.returncode, 0, prepared.stderr.decode())
            authorized = _authorize_workspace(workspace)
            self.assertEqual(authorized.returncode, 0, authorized.stderr.decode())
            ledger = FilesystemQualificationLedger((workspace / "ledger").resolve())
            delegation = json.loads(
                (workspace / "execution-delegation.json").read_bytes()
            )
            authorization = json.loads(
                (workspace / "execution-authorization.json").read_bytes()
            )
            authorization["binding_id"] = "bnd-" + "0" * 64
            scope_fields = (
                "experiment_id",
                "manifest_ref",
                "binding_id",
                "native_system_contract_ref",
                "command_ref",
                "version_probe_ref",
                "effect_class",
                "limits",
            )
            delegation["scope"] = {
                field: authorization[field] for field in scope_fields
            }
            delegation["delegation_id"] = derive_content_id(
                delegation, "delegation_id", "delegation-"
            )
            authorization["authority_source_ref"] = ledger.register_document(
                delegation,
                kind="authorization-delegation",
                schema="caplab-authorization-delegation/1",
            )
            authorization["authorization_id"] = derive_content_id(
                authorization,
                "authorization_id",
                "revbench-execution-auth-",
            )
            mismatched_ref = ledger.register_document(
                authorization,
                kind="revbench-execution-authorization",
                schema="caplab-revbench-execution-authorization/1",
            )
            mismatched_ref_path = workspace / "mismatched-authorization-ref.json"
            mismatched_ref_path.write_bytes(canonical_json(mismatched_ref) + b"\n")

            refused = _execute_workspace(
                workspace, authorization_ref=mismatched_ref_path
            )

            self.assertEqual(refused.returncode, 2)
            self.assertIn(b"binding_id", refused.stderr)
            self.assertFalse((workspace / "reviews.json").exists())

    def test_authorize_refuses_overwrite_before_mutating_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            scaffolded = _scaffold_workspace(workspace)
            self.assertEqual(scaffolded.returncode, 0, scaffolded.stderr.decode())
            prepared = _prepare_workspace(workspace)
            self.assertEqual(prepared.returncode, 0, prepared.stderr.decode())
            authorized = _authorize_workspace(workspace)
            self.assertEqual(authorized.returncode, 0, authorized.stderr.decode())
            retained_hashes = _workspace_content_hashes(workspace)
            time.sleep(1.1)

            refused = _authorize_workspace(workspace)

            self.assertEqual(refused.returncode, 2)
            self.assertIn(b"output_exists", refused.stderr)
            self.assertEqual(_workspace_content_hashes(workspace), retained_hashes)

    def test_authorize_refuses_provider_shaped_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            scaffolded = _scaffold_workspace(workspace)
            self.assertEqual(scaffolded.returncode, 0, scaffolded.stderr.decode())
            prepared = _prepare_workspace(workspace)
            self.assertEqual(prepared.returncode, 0, prepared.stderr.decode())
            manifest_path = workspace / "manifest.json"
            manifest = json.loads(manifest_path.read_bytes())
            manifest["binding"]["provider_or_path"]["kind"] = "direct-provider"
            manifest["binding"]["provider_or_path"]["identifier"] = "openai"
            manifest_path.chmod(0o600)
            manifest_path.write_bytes(canonical_json(manifest) + b"\n")

            refused = _authorize_workspace(workspace)

            self.assertEqual(refused.returncode, 2)
            self.assertIn(b"local_fixture_manifest_required", refused.stderr)
            self.assertFalse((workspace / "execution-authorization.json").exists())

    def test_inspect_refuses_a_provider_shaped_workspace_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            scaffolded = _scaffold_workspace(workspace)
            self.assertEqual(scaffolded.returncode, 0, scaffolded.stderr.decode())
            binding_path = workspace / "inputs" / "binding.json"
            binding = json.loads(binding_path.read_bytes())
            binding["provider_or_path"]["kind"] = "direct-provider"
            binding["provider_or_path"]["identifier"] = "provider-shaped-test"
            binding["binding_id"] = derive_content_id(binding, "binding_id", "bnd-")
            binding_path.chmod(0o600)
            binding_path.write_bytes(canonical_json(binding) + b"\n")
            before = _workspace_content_hashes(workspace)

            refused = _run(
                [sys.executable, str(TOOL), "inspect", str(workspace)],
                cwd=ROOT,
            )

            self.assertEqual(refused.returncode, 2)
            self.assertIn(b"workspace_binding_mismatch", refused.stderr)
            self.assertNotIn(b"provider_execution:", refused.stdout)
            self.assertEqual(_workspace_content_hashes(workspace), before)

    def test_authorize_refuses_drift_from_the_public_prepared_manifest(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            scaffolded = _scaffold_workspace(workspace)
            self.assertEqual(scaffolded.returncode, 0, scaffolded.stderr.decode())
            prepared = _prepare_workspace(workspace)
            self.assertEqual(prepared.returncode, 0, prepared.stderr.decode())
            manifest_path = workspace / "manifest.json"
            manifest = json.loads(manifest_path.read_bytes())
            manifest["experiment_id"] = "revbench-" + "0" * 64
            manifest_path.chmod(0o600)
            manifest_path.write_bytes(canonical_json(manifest) + b"\n")
            before = _workspace_content_hashes(workspace)

            refused = _authorize_workspace(workspace)

            self.assertEqual(refused.returncode, 2)
            self.assertIn(b"prepared_manifest_mismatch", refused.stderr)
            self.assertEqual(_workspace_content_hashes(workspace), before)
            self.assertFalse((workspace / "execution-authorization.json").exists())

    def test_authorize_refuses_a_symlinked_ledger_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            scaffolded = _scaffold_workspace(workspace)
            self.assertEqual(scaffolded.returncode, 0, scaffolded.stderr.decode())
            prepared = _prepare_workspace(workspace)
            self.assertEqual(prepared.returncode, 0, prepared.stderr.decode())
            retained_ledger = workspace / "retained-ledger"
            (workspace / "ledger").rename(retained_ledger)
            (workspace / "ledger").symlink_to(retained_ledger, target_is_directory=True)

            refused = _authorize_workspace(workspace)

            self.assertEqual(refused.returncode, 2)
            self.assertIn(b"ledger_must_be_real_directory", refused.stderr)
            self.assertFalse((workspace / "execution-authorization.json").exists())

    def test_scaffold_has_no_live_or_provider_option(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for option in ("--live", "--provider"):
                workspace = root / option.removeprefix("--")
                with self.subTest(option=option):
                    unsupported_arguments = (
                        [option, "example"] if option == "--provider" else [option]
                    )
                    refused = _run(
                        [
                            sys.executable,
                            str(TOOL),
                            "scaffold",
                            str(workspace),
                            "--authorized-by",
                            "CAPLAB test operator",
                            "--delegation-source",
                            "explicit local first-run evidence delegation",
                            "--valid-for-seconds",
                            "600",
                            *unsupported_arguments,
                        ],
                        cwd=ROOT,
                    )
                    self.assertEqual(refused.returncode, 2)
                    self.assertIn(b"unrecognized arguments", refused.stderr)
                    self.assertFalse(workspace.exists())

    def test_scaffold_refuses_when_static_c_compiler_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            empty_path = root / "empty-path"
            empty_path.mkdir()
            workspace = root / "workspace"

            refused = _run(
                [
                    sys.executable,
                    str(TOOL),
                    "scaffold",
                    str(workspace),
                    "--authorized-by",
                    "CAPLAB test operator",
                    "--delegation-source",
                    "explicit local first-run evidence delegation",
                    "--valid-for-seconds",
                    "600",
                ],
                cwd=ROOT,
                environment={"PATH": str(empty_path)},
            )

            self.assertEqual(refused.returncode, 2)
            self.assertIn(b"c_compiler_unavailable", refused.stderr)
            self.assertFalse(workspace.exists())

    def test_scaffold_refuses_nonempty_and_symlinked_destinations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            occupied = root / "occupied"
            occupied.mkdir()
            retained = occupied / "retained.txt"
            retained.write_text("owner content\n", encoding="utf-8")
            linked = root / "linked"
            linked.symlink_to(occupied, target_is_directory=True)

            for destination, expected_error in (
                (occupied, b"workspace_must_be_empty"),
                (linked, b"workspace_must_be_real_directory"),
            ):
                with self.subTest(destination=destination.name):
                    refused = _run(
                        [
                            sys.executable,
                            str(TOOL),
                            "scaffold",
                            str(destination),
                            "--authorized-by",
                            "CAPLAB test operator",
                            "--delegation-source",
                            "explicit local first-run evidence delegation",
                            "--valid-for-seconds",
                            "600",
                        ],
                        cwd=ROOT,
                    )
                    self.assertEqual(refused.returncode, 2)
                    self.assertIn(expected_error, refused.stderr)
                    self.assertEqual(
                        retained.read_text(encoding="utf-8"), "owner content\n"
                    )

    def test_contributor_can_scaffold_execute_score_and_inspect_persistent_fixture(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "revbench-first-run"
            scaffolded = _run(
                [
                    sys.executable,
                    str(TOOL),
                    "scaffold",
                    str(workspace),
                    "--authorized-by",
                    "CAPLAB test operator",
                    "--delegation-source",
                    "explicit local first-run evidence delegation",
                    "--valid-for-seconds",
                    "600",
                ],
                cwd=ROOT,
            )
            self.assertEqual(scaffolded.returncode, 0, scaffolded.stderr.decode())
            self.assertIn(b"-m caplab.revbench prepare", scaffolded.stdout)

            artifacts = {
                "fixture/fake_native.c",
                "fixture/fake-native",
                "inputs/binding.json",
                "inputs/capability.json",
                "inputs/protocol.json",
                "inputs/corpus.json",
                "inputs/case-selection.json",
                "inputs/basis-authorization-truth.json",
                "inputs/basis-authorization-case-selection.json",
                "inputs/basis-authorization-metric-derivation.json",
                "spec.json",
            }
            self.assertTrue(
                artifacts.issubset(_workspace_content_hashes(workspace)),
                sorted(artifacts - _workspace_content_hashes(workspace).keys()),
            )

            prepared = _run(
                [
                    sys.executable,
                    "-m",
                    "caplab.revbench",
                    "prepare",
                    "--spec",
                    str(workspace / "spec.json"),
                    "--ledger",
                    str(workspace / "ledger"),
                    "--output",
                    str(workspace / "manifest.json"),
                    "--reference-output",
                    str(workspace / "manifest-ref.json"),
                ],
                cwd=ROOT,
            )
            self.assertEqual(prepared.returncode, 0, prepared.stderr.decode())

            authorized = _run(
                [
                    sys.executable,
                    str(TOOL),
                    "authorize",
                    str(workspace),
                    "--authorized-by",
                    "CAPLAB test operator",
                    "--delegation-source",
                    "explicit local first-run execution delegation",
                    "--valid-for-seconds",
                    "600",
                ],
                cwd=ROOT,
            )
            self.assertEqual(authorized.returncode, 0, authorized.stderr.decode())
            self.assertIn(b"-m caplab.revbench execute", authorized.stdout)
            self.assertIn(b"-m caplab.revbench score", authorized.stdout)
            execution_authorization = json.loads(
                (workspace / "execution-authorization.json").read_bytes()
            )
            self.assertEqual(
                execution_authorization["manifest_ref"],
                json.loads((workspace / "manifest-ref.json").read_bytes()),
            )

            executed = _run(
                [
                    sys.executable,
                    "-m",
                    "caplab.revbench",
                    "execute",
                    "--manifest",
                    str(workspace / "manifest.json"),
                    "--execution-authorization-ref",
                    str(workspace / "execution-authorization-ref.json"),
                    "--ledger",
                    str(workspace / "ledger"),
                    "--output",
                    str(workspace / "reviews.json"),
                ],
                cwd=ROOT,
            )
            self.assertEqual(executed.returncode, 0, executed.stderr.decode())

            scored = _run(
                [
                    sys.executable,
                    "-m",
                    "caplab.revbench",
                    "score",
                    "--manifest",
                    str(workspace / "manifest.json"),
                    "--reviews",
                    str(workspace / "reviews.json"),
                    "--ledger",
                    str(workspace / "ledger"),
                    "--output",
                    str(workspace / "measurement.json"),
                ],
                cwd=ROOT,
            )
            self.assertEqual(scored.returncode, 0, scored.stderr.decode())

            reviews = json.loads((workspace / "reviews.json").read_bytes())
            measurement = json.loads((workspace / "measurement.json").read_bytes())
            self.assertEqual(reviews["status"], "complete")
            self.assertEqual(len(reviews["attempts"]), 4)
            self.assertEqual(
                measurement["sample_flow"],
                {
                    "attempted": 4,
                    "excluded": 0,
                    "infrastructure_failures": 0,
                    "missing": 0,
                    "planned": 4,
                    "subject_failures": 0,
                    "usable": 4,
                },
            )
            self.assertEqual(
                {
                    name: metric["value"]
                    for name, metric in measurement["metrics"].items()
                },
                {
                    "anchor_hit_rate": {"denominator": 1, "numerator": 1},
                    "catch_rate": {"denominator": 1, "numerator": 1},
                    "conformance_rate": {"denominator": 1, "numerator": 1},
                    "discrimination": {"denominator": 1, "numerator": 1},
                    "false_alarm_rate": {"denominator": 1, "numerator": 0},
                },
            )
            self.assertNotIn("qualification", measurement)

            ledger = FilesystemQualificationLedger((workspace / "ledger").resolve())
            validate_binding(
                json.loads((workspace / "inputs/binding.json").read_bytes()), ledger
            )
            validate_measurement(measurement, ledger)
            retained_documents = [
                json.loads(path.read_bytes())
                for path in sorted(workspace.rglob("*.json"))
            ]
            refs = [
                ref
                for document in retained_documents
                for ref in _content_refs(document)
            ]
            self.assertGreater(len(refs), 20)
            registered_document_records = _registered_document_graph(
                ledger, retained_documents
            )
            self.assertGreater(len(registered_document_records), 40)

            claim_schema = json.loads(
                (CONTRACTS / "qualification-claim-v1.schema.json").read_bytes()
            )
            records_schema = json.loads(
                (CONTRACTS / "qualification-records-v1.schema.json").read_bytes()
            )
            revbench_schema = json.loads(
                (CONTRACTS / "revbench-v1.schema.json").read_bytes()
            )
            live_schema = json.loads(
                (CONTRACTS / "revbench-live-native-v1.schema.json").read_bytes()
            )
            registry = Registry().with_resources(
                (
                    (claim_schema["$id"], Resource.from_contents(claim_schema)),
                    (records_schema["$id"], Resource.from_contents(records_schema)),
                    (
                        revbench_schema["$id"],
                        Resource.from_contents(revbench_schema),
                    ),
                    (live_schema["$id"], Resource.from_contents(live_schema)),
                )
            )
            revbench_validator = Draft202012Validator(
                revbench_schema, registry=registry
            )
            records_validator = Draft202012Validator(records_schema, registry=registry)
            content_ref_validator = Draft202012Validator(
                {"$ref": (claim_schema["$id"] + "#/$defs/content_ref")},
                registry=registry,
            )
            capability_validator = Draft202012Validator(
                {"$ref": (revbench_schema["$id"] + "#/$defs/bounded_capability")},
                registry=registry,
            )
            revbench_versions = {
                definition["properties"]["schema_version"]["const"]
                for branch in revbench_schema["oneOf"]
                if branch["$ref"].startswith("#/$defs/")
                for definition in [
                    revbench_schema["$defs"][branch["$ref"].removeprefix("#/$defs/")]
                ]
                if "schema_version" in definition.get("properties", {})
            }
            records_versions = {
                "caplab-binding/1",
                "caplab-measurement/1",
                "caplab-case-selection-manifest/1",
                "caplab-evidence-basis-authorization/1",
                "caplab-qualification-authorization/1",
                "caplab-authorization-delegation/1",
            }
            validated_versions: set[str] = set()
            auxiliary_payloads: set[bytes] = set()
            classified_registered = 0
            for ref, document in registered_document_records:
                schema_version = document.get("schema_version")
                if schema_version in revbench_versions:
                    revbench_validator.validate(document)
                    validated_versions.add(schema_version)
                elif schema_version in records_versions:
                    records_validator.validate(document)
                    validated_versions.add(schema_version)
                elif ref["schema"] in AUXILIARY_REGISTERED_SCHEMAS:
                    auxiliary_payloads.add(canonical_json(document))
                else:
                    self.fail(
                        "unclassified registered JSON document: "
                        f"schema={ref['schema']!r}, "
                        f"schema_version={schema_version!r}"
                    )
                classified_registered += 1
            self.assertEqual(classified_registered, len(registered_document_records))

            workspace_document_paths = [
                *sorted((workspace / "inputs").glob("*.json")),
                workspace / "spec.json",
                workspace / "manifest.json",
                workspace / "manifest-ref.json",
                workspace / "execution-delegation.json",
                workspace / "execution-authorization.json",
                workspace / "execution-authorization-ref.json",
                workspace / "reviews.json",
                workspace / "measurement.json",
            ]
            for path in workspace_document_paths:
                document = json.loads(path.read_bytes())
                schema_version = document.get("schema_version")
                if schema_version in revbench_versions:
                    revbench_validator.validate(document)
                    validated_versions.add(schema_version)
                elif schema_version in records_versions:
                    records_validator.validate(document)
                    validated_versions.add(schema_version)
                elif set(document) == CONTENT_REF_FIELDS:
                    content_ref_validator.validate(document)
                    ledger.resolve(document)
                elif path.name == "capability.json":
                    capability_validator.validate(document)
                elif canonical_json(document) in auxiliary_payloads:
                    pass
                else:
                    self.fail(
                        "unclassified emitted JSON document: "
                        f"{path.relative_to(workspace)}"
                    )
            self.assertTrue(
                {
                    "caplab-revbench-spec/1",
                    "caplab-revbench-manifest/1",
                    "caplab-revbench-execution-authorization/1",
                    "caplab-revbench-reviews/1",
                    "caplab-measurement/1",
                    "caplab-native-review-attempt/1",
                }.issubset(validated_versions)
            )

            before_inspection = _workspace_content_hashes(workspace)
            for _ in range(2):
                inspected = _run(
                    [sys.executable, str(TOOL), "inspect", str(workspace)],
                    cwd=ROOT,
                )
                self.assertEqual(inspected.returncode, 0, inspected.stderr.decode())
                self.assertIn(b"configured_subject: local-fixture", inspected.stdout)
                self.assertIn(
                    b"qualification_evaluation: not performed by this tool",
                    inspected.stdout,
                )
                self.assertIn(
                    b"provider_execution: unavailable for this local-fixture subject",
                    inspected.stdout,
                )
                self.assertIn(b"registered_refs_resolved:", inspected.stdout)
            self.assertEqual(_workspace_content_hashes(workspace), before_inspection)
            self.assertEqual(
                (workspace / "spec.json").read_bytes(),
                canonical_json(json.loads((workspace / "spec.json").read_bytes()))
                + b"\n",
            )


if __name__ == "__main__":
    unittest.main()
