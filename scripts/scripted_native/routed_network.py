"""Build and inspect the disconnected supervisor network for the routed profile."""

import json
import os
from pathlib import Path
import sys

from caplab.process_capture import capture_process, seal_capture_json
from .lifecycle import REPO, check_inputs, read_preparation, require


def namespace_ids():
    return {
        name: os.readlink("/proc/self/ns/" + name) for name in ("user", "net", "pid")
    }


def outer_command(root, *, source, dependency, group, child_command, task_input=None):
    """Borrow pinned input paths; expose only owned custody and cgroup for writes."""
    command = [
        "/usr/bin/bwrap",
        "--unshare-user",
        "--unshare-net",
        "--unshare-pid",
        "--unshare-ipc",
        "--unshare-uts",
        "--die-with-parent",
        "--new-session",
        "--clearenv",
    ]
    for cap in ("SYS_ADMIN", "NET_ADMIN", "SETPCAP", "NET_BIND_SERVICE"):
        command += ["--cap-add", "CAP_" + cap]
    command += [
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
        "--ro-bind",
        "/sys/fs/cgroup",
        "/sys/fs/cgroup",
        "--ro-bind",
        str(REPO),
        str(REPO),
        "--ro-bind",
        str(source),
        str(source),
        "--ro-bind",
        str(dependency),
        str(dependency),
        "--bind",
        str(root.parent),
        str(root.parent),
        "--ro-bind",
        str(root / "outer-etc"),
        "/etc",
        "--dir",
        "/run",
    ]
    if group is not None:
        command += ["--bind", str(group), str(group)]
    if task_input is not None:
        command += ["--ro-bind", str(task_input), str(task_input)]
    for device in (
        "/dev/null",
        "/dev/urandom",
        "/dev/zero",
        "/dev/full",
        "/dev/random",
        "/dev/tty",
        "/dev/net/tun",
    ):
        command += ["--dev-bind", device, device]
    environment = {
        "PATH": "/usr/bin:/usr/sbin:/bin",
        "LANG": "C.UTF-8",
        "PYTHONPATH": ":".join(
            map(str, (REPO / "src", REPO / "scripts", dependency.parent))
        ),
    }
    for key, value in environment.items():
        command += ["--setenv", key, value]
    return command + ["--", *child_command]


def configure_outer(root, expected_namespaces, *, quarantine_factory=None):
    current = namespace_ids()
    require(
        set(expected_namespaces) == set(current)
        and all(current[k] != expected_namespaces[k] for k in current),
        "routed supervisor did not enter distinct namespaces",
    )
    from caplab.capture_quarantine import check_capture_document, check_capture_bytes

    output = root / "outer-network"
    check_capture_bytes(quarantine_factory, os.fsencode(output))
    output.mkdir(mode=0o700)

    def run(name, args):
        command = ["/usr/sbin/ip", *args]
        environment = {"PATH": "/usr/bin:/usr/sbin:/bin", "LANG": "C.UTF-8"}
        document = {"command": command, "environment": environment}
        check_capture_document(quarantine_factory, document)
        check_capture_bytes(
            quarantine_factory, os.fsencode(output / (name + "-command.json"))
        )
        check_capture_bytes(
            quarantine_factory, os.fsencode(output / ("." + name + "-command.pending"))
        )
        seal_capture_json(output, name + "-command.json", document)
        receipt = capture_process(
            command,
            cwd=root,
            environment=environment,
            output_dir=output / name,
            max_stream_bytes=128 * 1024,
            timeout_seconds=5,
            quarantine_factory=quarantine_factory,
        )
        require(
            receipt["return_code"] == 0 and receipt["streams_complete"],
            "outer network command failed",
        )
        return (output / name / "native.stdout").read_bytes()

    links = json.loads(run("links", ["-j", "link"]))
    routes = json.loads(run("routes", ["-j", "route"]))
    require(
        [link["ifname"] for link in links] == ["lo"] and routes == [],
        "routed outer network is not initially disconnected",
    )
    run("loopback", ["link", "set", "lo", "up"])
    run("address", ["addr", "add", "198.18.0.1/32", "dev", "lo"])
    return {
        "schema": "caplab.scripted-outer-network/v1",
        "parent_namespaces": expected_namespaces,
        "namespaces": current,
        "initial_links": links,
        "initial_routes": routes,
        "fixture_address": "198.18.0.1",
        "study_eligible": False,
    }


def enter_outer(root, unit, expected_preparation_sha256):
    from .runner import seal

    prepared = read_preparation(
        root.parent, expected_sha256=expected_preparation_sha256
    )
    check_inputs(prepared)
    require(
        prepared.get("launch_profile")
        in ("codex-scripted-routed/v1", "codex-scripted-routed/v2"),
        "routed worker needs routed preparation",
    )
    member = Path("/proc/self/cgroup").read_text().strip()
    require(member.startswith("0::/") and "\n" not in member, "unified cgroup required")
    current = Path("/sys/fs/cgroup") / member[3:].lstrip("/")
    group = current.parent
    require(
        current.name == "supervisor" and group.name == unit, "wrong outer worker cgroup"
    )
    etc = root / "outer-etc"
    etc.mkdir(mode=0o700)
    (etc / "resolv.conf").write_text("nameserver 198.18.0.53\n")
    command = outer_command(
        root,
        source=Path(prepared["harness_manifest"]["source"]),
        dependency=Path(prepared["dependency_manifest"]["source"]),
        group=group,
        task_input=Path(prepared["task_input"]["custody"])
        if prepared.get("task_input") is not None
        else None,
        child_command=[
            sys.executable,
            "-B",
            str(REPO / "scripts/probe_scripted_native_capture.py"),
            "worker",
            str(root),
            "--unit",
            unit,
            "--preparation-sha256",
            expected_preparation_sha256,
        ],
    )
    seal(
        root,
        "outer-launch.json",
        {
            "command": command,
            "parent_namespaces": namespace_ids(),
            "preparation_sha256": expected_preparation_sha256,
        },
    )
    os.execv(command[0], command)
