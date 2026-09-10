"""Freeze exact destinations and install their policy in an authenticated peer."""

from contextlib import ExitStack
import hashlib
from ipaddress import IPv4Address
import json
import os
from pathlib import Path

from caplab.capture_quarantine import check_capture_bytes, check_capture_document
from caplab.codex_events import parse_native_json
from caplab.native_capture_invocation import _digest
from caplab.process_capture import capture_process, seal_capture_json
from caplab.task_capture_verify import _digest as _require_digest, _open, _require


_ENTER = r"""
import ctypes,errno,json,os,sys
user,net=map(int,sys.argv[1:3])
os.setns(user,os.CLONE_NEWUSER)
os.setns(net,os.CLONE_NEWNET)
for name,fd in (('user',user),('net',net)):
    actual=os.stat('/proc/self/ns/'+name);expected=os.fstat(fd)
    if (actual.st_dev,actual.st_ino)!=(expected.st_dev,expected.st_ino):
        raise RuntimeError('entered namespace differs')
libc=ctypes.CDLL(None,use_errno=True)
def prctl(*args):
    if libc.prctl(*args)!=0:raise OSError(ctypes.get_errno(),'prctl')
prctl(38,1,0,0,0)
prctl(47,4,0,0,0)
for capability in range(64):
    if capability==12:continue
    if libc.prctl(24,capability,0,0,0)!=0:
        error=ctypes.get_errno()
        if error==errno.EINVAL:break
        raise OSError(error,'drop capability bounding set')
else:raise RuntimeError('unsupported capability range')
class Header(ctypes.Structure):
    _fields_=[('version',ctypes.c_uint32),('pid',ctypes.c_int)]
class Caps(ctypes.Structure):
    _fields_=[('effective',ctypes.c_uint32),('permitted',ctypes.c_uint32),('inheritable',ctypes.c_uint32)]
header=Header(0x20080522,0);caps=(Caps*2)()
caps[0]=Caps(1<<12,1<<12,1<<12)
if libc.capset(ctypes.byref(header),ctypes.byref(caps))!=0:
    raise OSError(ctypes.get_errno(),'capset')
prctl(47,2,12,0,0)
with open('/proc/self/status') as status:
    fields=dict(line.split(':',1) for line in status.read().splitlines() if ':' in line)
observed={k:fields[k].strip() for k in ('CapEff','CapPrm','CapInh','CapBnd','CapAmb','NoNewPrivs')}
if observed!={**{k:'0000000000001000' for k in ('CapEff','CapPrm','CapInh','CapBnd','CapAmb')},'NoNewPrivs':'1'}:
    raise RuntimeError('helper capabilities differ')
print(json.dumps({'helper_capabilities':observed}),file=sys.stderr,flush=True)
os.close(user);os.close(net)
os.execv('/usr/sbin/nft',['/usr/sbin/nft',*sys.argv[3:]])
"""


def build_capture_network_policy(destinations: list[dict]) -> dict:
    _require(
        type(destinations) is list and 1 <= len(destinations) <= 64,
        "network policy needs 1 through 64 destinations",
    )
    seen = set()
    for item in destinations:
        _require(
            type(item) is dict and set(item) == {"address", "port"},
            "invalid destination fields",
        )
        address, port = item["address"], item["port"]
        _require(
            type(address) is str and len(address) <= 15, "invalid IPv4 destination"
        )
        parsed = IPv4Address(address)
        _require(
            str(parsed) == address
            and not parsed.is_multicast
            and not parsed.is_unspecified
            and int(parsed) != 0xFFFFFFFF,
            "destination must be an exact IPv4 unicast address",
        )
        _require(
            type(port) is int and 1 <= port <= 65535, "invalid TCP destination port"
        )
        _require((address, port) not in seen, "duplicate network destination")
        seen.add((address, port))
    plan = {
        "schema": "caplab.capture-network-policy/v1",
        "profile": "exact-ipv4-tcp/v1",
        "destinations": sorted(
            (dict(item) for item in destinations),
            key=lambda item: (item["address"], item["port"]),
        ),
        "execution_authorized": False,
        "study_eligible": False,
    }
    plan["network_policy_sha256"] = _digest(plan)
    return plan


def _validated(plan, expected):
    _require_digest(expected)
    _require(type(plan) is dict, "invalid network policy")
    rebuilt = build_capture_network_policy(plan.get("destinations"))
    _require(
        rebuilt["network_policy_sha256"] == expected
        and _digest(plan) == _digest(rebuilt),
        "network policy differs from its independent anchor or profile",
    )
    return rebuilt


