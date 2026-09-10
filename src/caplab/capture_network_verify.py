"""Bounded read-only consistency inspection of completed routing custody."""

from contextlib import ExitStack
from datetime import datetime, timedelta
import hashlib
import json
import math
import os
from pathlib import Path

from caplab.capture_network_policy import (
    _ENTER as _POLICY_ENTER,
    _normalized_rules,
    _rules,
    _validated,
    verify_capture_network_rules,
)
from caplab.capture_network_transport import _ENTER as _ROUTING_ENTER
from caplab.codex_events import parse_native_json
from caplab.task_capture import TaskCaptureLimits
from caplab.task_capture_verify import (
    CaptureVerificationError,
    _count,
    _digest,
    _identity,
    _open,
    _process,
    _read_file,
    _require,
)

_ENVIRONMENT = {"PATH": "/usr/bin:/usr/sbin:/bin", "LANG": "C.UTF-8"}
_CAPABILITIES = ("CapEff", "CapPrm", "CapInh", "CapBnd", "CapAmb")


def _same(actual, expected, label):
    _require(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        label,
    )


def _keys(value, keys, label):
    _require(
        isinstance(value, dict) and set(value) == set(keys.split()), "invalid " + label
    )


def _descriptors(value, count):
    _require(
        isinstance(value, list)
        and len(value) == count
        and all(type(fd) is int and fd > 2 for fd in value)
        and len(set(value)) == count,
        "invalid routing borrowed descriptors",
    )
    return value


def _routing_command(command, installation, *, parent_owned=False):
    _keys(
        command,
        "command environment borrowed_descriptors slirp_sha256 namespaces "
        "python_sha256 helper_source_sha256 network_policy_sha256 "
        "policy_installation_sha256 timeout_seconds max_stream_bytes"
        + (" namespace_profile network_identity_sha256" if parent_owned else ""),
        "routing command",
    )
    user, net, ready, exit_fd = _descriptors(command["borrowed_descriptors"], 4)
    expected = [
        "/usr/bin/python3",
        "-I",
        "-S",
        "-c",
        _ROUTING_ENTER,
        str(user),
        "--configure",
        "--enable-sandbox",
        "--enable-seccomp",
        "--disable-host-loopback",
        "--disable-dns",
        "--netns-type=path",
        f"--ready-fd={ready}",
        f"--exit-fd={exit_fd}",
        f"/proc/self/fd/{net}",
        "tap0",
    ]
    _same(command["command"], expected, "routing command differs from fixed profile")
    _same(command["environment"], _ENVIRONMENT, "routing environment differs")
    _require(
        command["helper_source_sha256"]
        == hashlib.sha256(_ROUTING_ENTER.encode()).hexdigest(),
        "routing helper source differs",
    )
    _digest(command["slirp_sha256"])
    _require(
        _digest(command["python_sha256"])
        == installation["tool_sha256"]["/usr/bin/python3"],
        "routing and policy Python observations differ",
    )
    _require(
        type(command["max_stream_bytes"]) is int
        and command["max_stream_bytes"] == 128 * 1024,
        "routing stream allowance differs",
    )


def _policy_identity(installation, preflight, *, parent_owned=False):
    fields = "peer_pid namespaces capabilities network_policy_sha256 tool_sha256 helper_source_sha256"
    if parent_owned:
        fields += " namespace_profile network_identity workload_credentials"
    _keys(preflight, "schema " + fields, "policy preflight")
    _keys(
        installation,
        "schema " + fields + " command_receipt_sha256 command_sha256 "
        "readback_sha256 rules_agree workload_release_verified transport_attached study_eligible",
        "policy installation",
    )
    for name in fields.split():
        _same(
            preflight[name],
            installation[name],
            "policy preflight and installation disagree",
        )
    if parent_owned:
        from caplab.capture_network_identity import verify_network_identity_observation

        _require(
            installation["namespace_profile"] == "parent-user/v1",
            "policy ownership profile differs",
        )
        identity = verify_network_identity_observation(
            installation["network_identity"],
            expected_profile="parent-user/v1",
            expected_peer_pid=installation["peer_pid"],
        )
        _same(
            installation["workload_credentials"],
            {
                kind: [str(identity["mapping_observer"][kind])] * 4
                for kind in ("uid", "gid")
            },
            "retained workload credentials differ",
        )
        _same(
            installation["namespaces"],
            {
                "user": identity["network_owner_user_namespace"],
                "net": identity["network_namespace"],
            },
            "policy namespaces differ from checked owner",
        )
        _same(
            installation["capabilities"],
            identity["capabilities"],
            "policy workload privileges disagree",
        )
    identities = installation["namespaces"]
    _keys(identities, "user net", "routing namespaces")
    for identity in identities.values():
        _keys(identity, "device inode", "namespace identity")
        _require(
            _count(identity["device"], "namespace device") > 0
            and _count(identity["inode"], "namespace inode") > 0,
            "invalid namespace identity",
        )
    _same(
        installation["capabilities"],
        {**dict.fromkeys(_CAPABILITIES, "0000000000000000"), "NoNewPrivs": "1"},
        "workload capability observation differs",
    )
    _keys(
        installation["tool_sha256"],
        "/usr/bin/python3 /usr/sbin/nft",
        "policy tool hashes",
    )
    for digest in installation["tool_sha256"].values():
        _digest(digest)
    _require(
        installation["helper_source_sha256"]
        == hashlib.sha256(_POLICY_ENTER.encode()).hexdigest(),
        "policy helper source differs",
    )
    for name in ("command_receipt_sha256", "command_sha256"):
        _keys(installation[name], "initial install readback", "policy command hashes")
        for digest in installation[name].values():
            _digest(digest)


