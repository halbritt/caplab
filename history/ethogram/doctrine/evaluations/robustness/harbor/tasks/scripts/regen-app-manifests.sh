#!/bin/bash
# Regenerate each pair task's shipped-app manifest (tests/app-manifest.json).
# The verifier diffs the agent's tree against this manifest to produce the
# deterministic change record; the hygiene gate fails if a manifest is stale.
set -eu

HERE="$(cd "$(dirname "$0")/.." && pwd)"
for TASK in checkout-retries-v2 checkout-retries-m1; do
  TASK_DIR="$HERE/$TASK" python3 - <<'PY'
import hashlib, json, os, pathlib
task = pathlib.Path(os.environ["TASK_DIR"])
app = task / "environment" / "app"
manifest = {
    path.relative_to(app).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(app.rglob("*")) if path.is_file()
}
out = task / "tests" / "app-manifest.json"
out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"{out}: {len(manifest)} files")
PY
done
