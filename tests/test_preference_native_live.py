"""Containment contract for native preference-study invocations."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from caplab.preference.native import load_native_instrument
from caplab.preference.native_live import (
    NativePreferenceLiveContractError,
    _native_result,
    assess_native_attempts,
    build_contained_invocation,
    build_contained_version_probe,
    execute_native_trial,
    load_native_custody_attempts,
    load_native_live_manifest,
    prepare_native_trial,
)


ROOT = Path(__file__).parents[1]
INSTRUMENT = ROOT / "docs/product/studies/preference-001/native-instrument.json"
MANIFEST = ROOT / "docs/product/studies/preference-001/native-live-manifest.json"
SOURCE = ROOT / "src/caplab/preference/native_live.py"


def active_document(custody_directory: str) -> dict[str, object]:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    document["status"] = "active"
    document["authority"] = "adr-0041"
    document["storage"]["raw_custody_root"] = custody_directory
    document["containment"]["source_sha256"] = hashlib.sha256(
        SOURCE.read_bytes()
    ).hexdigest()
    sealed = dict(document)
    sealed.pop("manifest_sha256")
    document["manifest_sha256"] = hashlib.sha256(
        json.dumps(
            sealed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    return document


class NativePreferenceLiveTests(unittest.TestCase):
    def test_prepared_manifest_cannot_cross_live_authorization_boundary(self) -> None:
        with tempfile.TemporaryDirectory(dir=MANIFEST.parent) as manifest_directory:
            document = active_document("/tmp/caplab-native-test-custody")
            document["status"] = "prepared-not-authorized"
            document["authority"] = "pending-adr-0041"
            sealed = dict(document)
            sealed.pop("manifest_sha256")
            document["manifest_sha256"] = hashlib.sha256(
                json.dumps(
                    sealed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
            ).hexdigest()
            path = Path(manifest_directory) / "prepared.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(
                NativePreferenceLiveContractError, "native_live_not_authorized"
            ):
                load_native_live_manifest(path, INSTRUMENT)

    def test_prepared_manifest_cannot_create_attempt_custody(self) -> None:
        instrument = load_native_instrument(INSTRUMENT)
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest = {
                "status": "prepared-not-authorized",
                "authority": "pending-adr-0041",
                "_instrument": instrument,
                "storage": {"raw_custody_root": temporary_directory},
            }
            with self.assertRaisesRegex(
                NativePreferenceLiveContractError, "native_live_not_authorized"
            ):
                prepare_native_trial(manifest, slot_index=0, attempt_kind="primary")
            self.assertEqual(list(Path(temporary_directory).iterdir()), [])

    def test_authorized_manifest_seals_one_native_slot_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as custody_directory, tempfile.TemporaryDirectory(
            dir=MANIFEST.parent
        ) as manifest_directory:
            document = active_document(custody_directory)
            active_path = Path(manifest_directory) / "manifest.json"
            active_path.write_text(json.dumps(document), encoding="utf-8")
            manifest = load_native_live_manifest(active_path, INSTRUMENT)
            attempt_root, command = prepare_native_trial(
                manifest, slot_index=0, attempt_kind="primary"
            )

            launch = json.loads((attempt_root / "launch.json").read_text(encoding="utf-8"))
            self.assertEqual(launch["task_id"], "P02")
            self.assertEqual(launch["subject_id"], "fable")
            self.assertEqual(launch["command"], command)
            self.assertTrue((attempt_root / "input/P02/.caplab-task.json").is_file())

    def test_authorized_manifest_refuses_changed_containment_source(self) -> None:
        with tempfile.TemporaryDirectory(dir=MANIFEST.parent) as manifest_directory:
            document = active_document("/tmp/caplab-native-test-custody")
            document["containment"]["source_sha256"] = "0" * 64
            sealed = dict(document)
            sealed.pop("manifest_sha256")
            document["manifest_sha256"] = hashlib.sha256(
                json.dumps(
                    sealed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
            ).hexdigest()
            active_path = Path(manifest_directory) / "manifest.json"
            active_path.write_text(json.dumps(document), encoding="utf-8")

            with self.assertRaisesRegex(
                NativePreferenceLiveContractError,
                "native_live_containment_source_mismatch",
            ):
                load_native_live_manifest(active_path, INSTRUMENT)

    def test_attempt_accounting_enforces_order_and_one_replacement(self) -> None:
        instrument = load_native_instrument(INSTRUMENT)
        manifest = {
            "_instrument": instrument,
            "limits": {
                "maximum_trials": 16,
                "maximum_replacements": 4,
                "maximum_wall_clock_hours": 12,
            },
        }
        failure = {
            "slot_index": 0,
            "attempt_kind": "primary",
            "status": "provider_failure",
            "duration_seconds": "1.25",
        }
        state = assess_native_attempts(manifest, [failure])
        self.assertEqual(state["pending_replacement_for"], 0)
        replacement = {
            "slot_index": 0,
            "attempt_kind": "replacement",
            "status": "completed",
            "duration_seconds": "2.50",
        }
        state = assess_native_attempts(manifest, [failure, replacement])
        self.assertEqual(state["next_slot_index"], 1)
        second_failure = dict(replacement, status="capture_failure")
        stopped = assess_native_attempts(manifest, [failure, second_failure])
        self.assertEqual(stopped["stop_reason"], "second_native_infrastructure_failure")
        self.assertFalse(stopped["complete"])
        with self.assertRaisesRegex(
            NativePreferenceLiveContractError, "native_primary_order_mismatch"
        ):
            assess_native_attempts(
                manifest,
                [
                    {
                        "slot_index": 1,
                        "attempt_kind": "primary",
                        "status": "completed",
                        "duration_seconds": "1",
                    }
                ],
            )

    def test_native_jsonl_extracts_each_harness_result_and_usage(self) -> None:
        claude = (
            b'{"type":"system","subtype":"init"}\n'
            b'{"type":"result","is_error":false,"result":"done",'
            b'"usage":{"input_tokens":12,"output_tokens":3}}\n'
        )
        codex = (
            b'{"type":"item.completed","item":{"type":"agent_message",'
            b'"text":"done"}}\n'
            b'{"type":"turn.completed","usage":{"input_tokens":10,'
            b'"output_tokens":4}}\n'
        )
        self.assertEqual(_native_result("fable", claude), ("done", {"input_tokens": 12, "output_tokens": 3}))
        self.assertEqual(_native_result("gpt", codex), ("done", {"input_tokens": 10, "output_tokens": 4}))

    def test_native_execution_seals_observation_before_next_slot(self) -> None:
        with tempfile.TemporaryDirectory() as custody_directory, tempfile.TemporaryDirectory(
            dir=MANIFEST.parent
        ) as manifest_directory:
            document = active_document(custody_directory)
            active_path = Path(manifest_directory) / "manifest.json"
            active_path.write_text(json.dumps(document), encoding="utf-8")
            manifest = load_native_live_manifest(active_path, INSTRUMENT)
            stdout = (
                b'{"type":"result","is_error":false,"result":"done",'
                b'"usage":{"input_tokens":12,"output_tokens":3}}\n'
            )
            completed = mock.Mock(returncode=0, stdout=stdout, stderr=b"")
            with mock.patch(
                "caplab.preference.native_live.preflight_native_runtime",
                return_value=document["runtime_versions"],
            ), mock.patch(
                "caplab.preference.native_live.subprocess.run", return_value=completed
            ):
                attempt_root = execute_native_trial(
                    manifest,
                    slot_index=0,
                    attempt_kind="primary",
                    prior_attempts=[],
                )

            self.assertTrue((attempt_root / "completion.json").is_file())
            observation = json.loads(
                (attempt_root / "observation.json").read_text(encoding="utf-8")
            )
            self.assertEqual(observation["status"], "completed")
            self.assertEqual(observation["usage"]["output_tokens"], 3)
            attempts = load_native_custody_attempts(manifest)
            self.assertEqual(attempts[0]["slot_index"], 0)
            self.assertEqual(
                assess_native_attempts(manifest, attempts)["next_slot_index"], 1
            )

    def test_both_native_harnesses_run_in_the_same_external_task_namespace(self) -> None:
        instrument = load_native_instrument(INSTRUMENT)
        with tempfile.TemporaryDirectory() as temporary_directory:
            task_root = Path(temporary_directory).resolve()
            fable = build_contained_invocation(instrument, "fable", "P01", task_root)
            gpt = build_contained_invocation(instrument, "gpt", "P01", task_root)

        for invocation in (fable, gpt):
            command = invocation["command"]
            self.assertEqual(command[0], "/usr/bin/bwrap")
            self.assertIn("--unshare-all", command)
            self.assertIn("--share-net", command)
            self.assertIn(str(task_root), command)
            self.assertIn("/work", command)
            self.assertNotIn(str(ROOT), command)
        self.assertIn("claude", fable["command"])
        self.assertIn("codex", gpt["command"])
        self.assertIn(str(Path("/home/halbritt/.local/share/striatum/harness-config/claude-code")), fable["command"])
        self.assertNotIn(str(Path("/home/halbritt/.local/share/striatum/harness-config/codex")), fable["command"])
        self.assertIn(str(Path("/home/halbritt/.local/share/striatum/harness-config/codex/config.toml")), gpt["command"])
        self.assertIn(str(Path("/home/halbritt/.codex/auth.json")), gpt["command"])
        self.assertNotIn(str(Path("/home/halbritt/.local/share/striatum/harness-config/claude-code")), gpt["command"])

    def test_version_probes_use_the_same_containment_without_a_model_prompt(self) -> None:
        instrument = load_native_instrument(INSTRUMENT)
        with tempfile.TemporaryDirectory() as temporary_directory:
            task_root = Path(temporary_directory).resolve()
            fable = build_contained_version_probe(instrument, "fable", task_root)
            gpt = build_contained_version_probe(instrument, "gpt", task_root)

        self.assertEqual(fable["command"][-2:], ["claude", "--version"])
        self.assertEqual(gpt["command"][-2:], ["codex", "--version"])


if __name__ == "__main__":
    unittest.main()
