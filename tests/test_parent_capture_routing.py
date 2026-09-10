"""An explicit parent-owned route supports nested tools and preserves its evidence."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from caplab.capture_network_policy import (
    build_capture_network_policy,
    install_capture_network_policy,
)
from caplab.capture_network_transport import capture_routed_network
from caplab.capture_network_verify import verify_capture_routing
from test_capture_network_transport import run_outer
from test_capture_network_verify import inputs, reseal, sha, write

PROFILE = "parent-user/v1"


def inspect(root):
    return verify_capture_routing(
        root / "network", **inputs(root), expected_namespace_profile=PROFILE
    )


def reseal_identity(root, identity):
    """Alter only new test custody, including every copy and hash of its identity."""
    network = root / "network"
    write(network / "identity.json", identity)
    for name in ("policy/preflight.json", "policy/installation.json"):
        path = network / name
        document = json.loads(path.read_bytes())
        document["network_identity"] = identity
        write(path, document)
    for name in ("command.json", "ready.json", "terminal.json"):
        path = network / name
        document = json.loads(path.read_bytes())
        document["network_identity_sha256"] = sha(network / "identity.json")
        write(path, document)
    reseal(root)


class ParentCaptureRoutingTests(unittest.TestCase):
    def run_route(self, root, mode="normal"):
        process = run_outer(root, mode, namespace_profile=PROFILE)
        self.assertEqual(
            process["return_code"], 0, (root / "outer/native.stderr").read_text()
        )
        self.assertTrue(process["streams_complete"])
        return json.loads((root / "result.json").read_bytes())

    def test_parent_owned_route_and_nested_sandbox_have_anchored_inspection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.run_route(root)
            files = {p: sha(p) for p in root.rglob("*") if p.is_file()}
            report = inspect(root)
            self.assertEqual(report["status"], "verified-observation")
            self.assertEqual(report["schema"], "caplab.capture-routing-inspection/v2")
            self.assertEqual(report["namespace_profile"], PROFILE)
            identity = json.loads((root / "network/identity.json").read_bytes())
            self.assertEqual(
                identity["workload_user_parent_namespace"],
                identity["network_owner_user_namespace"],
            )
            self.assertNotEqual(
                identity["workload_user_namespace"],
                identity["network_owner_user_namespace"],
            )
            self.assertEqual(report["network_identity"], identity)
            self.assertFalse(report["study_eligible"])
            self.assertFalse(report["native_containment_verified"])
            self.assertEqual(files, {p: sha(p) for p in files})
            with self.assertRaises(ValueError):
                verify_capture_routing(root / "network", **inputs(root))
            arguments = inputs(root)
            write(root / "plan.json", arguments.pop("plan"))
            command = [
                sys.executable,
                "scripts/inspect_capture_routing.py",
                str(root / "network"),
                "--policy",
                str(root / "plan.json"),
            ]
            for key, value in arguments.items():
                command += ["--" + key.replace("_", "-"), str(value)]
            rejected = subprocess.run(command, capture_output=True, timeout=10)
            self.assertEqual(rejected.returncode, 2, rejected.stderr.decode())
            self.assertEqual(rejected.stdout, b"")
            accepted = subprocess.run(
                command + ["--namespace-profile", PROFILE],
                capture_output=True,
                timeout=10,
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr.decode())
            self.assertEqual(json.loads(accepted.stdout), report)

    def test_rehashed_ownership_contradictions_are_refused_without_descriptor_leaks(
        self,
    ):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.run_route(root)
            original = {
                p: p.read_bytes() for p in (root / "network").rglob("*") if p.is_file()
            }
            identity = json.loads(original[root / "network/identity.json"])
            owner = identity["network_owner_user_namespace"]
            cases = [
                ("profile", "workload-user/v1"),
                ("peer_pid", True),
                ("workload_user_namespace", owner),
                ("workload_user_parent_namespace", identity["workload_user_namespace"]),
                (
                    "network_owner_user_namespace",
                    identity["supervisor_namespaces"]["user"],
                ),
                ("network_namespace", identity["supervisor_namespaces"]["net"]),
                ("workload_user_namespace", {"device": True, "inode": 123}),
                ("mapping_observer", {"uid": True, "gid": 1000}),
                ("uid_map", [[0, identity["mapping_observer"]["uid"], 1]]),
                ("gid_map", [[1000, identity["mapping_observer"]["gid"], True]]),
                ("gid_map", [[1000, 2**32, 1]]),
                ("uid_map", [[1000, 0, 1], [1001, 1, 1]]),
                (
                    "capabilities",
                    {**identity["capabilities"], "CapEff": "0000000000001000"},
                ),
                ("capabilities", {**identity["capabilities"], "NoNewPrivs": "0"}),
                ("study_eligible", True),
                ("surprise", "extra field"),
            ]
            descriptors = set(os.listdir("/proc/self/fd"))
            for key, value in cases:
                with self.subTest(key=key, value=value):
                    for path, raw in original.items():
                        path.write_bytes(raw)
                    changed = {**identity, key: value}
                    reseal_identity(root, changed)
                    with self.assertRaises(ValueError):
                        inspect(root)
                    self.assertEqual(descriptors, set(os.listdir("/proc/self/fd")))

    def test_credentials_cross_copy_links_and_independent_anchors_are_required(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.run_route(root)
            original = {
                p: p.read_bytes() for p in (root / "network").rglob("*") if p.is_file()
            }
            for name, key, value in [
                ("ready.json", "namespace_profile", "workload-user/v1"),
                ("terminal.json", "network_identity_sha256", "0" * 64),
                ("command.json", "network_identity_sha256", "0" * 64),
                ("identity.json", "peer_pid", 2147483647),
                (
                    "policy/preflight.json",
                    "workload_credentials",
                    {"uid": ["0"] * 4, "gid": ["0"] * 4},
                ),
                ("policy/installation.json", "network_identity", {}),
            ]:
                with self.subTest(name=name, key=key):
                    for path, raw in original.items():
                        path.write_bytes(raw)
                    path = root / "network" / name
                    document = json.loads(path.read_bytes())
                    document[key] = value
                    write(path, document)
                    # For credential changes, keep both policy copies consistent.
                    if key == "workload_credentials":
                        other = root / "network/policy/installation.json"
                        document = json.loads(other.read_bytes())
                        document[key] = value
                        write(other, document)
                    reseal(root)
                    with self.assertRaises(ValueError):
                        inspect(root)
            for path, raw in original.items():
                path.write_bytes(raw)
            arguments = inputs(root)
            identity_path = root / "network/identity.json"
            identity_path.unlink()
            identity_path.symlink_to(root / "result.json")
            with self.assertRaises((ValueError, OSError)):
                inspect(root)
            identity_path.unlink()
            identity_path.write_bytes(original[identity_path])
            document = json.loads((root / "network/ready.json").read_bytes())
            document["ready_observed_monotonic_ns"] += 1
            write(root / "network/ready.json", document)
            reseal(root)
            with self.assertRaises(ValueError):
                verify_capture_routing(
                    root / "network", **arguments, expected_namespace_profile=PROFILE
                )

    def test_parent_failure_paths_preserve_errors_and_close_owned_transport(self):
        for mode in ("missing-tun", "body-error", "timeout", "quarantine"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                result = self.run_route(root, mode)
                self.assertTrue(result["descriptor_population_preserved"])
                expected = (
                    "fixture body failed"
                    if mode == "body-error"
                    else "quarantined"
                    if mode == "quarantine"
                    else "did not stop normally"
                )
                self.assertIn(expected, result["error"]["message"])
                if mode == "quarantine":
                    self.assertFalse((root / "network/process").exists())
                    self.assertFalse((root / "network/terminal.json").exists())
                    continue
                terminal = json.loads((root / "network/terminal.json").read_bytes())
                self.assertEqual(
                    terminal["schema"], "caplab.capture-routing-terminal/v2"
                )
                self.assertEqual(terminal["normal_shutdown"], mode == "body-error")
                self.assertEqual(terminal["body_completed"], mode == "timeout")
                if mode == "missing-tun":
                    self.assertFalse((root / "network/ready.json").exists())
                    continue
                installation = json.loads(
                    (root / "network/policy/installation.json").read_bytes()
                )
                plan = build_capture_network_policy(
                    [{"address": "198.18.0.1", "port": 39071}]
                )
                with self.assertRaises(ValueError):
                    verify_capture_routing(
                        root / "network",
                        plan=plan,
                        expected_policy_sha256=plan["network_policy_sha256"],
                        expected_terminal_sha256=sha(root / "network/terminal.json"),
                        expected_ready_sha256=sha(root / "network/ready.json"),
                        expected_peer_pid=installation["peer_pid"],
                        expected_namespace_profile=PROFILE,
                    )

    def test_profile_selection_precedes_peer_access_and_rejects_legacy_custody(self):
        plan = build_capture_network_policy([{"address": "198.18.0.1", "port": 39071}])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for profile in (None, True, [], "parent", "parent-user/v2"):
                kwargs = dict(
                    plan=plan,
                    expected_policy_sha256=plan["network_policy_sha256"],
                    peer_pid=2147483647,
                    output_dir=root / "network",
                    namespace_profile=profile,
                )
                with self.subTest(profile=profile):
                    with self.assertRaises(ValueError):
                        install_capture_network_policy(**kwargs)
                    with self.assertRaises(ValueError):
                        with capture_routed_network(**kwargs, timeout_seconds=8):
                            self.fail("invalid profile reached workload")
                    self.assertFalse((root / "network").exists())
            self.assertEqual(run_outer(root)["return_code"], 0)
            with self.assertRaises(ValueError):
                inspect(root)
