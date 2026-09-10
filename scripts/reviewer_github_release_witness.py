#!/usr/bin/env python3
"""Bounded development reproduction of the sampled GitHub release-loss repair."""
from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import signal
import ssl
import subprocess
import sys
import sysconfig
import time

import reviewer_timeout_witness as custody


REPOSITORY = Path("/home/halbritt/git/ai-newsroom")
ROOT = Path("/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/github-release-witness-4")
CAPLAB = Path("/home/halbritt/git/caplab")
PROBE = CAPLAB / "docs/product/studies/reviewer-ranking-001/development-witnesses/github-release-preservation/probe.py"
AUTH = CAPLAB / "docs/records/authorization-2026-09-10-reviewer-github-release-witness-4.md"
COMMITS = {
    "introduction": "e7672756e15b45e68e7f0725b54247cc3e93b89a",
    "base": "33881f4a341681fb3b29f6cfd87bdb08e1de9134",
    "repair": "c04f6c8b3af6bef8876330f37d02c42effd12908",
}
CONDITIONS = ("ordinary", "low-eligible", "low-draft", "low-empty")
custody.REPOSITORY = REPOSITORY


def file_record(path: Path) -> dict:
    return {"path": str(path), "sha256": custody.sha(path.read_bytes())}


def prepare() -> None:
    ROOT.mkdir(mode=0o700)
    (ROOT / "fixture").mkdir(mode=0o700)
    (ROOT / "records").mkdir(mode=0o700)
    custody.write_new(ROOT / "runner.py", Path(__file__).read_bytes())
    custody.write_new(ROOT / "reviewer_timeout_witness.py", Path(custody.__file__).read_bytes())
    custody.write_new(ROOT / "fixture/probe.py", PROBE.read_bytes())
    custody.write_new(ROOT / "fixture/hosts", b"127.0.0.1 localhost api.github.com\n")
    custody.write_new(ROOT / "fixture/nsswitch.conf", b"hosts: files\n")
    cert_command = ["/usr/bin/openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                    "-keyout", str(ROOT / "fixture/key.pem"), "-out", str(ROOT / "fixture/cert.pem"),
                    "-days", "2", "-subj", "/CN=api.github.com", "-addext", "subjectAltName=DNS:api.github.com"]
    with (ROOT / "cert-stdout").open("xb") as out, (ROOT / "cert-stderr").open("xb") as err:
        subprocess.run(cert_command, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                       env={"PATH": "/usr/bin:/bin"}, check=True, timeout=12)
    snapshots = {role: custody.materialize(ROOT / role, commit) for role, commit in COMMITS.items()}
    governing = []
    parent = "fd4c031e7d7735ab5103cc0bf23987bf9090491a"
    for name in ("README.md", "newsroom/sources/base.py"):
        payload = custody.git("show", f"{parent}:{name}")
        destination = ROOT / "records" / name.replace("/", "_")
        custody.write_new(destination, payload)
        governing.append({"commit": parent, "path": name, "sha256": custody.sha(payload),
                          "git_blob": custody.git("rev-parse", f"{parent}:{name}").decode().strip(),
                          "custody_path": str(destination)})
    runtime = [file_record(Path(p)) for p in (sys.executable, "/usr/bin/bwrap", "/usr/bin/openssl")]
    stdlib = Path(sysconfig.get_path("stdlib"))
    runtime += [file_record(path) for path in sorted(stdlib.rglob("*"))
                if path.is_file() and path.suffix in {".py", ".so"} and "__pycache__" not in path.parts]
    criteria = {
        "family": "successfully fetched eligible release survives low quota",
        "ordinary": {"release_requests": "all defaults", "article_urls": [f"https://github.com/{r}/releases/tag/v1.0.0" for r in ("openai/openai-python", "anthropics/anthropic-sdk-python")]},
        "low-eligible": {"release_requests": 1, "article_urls": ["https://github.com/openai/openai-python/releases/tag/v1.0.0"]},
        "low-draft": {"release_requests": 1, "article_urls": []},
        "low-empty": {"release_requests": 1, "article_urls": []},
        "all": "HTTP 200 at exact configured release paths; no authorization; persisted empty repo baseline; no process failure",
        "expected_contrast": "Introduction/base lose low-quota eligible release; repair preserves it; all controls pass",
        "basis": "Original SourceAdapter contract and daily-news purpose; actual successful response bodies; GitHub remaining header means future request budget",
        "limits": "Developer-authored witness after inspecting both sides; no whole-change clean label, scorer, admission, or ranking",
    }
    defaults = {}
    for role in COMMITS:
        defaults[role] = {}
        module = ast.parse((ROOT / role / "newsroom/sources/github.py").read_text())
        for node in module.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                if name in {"TOPICS", "VELOCITY_TOPICS", "RELEASE_REPOS"}:
                    values = ast.literal_eval(node.value)
                    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                        raise ValueError("nonliteral default scan")
                    defaults[role][name] = values
        if set(defaults[role]) != {"TOPICS", "VELOCITY_TOPICS", "RELEASE_REPOS"}:
            raise ValueError("missing scan defaults")
        if defaults[role]["RELEASE_REPOS"][:2] != ["openai/openai-python", "anthropics/anthropic-sdk-python"]:
            raise ValueError("fixture repositories differ from defaults")
    criteria["default_scans"] = defaults
    custody.write_json(ROOT / "criteria.json", criteria)
    plan = {"schema": "caplab.github-release-preservation-plan/v1", "snapshots": snapshots,
            "source_repository": str(REPOSITORY), "governing_records": governing,
            "authorization_sha256": custody.sha(AUTH.read_bytes()),
            "criteria_sha256": custody.sha((ROOT / "criteria.json").read_bytes()),
            "fixture": [file_record(path) for path in sorted((ROOT / "fixture").iterdir())],
            "runner_sha256": custody.sha(Path(__file__).read_bytes()),
            "helper_sha256": custody.sha(Path(custody.__file__).read_bytes()),
            "runtime": runtime, "python_version": sys.version, "ssl_version": ssl.OPENSSL_VERSION,
            "cert_command": cert_command, "conditions": list(CONDITIONS), "repetitions": 3,
            "maximum_source_launches": 36, "maximum_preflights": 1,
            "per_process_seconds": 15, "preflight_seconds": 12, "total_seconds": 420,
            "expires_at": "2026-09-11T00:00:00Z"}
    custody.write_json(ROOT / "plan.json", plan)
    print(json.dumps({"prepared": str(ROOT), "plan_sha256": custody.sha((ROOT / "plan.json").read_bytes())}))


