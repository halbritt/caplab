#!/usr/bin/env python3
"""Build a Cairn binary from a clean clone and print the pins a retrieval arm needs.

    python3 scripts/retrieval_pin_cairn.py --checkout ~/git/cairn --output /tmp/cairn-a
    python3 scripts/retrieval_pin_cairn.py --checkout ~/git/cairn --revision <sha> --output /tmp/cairn-b

The output directory must not exist. It receives `src/` (a clone checked out at
the revision) and `cairn` (built from it). The printed JSON is the `binary` and
`checkout` pair for a `cairn` arm configuration. The binary's embedded revision
must equal the clone's HEAD and the clone must be clean, the same conditions the
runner enforces before it will run the arm. The source checkout is only read.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def run(command, **kwargs):
    done = subprocess.run([str(c) for c in command], capture_output=True, text=True, **kwargs)
    if done.returncode:
        raise SystemExit(f"{command[0]} {command[1]} failed: {done.stderr.strip()[-800:] or done.stdout.strip()[-800:]}")
    return done.stdout.strip()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--checkout", required=True, help="Cairn repository to clone (path or URL); not modified")
    parser.add_argument("--revision", help="commit to build (default: the repository's HEAD)")
    parser.add_argument("--output", required=True, type=Path, help="new directory for the clone and the binary")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if output.exists():
        parser.error(f"{output} already exists; choose a new directory")
    output.mkdir(parents=True)
    source, binary = output / "src", output / "cairn"
    run(["git", "clone", "--quiet", args.checkout, source])
    if args.revision:
        run(["git", "-C", source, "checkout", "--quiet", "--detach", args.revision])
    head = run(["git", "-C", source, "rev-parse", "HEAD"])
    run(["go", "build", "-o", binary, "./cmd/cairn"], cwd=source, timeout=1800)
    version = json.loads(run([binary, "version"]))["data"]
    if version.get("vcs_revision") != head or version.get("vcs_modified") is not False:
        raise SystemExit(f"built binary reports revision {version.get('vcs_revision')!r} "
                         f"(modified={version.get('vcs_modified')!r}), not the clone HEAD {head}")
    print(json.dumps({"binary": str(binary), "checkout": str(source), "vcs_revision": head,
                      "binary_sha256": "sha256:" + hashlib.sha256(binary.read_bytes()).hexdigest()}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
