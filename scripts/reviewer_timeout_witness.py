#!/usr/bin/env python3
"""Reproduce the sampled Council provider lifetime behavior in isolated snapshots."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time


REPOSITORY = Path("/home/halbritt/git/council")
DEPENDENCIES = REPOSITORY / "node_modules"
PROBE = Path(__file__).resolve().parents[1] / "docs/product/studies/reviewer-ranking-001/development-witnesses/council-provider-lifetime/probe.mts"
COMMITS = {
    "introduction": "9c66a76836245fbc8d203812a4a36f475341ce0e",
    "base": "32c9f09674b27b185abb7498883d9d3495ac4951",
    "repair": "19fb83494cf3ec8e338d748f566be3df21088a40",
}
CONDITIONS = ("ordinary", "delayed-body", "cancel-body", "pre-aborted")


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_new(path: Path, payload: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(payload)
        output.flush()
        os.fsync(output.fileno())
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_json(path: Path, document: dict) -> None:
    write_new(path, (json.dumps(document, indent=2, sort_keys=True) + "\n").encode())


def git(*arguments: str) -> bytes:
    return subprocess.check_output(["git", "--no-replace-objects", "-C", str(REPOSITORY), *arguments])


def materialize(root: Path, commit: str) -> dict:
    root.mkdir(mode=0o700)
    inventory = []
    for row in git("ls-tree", "-rz", commit).split(b"\0"):
        if not row:
            continue
        header, encoded = row.split(b"\t", 1)
        mode, kind, object_id = header.decode().split()
        relative = encoded.decode()
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("only tracked regular files may be materialized")
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("unsafe source path")
        payload = git("cat-file", "blob", object_id)
        expected = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
        if expected != object_id:
            raise ValueError("source blob identity mismatch")
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        write_new(destination, payload)
        destination.chmod(0o500 if mode == "100755" else 0o400)
        inventory.append({"path": relative, "git_blob": object_id, "mode": mode,
                          "bytes": len(payload), "sha256": sha(payload)})
    (root / "node_modules").mkdir(mode=0o700)
    return {"commit": commit, "tree": git("rev-parse", commit + "^{tree}").decode().strip(), "files": inventory}


def dependency_inventory() -> list[dict]:
    entries = []
    for path in sorted(DEPENDENCIES.rglob("*")):
        relative = str(path.relative_to(DEPENDENCIES))
        if path.is_symlink():
            if not path.resolve().is_relative_to(DEPENDENCIES.resolve()):
                raise ValueError("dependency symlink escapes its mount")
            entries.append({"path": relative, "symlink": os.readlink(path)})
        elif path.is_file():
            entries.append({"path": relative, "sha256": sha(path.read_bytes())})
    return entries


def prepare(root: Path) -> None:
    root.mkdir(mode=0o700)
    (root / "witness").mkdir(mode=0o700)
    write_new(root / "witness/probe.mts", PROBE.read_bytes())
    snapshots = {name: materialize(root / name, commit) for name, commit in COMMITS.items()}
    plan = {"schema": "caplab.council-provider-lifetime-plan/v1", "snapshots": snapshots,
            "probe_sha256": sha(PROBE.read_bytes()), "node_sha256": sha(Path("/usr/bin/node").read_bytes()),
            "bwrap_sha256": sha(Path("/usr/bin/bwrap").read_bytes()), "dependencies": dependency_inventory(),
            "conditions": list(CONDITIONS), "repetitions": 3, "maximum_launches": 36,
            "per_process_seconds": 15, "total_seconds": 480,
            "interpretation": "diagnostic source reproduction; zero reviewer calls; no qualification"}
    write_json(root / "plan.json", plan)
    print(json.dumps({"prepared": str(root), "plan_sha256": sha((root / "plan.json").read_bytes())}))


def verify_inputs(root: Path, plan: dict) -> None:
    if sha((root / "witness/probe.mts").read_bytes()) != plan["probe_sha256"]:
        raise ValueError("witness changed")
    for binary in ("node", "bwrap"):
        if sha(Path("/usr/bin", binary).read_bytes()) != plan[binary + "_sha256"]:
            raise ValueError("runtime executable changed")
    if dependency_inventory() != plan["dependencies"]:
        raise ValueError("runtime dependencies changed")
    for name, snapshot in plan["snapshots"].items():
        if snapshot["commit"] != COMMITS[name]:
            raise ValueError("source commit changed")
        for entry in snapshot["files"]:
            if sha((root / name / entry["path"]).read_bytes()) != entry["sha256"]:
                raise ValueError("materialized source changed")


def command(root: Path, role: str, condition: str) -> list[str]:
    return ["/usr/bin/bwrap", "--unshare-all", "--die-with-parent", "--new-session",
            "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib", "--ro-bind", "/lib64", "/lib64",
            "--symlink", "usr/bin", "/bin", "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
            "--dir", "/home/witness", "--ro-bind", str(root / role), "/source",
            "--ro-bind", str(DEPENDENCIES), "/source/node_modules",
            "--ro-bind", str(root / "witness"), "/witness", "--clearenv",
            "--setenv", "PATH", "/usr/bin:/bin", "--setenv", "HOME", "/home/witness",
            "--setenv", "TMPDIR", "/tmp", "--chdir", "/tmp",
            "/usr/bin/node", "/source/node_modules/tsx/dist/cli.mjs", "/witness/probe.mts", condition]


def run(root: Path, expected_plan: str) -> None:
    raw = (root / "plan.json").read_bytes()
    if sha(raw) != expected_plan:
        raise ValueError("plan hash mismatch")
    plan = json.loads(raw)
    verify_inputs(root, plan)
    write_json(root / "run-started.json", {"plan_sha256": expected_plan, "time_ns": time.time_ns()})
    started = time.monotonic()
    host_namespace = os.readlink("/proc/self/ns/net")
    launches = 0
    for role in COMMITS:
        for condition in CONDITIONS:
            for repetition in range(1, 4):
                if time.monotonic() - started >= 480:
                    raise RuntimeError("total execution budget exhausted")
                slot = root / f"{role}-{condition}-{repetition}"
                slot.mkdir(mode=0o700)
                argv = command(root, role, condition)
                write_json(slot / "launch.json", {"argv": argv, "time_ns": time.time_ns()})
                launches += 1
                process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
                timed_out = False
                try:
                    stdout, stderr = process.communicate(timeout=min(15, 480 - (time.monotonic() - started)))
                except subprocess.TimeoutExpired:
                    timed_out = True
                    os.killpg(process.pid, signal.SIGKILL)
                    stdout, stderr = process.communicate()
                write_new(slot / "stdout", stdout)
                write_new(slot / "stderr", stderr)
                write_json(slot / "completion.json", {"exit_code": process.returncode, "timed_out": timed_out})
                if process.returncode != 0 or timed_out:
                    raise RuntimeError(f"diagnostic process failed: {slot}")
                observation = json.loads(stdout)
                source = root / role / "src/v3/deepseek-runtime.ts"
                if observation["source_sha256"] != sha(source.read_bytes()) or observation["net_namespace"] == host_namespace:
                    raise ValueError("source or isolation witness mismatch")
                print(json.dumps({"slot": slot.name, "result": observation["result"], "requests": observation["requests"]}), flush=True)
    verify_inputs(root, plan)
    write_json(root / "run-complete.json", {"launches": launches, "elapsed_seconds": time.monotonic() - started,
                                            "plan_sha256": expected_plan})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--plan-sha256")
    args = parser.parse_args()
    if not args.root.is_absolute():
        parser.error("root must be absolute")
    if args.action == "prepare":
        prepare(args.root)
    else:
        if not args.plan_sha256:
            parser.error("run requires --plan-sha256")
        run(args.root, args.plan_sha256)


if __name__ == "__main__":
    main()
