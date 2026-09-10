"""Borrow helper namespaces only after checking their kernel ownership relationship."""

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
import fcntl
import os
from pathlib import Path

from caplab.task_capture_verify import _open, _require

_NS_GET_USERNS = 0xB701
_NS_GET_PARENT = 0xB702
_CAPABILITIES = ("CapEff", "CapPrm", "CapInh", "CapBnd", "CapAmb")
_PROFILES = ("workload-user/v1", "parent-user/v1")


@dataclass(frozen=True)
class CaptureNetworkNamespaces:
    """Descriptors are borrowed until context exit; observation is an owned snapshot."""

    user_fd: int
    network_fd: int
    observation: dict


def _identity(fd):
    stat = os.fstat(fd)
    return {"device": stat.st_dev, "inode": stat.st_ino}


def _text(proc, name, maximum):
    with _open(proc, name) as fd:
        raw = os.read(fd, maximum + 1)
    _require(len(raw) <= maximum, "network identity metadata exceeds allowance")
    return raw.decode("ascii")


def _mapping(raw):
    rows = []
    for line in raw.splitlines():
        fields = line.split()
        _require(
            len(fields) == 3 and all(f.isascii() and f.isdecimal() for f in fields),
            "invalid namespace ID mapping",
        )
        row = list(map(int, fields))
        _require(
            all(0 <= value < 2**32 for value in row) and row[2] > 0,
            "invalid namespace ID mapping range",
        )
        rows.append(row)
    _require(bool(rows), "namespace ID mapping is empty")
    return rows


@contextmanager
def open_capture_network_namespaces(peer_pid: int, *, profile: str):
    """Open a blocked authenticated peer's network and its owning user namespace.

    Caller owns peer authentication, namespace authority and the blocked lifetime.
    This reader neither enters namespaces nor authorizes helper execution. The
    parent profile admits only an immediate parent owner and internal UID/GID
    1000 mapped singly to this observer's UID/GID. Proc mapping coordinates are
    those of this observer, not necessarily the peer's immediate parent.
    Every returned descriptor closes on context exit, including exceptions.
    """
    _require(type(peer_pid) is int and peer_pid > 0, "invalid network peer PID")
    _require(
        type(profile) is str and profile in _PROFILES,
        "unsupported network namespace ownership profile",
    )
    with ExitStack() as stack:
        proc = stack.enter_context(
            _open(None, Path(f"/proc/{peer_pid}"), directory=True)
        )

        def namespace(name):
            fd = os.open("ns/" + name, os.O_RDONLY | os.O_CLOEXEC, dir_fd=proc)
            stack.callback(os.close, fd)
            return fd

        def related(fd, command):
            result = fcntl.ioctl(fd, command)
            stack.callback(os.close, result)
            os.set_inheritable(result, False)
            return result

        workload_user = namespace("user")
        network = namespace("net")
        owner = related(network, _NS_GET_USERNS)
        workload_identity, network_identity, owner_identity = map(
            _identity, (workload_user, network, owner)
        )
        supervisor = {}
        for kind in ("user", "net"):
            own = os.stat("/proc/self/ns/" + kind)
            supervisor[kind] = {"device": own.st_dev, "inode": own.st_ino}
        _require(
            network_identity != supervisor["net"]
            and owner_identity != supervisor["user"]
            and workload_identity != supervisor["user"],
            "network identity overlaps supervisor namespaces",
        )
        parent_identity = None
        if profile == "workload-user/v1":
            _require(
                owner_identity == workload_identity,
                "network owner differs from workload user namespace",
            )
        else:
            _require(
                owner_identity != workload_identity,
                "parent profile requires a distinct workload user namespace",
            )
            parent_identity = _identity(related(workload_user, _NS_GET_PARENT))
            _require(
                parent_identity == owner_identity,
                "network owner is not the workload immediate parent",
            )
        status = dict(
            line.split(":", 1)
            for line in _text(proc, "status", 16384).splitlines()
            if ":" in line
        )
        capabilities = {
            key: status.get(key, "").strip() for key in (*_CAPABILITIES, "NoNewPrivs")
        }
        _require(
            capabilities
            == {
                **{key: "0000000000000000" for key in _CAPABILITIES},
                "NoNewPrivs": "1",
            },
            "network peer retains privileges",
        )
        uid_map, gid_map = (
            _mapping(_text(proc, name, 4096)) for name in ("uid_map", "gid_map")
        )
        observer = {"uid": os.getuid(), "gid": os.getgid()}
        if profile == "parent-user/v1":
            _require(
                uid_map == [[1000, observer["uid"], 1]]
                and gid_map == [[1000, observer["gid"], 1]],
                "parent profile requires the selected non-root mapping",
            )
            _require(
                status.get("Uid", "").split() == [str(observer["uid"])] * 4
                and status.get("Gid", "").split() == [str(observer["gid"])] * 4,
                "workload credentials differ from selected mapping",
            )
        observation = {
            "schema": "caplab.capture-network-identity/v1",
            "profile": profile,
            "peer_pid": peer_pid,
            "supervisor_namespaces": supervisor,
            "workload_user_namespace": workload_identity,
            "workload_user_parent_namespace": parent_identity,
            "network_namespace": network_identity,
            "network_owner_user_namespace": owner_identity,
            "mapping_observer": observer,
            "uid_map": uid_map,
            "gid_map": gid_map,
            "capabilities": capabilities,
            "study_eligible": False,
        }
        yield CaptureNetworkNamespaces(owner, network, observation)
