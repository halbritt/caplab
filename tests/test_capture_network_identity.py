"""Kernel ownership checks for a zero-capability workload beneath its network owner."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import struct
import tempfile
import unittest

from caplab.capture_network_identity import open_capture_network_namespaces
from caplab.process_capture import capture_process

SETUP = r"""
import ctypes,errno,json,os,socket,subprocess,sys
from pathlib import Path
mode=sys.argv[1]
if mode in ('parent','wrong-map','grandparent'):
    os.unshare(os.CLONE_NEWUSER)
    Path('/proc/self/setgroups').write_text('deny\n')
    child=1001 if mode=='wrong-map' else 1000
    Path('/proc/self/uid_map').write_text(f'{child} 0 1\n')
    Path('/proc/self/gid_map').write_text(f'{child} 0 1\n')
    if mode=='grandparent':
        os.unshare(os.CLONE_NEWUSER)
        Path('/proc/self/setgroups').write_text('deny\n')
        Path('/proc/self/uid_map').write_text('1000 1000 1\n')
        Path('/proc/self/gid_map').write_text('1000 1000 1\n')
libc=ctypes.CDLL(None,use_errno=True)
def prctl(*args):
    if libc.prctl(*args)!=0:raise OSError(ctypes.get_errno(),'prctl')
prctl(38,1,0,0,0)
if mode!='privileged':
    prctl(47,4,0,0,0)
    for cap in range(64):
        if libc.prctl(24,cap,0,0,0)!=0:
            if ctypes.get_errno()==errno.EINVAL:break
            raise OSError(ctypes.get_errno(),'drop bounding capability')
    else:raise RuntimeError('unsupported capability range')
    class Header(ctypes.Structure):_fields_=[('version',ctypes.c_uint32),('pid',ctypes.c_int)]
    class Caps(ctypes.Structure):_fields_=[('effective',ctypes.c_uint32),('permitted',ctypes.c_uint32),('inheritable',ctypes.c_uint32)]
    header=Header(0x20080522,0);caps=(Caps*2)()
    if libc.capset(ctypes.byref(header),ctypes.byref(caps))!=0:raise OSError(ctypes.get_errno(),'capset')
report={'uid':os.getuid(),'gid':os.getgid()}
if mode=='parent':
    command=['/usr/bin/bwrap','--unshare-user','--uid','0','--gid','0',
        '--cap-add','CAP_NET_ADMIN','--ro-bind','/','/','--proc','/proc','--']
    nested=subprocess.run(command+['/usr/bin/true'],capture_output=True,timeout=3)
    assert nested.returncode==0,nested.stderr
    denial="from pathlib import Path;import os;f=dict(x.split(':',1) for x in Path('/proc/self/status').read_text().splitlines() if ':' in x);assert int(f['CapEff'],16)&(1<<12);os.execv('/usr/sbin/nft',['nft','add','table','inet','forbidden'])"
    denied=subprocess.run(command+['/usr/bin/python3','-B','-c',denial],capture_output=True,timeout=3)
    assert denied.returncode!=0 and b'Operation not permitted' in denied.stderr,denied
    report['nested_sandbox']=True;report['ancestor_network_mutation_refused']=True
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
    connection.settimeout(5);connection.connect('/control.sock')
    connection.sendall(json.dumps(report).encode());assert connection.recv(1)==b'1'
