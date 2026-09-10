"""Own restricted routing after policy installation and through helper shutdown."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack, contextmanager
import hashlib
import math
import os
from pathlib import Path
import select
import time

from caplab.capture_network_policy import _validated, install_capture_network_policy
from caplab.capture_quarantine import check_capture_bytes, check_capture_document
from caplab.process_capture import capture_process, seal_capture_json
from caplab.task_capture_verify import _open, _require


_ENTER = r"""
import ctypes,errno,json,os,sys
user=int(sys.argv[1])
os.setns(user,os.CLONE_NEWUSER)
actual=os.stat('/proc/self/ns/user');expected=os.fstat(user)
if (actual.st_dev,actual.st_ino)!=(expected.st_dev,expected.st_ino):
    raise RuntimeError('routing helper entered a different user namespace')
os.setresgid(0,0,0);os.setresuid(0,0,0)
libc=ctypes.CDLL(None,use_errno=True)
def prctl(*args):
    if libc.prctl(*args)!=0:raise OSError(ctypes.get_errno(),'prctl')
prctl(38,1,0,0,0);prctl(47,4,0,0,0)
for cap in range(64):
    if cap in (8,10,12,21):continue
    if libc.prctl(24,cap,0,0,0)!=0:
        error=ctypes.get_errno()
        if error==errno.EINVAL:break
        raise OSError(error,'drop routing helper bounding capability')
else:raise RuntimeError('unsupported capability range')
class Header(ctypes.Structure):
    _fields_=[('version',ctypes.c_uint32),('pid',ctypes.c_int)]
class Caps(ctypes.Structure):
    _fields_=[('effective',ctypes.c_uint32),('permitted',ctypes.c_uint32),('inheritable',ctypes.c_uint32)]
header=Header(0x20080522,0);caps=(Caps*2)()
caps[0]=Caps(0x201500,0x201500,0)
if libc.capset(ctypes.byref(header),ctypes.byref(caps))!=0:
    raise OSError(ctypes.get_errno(),'routing helper capset')
with open('/proc/self/status') as status:
    fields=dict(line.split(':',1) for line in status.read().splitlines() if ':' in line)