def _policy_command(command, name, expected_descriptors):
    _keys(command, "command environment borrowed_descriptors", "policy command")
    descriptors = _descriptors(command["borrowed_descriptors"], 3)
    if expected_descriptors is not None:
        _same(descriptors, expected_descriptors, "policy command descriptors disagree")
    user, net, policy = descriptors
    args = (
        ["-j", "-f", f"/proc/self/fd/{policy}"]
        if name == "install"
        else ["-j", "list", "ruleset"]
    )
    _same(
        command["command"],
        [
            "/usr/bin/python3",
            "-I",
            "-S",
            "-c",
            _POLICY_ENTER,
            str(user),
            str(net),
            *args,
        ],
        "policy command differs from fixed profile",
    )
    _same(command["environment"], _ENVIRONMENT, "policy command environment differs")
    return descriptors


def _json(raw):
    try:
        return parse_native_json(raw.decode("utf-8"))
    except (ValueError, UnicodeError, RecursionError) as error:
        raise CaptureVerificationError("invalid routing JSON") from error


class _Custody:
    def __init__(self, stack):
        self.stack = stack
        self.remaining = 1024 * 1024
        self.directories = []

    def directory(self, parent, name):
        fd = self.stack.enter_context(_open(parent, name, directory=True))
        info = os.fstat(fd)
        _require(
            info.st_uid == os.getuid() and info.st_mode & 0o077 == 0,
            "routing custody must be private and owned",
        )
        self.directories.append((parent, name, fd, _identity(info)))
        return fd

    def document(self, parent, name, expected=None):
        raw, size, digest = _read_file(parent, name, self.remaining, retain=True)
        self.remaining -= size
        if expected is not None:
            _require(
                digest == _digest(expected), "routing receipt hash mismatch: " + name
            )
        value = _json(raw)
        _require(isinstance(value, dict), "routing receipt must be an object")
        return value

    def unchanged(self):
        for parent, name, fd, before in self.directories:
            _require(
                before
                == _identity(os.fstat(fd))
                == _identity(os.stat(name, dir_fd=parent, follow_symlinks=False)),
                "routing custody changed during inspection",
            )


def _captured(reader, parent, name, expected, timeout):
    fd = reader.directory(parent, name)
    receipt = reader.document(fd, "capture.json", expected)
    _keys(
        receipt,
        "schema termination return_code streams_complete max_stream_bytes "
        "retained_stream_bytes timeout_seconds started_at finished_at started_monotonic_ns "
        "finished_monotonic_ns streams",
        "routing process receipt",
    )
    _require(
        receipt.get("schema") == "caplab.process-capture/v1",
        "unsupported routing process schema",
    )
    _process(fd, receipt, TaskCaptureLimits(128 * 1024, 1, 1, timeout))
    _require(
        receipt["return_code"] == 0 and receipt["streams_complete"],
        "routing command did not complete normally",
    )
    started = _count(receipt.get("started_monotonic_ns"), "process start")
    finished = _count(receipt.get("finished_monotonic_ns"), "process finish")
    _require(0 < started <= finished, "invalid routing process interval")
    for name in ("started_at", "finished_at"):
        value = receipt[name]
        _require(isinstance(value, str), "invalid process wall timestamp")
        try:
            timestamp = datetime.fromisoformat(value)
        except ValueError as error:
            raise CaptureVerificationError("invalid process wall timestamp") from error
        _require(
            timestamp.utcoffset() == timedelta(0), "process wall timestamp must be UTC"
        )
    raw = {}
    for stream, entry in receipt["streams"].items():
        _keys(
            entry,
            "bytes eof first_receipt_monotonic_ns last_receipt_monotonic_ns sha256 path",
            "routing stream receipt",
        )
        first, last = (
            entry.get(k + "_receipt_monotonic_ns") for k in ("first", "last")
        )
        if entry["bytes"]:
            _require(
                type(first) is int
                and type(last) is int
                and started <= first <= last <= finished,
                "stream observation outside process interval",
            )
        else:
            _require(
                first is None and last is None, "empty stream has byte observations"
            )
        raw[stream], size, digest = _read_file(
            fd, "native." + stream, 128 * 1024, retain=True
        )
        _require(
            size == entry["bytes"] and digest == entry["sha256"],
            "routing stream changed between reads",
        )
    return receipt, raw