def _rules(plan):
    table = {"family": "inet", "name": "caplab_capture"}
    scope = {"family": "inet", "table": table["name"]}
    chain = {
        **scope,
        "name": "output",
        "type": "filter",
        "hook": "output",
        "prio": 0,
        "policy": "drop",
    }
    entries = [{"table": table}, {"chain": chain}]
    for destination in plan["destinations"]:
        expressions = [
            {
                "match": {
                    "op": "==",
                    "left": {"payload": {"protocol": protocol, "field": field}},
                    "right": value,
                }
            }
            for protocol, field, value in (
                ("ip", "daddr", destination["address"]),
                ("tcp", "dport", destination["port"]),
            )
        ]
        entries.append(
            {
                "rule": {
                    **scope,
                    "chain": "output",
                    "expr": [*expressions, {"accept": None}],
                }
            }
        )
    entries.append(
        {
            "rule": {
                **scope,
                "chain": "output",
                "expr": [{"counter": {"packets": 0, "bytes": 0}}, {"drop": None}],
            }
        }
    )
    return entries


def _normalized_rules(document):
    _require(
        type(document) is dict and set(document) == {"nftables"}, "invalid nft ruleset"
    )
    entries = document["nftables"]
    _require(
        type(entries) is list and len(entries) <= 68, "unexpected nft ruleset size"
    )
    normalized = []
    for index, entry in enumerate(entries):
        _require(type(entry) is dict and len(entry) == 1, "invalid nft entry")
        kind, value = next(iter(entry.items()))
        if kind == "metainfo":
            _require(index == 0 and type(value) is dict, "invalid nft metadata")
            continue
        _require(
            kind in ("table", "chain", "rule") and type(value) is dict,
            "unexpected nft object",
        )
        value = json.loads(json.dumps(value))
        if "handle" in value:
            handle = value.pop("handle")
            _require(type(handle) is int and handle > 0, "invalid nft handle")
        if kind == "rule":
            expressions = value.get("expr")
            _require(type(expressions) is list, "invalid nft expressions")
            for expression in expressions:
                if type(expression) is dict and "counter" in expression:
                    counter = expression["counter"]
                    _require(
                        type(counter) is dict
                        and set(counter) == {"packets", "bytes"}
                        and all(type(n) is int and n >= 0 for n in counter.values()),
                        "invalid nft counter",
                    )
                    expression["counter"] = {"packets": 0, "bytes": 0}
        normalized.append({kind: value})
    return normalized


def verify_capture_network_rules(
    plan: dict, observed: dict, *, expected_policy_sha256: str
) -> None:
    """Compare a complete nft JSON readback; its trusted collection is caller-owned."""
    rebuilt = _validated(plan, expected_policy_sha256)
    _require(
        _digest(_normalized_rules(observed)) == _digest(_rules(rebuilt)),
        "installed nft rules differ from frozen network policy",
    )


