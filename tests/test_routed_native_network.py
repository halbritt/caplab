"""The production outer namespace and fixture are reachable only through routing."""

from contextlib import ExitStack
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
package = os.environ.get("CAPLAB_TEST_WEBSOCKETS_ROOT")
if package:
    sys.path.insert(0, str(Path(package).parent))
try:
    import websockets
except ModuleNotFoundError as error:
    if error.name != "websockets":
        raise
    raise unittest.SkipTest("requires the pinned WebSocket test dependency")

from caplab.capture_network_policy import build_capture_network_policy
from caplab.capture_network_transport import capture_routed_network
from caplab.capture_network_verify import verify_capture_routing
from caplab.process_capture import capture_process
from scripted_native.routed_network import outer_command, configure_outer, namespace_ids
from scripted_native.routed_fixture import supervised_fixture
from test_capture_network_policy import network_handoff

PRODUCER = r"""
import array,json,os,socket
from http.client import HTTPConnection
from pathlib import Path
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
    s.settimeout(10);s.connect('/control.sock')
    fds=[os.open(p,os.O_RDONLY|os.O_DIRECTORY) for p in ('/scratch','/tmp','/dev/shm','/work','/episode')]
    try:s.sendmsg([b'R'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',fds))])
    finally:
        for fd in fds:os.close(fd)
    assert s.recv(1)==b'1'
assert Path('/work/task.txt').read_bytes()==b'prepared routed input\n'
http=HTTPConnection('198.18.0.1',FIXTURE_PORT,timeout=2)
try:
    http.request('GET','/__fixture_check');r=http.getresponse()
    assert r.status==200 and r.read()==b'{"fixture":true}'
finally:http.close()
print('routed-fixture-replied',flush=True)
"""


def outer(root, parent):
    import hashlib
    import errno
    from scripted_native.lifecycle import check_task_selection

    selection = json.loads((root / "task-selection.json").read_bytes())
    check_task_selection(selection, root.parent)
    try:
        fd = os.open(Path(selection["custody"]) / "input.json", os.O_WRONLY)
    except OSError as error:
        assert error.errno == errno.EROFS, error
    else:
        os.close(fd)
        raise AssertionError("prepared input is writable inside outer namespace")

    before = set(os.listdir("/proc/self/fd"))
    observation = configure_outer(root, parent)
    with supervised_fixture(
        expected_identity={
            "model": "gpt-5.6-terra",
            "effort": "max",
            "summary": "detailed",
        },
        capture_dir=root / "protocol",
        observation_socket=None,
        quarantine_factory=None,
    ) as fixed:
        plan = build_capture_network_policy(
            [{"address": "198.18.0.1", "port": fixed.port}]
        )
        with ExitStack() as stack:

            def install(
                plan,
                *,
                peer_pid,
                output_dir,
                expected_policy_sha256,
                quarantine_factory,
            ):
                return stack.enter_context(
                    capture_routed_network(
                        plan,
                        peer_pid=peer_pid,
                        expected_policy_sha256=expected_policy_sha256,
                        output_dir=output_dir,
                        timeout_seconds=8,
                        quarantine_factory=quarantine_factory,
                    )
                )

            handoff, process = network_handoff(
                root,
                installer=install,
                plan=plan,
                producer=PRODUCER.replace("FIXTURE_PORT", str(fixed.port)),
                task_input=selection,
                root_mapping=True,
                command_prefix=(
                    "/usr/bin/setpriv",
                    "--bounding-set=-all",
                    "--inh-caps=-all",
                    "--ambient-caps=-all",
                    "--no-new-privs",
                ),
            )
        assert process["return_code"] == 0, process
    network = root / "network"
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    verified = verify_capture_routing(
        network,
        plan=plan,
        expected_policy_sha256=plan["network_policy_sha256"],
        expected_terminal_sha256=sha(network / "terminal.json"),
        expected_ready_sha256=sha(network / "ready.json"),
        expected_peer_pid=handoff["peer_pid"],
    )
    assert (
        fixed.summary["requests"][0]["status"] == 200
        and fixed.summary["fixture_thread_joined"]
    )
    assert before == set(os.listdir("/proc/self/fd"))
    (root / "result.json").write_text(
        json.dumps(
            {
                "outer": observation,
                "routing": verified,
                "fixture": fixed.summary,
                "handoff": handoff,
            },
            indent=2,
        )
        + "\n"
    )


