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

from scripted_native.lifecycle import prepare, read_preparation, consume
from scripted_native.inspection import inspect
from caplab.process_capture import seal_capture_json
from probe_native_capture_startup import harness_manifest


class ScriptedCapturePreparationTests(unittest.TestCase):
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
