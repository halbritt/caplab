"""Inspect fresh kernel routing custody, then challenge its evidence links."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from caplab.capture_network_policy import build_capture_network_policy
from test_capture_network_transport import run_outer


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(root):
    result = json.loads((root / "result.json").read_bytes())
    plan = build_capture_network_policy([{"address": "198.18.0.1", "port": 39071}])
    return {
        "plan": plan,
        "expected_policy_sha256": plan["network_policy_sha256"],
        "expected_terminal_sha256": sha(root / "network/terminal.json"),
        "expected_ready_sha256": sha(root / "network/ready.json"),
        "expected_peer_pid": result["handoff"]["peer_pid"],
    }


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True) + "\n")


def reseal(root):
    """Rehash this test's new custody so contradictions reach semantic checks."""
    network = root / "network"
    installation = json.loads((network / "policy/installation.json").read_bytes())
    for name in ("initial", "install", "readback"):
        installation["command_sha256"][name] = sha(
            network / f"policy/{name}-command.json"
        )
        installation["command_receipt_sha256"][name] = sha(
            network / f"policy/{name}/capture.json"
        )
    write(network / "policy/installation.json", installation)
    command = json.loads((network / "command.json").read_bytes())
    command["policy_installation_sha256"] = sha(network / "policy/installation.json")
    write(network / "command.json", command)
    ready = json.loads((network / "ready.json").read_bytes())
    ready["command_sha256"] = sha(network / "command.json")
    write(network / "ready.json", ready)
    terminal = json.loads((network / "terminal.json").read_bytes())
    terminal.update(
        command_sha256=sha(network / "command.json"),
        ready_sha256=sha(network / "ready.json"),
        capture_sha256=sha(network / "process/capture.json"),
    )
    write(network / "terminal.json", terminal)


def reseal_stream(root, directory, stream, raw):
    directory = root / "network" / directory
    (directory / ("native." + stream)).write_bytes(raw)
    receipt = json.loads((directory / "capture.json").read_bytes())
    receipt["streams"][stream].update(
        bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()
    )
    receipt["retained_stream_bytes"] = sum(
        s["bytes"] for s in receipt["streams"].values()
    )
    write(directory / "capture.json", receipt)
    if directory.name == "readback":
        path = root / "network/policy/installation.json"
        installation = json.loads(path.read_bytes())
        installation["readback_sha256"] = hashlib.sha256(raw).hexdigest()
        write(path, installation)
    reseal(root)


