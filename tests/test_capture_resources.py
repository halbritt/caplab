"""Resource observations retain real cgroup peaks and reject contradictory counters."""

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

REPO = Path(__file__).resolve().parents[1]


def sample(usage=20, peak=4096, started=100):
    return {
        "schema": "caplab.cgroup-resource-observation/v1",
        "cgroup": {
            "path": "/sys/fs/cgroup/caplab-synthetic",
            "device": 29,
            "inode": 123,
        },
        "kernel_release": "synthetic-kernel",
        "started_monotonic_ns": started,
        "finished_monotonic_ns": started + 10,
        "raw": {
            "cgroup.type": "domain\n",
            "cpu.stat": f"usage_usec {usage}\nuser_usec {usage - 5}\nsystem_usec 5\ncore_sched.force_idle_usec 0\n",
            "memory.current": "0\n",
            "memory.peak": f"{peak}\n",
            "cgroup.events": "populated 0\nfrozen 0\n",
        },
        "values": {
            "cpu_usage_usec": usage,
            "cpu_user_usec": usage - 5,
            "cpu_system_usec": 5,
            "memory_current_bytes": 0,
            "memory_peak_bytes": peak,
            "populated": 0,
            "frozen": 0,
        },
        "study_eligible": False,
    }


def worker(root, exit_code=0):
    from caplab.capture_resources import (
        read_cgroup_resources,
        verify_cgroup_resource_interval,
    )

    membership = Path("/proc/self/cgroup").read_text().strip()
    assert membership.startswith("0::/")
    supervisor = Path("/sys/fs/cgroup") / membership[4:]
    assert supervisor.name == "supervisor"
    owner = supervisor.parent
    (owner / "cgroup.subtree_control").write_text("+memory +pids")
    child = owner / "resource-child"
    child.mkdir()
    try:
        (child / "memory.max").write_text(str(64 * 1024**2))
        (child / "memory.swap.max").write_text("0")
        (child / "pids.max").write_text("8")
        descriptors = set(os.listdir("/proc/self/fd"))
        before = read_cgroup_resources(child)
        join = "import os,sys;from pathlib import Path;Path(sys.argv[1],'cgroup.procs').write_text(str(os.getpid()));os.execv(sys.argv[2],sys.argv[2:])"
        body = "import time;x=bytearray(24*1024**2);x[::4096]=b'x'*(len(x)//4096);end=time.process_time()+.08\nwhile time.process_time()<end:sum(range(1000))"
        body += f"\nimport sys;sys.exit({exit_code})"
        process = subprocess.run(
            [
                "/usr/bin/python3",
                "-B",
                "-c",
                join,
                str(child),
                "/usr/bin/python3",
                "-B",
                "-c",
                body,
            ],
            check=False,
            timeout=5,
            env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
        )
        assert process.returncode == exit_code
        after = read_cgroup_resources(child)
        report = verify_cgroup_resource_interval(
            before, after, expected_cgroup=before["cgroup"]
        )
        assert report["cpu_delta_usec"]["usage"] > 0
        assert report["accounted_memory_peak_bytes"] >= 24 * 1024**2
        assert after["values"]["populated"] == 0
        assert set(os.listdir("/proc/self/fd")) == descriptors
        (root / "result.json").write_text(
            json.dumps(
                {
                    "before": before,
                    "after": after,
                    "report": report,
                    "owner": str(owner),
                    "child_return_code": process.returncode,
                },
                indent=2,
            )
            + "\n"
        )
    finally:
        (child / "cgroup.kill").write_text("1")
        deadline = time.monotonic() + 2
        while "populated 1" in (child / "cgroup.events").read_text():
            if time.monotonic() > deadline:
                raise RuntimeError("owned resource group remains populated")
            time.sleep(0.01)
        child.rmdir()