def verify_capture_routing(
    root: Path,
    *,
    plan: dict,
    expected_policy_sha256: str,
    expected_terminal_sha256: str,
    expected_ready_sha256: str,
    expected_peer_pid: int,
    expected_namespace_profile: str = "workload-user/v1",
) -> dict:
    """Check retained consistency against externally supplied handoff anchors.

    Caller owns authentication, anchor provenance and stable private ancestry.
    No process is launched; execution, continuous liveness, tool selection and
    native containment cannot be established from these retained records alone.
    Missing, malformed or contradictory custody raises ValueError or OSError.
    """
    plan = _validated(plan, expected_policy_sha256)
    _require(
        type(expected_namespace_profile) is str
        and expected_namespace_profile in ("workload-user/v1", "parent-user/v1"),
        "unsupported expected ownership profile",
    )
    parent_owned = expected_namespace_profile == "parent-user/v1"
    version = "2" if parent_owned else "1"
    ownership_fields = (
        " namespace_profile network_identity_sha256" if parent_owned else ""
    )
    ownership = {}
    _digest(expected_terminal_sha256)
    _digest(expected_ready_sha256)
    _require(
        type(expected_peer_pid) is int and expected_peer_pid > 0,
        "invalid expected routing peer PID",
    )
    _require(
        isinstance(root, Path)
        and root.is_absolute()
        and root.resolve() == root
        and root != Path("/"),
        "routing root must be a resolved absolute path",
    )
    with ExitStack() as stack:
        reader = _Custody(stack)
        top = reader.directory(None, root)
        terminal = reader.document(top, "terminal.json", expected_terminal_sha256)
        ready = reader.document(top, "ready.json", expected_ready_sha256)
        _keys(
            terminal,
            "schema command_sha256 ready_sha256 capture_sha256 normal_shutdown "
            "body_completed tools_agree study_eligible" + ownership_fields,
            "routing terminal",
        )
        _keys(
            ready,
            "schema command_sha256 network_policy_sha256 namespaces "
            "ready_signal_observed ready_observed_monotonic_ns study_eligible"
            + ownership_fields,
            "routing readiness",
        )
        _require(
            terminal.get("schema") == "caplab.capture-routing-terminal/v" + version
            and ready.get("schema") == "caplab.capture-routing-readiness/v" + version,
            "unsupported routing lifecycle schema",
        )
        _require(
            terminal.get("ready_sha256") == expected_ready_sha256,
            "routing readiness differs from independent anchor",
        )
        command = reader.document(
            top, "command.json", _digest(terminal["command_sha256"])
        )
        _require(
            ready.get("command_sha256") == terminal["command_sha256"],
            "routing readiness and terminal commands differ",
        )
        _require(
            ready.get("network_policy_sha256") == expected_policy_sha256
            and command.get("network_policy_sha256") == expected_policy_sha256,
            "routing policy differs from selection",
        )
        for document, fields in (
            (terminal, ("normal_shutdown", "body_completed", "tools_agree")),
            (ready, ("ready_signal_observed",)),
        ):
            _require(
                all(document.get(k) is True for k in fields)
                and document.get("study_eligible") is False,
                "routing lifecycle is incomplete or claims eligibility",
            )
        policy = reader.directory(top, "policy")
        installation = reader.document(
            policy,
            "installation.json",
            _digest(command.get("policy_installation_sha256")),
        )
        preflight = reader.document(policy, "preflight.json")
        _require(
            installation.get("schema")
            == "caplab.capture-network-installation/v" + version
            and preflight.get("schema")
            == "caplab.capture-network-preflight/v" + version,
            "unsupported routing policy schema",
        )
        _require(
            type(installation.get("peer_pid")) is int
            and installation["peer_pid"] == expected_peer_pid,
            "routing peer differs from authenticated handoff",
        )
        _require(
            installation.get("network_policy_sha256") == expected_policy_sha256,
            "installation policy differs from selection",
        )
        _policy_identity(installation, preflight, parent_owned=parent_owned)
        _routing_command(command, installation, parent_owned=parent_owned)
        if parent_owned:
            identity_sha = _digest(command["network_identity_sha256"])
            identity = reader.document(top, "identity.json", identity_sha)
            _same(
                identity,
                installation["network_identity"],
                "routing and policy ownership differ",
            )
            for record in (terminal, ready, command):
                _require(
                    record.get("namespace_profile") == expected_namespace_profile
                    and record.get("network_identity_sha256") == identity_sha,
                    "routing ownership anchors disagree",
                )
            ownership = {
                "namespace_profile": expected_namespace_profile,
                "network_identity_sha256": identity_sha,
                "network_identity": identity,
            }

        identities = installation.get("namespaces")
        _same(
            identities, ready.get("namespaces"), "routing readiness namespaces disagree"
        )
        _same(
            identities, command.get("namespaces"), "routing command namespaces disagree"
        )
        _require(
            installation.get("rules_agree") is True
            and all(
                installation.get(k) is False
                for k in (
                    "workload_release_verified",
                    "transport_attached",
                    "study_eligible",
                )
            ),
            "invalid policy verification claims",
        )
        selected = reader.document(policy, "policy.json")
        _same(
            selected,
            {"nftables": [{"add": entry} for entry in _rules(plan)]},
            "retained policy differs from selection",
        )
        previous_finish = 0
        descriptors = None
        for name in ("initial", "install", "readback"):
            policy_command = reader.document(
                policy, name + "-command.json", installation["command_sha256"][name]
            )
            descriptors = _policy_command(policy_command, name, descriptors)
            process, streams = _captured(
                reader, policy, name, installation["command_receipt_sha256"][name], 5
            )
            _same(
                _json(streams["stderr"]),
                {
                    "helper_capabilities": {
                        **dict.fromkeys(_CAPABILITIES, "0000000000001000"),
                        "NoNewPrivs": "1",
                    }
                },
                "policy helper privilege observation differs",
            )
            _require(
                previous_finish <= process["started_monotonic_ns"],
                "policy command order disagrees",
            )
            previous_finish = process["finished_monotonic_ns"]
            if name == "initial":
                _require(
                    _normalized_rules(_json(streams["stdout"])) == [],
                    "initial namespace already contains policy",
                )
            elif name == "readback":
                _require(
                    hashlib.sha256(streams["stdout"]).hexdigest()
                    == installation.get("readback_sha256"),
                    "policy readback hash differs",
                )
                verify_capture_network_rules(
                    plan,
                    _json(streams["stdout"]),
                    expected_policy_sha256=expected_policy_sha256,
                )
        timeout = command.get("timeout_seconds")
        _require(
            type(timeout) in (int, float)
            and math.isfinite(timeout)
            and 0 < timeout <= 300,
            "invalid routing lifetime",
        )
        process, streams = _captured(
            reader, top, "process", _digest(terminal["capture_sha256"]), timeout
        )
        _same(
            _json(streams["stderr"].split(b"\n", 1)[0]),
            {
                "helper_capabilities": {
                    "CapEff": "0000000000201500",
                    "CapPrm": "0000000000201500",
                    "CapBnd": "0000000000201500",
                    "CapInh": "0000000000000000",
                    "CapAmb": "0000000000000000",
                    "NoNewPrivs": "1",
                }
            },
            "routing helper privilege observation differs",
        )
        observed = ready.get("ready_observed_monotonic_ns")
        _require(
            type(observed) is int
            and previous_finish
            <= process["started_monotonic_ns"]
            <= observed
            <= process["finished_monotonic_ns"],
            "routing readiness or policy is outside lifecycle order",
        )
        reader.unchanged()
    return {
        "schema": "caplab.capture-routing-inspection/v" + version,
        **ownership,
        "status": "verified-observation",
        "network_policy_sha256": expected_policy_sha256,
        "terminal_sha256": expected_terminal_sha256,
        "ready_sha256": expected_ready_sha256,
        "peer_pid": expected_peer_pid,
        "namespaces": identities,
        "native_containment_verified": False,
        "study_eligible": False,
    }
