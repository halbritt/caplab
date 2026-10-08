"""Real Quartermaster CLI, native one-shot custody and local process controls.

Set CAPLAB_TEST_SHARED_QM to the explicit SharedAdmissionLedger-capable CLI.
Clock injection controls the native one-second observation granularity only;
processes, custody, catalog projection and shared-home transactions are real.
"""

import contextlib
import copy
import datetime
import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.revbench.custody import (
    FilesystemLiveExecutionRuntime,
    LiveExecutionCustodyError,
)
from caplab.revbench.codex import _run_owned_process, build_live_launch_plan
from caplab.revbench import codex, custody
from caplab.revbench import shared_admission as shared
from caplab.revbench.execution import _terminal_custody_capture
import catalog_support as c
import tests.test_revbench_live_custody as native_fixture

CLI = os.environ.get("CAPLAB_TEST_SHARED_QM")
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def fixture(root, cli):
    def write(name, d):
        p = root / name
        p.write_bytes(canonical_json(d))
        return p

    source = c.catalog_source()
    source["routes"] = source["routes"][:1]
    source["accounts"] = source["accounts"][:1]
    source["accounts"][0]["quota_pool_ids"] = ["fixture-pool"]
    source["profiles"] = source["profiles"][:1]
    source["profiles"][0]["config_home"] = None
    source["profiles"].append(
        {
            "id": "fixture-other",
            "host": "fixture-host",
            "consumer": "surveyor",
            "account_id": "codex-main",
            "config_home": None,
            "credential_ref": None,
        }
    )
    source_path = write("source.json", source)
    published = json.loads(
        subprocess.check_output(
            [
                cli,
                "catalog",
                "publish",
                str(source_path),
                "--releases",
                str(root / "releases"),
                "--publisher",
                "fixture",
            ]
        )
    )
    releasepath = Path(published["path"])
    overlay = c.overlay()
    overlay["harnesses"]["codex"]["native"]["config_home"] = None
    overlay["selections"] = [
        {
            "id": "fixture-enrolled",
            "route": "terra",
            "account": "codex-main",
            "effort": "max",
            "profile": "caplab-codex-main",
            "release": None,
            "enabled": True,
            "roles": [],
            "controls": {"reason": "local process test"},
        }
    ]
    ov = write("overlay.json", overlay)
    release = json.loads(releasepath.read_bytes())
    projection = json.loads(
        subprocess.check_output([cli, "catalog", "project", str(releasepath), str(ov)])
    )

    now = NOW
    row = {
        "record": "quartermaster-observation/1",
        "subject": {"source_id": "agent-usage:codex-main"},
        "kind": "quota",
        "observed_at": now,
        "payload": {
            "catalog_account_id": "codex-main",
            "freshness": "fresh",
            "observation_schema": "agent-usage-quota-observations/1",
            "purpose": "observational_only",
            "catalog_release_id": release["release_id"],
            "generated_at": now,
            "observed_at": now,
            "stale_after_seconds": 600,
            "windows": [
                {
                    "identity_state": "known",
                    "value_state": "observed",
                    "reset_state": "scheduled",
                    "remaining_percent": 50,
                    "applicability": {"state": "known"},
                }
            ],
        },
    }
    row["_content_hash"] = "sha256:" + sha256_hex(canonical_json(row))
    write("observations.json", [row])
    policy = {
        "schema": "quartermaster-shared-admission-policy/1",
        "home_id": "fixture-home",
        "enabled_constraints": ["shared_concurrency_v1", "guarded_launches_v1"],
        "quota_veto_floor_percent": 0,
        "max_observation_age_seconds": 600,
        "charge_reader": {
            "reader_id": "outer-launch",
            "version": "v1",
            "max_concurrent_attempts": 1,
        },
        "pools": [
            {
                "pool_id": "fixture-pool",
                "home_id": "fixture-home",
                "scope": {"kind": "account", "account_ids": ["codex-main"]},
                "total_slots": 2,
                "reserve_floor_ppm": 0,
            }
        ],
        "callers": [
            {
                "caller_id": "caplab",
                "namespace": "caplab",
                "grants": [{"pool_id": "fixture-pool", "ceiling": 2}],
            }
        ],
        "launch_budgets": [
            {
                "pool_id": "fixture-pool",
                "windows": [
                    {
                        "window_id": "fixture-window",
                        "kind": "fixed",
                        "start": "2026-01-01T00:00:00Z",
                        "end": "2027-01-01T00:00:00Z",
                        "limit": 2,
                        "reserve": 0,
                        "caller_limits": {"caplab": 2},
                    }
                ],
            }
        ],
    }
    policy["callers"].append(
        {
            "caller_id": "other",
            "namespace": "surveyor",
            "grants": [{"pool_id": "fixture-pool", "ceiling": 2}],
        }
    )
    policy["launch_budgets"][0]["windows"][0]["caller_limits"]["other"] = 2
    write("policy.json", policy)
    return {
        "release_path": str(releasepath),
        "overlay_path": str(ov),
        "policy_path": str(root / "policy.json"),
        "observations_path": str(root / "observations.json"),
        "entry": projection["entries"][0]["key"],
    }