class CaptureResourceTests(unittest.TestCase):
    def test_interval_uses_cumulative_cpu_and_lifetime_peak_without_inventing_overhead(
        self,
    ):
        from caplab.capture_resources import verify_cgroup_resource_interval

        before, after = sample(), sample(usage=40, peak=8192, started=200)
        original = deepcopy((before, after))
        report = verify_cgroup_resource_interval(
            before, after, expected_cgroup=before["cgroup"]
        )
        self.assertEqual(
            report["cpu_delta_usec"], {"usage": 20, "user": 20, "system": 0}
        )
        self.assertEqual(report["accounted_memory_peak_bytes"], 8192)
        self.assertEqual(
            report["observation_interval_ns"], {"minimum": 90, "maximum": 110}
        )
        self.assertIsNone(report["incremental_capture_overhead_seconds"])
        self.assertFalse(report["kernel_origin_verified"])
        self.assertFalse(report["study_eligible"])
        self.assertEqual((before, after), original)
        report["cgroup"]["inode"] = 999
        self.assertEqual(before["cgroup"]["inode"], 123)

    def test_changed_identity_decreasing_counters_and_raw_parsed_disagreement_are_refused(
        self,
    ):
        from caplab.capture_resources import verify_cgroup_resource_interval

        before, after = sample(), sample(usage=40, peak=8192, started=200)
        cases = [
            (
                "cgroup",
                {"path": "/sys/fs/cgroup/caplab-synthetic", "device": 29, "inode": 999},
            ),
            ("kernel_release", "other"),
            ("started_monotonic_ns", 105),
            ("finished_monotonic_ns", True),
            ("values", {**after["values"], "cpu_usage_usec": True}),
            ("study_eligible", True),
            ("extra", 0),
        ]
        for key, value in cases:
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_cgroup_resource_interval(
                    before, after | {key: value}, expected_cgroup=before["cgroup"]
                )
        for raw in (
            "usage_usec 40\nusage_usec 40\nuser_usec 35\nsystem_usec 5\n",
            "usage_usec -1\nuser_usec 35\nsystem_usec 5\n",
            "usage_usec 40\n",
            "usage_usec 18446744073709551616\nuser_usec 35\nsystem_usec 5\n",
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                verify_cgroup_resource_interval(
                    before,
                    after | {"raw": after["raw"] | {"cpu.stat": raw}},
                    expected_cgroup=before["cgroup"],
                )
        for candidate in (
            sample(usage=10, peak=8192, started=200),
            sample(usage=40, peak=1024, started=200),
        ):
            with self.assertRaises(ValueError):
                verify_cgroup_resource_interval(
                    before, candidate, expected_cgroup=before["cgroup"]
                )

    def test_real_cgroup_usage_survives_child_exit_and_owned_group_removal(self):
        self.run_cgroup(0)

    def test_failed_child_retains_nonzero_resource_observations(self):
        self.run_cgroup(7)

    def run_cgroup(self, exit_code):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            unit = "caplab-resource-test-" + uuid.uuid4().hex + ".service"
            env = {
                "PATH": "/usr/bin:/bin",
                "LANG": "C.UTF-8",
                "XDG_RUNTIME_DIR": f"/run/user/{os.getuid()}",
                "DBUS_SESSION_BUS_ADDRESS": f"unix:path=/run/user/{os.getuid()}/bus",
            }
            command = [
                "/usr/bin/systemd-run",
                "--user",
                "--unit=" + unit,
                "--wait",
                "--pipe",
                "--collect",
                "--service-type=exec",
                "--property=Delegate=memory pids",
                "--property=DelegateSubgroup=supervisor",
                "--property=RuntimeMaxSec=30",
                "--property=MemoryMax=128M",
                "--property=MemorySwapMax=0",
                "--property=TasksMax=32",
                "--setenv=PYTHONPATH=" + str(REPO / "src"),
                "/usr/bin/python3",
                "-B",
                str(Path(__file__).resolve()),
                "worker",
                str(root),
                str(exit_code),
            ]
            try:
                result = subprocess.run(
                    command, env=env, capture_output=True, timeout=35
                )
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                observed = json.loads((root / "result.json").read_bytes())
                self.assertEqual(observed["child_return_code"], exit_code)
                self.assertGreater(observed["report"]["cpu_delta_usec"]["usage"], 0)
                self.assertGreaterEqual(
                    observed["report"]["accounted_memory_peak_bytes"], 24 * 1024**2
                )
            finally:
                subprocess.run(
                    ["/usr/bin/systemctl", "--user", "stop", unit],
                    env=env,
                    capture_output=True,
                    timeout=5,
                )
                state = subprocess.run(
                    [
                        "/usr/bin/systemctl",
                        "--user",
                        "show",
                        unit,
                        "--property=LoadState",
                        "--value",
                    ],
                    env=env,
                    capture_output=True,
                    check=True,
                    timeout=5,
                )
                self.assertEqual(state.stdout.strip(), b"not-found")
            self.assertFalse(Path(observed["owner"]).exists())

    def test_native_resource_inspection_requires_file_anchors_identity_and_enclosing_interval(
        self,
    ):
        import hashlib

        sys.path.insert(0, str(REPO / "scripts"))
        from scripted_native.inspection import inspect_resource_usage

        before, after = sample(), sample(usage=40, peak=8192, started=200)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            entries = []
            for phase, document in (("before", before), ("after", after)):
                name = "safe-resource-" + phase + ".json"
                raw = json.dumps(document).encode()
                (root / name).write_bytes(raw)
                entries.append(
                    {
                        "path": name,
                        "kind": "file",
                        "sha256": hashlib.sha256(raw).hexdigest(),
                    }
                )
            arguments = dict(
                capture_manifest={"entries": entries},
                expected_cgroup=before["cgroup"],
                process={"started_monotonic_ns": 120, "finished_monotonic_ns": 190},
            )
            report = inspect_resource_usage(root, **arguments)
            self.assertEqual(report["cpu_delta_usec"]["usage"], 20)
            self.assertTrue(report["captured_process_interval_enclosed"])
            for process in (
                {"started_monotonic_ns": 90, "finished_monotonic_ns": 190},
                {"started_monotonic_ns": 120, "finished_monotonic_ns": 210},
            ):
                with self.assertRaises(ValueError):
                    inspect_resource_usage(root, **(arguments | {"process": process}))
            with self.assertRaises(ValueError):
                inspect_resource_usage(
                    root,
                    **(
                        arguments
                        | {"expected_cgroup": before["cgroup"] | {"inode": 999}}
                    ),
                )
            (root / "safe-resource-after.json").write_text(
                json.dumps(sample(usage=80, peak=8192, started=200))
            )
            with self.assertRaises(ValueError):
                inspect_resource_usage(root, **arguments)
            entries[1]["sha256"] = hashlib.sha256(
                (root / "safe-resource-after.json").read_bytes()
            ).hexdigest()
            self.assertEqual(
                inspect_resource_usage(root, **arguments)["cpu_delta_usec"]["usage"], 60
            )
            duplicate = json.dumps(after).replace(
                '"study_eligible": false',
                '"study_eligible": true, "study_eligible": false',
            )
            (root / "safe-resource-after.json").write_text(duplicate)
            entries[1]["sha256"] = hashlib.sha256(duplicate.encode()).hexdigest()
            with self.assertRaises(ValueError):
                inspect_resource_usage(root, **arguments)
            entries.pop()
            with self.assertRaises(ValueError):
                inspect_resource_usage(root, **arguments)

    def test_non_cgroup_paths_are_refused_without_open_descriptors(self):
        from caplab.capture_resources import read_cgroup_resources

        descriptors = set(os.listdir("/proc/self/fd"))
        for path in (Path("/tmp"), Path("/sys/fs/cgroup"), Path("relative")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                read_cgroup_resources(path)
        self.assertEqual(set(os.listdir("/proc/self/fd")), descriptors)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "worker":
    worker(Path(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 0)
