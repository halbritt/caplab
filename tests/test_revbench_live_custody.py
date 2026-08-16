from __future__ import annotations

import tempfile
import unittest
from unittest import mock
import os
import stat
import subprocess
from pathlib import Path

from caplab.revbench.custody import (
    FilesystemLiveExecutionRuntime,
    FreshProcessCapture,
    LiveExecutionCustodyError,
    RecoveredProcessCapture,
    live_effect_id,
    live_process_id,
)
from caplab.revbench import custody
from caplab.runtime.canonical import canonical_json
from caplab.revbench.codex import _run_owned_process, build_live_launch_plan
from tests.test_revbench import write_fake_native


ROOT = Path(__file__).resolve().parents[1]


class LiveExecutionCustodyTests(unittest.TestCase):
    def _launch_plan(
        self,
        *,
        process_kind: str = "native-review",
        case_id: str = "case-a",
        arm: str = "control",
        assignment_index: int = 0,
        argv_sha256: str = "a" * 64,
    ):
        return {
            "schema_version": "caplab-revbench-live-launch-plan/1",
            "effect_scope": {
                "schema_version": "caplab-revbench-live-effect-scope/1",
                "manifest_sha256": "6" * 64,
                "experiment_id": "revbench-example",
                "binding_id": "bnd-" + "8" * 64,
                "case_id": case_id,
                "arm": arm,
                "assignment_index": assignment_index,
                "process_kind": process_kind,
            },
            "argv_sha256": argv_sha256,
            "containment_argv_sha256": "1" * 64,
            "stdin_sha256": "b" * 64,
            "environment_sha256": "c" * 64,
            "runtime_bundle_sha256": "d" * 64,
            "apparatus_sha256": "4" * 64,
            "command_sha256": "e" * 64,
            "credential_profile_id": "caplab-openai-revbench",
            "credential_profile_sha256": "f" * 64,
            "timeout_seconds": 5,
            "execution_deadline_at": "2027-01-01T00:00:00Z",
            "stdout_limit": 1024,
            "stderr_limit": 1024,
        }

    def _execution_intent(
        self, authorization_digit: str, *plans, custody_domain_id: str
    ):
        return {
            "schema_version": "caplab-revbench-live-execution-intent/1",
            "authorization_id": "revbench-execution-auth-" + authorization_digit * 64,
            "manifest_sha256": "6" * 64,
            "experiment_id": "revbench-example",
            "binding_id": "bnd-" + "8" * 64,
            "custody_domain_id": custody_domain_id,
            "apparatus_ref": {
                "kind": "execution-apparatus-receipt",
                "schema": "caplab-revbench-execution-apparatus/1",
                "media_type": "application/json",
                "sha256": "4" * 64,
                "byte_count": 1,
                "locator": "objects/sha256/44/" + "4" * 64,
                "registration_ref": "test:apparatus:" + "4" * 64,
                "custody": None,
            },
            "intent_recorded_at": "2026-08-14T00:00:00Z",
            "execution_deadline_at": "2027-01-01T00:00:00Z",
            "process_sequence": [
                {
                    "effect_id": live_effect_id(plan["effect_scope"]),
                    "process_id": live_process_id(plan),
                    "launch_plan": plan,
                }
                for plan in plans
            ],
        }

    def test_credential_mapping_requires_one_configured_private_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            ledger_root = parent / "ledger"
            ledger_root.mkdir(mode=0o700)
            credential_root = parent / "credentials"
            credential_root.mkdir(mode=0o700)
            source = credential_root / "codex-auth.json"
            source.write_bytes(b"private")
            source.chmod(0o600)
            runtime = FilesystemLiveExecutionRuntime(
                ledger_root,
                credential_root=credential_root,
                credential_sources={"caplab-openai-revbench": source.name},
            )
            self.assertEqual(
                runtime.credential_source("caplab-openai-revbench"), source
            )
            self.assertEqual(runtime.credential_root, credential_root)

            with self.assertRaisesRegex(
                LiveExecutionCustodyError, "credential_source_name_invalid"
            ):
                FilesystemLiveExecutionRuntime(
                    ledger_root,
                    credential_root=credential_root,
                    credential_sources={
                        "caplab-openai-revbench": Path("nested/auth.json")
                    },
                )

    def test_credential_root_must_be_disjoint_from_custody_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            ledger_root = parent / "ledger"
            ledger_root.mkdir(mode=0o700)
            custody = FilesystemLiveExecutionRuntime(ledger_root)
            nested = custody.root / "credentials"
            nested.mkdir(mode=0o700)
            with self.assertRaisesRegex(
                LiveExecutionCustodyError, "disjoint_from_evidence"
            ):
                FilesystemLiveExecutionRuntime(
                    ledger_root,
                    credential_root=nested,
                    credential_sources={"caplab-openai-revbench": "auth.json"},
                )

    def test_live_custody_root_must_be_outside_the_package_and_repository(self):
        with tempfile.TemporaryDirectory(
            prefix=".live-custody-test-", dir=ROOT
        ) as temporary:
            with self.assertRaisesRegex(
                LiveExecutionCustodyError,
                "live_custody_root_must_be_disjoint_from_package",
            ):
                FilesystemLiveExecutionRuntime(Path(temporary))

    def test_real_subprocess_tees_streams_and_completion_before_registration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "fake-native"
            write_fake_native(executable)
            runtime = FilesystemLiveExecutionRuntime(root)
            logical_argv = [str(executable), "--version"]
            scope = self._launch_plan(process_kind="version-probe")["effect_scope"]
            plan = build_live_launch_plan(
                scope,
                logical_argv=logical_argv,
                normalized_containment_argv=logical_argv,
                stdin=b"",
                contained_environment={},
                runtime_ref_sha256="d" * 64,
                apparatus_sha256="4" * 64,
                command_ref_sha256="e" * 64,
                credential_profile_id="caplab-openai-revbench",
                credential_profile_sha256="f" * 64,
                timeout_seconds=5,
                execution_deadline_at="2099-01-01T00:00:00Z",
                stdout_limit=1024,
                stderr_limit=1024,
            )
            execution_intent = self._execution_intent(
                "7", plan, custody_domain_id=runtime.custody_domain_id
            )
            execution_intent["execution_deadline_at"] = "2099-01-01T00:00:00Z"

            with runtime.claim_execution(execution_intent) as execution:
                capture = execution.claim_process(plan)
                self.assertIsInstance(capture, FreshProcessCapture)
                observation = _run_owned_process(
                    logical_argv,
                    logical_argv,
                    logical_argv,
                    b"",
                    contained_environment={},
                    runtime_ref_sha256="d" * 64,
                    apparatus_sha256="4" * 64,
                    command_ref_sha256="e" * 64,
                    credential_profile_id="caplab-openai-revbench",
                    credential_profile_sha256="f" * 64,
                    pass_fds=(),
                    capture=capture,
                    credential=None,
                    monotonic_deadline=float("inf"),
                )

            self.assertEqual(observation.stdout, b"fake-native 1\n")
            with runtime.claim_execution(execution_intent) as execution:
                recovered = execution.claim_process(plan)
            self.assertIsInstance(recovered, RecoveredProcessCapture)
            self.assertEqual(recovered.stdout, observation.stdout)
            self.assertEqual(recovered.stderr, observation.stderr)
            self.assertEqual(recovered.invocation_state, "invoked")
            self.assertEqual(recovered.termination, "exited")
            self.assertIsNotNone(recovered.completion)

    def test_runner_refuses_actual_plan_swap_before_popen(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            logical_argv = ["/not-run", "review"]
            scope = self._launch_plan()["effect_scope"]
            plan = build_live_launch_plan(
                scope,
                logical_argv=logical_argv,
                normalized_containment_argv=logical_argv,
                stdin=b"sealed-input",
                contained_environment={"LANG": "C.UTF-8"},
                runtime_ref_sha256="d" * 64,
                apparatus_sha256="4" * 64,
                command_ref_sha256="e" * 64,
                credential_profile_id="caplab-openai-revbench",
                credential_profile_sha256="f" * 64,
                timeout_seconds=5,
                execution_deadline_at="2099-01-01T00:00:00Z",
                stdout_limit=1024,
                stderr_limit=1024,
            )
            intent = self._execution_intent(
                "2", plan, custody_domain_id=runtime.custody_domain_id
            )
            intent["execution_deadline_at"] = "2099-01-01T00:00:00Z"
            with runtime.claim_execution(intent) as execution:
                capture = execution.claim_process(plan)
                with mock.patch("caplab.revbench.codex.subprocess.Popen") as popen:
                    with self.assertRaisesRegex(Exception, "actual_mismatch"):
                        _run_owned_process(
                            logical_argv,
                            logical_argv,
                            logical_argv,
                            b"swapped-input",
                            contained_environment={"LANG": "C.UTF-8"},
                            runtime_ref_sha256="d" * 64,
                            apparatus_sha256="4" * 64,
                            command_ref_sha256="e" * 64,
                            credential_profile_id="caplab-openai-revbench",
                            credential_profile_sha256="f" * 64,
                            pass_fds=(),
                            capture=capture,
                            credential=None,
                            monotonic_deadline=float("inf"),
                        )
                    popen.assert_not_called()
                capture.close()

    def test_post_spawn_selector_failure_kills_and_reaps_process(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "sleep-native"
            write_fake_native(executable, mode="sleep")
            runtime = FilesystemLiveExecutionRuntime(root)
            logical_argv = [str(executable), "review"]
            stdin = b"{}"
            scope = self._launch_plan()["effect_scope"]
            plan = build_live_launch_plan(
                scope,
                logical_argv=logical_argv,
                normalized_containment_argv=logical_argv,
                stdin=stdin,
                contained_environment={},
                runtime_ref_sha256="d" * 64,
                apparatus_sha256="4" * 64,
                command_ref_sha256="e" * 64,
                credential_profile_id="caplab-openai-revbench",
                credential_profile_sha256="f" * 64,
                timeout_seconds=5,
                execution_deadline_at="2099-01-01T00:00:00Z",
                stdout_limit=1024,
                stderr_limit=1024,
            )
            intent = self._execution_intent(
                "3", plan, custody_domain_id=runtime.custody_domain_id
            )
            intent["execution_deadline_at"] = "2099-01-01T00:00:00Z"
            spawned = []
            original_popen = subprocess.Popen

            def remember(*args, **kwargs):
                process = original_popen(*args, **kwargs)
                spawned.append(process)
                return process

            with runtime.claim_execution(intent) as execution:
                capture = execution.claim_process(plan)
                with (
                    mock.patch(
                        "caplab.revbench.codex.subprocess.Popen", side_effect=remember
                    ),
                    mock.patch(
                        "caplab.revbench.codex.selectors.DefaultSelector.register",
                        side_effect=RuntimeError("injected selector failure"),
                    ),
                ):
                    with self.assertRaisesRegex(RuntimeError, "selector failure"):
                        _run_owned_process(
                            logical_argv,
                            logical_argv,
                            logical_argv,
                            stdin,
                            contained_environment={},
                            runtime_ref_sha256="d" * 64,
                            apparatus_sha256="4" * 64,
                            command_ref_sha256="e" * 64,
                            credential_profile_id="caplab-openai-revbench",
                            credential_profile_sha256="f" * 64,
                            pass_fds=(),
                            capture=capture,
                            credential=None,
                            monotonic_deadline=float("inf"),
                        )
            self.assertEqual(len(spawned), 1)
            self.assertIsNotNone(spawned[0].returncode)

    def test_armed_incomplete_process_recovers_prefix_without_rearming(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan(arm="mutant", assignment_index=1)
            execution_intent = self._execution_intent(
                "1", plan, custody_domain_id=runtime.custody_domain_id
            )

            with runtime.claim_execution(execution_intent) as execution:
                process = execution.claim_process(plan)
                self.assertIsInstance(process, FreshProcessCapture)
                process.write_stdout(b'{"type":"item.completed"}\n')
                process.write_stderr(b"warning prefix\n")
                process.close()

            with runtime.claim_execution(execution_intent) as recovered_execution:
                recovered = recovered_execution.claim_process(plan)

            self.assertIsInstance(recovered, RecoveredProcessCapture)
            self.assertEqual(recovered.invocation_state, "uncertain")
            self.assertEqual(recovered.termination, "executor-interrupted")
            self.assertEqual(recovered.stdout, b'{"type":"item.completed"}\n')
            self.assertEqual(recovered.stderr, b"warning prefix\n")
            self.assertFalse(hasattr(recovered, "arm"))
            self.assertIsNotNone(recovered.recovery)
            first_recovery = recovered.recovery
            with runtime.claim_execution(execution_intent) as replayed_execution:
                replayed = replayed_execution.claim_process(plan)
            self.assertEqual(replayed.recovery, first_recovery)
            self.assertEqual(replayed.recovery["process_started_at"], None)
            self.assertEqual(replayed.recovery["process_completed_at"], None)

    def test_any_incomplete_intent_is_uncertain_and_never_reopens(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan(process_kind="version-probe")
            execution_intent = self._execution_intent(
                "4", plan, custody_domain_id=runtime.custody_domain_id
            )

            with runtime.claim_execution(execution_intent) as execution:
                process = execution.claim_process(plan)
                self.assertIsInstance(process, FreshProcessCapture)
                process.close()

            with runtime.claim_execution(execution_intent) as recovered_execution:
                recovered = recovered_execution.claim_process(plan)

            self.assertIsInstance(recovered, RecoveredProcessCapture)
            self.assertEqual(recovered.invocation_state, "uncertain")
            self.assertEqual(recovered.termination, "executor-interrupted")
            self.assertEqual(recovered.stdout, b"")
            self.assertEqual(recovered.stderr, b"")

    def test_restart_uses_retained_intent_instead_of_renewing_time_budget(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan(process_kind="version-probe")
            original = self._execution_intent(
                "5", plan, custody_domain_id=runtime.custody_domain_id
            )
            with runtime.claim_execution(original) as execution:
                process = execution.claim_process(plan)
                process.close()

            identity = {
                "schema_version": "caplab-revbench-live-execution-identity/1",
                "authorization_id": original["authorization_id"],
                "manifest_sha256": original["manifest_sha256"],
                "experiment_id": original["experiment_id"],
                "binding_id": original["binding_id"],
                "custody_domain_id": original["custody_domain_id"],
            }
            with runtime.claim_or_resume_execution(identity) as resumed:
                self.assertTrue(resumed.resumed)
                self.assertEqual(resumed.intent, original)
            self.assertEqual(runtime.retained_execution_intent(identity), original)

    def test_finalization_timestamp_is_durable_and_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan(process_kind="version-probe")
            intent = self._execution_intent(
                "7", plan, custody_domain_id=runtime.custody_domain_id
            )
            with runtime.claim_execution(intent) as execution:
                process = execution.claim_process(plan)
                timestamp = process.intent["intent_recorded_at"]
                process.complete(
                    {
                        "schema_version": "caplab-revbench-live-process-completion/1",
                        "process_id": live_process_id(plan),
                        "launch_attempted_at": timestamp,
                        "process_started_at": timestamp,
                        "process_completed_at": timestamp,
                        "completion_recorded_at": timestamp,
                        "stdout_complete": True,
                        "stderr_complete": True,
                        "exit_code": 0,
                        "termination": "exited",
                        "invocation_state": "invoked",
                    }
                )
                first = execution.finalization_recorded_at()
            with runtime.claim_execution(intent) as resumed:
                second = resumed.finalization_recorded_at()
            self.assertEqual(first, second)

    def test_claim_publication_failure_recovers_global_effect_without_relaunch(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan(process_kind="version-probe")
            intent = self._execution_intent(
                "6", plan, custody_domain_id=runtime.custody_domain_id
            )
            original_write = custody._write_exclusive
            failed = False

            def fail_claim_index(root, name, payload):
                nonlocal failed
                if root.name == "claims" and not failed:
                    failed = True
                    raise LiveExecutionCustodyError("injected_claim_index_failure")
                return original_write(root, name, payload)

            with runtime.claim_execution(intent) as execution:
                with mock.patch.object(
                    custody, "_write_exclusive", side_effect=fail_claim_index
                ):
                    with self.assertRaisesRegex(
                        LiveExecutionCustodyError, "injected_claim_index_failure"
                    ):
                        execution.claim_process(plan)

            with runtime.claim_execution(intent) as resumed:
                recovered = resumed.claim_process(plan)
            self.assertIsInstance(recovered, RecoveredProcessCapture)
            self.assertEqual(recovered.invocation_state, "uncertain")
            self.assertEqual(recovered.termination, "executor-interrupted")

    def test_manifest_claim_repairs_a_crash_before_session_materialization(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan(process_kind="version-probe")
            intent = self._execution_intent(
                "8", plan, custody_domain_id=runtime.custody_domain_id
            )
            original = custody._recover_execution_root
            failed = False

            def fail_after_manifest_claim(root, retained):
                nonlocal failed
                if not failed:
                    failed = True
                    raise LiveExecutionCustodyError("injected_session_gap")
                return original(root, retained)

            with mock.patch.object(
                custody,
                "_recover_execution_root",
                side_effect=fail_after_manifest_claim,
            ):
                with self.assertRaisesRegex(
                    LiveExecutionCustodyError, "injected_session_gap"
                ):
                    runtime.claim_execution(intent)

            identity = {
                "schema_version": "caplab-revbench-live-execution-identity/1",
                **{
                    field: intent[field]
                    for field in (
                        "authorization_id",
                        "manifest_sha256",
                        "experiment_id",
                        "binding_id",
                        "custody_domain_id",
                    )
                },
            }
            self.assertEqual(runtime.retained_execution_intent(identity), intent)
            with runtime.claim_execution(intent) as resumed:
                with self.assertRaisesRegex(
                    LiveExecutionCustodyError, "recovery_cannot_launch"
                ):
                    resumed.claim_process(plan)

    def test_effect_directory_gap_recovers_uncertain_without_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan(process_kind="version-probe")
            intent = self._execution_intent(
                "3", plan, custody_domain_id=runtime.custody_domain_id
            )
            original = custody._write_exclusive
            failed = False

            def fail_first_effect_record(root, name, payload):
                nonlocal failed
                if (
                    root.name == live_effect_id(plan["effect_scope"])
                    and name == "claim.json"
                    and not failed
                ):
                    failed = True
                    raise LiveExecutionCustodyError("injected_effect_gap")
                return original(root, name, payload)

            with runtime.claim_execution(intent) as execution:
                with mock.patch.object(
                    custody, "_write_exclusive", side_effect=fail_first_effect_record
                ):
                    with self.assertRaisesRegex(
                        LiveExecutionCustodyError, "live_effect_intent_publish_failed"
                    ):
                        execution.claim_process(plan)

            with runtime.claim_execution(intent) as resumed:
                recovered = resumed.claim_process(plan)
            self.assertIsInstance(recovered, RecoveredProcessCapture)
            self.assertEqual(recovered.invocation_state, "uncertain")
            self.assertEqual(recovered.termination, "executor-interrupted")

    def test_monotonic_total_deadline_cannot_be_renewed_by_wall_clock_rollback(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            logical_argv = ["/must-not-run", "--version"]
            scope = self._launch_plan(process_kind="version-probe")["effect_scope"]
            plan = build_live_launch_plan(
                scope,
                logical_argv=logical_argv,
                normalized_containment_argv=logical_argv,
                stdin=b"",
                contained_environment={},
                runtime_ref_sha256="d" * 64,
                apparatus_sha256="4" * 64,
                command_ref_sha256="e" * 64,
                credential_profile_id="caplab-openai-revbench",
                credential_profile_sha256="f" * 64,
                timeout_seconds=5,
                execution_deadline_at="2099-01-01T00:00:00Z",
                stdout_limit=1024,
                stderr_limit=1024,
            )
            intent = self._execution_intent(
                "5", plan, custody_domain_id=runtime.custody_domain_id
            )
            intent["execution_deadline_at"] = "2099-01-01T00:00:00Z"
            with runtime.claim_execution(intent) as execution:
                capture = execution.claim_process(plan)
                with (
                    mock.patch(
                        "caplab.revbench.codex.time.monotonic", return_value=10.0
                    ),
                    mock.patch("caplab.revbench.codex.subprocess.Popen") as popen,
                ):
                    observation = _run_owned_process(
                        logical_argv,
                        logical_argv,
                        logical_argv,
                        b"",
                        contained_environment={},
                        runtime_ref_sha256="d" * 64,
                        apparatus_sha256="4" * 64,
                        command_ref_sha256="e" * 64,
                        credential_profile_id="caplab-openai-revbench",
                        credential_profile_sha256="f" * 64,
                        pass_fds=(),
                        capture=capture,
                        credential=None,
                        monotonic_deadline=9.0,
                    )
                popen.assert_not_called()
            self.assertEqual(observation.invocation_state, "not-invoked")
            self.assertEqual(observation.termination, "authorization-expired")

    def test_authorization_cannot_move_to_a_fresh_custody_domain(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            first_root = parent / "first"
            second_root = parent / "second"
            first_root.mkdir(mode=0o700)
            second_root.mkdir(mode=0o700)
            first = FilesystemLiveExecutionRuntime(first_root)
            second = FilesystemLiveExecutionRuntime(second_root)
            self.assertNotEqual(first.custody_domain_id, second.custody_domain_id)
            plan = self._launch_plan(process_kind="version-probe")
            intent = self._execution_intent(
                "a", plan, custody_domain_id=first.custody_domain_id
            )
            with self.assertRaisesRegex(
                LiveExecutionCustodyError, "custody_domain_mismatch"
            ):
                second.claim_execution(intent)

    def test_uncertain_recovery_syncs_stream_prefix_before_sealing_digest(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan(process_kind="version-probe")
            intent = self._execution_intent(
                "9", plan, custody_domain_id=runtime.custody_domain_id
            )
            with runtime.claim_execution(intent) as execution:
                process = execution.claim_process(plan)
                process.write_stdout(b"visible-prefix")
                process.close()

            original = os.fdatasync
            synced_regular_files = 0

            def observe(descriptor):
                nonlocal synced_regular_files
                if stat.S_ISREG(os.fstat(descriptor).st_mode):
                    synced_regular_files += 1
                return original(descriptor)

            with mock.patch.object(custody.os, "fdatasync", side_effect=observe):
                with runtime.claim_execution(intent) as resumed:
                    recovered = resumed.claim_process(plan)
            self.assertEqual(recovered.stdout, b"visible-prefix")
            self.assertGreaterEqual(synced_regular_files, 2)

    def test_launch_plan_identity_and_declared_sequence_prevent_plan_swaps(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            expected = self._launch_plan(process_kind="version-probe")
            swapped = self._launch_plan(
                process_kind="version-probe", argv_sha256="0" * 64
            )
            self.assertNotEqual(live_process_id(expected), live_process_id(swapped))
            intent = self._execution_intent(
                "a", expected, custody_domain_id=runtime.custody_domain_id
            )

            with runtime.claim_execution(intent) as execution:
                with self.assertRaisesRegex(
                    LiveExecutionCustodyError, "process_not_declared"
                ):
                    execution.claim_process(swapped)
                process = execution.claim_process(expected)
                process.close()

    def test_next_process_cannot_be_claimed_before_prior_completion(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            version = self._launch_plan(process_kind="version-probe")
            native = self._launch_plan(process_kind="native-review")
            intent = self._execution_intent(
                "f",
                version,
                native,
                custody_domain_id=runtime.custody_domain_id,
            )
            with runtime.claim_execution(intent) as execution:
                first = execution.claim_process(version)
                first.close()
                with self.assertRaisesRegex(
                    LiveExecutionCustodyError, "prior_process_not_completed"
                ):
                    execution.claim_process(native)
                effect_root = (
                    runtime.root / "effects" / live_effect_id(version["effect_scope"])
                )
                self.assertFalse((effect_root / "recovery.json").exists())

    def test_new_authorization_cannot_replay_same_manifest_effect(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan()
            first = self._execution_intent(
                "b", plan, custody_domain_id=runtime.custody_domain_id
            )
            second = self._execution_intent(
                "c", plan, custody_domain_id=runtime.custody_domain_id
            )
            with runtime.claim_execution(first) as execution:
                process = execution.claim_process(plan)
                process.close()

            with self.assertRaisesRegex(
                LiveExecutionCustodyError, "manifest_already_claimed"
            ):
                runtime.claim_execution(second)

    def test_sealed_execution_is_terminal_and_idempotently_readable(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan()
            intent = self._execution_intent(
                "d", plan, custody_domain_id=runtime.custody_domain_id
            )
            sealed = {"schema_version": "caplab-revbench-live-seal/1", "attempts": []}
            with runtime.claim_execution(intent) as execution:
                process = execution.claim_process(plan)
                process.close()
                execution.seal(sealed)
                with self.assertRaisesRegex(
                    LiveExecutionCustodyError, "live_execution_sealed"
                ):
                    execution.claim_process(plan)
            with runtime.claim_execution(intent) as recovered:
                self.assertEqual(recovered.sealed, sealed)
                with self.assertRaisesRegex(
                    LiveExecutionCustodyError, "live_execution_sealed"
                ):
                    recovered.claim_process(plan)

    def test_invalid_completion_enum_is_rejected_before_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan()
            intent = self._execution_intent(
                "e", plan, custody_domain_id=runtime.custody_domain_id
            )
            with runtime.claim_execution(intent) as execution:
                process = execution.claim_process(plan)
                with self.assertRaisesRegex(
                    LiveExecutionCustodyError, "process_completion_invalid"
                ):
                    process.complete(
                        {
                            "schema_version": "caplab-revbench-live-process-completion/1",
                            "process_id": live_process_id(plan),
                            "launch_attempted_at": "2026-08-14T00:00:00Z",
                            "process_started_at": "2026-08-14T00:00:00Z",
                            "process_completed_at": "2026-08-14T00:00:01Z",
                            "completion_recorded_at": "2026-08-14T00:00:01Z",
                            "stdout_complete": True,
                            "stderr_complete": True,
                            "exit_code": 0,
                            "termination": "made-up",
                            "invocation_state": "invoked",
                        }
                    )
                process.close()

    def test_spawn_failure_launch_time_must_precede_completion_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = FilesystemLiveExecutionRuntime(Path(temporary))
            plan = self._launch_plan(case_id="temporal")
            intent = self._execution_intent(
                "0", plan, custody_domain_id=runtime.custody_domain_id
            )
            with runtime.claim_execution(intent) as execution:
                process = execution.claim_process(plan)
                with self.assertRaisesRegex(
                    LiveExecutionCustodyError, "process_completion_invalid"
                ):
                    process.complete(
                        {
                            "schema_version": "caplab-revbench-live-process-completion/1",
                            "process_id": live_process_id(plan),
                            "launch_attempted_at": "2026-08-14T00:00:02Z",
                            "process_started_at": None,
                            "process_completed_at": None,
                            "completion_recorded_at": "2026-08-14T00:00:01Z",
                            "stdout_complete": True,
                            "stderr_complete": True,
                            "exit_code": None,
                            "termination": "spawn-failure",
                            "invocation_state": "not-invoked",
                        }
                    )
                process.close()

    def test_visible_record_is_resynced_before_retry_trusts_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "owned"
            root.mkdir(mode=0o700)
            original = os.fsync
            failed = False

            def fail_first_directory_sync(descriptor):
                nonlocal failed
                if stat.S_ISDIR(os.fstat(descriptor).st_mode) and not failed:
                    failed = True
                    raise OSError("injected directory sync failure")
                return original(descriptor)

            with mock.patch.object(
                custody.os, "fsync", side_effect=fail_first_directory_sync
            ):
                with self.assertRaisesRegex(
                    LiveExecutionCustodyError, "record_publish_failed"
                ):
                    custody._write_exclusive(
                        root, "intent.json", canonical_json({"intent": "one-shot"})
                    )
            self.assertTrue((root / "intent.json").exists())

            directory_syncs = 0

            def count_directory_sync(descriptor):
                nonlocal directory_syncs
                if stat.S_ISDIR(os.fstat(descriptor).st_mode):
                    directory_syncs += 1
                return original(descriptor)

            with mock.patch.object(
                custody.os, "fsync", side_effect=count_directory_sync
            ):
                self.assertEqual(
                    custody._read_canonical_document(root / "intent.json"),
                    {"intent": "one-shot"},
                )
            self.assertGreaterEqual(directory_syncs, 1)

    def test_existing_effect_directory_is_resynced_with_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            effect = root / "effect"
            effect.mkdir(mode=0o700)
            original = os.fsync
            synced_inodes = []

            def observe(descriptor):
                metadata = os.fstat(descriptor)
                if stat.S_ISDIR(metadata.st_mode):
                    synced_inodes.append(metadata.st_ino)
                return original(descriptor)

            with mock.patch.object(custody.os, "fsync", side_effect=observe):
                self.assertFalse(custody._mkdir_exclusive(effect))
            self.assertIn(effect.stat().st_ino, synced_inodes)
            self.assertIn(root.stat().st_ino, synced_inodes)


if __name__ == "__main__":
    unittest.main()
