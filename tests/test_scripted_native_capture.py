"""Preparation and one-shot ownership for the fixed native diagnostic."""

import hashlib
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from scripted_native.lifecycle import (
    prepare,
    read_preparation,
    consume,
    check_task_selection,
)
from scripted_native.inspection import inspect
from caplab.process_capture import seal_capture_json
from caplab.task_input import prepare_task_input
from probe_native_capture_startup import harness_manifest


class ScriptedCapturePreparationTests(unittest.TestCase):
    def test_buffered_trace_is_explicit_and_bound_to_supervised_profile(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            native, dependency = self.installation(root), self.dependency(root)
            options = dict(
                codex_root=native,
                websockets_root=dependency,
                launch_profile="codex-scripted-routed/v2",
                resource_profile="cgroup-usage/v1",
                child_observation_profile="supervisor-poll/v1",
                trace_profile="sealed-buffer/v1",
            )
            with self.assertRaises(ValueError):
                prepare(
                    root / "refused", **(options | {"child_observation_profile": None})
                )
            self.assertFalse((root / "refused").exists())
            output = root / "capture"
            receipt = prepare(output, **options)
            prepared = read_preparation(
                output, expected_sha256=receipt["preparation_sha256"]
            )
            self.assertEqual(
                prepared["schema"], "caplab.scripted-native-preparation/v7"
            )
            self.assertEqual(prepared["trace_profile"], "sealed-buffer/v1")
            self.assertFalse((output / "consumption.json").exists())
            for changes in (
                {"schema": "caplab.scripted-native-preparation/v6"},
                {"trace_profile": "file/v1"},
                {"child_observation_profile": None},
                {"resource_profile": None},
            ):
                with self.subTest(changes=changes):
                    raw = json.dumps(prepared | changes).encode()
                    (output / "preparation.json").write_bytes(raw)
                    with self.assertRaises(ValueError):
                        read_preparation(
                            output, expected_sha256=hashlib.sha256(raw).hexdigest()
                        )

    def test_supervisor_observation_is_explicit_and_requires_resource_capture(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            native, dependency = self.installation(root), self.dependency(root)
            with self.assertRaises(ValueError):
                prepare(
                    root / "refused",
                    codex_root=native,
                    websockets_root=dependency,
                    launch_profile="codex-scripted-routed/v2",
                    child_observation_profile="supervisor-poll/v1",
                )
            self.assertFalse((root / "refused").exists())
            output = root / "capture"
            receipt = prepare(
                output,
                codex_root=native,
                websockets_root=dependency,
                launch_profile="codex-scripted-routed/v2",
                resource_profile="cgroup-usage/v1",
                child_observation_profile="supervisor-poll/v1",
            )
            prepared = read_preparation(
                output, expected_sha256=receipt["preparation_sha256"]
            )
            self.assertEqual(
                prepared["schema"], "caplab.scripted-native-preparation/v6"
            )
            self.assertEqual(
                prepared["child_observation_profile"], "supervisor-poll/v1"
            )
            self.assertFalse((output / "consumption.json").exists())
            for change in (
                {"schema": "caplab.scripted-native-preparation/v5"},
                {"child_observation_profile": "fixture/v1"},
                {"resource_profile": None},
            ):
                with self.subTest(change=change):
                    raw = json.dumps(prepared | change).encode()
                    (output / "preparation.json").write_bytes(raw)
                    with self.assertRaises(ValueError):
                        read_preparation(
                            output, expected_sha256=hashlib.sha256(raw).hexdigest()
                        )

    def test_routed_preparation_freezes_profile_and_routing_tools(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "capture"
            receipt = prepare(
                output,
                codex_root=self.installation(root),
                websockets_root=self.dependency(root),
                launch_profile="codex-scripted-routed/v1",
            )
            prepared = read_preparation(
                output, expected_sha256=receipt["preparation_sha256"]
            )
            self.assertEqual(
                prepared["schema"], "caplab.scripted-native-preparation/v3"
            )
            self.assertEqual(prepared["launch_profile"], "codex-scripted-routed/v1")
            self.assertEqual(prepared["limits"]["capture_seconds"], 75)
            self.assertEqual(prepared["limits"]["routing_handoff_seconds"], 25)
            self.assertIn(
                "/usr/bin/slirp4netns",
                [p["invoked_path"] for p in prepared["runtime_pins"]],
            )
            self.assertIsNone(prepared["task_input"])
            self.assertFalse((output / "consumption.json").exists())
            prepared["launch_profile"] = "codex-scripted-local/v1"
            (output / "preparation.json").write_text(json.dumps(prepared))
            with self.assertRaises(ValueError):
                read_preparation(
                    output,
                    expected_sha256=hashlib.sha256(
                        (output / "preparation.json").read_bytes()
                    ).hexdigest(),
                )

    def test_parent_routed_preparation_cannot_be_relabelled_as_prior_profile(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "capture"
            receipt = prepare(
                output,
                codex_root=self.installation(root),
                websockets_root=self.dependency(root),
                launch_profile="codex-scripted-routed/v2",
            )
            prepared = read_preparation(
                output, expected_sha256=receipt["preparation_sha256"]
            )
            self.assertEqual(
                prepared["schema"], "caplab.scripted-native-preparation/v4"
            )
            self.assertEqual(prepared["launch_profile"], "codex-scripted-routed/v2")
            self.assertEqual(prepared["limits"]["capture_seconds"], 75)
            self.assertFalse((output / "consumption.json").exists())
            for key, value in (
                ("schema", "caplab.scripted-native-preparation/v3"),
                ("launch_profile", "codex-scripted-routed/v1"),
                ("launch_profile", "codex-scripted-local/v1"),
            ):
                with self.subTest(key=key, value=value):
                    raw = json.dumps(prepared | {key: value}).encode()
                    (output / "preparation.json").write_bytes(raw)
                    with self.assertRaises(ValueError):
                        read_preparation(
                            output, expected_sha256=hashlib.sha256(raw).hexdigest()
                        )

    def test_resource_profile_requires_parent_routing_and_its_own_preparation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            native, dependency = self.installation(root), self.dependency(root)
            for launch in ("codex-scripted-local/v1", "codex-scripted-routed/v1"):
                with self.subTest(launch=launch), self.assertRaises(ValueError):
                    prepare(
                        root / "refused",
                        codex_root=native,
                        websockets_root=dependency,
                        launch_profile=launch,
                        resource_profile="cgroup-usage/v1",
                    )
                self.assertFalse((root / "refused").exists())
            output = root / "capture"
            receipt = prepare(
                output,
                codex_root=native,
                websockets_root=dependency,
                launch_profile="codex-scripted-routed/v2",
                resource_profile="cgroup-usage/v1",
            )
            prepared = read_preparation(
                output, expected_sha256=receipt["preparation_sha256"]
            )
            self.assertEqual(
                prepared["schema"], "caplab.scripted-native-preparation/v5"
            )
            self.assertEqual(prepared["resource_profile"], "cgroup-usage/v1")
            self.assertFalse((output / "consumption.json").exists())
            for key, value in (
                ("schema", "caplab.scripted-native-preparation/v4"),
                ("resource_profile", "cgroup-usage/v2"),
                ("launch_profile", "codex-scripted-routed/v1"),
            ):
                with self.subTest(key=key, value=value):
                    raw = json.dumps(prepared | {key: value}).encode()
                    (output / "preparation.json").write_bytes(raw)
                    with self.assertRaises(ValueError):
                        read_preparation(
                            output, expected_sha256=hashlib.sha256(raw).hexdigest()
                        )

    def test_unbounded_task_metadata_is_refused_before_opening_custody(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selection = {
                "custody": str(root / "absent"),
                "input_sha256": "0" * 64,
                "max_receipt_bytes": 2**40,
            }
            with self.assertRaisesRegex(ValueError, "task metadata allowance differs"):
                check_task_selection(selection, root / "capture")

    def test_task_input_limits_reserved_path_and_partial_selection_refuse_preparation(
        self,
    ):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            installation, dependency = self.installation(root), self.dependency(root)
            for mode in (
                "reserved",
                "read-only root",
                "oversized allowance",
                "two copies exceed budget",
                "missing hash",
                "missing custody",
                "overlap",
            ):
                with self.subTest(mode=mode):
                    case = root / mode
                    case.mkdir()
                    source = case / "source"
                    source.mkdir()
                    (
                        source
                        / ("capture-witness.txt" if mode == "reserved" else "task.py")
                    ).write_bytes(b"initial")
                    if mode == "read-only root":
                        source.chmod(0o500)
                    if mode == "two copies exceed budget":
                        (source / "task.py").write_bytes(b"x" * (512 * 1024))
                    bundle = case / "input"
                    anchor = prepare_task_input(
                        source,
                        output_dir=bundle,
                        max_task_bytes={
                            "oversized allowance": 2**30,
                            "two copies exceed budget": 1024**2,
                        }.get(mode, 1000),
                        max_task_entries=20,
                    )
                    output = (
                        bundle / "capture" if mode == "overlap" else case / "capture"
                    )
                    with self.assertRaises(ValueError):
                        prepare(
                            output,
                            codex_root=installation,
                            websockets_root=dependency,
                            task_input=None if mode == "missing custody" else bundle,
                            task_input_sha256=None
                            if mode == "missing hash"
                            else anchor,
                        )
                    self.assertFalse(output.exists())

    def test_prepared_task_is_anchored_and_drift_refuses_before_consumption(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "task-source"
            source.mkdir()
            (source / "task.py").write_bytes(b"print('caf\xc3\xa9')\n")
            bundle = root / "task-input"
            input_sha = prepare_task_input(
                source, output_dir=bundle, max_task_bytes=1000, max_task_entries=20
            )
            shutil.rmtree(source)
            output = root / "capture"
            receipt = prepare(
                output,
                codex_root=self.installation(root),
                websockets_root=self.dependency(root),
                task_input=bundle,
                task_input_sha256=input_sha,
            )
            prepared = read_preparation(
                output, expected_sha256=receipt["preparation_sha256"]
            )
            self.assertEqual(
                prepared["schema"], "caplab.scripted-native-preparation/v2"
            )
            self.assertEqual(prepared["task_input"]["input_sha256"], input_sha)
            path, auth_sha = self.authorization(
                root, output, receipt["preparation_sha256"]
            )
            inventory = json.loads((bundle / "inventory/inventory.json").read_bytes())
            entry = next(e for e in inventory["entries"] if e["kind"] == "file")
            (bundle / "inventory" / entry["object"]).write_bytes(b"changed")
            with self.assertRaises(ValueError):
                consume(
                    output,
                    expected_preparation_sha256=receipt["preparation_sha256"],
                    authorization_path=path,
                    expected_authorization_sha256=auth_sha,
                )
            self.assertFalse((output / "consumption.json").exists())

    def installation(self, root):
        source = root / "codex"
        source.mkdir()
        fixtures = REPO / "tests/fixtures/codex-launcher-0.153.4"
        paths = [
            ("codex.js", "bin/codex.js"),
            ("package.json", "package.json"),
            (
                "platform-package.json",
                "node_modules/@openai/codex-linux-x64/package.json",
            ),
        ]
        for original, relative in paths:
            target = source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(fixtures / original, target)
        binary = (
            source
            / "node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex"
        )
        binary.parent.mkdir(parents=True)
        binary.write_bytes(b"fixed preparation-only binary; never executable\n")
        return source

    def dependency(self, root):
        package = root / "websockets"
        package.mkdir()
        (package / "version.py").write_text(
            'released = True\ntag = version = commit = "15.0.1"\n'
        )
        (package / "__init__.py").write_text("")
        return package

    def test_preparation_pins_inputs_and_root_without_spending_an_attempt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "capture"
            receipt = prepare(
                output,
                codex_root=self.installation(root),
                websockets_root=self.dependency(root),
            )
            anchor = hashlib.sha256(
                (output / "preparation.json").read_bytes()
            ).hexdigest()
            self.assertEqual(receipt["preparation_sha256"], anchor)
            prepared = read_preparation(output, expected_sha256=anchor)
            self.assertEqual(prepared["custody_root"], str(output))
            self.assertEqual(prepared["attempt_limit"], 1)
            self.assertEqual(
                prepared["invocation"]["base_subject"]["model_id"], "gpt-5.6-terra"
            )
            self.assertFalse(prepared["execution_authorized"])
            self.assertFalse((output / "consumption.json").exists())
            self.assertEqual(
                json.loads((output / "preparation.json").read_bytes()), prepared
            )

    def test_authorization_binds_preparation_and_only_one_consumption_is_possible(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "capture"
            receipt = prepare(
                output,
                codex_root=self.installation(root),
                websockets_root=self.dependency(root),
            )
            anchor = receipt["preparation_sha256"]
            authorization = {
                "schema": "caplab.scripted-native-authorization/v1",
                "preparation_sha256": anchor,
                "custody_root": str(output),
                "attempt_limit": 1,
                "decision_owner": "fixed test owner",
                "authority_source": "fixed control only",
                "permitted_effect": "one-scripted-native-diagnostic",
            }
            path = root / "authorization.json"
            path.write_text(json.dumps(authorization))
            auth_sha = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "hash differs"):
                consume(
                    output,
                    expected_preparation_sha256=anchor,
                    authorization_path=path,
                    expected_authorization_sha256="0" * 64,
                )
            self.assertFalse((output / "consumption.json").exists())
            consumed = consume(
                output,
                expected_preparation_sha256=anchor,
                authorization_path=path,
                expected_authorization_sha256=auth_sha,
            )
            self.assertEqual(consumed["attempts_consumed"], 1)
            before = (output / "consumption.json").read_bytes()
            with self.assertRaises(FileExistsError):
                consume(
                    output,
                    expected_preparation_sha256=anchor,
                    authorization_path=path,
                    expected_authorization_sha256=auth_sha,
                )
            self.assertEqual((output / "consumption.json").read_bytes(), before)

    def test_rehashed_preparation_cannot_drop_runtime_pins_or_claim_a_binding(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "capture"
            prepare(
                output,
                codex_root=self.installation(root),
                websockets_root=self.dependency(root),
            )
            path = output / "preparation.json"
            original = json.loads(path.read_bytes())
            for change in [
                {"runtime_pins": []},
                {"binding_complete": True},
                {"limits": original["limits"] | {"swap_bytes": False}},
            ]:
                with self.subTest(change=change):
                    path.write_text(json.dumps(original | change))
                    with self.assertRaises(ValueError):
                        read_preparation(
                            output,
                            expected_sha256=hashlib.sha256(
                                path.read_bytes()
                            ).hexdigest(),
                        )

    def test_source_drift_refuses_before_consumption_and_partial_receipt_stays_spent(
        self,
    ):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.installation(root)
            output = root / "capture"
            receipt = prepare(
                output, codex_root=source, websockets_root=self.dependency(root)
            )
            path, auth_sha = self.authorization(
                root, output, receipt["preparation_sha256"]
            )
            invocation = dict(
                expected_preparation_sha256=receipt["preparation_sha256"],
                authorization_path=path,
                expected_authorization_sha256=auth_sha,
            )
            binary = (
                source
                / "node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex"
            )
            original = binary.read_bytes()
            binary.write_bytes(original + b"changed")
            with self.assertRaisesRegex(ValueError, "installation changed"):
                consume(output, **invocation)
            self.assertFalse((output / "consumption.json").exists())
            binary.write_bytes(original)
            (output / "consumption.json").write_bytes(b"{partial")
            with self.assertRaises(FileExistsError):
                consume(output, **invocation)
            self.assertEqual((output / "consumption.json").read_bytes(), b"{partial")

    def authorization(self, root, output, anchor):
        path = root / "authorization.json"
        path.write_text(
            json.dumps(
                {
                    "schema": "caplab.scripted-native-authorization/v1",
                    "preparation_sha256": anchor,
                    "custody_root": str(output),
                    "attempt_limit": 1,
                    "decision_owner": "fixed test owner",
                    "authority_source": "fixed control only",
                    "permitted_effect": "one-scripted-native-diagnostic",
                }
            )
        )
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_concurrent_consumers_have_exactly_one_winner(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "capture"
            receipt = prepare(
                output,
                codex_root=self.installation(root),
                websockets_root=self.dependency(root),
            )
            path, auth_sha = self.authorization(
                root, output, receipt["preparation_sha256"]
            )

            def attempt():
                try:
                    return consume(
                        output,
                        expected_preparation_sha256=receipt["preparation_sha256"],
                        authorization_path=path,
                        expected_authorization_sha256=auth_sha,
                    )
                except FileExistsError:
                    return None

            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(lambda _: attempt(), range(2)))
            (winner,) = [result for result in outcomes if result is not None]
            self.assertEqual(
                winner, json.loads((output / "consumption.json").read_bytes())
            )

    def test_incomplete_capture_is_unavailable_and_changed_capture_refuses(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "capture"
            prepared = prepare(
                output,
                codex_root=self.installation(root),
                websockets_root=self.dependency(root),
            )
            path, auth_sha = self.authorization(
                root, output, prepared["preparation_sha256"]
            )
            consume(
                output,
                expected_preparation_sha256=prepared["preparation_sha256"],
                authorization_path=path,
                expected_authorization_sha256=auth_sha,
            )
            run = output / "run"
            run.mkdir()
            (run / "retained-prefix").write_bytes(b"fixed interrupted producer output")
            result = {
                "schema": "caplab.scripted-native-result/v1",
                "preparation_sha256": prepared["preparation_sha256"],
                "consumption_sha256": hashlib.sha256(
                    (output / "consumption.json").read_bytes()
                ).hexdigest(),
                "outcome": {
                    "native_attempt_succeeded": False,
                    "execution_error": {"type": "fixed control"},
                },
                "capture_manifest": harness_manifest(run),
                "verification_performed": False,
                "binding_complete": False,
                "study_eligible": False,
            }
            seal_capture_json(output, "result.json", result)
            kwargs = {
                "expected_preparation_sha256": prepared["preparation_sha256"],
                "expected_result_sha256": hashlib.sha256(
                    (output / "result.json").read_bytes()
                ).hexdigest(),
            }
            report = inspect(output, **kwargs)
            self.assertEqual(report["status"], "unavailable")
            self.assertIn("safe-child-observation.json", report["missing_artifacts"])
            self.assertFalse(report["study_eligible"])
            with self.assertRaisesRegex(ValueError, "hash differs"):
                inspect(output, **(kwargs | {"expected_result_sha256": "0" * 64}))
            (run / "retained-prefix").write_bytes(b"changed after result seal")
            with self.assertRaisesRegex(ValueError, "capture manifest differs"):
                inspect(output, **kwargs)


if __name__ == "__main__":
    unittest.main()