observed={k:fields[k].strip() for k in ('CapEff','CapPrm','CapInh','CapBnd','CapAmb','NoNewPrivs')}
expected={'CapEff':'0000000000201500','CapPrm':'0000000000201500','CapBnd':'0000000000201500','CapInh':'0000000000000000','CapAmb':'0000000000000000','NoNewPrivs':'1'}
if observed!=expected:raise RuntimeError('routing helper capabilities differ')
print(json.dumps({'helper_capabilities':observed}),file=sys.stderr,flush=True)
os.close(user)
os.execv('/usr/bin/slirp4netns',['/usr/bin/slirp4netns',*sys.argv[2:]])
"""


@contextmanager
def capture_routed_network(
    plan: dict,
    *,
    expected_policy_sha256: str,
    peer_pid: int,
    output_dir: Path,
    timeout_seconds: float,
    quarantine_factory=None,
):
    """Yield recorded readiness; require normal captured helper shutdown on exit.

    Caller owns endpoint authority, authentication, blocked peer lifetime,
    exclusive namespace use, stable private custody and the body deadline.
    Readiness is not continuous liveness or full native containment. Failure
    leaves policy and partial custody; the caller must destroy its workload.
    """
    rebuilt = _validated(plan, expected_policy_sha256)
    _require(type(peer_pid) is int and peer_pid > 0, "invalid network peer PID")
    _require(
        type(timeout_seconds) in (int, float)
        and math.isfinite(timeout_seconds)
        and 0 < timeout_seconds <= 300,
        "transport lifetime must be positive and at most 300 seconds",
    )
    _require(
        isinstance(output_dir, Path)
        and output_dir.is_absolute()
        and output_dir.resolve() == output_dir
        and output_dir != Path("/"),
        "transport custody must be a resolved absolute path",
    )
    check_capture_bytes(quarantine_factory, os.fsencode(output_dir))
    check_capture_document(quarantine_factory, rebuilt)
    with ExitStack() as stack:
        proc = stack.enter_context(
            _open(None, Path(f"/proc/{peer_pid}"), directory=True)
        )
        namespaces, identities = {}, {}
        for kind in ("user", "net"):
            fd = os.open("ns/" + kind, os.O_RDONLY | os.O_CLOEXEC, dir_fd=proc)
            stack.callback(os.close, fd)
            peer, own = os.fstat(fd), os.stat("/proc/self/ns/" + kind)
            _require(
                (peer.st_dev, peer.st_ino) != (own.st_dev, own.st_ino),
                "transport cannot modify a supervisor namespace",
            )
            namespaces[kind] = fd
            identities[kind] = {"device": peer.st_dev, "inode": peer.st_ino}
        binary = Path("/usr/bin/slirp4netns")
        binary_sha256 = hashlib.sha256(binary.read_bytes()).hexdigest()
        python_sha256 = hashlib.sha256(
            Path("/usr/bin/python3").read_bytes()
        ).hexdigest()
        output_dir.mkdir(mode=0o700)

        def seal(name, document):
            for path in (
                output_dir / name,
                output_dir / ("." + name.removesuffix(".json") + ".pending"),
            ):
                check_capture_bytes(quarantine_factory, os.fsencode(path))
            check_capture_document(quarantine_factory, document)
            return seal_capture_json(output_dir, name, document)

        policy = install_capture_network_policy(
            rebuilt,
            expected_policy_sha256=expected_policy_sha256,
            peer_pid=peer_pid,
            output_dir=output_dir / "policy",
            quarantine_factory=quarantine_factory,
        )
        _require(
            policy["namespaces"] == identities, "transport and policy namespaces differ"
        )
        ready_read, ready_write = os.pipe2(os.O_CLOEXEC)
        stack.callback(os.close, ready_read)
        stack.callback(os.close, ready_write)
        exit_read, exit_write = os.pipe2(os.O_CLOEXEC)
        stack.callback(os.close, exit_read)
        exit_writer = stack.enter_context(os.fdopen(exit_write, "wb"))
        command = [
            "/usr/bin/python3",
            "-I",
            "-S",
            "-c",
            _ENTER,
            str(namespaces["user"]),
            "--configure",
            "--enable-sandbox",
            "--enable-seccomp",
            "--disable-host-loopback",
            "--disable-dns",
            "--netns-type=path",
            f"--ready-fd={ready_write}",
            f"--exit-fd={exit_read}",
            f"/proc/self/fd/{namespaces['net']}",
            "tap0",
        ]
        environment = {"PATH": "/usr/bin:/usr/sbin:/bin", "LANG": "C.UTF-8"}
        descriptors = (*namespaces.values(), ready_write, exit_read)
        command_sha256 = seal(
            "command.json",
            {
                "command": command,
                "environment": environment,
                "borrowed_descriptors": list(descriptors),
                "slirp_sha256": binary_sha256,
                "namespaces": identities,
                "python_sha256": python_sha256,
                "helper_source_sha256": hashlib.sha256(
                    _ENTER.encode("utf-8")
                ).hexdigest(),
                "network_policy_sha256": expected_policy_sha256,
                "policy_installation_sha256": hashlib.sha256(
                    (output_dir / "policy/installation.json").read_bytes()
                ).hexdigest(),
                "timeout_seconds": timeout_seconds,
                "max_stream_bytes": 128 * 1024,
            },
        )
        pool = stack.enter_context(ThreadPoolExecutor(max_workers=1))
        future = pool.submit(
            capture_process,
            command,
            cwd=output_dir,
            environment=environment,
            output_dir=output_dir / "process",
            max_stream_bytes=128 * 1024,
            timeout_seconds=timeout_seconds,
            pass_fds=descriptors,
            quarantine_factory=quarantine_factory,
        )
        ready_sha256 = None
        body_completed = False
        try:
            deadline = time.monotonic() + min(5, timeout_seconds)
            while True:
                if future.done():
                    future.result()
                    raise RuntimeError("routing helper exited before readiness")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("routing helper readiness timed out")
                if select.select([ready_read], [], [], min(0.05, remaining))[0]:
                    _require(
                        os.read(ready_read, 1) == b"1",
                        "invalid routing readiness signal",
                    )
                    break
            _require(not future.done(), "routing helper ended at readiness")
            ready = {
                "schema": "caplab.capture-routing-readiness/v1",
                "command_sha256": command_sha256,
                "network_policy_sha256": expected_policy_sha256,
                "namespaces": identities,
                "ready_signal_observed": True,
                "ready_observed_monotonic_ns": time.monotonic_ns(),
                "study_eligible": False,
            }
            ready_sha256 = seal("ready.json", ready)
            yield ready
            body_completed = True
        finally:
            # slirp observes HUP on this pipe; writing a byte does not stop it.
            exit_writer.close()
            receipt = future.result(timeout=timeout_seconds + 5)
            normal = receipt["return_code"] == 0 and receipt["streams_complete"]
            tools_agree = (
                hashlib.sha256(binary.read_bytes()).hexdigest() == binary_sha256
            )
            tools_agree = (
                tools_agree
                and hashlib.sha256(Path("/usr/bin/python3").read_bytes()).hexdigest()
                == python_sha256
            )
            seal(
                "terminal.json",
                {
                    "schema": "caplab.capture-routing-terminal/v1",
                    "command_sha256": command_sha256,
                    "ready_sha256": ready_sha256,
                    "capture_sha256": hashlib.sha256(
                        (output_dir / "process/capture.json").read_bytes()
                    ).hexdigest(),
                    "normal_shutdown": normal,
                    "body_completed": body_completed,
                    "tools_agree": tools_agree,
                    "study_eligible": False,
                },
            )
            _require(normal, "routing helper did not stop normally")
            _require(tools_agree, "routing helper binary changed")