@unittest.skipUnless(CLI, "set CAPLAB_TEST_SHARED_QM to the explicit candidate CLI")
class SharedAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.runtime = FilesystemLiveExecutionRuntime(self.root)
        self.paths = fixture(self.root, CLI)
        self.document = {
            "schema_version": shared.SCHEMA,
            "cli": CLI,
            "cli_sha256": sha256_hex(Path(CLI).read_bytes()),
            "home": str(self.root / "shared-home"),
            "home_id": "fixture-home",
            "caller_id": "caplab",
            "custody_domain_id": self.runtime.custody_domain_id,
            "binding_id": "bnd-" + "8" * 64,
            "credential_profile_sha256": "f" * 64,
            **self.paths,
        }
        for name in ("release", "overlay", "policy"):
            self.document[name + "_sha256"] = sha256_hex(
                Path(self.document[name + "_path"]).read_bytes()
            )
        self.config = self.root / "enrollment.json"
        self.config.write_bytes(canonical_json(self.document))
        self.enrollment = shared.SharedAdmissionEnrollment.read(self.config)
        self.clocks = contextlib.ExitStack()
        self.addCleanup(self.clocks.close)
        for target in (shared, codex, custody):
            self.clocks.enter_context(
                mock.patch.object(
                    target,
                    "_now" if target is shared else "_timestamp",
                    return_value=NOW,
                )
            )

    def plan(
        self,
        command=None,
        *,
        case="case-a",
        contained=True,
        kind="native-review",
        bind_root=False,
    ):
        logical = ["/bin/true"] if command is None else command
        argv = (
            [
                "/usr/bin/bwrap",
                "--unshare-all",
                "--die-with-parent",
                "--new-session",
                *(["--ro-bind", "/", "/"] if bind_root else []),
                "--",
                *logical,
            ]
            if contained
            else logical
        )
        scope = native_fixture.LiveExecutionCustodyTests()._launch_plan(
            case_id=case, process_kind=kind
        )["effect_scope"]
        return (
            build_live_launch_plan(
                scope,
                logical_argv=logical,
                normalized_containment_argv=argv,
                stdin=b"",
                contained_environment={},
                runtime_ref_sha256="d" * 64,
                apparatus_sha256="4" * 64,
                command_ref_sha256="e" * 64,
                credential_profile_id="caplab-openai-revbench",
                credential_profile_sha256="f" * 64,
                timeout_seconds=5,
                execution_deadline_at="2027-01-01T00:00:00Z",
                stdout_limit=1024,
                stderr_limit=1024,
            ),
            argv,
            logical,
        )

    def claim(self, plan):
        intent = native_fixture.LiveExecutionCustodyTests()._execution_intent(
            "7", plan, custody_domain_id=self.runtime.custody_domain_id
        )
        session = self.runtime.claim_execution(intent)
        self.addCleanup(session.close)
        shared.require_retained_enrollment(session, self.enrollment)
        capture = session.claim_process(plan)
        return session, capture

    def run_process(self, capture, plan, argv, logical, deadline=float("inf")):
        capture.shared_admission = self.enrollment.capture(capture)
        return _run_owned_process(
            argv,
            argv,
            logical,
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
            monotonic_deadline=deadline,
        )

    def snapshot(self):
        raw = subprocess.check_output(
            [
                CLI,
                "admission",
                "status",
                "--home",
                self.document["home"],
                "--home-id",
                "fixture-home",
                "--now",
                NOW,
            ]
        )
        return json.loads(raw)

    def test_real_outer_exec_failure_counts_once_and_recovery_does_not_charge_again(
        self,
    ):
        plan, argv, logical = self.plan(["/not-a-caplab-child-executable"])
        session, capture = self.claim(plan)
        observation = self.run_process(capture, plan, argv, logical)
        self.assertEqual(observation.invocation_state, "invoked")
        self.assertNotEqual(
            observation.exit_code, 0
        )  # real outer child, contained exec fails
        self.assertIn(b"execvp", observation.stderr)
        terminal = _terminal_custody_capture(session, plan, capture, self.enrollment)
        expected = {
            "slots": 1,
            "windows": {"fixture-window": {"spent": 1, "outstanding": 0}},
        }
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"], expected)
        before = self.snapshot()["records"]
        _terminal_custody_capture(session, plan, terminal, self.enrollment)
        self.assertEqual(self.snapshot()["records"], before)
        with self.assertRaisesRegex(LiveExecutionCustodyError, "native_right_closed"):
            self.enrollment.capture(terminal).prepare(argv)

    def test_real_popen_exec_error_is_uncertain_and_retains_both_reservations(self):
        plan, argv, logical = self.plan(
            ["/no-such-outer-caplab-executable"], contained=False
        )
        session, capture = self.claim(plan)
        observation = self.run_process(capture, plan, argv, logical)
        self.assertEqual(observation.termination, "spawn-failure")
        _terminal_custody_capture(session, plan, capture, self.enrollment)
        snap = self.snapshot()
        self.assertEqual(
            snap["pools"]["fixture-pool"],
            {"slots": 1, "windows": {"fixture-window": {"spent": 0, "outstanding": 1}}},
        )
        self.assertEqual(
            next(iter(snap["allocations"].values()))["counts"]["possible_unknown"], 1
        )

    def test_real_namespace_tree_closure_settles_once_and_preserves_spent_launch(self):
        plan, argv, logical = self.plan(["/bin/sleep", "0.3"], bind_root=True)
        session, capture = self.claim(plan)
        observation = self.run_process(capture, plan, argv, logical)
        self.assertEqual(observation.exit_code, 0)
        terminal = _terminal_custody_capture(session, plan, capture, self.enrollment)
        proof = json.loads(
            (
                capture.custody_root / "shared-admission-namespace-closure.json"
            ).read_bytes()
        )
        self.assertEqual(proof["namespace_init"]["namespace_pids"][-1], 1)
        self.assertEqual(proof["ended_at"], NOW)
        self.assertEqual(
            self.snapshot()["pools"]["fixture-pool"],
            {"slots": 0, "windows": {"fixture-window": {"spent": 1, "outstanding": 0}}},
        )
        before = self.snapshot()["records"]
        _terminal_custody_capture(session, plan, terminal, self.enrollment)
        self.assertEqual(self.snapshot()["records"], before)

    def test_positive_prechild_retirement_returns_unused_slot_and_bound(self):
        plan, argv, logical = self.plan()
        session, capture = self.claim(plan)
        gate = self.enrollment.capture(capture)
        self.assertTrue(gate.prepare(argv))
        # Honest code path before any Popen: complete the consumed native right.
        capture.shared_admission = gate
        codex._complete_before_launch(capture, "preflight-refused")
        self.assertEqual(
            self.snapshot()["pools"]["fixture-pool"],
            {"slots": 0, "windows": {"fixture-window": {"spent": 0, "outstanding": 0}}},
        )
        result = json.loads(
            (
                capture.custody_root / "shared-admission-terminal-result.json"
            ).read_bytes()
        )
        self.assertEqual((result["launched"], result["unused"]), (0, 1))

    def test_crash_after_permit_has_no_replay_right_and_keeps_hold(self):
        plan, argv, logical = self.plan()
        session, capture = self.claim(plan)
        self.assertTrue(self.enrollment.capture(capture).prepare(argv))
        capture.close()  # lost process/creation receipt; do not infer zero
        recovered = session.claim_process(plan)
        self.assertEqual(recovered.invocation_state, "uncertain")
        result = self.enrollment.capture(recovered).reconcile(None)
        self.assertEqual(result["status"], "hold")
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"]["slots"], 1)
        with self.assertRaisesRegex(LiveExecutionCustodyError, "native_right_closed"):
            self.enrollment.capture(recovered).prepare(argv)

    def test_sealed_native_recovery_reconciles_closed_right_without_new_claim(self):
        plan, argv, logical = self.plan()
        session, capture = self.claim(plan)
        self.assertTrue(self.enrollment.capture(capture).prepare(argv))
        # Native completion survives loss of the shared settlement response.
        codex._complete_before_launch(capture, "preflight-refused")
        intent = copy.deepcopy(session.intent)
        session.seal({"fixture": "sealed custody, no measurement claim"})
        session.close()
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"]["slots"], 1)
        recovered = self.runtime.claim_execution(intent)
        self.addCleanup(recovered.close)
        self.assertIsNotNone(recovered.sealed)
        results = self.enrollment.reconcile_session(recovered)
        self.assertEqual(results[0]["status"], "settled")
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"]["slots"], 0)
        records = self.snapshot()["records"]
        self.enrollment.reconcile_session(recovered)
        self.assertEqual(self.snapshot()["records"], records)
        with self.assertRaisesRegex(LiveExecutionCustodyError, "live_execution_sealed"):
            recovered.claim_process(plan)

    def test_creation_crossing_clock_second_is_known_child_with_unresolved_time(self):
        plan, argv, logical = self.plan()
        session, capture = self.claim(plan)
        after = (
            datetime.datetime.fromisoformat(NOW.replace("Z", "+00:00"))
            + datetime.timedelta(seconds=1)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        with (
            mock.patch.object(
                codex, "_timestamp", side_effect=[NOW, after, after, after]
            ),
            mock.patch.object(shared, "_now", return_value=after),
        ):
            self.run_process(capture, plan, argv, logical)
            _terminal_custody_capture(session, plan, capture, self.enrollment)
            self.assertEqual(
                self.enrollment.capture(session.claim_process(plan)).reconcile(
                    session.claim_process(plan).completion
                )["status"],
                "hold",
            )
        with mock.patch.object(shared, "_now", return_value=after):
            raw = subprocess.check_output(
                [
                    CLI,
                    "admission",
                    "status",
                    "--home",
                    self.document["home"],
                    "--home-id",
                    "fixture-home",
                    "--now",
                    after,
                ]
            )
        entry = next(iter(json.loads(raw)["allocations"].values()))
        self.assertEqual(
            entry["counts"],
            {"known_created": 1, "possible_unknown": 0, "creation_time_unknown": 1},
        )
        self.assertIsNone(entry["terminal"])

    def test_pinned_enrollment_cannot_be_disabled_or_rebound_on_resume(self):
        plan, argv, logical = self.plan()
        session, capture = self.claim(plan)
        capture.close()
        with self.assertRaisesRegex(
            LiveExecutionCustodyError, "retained_enrollment_required"
        ):
            shared.require_retained_enrollment(session, None)
        changed = copy.deepcopy(self.document)
        changed["binding_id"] = "bnd-" + "9" * 64
        replacement = shared.SharedAdmissionEnrollment(changed)
        with self.assertRaisesRegex(
            LiveExecutionCustodyError, "native_identity_mismatch"
        ):
            replacement.bind_session(session)
        policy = Path(self.document["policy_path"])
        policy.write_bytes(policy.read_bytes() + b" ")
        with self.assertRaisesRegex(LiveExecutionCustodyError, "pin_changed"):
            self.enrollment.check_pins()

    def test_missing_local_allocation_receipt_recovers_committed_home_without_new_admission(
        self,
    ):
        plan, argv, logical = self.plan()
        session, capture = self.claim(plan)
        original = os.link

        def fail_allocation(src, dst, **kwargs):
            if dst == "shared-admission-allocation.json":
                raise OSError("injected durable publication failure")
            return original(src, dst, **kwargs)

        with mock.patch.object(custody.os, "link", side_effect=fail_allocation):
            with self.assertRaisesRegex(
                LiveExecutionCustodyError, "record_publish_failed"
            ):
                self.enrollment.capture(capture).prepare(argv)
        capture.close()
        recovered = session.claim_process(plan)
        before = self.snapshot()["records"]
        result = self.enrollment.capture(recovered).reconcile(None)
        self.assertEqual(result["status"], "hold")
        self.assertEqual(self.snapshot()["records"], before)
        self.assertEqual(self.snapshot()["pools"]["fixture-pool"]["slots"], 1)

    def test_admission_latency_does_not_restart_or_extend_native_deadline(self):
        plan, argv, logical = self.plan()
        session, capture = self.claim(plan)
        observation = self.run_process(
            capture, plan, argv, logical, deadline=time.monotonic() + 0.05
        )
        self.assertEqual(observation.termination, "authorization-expired")
        self.assertIsNone(observation.launch_attempted_at)
        self.assertEqual(
            self.snapshot()["pools"]["fixture-pool"],
            {"slots": 0, "windows": {"fixture-window": {"spent": 0, "outstanding": 0}}},
        )

    def test_quota_becoming_unknown_between_reserve_and_prepare_closes_without_creation(
        self,
    ):
        plan, argv, logical = self.plan()
        session, capture = self.claim(plan)
        observation_path = Path(self.document["observations_path"])
        original = Path.read_bytes
        reads = 0

        def changed_observation(path):
            nonlocal reads
            if path == observation_path:
                reads += 1
                if reads == 2:
                    observation_path.write_bytes(b"[]")
            return original(path)

        with mock.patch.object(Path, "read_bytes", changed_observation):
            observation = self.run_process(capture, plan, argv, logical)
        self.assertEqual(observation.termination, "preflight-refused")
        self.assertIsNone(observation.launch_attempted_at)
        self.assertEqual(
            self.snapshot()["pools"]["fixture-pool"],
            {"slots": 0, "windows": {"fixture-window": {"spent": 0, "outstanding": 0}}},
        )

    def test_generic_uncontained_child_exit_is_not_a_tree_closure_oracle(self):
        plan, argv, logical = self.plan(contained=False)
        session, capture = self.claim(plan)
        observation = self.run_process(capture, plan, argv, logical)
        self.assertEqual(observation.exit_code, 0)
        terminal = _terminal_custody_capture(session, plan, capture, self.enrollment)
        result = self.enrollment.capture(terminal).reconcile(terminal.completion)
        self.assertEqual(result["code"], "tree_containment_unproved")
        self.assertEqual(
            self.snapshot()["pools"]["fixture-pool"],
            {"slots": 1, "windows": {"fixture-window": {"spent": 1, "outstanding": 0}}},
        )

    def test_old_unenrolled_intent_cannot_be_enrolled_after_claim(self):
        plan, argv, logical = self.plan()
        intent = native_fixture.LiveExecutionCustodyTests()._execution_intent(
            "7", plan, custody_domain_id=self.runtime.custody_domain_id
        )
        with self.runtime.claim_execution(intent):
            pass
        with self.runtime.claim_execution(intent) as session:
            with self.assertRaisesRegex(
                LiveExecutionCustodyError, "late_enrollment_refused"
            ):
                shared.require_retained_enrollment(session, self.enrollment)

    def test_version_helper_and_other_consumer_share_capacity_before_review_root(self):
        version, argv, logical = self.plan(kind="version-probe")
        native, native_argv, native_logical = self.plan()
        intent = native_fixture.LiveExecutionCustodyTests()._execution_intent(
            "7", version, native, custody_domain_id=self.runtime.custody_domain_id
        )
        with self.runtime.claim_execution(intent) as session:
            shared.require_retained_enrollment(session, self.enrollment)
            capture = session.claim_process(version)
            self.run_process(capture, version, argv, logical)
            _terminal_custody_capture(session, version, capture, self.enrollment)
            request = {
                "request_id": "external-consumer",
                "caller_id": "other",
                "route_id": "terra",
                "account_id": "codex-main",
                "max_slots": 1,
                "max_launches": 1,
                "home_id": "fixture-home",
                "valid_until": "2027-01-01T00:00:00Z",
            }
            path = self.root / "other-request.json"
            path.write_bytes(canonical_json(request))
            result = json.loads(
                subprocess.check_output(
                    [
                        CLI,
                        "admission",
                        "reserve",
                        "--home",
                        self.document["home"],
                        "--home-id",
                        "fixture-home",
                        "--now",
                        NOW,
                        "--request",
                        str(path),
                        "--policy",
                        self.paths["policy_path"],
                        "--catalog",
                        self.paths["release_path"],
                        "--observations",
                        self.paths["observations_path"],
                        "--holder-id",
                        "external-holder",
                        "--namespace",
                        "surveyor",
                    ]
                )
            )
            self.assertEqual(result["status"], "admitted")
            native_capture = session.claim_process(native)
            observation = self.run_process(
                native_capture, native, native_argv, native_logical
            )
            self.assertIsNone(observation.launch_attempted_at)
            self.assertEqual(
                self.snapshot()["pools"]["fixture-pool"],
                {
                    "slots": 2,
                    "windows": {"fixture-window": {"spent": 1, "outstanding": 1}},
                },
            )

    def test_enrollment_checks_the_complete_native_binding_not_just_catalog_labels(
        self,
    ):
        import tests.test_revbench as rb
        import tests.test_revbench_codex as native_binding

        registrar = rb.MemoryRegistrar()
        bundle_root = self.root / "bundle"
        bundle_root.mkdir()
        policy, members = native_binding.make_synthetic_bundle_fixture(bundle_root)
        binding, native_ref = native_binding.make_live_codex_binding(
            registrar, policy=policy, member_bytes=members
        )
        document = copy.deepcopy(self.document)
        document["binding_id"] = binding["binding_id"]
        runtime = json.loads(registrar.resolve(binding["configuration"]["runtime_ref"]))
        document["credential_profile_sha256"] = runtime["credential_profile_ref"][
            "sha256"
        ]
        enrollment = shared.SharedAdmissionEnrollment(document)
        spec = {"binding": binding, "native_system_contract_ref": native_ref}
        enrollment.validate_binding(spec, registrar, self.runtime.custody_domain_id)
        wrong = copy.deepcopy(document)
        wrong["credential_profile_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            LiveExecutionCustodyError, "credential_profile_mismatch"
        ):
            shared.SharedAdmissionEnrollment(wrong).validate_binding(
                spec, registrar, self.runtime.custody_domain_id
            )
        tampered = copy.deepcopy(spec)
        tampered["binding"]["reasoning_effort"] = "high"
        with self.assertRaisesRegex(ValueError, "catalog_effort_mismatch"):
            enrollment.validate_binding(
                tampered, registrar, self.runtime.custody_domain_id
            )

    def test_policy_cutoffs_require_fixed_whole_second_native_representation(self):
        original = json.loads(Path(self.document["policy_path"]).read_bytes())
        for label in ("rolling", "fractional-cutoff"):
            with self.subTest(policy=label):
                policy = copy.deepcopy(original)
                window = policy["launch_budgets"][0]["windows"][0]
                if label == "rolling":
                    window["kind"] = "rolling"
                    window.pop("start")
                    window.pop("end")
                    window["duration_seconds"] = 60
                else:
                    window["start"] = "2026-01-01T00:00:00.500000Z"
                path = self.root / (label + ".json")
                path.write_bytes(canonical_json(policy))
                doc = copy.deepcopy(self.document)
                doc["policy_path"] = str(path)
                doc["policy_sha256"] = sha256_hex(path.read_bytes())
                with self.assertRaisesRegex(
                    LiveExecutionCustodyError, "time_resolution_unsupported"
                ):
                    shared.SharedAdmissionEnrollment(doc)
                self.assertFalse(Path(doc["home"]).exists())


class KernelProcessProofTests(unittest.TestCase):
    def test_actual_pidfd_tracks_owned_process_death_and_rejects_unsafe_pid(self):
        from caplab.revbench.process_tree import ProcessWitness, ProcessProofUnavailable

        with self.assertRaises(ProcessProofUnavailable):
            ProcessWitness.open(1)
        process = subprocess.Popen(
            ["/usr/bin/python3", "-I", "-S", "-c", "import time; time.sleep(5)"]
        )
        try:
            with ProcessWitness.open(process.pid) as witness:
                self.assertEqual(witness.fact["pid"], process.pid)
                self.assertEqual(witness.fact["parent_pid"], os.getpid())
                self.assertFalse(witness.dead())
                process.terminate()
                process.wait(timeout=2)
                self.assertTrue(witness.dead(100))
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2)

    def test_actual_namespace_init_quiescence_when_host_permits_pid_namespaces(self):
        from caplab.revbench.process_tree import namespace_init

        # Kernel capability control, not a replacement-harness/model experiment.
        process = subprocess.Popen(
            [
                "/usr/bin/bwrap",
                "--unshare-all",
                "--die-with-parent",
                "--new-session",
                "--ro-bind",
                "/",
                "/",
                "--",
                "/bin/sleep",
                "0.3",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        witness = None
        try:
            witness = namespace_init(process.pid, deadline=time.monotonic() + 1)
            stdout, stderr = process.communicate(timeout=2)
            if witness is None:
                if process.returncode != 0 and b"Operation not permitted" in stderr:
                    self.skipTest(
                        "host refuses PID/user namespace setup; successful namespace closure remains unqualified"
                    )
                self.fail(
                    "namespace init identity was not observed: " + stderr.decode()
                )
            self.assertEqual(witness.fact["namespace_pids"][-1], 1)
            self.assertTrue(witness.dead(100))
        finally:
            if witness is not None:
                witness.close()
            if process.poll() is None:
                process.kill()
                process.wait(timeout=2)