def verify_inputs(plan: dict) -> None:
    if custody.sha(Path(__file__).read_bytes()) != plan["runner_sha256"]:
        raise ValueError("runner drift")
    if custody.sha(Path(custody.__file__).read_bytes()) != plan["helper_sha256"]:
        raise ValueError("helper drift")
    if custody.sha(AUTH.read_bytes()) != plan["authorization_sha256"]:
        raise ValueError("authorization drift")
    for entry in plan["fixture"] + plan["runtime"]:
        if custody.sha(Path(entry["path"]).read_bytes()) != entry["sha256"]:
            raise ValueError("fixture or runtime drift: " + entry["path"])
    if custody.sha((ROOT / "criteria.json").read_bytes()) != plan["criteria_sha256"]:
        raise ValueError("criteria drift")
    for role, source in plan["snapshots"].items():
        for entry in source["files"]:
            if custody.sha((ROOT / role / entry["path"]).read_bytes()) != entry["sha256"]:
                raise ValueError("source drift")


def run(role: str, condition: str, repetition: int) -> None:
    plan = json.loads((ROOT / "plan.json").read_text())
    verify_inputs(plan)
    if time.time() >= 1789084800:
        raise ValueError("authorization expired")
    preflight = condition == "preflight"
    if preflight:
        if role != "introduction" or repetition != 0:
            raise ValueError("one preflight slot only")
        label = "preflight"
    else:
        if condition not in CONDITIONS or repetition not in (1, 2, 3):
            raise ValueError("unassigned source slot")
        previous = json.loads((ROOT / "preflight/completion.json").read_text())
        if previous["returncode"] != 0 or previous["termination"] != "exit":
            raise ValueError("preflight not successful")
        label = f"{role}-{condition}-{repetition}"
    # This runner is sequential: incomplete earlier slots forbid a new launch.
    elapsed = 0.0
    for launch in ROOT.glob("*/launch.json"):
        result = json.loads((launch.parent / "completion.json").read_text())
        elapsed += result["elapsed_seconds"]
    timeout = plan["preflight_seconds"] if preflight else plan["per_process_seconds"]
    if elapsed + timeout > plan["total_seconds"]:
        raise ValueError("total process budget exhausted")
    slot = ROOT / label
    slot.mkdir(mode=0o700)
    argv = ["/usr/bin/bwrap", "--die-with-parent", "--unshare-all",
            "--uid", "0", "--gid", "0", "--cap-drop", "ALL",
            "--cap-add", "CAP_NET_BIND_SERVICE",
            "--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib",
            "--ro-bind", "/lib64", "/lib64", "--ro-bind", str(ROOT / role), "/source",
            "--ro-bind", str(ROOT / "fixture"), "/fixture",
            "--ro-bind", str(ROOT / "fixture/hosts"), "/etc/hosts",
            "--ro-bind", str(ROOT / "fixture/nsswitch.conf"), "/etc/nsswitch.conf",
            "--tmpfs", "/tmp", "--proc", "/proc", "--dev", "/dev", "--dir", "/home/witness",
            "--chdir", "/tmp", "--clearenv", "--setenv", "HOME", "/home/witness",
            "--setenv", "SSL_CERT_FILE", "/fixture/cert.pem",
            "--", sys.executable, "-I", "-B", "/fixture/probe.py", condition]
    custody.write_json(slot / "launch.json", {"argv": argv, "started_at": time.time(),
                                             "plan_sha256": custody.sha((ROOT / "plan.json").read_bytes())})
    start = time.monotonic()
    with (slot / "stdout").open("xb") as out, (slot / "stderr").open("xb") as err:
        child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err, start_new_session=True)
        custody.write_json(slot / "process.json", {"pid": child.pid,
            "proc_start_ticks": Path(f"/proc/{child.pid}/stat").read_text().rsplit(")", 1)[1].split()[19]})
        termination = "exit"
        try:
            child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            termination = "deadline"
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=5)
    result = {"returncode": child.returncode, "termination": termination,
              "elapsed_seconds": time.monotonic() - start,
              "stdout_sha256": custody.sha((slot / "stdout").read_bytes()),
              "stderr_sha256": custody.sha((slot / "stderr").read_bytes())}
    custody.write_json(slot / "completion.json", result)
    verify_inputs(plan)
    print(json.dumps({"slot": label, **result}))


if __name__ == "__main__":
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "run"))
    parser.add_argument("role", nargs="?", choices=tuple(COMMITS))
    parser.add_argument("condition", nargs="?", choices=("preflight", *CONDITIONS))
    parser.add_argument("repetition", nargs="?", type=int)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    else:
        run(args.role, args.condition, args.repetition)