"""


@contextmanager
def peer(mode):
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
            path = root / "control.sock"
            listener.bind(str(path))
            listener.listen(1)
            listener.settimeout(8)
            command = [
                "/usr/bin/bwrap",
                "--unshare-all",
                "--uid",
                "0",
                "--gid",
                "0",
                "--die-with-parent",
                "--new-session",
                "--clearenv",
                "--cap-add",
                "CAP_SETPCAP",
                "--cap-add",
                "CAP_SETFCAP",
                "--ro-bind",
                "/usr",
                "/usr",
                "--symlink",
                "usr/bin",
                "/bin",
                "--symlink",
                "usr/lib",
                "/lib",
                "--symlink",
                "usr/lib64",
                "/lib64",
                "--proc",
                "/proc",
                "--tmpfs",
                "/tmp",
                "--dir",
                "/dev",
                "--dev-bind",
                "/dev/null",
                "/dev/null",
                "--ro-bind",
                str(path),
                "/control.sock",
                "--",
                "/usr/bin/python3",
                "-B",
                "-c",
                SETUP,
                mode,
            ]
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(
                    capture_process,
                    command,
                    cwd=root,
                    environment={"PATH": "/usr/bin:/usr/sbin:/bin", "LANG": "C.UTF-8"},
                    output_dir=root / "process",
                    max_stream_bytes=65536,
                    timeout_seconds=12,
                )
                try:
                    connection, _ = listener.accept()
                except TimeoutError:
                    result = future.result(timeout=15)
                    raise AssertionError(
                        (result, (root / "process/native.stderr").read_text())
                    )
                with connection:
                    connection.settimeout(5)
                    pid, _, _ = struct.unpack(
                        "3i",
                        connection.getsockopt(
                            socket.SOL_SOCKET, socket.SO_PEERCRED, 12
                        ),
                    )
                    report = json.loads(connection.recv(4096))
                    try:
                        yield pid, report
                    finally:
                        connection.sendall(b"1")
                result = future.result(timeout=15)
                assert result["return_code"] == 0 and result["streams_complete"], result


def fd_population():
    return set(os.listdir("/proc/self/fd"))


class CaptureNetworkIdentityTests(unittest.TestCase):
    def test_parent_owner_supports_nested_sandbox_without_network_authority(self):
        with peer("parent") as (pid, report):
            before = fd_population()
            with open_capture_network_namespaces(
                pid, profile="parent-user/v1"
            ) as lease:
                observation = lease.observation
                self.assertTrue(report["nested_sandbox"])
                self.assertTrue(report["ancestor_network_mutation_refused"])
                self.assertEqual(
                    observation["workload_user_parent_namespace"],
                    observation["network_owner_user_namespace"],
                )
                self.assertNotEqual(
                    observation["workload_user_namespace"],
                    observation["network_owner_user_namespace"],
                )
                self.assertEqual(observation["uid_map"], [[1000, os.getuid(), 1]])
                self.assertEqual(observation["gid_map"], [[1000, os.getgid(), 1]])
                self.assertFalse(observation["study_eligible"])
                for fd, key in (
                    (lease.user_fd, "network_owner_user_namespace"),
                    (lease.network_fd, "network_namespace"),
                ):
                    stat = os.fstat(fd)
                    self.assertEqual(
                        {"device": stat.st_dev, "inode": stat.st_ino}, observation[key]
                    )
                    self.assertFalse(os.get_inheritable(fd))
            self.assertEqual(fd_population(), before)
            for fd in (lease.user_fd, lease.network_fd):
                with self.assertRaises(OSError):
                    os.fstat(fd)

    def test_same_user_profile_keeps_legacy_namespace_relationship(self):
        with peer("same") as (pid, _):
            with open_capture_network_namespaces(
                pid, profile="workload-user/v1"
            ) as lease:
                self.assertEqual(
                    lease.observation["workload_user_namespace"],
                    lease.observation["network_owner_user_namespace"],
                )
            with self.assertRaises(ValueError):
                with open_capture_network_namespaces(pid, profile="parent-user/v1"):
                    self.fail("same-user owner accepted as parent")

    def test_wrong_relationship_mapping_and_privileged_peer_are_refused_without_leaks(
        self,
    ):
        for mode, profile in [
            ("parent", "workload-user/v1"),
            ("wrong-map", "parent-user/v1"),
            ("grandparent", "parent-user/v1"),
            ("privileged", "workload-user/v1"),
        ]:
            with self.subTest(mode=mode), peer(mode) as (pid, _):
                before = fd_population()
                with self.assertRaises(ValueError):
                    with open_capture_network_namespaces(pid, profile=profile):
                        self.fail("unsafe identity accepted")
                self.assertEqual(fd_population(), before)

    def test_self_invalid_inputs_and_body_error_close_owned_descriptors(self):
        before = fd_population()
        for pid, profile in [
            (True, "workload-user/v1"),
            (0, "workload-user/v1"),
            (os.getpid(), "workload-user/v1"),
            (os.getpid(), "unknown"),
        ]:
            with self.subTest(pid=pid, profile=profile), self.assertRaises(ValueError):
                with open_capture_network_namespaces(pid, profile=profile):
                    self.fail("invalid peer accepted")
        self.assertEqual(fd_population(), before)
        with peer("same") as (pid, _):
            before = fd_population()
            with self.assertRaisesRegex(RuntimeError, "body failed"):
                with open_capture_network_namespaces(pid, profile="workload-user/v1"):
                    raise RuntimeError("body failed")
            self.assertEqual(fd_population(), before)