class RoutedNativeNetworkTests(unittest.TestCase):
    def test_joined_fixture_summary_requires_numeric_peer_and_completion_identity(self):
        from scripted_native.support import combine_routed_summary

        native = {
            "external_fixture": {"address": "198.18.0.1", "port": 39071},
            "requests": [],
            "errors": [],
            "websocket_messages": [],
            "library_events": [],
            "scripted_generated_responses": 0,
            "deferred_close": None,
            "fixture_stop_reason": None,
        }
        fixture = {
            "schema": "caplab.supervised-scripted-fixture/v1",
            "bind_address": "198.18.0.1",
            "port": 39071,
            "peer_pid": 1,
            "finished_monotonic_ns": 100,
            "fixture_thread_joined": True,
            "fixture_closed": True,
            "study_eligible": False,
            **{k: v for k, v in native.items() if k != "external_fixture"},
        }
        self.assertEqual(combine_routed_summary(native, fixture), native)
        for field, value in [
            ("peer_pid", True),
            ("peer_pid", 0),
            ("finished_monotonic_ns", True),
            ("finished_monotonic_ns", 0),
            ("port", True),
        ]:
            with (
                self.subTest(field=field, value=value),
                self.assertRaises(RuntimeError),
            ):
                combine_routed_summary(native, fixture | {field: value})

    def test_production_outer_and_supervised_fixture_support_restricted_handoff(self):
        with tempfile.TemporaryDirectory() as temporary:
            from caplab.task_input import prepare_task_input

            root = Path(temporary) / "capture/run"
            root.mkdir(mode=0o700, parents=True)
            source = Path(temporary) / "task-source"
            source.mkdir()
            (source / "task.txt").write_bytes(b"prepared routed input\n")
            bundle = Path(temporary) / "task-input"
            anchor = prepare_task_input(
                source, output_dir=bundle, max_task_bytes=1000, max_task_entries=10
            )
            (root / "task-selection.json").write_text(
                json.dumps(
                    {
                        "custody": str(bundle),
                        "input_sha256": anchor,
                        "max_receipt_bytes": 300000,
                    }
                )
            )
            (root / "outer-etc").mkdir()
            (root / "outer-etc/resolv.conf").write_text("nameserver 198.18.0.53\n")
            before = namespace_ids()
            command = outer_command(
                root,
                source=REPO / "tests/fixtures/codex-launcher-0.153.4",
                dependency=Path(websockets.__file__).parent,
                group=None,
                task_input=bundle,
                child_command=[
                    sys.executable,
                    "-B",
                    str(Path(__file__).resolve()),
                    "outer",
                    str(root),
                    json.dumps(before),
                ],
            )
            process = capture_process(
                command,
                cwd=root,
                environment={"PATH": "/usr/bin:/usr/sbin:/bin", "LANG": "C.UTF-8"},
                output_dir=root / "process",
                max_stream_bytes=128 * 1024,
                timeout_seconds=30,
            )
            self.assertEqual(
                process["return_code"], 0, (root / "process/native.stderr").read_text()
            )
            self.assertTrue(process["streams_complete"])
            self.assertEqual(namespace_ids(), before)
            result = json.loads((root / "result.json").read_bytes())
            self.assertEqual(result["routing"]["status"], "verified-observation")
            self.assertFalse(result["routing"]["native_containment_verified"])


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "outer":
    outer(Path(sys.argv[2]), json.loads(sys.argv[3]))