def install_capture_network_policy(
    plan: dict,
    *,
    expected_policy_sha256: str,
    peer_pid: int,
    output_dir: Path,
    quarantine_factory=None,
) -> dict:
    """Install before release of an authenticated, zero-capability peer.

    The caller owns authentication, the blocked peer's lifetime, private stable
    custody ancestry and endpoint authorization. Failure may leave an installed
    policy and partial receipts; the caller must withhold release and destroy its
    namespace. This does not attach transport or prove full native containment.
    """
    rebuilt = _validated(plan, expected_policy_sha256)
    _require(type(peer_pid) is int and peer_pid > 0, "invalid network peer PID")
    _require(
        isinstance(output_dir, Path)
        and output_dir.is_absolute()
        and output_dir.resolve() == output_dir
        and output_dir != Path("/"),
        "network custody must be a resolved absolute path",
    )
    check_capture_document(quarantine_factory, rebuilt)
    check_capture_bytes(quarantine_factory, os.fsencode(output_dir))
    with ExitStack() as stack:
        proc = stack.enter_context(
            _open(None, Path(f"/proc/{peer_pid}"), directory=True)
        )
        namespace_fds, identities = {}, {}
        for kind in ("user", "net"):
            fd = os.open("ns/" + kind, os.O_RDONLY | os.O_CLOEXEC, dir_fd=proc)
            stack.callback(os.close, fd)
            own = os.stat("/proc/self/ns/" + kind)
            peer = os.fstat(fd)
            _require(
                (own.st_dev, own.st_ino) != (peer.st_dev, peer.st_ino),
                "network policy cannot modify a supervisor namespace",
            )
            namespace_fds[kind] = fd
            identities[kind] = {"device": peer.st_dev, "inode": peer.st_ino}
        status_fd = stack.enter_context(_open(proc, "status"))
        raw = os.read(status_fd, 16385)
        _require(len(raw) <= 16384, "peer status exceeds allowance")
        fields = dict(
            line.split(":", 1)
            for line in raw.decode("ascii").splitlines()
            if ":" in line
        )
        keys = ("CapEff", "CapPrm", "CapInh", "CapBnd", "CapAmb")
        capabilities = {
            key: fields.get(key, "").strip() for key in (*keys, "NoNewPrivs")
        }
        _require(
            all(capabilities[k] == "0000000000000000" for k in keys)
            and capabilities["NoNewPrivs"] == "1",
            "network peer retains privileges",
        )
        tools = {
            name: hashlib.sha256(Path(name).read_bytes()).hexdigest()
            for name in ("/usr/bin/python3", "/usr/sbin/nft")
        }
        preflight = {
            "schema": "caplab.capture-network-preflight/v1",
            "peer_pid": peer_pid,
            "namespaces": identities,
            "capabilities": capabilities,
            "network_policy_sha256": expected_policy_sha256,
            "tool_sha256": tools,
            "helper_source_sha256": hashlib.sha256(_ENTER.encode("utf-8")).hexdigest(),
        }
        check_capture_document(quarantine_factory, preflight)
        output_dir.mkdir(mode=0o700)

        def seal(name, document):
            for path in (
                output_dir / name,
                output_dir / ("." + name.removesuffix(".json") + ".pending"),
            ):
                check_capture_bytes(quarantine_factory, os.fsencode(path))
            check_capture_document(quarantine_factory, document)
            return seal_capture_json(output_dir, name, document)

        seal("preflight.json", preflight)
        seal("policy.json", {"nftables": [{"add": entry} for entry in _rules(rebuilt)]})
        policy_fd = stack.enter_context(_open(None, output_dir / "policy.json"))
        prefix = [
            "/usr/bin/python3",
            "-I",
            "-S",
            "-c",
            _ENTER,
            str(namespace_fds["user"]),
            str(namespace_fds["net"]),
        ]
        captured = {}
        commands = {}

        def run(name, args):
            command = prefix + args
            environment = {"PATH": "/usr/bin:/usr/sbin:/bin", "LANG": "C.UTF-8"}
            commands[name] = seal(
                name + "-command.json",
                {
                    "command": command,
                    "environment": environment,
                    "borrowed_descriptors": [*namespace_fds.values(), policy_fd],
                },
            )
            receipt = capture_process(
                command,
                cwd=output_dir,
                environment=environment,
                output_dir=output_dir / name,
                max_stream_bytes=128 * 1024,
                timeout_seconds=5,
                pass_fds=(*namespace_fds.values(), policy_fd),
                quarantine_factory=quarantine_factory,
            )
            _require(
                receipt["return_code"] == 0 and receipt["streams_complete"],
                "network policy command failed: " + name,
            )
            helper = parse_native_json(
                (output_dir / name / "native.stderr").read_text()
            )
            _require(
                helper
                == {
                    "helper_capabilities": {
                        **{
                            k: "0000000000001000"
                            for k in ("CapEff", "CapPrm", "CapInh", "CapBnd", "CapAmb")
                        },
                        "NoNewPrivs": "1",
                    }
                },
                "network helper privilege observation differs",
            )
            captured[name] = hashlib.sha256(
                (output_dir / name / "capture.json").read_bytes()
            ).hexdigest()
            return (output_dir / name / "native.stdout").read_bytes()

        initial = parse_native_json(
            run("initial", ["-j", "list", "ruleset"]).decode("utf-8")
        )
        _require(
            _normalized_rules(initial) == [], "network namespace already has nft policy"
        )
        run("install", ["-j", "-f", f"/proc/self/fd/{policy_fd}"])
        observed = parse_native_json(
            run("readback", ["-j", "list", "ruleset"]).decode("utf-8")
        )
        verify_capture_network_rules(
            rebuilt, observed, expected_policy_sha256=expected_policy_sha256
        )
        _require(
            all(
                hashlib.sha256(Path(name).read_bytes()).hexdigest() == sha
                for name, sha in tools.items()
            ),
            "network tools changed during installation",
        )
        result = {
            **preflight,
            "schema": "caplab.capture-network-installation/v1",
            "command_receipt_sha256": captured,
            "command_sha256": commands,
            "readback_sha256": hashlib.sha256(
                (output_dir / "readback/native.stdout").read_bytes()
            ).hexdigest(),
            "rules_agree": True,
            "workload_release_verified": False,
            "transport_attached": False,
            "study_eligible": False,
        }
        seal("installation.json", result)
        return result