class CaptureNetworkVerifyTests(unittest.TestCase):
    def test_real_routing_custody_agrees_with_independent_handoff_anchors(self):
        from caplab.capture_network_verify import verify_capture_routing

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            process = run_outer(root)
            self.assertEqual(
                process["return_code"], 0, (root / "outer/native.stderr").read_text()
            )
            arguments = inputs(root)
            files = {p: sha(p) for p in root.rglob("*") if p.is_file()}
            descriptors = set(os.listdir("/proc/self/fd"))
            report = verify_capture_routing(root / "network", **arguments)
            self.assertEqual(report["status"], "verified-observation")
            self.assertEqual(report["peer_pid"], arguments["expected_peer_pid"])
            self.assertEqual(report["ready_sha256"], arguments["expected_ready_sha256"])
            self.assertFalse(report["study_eligible"])
            self.assertFalse(report["native_containment_verified"])
            self.assertEqual(files, {p: sha(p) for p in files})
            self.assertEqual(descriptors, set(os.listdir("/proc/self/fd")))

    def test_rehashed_configuration_and_observation_contradictions_are_refused(self):
        from caplab.capture_network_verify import verify_capture_routing

        cases = [
            ("command.json", "command", ["/bin/true"]),
            ("command.json", "environment", {"PATH": "/tmp"}),
            ("command.json", "borrowed_descriptors", [3, 3, 4, 5]),
            ("command.json", "helper_source_sha256", "0" * 64),
            ("command.json", "python_sha256", "0" * 64),
            ("command.json", "slirp_sha256", "bad"),
            ("command.json", "max_stream_bytes", 1),
            ("command.json", "surprise", True),
            ("policy/initial-command.json", "command", ["/bin/true"]),
            ("policy/install-command.json", "environment", {}),
            ("policy/readback-command.json", "borrowed_descriptors", [3, True, 5]),
            ("policy/preflight.json", "peer_pid", None),
            ("policy/installation.json", "peer_pid", 2147483647),
            ("ready.json", "ready_signal_observed", 1),
            ("ready.json", "ready_observed_monotonic_ns", 0),
            ("ready.json", "study_eligible", True),
            ("terminal.json", "body_completed", False),
            ("process/capture.json", "return_code", 1),
            ("process/capture.json", "started_monotonic_ns", 0),
            ("process/capture.json", "surprise", True),
            ("process/capture.json", "finished_at", "yesterday"),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            process = run_outer(root)
            self.assertEqual(
                process["return_code"], 0, (root / "outer/native.stderr").read_text()
            )
            original = {
                p: p.read_bytes() for p in (root / "network").rglob("*") if p.is_file()
            }
            descriptors = set(os.listdir("/proc/self/fd"))
            for name, key, value in cases:
                with self.subTest(name=name, key=key):
                    for path, raw in original.items():
                        path.write_bytes(raw)
                    path = root / "network" / name
                    document = json.loads(path.read_bytes())
                    document[key] = value
                    write(path, document)
                    reseal(root)
                    with self.assertRaises(ValueError):
                        verify_capture_routing(root / "network", **inputs(root))
                    self.assertEqual(descriptors, set(os.listdir("/proc/self/fd")))

    def test_rehashed_rules_and_capability_streams_cannot_claim_success(self):
        from caplab.capture_network_verify import verify_capture_routing

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(run_outer(root)["return_code"], 0)
            original = {
                p: p.read_bytes() for p in (root / "network").rglob("*") if p.is_file()
            }
            for directory, stream, raw in [
                ("policy/readback", "stdout", b'{"nftables": []}\n'),
                (
                    "policy/initial",
                    "stdout",
                    original[root / "network/policy/readback/native.stdout"],
                ),
                ("policy/install", "stderr", b'{"helper_capabilities": {}}\n'),
                ("process", "stderr", b'{"helper_capabilities": {}}\n'),
            ]:
                with self.subTest(directory=directory, stream=stream):
                    for path, content in original.items():
                        path.write_bytes(content)
                    reseal_stream(root, directory, stream, raw)
                    with self.assertRaises(ValueError):
                        verify_capture_routing(root / "network", **inputs(root))

    def test_independent_anchors_and_safe_file_reads_refuse_changed_custody(self):
        from caplab.capture_network_verify import verify_capture_routing

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(run_outer(root)["return_code"], 0)
            arguments = inputs(root)
            descriptors = set(os.listdir("/proc/self/fd"))
            for key in (
                "expected_policy_sha256",
                "expected_terminal_sha256",
                "expected_ready_sha256",
            ):
                with self.subTest(anchor=key), self.assertRaises(ValueError):
                    verify_capture_routing(
                        root / "network", **{**arguments, key: "0" * 64}
                    )
            for name in (
                "terminal.json",
                "policy/preflight.json",
                "process/native.stdout",
            ):
                path = root / "network" / name
                raw = path.read_bytes()
                for kind in ("symlink", "fifo", "missing", "oversized", "changed"):
                    with self.subTest(name=name, kind=kind):
                        path.unlink()
                        if kind == "symlink":
                            path.symlink_to(root / "result.json")
                        elif kind == "fifo":
                            os.mkfifo(path)
                        elif kind == "oversized":
                            with path.open("wb") as f:
                                f.truncate(1024 * 1024 + 1)
                        elif kind == "changed":
                            path.write_bytes(b"{}\n")
                        with self.assertRaises((ValueError, OSError)):
                            verify_capture_routing(root / "network", **arguments)
                        if path.exists() or path.is_symlink():
                            path.unlink()
                        path.write_bytes(raw)
                        self.assertEqual(descriptors, set(os.listdir("/proc/self/fd")))
            self.assertEqual(
                verify_capture_routing(root / "network", **arguments)["status"],
                "verified-observation",
            )

    def test_failed_routing_lifecycles_are_not_completed_observations(self):
        from caplab.capture_network_verify import verify_capture_routing

        for mode in ("body-error", "timeout"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                self.assertEqual(run_outer(root, mode)["return_code"], 0)
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
                    )

    def test_cli_inspects_anchored_custody_and_rejects_wrong_peer(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(run_outer(root)["return_code"], 0)
            arguments = inputs(root)
            plan_path = root / "plan.json"
            write(plan_path, arguments.pop("plan"))
            command = [
                sys.executable,
                "scripts/inspect_capture_routing.py",
                str(root / "network"),
                "--policy",
                str(plan_path),
            ]
            for key, value in arguments.items():
                command.extend(["--" + key.replace("_", "-"), str(value)])
            result = subprocess.run(command, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertEqual(
                json.loads(result.stdout)["status"], "verified-observation"
            )
            command[-1] = "2147483647"
            result = subprocess.run(command, capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
            self.assertIn(b"authenticated handoff", result.stderr)
